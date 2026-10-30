"""RFL opponent rotation (anchored on 2041 = year 0, repeats every 5 years). TEAMS order = the order Dan listed them (league.json divisions)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import ROOT, load
L = load(f'{ROOT}/data/league.json')
DIVS = ["North", "West", "South", "East"]; CONFS = ["Regal", "Majestic"]
def div(conf, d): return next(x['roster'] for x in L['divisions'] if x['conf'] == conf and x['div'] == d)
NFL_STYLE_FROM = 2046   # first season scheduled with last year's standings (Dan, 30 Oct 2026)
def games_for(year, S=None, new=None):
    """2041-2045: pure 5-year rotation. 2046 on: 8 division games; per other division in the conference one same-place game and one
    rotation game (bumped to the nearest legal opponent if it would repeat the same-place opponent); per other-conference division one
    game against a place that is not your own (4x4 Latin grid of place shifts, shifted each year). Home/away: an Euler orientation of the
    non-division games, so every club is 5 home / 5 away outside the division (9/9 overall)."""
    if new is None: new = year >= NFL_STYLE_FROM
    if new: return games_standings(year, S)
    y = year - 2041; out = []
    add = lambda host, vis, kind: out.append({"host": host, "visitor": vis, "kind": kind})
    for c in CONFS:
        for d in DIVS:
            T = div(c, d)
            for i in range(5):
                for j in range(5):
                    if i != j: add(T[i], T[j], "division")
        pairs = [(a, b) for k, a in enumerate(DIVS) for b in DIVS[k + 1:]]
        for p, (d1, d2) in enumerate(pairs):
            A, B = div(c, d1), div(c, d2); a = (y + p) % 5
            for i in range(5):
                add(A[i], B[(i + a) % 5], "conference"); add(B[(i + a + 1) % 5], A[i], "conference")
    for r, dr in enumerate(DIVS):
        for m, dm in enumerate(DIVS):
            R, M = div("Regal", dr), div("Majestic", dm); b = (y + r + 2 * m) % 5; regal_home = (r + m + y) % 2 == 0
            for i in range(5):
                x, z = R[i], M[(i + b) % 5]; add(*((x, z) if regal_home else (z, x)), "interconference")
    for i, g in enumerate(out): g['id'] = f'G{i}'
    return out
def games_standings(year, S=None):
    import itertools, collections, random
    from rfl import season as SE
    if S is None:
        S = load(f'{ROOT}/data/state_{year - 1}.json')
        assert S['season']['year'] == year - 1 and S['season'].get('week_done', 0) >= 20, f'{year - 1} regular season not finished'
    st = SE.standings(S); y = year - 2041; out = []
    add = lambda host, vis, kind: out.append({"host": host, "visitor": vis, "kind": kind})
    place = {t: i for c in CONFS for d in DIVS for i, t in enumerate(st[c][d])}
    for c in CONFS:
        for d in DIVS:
            T = div(c, d)
            for i in range(5):
                for j in range(5):
                    if i != j: add(T[i], T[j], "division")
    edges = []
    for c in CONFS:
        pairs = [(a, b) for k, a in enumerate(DIVS) for b in DIVS[k + 1:]]
        for p, (d1, d2) in enumerate(pairs):
            A, B = div(c, d1), div(c, d2); a = (y + p) % 5
            for i in range(5): edges.append((st[c][d1][i], st[c][d2][i], "conference"))        # same place
            base = [(i + a) % 5 for i in range(5)]; best = None
            for perm in itertools.permutations(range(5)):
                if any(place[A[i]] == place[B[perm[i]]] for i in range(5)): continue
                cost = sum(perm[i] != base[i] for i in range(5))
                if best is None or cost < best[0]: best = (cost, perm)
            for i in range(5): edges.append((A[i], B[best[1][i]], "conference"))                # rotation
    for r, dr in enumerate(DIVS):
        for m, dm in enumerate(DIVS):
            k = (r + m + y) % 4 + 1
            for p in range(5): edges.append((st["Regal"][dr][p], st["Majestic"][dm][(p + k) % 5], "interconference"))
    adj = collections.defaultdict(list)
    for n, (a, b, k) in enumerate(edges): adj[a].append((n, b)); adj[b].append((n, a))
    # every club has 10 non-division games (even degree), so walking closed trails gives exactly 5 home and 5 away
    return _finish(out, edges, adj, year)
def _finish(out, edges, adj, year):
    import collections, random
    used = [False] * len(edges); orient = {}; rnd = random.Random(year * 7)
    ptr = collections.defaultdict(list)
    for v in adj: ptr[v] = list(adj[v]); rnd.shuffle(ptr[v])
    for s0 in sorted(adj, key=lambda v: rnd.random()):
        while True:
            while ptr[s0] and used[ptr[s0][-1][0]]: ptr[s0].pop()
            if not ptr[s0]: break
            v = s0
            while True:
                while ptr[v] and used[ptr[v][-1][0]]: ptr[v].pop()
                if not ptr[v]: break
                n, w = ptr[v].pop(); used[n] = True; orient[n] = (w, v)   # trail leaves v, arrives at w: w hosts v
                v = w
    for n, (a, b, k) in enumerate(edges):
        host, vis = orient[n]; out.append({"host": host, "visitor": vis, "kind": k})
    for i, g in enumerate(out): g['id'] = f'G{i}'
    return out
if __name__ == '__main__':
    yr = int(sys.argv[1]); gs = games_for(yr); json.dump(gs, open(f'{ROOT}/data/matchups_{yr}.json', 'w')); print(len(gs))
