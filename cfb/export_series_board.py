"""Payload for the Series Office (Dan, 2026-10-24): non-conference games booked up to ten
seasons ahead, with the pre-drawn conference slates (conf_plan.py) visible beside them.

Everything structural is a lookup: teams/guests/history from state/schedule_board.json
(export_schedule_board.py), conference slates from state/conf_plan.json, locked
cross-conference rivalries from U['fixed_pairs'] with the host alternating each year.
Conference games ship as index tuples [a, b, hostIsA(1/0), week|-1, locked] to keep the
page small.   python3 export_series_board.py -> state/series_board.json
"""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import export_schedule_board as XS

def build(out='/home/claude/cfb2/state/series_board.json'):
    base = XS.build()
    plan = json.load(open('/home/claude/cfb2/state/conf_plan.json'))
    years = sorted(int(y) for y in plan)
    names = [t['name'] for t in base['teams']]
    idx = {n: i for i, n in enumerate(names)}
    teams = []
    for t in base['teams']:
        teams.append({k: t[k] for k in ('name', 'full', 'mascot', 'conf', 'tier', 'prestige',
                      'state', 'xy', 'colors', 'w14_pinned', 'conf_free', 'nc_history',
                      'owed', 'series')})
    conf = {}
    for y in years:
        rows = []
        for c, gs in plan[str(y)]['conferences'].items():
            for g in gs:
                rows.append([idx[g['a']], idx[g['b']], 1 if g['host'] == g['a'] else 0,
                             g['week'] if g.get('week') is not None else -1,
                             1 if g.get('locked') else 0])
        conf[str(y)] = rows
    locked = []
    for L in base['locked']:
        locked.append({'a': L['a'], 'b': L['b'], 'week': L['week'], 'type': L['type'],
                       'host0': L['host'], 'record': L.get('record')})
    payload = {
        'first_year': years[0], 'years': years, 'slots': base['slots'],
        'conferences': base['conferences'], 'teams': teams, 'subs': base['subs'],
        'locked': locked, 'conf': conf, 'w14': base['w14'],
        'return_window': base['return_window'], 'base_year': base['year'],
    }
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload

if __name__ == '__main__':
    p = build()
    import os
    print(len(p['teams']), len(p['subs']), p['years'], os.path.getsize('/home/claude/cfb2/state/series_board.json')//1024, 'KB')
