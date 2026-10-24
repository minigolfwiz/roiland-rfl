"""Series Office save -> the non-conference hand-off the engine reads.

The Series Office keeps one db document per season (series/y2043 ...): {year, games:[{h,v,sub,sid}]}.
Pull a year with ArtifactData (out_dir) and run:
    python3 convert_series_db.py state/series_save/series/y2043.json
-> state/noncon_s<season>_handoff.json  (same shape the Scheduling Office produced), with the
six locked cross-conference rivalries added for that year (host alternates by year offset
from the 2043 hosts in state/series_board.json). Then fill_noncon.py + fix_p6_hosting.py
fill whatever is still open, exactly as before.
"""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
board = json.load(open('/home/claude/cfb2/state/series_board.json'))

def convert(path):
    d = json.load(open(path))
    d = d.get('data', d)
    y = d['year']; Y0 = board['first_year']
    games = []
    for L in board['locked']:
        host = L['host0'] if (y - Y0) % 2 == 0 else (L['b'] if L['host0'] == L['a'] else L['a'])
        vis = L['b'] if host == L['a'] else L['a']
        games.append({'host': host, 'visitor': vis, 'sub': False, 'locked': True, 'auto': False, 'week': L['week']})
    for g in d['games']:
        games.append({'host': g['h'], 'visitor': g['v'], 'sub': bool(g.get('sub')), 'locked': False, 'auto': False, 'week': g.get('week')})
    used = sum(1 if g['sub'] else 2 for g in games)
    out = {'season': y - 2025, 'year': y, 'complete': used == 152 * 3, 'games': games,
           'blocking': 0, 'open_dates': 152 * 3 - used}
    p = '/home/claude/cfb2/state/noncon_s%d_handoff.json' % (y - 2025)
    json.dump(out, open(p, 'w'))
    print(p, len(games), 'games,', out['open_dates'], 'open dates')

if __name__ == '__main__':
    convert(sys.argv[1])
