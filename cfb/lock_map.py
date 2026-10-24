"""Lock the Map Office placements into the universe (Dan, 2040 postseason).

Reads the page's saved document (state/mapdb/map/v1.json, fetched from the artifact's db) and writes
U['school_coords'], U['city_coords'] and any moved state seeds into state/universe.pkl. Additive: a school
or city not placed in the office keeps whatever it had. state_coords stay the sim's distance basis until
the engine is switched to school-level coordinates. Also writes state/map_placements.json (canon copy).
    python3 lock_map.py            # dry run (items the page has flagged with the Lock button)
    python3 lock_map.py --commit
    python3 lock_map.py --all --commit   # every placed item, ignoring the flags
"""
import sys, json, pickle, shutil, datetime
sys.path.insert(0, '/home/claude/cfb2')
H = '/home/claude/cfb2'
d = json.load(open(H + '/state/mapdb/map/v1.json')); d = d.get('data', d)
with open(H + '/state/universe.pkl', 'rb') as f: U = pickle.load(f)
sc = U.setdefault('school_coords', {}); cc = U.setdefault('city_coords', {})
locks = d.get('locks') or {}          # page flags: 'sc:Name' / 'ci:Name|State' -> true (lock) / false (unlock)
ALL = '--all' in sys.argv              # --all: lock everything placed (the pre-button behaviour)
STATES = set(a for a in sys.argv[1:] if not a.startswith('--'))   # lock_map.py Barhold Tengus --commit: every placed item in those states
want_s = lambda k: ALL or U['schools'][k]['state'] in STATES or k in STATES or locks.get('sc:' + k) is True
NAMES = STATES                          # a bare argument also matches a school or city by name (lock_map.py Gunterburg --commit)
want_c = lambda c: ALL or c['state'] in STATES or c['name'] in NAMES or locks.get('ci:' + c['name'] + '|' + c['state']) is True
new_s = {k: (round(v[0], 2), round(v[1], 2)) for k, v in (d.get('schools') or {}).items() if k in U['schools'] and want_s(k)}
new_c = {c['name'] + '|' + c['state']: {'city': c['name'], 'state': c['state'], 'xy': (round(c['x'], 2), round(c['y'], 2)), 'custom': bool(c.get('custom'))}
         for c in (d.get('cities') or []) if c.get('placed') and want_c(c)}
drop_s, drop_c = [], []   # Dan, 2040: a lock is permanent -- nothing is ever unlocked by this script
moved = {k: tuple(v) for k, v in (d.get('states') or {}).items() if k in U['state_coords'] and tuple(v) != tuple(U['state_coords'][k])}
new_s = {k: v for k, v in new_s.items() if k not in sc}; new_c = {k: v for k, v in new_c.items() if k not in cc}   # locked stays locked, at its locked spot
ch_s = dict(new_s); ch_c = dict(new_c)
print('schools: %d to lock, %d new/changed, %d to unlock; cities: %d to lock, %d new/changed, %d to unlock; state seeds moved: %d' % (len(new_s), len(ch_s), len(drop_s), len(new_c), len(ch_c), len(drop_c), len(moved)))
for k in drop_s: print('   UNLOCK school %s' % k)
for k in drop_c: print('   UNLOCK city   %s' % k)
for k, v in ch_s.items(): print('   school %-22s %s' % (k, v))
for k, v in ch_c.items(): print('   city   %-22s %s' % (v['city'] + ', ' + v['state'], v['xy']))
if '--commit' in sys.argv:
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    shutil.copy(H + '/state/universe.pkl', H + '/state/universe.pkl.pre_maplock_' + stamp)
    sc.update(new_s); cc.update(new_c)
    for k in drop_s: sc.pop(k, None)
    for k in drop_c: cc.pop(k, None)
    for k, v in moved.items(): U['state_coords'][k] = v
    U['map_lock'] = {'when': d.get('saved'), 'schools': len(sc), 'cities': len(cc), 'image': 'state/roiland_map.png (596x596; sim units = pixels)'}
    with open(H + '/state/universe.pkl', 'wb') as f: pickle.dump(U, f)
    json.dump({'saved': d.get('saved'), 'school_coords': sc, 'city_coords': cc, 'state_coords': U['state_coords']}, open(H + '/state/map_placements.json', 'w'), indent=1)
    print('LOCKED: universe.pkl updated (backup .pre_maplock_%s), state/map_placements.json written' % stamp)
