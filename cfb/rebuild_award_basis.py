"""Rebuild the canon award-basis stat aggregate from the game database.

WHY THIS EXISTS. The canon basis for individual awards is the regular season plus the
conference title games, and nothing else -- the playoff is excluded, so a trophy cannot
be won in January. `playoff.run_champ` honours that only if it is handed the aggregate
taken BEFORE round one, saved at `state/season_state.pkl.pre_s{N}_po_r1`.

In 2038 nothing took that snapshot. `install_field.py` writes the bracket and does not
save state; `playoff.run_round1` does not either. By the time anybody noticed, two
playoff rounds were in `season_stats` and the file the finaliser looks for did not
exist, so awards would either have silently included playoff production or not been
written at all.

The snapshot is recoverable because every box score is in the database and every
postseason game is identifiable by its id. So rather than guess, this rebuilds the
aggregate the same way the season built it -- `SE.merge_stats` over box scores, in the
order they were played -- from exactly the games that belong in the basis:

    S{N}W*    regular season        included
    S{N}CCG_* conference finals     included
    S{N}PO_*  playoff               EXCLUDED

The result is written to the path the finaliser reads. It is checked against the live
aggregate before anything is saved: every basis player must appear, and no basis total
may exceed the live total, because the live one is this plus the playoff.

    python3 rebuild_award_basis.py            # dry run, prints the differences
    python3 rebuild_award_basis.py --commit
"""
import sys, os, re, pickle, copy
sys.path.insert(0, '/home/claude/cfb2')
import season as SE
from games_db import load_db

STATE = '/home/claude/cfb2/state'


def basis_games(db, season):
    """Every game id in the award basis, in the order it was played."""
    reg, ccg = [], []
    for gid, b in db.items():
        g = str(gid)
        if not g.startswith("S%d" % season):
            continue
        if "PO_" in g:
            continue
        (ccg if "CCG" in g else reg).append((b.get("week", 0) or 0, g))
    reg.sort()
    ccg.sort()
    return [g for _w, g in reg] + [g for _w, g in ccg]


def build(commit=False):
    s = SE.load_state()
    season = s["season"]
    db = load_db()
    out = os.path.join(STATE, 'season_state.pkl.pre_s%d_po_r1' % season)
    if os.path.exists(out):
        raise SystemExit("%s already exists -- refusing to overwrite a real snapshot" % out)

    gids = basis_games(db, season)
    agg = {}
    for gid in gids:
        SE.merge_stats(agg, db[gid])

    live = s["season_stats"]
    # ---- checks -----------------------------------------------------------------
    missing = [p for p in agg if p not in live]
    if missing:
        raise SystemExit("%d players in the basis are absent from the live aggregate -- "
                         "the rebuild does not match the season" % len(missing))
    # The real invariant is that basis + playoff adds back up to the live aggregate,
    # exactly. The first version of this check instead asserted that no basis total may
    # exceed the live total, which is not true: a player can LOSE yardage in a playoff
    # game. Larksdale's Zhenzhen Yeon-Won ran for 1,184 through the conference final and
    # for -1 against Ranroman, so his basis total is legitimately one yard higher than
    # the live one, and the weaker check failed on four such players.
    po = {}
    for gid, b in db.items():
        if str(gid).startswith("S%dPO_" % season):
            SE.merge_stats(po, b)
    bad = []
    for pid, lv in live.items():
        for k, v in lv.items():
            if not isinstance(v, (int, float)):
                continue
            want = agg.get(pid, {}).get(k, 0) + po.get(pid, {}).get(k, 0)
            if abs(want - v) > 1e-6:
                bad.append((lv.get("name"), k, agg.get(pid, {}).get(k, 0),
                            po.get(pid, {}).get(k, 0), v))
    if bad:
        raise SystemExit("basis + playoff does not reconstruct the live aggregate "
                         "(%d mismatches): %s" % (len(bad), bad[:5]))

    playoff_only = [p for p in live if p not in agg]
    print("award basis for season %d (%d)" % (season, 2025 + season))
    print("  games: %d regular + conference finals" % len(gids))
    print("  players: %d in the basis, %d in the live aggregate" % (len(agg), len(live)))
    print("  appeared only in the playoff: %d" % len(playoff_only))
    # a couple of worked examples, so the exclusion is visible rather than asserted
    shown = 0
    for pid, d in sorted(agg.items(), key=lambda kv: -(kv[1].get("PassYds", 0))):
        lv = live[pid]
        if lv.get("PassYds", 0) > d.get("PassYds", 0):
            print("    %-26s %s  basis %d pass yds, with the playoff %d"
                  % (d.get("name"), d.get("team"), d.get("PassYds", 0), lv.get("PassYds", 0)))
            shown += 1
            if shown >= 3:
                break

    if not commit:
        print("\nDRY RUN. Re-run with --commit to write the snapshot.")
        return agg

    snap = copy.deepcopy(s)
    snap["season_stats"] = agg
    with open(out, 'wb') as f:
        pickle.dump(snap, f)
    print("\nWROTE %s" % out)
    return agg


if __name__ == "__main__":
    build(commit='--commit' in sys.argv)
