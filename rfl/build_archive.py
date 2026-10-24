"""Rebuild the RFL Archive page with the 2042 season and the 2043 offseason so far.
Usage: python3 rfl/build_archive.py <index.html in> <archive_bios.json in> <outdir>
Reads the live Archive page (data block D + biography file), adds: seasons[2042], 2042 awards, all-time totals, trade/conduct news,
front-office changes (2042 results, then the 2043 moves), the 2043 pre-draft club cards, and refreshes player biographies from the state."""
import json, sys, os, random, re, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *

src, biosrc, out = sys.argv[1:4]
html = open(src).read(); BIOS = json.load(open(biosrc))
i = html.index('const D = ') + 10; D, end = json.JSONDecoder().raw_decode(html[i:]); tail = html[i + end:]
S = load(f'{ROOT}/data/state_2042.json'); H = json.load(open(f'{ROOT}/data/rfl_history_1951_2040.json'))
se = S['season']; PO = se['playoffs']; Y = 2042; CAP43 = cap_for(2043)
rnd = random.Random(2043004)
assert '2042' not in D['seasons']

# ---------------------------------------------------------------- coach / GM lookup
coaches, gms = D['coaches'], D['gms']
cby = {c['name']: c for c in coaches}; gby = {g['name']: g for g in gms}
def open_stint(person, role=None):
    for s in reversed(person['stints']):
        if s['end'] is None and (role is None or s['role'] == role): return s
    return None
def incumbent(club, role):
    for p in (gms if role == 'GM' else coaches):
        s = open_stint(p, role)
        if s and s['club'] == club: return p
champ = PO['champion']; confs = {r['conf']: r['winner'] for r in PO['rounds']['conference']}
coy = se['awards']['Coach of the Year']['finalists'][0]
in_po = {t for c in PO['seeds'].values() for t in c}
# ---------------------------------------------------------------- 2042 results onto the incumbents
for t, v in se['records'].items():
    for role in ('HC', 'GM'):
        p = incumbent(t, role); assert p, (t, role)
        s = open_stint(p, role); r = s['rec']
        s['rec'] = [r[0] + v['w'], r[1] + v['l'], r[2] + v['t'], r[3] + (t in in_po), r[4] + ([Y] if t == champ else [])]
        key = 'hc' if role == 'HC' else 'hc'
        p['hc'] = [p['hc'][0] + v['w'], p['hc'][1] + v['l'], p['hc'][2] + v['t']]
        p['po'] += int(t in in_po)
        if t == champ: p['titles'].append(Y)
        if role == 'HC':
            if t in confs.values(): p.setdefault('ct', []).append(Y)
            if p['name'] == coy['name']: p['coy'].append(Y)
        elif t in confs.values(): p.setdefault('ct', []).append(Y)
# ---------------------------------------------------------------- the 2043 front-office moves
nid = dict(c=max(c['id'] for c in coaches) + 1, g=max(g['id'] for g in gms) + 1)
first = sorted({c['name'].split(' ')[0] for c in coaches}); last = sorted({c['name'].split(' ', 1)[1] for c in coaches if ' ' in c['name']})
used = set(cby) | set(gby)
def newname():
    while True:
        n = f"{rnd.choice(first)} {rnd.choice(last)}"
        if n not in used: used.add(n); return n
def mk_person(kind, club, role):
    n = newname()
    if kind == 'c':
        p = dict(id=nid['c'], name=n, born=rnd.randint(1984, 2002), status='active', stints=[], hc=[0, 0, 0], po=0, titles=[], ct=[], coy=[], fired=0); nid['c'] += 1; coaches.append(p); cby[n] = p
        BIOS['coaches'][str(p['id'])] = dict(kind='coach', retired=None, origin='position coach', **{k: p[k] for k in p if k != 'id'}); bio = BIOS['coaches'][str(p['id'])]
    else:
        p = dict(id=nid['g'], name=n, born=rnd.randint(1986, 2004), status='active', origin='scout', stints=[], hc=[0, 0, 0], po=0, titles=[], ct=[], coy=[], fired=0); nid['g'] += 1; gms.append(p); gby[n] = p
        BIOS['gms'][str(p['id'])] = dict(kind='gm', name=n, born=p['born'], status='active', origin='scout', stints=p['stints'], rec=[0, 0, 0], po=0, titles=[], fired=0)
    p['stints'].append(dict(club=club, role=role, start=2043, end=None, how=None, rec=None)); return p
moves = S['offseason']['staff']['moves']; cond = S['offseason']['staff']['conduct']
backfill = []
for m in moves:
    club, rest = m.split(': ', 1); new, rest = rest.split(' replaces ', 1); old, what = rest.rsplit(' as ', 1)
    role = 'GM' if 'general' in what else 'HC'; people = gby if role == 'GM' else cby
    o = people[old]; s = open_stint(o, role); assert s and s['club'] == club, (m, s)
    c = next((x for x in cond if old in x), None)
    how = 'retired' if c and 'retires' in c else ('resigned' if c else 'fired')
    s['end'] = 2042; s['how'] = how
    if how == 'retired': o['status'] = 'retired'; o['retired'] = 2042
    if how == 'fired': o['fired'] += 1
    n = people[new]; ns = open_stint(n)
    if ns: ns['end'] = 2042; ns['how'] = f"hired as {role} by {club}"; backfill.append((ns['club'], ns['role'], role == 'GM'))
    else: print('hired from outside the league:', new, '->', club)
    n['stints'].append(dict(club=club, role=role, start=2043, end=None, how=None, rec=[0, 0, 0, 0, []]))
for club, vrole, isgm in backfill:
    pool = [] if isgm else [c for c in coaches if c['status'] == 'active' and open_stint(c) is None and c['born'] >= 1965 and c['stints'] and (c['stints'][-1]['end'] or 0) >= 2038 and c['stints'][-1]['club'] != club and c['id'] < 470]
    if pool and rnd.random() < .6:
        p = rnd.choice(pool); p['stints'].append(dict(club=club, role=vrole, start=2043, end=None, how=None, rec=None))
    else: mk_person('g' if isgm else 'c', club, vrole)
# biography copies of every staff member (the bios file mirrors these lists)
for p in coaches: BIOS['coaches'][str(p['id'])] = dict(kind='coach', origin=BIOS['coaches'].get(str(p['id']), {}).get('origin', 'position coach'), retired=p.get('retired'), **{k: v for k, v in p.items() if k not in ('id', 'retired')})
for p in gms: BIOS['gms'][str(p['id'])] = dict(kind='gm', retired=p.get('retired'), **{k: v for k, v in p.items() if k not in ('id', 'retired', 'hc', 'ct', 'coy')}, rec=p['hc'])

# ---------------------------------------------------------------- 2042 season block
def seedmap(conf): return {t: i + 1 for i, t in enumerate(PO['seeds'][conf])}
pol = []
for k in ('first', 'second', 'conference'):
    for g in PO['rounds'][k]:
        pol.append(dict(year=Y, conf=g['conf'], stage={'first': 'First round', 'second': 'Second round', 'conference': 'Conference championship'}[k], home=g['home'], away=g['away'], winner=g['winner'],
                        home_pts=g['home_pts'], away_pts=g['away_pts'], home_seed=g['home_seed'], away_seed=g['away_seed'], ot=g['ot']))
mb = PO['rounds']['megabowl'][0]; site = PO['site']
pol.append(dict(year=Y, conf='Mega Bowl', stage='Mega Bowl', home=mb['home'], away=mb['away'], winner=mb['winner'], home_pts=mb['home_pts'], away_pts=mb['away_pts'],
                home_seed='R' if mb['home'] == confs['Regal'] else 'M', away_seed='R' if mb['away'] == confs['Regal'] else 'M',
                site=dict(city=site['city'], state=site['state'], stadium=site['stadium'], host=site['host']), ot=mb['ot']))
from rfl import season as SE
stand = SE.standings(S)
win = {c: {d: stand[c][d][0] for d in stand[c]} for c in stand}
aw = {}
for k in D['awards']['order'][:4]:
    f = se['awards'][k]['finalists'][0]; aw[k] = dict(pid=f['pid'], name=f['name'], pos=f['pos'], club=f['club'])
cp = cby[coy['name']]; aw['Coach of the Year'] = dict(pid=f"c{cp['id']}", name=coy['name'], pos=None, club=coy['club'])
aw['Mega Bowl MVP'] = dict(pid=PO['mvp']['pid'], name=PO['mvp']['name'], pos=PO['mvp']['pos'], club=PO['mvp']['club'])
notable = []
for r in S['offseason']['retired']:
    p = S['players'][str(r['pid'])]
    if ovr(p) >= 8.0 or p.get('honors') or r['age'] >= 35: notable.append(dict(pid=r['pid'], name=r['name'], pos=r['pos'], age=r['age']))
prev = D['seasons']['2041']
D['seasons']['2042'] = dict(al=prev['al'], res={t: [v['w'], v['l'], v['t']] for t, v in se['records'].items()}, order=[], win=win, seeds=PO['seeds'], po=pol, champ=champ,
                            cc={'Regal': confs['Regal'], 'Majestic': confs['Majestic']}, aw=aw, site=dict(city=site['city'], state=site['state'], stadium=site['stadium'], host=site['host']),
                            G=18, cap=cap_for(2042), draft=[], dy=None, ret=notable)
for k in D['awards']['order']:
    v = aw[k]; D['awards']['byyear'][k].append(dict(y=Y, name=v['name'], pos=v['pos'], club=v['club'], pid=v['pid']))
D['allt'] = {t: {k: c[k] for k in ('joined', 'titles', 'ct', 'w', 'l', 't', 'po', 'dt')} for t, c in H['clubs'].items()}
# ---------------------------------------------------------------- news: trades and conduct
P = S['players']; byname = {p['name']: p for p in P.values()}
def trade_entries(lines, year):
    out = []
    for ln in lines:
        m = re.match(r'(.+?) trade (.+?) \((\w+), [\d.]+\) to (.+?) for a ', ln)
        if m: out.append(dict(year=year, kind='trade', text=ln, club=m.group(4), other=m.group(1), pid=byname[m.group(2)]['pid'] if m.group(2) in byname else None))
    return out
D['tx'] += trade_entries(H['offseason_2042']['transactions'], 2041)
D['tx'] += trade_entries(S['offseason']['trades'], Y)
for c in cond:
    club = c.split(' head coach')[0].split(' general manager')[0]
    D['tx'].append(dict(year=Y, kind='conduct', club=club, text=c))
# ---------------------------------------------------------------- club cards for the 2043 draft
stt = {}
for t, c in S['clubs'].items():
    ps = [P[str(i)] for i in c['roster']]; pay = payroll(S, t)
    rook = sorted([p for p in ps if p.get('draft') and p['draft']['year'] == 2042], key=lambda p: p['draft']['pick'])[:3]
    top = sorted(ps, key=lambda p: -p['abil'])[:5]
    stt[t] = dict(room=CAP43 - pay, payroll=pay, cap=CAP43, picks=c['picks']['2043'], n=len(ps), gm=c['gm']['name'], coach=c['coach']['name'],
                  rookies=[dict(pid=p['pid'], name=p['name'], pos=p['pos'], pick=p['draft']['pick']) for p in rook],
                  top=[dict(pid=p['pid'], name=p['name'], pos=p['pos'], abil=p['abil'], age=2043 - p['born']) for p in top])
D['state'] = stt
# ---------------------------------------------------------------- biographies refreshed from the state
byear = {}
for k, lst in D['awards']['byyear'].items():
    for w in lst:
        if isinstance(w['pid'], int): byear.setdefault(w['pid'], set()).add((w['y'], k))
added = 0
for pid, p in P.items():
    b = BIOS['players'].get(pid)
    stops = [dict(club=c, **{'from': f, 'to': t}) for f, c, t in p.get('career', [])]
    hon = {tuple(x) for x in p.get('honors', [])}
    if b is None:
        b = BIOS['players'][pid] = dict(name=p['name'], pos=p['pos'], cpos=None, born=p['born'], college=None, conf=None, guest=None, draft=p.get('draft'), udfa=not p.get('draft'), stops=[], honors=[], rings=[], tag=p.get('tag'), real=False, exit=None, cfb=None); added += 1
    else:
        first_from = stops[0]['from'] if stops else None
        if first_from is not None: b['stops'] = [x for x in b['stops'] if x['to'] < first_from] + stops
    b['honors'] = sorted([list(h) for h in (hon | byear.get(int(pid), set()) | {tuple(x) for x in b['honors']})])
    b['rings'] = sorted(set(b['rings']) | set(p.get('rings', [])))
    b.update(status=p['status'], retired=p.get('retired'), club=p['club'], abil=p['abil'], pot=p['pot'], arch=p.get('arch'), contract=p.get('contract'))
    if p['status'] == 'retired': b['exit'] = None
# ---------------------------------------------------------------- page text
H2 = html[:i - 10]
new = H2 + 'const D = ' + json.dumps(D, separators=(',', ':'), ensure_ascii=False) + tail
def sub(a, b, n=1):
    global new
    assert new.count(a) >= 1, a
    new = new.replace(a, b)
sub('<h3>All-time table <small>1951–2040</small>', '<h3>All-time table <small>1951–2042</small>')
sub('Clubs entering the 2042 draft <small>after free agency, before the draft', 'Clubs entering the 2043 draft <small>after free agency and trades, before the draft')
sub('2042 picks: ', '2043 picks: ')
sub('>2042 rosters<', '>2043 rosters<')
sub("(p.retired || 2041) - p.born", "(p.retired || 2043) - p.born")
os.makedirs(out, exist_ok=True)
open(f'{out}/index.body.html', 'w').write(new)
json.dump(BIOS, open(f'{out}/archive_bios.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('seasons', len(D['seasons']), 'coaches', len(coaches), 'gms', len(gms), 'new bios', added, 'tx', len(D['tx']), 'size', len(new))
