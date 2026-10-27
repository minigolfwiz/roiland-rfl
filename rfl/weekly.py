"""Play one week end to end: run_week → Season page → compressed project state → summary. Usage: python3 rfl/weekly.py N"""
import sys, os, json, subprocess, collections
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
# penalty digest for the weekly write-up (flags are real events; no hidden traits are ever shown)
pens = [(r, x) for r in res for x in r.get('pens', [])]
if pens:
    byteam = collections.Counter(x['team'] for _, x in pens); yds = collections.Counter()
    for _, x in pens: yds[x['team']] += x['yds']
    print(f"flags: {len(pens)} accepted ({len(pens) / (2 * len(res)):.1f} per team-game), {sum(x['yds'] for _, x in pens)} yds | most flagged:", [(t.split()[-1], byteam[t], yds[t]) for t, _ in byteam.most_common(3)])
    pf = [(x['name'], x['pos'], x['team'].split()[-1], x['type'], f"Q{x['q']} {x['t']}" if x['q'] != 'OT' else f"OT {x['t']}") for _, x in pens if x['type'] in ('unnecessary roughness', 'roughing the passer')]
    print('personal fouls:', pf)
    multi = collections.Counter((x['name'], x['pos'], x['team'].split()[-1]) for _, x in pens); print('flagged 3+ times in one game:', [(k, v) for k, v in multi.items() if v >= 3] or 'none')
    led = sorted(((v.get('pen', 0), P[pid]['name'], P[pid]['pos'], (P[pid]['club'] or '').split()[-1]) for pid, v in S['season']['stats'].items() if v.get('pen')), reverse=True)[:5]
    print('season flag leaders:', led)
