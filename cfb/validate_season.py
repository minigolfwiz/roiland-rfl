"""Phase 2 validation: simulate full synthetic seasons (152 teams x 12 games = 912 games each),
accumulate season stats, compare national leaders + distributions to real CFB reference numbers.
"""
import sys, random, statistics, time, collections
sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E

def run_season(season_tag, seed_offset, do_reputation=True):
    rng = random.Random(4400 + seed_offset)
    teams = list(E.U["teams"])
    prestige = E.U["prestige"]
    season = collections.defaultdict(lambda: collections.defaultdict(float))
    meta = {}
    per_game = collections.defaultdict(list)   # pid -> list of key volume-stat per game (for CV)
    injuries_all = []
    backup_qb_games = 0
    totals = []
    counter = seed_offset * 10000
    t0 = time.time()
    for week in range(12):
        order = sorted(teams, key=lambda t: prestige[t] + rng.gauss(0, 9))
        for i in range(0, len(order), 2):
            h, a = order[i], order[i+1]
            if rng.random() < 0.5: h, a = a, h
            box, _ = E.simulate_game(h, a, seed=E.game_seed(counter), keep_pbp=False)
            counter += 1
            totals.append(box["home_score"] + box["away_score"])
            injuries_all.extend(box["injuries"])
            # detect garbage-time backup QB usage
            qb_atts = [(s.get("Att",0), pid, s) for pid, s in box["stats"].items() if s["pos"]=="QB" and s.get("Att",0)>0]
            for t in (h, a):
                t_qbs = [x for x in qb_atts if x[2]["team"] == t]
                if len(t_qbs) >= 2: backup_qb_games += 1
            for pid, s in box["stats"].items():
                meta[pid] = (s["name"], s["team"], s["pos"], s["cls"])
                for k, v in s.items():
                    if isinstance(v, (int, float)):
                        season[pid][k] += v
                if s["pos"] == "QB" and s.get("Att",0) >= 10: per_game[pid].append(s.get("PassYds",0))
                if s["pos"] == "RB" and s.get("RushAtt",0) >= 8: per_game[pid].append(s.get("RushYds",0))
                if s["pos"] in ("WR","TE") and s.get("Targets",0) >= 4: per_game[pid].append(s.get("RecYds",0))
            if do_reputation:
                E.update_reputation(box)
    dt = time.time() - t0
    return dict(season=season, meta=meta, per_game=per_game, injuries=injuries_all,
                backup_qb_games=backup_qb_games, totals=totals, secs=dt, n_games=counter - seed_offset*10000)

def leaders(res, key, pos_filter, n=5, min_key=None, min_val=0):
    rows = []
    for pid, s in res["season"].items():
        name, team, pos, cls = res["meta"][pid]
        if pos not in pos_filter: continue
        if min_key and s.get(min_key,0) < min_val: continue
        rows.append((s.get(key,0), name, team, pos, s))
    rows.sort(reverse=True, key=lambda x: x[0])
    return rows[:n]

def report(res, tag):
    print(f"\n================ SEASON {tag}: {res['n_games']} games in {res['secs']:.1f}s ================")
    print(f"avg total pts {statistics.mean(res['totals']):.1f} (real CFB ~55) | sd {statistics.stdev(res['totals']):.1f}")
    print("\nPASSING LEADERS (real #1 ~4,500-5,700; ~8-12 hit 4,000):")
    for v, name, team, pos, s in leaders(res, "PassYds", ("QB",)):
        print(f"  {int(v):5d} yds  {name} ({team})  {int(s.get('PassTD',0))} TD {int(s.get('INT',0))} INT  {int(s.get('Comp',0))}/{int(s.get('Att',0))}")
    n4000 = sum(1 for pid,s in res["season"].items() if res["meta"][pid][2]=="QB" and s.get("PassYds",0)>=4000)
    print(f"  4,000+ yd passers: {n4000}")
    print("\nRUSHING LEADERS (real #1 ~1,900-2,600; ~25-40 hit 1,000):")
    for v, name, team, pos, s in leaders(res, "RushYds", ("RB","QB")):
        print(f"  {int(v):5d} yds  {name} ({team},{pos})  {int(s.get('RushTD',0))} TD on {int(s.get('RushAtt',0))} car")
    n1000 = sum(1 for pid,s in res["season"].items() if res["meta"][pid][2]=="RB" and s.get("RushYds",0)>=1000)
    print(f"  1,000+ yd rushers: {n1000}")
    print("\nRECEIVING LEADERS (real #1 ~1,500-1,800; ~25-45 hit 1,000):")
    for v, name, team, pos, s in leaders(res, "RecYds", ("WR","TE","ATH")):
        print(f"  {int(v):5d} yds  {name} ({team})  {int(s.get('Rec',0))} rec {int(s.get('RecTD',0))} TD")
    n1000r = sum(1 for pid,s in res["season"].items() if res["meta"][pid][2] in ("WR","TE") and s.get("RecYds",0)>=1000)
    print(f"  1,000+ yd receivers: {n1000r}")
    print("\nSACK LEADERS (real #1 ~13-17.5):")
    for v, name, team, pos, s in leaders(res, "Sacks", ("DL","LB")):
        print(f"  {v:4.1f}  {name} ({team},{pos})")
    print("\nINT LEADERS (real #1 ~6-9):")
    for v, name, team, pos, s in leaders(res, "INT_def", ("CB","S","LB")):
        print(f"  {int(v):2d}  {name} ({team},{pos})")
    # star CV (spec 4: 0.30-0.35 for stars)
    cvs = []
    vols = sorted(((sum(g), pid) for pid, g in res["per_game"].items() if len(g) >= 9), reverse=True)[:40]
    for _, pid in vols:
        g = res["per_game"][pid]
        m = statistics.mean(g)
        if m > 20: cvs.append(statistics.stdev(g)/m)
    print(f"\nSTAR game-to-game CV (top 40 by volume): mean {statistics.mean(cvs):.2f} (spec target 0.30-0.35)")
    # injuries
    inj = res["injuries"]
    sev = collections.Counter("season" if i["weeks_out"]>=99 else ("multi" if i["weeks_out"]>=3 else "minor") for i in inj)
    n = max(1,len(inj))
    print(f"\nINJURIES: {len(inj)} total = {len(inj)/res['n_games']:.2f}/game | minor {100*sev['minor']/n:.0f}% / multi-week {100*sev['multi']/n:.0f}% / season-ending {100*sev['season']/n:.0f}% (spec 60/35/5)")
    print(f"  sample: " + "; ".join(f"{i['name']} ({i['pos']}) {i['desc']} Q{i['q']} [{'season' if i['weeks_out']>=99 else str(i['weeks_out'])+'wk'}]" for i in inj[:3]))
    print(f"GARBAGE TIME: backup QB threw a pass in {res['backup_qb_games']} team-games (evidence of starter rest)")
    # reputation risers
    reps = sorted(((pl.get("rep",0), pl["name"], pl["team"], pl["pos"], pl["abil"]) for tm in E.ROSTERS.values() for pl in tm), reverse=True)[:5]
    print("TOP REPUTATION RISERS (usage boost active):")
    for r, name, team, pos, ab in reps:
        print(f"  rep {r:+.2f}  {name} ({team},{pos}) hidden abil {ab}")

if __name__ == "__main__":
    res = run_season("A", seed_offset=1)
    report(res, "A")
