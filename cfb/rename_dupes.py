"""Rename players with duplicated surnames (keep the top wk-1 performer per surname).
New names from names_v2 (18 backgrounds incl. Roia ~8%, 40/40/20 pairing).
Propagates: rosters, season_state (stats + injury log), games_db (stats, scoring descs, injuries)."""
import sys, pickle, random, collections
sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E
import names_v2 as N
from committee import _prod_points

rng = random.Random(66110099)

with open('/home/claude/cfb2/state/season_state.pkl','rb') as f:
    S = pickle.load(f)
with open('/home/claude/cfb2/state/games_db.pkl','rb') as f:
    DB = pickle.load(f)

players = [pl for tm in E.ROSTERS.values() for pl in tm]
P = {pl["pid"]: pl for pl in players}
print(f"players: {len(players)}")

def surname(name): return name.split(" ", 1)[1]

groups = collections.defaultdict(list)
for pl in players:
    groups[surname(pl["name"])].append(pl)

dup_groups = {s: v for s, v in groups.items() if len(v) > 1}
print(f"distinct surnames: {len(groups)} | duplicated surnames: {len(dup_groups)} | players in dup groups: {sum(len(v) for v in dup_groups.values())}")

def production(pl):
    st = S["season_stats"].get(pl["pid"])
    return _prod_points(pl["pos"], st) if st else 0.0

# rank each dup group: production desc, hidden ability desc, pid
keep = {}
to_rename = []
for s, v in dup_groups.items():
    v.sort(key=lambda pl: (-production(pl), -pl["abil"], pl["pid"]))
    keep[s] = v[0]
    to_rename.extend(v[1:])
print(f"protected top performers: {len(keep)} | players to rename: {len(to_rename)}")

# used names: all current full names + coach names (kept names stay reserved)
used = set(pl["name"] for pl in players)
for cs in E.COACHES.values():
    for role in ("HC","OC","DC"):
        used.add(cs[role]["name"])

# surname usage: start with post-keep counts (each dup surname keeps exactly 1)
surname_usage = collections.Counter()
for s, v in groups.items():
    surname_usage[s] = 1 if s in dup_groups else len(v)

renames = {}   # pid -> (old, new, fb, lb)
bg_stats = collections.Counter()
pair_stats = collections.Counter()
for pl in sorted(to_rename, key=lambda x: x["pid"]):
    old = pl["name"]
    used.discard(old)  # the top performer keeps it; others' identical fulls may exist -> keep reserved if kept player's exact full name
    if keep[surname(old)]["name"] == old:
        used.add(old)   # exact same full name as the protected player: stay reserved
    new, fb, lb = N.pick_name_v2(rng, used, surname_usage=surname_usage, surname_cap=2)
    renames[pl["pid"]] = (old, new, fb, lb)
    pl["name"] = new
    if fb == "Roia" or lb == "Roia": bg_stats["roia"] += 1
    if fb == lb: pair_stats["same"] += 1
    elif lb in N.SIMILAR.get(fb, ()): pair_stats["similar"] += 1
    else: pair_stats["other"] += 1

# propagate: season stats + injury log
for pid, (old, new, fb, lb) in renames.items():
    if pid in S["season_stats"]:
        S["season_stats"][pid]["name"] = new
for entry in S["inj_log"]:
    if entry["pid"] in renames:
        entry["name"] = renames[entry["pid"]][1]

# propagate: games_db (stats, scoring play descriptions, injuries)
ambiguous = 0
for gid, box in DB.items():
    box_old_names = {}
    for pid, st in box["stats"].items():
        if pid in renames:
            old, new = renames[pid][0], renames[pid][1]
            st["name"] = new
            if old in box_old_names and box_old_names[old] != new:
                ambiguous += 1
            box_old_names[old] = new
    for sp in box["scoring_plays"]:
        for old, new in box_old_names.items():
            if old in sp["desc"]:
                sp["desc"] = sp["desc"].replace(old, new)
    for inj in box["injuries"]:
        if inj["pid"] in renames:
            inj["name"] = renames[inj["pid"]][1]

E.persist_rosters()
with open('/home/claude/cfb2/state/season_state.pkl','wb') as f:
    pickle.dump(S, f)
with open('/home/claude/cfb2/state/games_db.pkl','wb') as f:
    pickle.dump(DB, f)

n = len(renames)
print(f"\nrenamed {n} players | ambiguous same-name-in-box collisions: {ambiguous}")
print(f"Roia share of new names: {100*bg_stats['roia']/n:.1f}% (target ~8%)")
print(f"pairing: same-bg {100*pair_stats['same']/n:.0f}% | similar {100*pair_stats['similar']/n:.0f}% | other {100*pair_stats['other']/n:.0f}% (target 40/40/20)")

# after-state duplicate check
new_groups = collections.Counter(surname(pl["name"]) for pl in players)
still_dup = sum(1 for s, c in new_groups.items() if c > 1)
maxdup = new_groups.most_common(3)
print(f"surnames appearing 2+ times after rename: {still_dup} (was {len(dup_groups)}) | heaviest: {maxdup}")

print("\nsample renames:")
for pid in list(renames)[:10]:
    old, new, fb, lb = renames[pid]
    print(f"  {old} -> {new}  [{fb}/{lb}]")
print("\nsample protected stars (kept name despite duplicates):")
shown = 0
for s, pl in keep.items():
    if production(pl) > 25 and shown < 6:
        print(f"  {pl['name']} ({pl['team']} {pl['pos']}) kept '{s}' - wk1 prod {production(pl):.0f}, {len(dup_groups[s])-1} others renamed")
        shown += 1
