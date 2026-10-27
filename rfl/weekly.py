"""Play one week end to end: run_week → Season page → compressed project state → summary. Usage: python3 rfl/weekly.py N"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import season as SE
wk = int(sys.argv[1]); path = STATE
S = load(path); res = SE.run_week(S, wk); save(S, path); write_project_state(S, Z64)
subprocess.run(['python3', f'{ROOT}/rfl/build_page.py'], check=True)
for r in res: print(f"{r['slot']:4} {r['away']} {r['away_pts']} @ {r['home']} {r['home_pts']}{' (OT)' if r['ot'] else ''}")
P = S['players']; rows = []
for r in res:
    for side, team in (('H', r['home']), ('A', r['away'])):
        for pid, v in r['stats'][side].items():
            rows.append((v.get('pass_yds', 0), v.get('rush_yds', 0), v.get('rec_yds', 0), v.get('pass_td', 0) + v.get('rush_td', 0) + v.get('rec_td', 0), v.get('ints', 0), P[str(pid)]['name'], P[str(pid)]['pos'], team.split()[-1]))
print('pass', sorted(rows, key=lambda x: -x[0])[:3]); print('rush', sorted(rows, key=lambda x: -x[1])[:3]); print('rec', sorted(rows, key=lambda x: -x[2])[:3])
print('inj 3+:', [(i['team'].split()[-1], i['name'], i['pos'], i['weeks'], i['kind']) for r in res for i in r['injuries'] if i['weeks'] >= 3])
rec = S['season']['records']; print('unbeaten:', [t.split()[-1] for t in rec if rec[t]['l'] == 0 and rec[t]['t'] == 0], 'winless:', [t.split()[-1] for t in rec if rec[t]['w'] == 0 and rec[t]['t'] == 0])
