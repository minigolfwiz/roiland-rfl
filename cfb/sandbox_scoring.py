"""A/B the engine's scoring without touching canon.

Plays N games straight through `E.simulate_game` using the real rosters and real
matchups, and throws every result away -- nothing is written to the games database, the
season state or the rosters. That makes it safe to run the same slate against two
versions of the engine and compare.

Matchups and seeds come from the 2037 schedule, so both arms play the identical slate.
Seeds are offset by a constant so the sandbox never reuses a canon seed.
"""
import sys, json, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db

SEED_OFFSET = 7_000_000


def run(n=240, start=0, quiet=True):
    SUB.register(E)
    s = SE.load_state()
    db = load_db()
    slate = [(wk, gid) for wk, gid in s["results"] if wk >= 4]
    slate = slate[start:start + n]

    pts, games = [], 0
    qbreak_resets = 0
    crossings = 0
    for i, (wk, gid) in enumerate(slate):
        b = db.get(gid)
        if not b:
            continue
        home, away = b["home"], b["away"]
        box, pbp = E.simulate_game(home, away, SEED_OFFSET + i, site="home",
                                   keep_pbp=True)
        games += 1
        pts += [box["home_score"], box["away_score"]]
        # did any possession lose ground across a quarter break?
        plays = [p for p in pbp if isinstance(p, dict)]
        for j in range(1, len(plays)):
            a, c = plays[j - 1], plays[j]
            if a.get("q") == c.get("q") or c.get("q") == 3:
                continue
            if a.get("team") != c.get("team"):
                continue
            sa, sc = a.get("spot"), c.get("spot")
            if not isinstance(sa, (int, float)) or not isinstance(sc, (int, float)):
                continue
            crossings += 1
            if sc - sa < -10:
                qbreak_resets += 1
    return {
        "games": games,
        "pts_per_team": sum(pts) / len(pts) if pts else 0,
        "quarter_crossings": crossings,
        "resets": qbreak_resets,
        "reset_rate": qbreak_resets / crossings if crossings else 0,
    }


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 240
    r = run(n)
    print("sandbox: %d games (nothing written)" % r["games"])
    print("  pts per team            : %.2f   (target 24.40)" % r["pts_per_team"])
    print("  possessions crossing a quarter break: %d" % r["quarter_crossings"])
    print("  of those, ball moved back >10 yds   : %d  (%.0f%%)"
          % (r["resets"], 100 * r["reset_rate"]))
