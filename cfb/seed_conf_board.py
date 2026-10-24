"""Bake the weeks Dan has already placed (state/conf_s<N>_handoff.json) into
state/conf_board.json and rebuild conf_office.html, so the Office shows his progress
even when the saved-board read fails. Placed games stay unlocked (movable)."""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import season as SE
SN = SE.load_state().get('season')
P = json.load(open('state/conf_board.json'))
H = json.load(open('state/conf_s%d_handoff.json' % SN))
wk = {frozenset((g['host'], g['visitor'])): g['week'] for g in H['games'] if g['week'] is not None}
n = 0
for c in P['conferences']:
    for g in c['games']:
        w = wk.get(frozenset((g['a'], g['b'])))
        if w is not None and g['week'] != w: g['week'] = w; n += 1
for g in P['noncon']:
    w = wk.get(frozenset((g['host'], g['visitor'])))
    if w is not None and g['week'] != w: g['week'] = w; n += 1
json.dump(P, open('state/conf_board.json', 'w'))
placed = sum(1 for c in P['conferences'] for g in c['games'] if g['week'] is not None) + sum(1 for g in P['noncon'] if g['week'] is not None)
tpl = open('conf_office_template.html').read()
open('conf_office.html', 'w').write(tpl.replace('__DATA__', json.dumps(P)))
print('seeded %d weeks (%d placed total of 980); conf_office.html rebuilt' % (n, placed))
