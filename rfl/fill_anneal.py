"""Finish a partial board under Dan's rules by local search with timetabling moves.
Stage 1: build any complete assignment where every club plays once a week with two byes (MRV with restarts — easy).
Stage 2: anneal with structure-preserving moves (whole-week swaps and partial swaps with ejection chains) on the real rules:
byes in 4–11 and 12–18 with ≥3 games between, no three home/road games in a row (byes don't reset), division rematches not in
consecutive weeks, and a penalty for moving one of Dan's placed games. Usage: python3 rfl/fill_anneal.py 2043 [seed] [seconds]"""
import json, sys, os, random, collections, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import ROOT, load
yr = int(sys.argv[1]); seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1; budget = float(sys.argv[3]) if len(sys.argv) > 3 else 500
G = load(f'{ROOT}/data/matchups_{yr}.json'); saved = load(f'{ROOT}/data/db/rfl/schedule{yr}.json')
fixed = {r['id']: r['week'] for r in saved['weeks'] if r.get('week') is not None}
W = list(range(1, 21)); rnd = random.Random(seed); teams = sorted({g['host'] for g in G}); NG = len(G)
by_team = collections.defaultdict(list)
for i, g in enumerate(G): by_team[g['host']].append(i); by_team[g['visitor']].append(i)
host = [g['host'] for g in G]; vis = [g['visitor'] for g in G]; isdiv = [g['kind'] == 'division' for g in G]
fixw = [fixed.get(g['id']) for g in G]; FIXW = float(os.environ.get('FIXW', 2.0))
def opp(i, t): return vis[i] if host[i] == t else host[i]

# ---------------------------------------------------------------- stage 1: one game a week, two byes (any weeks)
def stage1():
    for attempt in range(1, 2000):
        r = random.Random(seed * 1000 + attempt)
        week = [fixw[i] for i in range(NG)]; slot = {t: [None] * 21 for t in teams}
        ok = True
        for i, w in enumerate(week):
            if w is not None:
                for t in (host[i], vis[i]):
                    if slot[t][w] is not None: ok = False
                    slot[t][w] = i
        if not ok: break
        left = [i for i in range(NG) if week[i] is None]
        def free(i): return [w for w in W if slot[host[i]][w] is None and slot[vis[i]][w] is None]
        stuck = False
        while left:
            i = min(left, key=lambda k: (len(free(k)), r.random())); f = free(i)
            if not f: stuck = True; break
            per = collections.Counter(w for w in week if w is not None)
            w = min(f, key=lambda w: per[w] + r.random() * .8); week[i] = w; slot[host[i]][w] = i; slot[vis[i]][w] = i; left.remove(i)
        if not stuck: return week, slot
    return None, None
week, slot = stage1()
if week is None: print('stage 1 failed'); sys.exit(1)
print('stage 1 done', flush=True)

# ---------------------------------------------------------------- cost
def team_cost(t):
    sl = slot[t]; c = 0
    byes = [w for w in W if sl[w] is None]
    if len(byes) != 2: c += 5 * abs(len(byes) - 2)
    else:
        b1, b2 = byes
        if not (4 <= b1 <= 11): c += 2
        if not (12 <= b2 <= 18): c += 2
        if b2 - b1 < 4: c += 2
    run = 0; last = None; prev = None
    for w in W:
        i = sl[w]
        if i is None: continue
        s = host[i] == t
        if s == last: run += 1
        else: run = 1; last = s
        if run > 2: c += 2
        if prev is not None and isdiv[i] and isdiv[prev] and sl[w - 1] == prev and opp(i, t) == opp(prev, t): c += 2
        prev = i
    return c
def fixpen(i): return FIXW if fixw[i] is not None and week[i] != fixw[i] else 0
tc = {t: team_cost(t) for t in teams}; fp = sum(fixpen(i) for i in range(NG)); cost = sum(tc.values()) + fp
print('start cost', cost, flush=True)

def chain(t, w1, w2):
    """Teams whose (w1, w2) games must swap together so everyone keeps one game a week."""
    S = set(); stack = [t]
    while stack:
        x = stack.pop()
        if x in S: continue
        S.add(x)
        for w in (w1, w2):
            i = slot[x][w]
            if i is not None:
                o = opp(i, x)
                if o not in S: stack.append(o)
    return S
def apply_partial(S, w1, w2):
    games = set()
    for x in S:
        for w in (w1, w2):
            i = slot[x][w]
            if i is not None: games.add(i)
    for i in games:
        for t in (host[i], vis[i]): slot[t][week[i]] = None
    for i in games: week[i] = w2 if week[i] == w1 else w1
    for i in games:
        for t in (host[i], vis[i]): slot[t][week[i]] = i
    return games

T = .8; t0 = time.time(); best = (cost, list(week)); it = 0
while time.time() - t0 < budget and cost > 0:
    it += 1
    if rnd.random() < .15:
        w1, w2 = rnd.sample(W, 2); S = set(teams)   # whole-week swap
    else:
        t = rnd.choice(teams); w1, w2 = rnd.sample(W, 2)
        if slot[t][w1] is None and slot[t][w2] is None: continue
        S = chain(t, w1, w2)
        if len(S) > 14: continue
    games = {slot[x][w] for x in S for w in (w1, w2) if slot[x][w] is not None}
    before = sum(tc[x] for x in S) + sum(fixpen(i) for i in games); apply_partial(S, w1, w2)
    after = {x: team_cost(x) for x in S}; d = sum(after.values()) + sum(fixpen(i) for i in games) - before
    if d <= 0 or rnd.random() < math.exp(-d / T):
        tc.update(after); cost += d
        if cost < best[0]: best = (cost, list(week))
    else:
        apply_partial(S, w1, w2)
    if it % 20000 == 0:
        T = max(.06, T * .95); cost = sum(tc.values()) + sum(fixpen(i) for i in range(NG))
        print(it, round(cost, 1), round(best[0], 1), 'T=%.2f' % T, '%.0fs' % (time.time() - t0), flush=True)
        if it % 600000 == 0 and cost > 0: T = .5
cost, week = best
slot = {t: [None] * 21 for t in teams}
for i, w in enumerate(week): slot[host[i]][w] = i; slot[vis[i]][w] = i
tc = {t: team_cost(t) for t in teams}
moved = [(G[i]['id'], fixw[i], week[i]) for i in range(NG) if fixw[i] is not None and week[i] != fixw[i]]
print('cost', cost, 'violations', {t: v for t, v in tc.items() if v}, 'moved fixed', len(moved), moved)
if cost - FIXW * len(moved) == 0:
    # per-seed output so parallel runs do not overwrite each other; copy the chosen one to data/schedule_{yr}.json
    os.makedirs(f'{ROOT}/data/fill_runs', exist_ok=True)
    json.dump(dict(year=yr, seed=seed, moved=moved, games=[dict(g, week=week[i]) for i, g in enumerate(G)]),
              open(f'{ROOT}/data/fill_runs/schedule_{yr}_s{seed}.json', 'w'))
    print('SOLVED per-week games', sorted(collections.Counter(week).items()))
