"""Turn the Conference Office's saved doc (conf/s<N>: [{id, week}]) into the hand-off and
sched files install_hand_schedule.py expects. Ids are positional in conf_board.json:
C<conf index>-<game index> and N<noncon index>."""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import season as SE
SN = SE.load_state().get('season')
P = json.load(open('state/conf_board.json'))
D = json.load(open(sys.argv[1]))
wk = {r['id']: r['week'] for r in D['weeks']}
games = []
for ci, c in enumerate(P['conferences']):
    for i, g in enumerate(c['games']):
        w = wk.get('C%d-%d' % (ci, i), g['week'])
        host = g['host']; vis = g['b'] if host == g['a'] else g['a']
        games.append({'conf': c['conference'], 'host': host, 'visitor': vis, 'week': w, 'locked': bool(g['locked'])})
nc = []
for i, g in enumerate(P['noncon']):
    w = wk.get('N%d' % i, g['week'])
    nc.append({'conf': None, 'host': g['host'], 'visitor': g['visitor'], 'week': w, 'locked': bool(g['locked']), 'sub': bool(g['sub'])})
missing = [g for g in games if g['week'] is None]
print('conference games', len(games), 'unplaced', len(missing), '| noncon', len(nc), 'unplaced', sum(1 for g in nc if g['week'] is None))
allg = games + nc
missing = [g for g in allg if g['week'] is None]
H = {'season': SN, 'year': 2025 + SN, 'complete': not missing, 'games': allg}
json.dump(H, open('state/conf_s%d_handoff.json' % SN, 'w'), indent=1)
print('wrote state/conf_s%d_handoff.json (complete=%s, %d placed of %d)' % (SN, not missing, len(allg) - len(missing), len(allg)))
if not missing:
    json.dump(H, open('state/conf_sched_s%d.json' % SN, 'w'), indent=1); print('and state/conf_sched_s%d.json' % SN)
