"""Scouting: what each team knows about the other, and what it does about it.

Before this, play-calling was blind. `pass_prob` was built from down, distance, the
clock, the margin, the offence's own scheme and the weather -- and nothing about the
defence lined up across from it. A Cover-Heavy secondary with nothing up front got
attacked exactly the same way as a dominant front with no corners. The defence, for its
part, never anticipated anything: it executed the same way whether it was facing an
Option team or an Air Raid. That is the engine's parity problem in one sentence,
because when neither side can exploit the other, roster quality only shows up through
execution noise and every game drifts toward a coin flip.

Three pieces, all built from data already in the universe and the rosters -- no new
player attributes, nothing invented:

  1. IDENTITY  -- what a team actually is. Read from its scheme, its personnel balance
     (passer quality against rusher quality) and its unit strengths.
  2. GAME PLAN -- set once pre-snap-of-the-game from the opponent's identity. The
     offence leans toward whichever half of the defence is weaker; the defence commits
     toward whatever the offence is built to do.
  3. ADAPTATION -- updated every play from what has actually happened in THIS game.
     A plan built on the opponent's season profile gets overwritten by the evidence in
     front of it, which is what "how they are competing this week" means.

Every adjustment is scaled by the relevant coaches' skills, facing each other. A good
OC against a poor DC exploits the weakness; a poor OC against a good DC gets read all
afternoon and cannot do anything with what it sees. That is the point: it makes coaching
and roster quality compound instead of cancelling.

Determinism: nothing here draws randomness. Same seed in, same game out.
"""

# How hard the plan is allowed to push. These are the knobs worth tuning.
PLAN_WEIGHT = 0.16        # max shift in pass probability from the pre-game read
ADAPT_WEIGHT = 0.14       # max additional shift from in-game evidence
COMMIT_EDGE = 0.95        # defensive yards-per-play swing at a full correct commit
SKILL_SCALE = 6.0         # coach skills are ~3-8; this normalises the difference
MIN_PLAYS_TO_ADAPT = 8    # below this, in-game evidence is too thin to act on

# League-normal yards per play, measured off 2037 canon (17,544 runs and 19,327 pass
# plays, the latter including incompletions and sacks). These exist because comparing
# raw pass YPP against raw run YPP is biased by 3.8 yards -- pass plays simply yield
# more per snap in a functioning offence. "Go where the yards are" naively written
# therefore pushes EVERY offence toward the pass in EVERY game, which is a systematic
# bias wearing the costume of a matchup read. Each play type is judged against its own
# normal instead, so the read says "our run game is beating what a run game should do
# today", which is the actual question.
NORM_RUN_YPP = 3.98
NORM_PASS_YPP = 7.77


# Component switches, for isolating each mechanism when calibrating. ALL TRUE IN PLAY --
# these exist so a calibration script can turn one mechanism off and attribute its effect
# (see `calib_sweep.py`). Anything that flips them must set them back; a season simulated
# with one off would be canon built on a crippled engine.
ENABLE = {"shift": True, "quick": True, "commit": True}


def _clamp(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


def _skill_edge(mine, theirs):
    """How much better I am at this than the coach opposite, as -1..+1.

    A matched pair cancels to zero, so scouting is a contest rather than a free buff.
    """
    return _clamp((mine - theirs) / SKILL_SCALE, -1.0, 1.0)


class Identity:
    """What a team is, from its own roster, scheme and personnel balance."""

    def __init__(self, tg, off_scheme, def_scheme, OFF_SCHEMES, DEF_SCHEMES):
        self.team = tg.team
        osch = OFF_SCHEMES.get(off_scheme, {})
        dsch = DEF_SCHEMES.get(def_scheme, {})
        self.off_scheme = off_scheme
        self.def_scheme = def_scheme
        self.scheme_pass_bias = osch.get("pass_bias", 0.0)
        self.blitz = dsch.get("blitz", 0.0)
        self.cover_scheme = dsch.get("coverage", 0.0)
        self.big_play_allowed = dsch.get("big_play_allowed", 0.0)

        # --- offensive identity: is this team built to throw or to run? ---
        qb = tg.qb()
        arm = tg.fa(qb, "arm") if qb is not None else 4.0
        rb = tg.rbs[0] if tg.rbs else None
        legs = tg.fa(rb, "run") if rb is not None else 4.0
        rblk, pblk = tg.run_block(), tg.pass_block()
        # personnel lean, centred at 0: positive means the passing game is the strength
        self.personnel_pass_lean = _clamp(((arm - legs) + (pblk - rblk)) / 8.0, -1.0, 1.0)
        # what the offence is expected to do, as a probability-space offset
        self.pass_lean = _clamp(self.scheme_pass_bias * 2.2
                                + self.personnel_pass_lean * 0.35, -0.6, 0.6)

        # --- defensive identity: strong where? ---
        self.front = tg.run_def()
        self.cover = tg.coverage() + self.cover_scheme * 4.0
        # positive => the back end is the strength and the front is the soft spot,
        # so the run is the way in. Negative => throw it.
        self.soft_vs_run = _clamp((self.cover - self.front) / 3.0, -1.0, 1.0)

    def __repr__(self):
        return ("<%s %s/%s pass_lean %+.2f front %.2f cover %.2f soft_vs_run %+.2f>"
                % (self.team, self.off_scheme, self.def_scheme, self.pass_lean,
                   self.front, self.cover, self.soft_vs_run))


class Scout:
    """One team's book on its opponent, carried through a single game."""

    def __init__(self, me, them, my_oc, my_dc, their_oc, their_dc):
        self.me, self.them = me, them
        # how well my coordinators win their matchup
        self.off_edge = _skill_edge(my_oc, their_dc)   # my attack vs their read
        self.def_edge = _skill_edge(my_dc, their_oc)   # my read vs their attack

        # ---- the pre-game plan ----
        # Attack the softer half of their defence. Scaled by how much better my OC is
        # than their DC: a weak OC sees the same weakness and cannot use it.
        # Signed, not max(0,...): an OC who is out-coached mis-reads the defence and
        # attacks the wrong half, which is how a skill contest should behave. A matched
        # pair gets a small genuine read; a mismatch gets a real one, either direction.
        self.plan_pass_shift = (-them.soft_vs_run) * PLAN_WEIGHT * (0.35 + 0.65 * self.off_edge)
        # Against a heavy blitz, throw a touch more but get the ball out quicker.
        self.plan_pass_shift += them.blitz * 0.30
        self.quick_game = them.blitz > 0.04

        # My defence commits toward what they are built to do. +1 = all-in on the pass.
        # Likewise signed: a DC who is out-coached commits the wrong way.
        self.commit = _clamp(them.pass_lean * (0.55 + 0.65 * self.def_edge), -0.9, 0.9)

        # ---- what I have actually seen this game ----
        self.seen_run = 0
        self.seen_pass = 0
        self.run_yards = 0.0
        self.pass_yards = 0.0

    # ------------------------------------------------------------------ observing
    def observe(self, kind, yards):
        """Log one play by the team I am defending."""
        if kind == "run":
            self.seen_run += 1
            self.run_yards += yards
        else:
            self.seen_pass += 1
            self.pass_yards += yards
        n = self.seen_run + self.seen_pass
        if n >= MIN_PLAYS_TO_ADAPT:
            observed_pass_rate = self.seen_pass / n
            # drift the commitment toward the observed tendency, at a rate set by how
            # well my DC reads the game
            target = _clamp((observed_pass_rate - 0.5) * 1.6, -0.9, 0.9)
            rate = _clamp(0.10 + 0.14 * self.def_edge, 0.02, 0.30)
            self.commit += (target - self.commit) * rate

    def my_success(self, kind, yards):
        """Log one of MY OWN plays, so my offence can notice what is working."""
        if kind == "run":
            self._my_run = getattr(self, "_my_run", 0) + 1
            self._my_run_y = getattr(self, "_my_run_y", 0.0) + yards
        else:
            self._my_pass = getattr(self, "_my_pass", 0) + 1
            self._my_pass_y = getattr(self, "_my_pass_y", 0.0) + yards

    # ------------------------------------------------------------------ acting
    def pass_shift(self):
        """What to add to pass probability: the plan, plus what is working today."""
        if not ENABLE["shift"]:
            return 0.0
        shift = self.plan_pass_shift
        nr = getattr(self, "_my_run", 0)
        np_ = getattr(self, "_my_pass", 0)
        if nr + np_ >= MIN_PLAYS_TO_ADAPT and nr >= 2 and np_ >= 2:
            rpp = getattr(self, "_my_run_y", 0.0) / nr
            ppp = getattr(self, "_my_pass_y", 0.0) / np_
            # each phase against its OWN normal, so the read is "which of our two
            # attacks is over-performing today", not "which gains more yards per snap"
            edge = _clamp(((ppp - NORM_PASS_YPP) - (rpp - NORM_RUN_YPP)) / 5.0, -1.0, 1.0)
            shift += edge * ADAPT_WEIGHT * (0.4 + 0.6 * self.off_edge)
        return _clamp(shift, -0.30, 0.30)

    def commit_edge(self, play_is_pass):
        """Yards-per-play adjustment for the DEFENCE on the play just called.

        Guessing right helps, guessing wrong hurts, and the magnitudes are symmetric --
        so a committed defence is a gamble, not a free upgrade. Returned as a positive
        number meaning "yards taken away from the offence".
        """
        if not ENABLE["commit"]:
            return 0.0
        c = self.commit
        aligned = c if play_is_pass else -c
        return aligned * COMMIT_EDGE


def build(H, A, off_scheme, def_scheme, OFF_SCHEMES, DEF_SCHEMES):
    """Return (scout_for_H, scout_for_A). Each one is that team's book on the other."""
    idH = Identity(H, off_scheme[H.team], def_scheme[H.team], OFF_SCHEMES, DEF_SCHEMES)
    idA = Identity(A, off_scheme[A.team], def_scheme[A.team], OFF_SCHEMES, DEF_SCHEMES)
    sH = Scout(idH, idA, H.oc_skill, H.dc_skill, A.oc_skill, A.dc_skill)
    sA = Scout(idA, idH, A.oc_skill, A.dc_skill, H.oc_skill, H.dc_skill)
    return sH, sA, idH, idA
