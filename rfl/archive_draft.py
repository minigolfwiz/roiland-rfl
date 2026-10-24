"""Incremental Archive step: add the 2043 draft to the live Archive page.
Usage: python3 rfl/archive_draft.py <index.html in> <archive_bios.json in> <outdir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
src, biosrc, out = sys.argv[1:4]
html = open(src).read(); BIOS = json.load(open(biosrc))
S = json.load(open('data/state_2042.json')); P = S['players']; CAP43 = cap_for(2043)
K = json.load(open('data/rfl_draft_2043_picks.json'))['picks']
i = html.index('const D = ') + 10; D, end = json.JSONDecoder().raw_decode(html[i:])
head, tail = html[:i - 10], html[i + end:]
rk = {p['draft']['pick']: p for p in P.values() if p.get('draft') and p['draft']['year'] == 2043}
via = {k['overall']: k['via'] for k in K}
draft = []
for k in K:
    p = rk[k['overall']]
    draft.append(dict(round=k['round'], pick=k['overall'], pid=p['pid'], name=p['name'], pos=p['pos'], college=p['college'], club=p['draft']['club'], via=k['via'], real=bool(p.get('real'))))
D['seasons']['2042']['draft'] = draft; D['seasons']['2042']['dy'] = 2043
for t, c in S['clubs'].items():
    ps = [P[str(x)] for x in c['roster']]
    rook = sorted([p for p in ps if p.get('draft') and p['draft']['year'] == 2043], key=lambda p: p['draft']['pick'])[:3]
    top = sorted(ps, key=lambda p: -p['abil'])[:5]; pay = payroll(S, t)
    D['state'][t].update(room=CAP43 - pay, payroll=pay, n=len(ps),
        rookies=[dict(pid=p['pid'], name=p['name'], pos=p['pos'], pick=p['draft']['pick']) for p in rook],
        top=[dict(pid=p['pid'], name=p['name'], pos=p['pos'], abil=p['abil'], age=2043 - p['born']) for p in top])
added = 0
for pid, p in P.items():
    b = BIOS['players'].get(pid)
    if b is None:
        b = BIOS['players'][pid] = dict(name=p['name'], pos=p['pos'], cpos=None, born=p['born'], college=None, conf=None, guest=None, draft=None, udfa=False, stops=[], honors=[], rings=[], tag=p.get('tag'), real=False, exit=None, cfb=None); added += 1
    if p.get('draft') and p['draft']['year'] == 2043:
        d = dict(p['draft']); v = via.get(d['pick'])
        if v: d['via'] = v
        b.update(draft=d, udfa=False, college=p.get('college'), conf=p.get('conf'), real=bool(p.get('real')))
    elif p.get('udfa') and (p.get('contract') or {}).get('signed') == 2043 and b.get('draft') is None:
        b.update(udfa=True, college=p.get('college'), conf=p.get('conf'), real=bool(p.get('real')))
    b.update(status=p['status'], retired=p.get('retired'), club=p['club'], abil=p['abil'], pot=p['pot'], arch=p.get('arch'), contract=p.get('contract'))
new = head + 'const D = ' + json.dumps(D, separators=(',', ':'), ensure_ascii=False) + tail
def sub(a, b):
    global new
    assert a in new, a; new = new.replace(a, b)
sub('Clubs entering the 2043 draft <small>after free agency and trades, before the draft', 'Clubs after the 2043 draft <small>after the draft, undrafted signings and camp cuts')
sub(' · see the Draft Book for the full draft', ' · full 2043 draft under the 2042 season')
sub('2043 picks: ', '2043 picks used: ')
os.makedirs(out, exist_ok=True)
open(f'{out}/index.body.html', 'w').write(new)
json.dump(BIOS, open(f'{out}/archive_bios.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('draft', len(draft), 'new bios', added, 'size', len(new))
