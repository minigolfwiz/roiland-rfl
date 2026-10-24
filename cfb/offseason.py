"""DEAD CODE -- SUPERSEDED, AND DANGEROUS TO RUN. Kept for reference only.

This was the original monolithic offseason: draft -> transfers -> recruiting ->
development -> class rollover, all in one call. Every one of those stages now has its
own module, and those are what ran the 2035->2036 cycle. The live pipeline is:

    carousel.py -> draft.py -> portal.py -> recruiting.py -> development.py
                -> roster_final.py -> rollover.py

Two reasons this file must not run alongside that pipeline:

  * `run_offseason` does its OWN class rollover (stage 5 below). Run it and then
    `rollover.py` in the same cycle and every player on every roster advances TWO
    years -- freshmen become juniors, juniors graduate a year early.
  * its promotion table omits "RS", the redshirt dead end that `rollover.py` fixes.
    A redshirt processed here would never advance again.

`run_offseason` therefore raises on entry. The body is left intact because it is the
only surviving record of some of the original tuning; read it, do not call it.
"""
import pickle, random, math, collections
import sys; sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E
from committee import _prod_points
import names_v2 as NV

U = E.U; TEAMS = U["teams"]; PRESTIGE = U["prestige"]; TIERS = U["tiers"]; CONF = U["team_conf"]

def run_offseason(state, season_num, master_seed):
    raise RuntimeError(
        "offseason.run_offseason is dead code and would advance every player two "
        "classes if run alongside rollover.py. Use the standalone pipeline instead: "
        "carousel -> draft -> portal -> recruiting -> development -> roster_final "
        "-> rollover. See this module's docstring."
    )
    rng = random.Random(master_seed)
    log = {"draft": [], "withdrawals": [], "transfers": [], "recruiting": {}, "development": [], "graduated": 0}
    P = {p["pid"]: p for tm in E.ROSTERS.values() for p in tm}
    prod = {pid: _prod_points(P[pid]["pos"], s) for pid, s in state["season_stats"].items() if pid in P}

    # ---- 1) DRAFT ----
    declared = []
    for tm in E.ROSTERS.values():
        for pl in tm:
            pr = prod.get(pl["pid"], 0.0)
            if pl["cls"] in ("Sr", "RS"):
                declared.append((pl, pr, False))          # seniors: out regardless
            elif pl["cls"] == "Jr":
                urge = (pl["abil"]-7.0)*0.11 + pr/220.0
                if rng.random() < max(0.0, min(0.85, urge)):
                    declared.append((pl, pr, True))       # early entrant
    # scouting: observed production + noisy read of ability
    POSVAL = {"QB":1.12,"WR":1.06,"DL":1.08,"CB":1.05,"OL":1.02,"RB":0.98,"TE":0.97,"LB":1.0,"S":0.99,"K":0.45,"P":0.42,"ATH":0.9}
    board = []
    for pl, pr, early in declared:
        scout = (pr*0.011 + pl["abil"]*0.62 + rng.gauss(0, 1.15)) * POSVAL.get(pl["pos"],1.0)
        board.append((scout, pl, pr, early))
    board.sort(key=lambda x: -x[0])
    n_picks = 112  # 4 rounds x 28
    drafted = set()
    for i, (scout, pl, pr, early) in enumerate(board[:n_picks]):
        rd = i//28 + 1
        drafted.add(pl["pid"])
        log["draft"].append({"pick": i+1, "round": rd, "name": pl["name"], "team": pl["team"],
                             "pos": pl["pos"], "cls": pl["cls"], "early": early,
                             "inj_flags": len([h for h in pl["inj_hist"] if h["weeks"] >= 3])})
    # withdrawal: undrafted early entrants mostly return
    leaving = set(drafted)
    for scout, pl, pr, early in board[n_picks:]:
        if early and rng.random() < 0.85:
            log["withdrawals"].append({"name": pl["name"], "team": pl["team"], "pos": pl["pos"]})
        else:
            leaving.add(pl["pid"])
    # seniors not drafted still graduate
    for pl, pr, early in declared:
        if not early:
            leaving.add(pl["pid"])
    log["graduated"] = sum(1 for pl, pr, e in declared if not e)
    for t in TEAMS:
        E.ROSTERS[t] = [pl for pl in E.ROSTERS[t] if pl["pid"] not in leaving]

    # ---- 2) TRANSFER PORTAL (valuation = OBSERVED production) ----
    portal = []
    for t in TEAMS:
        keep = []
        for pl in E.ROSTERS[t]:
            pr = prod.get(pl["pid"], 0.0)
            small = PRESTIGE[t] < 55
            starved = pr < 5 and pl["cls"] in ("So","Jr") and pl["abil"] > PRESTIGE[t]/100*3.3 + 4.6
            star_small = small and pr > 140
            p_leave = 0.06 + (0.34 if star_small else 0) + (0.10 if starved else 0)
            if rng.random() < p_leave:
                portal.append((pl, pr))
            else:
                keep.append(pl)
        E.ROSTERS[t] = keep
    # market: teams bid by prestige; value keyed to observed production (+rep), NOT hidden ability
    portal.sort(key=lambda x: -(x[1] + 40*math.tanh(x[0].get("rep",0))))
    for pl, pr in portal:
        pool = [t for t in TEAMS if t != pl["team"] and len(E.ROSTERS[t]) < 70]
        w = [max(1.0, PRESTIGE[t])**2.1 for t in pool]
        dest = rng.choices(pool, weights=w)[0]
        log["transfers"].append({"name": pl["name"], "pos": pl["pos"], "cls": pl["cls"],
                                 "from": pl["team"], "to": dest, "observed_prod": round(pr),
                                 "hidden_abil": pl["abil"]})
        pl["team"] = dest; pl["transfer"] = True
        E.ROSTERS[dest].append(pl)

    # ---- 3) RECRUITING (class-balance: gems capped below elite-veteran tier) ----
    import collections as _c
    used = set(p["name"] for tm in E.ROSTERS.values() for p in tm)
    used |= set(c[r]["name"] for c in E.COACHES.values() for r in ("HC","OC","DC"))
    _susage = _c.Counter(p["name"].split()[-1] for tm in E.ROSTERS.values() for p in tm)
    def new_name():
        return NV.pick_name_v2(rng, used, surname_usage=_susage, surname_cap=2)[0]
    from gen_rosters_lib import ROSTER_TEMPLATE, ARCHETYPES
    next_pid = max(p["pid"] for tm in E.ROSTERS.values() for p in tm) + 1
    for t in TEAMS:
        quality = PRESTIGE[t]/10*0.62 + (state["record"][t]["W"]-6)*0.09
        counts = collections.Counter(p["pos"] for p in E.ROSTERS[t])
        cls_stars = []
        for pos, target in ROSTER_TEMPLATE:
            for _ in range(max(0, target - counts.get(pos, 0))):
                abil = rng.gauss(3.55 + quality*0.42, 1.0)
                if rng.random() < 0.012: abil += rng.uniform(1.0, 2.0)
                abil = max(1.5, min(8.6, abil))          # freshman gem cap (spec 11)
                arch = rng.choices([a for a,_ in ARCHETYPES[pos]], weights=[w for _,w in ARCHETYPES[pos]])[0]
                pl = {"pid": next_pid, "name": new_name(), "team": t, "pos": pos, "cls": "Fr",
                      "arch": arch, "abil": round(abil,2),
                      "dur": round(max(0.15, min(0.95, rng.gauss(0.62, 0.15))), 3),
                      "rep": 0.0, "inj_hist": [], "freshman": True}
                next_pid += 1
                E.ROSTERS[t].append(pl)
                stars = 5 if abil >= 7.6 else 4 if abil >= 6.6 else 3 if abil >= 5.4 else 2
                cls_stars.append(stars)
        log["recruiting"][t] = {"n": len(cls_stars), "avg_stars": round(sum(cls_stars)/max(1,len(cls_stars)),2),
                                "five_stars": cls_stars.count(5)}

    # ---- 4) DEVELOPMENT ----
    GROW = {"Fr": 0.52, "So": 0.34, "Jr": 0.17, "Sr": 0.0, "RS": 0.10}
    for t in TEAMS:
        for pl in E.ROSTERS[t]:
            if pl.get("freshman"): continue
            head = max(0.0, 9.9 - pl["abil"])
            g = max(-0.25, rng.gauss(GROW.get(pl["cls"], 0.2) * head/4.4, 0.16))
            if g > 0.65: log["development"].append({"name": pl["name"], "team": pl["team"], "pos": pl["pos"], "jump": round(g,2)})
            pl["abil"] = round(min(9.95, pl["abil"] + g), 2)
            pl["rep"] *= 0.5

    # ---- 5) CLASS ROLLOVER ----
    up = {"Fr": "So", "So": "Jr", "Jr": "Sr"}
    for t in TEAMS:
        for pl in E.ROSTERS[t]:
            if pl.get("freshman"): pl.pop("freshman"); continue
            if pl["cls"] in up:
                if pl["cls"] == "Fr" and rng.random() < 0.07: pl["cls"] = "RS"
                else: pl["cls"] = up[pl["cls"]]
    E.persist_rosters()
    with open(f'/home/claude/cfb2/state/offseason_s{season_num}.pkl','wb') as f:
        pickle.dump(log, f)
    return log
