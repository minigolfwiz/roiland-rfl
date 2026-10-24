"""Replay a whole regular season in the sandbox and measure its SHAPE.

Dan's target, 2037, replacing the per-game framing:
  * 1-3 undefeated regular seasons a year
  * the top 5 averaging <= 1.2 losses; the top 15 rarely above 3
  * elite teams winning ~92-95% of their games against their actual schedule

Record distribution is multiplicative, so it is a far more sensitive instrument than any
single-game statistic: 80.5% a game and 93% a game look nearly identical on one Saturday
and produce 9-3 against 12-0 over a season. That is why this measures the season and not
the game.

Nothing is written. The 2037 schedule supplies the matchups so every arm plays the same
slate, and seeds are offset well clear of canon.
"""
import sys, collections, statistics
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db

SEED_OFFSET = 8_100_000


def run(seed_offset=SEED_OFFSET, verbose=False):
    SUB.register(E)
    s = SE.load_state()
    db = load_db()
    FBS = set(E.U["teams"])
    rec = collections.defaultdict(lambda: [0, 0])
    pts = []
    for i, (wk, gid) in enumerate(s["results"]):
        b = db.get(gid)
        if not b:
            continue
        h, a = b["home"], b["away"]
        site = "home"
        box, _ = E.simulate_game(h, a, seed_offset + i, site=site, keep_pbp=False)
        hw = box["home_score"] > box["away_score"]
        for t, won in ((h, hw), (a, not hw)):
            if t in FBS:
                rec[t][0 if won else 1] += 1
        pts += [box["home_score"], box["away_score"]]

    # rank by win total, then by points (a stand-in for the committee, good enough for
    # a shape measurement and immune to rating-model drift)
    diff = {}
    for t in rec:
        diff[t] = rec[t][0]
    order = sorted(rec, key=lambda t: (-rec[t][0], rec[t][1]))
    losses = {t: rec[t][1] for t in rec}
    und = [t for t in rec if losses[t] == 0]
    one = [t for t in rec if losses[t] == 1]
    top5 = order[:5]
    top15 = order[:15]
    top25 = order[:25]
    return {
        "pts_per_team": sum(pts) / len(pts),
        "undefeated": len(und),
        "und_names": und,
        "zero_or_one": len(und) + len(one),
        "top5_mean_losses": statistics.mean(losses[t] for t in top5),
        "top15_mean_losses": statistics.mean(losses[t] for t in top15),
        "top25_mean_losses": statistics.mean(losses[t] for t in top25),
        "top15_max_losses": max(losses[t] for t in top15),
        "best_record": "%d-%d" % tuple(rec[order[0]]),
        "top10": [(t, "%d-%d" % tuple(rec[t])) for t in order[:10]],
        "loss_hist": dict(sorted(collections.Counter(losses.values()).items())),
    }


def show(label, r):
    print("%s" % label)
    print("   pts/team                %.2f" % r["pts_per_team"])
    print("   undefeated teams        %d   %s" % (r["undefeated"], r["und_names"] or ""))
    print("   teams at 0 or 1 loss    %d" % r["zero_or_one"])
    print("   best record             %s" % r["best_record"])
    print("   mean losses: top5 %.1f | top15 %.1f | top25 %.1f | worst in top15: %d"
          % (r["top5_mean_losses"], r["top15_mean_losses"], r["top25_mean_losses"],
             r["top15_max_losses"]))
    print("   league loss histogram   %s" % r["loss_hist"])


if __name__ == "__main__":
    show("current engine", run())
