"""Independent audit of a filled RFL schedule against Dan's rules (separate from the solver's own cost function).
Usage: python3 rfl/audit_schedule.py 2043 data/fill_runs/schedule_2043_s12.json  (or data/schedule_2043.json)"""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import ROOT, load
yr = int(sys.argv[1]); run = load(sys.argv[2]); G = run['games'] if isinstance(run, dict) else run
L = load(f'{ROOT}/data/league.json'); T = L['teams']
fixed = {r['id']: r['week'] for r in load(f'{ROOT}/data/db/rfl/schedule{yr}.json')['weeks']}
M = {g['id']: g for g in load(f'{ROOT}/data/matchups_{yr}.json')}
bad = []
assert len(G) == 360 and {g['id'] for g in G} == set(M)
for g in G:
    m = M[g['id']]; assert (g['host'], g['visitor'], g['kind']) == (m['host'], m['visitor'], m['kind'])
    if g['id'] in fixed and fixed[g['id']] != g['week']: bad.append(('moved fixed', g['id'], fixed[g['id']], g['week']))
by = collections.defaultdict(dict)
for g in G:
    for t in (g['host'], g['visitor']):
        if g['week'] in by[t]: bad.append(('two games in a week', t, g['week']))
        by[t][g['week']] = g
for t in sorted(T):
    wk = by[t]; games = sorted(wk)
    if len(games) != 18: bad.append(('games', t, len(games)))
    byes = [w for w in range(1, 21) if w not in wk]
    if len(byes) != 2: bad.append(('byes', t, byes)); continue
    b1, b2 = byes
    if not 4 <= b1 <= 11: bad.append(('bye1', t, b1))
    if not 12 <= b2 <= 18: bad.append(('bye2', t, b2))
    if b2 - b1 - 1 < 3: bad.append(('byes too close', t, byes))
    run = 0; last = None
    for w in games:                      # byes do not reset the streak
        h = wk[w]['host'] == t
        run = run + 1 if h == last else 1; last = h
        if run > 2: bad.append(('3 in a row', t, 'home' if h else 'road', w))
    kinds = collections.Counter(wk[w]['kind'] for w in games); home = sum(wk[w]['host'] == t for w in games)
    if (kinds['division'], kinds['conference'], kinds['interconference'], home) != (8, 6, 4, 9): bad.append(('format', t, dict(kinds), home))
    opp = {w: (wk[w]['visitor'] if wk[w]['host'] == t else wk[w]['host']) for w in games}
    for w in games:
        if w + 1 in wk and opp[w] == opp[w + 1] and wk[w]['kind'] == 'division': bad.append(('rematch back-to-back', t, opp[w], w))
per = collections.Counter(g['week'] for g in G)
for w in (1, 2, 3, 19, 20):
    if per[w] != 20: bad.append(('week not full', w, per[w]))
print('per-week', dict(sorted(per.items())))
print('PASS' if not bad else 'FAIL'); [print(b) for b in bad]
