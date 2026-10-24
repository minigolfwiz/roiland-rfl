"""The transfer portal.

Rebuilt for the 2036 cycle. The standalone module died in the 2035 reset and the
version inside offseason.py was a stub: no reasons, no withdrawal, no gating, and no
memory of the coaching carousel.

Three principles carried over from canon:

  * players are valued on OBSERVED PRODUCTION, never on hidden ability -- a coach
    recruiting out of the portal sees a stat line, not a rating
  * a program's bar rises with its prestige, so a walk-on cannot transfer to a
    blueblood just because he wants to
  * nobody vanishes: a player nobody calls withdraws and returns to his old locker room

New this cycle:

  * COACH FOLLOWING. The carousel records every coach who changed schools; a player
    whose coach left is pulled hard toward wherever that coach went.
  * LINEMEN CAN FINALLY MOVE. Valuation ran on a production function that returns
    zero for 100% of offensive linemen, so no lineman had ever cleared any program's
    bar -- the "zero OL transfers" mystery. They are now valued on blocking.
"""
import sys, math, random, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from committee import _prod_points

U = E.U
TEAMS = U["teams"]
PRESTIGE = U["prestige"]
# How selective programs are. The bar rises with prestige, and the FLOOR matters just
# as much: a player nobody saw play has no market anywhere, which is why roughly half
# of everyone who enters the portal withdraws and goes back to his old locker room.
INTEREST_K = 0.80
INTEREST_FLOOR = 11.0


def value_of(pl, stats):
    """What the market sees. Production for everyone who generates a stat line, and a
    blocking grade for the linemen who never will."""
    st = stats.get(pl["pid"], {})
    base = _prod_points(pl["pos"], st)
    if pl["pos"] in ("OL", "P") and base == 0.0:
        a = pl.get("attrs") or {}
        if pl["pos"] == "OL":
            grade = (a.get("pblk", pl.get("abil", 5.0)) + a.get("rblk", pl.get("abil", 5.0))) / 2.0
            base = max(0.0, (grade - 4.2) * 6.2)
        else:
            base = max(0.0, (a.get("leg", pl.get("abil", 5.0)) - 4.2) * 3.2)
        # PLAYING TIME. Every lineman has a blocking grade, but a quarter of a roster's
        # linemen never take a snap, and nobody recruits a player they have not seen.
        # A lineman who appears nowhere in the season's statistics -- not even a penalty
        # -- is a backup, and the market treats him like one. Without this, linemen went
        # from never transferring to being the single largest group in the portal.
        if not st:
            base *= 0.2
    return base + 40.0 * math.tanh(pl.get("rep", 0.0))


def portal_reason(pl, src, val, s, rng, staff_turnover):
    """Why he is leaving. Checked in order of how strongly each explains the move."""
    if staff_turnover and rng.random() < 0.55:
        return rng.choice(["left after the staff turnover",
                           "didn't fit the new staff's plans"])
    inj = len([h for h in (pl.get("inj_hist") or []) if isinstance(h, dict) and h.get("weeks", 0) >= 3])
    if inj >= 1 and rng.random() < 0.5:
        return "fresh start after the injuries"
    if PRESTIGE[src] < 55 and val > 120:
        return "star at a small school"
    rec = s["record"].get(src, {})
    if rec.get("W", 0) <= 3 and rng.random() < 0.6:
        return "left a sinking program"
    if val < 12:
        return rng.choice(["promised a bigger role elsewhere", "buried on the depth chart"])
    return rng.choice(["seeking a change", "wants to play closer to home",
                       "promised a bigger role elsewhere", "one shot at a bigger stage"])


def run_portal(seed=51010, cap=70):
    rng = random.Random(seed)
    s = SE.load_state()
    stats = s["season_stats"]
    moves = s.get("coach_moves") or []
    # which programs changed a coach at all -- drives the push reasons
    turnover = {m["from"] for m in moves}

    # ---------- 1) who enters ----------
    # Value scales differ enormously by position -- a linebacker's production number is
    # not comparable to a receiver's, and a lineman's blocking proxy is a third scale
    # again. Absolute thresholds therefore produced position bias: whichever group's
    # numbers happened to sit low got flagged "buried" wholesale and flooded the portal.
    # Thresholds are POSITION-RELATIVE instead, so "buried" and "star" mean the same
    # thing to a tackle as to a quarterback.
    _vals = collections.defaultdict(list)
    for t in TEAMS:
        for pl in E.ROSTERS[t]:
            if not pl.get("_leaving"):
                _vals[pl["pos"]].append(value_of(pl, stats))
    _med = {}
    for pos, v in _vals.items():
        v = sorted(v)
        _med[pos] = v[len(v) // 2] if v else 1.0

    entrants = []
    _valmap = {}
    for t in TEAMS:
        keep = []
        for pl in E.ROSTERS[t]:
            if pl.get("_leaving"):
                keep.append(pl); continue
            val = value_of(pl, stats)
            _valmap[pl["pid"]] = val
            med = max(1.0, _med.get(pl["pos"], 1.0))
            small = PRESTIGE[t] < 55
            buried = val < 0.32 * med and pl["cls"] in ("So", "Jr")
            star_small = small and val > 3.2 * med
            # Dan, 2039 end: a backup on a LOSING, stacked roster leaves more readily --
            # he came to a big programme to play and win and is doing neither
            r = s["record"].get(t, {})
            losing_stack = (PRESTIGE[t] >= 65 and r.get("W", 0) < r.get("L", 0)
                            and val < 0.6 * med and pl["cls"] in ("So", "Jr", "RS"))
            # Rates calibrated to canon's volume: roughly 500 players enter the portal
            # and a little over 200 find a new home, the rest withdrawing.
            p = 0.026 + (0.16 if star_small else 0) + (0.040 if buried else 0) + (0.07 if losing_stack else 0)
            if t in turnover:
                p += 0.028                     # a new staff shakes players loose
            if rng.random() < p:
                entrants.append({"pl": pl, "from": t, "val": val,
                                 "reason": portal_reason(pl, t, val, s, rng, t in turnover)})
            else:
                keep.append(pl)
        E.ROSTERS[t] = keep

    # ---------- 2) the market ----------
    committed = collections.Counter({t: len(E.ROSTERS[t]) for t in TEAMS})
    rec = s["record"]
    entrants.sort(key=lambda e: -e["val"])
    transfers, no_takers = [], []
    # Coach-following diagnostics. The feature can look broken for two very different
    # reasons -- nobody had a coach to follow, or the prestige gate kept the coach's new
    # school out of the player's pool -- and the transfer list alone cannot tell them
    # apart. Counting is free and consumes no RNG, so the next cycle can be checked
    # against this one instead of re-derived.
    diag = {"entrants": 0, "lost_a_coach": 0, "dest_in_pool": 0,
            "followed": 0, "pool_sizes": []}

    for e in entrants:
        pl, src, val = e["pl"], e["from"], e["val"]
        diag["entrants"] += 1
        _his_moves = [mv for mv in moves if mv["from"] == src]
        if _his_moves:
            diag["lost_a_coach"] += 1
        # The floor is position-relative for the same reason the entry test is: an
        # absolute cut-off silently decides which POSITIONS are allowed to transfer
        # rather than which PLAYERS are good enough.
        med = max(1.0, _med.get(pl["pos"], 1.0))
        # 2040 (Dan): the floor was a flat 1.05 x the position median for EVERY
        # destination, so a buried P6 backup (by definition under 0.32 x median) had
        # no taker anywhere and half of all P6 entrants withdrew; the lower division
        # never got the player it exists to catch. The floor now scales with the
        # destination's prestige: ~0.15 x median at a 30-prestige programme, ~0.9 x at 90.
        def floor_for(t):
            return med * max(0.12, 0.012 * PRESTIGE[t] - 0.2)
        pool = [t for t in TEAMS
                if t != src and committed[t] < cap
                and val >= max(floor_for(t), (PRESTIGE[t] - 45) * INTEREST_K * (med / 30.0))]
        if not pool:
            pl["team"] = src
            E.ROSTERS[src].append(pl)
            no_takers.append({"name": pl["name"], "pos": pl["pos"], "cls": pl["cls"],
                              "from": src, "value": round(val), "reason": e["reason"],
                              "outcome": "withdrew, returned to " + src})
            continue

        def pull(t):
            r = rec.get(t, {})
            hc = E.COACHES.get(t, {}).get("HC", {})
            return max(1.0, PRESTIGE[t] + r.get("W", 0) * 1.2 + hc.get("skill", 5.0) * 2.5)

        # 2040 (Dan): the exponent was 2.1-3.0 on a pull that is mostly prestige, so
        # a 90 outweighed a 30 by 10-25x and the portal ran L6 -> P6 168 to 10. Real
        # traffic runs heavily the other way for playing time. Flattened to 1.1-1.5
        # with the depth-chart factor below doing the real steering.
        # ...but a star still wants the big stage: the exponent climbs with value, so
        # a 200-value quarterback weighs prestige harder than before (3.1) while a
        # backup barely weighs it at all (1.1).
        k = 1.1 + min(2.1, max(0.0, (val - 30.0) * 0.012))
        w = [pull(t) ** k for t in pool]
        # ---- PLAYING TIME (Dan, 2039 end) ----
        # A transfer goes where he would start. He weighs the destination's depth
        # chart on what he can see -- the production of the players already there --
        # against his own line: a room with a full set of better-producing starters
        # who will still be around is worth a third as much as an open job.
        from recruiting import STARTERS, YOUNG
        need = STARTERS.get(pl["pos"], 2)
        for i, t in enumerate(pool):
            ahead = sum(1 for q in E.ROSTERS[t] if q["pos"] == pl["pos"] and not q.get("_leaving")
                        and q.get("cls") in YOUNG + ("Jr",) and _valmap.get(q["pid"], 0.0) >= val)
            w[i] *= 2.5 if ahead < need else 0.2
        diag["pool_sizes"].append(len(pool))
        if any(mv["to"] in pool for mv in _his_moves):
            diag["dest_in_pool"] += 1

        # ---- COACH FOLLOWING ----
        # This used to be a WEIGHT NUDGE and it did nothing. The destination is drawn
        # from a pool whose median size is 150 schools, so an average school's share is
        # about 0.67%; multiplying one school's weight by 3.5 takes it to 2.3%. In 2038
        # that produced ONE follow out of 59 players whose coach's new school was in
        # their pool -- 1.4 expected, so the feature was working exactly as written and
        # the number it produced was noise. Meanwhile 34 players moved with a reason that
        # explicitly named the staff change, and one of them went where the coach went.
        #
        # It is a DECISION now. A player whose own stated reason is the staff change
        # follows outright, most of the time, when the coach's new school will have him.
        # Anyone else keeps the old nudge, which is what it was always meant to be.
        OFF = {"QB", "RB", "WR", "TE", "OL"}
        FOLLOW_P = 0.55               # staff-driven movers who follow, when they can
        STAFF_REASON = ("staff turnover", "new staff")
        staff_driven = any(x in e["reason"] for x in STAFF_REASON)
        followable, strong = {}, []
        for mv in moves:
            if mv["from"] != src or mv["to"] not in pool:
                continue
            same_side = (mv["to_role"] == "HC") or \
                        (mv["to_role"] == "OC" and pl["pos"] in OFF) or \
                        (mv["to_role"] == "DC" and pl["pos"] not in OFF)
            w[pool.index(mv["to"])] *= 3.5 if same_side else 2.0
            followable[mv["to"]] = mv
            if same_side:
                strong.append(mv["to"])

        dest = None
        if staff_driven and strong and rng.random() < FOLLOW_P:
            dest = rng.choice(strong)
            diag["decided_follow"] = diag.get("decided_follow", 0) + 1
        if dest is None:
            dest = rng.choices(pool, weights=w)[0]
        reason = e["reason"]
        if dest in followable:
            mv = followable[dest]
            title = "Coach" if mv["to_role"] == "HC" else mv["to_role"]
            reason = "followed %s %s to %s" % (title, mv["coach"], dest)
            diag["followed"] += 1

        transfers.append({"name": pl["name"], "pos": pl["pos"], "cls": pl["cls"],
                          "from": src, "to": dest, "value": round(val),
                          "hidden_abil": pl["abil"], "reason": reason})
        pl["team"] = dest
        pl["transfer"] = True
        E.ROSTERS[dest].append(pl)
        committed[dest] += 1

    ps = diag.pop("pool_sizes")
    diag["pool_median"] = sorted(ps)[len(ps) // 2] if ps else 0
    s["portal_s%d" % s.get("season", 1)] = {"transfers": transfers,
                                            "no_takers": no_takers, "diag": diag}
    E.persist_rosters()
    SE.save_state(s)
    return transfers, no_takers


if __name__ == "__main__":
    tr, nt = run_portal()
    print("transfers: %d | withdrew: %d" % (len(tr), len(nt)))
