"""Give thirteen seasons of football their due, then restart 2038 on the same schedule.

Dan's call, 2026-10-09. Two things happen here and they have to happen in this order:

  1. PRESTIGE IS BACK-APPLIED. Every programme's prestige becomes
         0.45 * what Dan designed  +  0.55 * what it has earned
     where "earned" is thirteen seasons of Elo -- schedule-adjusted, so beating the Low
     Sixteen is not the same as beating the Great Fourteen. The 45% anchor is deliberate:
     pure merit flattened the P6/L6 cliff from 33 points to under 10 and dissolved the
     tier architecture. At 55% the cliff survives at 20 points while programmes still
     move up to 40.

  2. ROSTERS ARE REGENERATED from the new prestige, because every recruiting class since
     2026 would have been different. Keeping the old rosters would have meant a restart
     that played almost identically.

WHAT IS DESTROYED, stated plainly: the 2038 rosters as they stand, including the players
named in the preseason notes, the incoming recruiting class and the portal moves, are
replaced by the players the new prestige would have produced. Coaching staffs are NOT
touched -- the carousel is history and the coaches earned their jobs.

WHAT IS PRESERVED: the schedule, exactly; every game of seasons 1-12; every programme's
identity, conference, colours and title history.

WHAT IS VOIDED: weeks 0 and 1 of 2038, 106 games. Under the standing rule, once this
runs those games never happened and are never referenced again.

Everything is backed up before anything is written. Run with --commit to do it.
"""
import sys, os, json, shutil, pickle, random, collections, statistics
sys.path.insert(0, '/home/claude/cfb2')

STATE = '/home/claude/cfb2/state'
BLEND = 0.55            # share of prestige that is earned rather than designed
SEASON = 13
TAG = '.pre_prestige_s13'


def backup(paths):
    """Copy each file aside, and REFUSE if one of them is not there.

    The first version skipped missing files silently and returned a list of what it had
    managed to copy. It was called with 'games.pkl' and 'state.pkl'; the real names are
    'games_db.pkl' and 'season_state.pkl', so it quietly backed up neither and reported
    success. The restart then deleted 106 games that no longer exist anywhere. A backup
    routine that cannot tell 'saved' from 'not found' is worse than none, because it
    reports the same thing either way.
    """
    missing = [f for f in paths if not os.path.exists(os.path.join(STATE, f))]
    if missing:
        raise SystemExit('BACKUP ABORTED - these do not exist: %s\n'
                         'Nothing has been written. Fix the names and re-run.' % missing)
    done = []
    for f in paths:
        p = os.path.join(STATE, f)
        shutil.copy(p, p + TAG)
        if os.path.getsize(p + TAG) != os.path.getsize(p):
            raise SystemExit('BACKUP ABORTED - %s did not copy cleanly.' % f)
        done.append(f)
    return done


def new_prestige(U, db):
    import prestige as P
    elo = P.elo_history(db, U["teams"], through=SEASON)
    last = elo[max(elo)]
    lo, hi = min(last.values()), max(last.values())
    earned = {t: 5.0 + 92.0 * (last[t] - lo) / (hi - lo) for t in U["teams"]}
    out = {}
    for t in U["teams"]:
        out[t] = round(U["prestige"][t] * (1 - BLEND) + earned[t] * BLEND, 1)
    return out, earned


def regen_rosters(U, seed=20380009):
    """Rebuild every FBS roster from the new prestige, using gen_rosters' own code.

    `derive_attrs` and the roster template are lifted out of gen_rosters.py rather than
    reimplemented, so a 2038 roster is built by exactly the code that built every other
    one. Only the prestige feeding it has changed.
    """
    import pbp_engine as E
    src = open('/home/claude/cfb2/gen_rosters.py').read()
    head = src[:src.index('rosters = {}')]
    # gen_rosters still imports the original `names` module, which lived in the old cfb
    # tree and is gone. Names here come from names_v2 instead, so the import is stubbed
    # rather than restored -- nothing below it in the lifted section uses those lists.
    head = head.replace('from names import FIRST_NAMES, LAST_NAMES',
                        'FIRST_NAMES, LAST_NAMES = ["A"], ["B"]')
    ns = {}
    exec(compile(head, 'gen_rosters_head', 'exec'), ns)
    derive = ns['derive_attrs']; pick_arch = ns['pick_arch']
    TEMPLATE = ns['ROSTER_TEMPLATE']; CLASSES = ns['CLASSES']
    CLASS_W = ns['CLASS_W']; CLASS_AB = ns['CLASS_AB']
    import names_v2 as NV
    rng = random.Random(seed)
    used = set(); sur = collections.Counter()
    def fresh():
        n = NV.pick_name_v2(rng, used, surname_usage=sur, surname_cap=2)
        n = n[0] if isinstance(n, (tuple, list)) else n
        used.add(n); sur[n.split()[-1]] += 1
        return n
    # Match each programme's CURRENT roster size rather than the bare template. The
    # template is 62; live rosters run 63-70 because recruiting and attrition have moved
    # them. Generating a flat 62 would leave every programme one or more short of
    # ROSTER_MIN, which is exactly the shortfall that produced a league full of walk-ons
    # the last time it happened.
    want = {t: max(len(E.ROSTERS.get(t) or []), sum(n for _p, n in TEMPLATE))
            for t in U["teams"]}
    fill_pos = [pos for pos, n in TEMPLATE for _ in range(n)]

    pid = 2_000_000
    out = {}
    for team in U["teams"]:
        p = U["prestige"][team]
        base = 4.15 + (p / 100) * 3.3
        players = []
        slots = [(pos, 1) for pos, n in TEMPLATE for _ in range(n)]
        extra = want[team] - len(slots)
        slots += [(rng.choice(fill_pos), 1) for _ in range(max(0, extra))]
        for pos, n in slots:
            for _ in range(n):
                cls = rng.choices(CLASSES, weights=CLASS_W)[0]
                abil = rng.gauss(base + CLASS_AB[cls], 1.05)
                if rng.random() < 0.015:
                    abil += rng.uniform(1.2, 2.4)
                abil = max(1.5, min(9.95, abil))
                arch = pick_arch(pos)
                pid += 1
                players.append({
                    "pid": pid, "name": fresh(), "team": team, "pos": pos, "cls": cls,
                    "arch": arch, "abil": round(abil, 2),
                    "dur": round(max(0.15, min(0.95, rng.gauss(0.62, 0.15))), 3),
                    "rep": 0.0, "inj_hist": [],
                    "attrs": derive(pos, abil, arch, cls),
                    "pot": round(min(10.0, abil + max(0.0, rng.gauss(0.9, 0.6))), 2),
                })
        out[team] = players
    return out


def main(commit=False):
    import season as SE, pbp_engine as E
    from games_db import load_db, save_db, load_reg, save_reg
    U = E.U
    db, reg = load_db(), load_reg()
    s = SE.load_state()
    if s.get("season") != SEASON:
        raise SystemExit("state is season %s, this restarts %d" % (s.get("season"), SEASON))

    newp, earned = new_prestige(U, db)
    old = dict(U["prestige"])
    moves = sorted(((newp[t] - old[t], t) for t in U["teams"]))
    s13 = [gid for gid in db if str(gid).startswith("S%d" % SEASON)]

    print("PRESTIGE  %d%% earned / %d%% designed" % (BLEND * 100, (1 - BLEND) * 100))
    print("  biggest fallers: %s" % ", ".join("%s %.0f->%.0f" % (t, old[t], newp[t]) for _d, t in moves[:5]))
    print("  biggest risers : %s" % ", ".join("%s %.0f->%.0f" % (t, old[t], newp[t]) for _d, t in moves[-5:]))
    spread_old = statistics.pstdev([statistics.mean(old[t] for t in tl) for tl in U["conferences"].values()])
    spread_new = statistics.pstdev([statistics.mean(newp[t] for t in tl) for tl in U["conferences"].values()])
    print("  conference spread %.1f -> %.1f" % (spread_old, spread_new))
    print("ROSTERS   152 regenerated from the new prestige")
    print("SEASON    voiding %d played games, schedule of %d kept" % (len(s13), len(s["sched"])))
    if not commit:
        print("\nDRY RUN. Re-run with --commit.")
        return

    backup(['universe.pkl', 'rosters.pkl', 'season_state.pkl', 'games_db.pkl',
            'seed_registry.pkl'])

    # ---- 1. prestige ----
    U["prestige"] = newp
    U["prestige_designed"] = old                 # what Dan originally set, kept for the anchor
    U["prestige_dynamic_from"] = SEASON
    pickle.dump(U, open(os.path.join(STATE, 'universe.pkl'), 'wb'))

    # ---- 2. rosters ----
    ros = regen_rosters(U)
    pickle.dump(ros, open(os.path.join(STATE, 'rosters.pkl'), 'wb'))

    # ---- 3. void season 13 and rewind to week 0 ----
    for gid in s13:
        del db[gid]
    if isinstance(reg.get("assigned"), dict):
        for gid in s13:
            reg["assigned"].pop(gid, None)
    save_db(db); save_reg(reg)

    s["results"] = []
    s["next_week"] = 0
    s["record"] = {t: {"W": 0, "L": 0, "confW": 0, "confL": 0, "PF": 0, "PA": 0} for t in U["teams"]}
    s["season_stats"] = {}
    s["inj_out"] = {}; s["inj_recent"] = {}; s["inj_log"] = []
    s["heat"] = {t: 0.0 for t in U["teams"]}
    for k in list(s):
        if k.startswith("media_poll") or k.startswith("committee"):
            s.pop(k, None)
    SE.save_state(s)
    print("\nRESTARTED. Season %d is at week 0 on the same schedule." % SEASON)


if __name__ == "__main__":
    main(commit='--commit' in sys.argv)
