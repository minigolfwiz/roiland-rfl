"""Install a filled schedule and the Broadcast/Primetime Desk picks into a new season.
Usage: python3 rfl/install_schedule.py 2043 data/fill_runs/schedule_2043_s11.json
Reads the chosen fill run, the desk picks (data/rfl_primetime_<yr>.json: prime[] with slot thu/snf/mnf and pins[]),
writes data/schedule_<yr>.json (games with week+slot), data/rfl_broadcast_slots_<yr>.json (2042 shape),
data/db/rfl/schedule<yr>_filled.json (Office db doc shape), and starts the season in the state:
state_<yr>.json is created from state_<yr-1>.json (the offseason already ran there) and the compressed copy is written."""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import ROOT, load, save, write_project_state
from rfl import season as SE
yr = int(sys.argv[1]); run = load(sys.argv[2]); G = run['games']
desk = load(f'{ROOT}/data/rfl_primetime_{yr}.json')
prime = {p['id']: p for p in desk['prime']}; pins = {p['id']: p for p in desk['pins']}
# slots: desk slot names are thu / snf / mnf; week 20 has two Sunday nights -> the second is 'snf2' (2042 convention)
slot_of = {}; snf_seen = collections.Counter()
for g in G:
    p = prime.get(g['id'])
    if p is None: slot_of[g['id']] = 'sun'; continue
    assert p['week'] == g['week'], f"primetime game {g['id']} moved: desk wk {p['week']} -> {g['week']}"
    s = p['slot']
    if s == 'snf':
        snf_seen[g['week']] += 1
        if snf_seen[g['week']] == 2: s = 'snf2'
    slot_of[g['id']] = s
for pid, p in pins.items():
    w = next(g['week'] for g in G if g['id'] == pid)
    if w != p['week']: print(f"NOTE pinned game {pid} ({p['visitor']} at {p['host']}) moved from week {p['week']} to {w}")
sched = [dict(id=g['id'], host=g['host'], visitor=g['visitor'], kind=g['kind'], week=g['week'], slot=slot_of[g['id']]) for g in G]
sched.sort(key=lambda g: (g['week'], {'thu': 0, 'sun': 1, 'snf': 2, 'snf2': 3, 'mnf': 4}[g['slot']], g['id']))
json.dump(sched, open(f'{ROOT}/data/schedule_{yr}.json', 'w'))
json.dump(dict(year=yr, weeks=[dict(id=g['id'], week=g['week']) for g in sched], saved=f'filled by Claude (seed {run["seed"]})'), open(f'{ROOT}/data/db/rfl/schedule{yr}_filled.json', 'w'))
slots = {}
for g in sched:
    if g['slot'] == 'sun': continue
    slots.setdefault(str(g['week']), {})[g['slot']] = f"{g['visitor']} at {g['host']}"
json.dump(dict(year=yr, note=f'Dan\'s TNF/SNF/MNF picks for {yr} from the Primetime Desk; week 20 has two SNF and no MNF', slots=slots), open(f'{ROOT}/data/rfl_broadcast_slots_{yr}.json', 'w'), indent=1)
# season state
prev = f'{ROOT}/data/state_{yr - 1}.json'; cur = f'{ROOT}/data/state_{yr}.json'
if not os.path.exists(cur):
    S = load(prev); assert S['season']['year'] == yr - 1 and S['season']['week_done'] >= 20, 'previous season not finished'
    assert 'draft' in S.get('offseason', {}).get('done', []), 'offseason draft not done'
    S[f'season_{yr - 1}_closed'] = True
    SE.init_season(S, yr, sched); S.pop('offseason', None)
    save(S, cur); write_project_state(S, f'{ROOT}/data/rfl_state_{yr}.z64'); print('season started', yr, 'state', cur)
else:
    print('state already exists; schedule files rewritten only')
print('games', len(sched), 'per week', sorted(collections.Counter(g['week'] for g in sched).items()))
print('slots', {w: sorted(v) for w, v in slots.items()})
