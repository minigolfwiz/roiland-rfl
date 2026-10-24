"""Does roster/coaching quality show up on the scoreboard?

For each sandbox game, pair the pre-game talent gap with what actually happened. A
league with working parity shows a strong relationship: big gaps produce big margins and
reliable favourites. The complaint was that every game played like a coin flip, which in
these terms means a flat slope and a favourite win rate near 50%.
"""
import sys, statistics; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db

def run(n=300, seed_offset=7_000_000):
    SUB.register(E)
    s = SE.load_state(); db = load_db()
    slate = [(wk, gid) for wk, gid in s["results"] if wk >= 4][:n]
    gaps, margins, fav_win, pts = [], [], [], []
    for i, (wk, gid) in enumerate(slate):
        b = db.get(gid)
        if not b: continue
        h, a = b["home"], b["away"]
        try: gap = SE._talent(h) - SE._talent(a)
        except Exception: continue
        box, _ = E.simulate_game(h, a, seed_offset + i, site="home", keep_pbp=False)
        m = box["home_score"] - box["away_score"]
        gaps.append(gap); margins.append(m)
        pts += [box["home_score"], box["away_score"]]
        if abs(gap) > 0.15:
            fav_win.append(1 if (m > 0) == (gap > 0) else 0)
    # least squares slope of margin on talent gap
    mg, mm = statistics.mean(gaps), statistics.mean(margins)
    num = sum((g-mg)*(x-mm) for g, x in zip(gaps, margins))
    den = sum((g-mg)**2 for g in gaps)
    slope = num/den if den else 0
    # correlation
    sg = statistics.pstdev(gaps); sm = statistics.pstdev(margins)
    corr = (num/len(gaps))/(sg*sm) if sg and sm else 0
    # how often a CLEAR mismatch produced a blowout
    big = [(g, x) for g, x in zip(gaps, margins) if abs(g) > 0.6]
    blow = sum(1 for g, x in big if abs(x) >= 21)
    return {"games": len(gaps), "pts_per_team": sum(pts)/len(pts),
            "slope": slope, "corr": corr,
            "fav_win": sum(fav_win)/len(fav_win) if fav_win else 0,
            "n_fav": len(fav_win),
            "mean_abs_margin": statistics.mean(abs(x) for x in margins),
            "one_score": sum(1 for x in margins if abs(x) <= 8)/len(margins),
            "blowout_rate_big_gap": blow/len(big) if big else 0, "n_big": len(big)}

def show(label, r):
    print("%s  (%d games)" % (label, r["games"]))
    print("   pts/team                         %.2f" % r["pts_per_team"])
    print("   margin vs talent gap: slope      %.2f pts per unit of talent" % r["slope"])
    print("   margin vs talent gap: corr       %.3f" % r["corr"])
    print("   favourite wins (gap > 0.15)      %.1f%%  (n=%d)" % (100*r["fav_win"], r["n_fav"]))
    print("   mean margin                      %.1f" % r["mean_abs_margin"])
    print("   one-score games (<=8)            %.1f%%" % (100*r["one_score"]))
    print("   blowouts when gap > 0.6          %.1f%%  (n=%d)" % (100*r["blowout_rate_big_gap"], r["n_big"]))

if __name__ == "__main__":
    show("current engine", run(int(sys.argv[1]) if len(sys.argv) > 1 else 300))
