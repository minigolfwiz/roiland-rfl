"""Prestige that moves.

Until 2038, prestige was a number set when the universe was made and never written back.
`recruiting.py` read it to decide who could sign whom; nothing anywhere updated it.
Thirteen seasons of football did not move it by a point, which meant no programme could
ever rise or fall: Ciarralotta won 43% of its games across thirteen years on a prestige
of 85.5 and went on recruiting like a blue-blood, while Coastal Ranroman won 60% on 32.7
and went on recruiting like nobody.

This module makes prestige an OUTPUT as well as an input. Dan's brief: "it should be
affected by a lot of things, history, coach, recent bumps, good players, player
retention, everything."

------------------------------------------------------------------------------- the model

Prestige is a slow average of what a programme has been, pulled each year toward what it
has just shown itself to be.

    target  = how good this programme looks right now, on 0-100
    drift   = (target - prestige) * ADJUST, capped at MAX_MOVE a season
    new     = prestige + drift

`target` is a weighted blend of six things, each normalised to 0-100 across the league:

    on-field merit   .40   a schedule-adjusted rating, not a win rate (see below)
    honours          .16   national title, playoff run, conference championship
    history          .14   the programme's deep past: titles, all-time standing
    coaching         .12   head coach, with the coordinators at half weight
    talent on hand   .12   the best players on the roster now
    retention        .06   who stayed, who left through the portal

WHY MERIT IS NOT WIN RATE. A Low Sixteen programme that wins 56% of its games against
Low Sixteen opposition is not the equal of a Great Fourteen programme that goes 56%
against the Great Fourteen. Measured on raw win rate the two look identical, and a model
built on it flattened the twelve conferences from a spread of 22.1 to 6.4 -- it paid
weak-schedule programmes for beating each other and quietly dissolved the P6/L6 tiers.
Elo is used instead: it is schedule-adjusted by construction, because what a win is
worth depends on who it was against.

WHY IT MOVES SLOWLY. ADJUST is 0.22 and MAX_MOVE is 7, so a programme that collapses
outright takes about five years to fall out of the elite and a decade to hit bottom.
That is the point. Blue-bloods should be able to have a bad year, and a good year should
not make anybody a blue-blood.
"""
import sys, re, math, collections, statistics
sys.path.insert(0, '/home/claude/cfb2')

ADJUST   = 0.22        # share of the gap to the target closed each season
MAX_MOVE = 7.0         # hard cap on one season's movement, in prestige points
FLOOR, CEIL = 3.0, 99.0

WEIGHTS = {
    "merit":     0.40,
    "honours":   0.16,
    "history":   0.14,
    "coaching":  0.12,
    "talent":    0.12,
    "retention": 0.06,
}

# Elo, used only to produce the schedule-adjusted merit term
K_GAME, HOME_ELO = 22.0, 45.0
REGRESS = 0.16         # pulled toward the league mean each offseason: rosters turn over
BONUS = {"title": 55, "final": 32, "semis": 22, "playoff": 10, "conf": 16}


def _norm(d):
    """Spread a dict of raw numbers across 0-100 by rank-preserving linear scaling."""
    if not d:
        return {}
    lo, hi = min(d.values()), max(d.values())
    if hi - lo < 1e-9:
        return {k: 50.0 for k in d}
    return {k: 100.0 * (v - lo) / (hi - lo) for k, v in d.items()}


# --------------------------------------------------------------------------- merit (Elo)
def elo_history(db, teams, guest_rating=1180.0, through=None):
    """Run every game ever played through Elo. Returns {season: {team: rating}}.

    Guests sit at a fixed low rating, so beating one earns almost nothing and losing to
    one is expensive -- which is how a guarantee game should feel.
    """
    TS = set(teams)
    def season_of(gid):
        m = re.match(r"^S(\d+)", str(gid))
        return int(m.group(1)) if m else None

    by_season = collections.defaultdict(list)
    for gid, b in db.items():
        sn = season_of(gid)
        if sn is None or (through is not None and sn > through):
            continue
        by_season[sn].append((b.get("week", 0) or 0, str(gid), b))
    for sn in by_season:
        by_season[sn].sort(key=lambda x: (x[0], x[1]))

    R = {t: 1500.0 for t in TS}
    out = {}
    for sn in sorted(by_season):
        for _wk, gid, b in by_season[sn]:
            h, a = b.get("home"), b.get("away")
            if not h or not a:
                continue
            rh, ra = R.get(h, guest_rating), R.get(a, guest_rating)
            exp_h = 1 / (1 + 10 ** ((ra - rh - HOME_ELO) / 400))
            won_h = 1.0 if b["home_score"] > b["away_score"] else 0.0
            # margin counts, with diminishing returns so a 60-point win is not 3x a 20
            mult = min(2.2, 1.0 + abs(b["home_score"] - b["away_score"]) / 22.0)
            d = K_GAME * mult * (won_h - exp_h)
            if h in R: R[h] += d
            if a in R: R[a] -= d
        out[sn] = dict(R)
        mean = statistics.mean(R.values())
        for t in R:
            R[t] += (mean - R[t]) * REGRESS
    return out


# ------------------------------------------------------------------- the component terms
MERIT_ELO = 0.75       # Dan, 2039 end: merit is Elo blended with where you finished in
MERIT_FINISH = 0.25    # your own conference, so 12th of 14 costs you even when Elo forgives
# who you lost to. Elo alone let 6-6 Ranroman State target 99 and the whole Great
# Fourteen inflate together (12 of 14 rose in the first two dynamic seasons).
PENALTY = {"losing": -12, "last": -20, "two_losing": -8}   # negative honours (Dan, 2039 end)


def conf_finish(U, records):
    """Where each programme finished in its own conference, 0 (last) to 100 (first),
    on conference record then overall wins. Ties share the better percentile."""
    out = {}
    for conf, teams in U["conferences"].items():
        ts = [t for t in teams if t in records]
        if len(ts) < 2:
            for t in ts: out[t] = 50.0
            continue
        key = lambda t: (records[t].get("confW", 0) - records[t].get("confL", 0),
                         records[t].get("confW", 0), records[t].get("W", 0) - records[t].get("L", 0))
        order = sorted(ts, key=key, reverse=True)
        n = len(order)
        for i, t in enumerate(order):
            j = i
            while j > 0 and key(order[j - 1]) == key(t):
                j -= 1
            out[t] = 100.0 * (n - 1 - j) / (n - 1)
    return out


def season_records(U, state, season):
    """{season_number: {team: record}} for the seasons prestige can see: archived rows,
    plus the live record for the season just played when it is not archived yet."""
    out = {}
    for sk, rec in (state.get("season_archive") or {}).items():
        try:
            sn = int(sk)
        except Exception:
            continue
        if isinstance(rec, dict) and rec.get("standings"):
            out[sn] = rec["standings"]
    if season not in out and state.get("record"):
        out[season] = state["record"]
    return out


def components(U, db, state, elo_now, season):
    """Each of Dan's six factors, every one of them a LOOKUP, normalised to 0-100."""
    teams = list(U["teams"])
    TS = set(teams)
    geo = U.get("geo", {})

    elo_n = _norm({t: elo_now.get(t, 1400.0) for t in teams})
    recs = season_records(U, state, season)
    finish = conf_finish(U, recs.get(season, state.get("record") or {}))
    merit = {t: MERIT_ELO * elo_n[t] + MERIT_FINISH * finish.get(t, 50.0) for t in teams}

    # ---- honours: what the programme has just won, and what it has ever won ----
    honours = {t: 0.0 for t in teams}
    history = {t: 0.0 for t in teams}
    # SOURCE BUG, fixed. This read `geo[t]["titles"]`, which does not exist -- `geo`
    # carries only state, mascot and full_name, so `titles` was None for all 152
    # programmes and the history term was a flat 50 for everybody: 14% of the weight
    # doing nothing but dilution. The real 1929-onward championship canon lives in
    # `state["history"]["book"][team]`, which is what `finalize_season` writes.
    book = ((state.get("history") or {}).get("book") or {})
    for t in teams:
        rec = book.get(t) or {}
        for y in (rec.get("titles") or []):
            try:
                age = max(0, season + 2025 - int(y))
            except Exception:
                continue
            history[t] += 40.0 * (0.965 ** age)      # a 1971 title still counts, faintly
        for y in (rec.get("runnerup") or []):
            try:
                age = max(0, season + 2025 - int(y))
            except Exception:
                continue
            history[t] += 12.0 * (0.965 ** age)      # reaching one counts for something
    arch = (state.get("season_archive") or {})
    for sk, rec in arch.items():
        try:
            sn = int(sk)
        except Exception:
            continue
        age = max(0, season - sn)
        decay = 0.72 ** age                               # recent honours dominate
        champ = rec.get("champion")
        if champ in honours:
            honours[champ] += BONUS["title"] * decay
    # ---- negative honours (Dan, 2039 end): losing finally registers ----
    # Honours only ever added -- a title +55, a conference title +16 -- so a programme
    # that went 3-9 three years running lost nothing here. Mirror it: a losing season,
    # a last-place conference finish, and two losing seasons back to back all count
    # against, with the same 0.72 decay as the bonuses.
    for sn, recs_sn in recs.items():
        if sn > season or sn < season - 5:
            continue
        decay = 0.72 ** max(0, season - sn)
        fin = conf_finish(U, recs_sn)
        prev = recs.get(sn - 1) or {}
        for t in teams:
            r = recs_sn.get(t)
            if not r:
                continue
            losing = r.get("W", 0) < r.get("L", 0)
            if losing:
                honours[t] += PENALTY["losing"] * decay
                pr = prev.get(t)
                if pr and pr.get("W", 0) < pr.get("L", 0):
                    honours[t] += PENALTY["two_losing"] * decay
            if fin.get(t, 50.0) <= 0.0:
                honours[t] += PENALTY["last"] * decay
    import os, pickle
    for sn in range(max(1, season - 5), season + 1):
        p = '/home/claude/cfb2/state/conf_champs_s%d.pkl' % sn
        if not os.path.exists(p):
            continue
        try:
            cc = pickle.load(open(p, 'rb'))
        except Exception:
            continue
        decay = 0.72 ** max(0, season - sn)
        for _c, t in cc.items():
            if t in honours:
                honours[t] += BONUS["conf"] * decay

    # ---- coaching: the head coach carries it, coordinators at half weight ----
    # SOURCE BUG, fixed. Coaching staffs live in `pbp_engine.COACHES`, loaded from
    # state/coaches.pkl -- never in the season state. `state.get("coaches")` was always
    # empty, every staff fell to the 5.0 default, and another 12% of the weight was a
    # flat 50. Dan's brief named the coach explicitly as one of the six things prestige
    # should move on.
    import pbp_engine as _E
    coaches = _E.COACHES or {}
    coaching = {}
    for t in teams:
        st = coaches.get(t) or {}
        def sk(role):
            r = st.get(role) or {}
            return r.get("skill", 5.0) if isinstance(r, dict) else 5.0
        coaching[t] = sk("HC") + 0.5 * (sk("OC") + sk("DC")) / 2.0

    # ---- talent on hand: the best players actually on the roster ----
    import pbp_engine as E
    talent = {}
    for t in teams:
        r = E.ROSTERS.get(t) or []
        best = sorted((p.get("abil", 5.0) for p in r), reverse=True)[:22]
        talent[t] = statistics.mean(best) if best else 5.0

    # ---- retention: who stayed. Net portal movement, as the state recorded it ----
    # SOURCE BUG, fixed. `portal.py` writes its record to `portal_s{season}` as a dict
    # with a "transfers" list; this looked for a top-level "portal_log" or "portal" that
    # nothing has ever written, so retention was a flat 50 for everybody too. With
    # history and coaching also dead that was 32% of the weight -- almost a third of what
    # moves prestige -- contributing nothing but dilution.
    retention = {t: 0.0 for t in teams}
    rec_portal = state.get("portal_s%d" % season) or {}
    moves = rec_portal.get("transfers") if isinstance(rec_portal, dict) else None
    if isinstance(moves, list):
        for m in moves:
            if not isinstance(m, dict):
                continue
            fr, to = m.get("from"), m.get("to")
            if fr in retention: retention[fr] -= 1.0
            if to in retention: retention[to] += 1.0

    return {
        "merit": _norm(merit), "honours": _norm(honours), "history": _norm(history),
        "coaching": _norm(coaching), "talent": _norm(talent), "retention": _norm(retention),
    }


def targets(U, db, state, season, elo=None):
    """What this programme looks like now, ON THE LEAGUE'S OWN PRESTIGE SCALE.

    THE RAW BLEND IS NOT A PRESTIGE. Each component is min-max normalised to 0-100, and
    those distributions are right-skewed -- a handful of elite programmes stretch the
    top end -- so the weighted blend comes out with a mean near 33 while the league's
    prestige has a mean near 47. Left like that the target is BELOW current prestige for
    145 of 152 programmes, every single year: the whole league deflates toward the floor
    a few points a season and the P6/L6 architecture dissolves. That is the opposite of
    what dynamic prestige was built to do, and it would have been invisible for about
    three seasons.

    Prestige is a RELATIVE standing, so the target is too. The blend is standardised and
    mapped onto the DESIGNED prestige distribution -- the anchor Dan set, which never
    moves -- so a programme's target says where it ranks, not what a min-max scaler
    happened to produce. Anchoring to the designed spread rather than the current one
    also stops drift compounding: the league's overall level cannot wander, only the
    order within it.
    """
    elo = elo or elo_history(db, U["teams"], through=season)
    now = elo.get(season) or elo[max(elo)]
    comp = components(U, db, state, now, season)
    raw = {t: sum(WEIGHTS[k] * comp[k].get(t, 50.0) for k in WEIGHTS) for t in U["teams"]}
    out = quantile_map(raw, anchor_values(U))
    # PEDIGREE FLOOR (Dan, 2040 offseason): "North Hatesei is the most storied school
    # in history; their prestige should be higher, even without their recent failures."
    # Twenty-one titles scored 100 on history and 14% of the blend, and a 4-8 year
    # still put them at 62.9. A programme's target cannot fall below a floor set by
    # its history alone: 0.80 * history (NH 80; Central Stanton 38 and Greene 26 are
    # already far above theirs, so only a dynasty-grade past ever binds),
    # so a dynasty has bad years, not bad decades.
    for t in out:
        out[t] = max(out[t], PEDIGREE_BASE + PEDIGREE_SLOPE * comp["history"].get(t, 0.0))
    return out, comp


PEDIGREE_BASE, PEDIGREE_SLOPE = 0.0, 0.80


def anchor_values(U):
    """The fixed shape of the league: the sorted multiset of prestige values every
    target is drawn from. Set once by the 2039 recalibration (`prestige_anchor`); the
    designed values before that."""
    a = U.get("prestige_anchor")
    if not a:
        src = U.get("prestige_designed") or U["prestige"]
        a = sorted(src[t] for t in U["teams"])
    return sorted(a)


def quantile_map(raw, anchor):
    """Rank-to-value. The z-score map this replaces (Dan, 2039 end) stretched a right-
    skewed blend onto the anchor's spread, so the top six programmes all pinned at the
    99 ceiling and were dragged up together, 7 points a year, toward a value none of
    them could reach. Here the best raw score takes the anchor's best value, the
    second its second, and so on: exactly one programme can hold the top, and the
    league's overall level cannot move, only the order within it."""
    order = sorted(raw, key=lambda t: -raw[t])
    n = len(order); m = len(anchor)
    out = {}
    for i, t in enumerate(order):
        # i-th best of n maps onto the i-th best of the anchor
        j = min(m - 1, int(round(i * (m - 1) / max(1, n - 1))))
        out[t] = max(FLOOR, min(CEIL, anchor[m - 1 - j]))
    return out


def recalibrate(U, db, state, season, write=False):
    """ONE-OFF (Dan, 2039 end): re-fit prestige to the model's own targets, normalised
    WITHIN TIER. Each tier keeps exactly the multiset of values it has now -- the P6
    keeps its 90s top and its 40s floor -- but who holds which value is decided by the
    blend, so a Great Fourteen programme that has been finishing 12th takes a P6 floor
    value instead of the 68 it was designed with. Also freezes the league-wide anchor
    for every later season's targets."""
    elo = elo_history(db, U["teams"], through=season)
    now = elo.get(season) or elo[max(elo)]
    comp = components(U, db, state, now, season)
    raw = {t: sum(WEIGHTS[k] * comp[k].get(t, 50.0) for k in WEIGHTS) for t in U["teams"]}
    new = {}
    for tier in sorted({U["tiers"][c] for c in U["tiers"]}):
        ts = [t for t in U["teams"] if U["tiers"][U["team_conf"][t]] == tier]
        vals = sorted(U["prestige"][t] for t in ts)
        new.update(quantile_map({t: raw[t] for t in ts}, vals))
    if write:
        U["prestige_pre_recal_s%d" % season] = dict(U["prestige"])
        for t in new:
            U["prestige"][t] = round(new[t], 1)
        U["prestige_anchor"] = sorted(U["prestige"][t] for t in U["teams"])
        U["prestige_recal_season"] = season
    return new, raw


def step(U, db, state, season, write=True):
    """Move every programme's prestige one season toward what it has earned.

    Called once per offseason. Returns {team: (old, new, target)}.
    """
    tgt, _comp = targets(U, db, state, season)
    moved = {}
    for t in U["teams"]:
        old = U["prestige"][t]
        gap = tgt[t] - old
        d = max(-MAX_MOVE, min(MAX_MOVE, gap * ADJUST))
        new = max(FLOOR, min(CEIL, old + d))
        moved[t] = (old, new, tgt[t])
        if write:
            U["prestige"][t] = round(new, 1)
    return moved
