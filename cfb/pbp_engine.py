"""Roiland CFB v2 - play-by-play engine (Phase 2).
Adds: defensive attention / usage-efficiency tradeoff, generational exceptions, fatigue,
reputation feedback, in-engine injuries with in-game exits + severity + flavor text.
Deterministic: same seed + rosters + availability => identical game.
"""
import pickle, random, math

with open('/home/claude/cfb2/state/universe.pkl','rb') as f:
    U = pickle.load(f)
with open('/home/claude/cfb2/state/rosters.pkl','rb') as f:
    ROSTERS = pickle.load(f)
with open('/home/claude/cfb2/state/coaches.pkl','rb') as f:
    COACHES = pickle.load(f)

GENERATIONAL = 8.9   # ~top 1% hidden ability

# injury calibration (2039 end): contact on the ball, on the tackle, and per-snap exposure
INJ_BALL = 0.85
INJ_TACKLE = 1.0
INJ_SNAP_RISK = {"OL": 0.055, "DL": 0.042, "DB": 0.04, "LB": 0.008}
INJ_CATCH = 1.25
INJ_MINOR = ["ankle sprain","hamstring tightness","shoulder stinger","bruised ribs","hip pointer","concussion protocol"]
INJ_MED   = ["high-ankle sprain","MCL sprain","broken hand","turf toe","AC joint sprain","quad strain"]
INJ_SEASON= ["torn ACL","ruptured Achilles","broken leg","torn labrum"]

def depth(team, pos, n=None, exclude=frozenset()):
    pool = [p for p in ROSTERS[team] if p["pos"] == pos and p["pid"] not in exclude]
    pool.sort(key=lambda p: -(p["abil"] * (1 + 0.25*math.tanh(p.get("rep",0.0)))))
    return pool if n is None else pool[:n]

class TeamGame:
    def __init__(self, team, rng, unavailable=frozenset(), recently_returned=frozenset()):
        self.team = team; self.rng = rng
        self.ex = set(unavailable)
        self.recent = set(recently_returned)
        self.rebuild()
        self.form = {}
        for pl in ROSTERS[team]:
            self.form[pl["pid"]] = math.exp(rng.gauss(0, 0.35))
        self.garbage = False
        cs = COACHES[team]
        self.oc_skill = cs["OC"]["skill"]; self.dc_skill = cs["DC"]["skill"]; self.hc_skill = cs["HC"]["skill"]
        self.run_bias = 0.5 + (rng.random()-0.5)*0.16
        self.touches = {}     # pid -> touches+targets this game (usage cap + fatigue)
        self.game_penalties = {}  # pid -> penalties committed this game (workload effect)
        cs2 = COACHES.get(self.team, {})
        # disciplined coaches bench offenders faster; derive a bench tendency from team_discipline
        self.bench_tendency = 2.0 - cs2.get("team_discipline", 1.0)  # ~0.8 (lax) .. ~1.18 (strict)
        self._threat_profile()

    def rebuild(self):
        ex = self.ex
        self.qbs = depth(self.team,"QB",3,ex); self.rbs = depth(self.team,"RB",4,ex)
        self.wrs = depth(self.team,"WR",6,ex); self.tes = depth(self.team,"TE",3,ex)
        self.ols = depth(self.team,"OL",8,ex); self.dls = depth(self.team,"DL",6,ex)
        self.lbs = depth(self.team,"LB",5,ex); self.cbs = depth(self.team,"CB",4,ex)
        self.ss  = depth(self.team,"S",4,ex)
        self.k   = depth(self.team,"K",1,ex);  self.p  = depth(self.team,"P",1,ex)

    def _threat_profile(self):
        """Spec 3: attention = f(share of offense, supporting cast)."""
        threats = sorted(self.wrs[:5]+self.tes[:2]+self.rbs[:2], key=lambda p: -p["abil"])[:6]
        vals = [max(1.0, p["abil"]) for p in threats]
        tot = sum(vals) if vals else 1.0
        cast = (sum(vals[1:4])/max(1,len(vals[1:4]))) if len(vals) > 1 else 4.0
        cast_amp = 1 + max(0.0, (6.0-cast))*0.38      # weak cast => defenses key harder
        self.attention = {}
        self.exp_share = {}
        for p, v in zip(threats, vals):
            share = v/tot
            att = share * cast_amp
            if p["abil"] >= GENERATIONAL: att *= 0.62   # generational resistance
            self.attention[p["pid"]] = att
            self.exp_share[p["pid"]] = share

    def knock_out(self, pl):
        self.ex.add(pl["pid"]); self.rebuild()

    def fa(self, pl, attr):
        base = pl.get("attrs",{}).get(attr, pl["abil"])
        return base * self.form.get(pl["pid"], 1.0)
    def f(self, pl): return pl["abil"] * self.form.get(pl["pid"], 1.0)

    def qb(self):  return (self.qbs[1] if self.garbage and len(self.qbs)>1 else (self.qbs[0] if self.qbs else None))
    def kicker(self): return self.k[0] if self.k else None
    def punter(self): return self.p[0] if self.p else None

    def usage_mult(self, pl):
        """Soft usage cap: weight down over-fed players unless generational or hot (form)."""
        tot = max(1, sum(self.touches.values()))
        if tot < 8: return 1.0
        share = self.touches.get(pl["pid"],0)/tot
        cap = 0.40 if pl["abil"] >= GENERATIONAL else 0.28
        hot = self.form.get(pl["pid"],1.0) > 1.22
        eff_cap = cap * (1.15 if hot else 1.0)
        if share > eff_cap: return 0.33
        if share > eff_cap*0.85: return 0.68
        return 1.0

    def rep_mult(self, pl):
        return max(0.7, min(1.3, 1 + 0.25*math.tanh(pl.get("rep",0.0))))

    def penalty_mult(self, pl):
        """Excessive in-game penalties reduce a player's workload — the coach benches
        repeat offenders. Effect scales with count AND the player's role/discipline:
        skill players on a short leash lose touches faster than trench players."""
        n = self.game_penalties.get(pl["pid"], 0)
        if n < 2: return 1.0
        # base reduction per foul beyond the first; disciplined coaches yank quicker
        per = 0.16 * self.bench_tendency
        # star players (high ability / generational) get a longer leash
        leash = 1.0 + (0.5 if pl["abil"] >= GENERATIONAL else (0.2 if pl["abil"] >= 8.2 else 0.0))
        reduction = min(0.72, (n-1) * per / leash)
        return max(0.28, 1.0 - reduction)

    def pick_rb(self):
        pool = self.rbs[1:] if self.garbage and len(self.rbs)>1 else self.rbs
        if not pool: return None
        w = [max(0.05,(self.f(p))**2.2) * self.usage_mult(p) * self.rep_mult(p) * self.penalty_mult(p) for p in pool]
        w[0] *= 3.8
        if len(w)>1: w[1] *= 1.2
        return self.rng.choices(pool, weights=w)[0]

    def pick_target(self):
        pool = (self.wrs[2:] + self.tes[1:] + self.rbs[1:]) if self.garbage else \
               (self.wrs[:5] + self.tes[:2] + self.rbs[:2])
        pool = [p for p in pool if p]
        if not pool: return None
        w = []
        for p in pool:
            base = max(0.05, self.fa(p,"hands") * self.fa(p,"route") if p["pos"] in ("WR","TE","ATH") else self.fa(p,"hands")*2.2)
            if p["pos"] == "RB": base *= 0.45
            if p["pos"] == "TE": base *= 0.75
            w.append((base**1.6) * self.usage_mult(p) * self.rep_mult(p) * self.penalty_mult(p))
        return self.rng.choices(pool, weights=w)[0]

    def pick_tackler(self, vs_pass):
        if vs_pass:
            pool = self.lbs[:4]+self.cbs[:3]+self.ss[:3]+self.dls[:2]
            wts  = [1.1]*len(self.lbs[:4])+[1.15]*len(self.cbs[:3])+[1.2]*len(self.ss[:3])+[0.4]*len(self.dls[:2])
        else:
            pool = self.dls[:5]+self.lbs[:5]+self.ss[:2]+self.cbs[:2]
            wts  = [1.0]*len(self.dls[:5])+[1.5]*len(self.lbs[:5])+[0.7]*len(self.ss[:2])+[0.4]*len(self.cbs[:2])
        pool2, w2 = [], []
        for p, w in zip(pool, wts):
            pool2.append(p); w2.append(w * max(0.3, self.fa(p,"tkl")))
        return self.rng.choices(pool2, weights=w2)[0] if pool2 else None

    def pass_block(self): return sum(self.fa(p,"pblk") for p in self.ols[:5])/max(1,len(self.ols[:5]))
    def run_block(self):  return sum(self.fa(p,"rblk") for p in self.ols[:5])/max(1,len(self.ols[:5]))
    def pass_rush(self):
        top = sorted((self.fa(p,"rush") for p in self.dls[:5]),reverse=True)[:4]
        return sum(top)/max(1,len(top))
    def run_def(self):
        a = sum(self.fa(p,"rdef") for p in self.dls[:5])/max(1,len(self.dls[:5]))
        b = sum(self.fa(p,"tkl") for p in self.lbs[:4])/max(1,len(self.lbs[:4]))
        return (a+b)/2
    def coverage(self):
        c1 = sum(self.fa(p,"cov") for p in self.cbs[:3])/max(1,len(self.cbs[:3]))
        c2 = sum(self.fa(p,"cov") for p in self.ss[:2])/max(1,len(self.ss[:2]))
        c3 = sum(self.fa(p,"cov") for p in self.lbs[:3])/max(1,len(self.lbs[:3]))
        return c1*0.6 + c2*0.25 + c3*0.15
    def ballhawk(self):
        pool = self.cbs[:3]+self.ss[:2]
        return sum(self.fa(p,"ball") for p in pool)/max(1,len(pool))

def bump(d, pl, key, amt=1):
    if pl is None: return
    s = d.setdefault(pl["pid"], {"name": pl["name"], "team": pl["team"], "pos": pl["pos"], "cls": pl["cls"]})
    s[key] = s.get(key, 0) + amt

def simulate_game(home, away, seed, site="home", unavailable_home=frozenset(), unavailable_away=frozenset(),
                  rivalry=False, keep_pbp=True, postseason=False,
                  recently_returned_home=frozenset(), recently_returned_away=frozenset(), hfa_override=None):
    rng = random.Random(seed)
    H = TeamGame(home, rng, unavailable_home, recently_returned_home)
    A = TeamGame(away, rng, unavailable_away, recently_returned_away)
    hfa_pts = (hfa_override if hfa_override is not None else COACHES[home]["hfa_base"]) if site == "home" else 0.0
    coach_edge = {home: (H.hc_skill-5)*0.05, away: (A.hc_skill-5)*0.05}

    score = {home: 0, away: 0}
    stats = {}; pbp = []; scoring_plays = []; injuries = []; clutch = []
    # Turnovers that did NOT score. A pick-six or a fumble returned for a touchdown is
    # already in scoring_plays, so recording it here too would show it twice on the
    # timeline; these are the ones that change possession and nothing else.
    turnovers = []

    # ---- WEATHER (deterministic per seed) ----
    _wr = random.Random(seed ^ 0x5EED)
    dome = COACHES[home].get("dome", False) if site == "home" else False
    if dome:
        weather = {"wind": 0, "precip": 0, "cold": 0, "dome": True, "label": "dome"}
    else:
        roll = _wr.random()
        if roll < 0.60:
            weather = {"wind": _wr.uniform(0, 1.5), "precip": 0, "cold": 0, "dome": False, "label": "clear"}
        elif roll < 0.78:
            weather = {"wind": _wr.uniform(1.5, 4.0), "precip": 0, "cold": 0, "dome": False, "label": "windy"}
        elif roll < 0.90:
            weather = {"wind": _wr.uniform(1, 3), "precip": _wr.uniform(0.3, 1.0), "cold": 0, "dome": False, "label": "rain"}
        else:
            weather = {"wind": _wr.uniform(1, 3.5), "precip": _wr.uniform(0, 0.7), "cold": 1, "dome": False, "label": "cold/snow"}
    # ---- MOMENTUM (running signed value; nudges wp + perf slightly, mostly narrative) ----
    momentum = {"val": 0.0, "team": None, "swings": []}
    # ---- SCHEMES ----
    OFF_SCHEMES = U.get("OFF_SCHEMES", {}); DEF_SCHEMES = U.get("DEF_SCHEMES", {})
    off_scheme = {home: COACHES[home].get("off_scheme", "Pro-Style"), away: COACHES[away].get("off_scheme", "Pro-Style")}
    def_scheme = {home: COACHES[home].get("def_scheme", "4-3 Base"), away: COACHES[away].get("def_scheme", "4-3 Base")}
    # ---- SCOUTING: each side's book on the other (see scouting.py) ----
    import scouting as SC
    _scout_h, _scout_a, _ident_h, _ident_a = SC.build(H, A, off_scheme, def_scheme,
                                                      U["OFF_SCHEMES"], U["DEF_SCHEMES"])
    SCOUT = {home: _scout_h, away: _scout_a}
    IDENT = {home: _ident_h, away: _ident_a}

    state = {"q": 1, "clock": 900, "poss": None, "spot": 25, "down": 1, "dist": 10}
    opener = rng.choice([home, away])

    def other(t): return away if t == home else home
    def TG(t): return H if t == home else A

    def log(desc, t=None):
        mm, ss = state["clock"]//60, state["clock"]%60
        entry = {"q": state["q"], "clock": f"{mm}:{ss:02d}", "team": t or state["poss"],
                 "down": state["down"], "dist": state["dist"], "spot": state["spot"], "desc": desc}
        if keep_pbp:
            pbp.append(entry)
        # always capture the final 5:00 of regulation and all overtime, plus the running score,
        # so close games can have their crunch-time sequence surfaced later (kept compact).
        if state["q"] >= 4 and (state["q"] > 4 or state["clock"] <= 300):
            clutch.append({**entry, "score": (score[home], score[away])})

    def runoff(sec): state["clock"] = max(0, state["clock"] - sec)

    # ---- TIMEOUTS (2035 endgame overhaul) ----
    # The engine had no timeout model at all, so a trailing team could never stop the
    # clock and late comebacks were rarer than canon (30.0% one-score games against
    # canon's 36.8%). Three per half each, reset at the break.
    timeouts = {home: 3, away: 3}

    def maybe_defense_timeout(base_sec):
        """The trailing DEFENSE burns a timeout to stop a running clock late."""
        d = other(state["poss"])
        if timeouts[d] <= 0 or base_sec <= 10:
            return base_sec
        _deficit = score[state["poss"]] - score[d]
        if _deficit <= 0:
            return base_sec                      # they are ahead or tied; let it run
        if _deficit > 16:
            return base_sec                      # three scores down: the clock is moot
        # Timeouts are scarce and spending them early is the classic coaching error.
        # A staff holds them until the clock is genuinely the binding constraint --
        # roughly the last two minutes, stretched a little when two scores behind and
        # they will need the ball twice.
        _window = 135 + (45 if _deficit > 8 else 0)
        urgent = (state["q"] == 4 and state["clock"] <= _window) or \
                 (state["q"] == 2 and state["clock"] <= 75)
        if not urgent:
            return base_sec
        timeouts[d] -= 1
        log(f"Timeout {d} ({timeouts[d]} left)", d)
        return 3

    def add_momentum(team, amount):
        # momentum accrues to a team; decays and flips. Big plays swing it.
        if momentum["team"] == team:
            momentum["val"] = min(6.0, momentum["val"] + amount)
        else:
            momentum["val"] -= amount
            if momentum["val"] < 0:
                momentum["team"] = team; momentum["val"] = min(6.0, -momentum["val"])
        momentum["swings"].append({"q": state["q"], "team": team, "val": round(momentum["val"], 1)})

    # ----- penalties (real-CFB set, discipline-weighted) -----
    import penalties as PEN
    import special_teams as ST
    def team_disc(tm):
        return COACHES.get(tm, {}).get("team_discipline", 1.0)
    pen_count = {home: 0, away: 0}   # accepted penalties per team
    pen_yards = {home: 0, away: 0}
    def record_penalty(name, team_committing, offender, yds_applied):
        pen_count[team_committing] += 1
        pen_yards[team_committing] += abs(yds_applied)
        if offender is not None:
            bump(stats, offender, "Penalties")
            # track penalty yards charged to the player's team for their account
            bump(stats, offender, "PenYds", abs(yds_applied))
            # per-game count on the committing team's TeamGame -> feeds workload reduction
            tg = H if team_committing == home else A
            tg.game_penalties[offender["pid"]] = tg.game_penalties.get(offender["pid"], 0) + 1
        box_pen_log.append({"q": state["q"], "clock": state["clock"], "team": team_committing,
                            "name": name, "player": (offender or {}).get("name") if offender else None,
                            "yards": yds_applied})
    box_pen_log = []

    def eff_edge(off, deff, off_val, def_val):
        # EDGE_SCALE amplifies the part of the gap that comes from the two TEAMS -- unit
        # strength and coaching -- and deliberately leaves home field alone, since the
        # stadium is not a talent difference and scaling it would only inflate the home
        # win rate, which already measures correctly.
        gap = (off_val - def_val) * EDGE_SCALE
        if rivalry: gap *= RIVALRY_GAP
        gap += (coach_edge[off.team] - coach_edge[deff.team]) * EDGE_SCALE
        gap += hfa_pts*0.10 if off.team == home else -hfa_pts*0.10
        return gap

    def check_garbage():
        margin = abs(score[home]-score[away])
        if (state["q"] == 4 and margin >= 25) or (state["q"] == 4 and state["clock"] < 300 and margin >= 18) \
           or (state["q"] == 3 and margin >= 28):
            H.garbage = A.garbage = True

    # ----- injuries (spec 5) -----
    # 2039 end (Dan's injury audit): the ball-carrier roll made running backs 49% of
    # all injuries and linemen 0.2% -- OL got hurt twice in a season, league-wide --
    # because only the player with the ball and his tackler ever rolled, at the
    # highest contact. Contact on the ball is cut, tacklers roll at full contact, and
    # every lineman and defensive back takes a small per-snap exposure (trench_injury)
    # instead of the old once-in-a-blue-moon ambient roll. Calibrated on 1,000 sample
    # games to ~0.65 time-loss injuries per team-game with position shares near the
    # real distribution (OL/DL ~15% each, DBs ~20%, RB ~12%).
    POS_RISK = {"RB":0.8,"QB":1.3,"WR":1.0,"TE":1.6,"OL":1.0,"DL":1.0,"LB":1.0,"CB":1.0,"S":1.0,"K":0.15,"P":0.15,"ATH":1.0}
    SNAP_RISK = INJ_SNAP_RISK
    def injury_check(O_or_D, pl, contact=1.0):
        if pl is None or pl["pid"] in [i["pid"] for i in injuries]: return False
        # durability: steeper than before (0.5+1.6x) so the hidden trait separates players
        risk = 0.0038 * contact * POS_RISK.get(pl["pos"],1.0) * (0.35 + 2.0*(1.0 - pl["dur"]))
        if pl["pid"] in O_or_D.recent: risk *= 1.6
        if rng.random() >= risk: return False
        r = rng.random()
        if postseason:  # gut it out
            sev = "minor" if r < 0.70 else ("med" if r < 0.92 else "season")
        else:
            sev = "minor" if r < 0.54 else ("med" if r < 0.82 else "season")
        if sev == "minor": weeks = rng.choice([1,1,2]); flavor = rng.choice(INJ_MINOR)
        elif sev == "med": weeks = rng.randint(3,6);    flavor = rng.choice(INJ_MED)
        else:              weeks = 99;                  flavor = rng.choice(INJ_SEASON)
        injuries.append({"pid": pl["pid"], "name": pl["name"], "team": pl["team"], "pos": pl["pos"],
                         "weeks_out": weeks, "desc": flavor, "q": state["q"]})
        O_or_D.knock_out(pl)
        log(f"INJURY - {pl['name']} ({pl['pos']}) leaves the game ({flavor})", pl["team"])
        return True

    def ambient_injury():
        """Per-snap exposure for everyone who collides without the ball: the five
        linemen and four down linemen on every play, the secondary on every play at a
        lower rate (they roll again as tacklers)."""
        for side, pool, c in ((O_now[0], O_now[0].ols[:5], SNAP_RISK["OL"]),
                              (O_now[1], O_now[1].dls[:4], SNAP_RISK["DL"]),
                              (O_now[1], O_now[1].cbs[:2] + O_now[1].ss[:2], SNAP_RISK["DB"]),
                              (O_now[1], O_now[1].lbs[:3], SNAP_RISK["LB"])):
            for pl in pool:
                injury_check(side, pl, contact=c)
    O_now = [H, A]

    def touch(O, pl):
        O.touches[pl["pid"]] = O.touches.get(pl["pid"], 0) + 1

    def fatigue_malus(O, pl):
        if state["q"] < 4: return 0.0
        t = O.touches.get(pl["pid"], 0)
        return -0.06 * max(0, t - 17)

    # ----- plays -----
    def _carry(O, D, ball, designed_qb=False, scramble=False):
        blk = eff_edge(O, D, O.run_block(), D.run_def())
        att_pen = max(0.0, O.attention.get(ball["pid"], 0) - 0.24) * 2.6
        run_attr = "run" if ball["pos"]=="RB" else "mob"
        # 0.42 made a full point of blocking edge worth less than half a yard a carry, so
        # the engine separated teams far less than `season.win_prob` assumed: a 1.0 talent
        # gap produced a 71% win rate where win_prob said 85%. 0.65 narrows that and is
        # what turns a mismatch into a scoreboard margin instead of a close game.
        base = 2.95 + 0.34*(O.fa(ball, run_attr) - 5) + 0.65*blk - att_pen + fatigue_malus(O, ball) - CAL_RUN_DAMP
        base -= state.get("_commit", 0.0)        # defence guessed run (or did not)
        if designed_qb: base += 0.35              # designed QB runs are schemed for yards
        if scramble:    base += 0.15              # scrambles: broken play, some open grass
        yds = rng.gauss(base, (3.35 if not scramble else 4.0) * NOISE_SCALE)
        spd = O.fa(ball, "spd" if ball["pos"]=="RB" else "mob")
        breakaway = 0.047 + max(0, spd-6)*0.010
        if scramble: breakaway += 0.02
        if rng.random() < breakaway:
            yds += rng.expovariate(1/13.0) * (0.7 + spd/12)
        yds = int(round(max(-5, yds))); yds = min(yds, 100 - state["spot"])
        fumble = rng.random() < (0.008 if ball["pos"]=="RB" else 0.011)  # QBs fumble a bit more running
        bump(stats, ball, "RushAtt"); bump(stats, ball, "RushYds", yds)
        touch(O, ball)
        tkl = D.pick_tackler(vs_pass=False)
        if not fumble: bump(stats, tkl, "Tackles")
        # QBs take more contact risk running than a back does
        injury_check(O, ball, contact=1.2 if ball["pos"]=="QB" else INJ_BALL)
        if tkl: injury_check(D, tkl, contact=INJ_TACKLE)
        typ = "qbrun" if (designed_qb or scramble) else "run"
        return {"type":typ,"player":ball,"yds":yds,"fumble":fumble,"tackler":tkl,"scramble":scramble}

    def run_play(O, D):
        rb = O.pick_rb()
        qb = O.qb()
        # designed QB run: probability scales with true mobility (dual-threats ~ up to ~22% of runs)
        if qb is not None:
            mob = O.fa(qb, "mob")
            # designed-run rate rises with mobility but saturates (elite dual-threats ~13-15%, not 22%)
            designed_p = min(0.15, max(0.0, (mob - 4.5) * 0.032))
            # hard per-game realism cap: no QB should approach RB-level carry volume
            qb_carries = stats.get(qb["pid"], {}).get("RushAtt", 0)
            if qb_carries >= 20:
                designed_p *= 0.15        # sharply taper once a QB already has a heavy load
            if rb is not None and rng.random() < designed_p:
                return _carry(O, D, qb, designed_qb=True)
        if rb is None: rb = qb
        if rb is None: return {"type":"kneel","yds":0}
        return _carry(O, D, rb)

    def pass_play(O, D, need_chunk=False):
        qb = O.qb()
        if qb is None: return run_play(O, D)
        prot = eff_edge(O, D, O.pass_block(), D.pass_rush())
        mob = O.fa(qb, "mob")
        # under pressure, a mobile QB may scramble instead of eating a sack or forcing a throw
        pressure = max(0.0, 0.09 - prot*0.02)            # how often the pocket breaks down
        scramble_p = pressure * max(0.0, (mob - 4.0) * 0.16)
        if stats.get(qb["pid"], {}).get("RushAtt", 0) >= 18:
            scramble_p *= 0.25
        if rng.random() < scramble_p:
            return _carry(O, D, qb, scramble=True)
        sack_p = min(0.16, max(0.015, 0.068 - prot*0.016 - max(0, mob-5)*0.009))
        if rng.random() < sack_p:
            loss = -int(round(rng.uniform(4, 9)))
            # when backed up near own goal, a sack CAN reach the end zone (safety) — but not
            # unrealistically far; cap the backward travel just past the goal line.
            if state["spot"] + loss < 0:
                loss = max(loss, -(state["spot"] + rng.randint(1, 3)))
            sacker_pool = D.dls[:4] + D.lbs[:2]
            if sacker_pool:
                sw = [max(0.2, D.fa(p,"rush"))**2 for p in sacker_pool]
                sacker = rng.choices(sacker_pool, weights=sw)[0]
                bump(stats, sacker, "Sacks"); bump(stats, sacker, "Tackles")
            else: sacker = None
            bump(stats, qb, "SackedFor", -loss)
            injury_check(O, qb, contact=1.2)
            return {"type":"sack","player":qb,"yds":loss,"fumble":rng.random()<0.02,"tackler":sacker}
        tgt = O.pick_target()
        if tgt is None: return run_play(O, D)
        arch = tgt.get("arch","")
        if arch == "Deep Threat": air_mu, air_sd = 14.0, 8.0
        elif arch == "Possession": air_mu, air_sd = 7.5, 4.0
        elif arch == "Slot Technician": air_mu, air_sd = 8.5, 4.5
        elif tgt["pos"] == "TE": air_mu, air_sd = 7.0, 4.0
        elif tgt["pos"] == "RB": air_mu, air_sd = 1.5, 2.5
        else: air_mu, air_sd = 9.0, 5.5
        if need_chunk: air_mu += 5.0
        # ---- the vertical shot ----
        # Without this the deepest ball the engine could draw was a Deep Threat's 11.4-yard
        # mean plus noise, so 40+ air yards effectively never happened: across 3,689
        # completions in a 106-game season the longest was 68 yards and not one reached 70.
        # Runs already had a breakaway and could produce an 80-yard touchdown; the passing
        # game had no equivalent, so the sport's signature play -- the bomb to a receiver
        # behind the secondary -- could not occur at all.
        #
        # This does not make deep balls easy. `comp` already carries -0.017 for every yard
        # of air past 8, so a 40-yard throw lands on the 0.22 completion floor, which is
        # roughly what a real deep shot completes at. The shot is a CHOICE to take a low
        # percentage swing, not a free play.
        if rng.random() < SHOT_RATE * (1.7 if arch == "Deep Threat" else 1.0) \
                                    * (2.0 if need_chunk else 1.0):
            air_mu += SHOT_DEPTH
            air_sd += 4.0
        air_mu = max(1.2, air_mu - CAL_AIR_SHIFT)
        air = max(-3, rng.gauss(air_mu, air_sd))
        _qys = stats.get(qb["pid"], {}).get("PassYds", 0)
        if _qys > 400:
            air *= max(0.5, 1 - (_qys - 400)*0.004)   # defenses shell deep; throws shorten
        cov = D.coverage() + state.get("_commit", 0.0) * 0.55   # sitting on the pass, or not
        att_pen = max(0.0, O.attention.get(tgt["pid"], 0) - 0.20) * 0.85
        qb_sofar = stats.get(qb["pid"], {}).get("PassYds", 0)
        tgt_sofar = stats.get(tgt["pid"], {})
        vol_pen = max(0, qb_sofar - 350)*0.0012 + max(0, qb_sofar - 430)*0.0050 \
                + max(0, tgt_sofar.get("Targets", 0) - 10)*0.016 \
                + max(0, tgt_sofar.get("RecYds", 0) - 150)*0.0013
        comp = 0.578 + CAL_COMP_BASE + (O.fa(qb,"acc")-5)*0.026 + (O.fa(tgt,"hands")-5)*0.016 + eff_edge(O,D,0,0)*0.01 \
               - (cov-5)*0.033 - max(0, air-8)*0.017 - att_pen + fatigue_malus(O, tgt)*0.05
        comp = min(0.78, max(0.22, comp)) - CAL_COMP_DAMP
        comp = max(0.05, comp - vol_pen)   # volume clamp pierces the floor
        touch(O, tgt)
        if rng.random() < comp:
            yac_pen = max(0.0, O.attention.get(tgt["pid"],0) - 0.20) * 8.0 \
                    + max(0, stats.get(tgt["pid"], {}).get("RecYds", 0) - 140)*0.017
            yac = max(0, rng.gauss(2.8 + CAL_YAC_BONUS + (O.fa(tgt,"spd")-5)*0.55 - yac_pen, 2.9 * NOISE_SCALE))
            if rng.random() < 0.032 + max(0, O.fa(tgt,"spd")-6.5)*0.015:
                # NOT scaled by receiver speed, though the run breakaway is. Tried it: it
                # lifts the whole distribution rather than just the tail and took yards per
                # completion from 13.4 to 14.3 against a real-world ~12. The tail belongs
                # to the vertical shot above, which pays for itself in completion rate.
                yac += rng.expovariate(1/14.0)
            yds = int(round(air + yac)); yds = min(yds, 100 - state["spot"])
            bump(stats, qb, "Comp"); bump(stats, qb, "Att"); bump(stats, qb, "PassYds", yds)
            bump(stats, tgt, "Rec"); bump(stats, tgt, "RecYds", yds); bump(stats, tgt, "Targets")
            tkl = D.pick_tackler(vs_pass=True)
            bump(stats, tkl, "Tackles")
            injury_check(O, tgt, contact=INJ_CATCH)
            if tkl: injury_check(D, tkl, contact=INJ_TACKLE)
            return {"type":"comp","player":qb,"target":tgt,"yds":yds,"fumble":rng.random()<0.004,"tackler":tkl}
        else:
            bump(stats, tgt, "Targets")
            int_p = 0.047 + max(0, air-10)*0.004 + (D.ballhawk()-5)*0.010 - (O.fa(qb,"acc")-5)*0.009
            if rng.random() < max(0.015, min(0.14, int_p)):
                picker_pool = D.cbs[:3]+D.ss[:2]+D.lbs[:2]
                pw = [max(0.2, D.fa(p,"ball"))**1.6 * (0.3 if p["pos"]=="LB" else 1.0) for p in picker_pool]
                picker = rng.choices(picker_pool, weights=pw)[0]
                bump(stats, qb, "Att"); bump(stats, qb, "INT")
                bump(stats, picker, "INT_def")
                ret = int(max(0, rng.gauss(8, 9)))
                # HOUSE CALL: a defender with open field can take it the distance regardless of
                # spot (this is how most real pick-6s happen). Scaled by ball skill + speed.
                house = min(0.04, 0.012 + D.fa(picker,"ball")*0.0025 + D.fa(picker,"speed")*0.0015)
                take_it_back = rng.random() < house
                return {"type":"int","player":qb,"target":tgt,"picker":picker,"ret":ret,
                        "air":int(air),"house_call":take_it_back}
            bump(stats, qb, "Att")
            return {"type":"inc","player":qb,"target":tgt,"yds":0}

    def try_fg(O):
        k = O.kicker(); dist = (100 - state["spot"]) + 17
        if k is None: return False, dist, None
        p = 0.985 - max(0, dist-20)*0.0125 - (5-O.fa(k,"accy"))*0.018 - max(0,dist-49)*0.012
        good = rng.random() < max(0.03, min(0.99, p))
        bump(stats, k, "FGAtt")
        if good: bump(stats, k, "FGMade")
        return good, dist, k

    def punt(O):
        recv = A if O.team == home else H
        res = ST.punt(rng, O, recv, state["spot"], weather)
        p = O.punter()
        if p and res.get("net"): bump(stats, p, "Punts"); bump(stats, p, "PuntYds", int(res["net"]))
        if res["type"] == "return_td":
            # returner takes it to the house
            r = res["ret"]
            log(f"Punt returned for a TOUCHDOWN by {r['name']}!", recv.team)
            return ("return_td", recv.team, r)
        if res["type"] == "block":
            log(f"PUNT BLOCKED! {recv.team} takes over", recv.team)
            return ("block", recv.team, res["new_spot"])
        if res["type"] == "muff":
            log(f"MUFFED PUNT! {O.team} recovers", O.team)
            return ("muff", O.team, res["new_spot"])
        if res.get("returner") and res.get("ret_yards", 0) > 0:
            bump(stats, res["returner"], "PuntRetYds", res["ret_yards"])
        return ("punt", recv.team, res["new_spot"])

    def extra_point(O):
        k = O.kicker()
        good = rng.random() < (0.985 - (5-O.fa(k,"accy"))*0.01 if k else 0.9)
        if k: bump(stats, k, "XPAtt")
        if good and k: bump(stats, k, "XPMade")
        return good

    def two_point(O, D):
        sv = state["dist"]; state["dist"] = 3
        res = run_play(O, D) if rng.random() < 0.45 else pass_play(O, D)
        state["dist"] = sv
        return res.get("yds",0) >= 3 and res["type"] in ("run","qbrun","comp")

    def should_go_2pt(t):
        # called AFTER the 6 points are on the board; margin IS the post-TD margin
        if state["q"] > 4:
            return True   # ROILAND RULE: 2-pt conversion required from the first OT
        margin = score[t] - score[other(t)]
        agg = COACHES[t]["HC"].get("aggression", 0.5)
        late = state["q"] == 4 and state["clock"] < 420
        if not late:
            return rng.random() < 0.006 * agg      # surprise 2s: coach-flavored, league rate unchanged
        # CONSENSUS: every coach goes, whatever his temperament.
        #
        # +5 was moved here from the aggressive tier on 2026-10-09 after Orlot Western
        # kicked at +5 against Clark and lost 34-33 to a touchdown and extra point -- the
        # exact failure the two-point attempt exists to prevent. Up 6 their touchdown and
        # extra point WINS; up 7 it only ties. Computed over one opposing possession it is
        # worth +9.5 points of win probability, the largest edge anywhere on the chart and
        # bigger than -2, which was already consensus. A 0.27-aggression coach declining
        # it was the engine working as written, and the engine was written wrong.
        if margin in (-2, -5, -11, 5):
            return True
        # ANALYTICS: defensible either way, so temperament decides. +4 added at the same
        # time: it only clears the kick when the opponent is likely to score, so it is a
        # real judgement call rather than a mistake.
        if margin in (-12, -9, -8, 1, 4):
            return rng.random() < agg
        return False

    def touchdown(O, D, scorer, kind, yds):
        score[O.team] += 6
        desc = f"{scorer['name']} {yds}-yd {kind} TD"
        if kind == "pass": bump(stats, O.qb(), "PassTD"); bump(stats, scorer, "RecTD")
        elif kind == "rush": bump(stats, scorer, "RushTD")
        elif kind == "INT return": bump(stats, scorer, "DefTD")
        # OT WALK-OFF: if the second team in an OT period takes the lead with this TD,
        # the game is already won — no conversion is attempted.
        if state.get("ot_second") and score[O.team] > score[other(O.team)]:
            desc += " (game-winning TD)"
            scoring_plays.append({"q": state["q"], "clock": state["clock"], "team": O.team,
                                  "desc": desc, "score": (score[home], score[away])})
            log(f"TOUCHDOWN - {desc} - GAME OVER  [{home} {score[home]} - {score[away]} {away}]", O.team)
            state["ot_walkoff"] = True
            return
        if should_go_2pt(O.team):
            sp = state["spot"]; state["spot"] = 97
            ok = two_point(O, D); state["spot"] = sp
            if ok: score[O.team] += 2; desc += " (2pt good)"
            else: desc += " (2pt failed)"
        else:
            if extra_point(O): score[O.team] += 1
            else: desc += " (XP missed)"
        scoring_plays.append({"q": state["q"], "clock": state["clock"], "team": O.team,
                              "desc": desc, "score": (score[home], score[away])})
        log(f"TOUCHDOWN - {desc}  [{home} {score[home]} - {score[away]} {away}]", O.team)

    def drive(possessor, start_spot, ot=False, resume=None):
        # `resume` carries (down, dist) when a drive is continuing across a quarter
        # break rather than beginning after a kickoff. Without it the loop restarted
        # the possession from a kickoff spot at first-and-ten, which moved the ball
        # backward ~24 yards about 1.3 times a game -- 58% of the time from scoring
        # range. See the quarter-break note in PENDING.md.
        state["poss"] = possessor; state["spot"] = max(1, min(99, start_spot))
        if resume is not None:
            state["down"], state["dist"] = resume
            state["dist"] = max(1, min(state["dist"], 100 - state["spot"]))
        else:
            state["down"] = 1; state["dist"] = min(10, 100-state["spot"])
        O, D = TG(possessor), TG(other(possessor))
        O_now[0], O_now[1] = O, D
        while True:
            check_garbage(); ambient_injury()
            if not ot and state["clock"] <= 0: return "clock"
            margin = score[possessor] - score[other(possessor)]
            two_min = (state["q"] in (2,4)) and state["clock"] <= 120
            hurry = two_min and margin <= 0
            # END-OF-HALF AWARENESS: last snap of Q2/Q4 (any down)
            # VICTORY FORMATION (2035 overhaul): a leading team kneels as soon as it can
            # actually run the clock out, not only in the last seven seconds. Each kneel
            # burns about 40 seconds unless the defense stops it with a timeout, so the
            # lead is only safe when the snaps in hand outlast their remaining timeouts.
            if (not ot) and state["q"] == 4 and margin > 0:
                _d = other(possessor)
                _downs_left = max(0, 4 - state["down"])
                _burnable = 40 * max(0, _downs_left - timeouts[_d])
                if state["clock"] <= _burnable or state["clock"] <= 7:
                    log("Victory formation - kneel to end the game")
                    runoff(state["clock"])
                    return "clock"

            last_play = (not ot) and state["q"] in (2, 4) and state["clock"] <= 7
            if last_play:
                k = O.kicker()
                fg_dist = (100 - state["spot"]) + 17
                in_range = fg_dist <= min(61, 48 + ((k["abil"] if k else 4.0)-5)*3.2)
                fg_useful = state["q"] == 2 or (state["q"] == 4 and -3 <= margin <= 0)
                if in_range and fg_useful:
                    good, dist, kk = try_fg(O)
                    runoff(7)
                    if good:
                        score[possessor] += 3
                        scoring_plays.append({"q":state["q"],"clock":state["clock"],"team":possessor,
                                              "desc": f"{kk['name']} {dist}-yd FG" + (" (game-winner)" if state["q"] == 4 and score[possessor] > score[other(possessor)] else (" (ties it)" if state["q"] == 4 else " (end of half)")),"score":(score[home],score[away])})
                        log(f"FG GOOD from {dist} as time expires ({kk['name']})  [{home} {score[home]} - {score[away]} {away}]")
                        return "fg"
                    log(f"FG MISSED from {dist} as time expires")
                    return "fg_miss"
            if state["down"] == 4:
                k = O.kicker()
                k_leg = ST._leg(k) if k else 4.0
                fg_dist = (100 - state["spot"]) + 17
                agg = COACHES[O.team]["HC"].get("aggression", 0.5)
                decision = ST.fourth_down_decision(rng, state["spot"], state["dist"], state["q"],
                                                   state["clock"], margin, agg, k_leg, ot=ot,
                                                   def_timeouts=timeouts[other(O.team)],
                                                   own_timeouts=timeouts[O.team])
                # fake punt/FG: rare aggression-driven surprise on a punt/FG decision
                if decision in ("punt", "field_goal") and ST.fake_punt(rng, O, agg) and state["dist"] <= 6:
                    log(f"FAKE {'PUNT' if decision=='punt' else 'FG'}! {O.team} goes for it", O.team)
                    decision = "go"
                if decision == "field_goal":
                    # block chance first
                    if ST.fg_block(rng, O, fg_dist):
                        recv = other(possessor)
                        log(f"FIELD GOAL BLOCKED! {recv} takes over", recv)
                        runoff(5); state["next_spot"] = max(20, min(80, 100 - state["spot"])); return "fg_miss"
                    good, dist, kk = try_fg(O); runoff(5)
                    if good:
                        score[possessor] += 3
                        scoring_plays.append({"q":state["q"],"clock":state["clock"],"team":possessor,
                                              "desc": f"{kk['name']} {dist}-yd FG","score":(score[home],score[away])})
                        log(f"FG GOOD from {dist} ({kk['name']})  [{home} {score[home]} - {score[away]} {away}]")
                        add_momentum(possessor, 1.0)
                        return "fg"
                    log(f"FG MISSED from {dist}"); add_momentum(other(possessor), 1.2); return "fg_miss"
                if decision == "punt":
                    pres = punt(O); runoff(rng.randint(12, 18))
                    kind = pres[0]
                    if kind == "return_td":
                        _, rt_team, rtr = pres
                        score[rt_team] += 6
                        # PAT
                        sp0 = state["spot"]; state["spot"] = 97
                        rk = (H if rt_team==home else A).kicker()
                        if extra_point(H if rt_team==home else A): score[rt_team] += 1
                        state["spot"] = sp0
                        scoring_plays.append({"q":state["q"],"clock":state["clock"],"team":rt_team,
                                              "desc": f"{rtr['name']} punt return TD","score":(score[home],score[away])})
                        log(f"PUNT RETURN TOUCHDOWN {rtr['name']}!  [{home} {score[home]} - {score[away]} {away}]", rt_team)
                        add_momentum(rt_team, 2.5)
                        state["next_spot"] = kickoff_spot(); return "def_td"
                    if kind == "block":
                        _, recv_team, sp = pres
                        state["poss"] = recv_team
                        state["next_spot"] = sp; add_momentum(recv_team, 2.0); return "punt"
                    if kind == "muff":
                        _, keep_team, sp = pres  # kicking team recovered
                        add_momentum(keep_team, 1.5)
                        state["next_spot"] = sp; state["_muff_keep"] = keep_team; return "punt"
                    _, recv_team, new_spot = pres
                    log(f"Punt - {recv_team} ball at own {new_spot}")
                    state["next_spot"] = new_spot; return "punt"
                # decision == 'go' -> fall through to run the play
            # ---- PRE-SNAP PENALTY CHECK (scrimmage downs only) ----
            ps = PEN.pre_snap_penalty(rng, O.ols + [O.qb()] + O.wrs[:3] if O.qb() else O.ols,
                                      D.dls + D.lbs[:2],
                                      team_disc(O.team), team_disc(D.team))
            if ps:
                pname, pmeta, poff = ps
                if pmeta["side"] == "off":
                    # offensive pre-snap: march back, replay down (no clock play)
                    back = min(abs(pmeta["yds"]), max(1, state["spot"]//2))  # half-distance to own goal
                    state["spot"] = max(1, state["spot"] - back)
                    record_penalty(pname, O.team, poff, -back)
                    log(f"FLAG - {pname} on {O.team}" + (f" ({poff['name']})" if poff else "") + f", -{back}. Replay {state['down']}", O.team)
                    state["dist"] = state["dist"] + back
                    runoff(rng.randint(2,5)); continue
                else:
                    # defensive pre-snap: walk off toward end zone; auto 1st if it reaches the line
                    gain = min(pmeta["yds"], max(1, (100 - state["spot"])//2))
                    auto = pmeta.get("auto_first_if_ge_dist") and gain >= state["dist"]
                    state["spot"] = min(99, state["spot"] + gain)
                    record_penalty(pname, D.team, poff, gain)
                    if auto:
                        log(f"FLAG - {pname} on {D.team}" + (f" ({poff['name']})" if poff else "") + f", +{gain}, automatic first down", D.team)
                        state["down"] = 1; state["dist"] = min(10, 100 - state["spot"])
                    else:
                        log(f"FLAG - {pname} on {D.team}" + (f" ({poff['name']})" if poff else "") + f", +{gain}. Replay {state['down']}", D.team)
                        state["dist"] = max(1, state["dist"] - gain)
                    runoff(rng.randint(2,5)); continue
            # Play-calling reads DOWN as well as distance. The old table looked only at
            # yards to gain, so third-and-five was called exactly like first-and-five and
            # half of all third downs were run plays -- the single biggest reason only a
            # quarter of them were being converted. Rates follow real play-calling: early
            # downs near balanced, third and fourth down heavily pass unless it is short.
            _d, _dist = state["down"], state["dist"]
            if _d <= 1:
                pass_prob = 0.42 if _dist <= 3 else 0.50
            elif _d == 2:
                pass_prob = 0.33 if _dist <= 2 else (0.50 if _dist <= 6 else 0.64)
            else:
                pass_prob = 0.32 if _dist <= 2 else (0.74 if _dist <= 6 else 0.88)
            if hurry: pass_prob = 0.86
            if margin > 10 and state["q"] == 4: pass_prob = 0.26
            if margin >= 26 and state["q"] >= 3: pass_prob = 0.18
            pass_prob += (0.5 - O.run_bias)*0.3
            # ---- SCHEME + WEATHER effects on play-calling ----
            osch = OFF_SCHEMES.get(off_scheme[O.team], {})
            pass_prob += osch.get("pass_bias", 0.0)
            # bad weather pushes run-heavier and dampens the deep game
            if weather["label"] in ("rain", "cold/snow"):
                pass_prob -= 0.06 + weather.get("precip", 0) * 0.05
            if weather["wind"] > 2.5:
                pass_prob -= 0.03
            # momentum: team riding a wave gets a tiny boost to its identity
            if momentum["team"] == O.team and abs(momentum["val"]) > 2:
                pass_prob += osch.get("pass_bias", 0.0) * 0.3
            # ---- SCOUTING: attack the softer half of this defence, and go where the
            # yards have actually been today. Scaled by OC-against-DC skill.
            _sc = SCOUT[O.team]
            pass_prob += _sc.pass_shift()
            pass_prob = max(0.10, min(0.92, pass_prob))
            need_chunk = hurry or (state["down"] >= 3 and state["dist"] >= 9)
            # a blitzing defence gets the ball out quicker: fewer deep developing routes
            if _sc.quick_game and SC.ENABLE["quick"] and not hurry and state["dist"] <= 8:
                need_chunk = False
            _is_pass = rng.random() < pass_prob
            # the DEFENCE's pre-snap commitment, settled against the play actually run:
            # right guess takes yards away, wrong guess gives them up, symmetrically
            state["_commit"] = SCOUT[D.team].commit_edge(_is_pass)
            res = pass_play(O, D, need_chunk) if _is_pass else run_play(O, D)
            state.pop("_commit", None)
            # both books update on what just happened
            _k = "pass" if _is_pass else "run"
            _y = res.get("yds", 0) or 0
            SCOUT[D.team].observe(_k, _y)
            SCOUT[O.team].my_success(_k, _y)
            if res["type"] == "kneel": runoff(40); state["down"] += 1; continue
            # ---- LIVE PENALTY CHECK ----
            # determine play phase for foul eligibility
            if res["type"] in ("comp",): _phase = "pass_complete"
            elif res["type"] in ("inc",): _phase = "pass_incomplete"
            elif res["type"] in ("int",): _phase = "pass"
            elif res["type"] in ("run","qbrun"): _phase = "run"
            elif res["type"] == "sack": _phase = "pass"
            else: _phase = "any"
            # skip turnover plays for simplicity (penalty on TO is rare/declined)
            if res["type"] not in ("int",) and not res.get("fumble"):
                lp = PEN.live_penalty(rng, _phase,
                                      O.ols + [O.qb()] + O.wrs[:3] + O.rbs[:2] if O.qb() else O.ols,
                                      D.dls + D.lbs[:3] + D.cbs[:3] + D.ss[:2],
                                      team_disc(O.team), team_disc(D.team))
                if lp:
                    lname, lmeta, loff = lp
                    committing = O.team if lmeta["side"] == "off" or (lmeta["side"]=="either" and loff in (O.ols+O.rbs+O.wrs)) else D.team
                    # decide accept/decline heuristically: accept if it helps the non-committing team
                    play_gain = res.get("yds", 0) if res["type"] in ("comp","run","qbrun") else 0
                    if lmeta["side"] == "off":
                        # offensive foul: defense will accept if play_gain>0 (wipe the gain) -> replay
                        back = min(abs(lmeta["yds"]), max(1, state["spot"]//2))
                        state["spot"] = max(1, state["spot"] - back)
                        record_penalty(lname, committing, loff, -back)
                        state["dist"] += back
                        log(f"FLAG - {lname} on {committing}" + (f" ({loff['name']})" if loff else "") + f", -{back}, no play. Replay {state['down']}", committing)
                        if lmeta.get("ejection"): log(f"   {loff['name']} ejected", committing) if loff else None
                        runoff(rng.randint(4,7)); continue
                    else:
                        # defensive foul benefits offense
                        if lmeta["yds"] == "spot":  # DPI: spot foul (approx big chunk)
                            gain = min(max(12, state["dist"]+2), max(1,(100-state["spot"])))
                        else:
                            gain = min(lmeta["yds"], max(1,(100-state["spot"])//2))
                        state["spot"] = min(99, state["spot"] + gain)
                        record_penalty(lname, committing, loff, gain)
                        if lmeta.get("auto_first") or lmeta.get("yds")=="spot" or gain >= state["dist"]:
                            state["down"] = 1; state["dist"] = min(10, 100 - state["spot"])
                            log(f"FLAG - {lname} on {committing}" + (f" ({loff['name']})" if loff else "") + f", +{gain}, automatic first down", committing)
                        else:
                            state["dist"] = max(1, state["dist"] - gain)
                            log(f"FLAG - {lname} on {committing}" + (f" ({loff['name']})" if loff else "") + f", +{gain}. Replay {state['down']}", committing)
                        if lmeta.get("ejection") and loff: log(f"   {loff['name']} ejected", committing)
                        runoff(rng.randint(4,7)); continue
            if res["type"] == "int":
                ret = res["ret"]
                land = 100 - (state["spot"] + res["air"])
                # house call OR geometric reach into the end zone -> pick six
                if res.get("house_call") or (land + ret >= 99):
                    # The return on a pick-six is the distance from where the ball was
                    # caught to the goal line -- nothing else. This used to take the drawn
                    # return length (or the larger of the two), which produced 112-, 113-,
                    # 121- and 125-yard interception returns in 2038. `land` can be a few
                    # yards negative for a ball picked off in the end zone, so the cap is
                    # 109. Forward only; 2038's box scores stand. (Found 2039 week 2.)
                    house_ret = int(max(1, min(109, 100 - land)))
                    log(f"INTERCEPTED - {res['picker']['name']} picks off {res['player']['name']}, returns it {house_ret} the distance!")
                    touchdown(D, O, res["picker"], "INT return", house_ret)
                    state["next_spot"] = None; return "def_td"
                log(f"INTERCEPTED - {res['picker']['name']} picks off {res['player']['name']}, returns {ret}")
                turnovers.append({"q": state["q"], "clock": state["clock"], "team": O.team,
                                  "by": D.team, "kind": "int",
                                  "desc": "%s intercepted by %s%s" % (
                                      res['player']['name'], res['picker']['name'],
                                      (", returns %d" % ret) if ret else "")})
                runoff(rng.randint(5, 9))
                state["next_spot"] = max(1, min(99, land + ret)); return "int"
            if res.get("fumble"):
                log(f"FUMBLE - {res['player']['name']} loses it; {other(possessor)} recovers")
                turnovers.append({"q": state["q"], "clock": state["clock"], "team": possessor,
                                  "by": other(possessor), "kind": "fum",
                                  "desc": "%s fumbles, recovered by %s" % (
                                      res['player']['name'], other(possessor))})
                bump(stats, res.get("tackler"), "FumRec"); runoff(rng.randint(5, 9))
                state["next_spot"] = max(1, min(99, 100 - (state["spot"] + max(0,res.get("yds",0))))); return "fumble"
            yds = res.get("yds", 0)
            if res["type"] == "inc":
                log(f"Pass incomplete, {res['player']['name']} to {res['target']['name']}")
                runoff(rng.randint(4, 7))
            else:
                state["spot"] += yds
                if res["type"] == "comp": log(f"{res['player']['name']} complete to {res['target']['name']} for {yds}")
                elif res["type"] == "sack": log(f"SACK - {(res['tackler'] or {}).get('name','defense')} drops {res['player']['name']} for {yds}")
                elif res["type"]=="qbrun" and res.get("scramble"): log(f"{res['player']['name']} scrambles for {yds}")
                elif res["type"]=="qbrun": log(f"{res['player']['name']} keeper for {yds}")
                else: log(f"{res['player']['name']} rush for {yds}")
                # SAFETY: offense driven back into its own end zone (ball dead at/behind own goal).
                # Not every backward play into the EZ is a safety (QB throws it away, back lunges
                # forward); sacks are the most common real cause, so weight by play type.
                if state["spot"] <= 0:
                    safety_p = 0.30 if res["type"]=="sack" else 0.16
                    if rng.random() >= safety_p:
                        # avoided: ball spotted at the 1, play on
                        state["spot"] = 1
                        log("...ruled down at the 1, narrowly avoids the safety")
                        state["down"] += 1
                        if state["down"] > 4:
                            log("Turnover on downs"); state["next_spot"] = 99; return "downs"
                        state["dist"] = min(state.get("dist",10), 99); continue
                    score[other(possessor)] += 2
                    how = "sack" if res["type"]=="sack" else ("run stuffed" if res["type"] in ("run","qbrun") else "tackled")
                    tk = res.get("tackler")
                    desc = f"SAFETY - {(tk or {}).get('name','defense')} {how} in the end zone"
                    scoring_plays.append({"q":state["q"],"clock":state["clock"],"team":other(possessor),
                                          "desc":desc,"score":(score[home],score[away])})
                    log(f"SAFETY - {other(possessor)} scores 2  [{home} {score[home]} - {score[away]} {away}]", other(possessor))
                    if tk: bump(stats, tk, "Safety")
                    runoff(rng.randint(4,7))
                    if ot: return "safety"
                    # free kick: scoring team receives from the conceding team's own ~20
                    state["next_spot"] = kickoff_spot()
                    state["_safety_kick"] = other(possessor)   # team that will receive
                    return "safety"
                if state["spot"] >= 100:
                    scorer = res.get("target") if res["type"]=="comp" else res["player"]
                    state["spot"] = 99
                    touchdown(O, D, scorer, "pass" if res["type"]=="comp" else "rush", yds)
                    runoff(rng.randint(4, 7)); state["next_spot"] = None; return "td"
                base_ro = 38 if not hurry else 14
                if res["type"] == "comp" and rng.random() < (0.35 if hurry else 0.12):
                    base_ro = 7 if hurry else 16
                _sec = rng.randint(base_ro-6, base_ro+5) if not ot else rng.randint(4, 8)
                if not ot: _sec = maybe_defense_timeout(_sec)
                runoff(_sec)
                state["dist"] -= yds
                if state["dist"] <= 0:
                    state["down"] = 1; state["dist"] = min(10, 100 - state["spot"]); continue
            state["down"] += 1
            if state["down"] > 4:
                log(f"Turnover on downs")
                state["next_spot"] = max(1, 100 - state["spot"]); return "downs"

    def kickoff_spot():
        return 25 if rng.random() < 0.72 else rng.randint(18, 38)

    receiver = opener
    state["next_spot"] = kickoff_spot()
    while state["q"] <= 4:
        # ONSIDE KICK: after a score, if the team that just conceded is trailing late, they may onside
        if state.pop("_try_onside", False):
            kicking = other(receiver)  # team that scored kicks off
            trailing_late = (state["q"] == 4 and state["clock"] < 240
                             and (score[kicking] - score[receiver]) < 0)
            o = ST.onside_kick(rng, H if kicking==home else A, trailing_late)
            if o["recovered_by_kicking"]:
                log(f"ONSIDE KICK RECOVERED by {kicking}!", kicking)
                receiver = kicking
                state["next_spot"] = o["spot"]
            else:
                if trailing_late: log(f"Onside kick fails; {receiver} recovers")
                state["next_spot"] = o["spot"]
        # KICKOFF RETURN TD (rare)
        elif state.get("next_spot") == "KRTD":
            rtd_team, rtr = state.pop("_ko_rtd")
            score[rtd_team] += 6
            sp0 = state.get("spot"); state["spot"] = 97
            if extra_point(H if rtd_team==home else A): score[rtd_team] += 1
            scoring_plays.append({"q":state["q"],"clock":state["clock"],"team":rtd_team,
                                  "desc": f"{rtr['name']} kickoff return TD","score":(score[home],score[away])})
            log(f"KICKOFF RETURN TOUCHDOWN {rtr['name']}!  [{home} {score[home]} - {score[away]} {away}]", rtd_team)
            add_momentum(rtd_team, 2.5)
            receiver = other(rtd_team)
            state["next_spot"] = kickoff_spot()
        # A drive interrupted by the end of a quarter resumes where it left off: same
        # team, same spot, same down and distance. Only a genuinely new possession
        # starts from a kickoff spot.
        _resume = state.pop("_resume", None)
        if _resume is not None:
            _ns, _dd = _resume
        else:
            _dd = None
            _ns = state.get("next_spot")
            if not isinstance(_ns, int): _ns = kickoff_spot()
        result = drive(receiver, _ns, resume=_dd)
        nxt = state.pop("next_spot", None)
        if result != "clock":
            receiver = other(state["poss"])
            if result in ("td","fg","def_td"):
                # possible kickoff return TD or onside attempt on the ensuing kick
                scorer = state["poss"]
                # check for a kickoff-return TD by the receiving team
                kg = H if scorer==home else A; rg = H if receiver==home else A
                start, rtd = ST.kickoff_return(rng, kg, rg, weather)
                # if the team that just got scored on is trailing late, they'd rather the OTHER
                # team onside — actually the SCORING team onsides only if THEY are trailing late
                if (state["q"]==4 and state["clock"]<240 and (score[scorer]-score[receiver])<0):
                    state["_try_onside"] = True
                    state["next_spot"] = None
                elif rtd is not None:
                    state["_ko_rtd"] = (receiver, rtd); state["next_spot"] = "KRTD"
                else:
                    state["next_spot"] = start if start else kickoff_spot()
            elif result == "fg_miss": state["next_spot"] = max(20, 100 - state["spot"])
            elif result == "safety":
                receiver = state.pop("_safety_kick", other(state["poss"]))
                state["next_spot"] = kickoff_spot()
            else: state["next_spot"] = nxt if nxt else kickoff_spot()
        if state["clock"] <= 0:
            # Stash the live ball before the quarter rolls over, so the possession can
            # pick up where it stopped. Halftime is different: the second half opens
            # with a kickoff, so nothing is carried across the Q2->Q3 break.
            if result == "clock" and state["q"] in (1, 3):
                state["_resume"] = (state["spot"], (state["down"], state["dist"]))
            state["q"] += 1; state["clock"] = 900
            if state["q"] == 3:
                receiver = other(opener); state["next_spot"] = kickoff_spot()
                state.pop("_resume", None)
                timeouts[home] = 3; timeouts[away] = 3   # fresh set each half
            if state["q"] > 4: break

    ot_num = 0
    while score[home] == score[away]:
        ot_num += 1
        state["q"] = 4 + ot_num; state["clock"] = 0
        first = rng.choice([home, away])
        state["ot_walkoff"] = False
        for idx, team_ in enumerate((first, other(first))):
            state["ot_second"] = (idx == 1)   # True on the trailing/second possession
            drive(team_, 75, ot=True)
            state.pop("next_spot", None)
            if state.get("ot_walkoff"):        # second team took the lead -> game over
                break
        state.pop("ot_second", None)
        if ot_num >= 6: break

    box = {"home": home, "away": away, "home_score": score[home], "away_score": score[away],
           "seed": seed, "site": site, "rivalry": rivalry, "ot": ot_num, "postseason": postseason,
           "stats": stats, "scoring_plays": scoring_plays, "turnovers": turnovers,
           "injuries": injuries, "n_plays": len(pbp),
           "penalties": {home: {"n": pen_count[home], "yds": pen_yards[home]},
                         away: {"n": pen_count[away], "yds": pen_yards[away]}},
           "penalty_log": box_pen_log,
           "weather": weather["label"],
           "off_scheme": {home: off_scheme[home], away: off_scheme[away]},
           "def_scheme": {home: def_scheme[home], away: def_scheme[away]},
           "final_momentum": {"team": momentum["team"], "val": round(momentum["val"],1)}}
    # keep the crunch-time sequence only when the game finished close (<=8, i.e. one score) or in OT
    if abs(score[home] - score[away]) <= 8 or ot_num > 0:
        box["clutch"] = clutch
    return box, pbp

# ----- reputation feedback (spec 4): call after each game; persists into ROSTERS in-memory -----
BASELINE = {"ypt_wr": 7.0, "ypc_rb": 4.4, "ypa_qb": 7.1}
def update_reputation(box):
    for pid, s in box["stats"].items():
        pos = s["pos"]; z = None
        if pos == "QB" and s.get("Att",0) >= 12:
            ypa = s.get("PassYds",0)/s["Att"]
            z = (ypa - BASELINE["ypa_qb"])/2.2 + s.get("PassTD",0)*0.09 - s.get("INT",0)*0.14
        elif pos == "RB" and s.get("RushAtt",0) >= 8:
            z = (s.get("RushYds",0)/s["RushAtt"] - BASELINE["ypc_rb"])/1.9 + s.get("RushTD",0)*0.10
        elif pos in ("WR","TE","ATH") and s.get("Targets",0) >= 4:
            z = (s.get("RecYds",0)/s["Targets"] - BASELINE["ypt_wr"])/3.2 + s.get("RecTD",0)*0.12
        if z is None: continue
        for pl in ROSTERS[s["team"]]:
            if pl["pid"] == pid:
                pl["rep"] = max(-1.5, min(2.0, 0.75*pl.get("rep",0.0) + 0.25*max(-2.0, min(2.5, z))))
                break

def persist_rosters():
    """Write rosters back to disk, keeping FBS and subdivision programs separate.

    Subdivision guests are merged into ROSTERS at the start of a simulation window
    (subdivision.register). Dumping the merged table into rosters.pkl would quietly
    turn 62 guest schools into FBS members, so they are split back out here and
    saved to their own file -- their injuries and reputation still persist.
    """
    fbs_names = set(U["teams"])
    fbs = {t: r for t, r in ROSTERS.items() if t in fbs_names}
    guests = {t: r for t, r in ROSTERS.items() if t not in fbs_names}
    with open('/home/claude/cfb2/state/rosters.pkl','wb') as f:
        pickle.dump(fbs, f)
    if guests:
        with open('/home/claude/cfb2/state/sub_rosters.pkl','wb') as f:
            pickle.dump(guests, f)

# ---------------------------------------------------------------------------
# OFFENSIVE CALIBRATION (2035 rebuild).
# The engine recovered from the bundle is the Season-3 tuning. Seven seasons of
# later balance work were lost with the live code, and on first run it produced
# 25.5 pts/team vs the 19.7 pts/team the pre-reset 2035 engine was posting.
# Rather than guess at scattered constants, offence is damped by two fitted
# values -- completion rate and rushing yards per carry -- chosen to reproduce
# the canon scoring level measured from the recovered history.
# ---------------------------------------------------------------------------
# --- 2036 PASSING RECALIBRATION (forward from week 7) -------------------------------
# Scoring had fallen to 19 points a team while YARDS stayed realistic (373 a team at
# 5.56 a play against real football's 410 and 5.9). The leak was third down: 25%
# conversion against a real 40%, because the passing game was shaped wrong rather than
# sized wrong -- 46.7% completions at 14.6 yards each, versus a real 63% at 11.9.
# Routes averaged 9 air yards and every yard past 8 costs completion probability, so the
# engine threw deep, missed, and recovered the yardage on the few that connected. Net
# yards came out right, which is exactly why the earlier calibration never caught it.
#
# These move yardage from the air to after the catch. Yards per completion barely
# changes; the completion RATE rises, which is what lets a drive survive third down.
# How hard a talent advantage bites. 1.0 is the engine as it stood through 2037.
#
# Measured head-to-head in the sandbox, free of schedule effects, the 1.0 engine gives a
# top-10 roster an 89.1% win rate against a bottom-10 one and 80.2% against a median
# programme; real college football is nearer 97% and 85%. As a logistic on the talent
# gap that is k = 1.33 against a real-world k = 1.80.
#
# This alone does NOT solve the separation problem. The arithmetic puts it at about
# +0.12 undefeated teams a season against a target of 1-3, because the dominant cause is
# that the Great Fourteen holds 7 of the top 10 and they play each other nine times a
# year. This is only the half of the fix that lives in the engine.
EDGE_SCALE = 1.0

# Per-play randomness, as a multiplier on the spread of every yardage draw. 1.0 is the
# engine as it stood through 2037.
#
# This is the OTHER way to sharpen separation, and on the evidence the better one. A
# game is roughly 150 plays, so the favourite's win rate is set by the ratio of its
# per-play edge to per-play noise. EDGE_SCALE raises the edge, which sounds equivalent
# and is not: a bigger mean edge compounds hardest where the gap is already enormous, so
# it blew the subdivision margin from +21.6 to +30.8 while barely moving the FBS curve
# that matters. Cutting noise leaves every mean untouched and sharpens the whole curve
# at once.
NOISE_SCALE = 1.0

# In a rivalry game the strength gap is compressed to this fraction (it was a literal 0.55
# until the 2042 parity audit; the default is unchanged, so no result moves).
RIVALRY_GAP = 0.70

# The vertical shot: how often an offence takes one, and how much depth it adds.
# Calibrated against the explosive-play tail rather than guessed -- see the sweep in
# PENDING. SHOT_RATE is per pass attempt, before the Deep Threat and need-a-chunk
# multipliers.
SHOT_RATE = 0.12
SHOT_DEPTH = 28.0

CAL_AIR_SHIFT = 4.4       # yards taken off every route's depth. Raised from 2.6 alongside
                          # the vertical shot: the shot adds the tail, and taking a little
                          # depth off the routine throw keeps yards per completion where it
                          # was (14.10 against 13.99 before) instead of inflating the whole
                          # distribution. The pair was chosen off a sweep -- see PENDING.
CAL_YAC_BONUS = 2.0       # yards added after the catch
CAL_COMP_BASE = 0.030     # lift on the base completion probability. Lowered from 0.055
                          # when scouting went in: offences that can now identify and
                          # attack the softer half of a defence score about a point more
                          # per team per game, and the point of scouting is to change WHO
                          # scores, not to inflate the league. Swept on the sandbox: 0.055
                          # -> 25.24, 0.040 -> 24.81, 0.030 -> 24.45, 0.022 -> 24.13.
CAL_COMP_DAMP = 0.0       # the old blanket damper, no longer needed
CAL_RUN_DAMP  = 0.900     # UNCHANGED: rushing already runs at 4.23 a carry vs a real 4.3

BASE_SEED = 88110000
def game_seed(counter): return BASE_SEED + counter
