"""Roiland Football League engine core (rebuilt Oct 2026).
Players and clubs are plain dicts so the whole state round-trips through JSON.

Player: pid, name, pos, born, college, conf, tier, abil (1-10 current), pot (ceiling), dur (0-1 durability),
        arch, attrs {k: 1-10}, club, status (active/retired/out), contract {salary, years, left, signed, kind},
        draft {year, round, pick, club}, career [[year, club, year]...], honors [[year, award]...], real (from the college sim)
Club:   name, conf, div, roster [pid...], gm {name, eye, discipline, aggression, bias}, coach {name, skill}, picks {year: [[round, orig_club]...]}
"""
import json, math, random, hashlib, os
from rfl import discipline as _disc
ROOT =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Current season year: data/current_year.txt (one number). State files are year-named so a new season never overwrites the old one.
YEAR = int(open(f'{ROOT}/data/current_year.txt').read().strip()) if os.path.exists(f'{ROOT}/data/current_year.txt') else 2042
STATE = f'{ROOT}/data/state_{YEAR}.json'; Z64 = f'{ROOT}/data/rfl_state_{YEAR}.z64'
R = random.Random(2042)
POS = ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'CB', 'S', 'K', 'P']
ATTR = {'QB': ['acc', 'arm', 'mob'], 'RB': ['run', 'spd', 'hands'], 'WR': ['hands', 'spd', 'route'], 'TE': ['hands', 'spd', 'route', 'blk'],
        'OL': ['pblk', 'rblk'], 'DL': ['rush', 'rdef'], 'LB': ['tkl', 'cov', 'rush'], 'CB': ['cov', 'tkl', 'ball'], 'S': ['cov', 'tkl', 'ball'],
        'K': ['leg', 'accy'], 'P': ['leg', 'ctl']}
ARCHS = {'QB': ['Pocket Passer', 'Gunslinger', 'Dual-Threat', 'Game Manager'], 'RB': ['Power Back', 'Speed Back', 'All-Purpose', 'Short-Yardage Bruiser'],
         'WR': ['Deep Threat', 'Possession', 'Slot Technician', 'Contested-Catch'], 'TE': ['Receiving TE', 'Blocking TE', 'Hybrid'],
         'OL': ['Pass Protector', 'Run Mauler', 'Balanced'], 'DL': ['Edge Rusher', 'Interior Penetrator', 'Run Stuffer'],
         'LB': ['Blitzer', 'Coverage LB', 'Run-Stopping LB'], 'CB': ['Press', 'Ball-Hawk', 'Shutdown'], 'S': ['Box Safety', 'Center Fielder', 'Hybrid Safety'],
         'K': ['Accurate', 'Big Leg'], 'P': ['Big Leg', 'Directional']}
# archetype lean: which attrs run above the player's overall
LEAN = {'Pocket Passer': {'acc': .5, 'mob': -1.5}, 'Gunslinger': {'arm': 1.0, 'acc': -.6, 'mob': -1.0}, 'Dual-Threat': {'mob': 1.6, 'arm': -.3}, 'Game Manager': {'acc': .9, 'arm': -.6, 'mob': -1.2},
        'Power Back': {'run': .6, 'spd': -.8}, 'Speed Back': {'spd': 1.2, 'run': -.5}, 'All-Purpose': {'hands': .6}, 'Short-Yardage Bruiser': {'run': .9, 'spd': -1.8, 'hands': -.6},
        'Deep Threat': {'spd': 1.0, 'hands': -.5}, 'Possession': {'hands': .9, 'spd': -.6}, 'Slot Technician': {'route': .8, 'spd': -.3}, 'Contested-Catch': {'hands': .6, 'spd': -.6},
        'Receiving TE': {'route': .5, 'blk': -1.0}, 'Blocking TE': {'blk': .9, 'spd': -.8, 'route': -.5}, 'Hybrid': {},
        'Pass Protector': {'pblk': .5, 'rblk': -.4}, 'Run Mauler': {'rblk': .6, 'pblk': -.4}, 'Balanced': {},
        'Edge Rusher': {'rush': .6, 'rdef': -.8}, 'Interior Penetrator': {'rush': .3, 'rdef': -.3}, 'Run Stuffer': {'rdef': .6, 'rush': -.8},
        'Blitzer': {'rush': .7, 'cov': -.8}, 'Coverage LB': {'cov': .8, 'rush': -.8}, 'Run-Stopping LB': {'tkl': .6, 'cov': -.6},
        'Press': {'cov': .3, 'ball': -.3}, 'Ball-Hawk': {'ball': .8, 'tkl': -.6}, 'Shutdown': {'cov': .7, 'tkl': -.5},
        'Box Safety': {'tkl': .7, 'cov': -.7}, 'Center Fielder': {'ball': .6, 'cov': .3, 'tkl': -.8}, 'Hybrid Safety': {},
        'Accurate': {'accy': .6, 'leg': -.6}, 'Big Leg': {'leg': .8, 'accy': -.6, 'ctl': -.5}, 'Directional': {'ctl': .7, 'leg': -.6}}
# roster targets (count, starters)
DEPTH = {'QB': (3, 1), 'RB': (4, 1), 'WR': (6, 3), 'TE': (3, 1), 'OL': (9, 5), 'DL': (8, 4), 'LB': (7, 3), 'CB': (6, 2), 'S': (4, 2), 'K': (1, 1), 'P': (1, 1)}
ROSTER_MAX = 53
FIRST = ['Aiyana', 'Akira', 'Alejandro', 'Amara', 'Anders', 'Annika', 'Arjun', 'Bartholomew', 'Beatrix', 'Bo', 'Caden', 'Chiara', 'Dmitri', 'Elin', 'Emeka', 'Esteban', 'Fatima', 'Gael', 'Hana', 'Idris', 'Ines', 'Jaxon', 'Kaelan', 'Lior', 'Mateo', 'Nadia', 'Oren', 'Priya', 'Quill', 'Rafael', 'Saoirse', 'Tobias', 'Uma', 'Vikram', 'Wren', 'Xiomara', 'Yusuf', 'Zara', 'Halvard', 'Imogen', 'Kofi', 'Leilani', 'Marcelo', 'Nikolai', 'Odessa', 'Petra', 'Ronan', 'Sade', 'Tiberius', 'Vesna']
LAST = ['Ashgrove', 'Brightwater', 'Calderwood', 'Dunmore', 'Eastlake', 'Fairweather', 'Greystone', 'Hollowell', 'Ironside', 'Juniper', 'Kestrel', 'Longfield', 'Marrow', 'Nightingale', 'Oakhurst', 'Pemberly', 'Quarrie', 'Ravenscroft', 'Stillwater', 'Thorncastle', 'Underhill', 'Vance', 'Wexley', 'Yarrow', 'Zephyrine', 'Blackwood', 'Copperfield', 'Dellacroix', 'Fenwick', 'Galloway', 'Hartwell', 'Islington', 'Kingsley', 'Lockwood', 'Mortlake', 'Northway', 'Osterhout', 'Pendragon', 'Redfern', 'Sheffield']

def age(p, year): return year - p['born']
def sha(s): return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
def gen_attrs(pos, abil, arch, rnd):
    out = {}
    for k in ATTR[pos]:
        v = abil + LEAN.get(arch, {}).get(k, 0) + rnd.gauss(0, .45)
        out[k] = round(max(1.0, min(10.0, v)), 2)
    return out
def parse_attrs(s):
    """'pblk 9.0 rblk 9.8' → dict"""
    if not s: return None
    if isinstance(s, dict): return s
    t = s.split(); return {t[i]: float(t[i + 1]) for i in range(0, len(t) - 1, 2)}
def ovr(p):
    """Overall used for depth charts: ability blended with the attrs that matter for the position."""
    a = p.get('attrs') or {}
    if not a: return p['abil']
    return round(.6 * p['abil'] + .4 * sum(a.values()) / len(a), 2)

# ---------------------------------------------------------------- economy
CAP = {2040: 290521019, 2041: 304466028, 2042: 309506118}
def cap_for(year):
    if year in CAP: return CAP[year]
    rnd = random.Random(year * 7919); CAP[year] = int(cap_for(year - 1) * (1 + rnd.gauss(.048, .02))); return CAP[year]
BASIS = dict(QB=.060, OL=.034, DL=.034, WR=.034, CB=.032, LB=.027, S=.026, RB=.026, TE=.026, K=.008, P=.007)
def raw_value(p, year):
    a = age(p, year); v = BASIS[p['pos']] * math.exp(1.5 * (p['abil'] - 7.5))
    if a >= 30: v *= max(.45, 1 - .11 * (a - 29))
    if a <= 25: v *= 1 + .08 * max(0, p['pot'] - p['abil'])
    return v
SCALE = {2042: 1.05}
def market_value(p, year):
    cap = cap_for(year); k = SCALE.get(year, 1.0)
    return max(.004 * cap, min(.18 * cap, cap * k * raw_value(p, year)))
def rookie_salary(year, overall):
    cap = cap_for(year)
    if overall <= 32: return cap * (.045 * (.006 / .045) ** ((overall - 1) / 31))
    return cap * (.0048 if overall <= 100 else .0042)
def payroll(S, t): return sum((S['players'][str(pid)]['contract'] or {}).get('salary', 0) for pid in S['clubs'][t]['roster'])

# ---------------------------------------------------------------- staff profiles (deterministic from name)
def gm_profile(name):
    rnd = random.Random(sha(name))
    return dict(name=name, eye=round(rnd.uniform(.35, .9), 3), discipline=round(rnd.uniform(.3, .9), 3), aggression=round(rnd.uniform(.2, .8), 3), bias=rnd.sample(POS[:9], 2))
def coach_profile(name):
    rnd = random.Random(sha(name) ^ 0xC0AC)
    return dict(name=name, skill=round(rnd.gauss(0, .08), 3), style=rnd.choice(['balanced', 'pass-first', 'run-first', 'aggressive', 'conservative']), disc=_disc.gen_coach_disc(name))

# ---------------------------------------------------------------- state io
def load(path): return json.load(open(path))
def save(S, path):
    json.dump(S, open(path, 'w'), separators=(',', ':'))
def new_pid(S):
    S['next_pid'] = S.get('next_pid', 9100000) + 1; return S['next_pid']
def gen_player(S, pos, year, abil, rnd, club=None, age_=None):
    arch = rnd.choice(ARCHS[pos]); a = age_ or rnd.randint(24, 31)
    name = f"{rnd.choice(FIRST)} {rnd.choice(LAST)}"
    while any(q['name'] == name for q in S['players'].values()): name = f"{rnd.choice(FIRST)} {rnd.choice(LAST)}-{rnd.choice(LAST)[:4]}"
    pid = new_pid(S)
    p = dict(pid=pid, name=name, pos=pos, born=year - a, college=None, conf=None, tier=None, abil=round(abil, 2), pot=round(max(abil, abil + rnd.uniform(0, .6)), 2),
             dur=round(rnd.uniform(.4, .9), 2), arch=arch, attrs=gen_attrs(pos, abil, arch, rnd), club=club, status='active', real=False, invented=True,
             contract=dict(salary=int(.004 * cap_for(year)), years=1, left=1, signed=year, kind='street'), draft=None, career=[[year, club, year]] if club else [], honors=[])
    p.update(_disc.gen_traits(name, year - a, year))     # hidden discipline traits (Dan, 27 Oct 2026)
    S['players'][str(pid)] = p; return p
def depth_chart(S, t):
    """pos → players sorted best first (active, healthy)."""
    out = {pos: [] for pos in POS}
    for pid in S['clubs'][t]['roster']:
        p = S['players'][str(pid)]
        if p.get('inj'): continue
        out[p['pos']].append(p)
    for pos in out: out[pos].sort(key=lambda p: -(ovr(p) + p.get('form', 0)))
    return out
def strength(S, t):
    """Weighted starter quality, 0-10."""
    dc = depth_chart(S, t); W = dict(QB=3.0, OL=2.0, WR=1.6, DL=1.8, CB=1.3, LB=1.2, S=.9, RB=1.0, TE=.7, K=.3, P=.2)
    tot = 0; wsum = 0
    for pos, (n, st) in DEPTH.items():
        ps = dc[pos][:st]; v = (sum(ovr(p) for p in ps) + 4.5 * (st - len(ps))) / st
        tot += W[pos] * v; wsum += W[pos]
    return round(tot / wsum, 3)

# ---------------------------------------------------------------- compact save for the project (2 MB cap) and exact restore
_PDEF = {'tier': None, 'status': 'active', 'honors': [], 'rings': [], 'tag': None, 'inj': None, 'form': 0, 'starter': False}
def compact_state(S):
    """Players as a list with default-valued fields dropped; everything else kept. expand_state() reverses it exactly."""
    out = {k: v for k, v in S.items() if k != 'players'}
    out['players'] = [{k: v for k, v in p.items() if not (k in _PDEF and v == _PDEF[k])} for p in S['players'].values()]
    return out
def expand_state(C):
    S = {k: v for k, v in C.items() if k != 'players'}
    S['players'] = {str(p['pid']): {**{k: (list(v) if isinstance(v, list) else v) for k, v in _PDEF.items() if k not in ('inj', 'form', 'starter')}, **p} for p in C['players']}
    return S
HEADER = 'RFL state — zlib-compressed, base64 JSON of engine.compact_state(S). Restore: engine.read_project_state(path) → full state dict.\n'
def write_project_state(S, path):
    import zlib, base64
    s = json.dumps(compact_state(S), separators=(',', ':')).encode()
    open(path, 'w').write(HEADER + base64.b64encode(zlib.compress(s, 9)).decode())
def read_project_state(path):
    import zlib, base64
    txt = open(path).read(); b64 = txt.split('\n', 1)[1].strip()
    return expand_state(json.loads(zlib.decompress(base64.b64decode(b64))))
