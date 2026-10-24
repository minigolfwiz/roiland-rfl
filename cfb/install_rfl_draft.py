"""Install a draft run in the RFL conversation as this season's college draft (stage 2 of 7).

Dan, 2040-41 offseason: the pro league (RFL) drafts from the college pool in its own tab.
This takes the RFL's 280 picks back and does what draft.py's stage used to do:
    s['draft_s{N}'] = {'picks': [...]}, then draft.mark_departures (seniors leave, drafted
    underclassmen leave, undrafted early entrants mostly return).

    python3 install_rfl_draft.py state/rfl_draft_2041.json            # dry run
    python3 install_rfl_draft.py state/rfl_draft_2041.json --commit
Input: {"season": 15, "picks": [{"overall":1,"round":1,"pick":1,"rfl_team":"...","pid":...}, ...]}
pids must come from state/draft_pool_2041.json; subdivision prospects carry string pids ("SUB_n").
"""
import sys, json, shutil
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, draft as D
H = '/home/claude/cfb2'
src = sys.argv[1]; commit = '--commit' in sys.argv
rfl = json.load(open(src)); s = SE.load_state(); N = s['season']
assert rfl.get('season') == N, 'season mismatch: file %s vs state %s' % (rfl.get('season'), N)
pool = {e['pid']: e for e in json.load(open(H + '/state/draft_pool_%d.json' % (2025 + N + 1)))['pool']}
picks = []; seen = set(); bad = []
for p in rfl['picks']:
    pid = p['pid']
    if pid not in pool or pid in seen: bad.append(pid); continue
    seen.add(pid); e = pool[pid]
    picks.append({'overall': p['overall'], 'round': p['round'], 'pick': p['pick'], 'rfl_team': p.get('rfl_team'),
                  'pid': pid, 'name': e['name'], 'team': e['college'], 'pos': e['pos'], 'cls': e['cls'], 'abil': e['abil'],
                  'prod': e['prod'], 'stock': e['college_scout_stock'], 'base': e['college_draft_grade'],
                  'eligible': True, 'declared': True, 'early': e['early_entrant'], 'subdivision': e['subdivision']})
picks.sort(key=lambda p: p['overall'])
print('%d valid picks (%d rejected: not in pool / duplicate)' % (len(picks), len(bad)), bad[:10])
assert len(picks) == 280, 'expected 280 picks'
assert [p['overall'] for p in picks] == list(range(1, 281)), 'overall numbering must be 1..280'
early = sum(1 for p in picks if p['early']); subs = sum(1 for p in picks if p['subdivision'])
print('early entrants drafted %d | subdivision %d | round-1 colleges: %s' % (early, subs, [p['team'] for p in picks[:40]]))
if commit:
    for f in ('season_state', 'rosters'): shutil.copy(H + '/state/%s.pkl' % f, H + '/state/%s.pkl.pre_s%d_draft' % (f, N + 1))
    # the declared pool as draft.py would have built it, for mark_departures' withdraw logic
    _s, _p, dpool = D.run_draft()
    s['draft_s%d' % N] = {'picks': picks, 'source': 'RFL draft (pro-league conversation)', 'file': src}
    s['draft_size_rule'] = s.get('draft_size_rule') or {}
    SE.save_state(s)
    leaving, withdrew = D.mark_departures(s, picks, dpool)
    print('INSTALLED draft_s%d: %d leaving college, %d drafted, %d withdrew to school' % (N, len(leaving), len(picks), len(withdrew)))
