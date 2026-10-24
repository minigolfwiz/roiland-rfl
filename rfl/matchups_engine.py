"""RFL opponent rotation (anchored on 2041 = year 0, repeats every 5 years). TEAMS order = the order Dan listed them (league.json divisions)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import ROOT, load
L = load(f'{ROOT}/data/league.json')
DIVS = ["North", "West", "South", "East"]; CONFS = ["Regal", "Majestic"]
def div(conf, d): return next(x['roster'] for x in L['divisions'] if x['conf'] == conf and x['div'] == d)
def games_for(year):
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
if __name__ == '__main__':
    yr = int(sys.argv[1]); gs = games_for(yr); json.dump(gs, open(f'{ROOT}/data/matchups_{yr}.json', 'w')); print(len(gs))
