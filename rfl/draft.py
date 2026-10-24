"""The RFL draft: 7 rounds x 40, need-based, each GM grading on their own eye. Then undrafted signings and camp cuts
that always leave 3 QB, 1 K, 1 P and real depth. Usage: python3 rfl/draft.py [dry]
2043 version: works on the live state (data/state_2042.json, offseason step 'draft'), order from the 2042 results,
pool from the college sim's JSON (data/draft_pool_2043.json = cfb/state/draft_pool_2043.json)."""
import json, random, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
YEAR = 2043
DRY = 'dry' in sys.argv
S = load(f'{ROOT}/data/state_2042.json'); L = load(f'{ROOT}/data/league.json')
clubs = sorted(L['teams']); rnd = random.Random(YEAR * 31)
ROUNDS = 7

def draft_order(S):
    """Worst to best: non-playoff clubs by record (point differential, points scored break ties), then playoff exits by round, champion last."""
    po = S['season']['playoffs']; R = S['season']['records']; exit_ = {}
    for k in ('first', 'second', 'conference', 'megabowl'):
        for g in po['rounds'][k]:
            exit_[g['away'] if g['winner'] == g['home'] else g['home']] = k
            if k == 'megabowl': exit_[g['winner']] = 'champ'
    rank = {'none': 0, 'first': 1, 'second': 2, 'conference': 3, 'megabowl': 4, 'champ': 5}
    pct = lambda t: (R[t]['w'] + .5 * R[t]['t']) / (R[t]['w'] + R[t]['l'] + R[t]['t'])
    return sorted(R, key=lambda t: (rank[exit_.get(t, 'none')], pct(t), R[t]['pf'] - R[t]['pa'], R[t]['pf']))

def load_pool(path):
    pool = []
    for e in json.load(open(path))['pool']:
        sub = bool(e['subdivision']); pos = 'WR' if e['pos'] == 'ATH' else e['pos']; abil = float(e['abil'])
        pot = float(e['pot']) if e.get('pot') is not None else round(abil + rnd.uniform(.1, .8), 2)
        arch = e['arch'] or rnd.choice(ARCHS[pos])
        at = {k: float(v) for k, v in e['attrs'].items()} if e.get('attrs') else gen_attrs(pos, abil, arch, rnd)
        if set(at) != set(ATTR[pos]): at = gen_attrs(pos, abil, arch, rnd) if not set(ATTR[pos]) <= set(at) else {k: at[k] for k in ATTR[pos]}
        pool.append(dict(cfb_pid=e['pid'], name=e['name'], pos=pos, cls=e['cls'], college=e['college'], conf=e['conference'], tier=e['tier'], early=bool(e['early_entrant']), sub=sub,
                         abil=abil, pot=pot, dur=float(e['dur']) if e.get('dur') is not None else round(rnd.uniform(.4, .9), 2), arch=arch, attrs=at,
                         prod=float(e.get('prod') or 0.0), stock=float(e['college_scout_stock']), stats=e.get('final_season_stats') or {}, born=YEAR - (22 if e['cls'] == 'Sr' else 21)))
    return pool

def grade(gm, q, need_qb=False):
    r = random.Random(sha(gm['name'] + q['name']))
    noise = r.gauss(0, (1 - gm['eye']) * .55)
    v = q['abil'] + gm['aggression'] * .7 * max(0, q['pot'] - q['abil']) + noise
    if q['pos'] in gm['bias']: v += .25
    if q['pos'] in ('K', 'P'): v -= 1.6
    if q['pos'] == 'QB': v += (.6 if need_qb else .1)
    if q['sub']: v -= .4
    return v

def needs(t):
    dc = depth_chart(S, t); out = {}
    for pos, (n, st) in DEPTH.items():
        ps = dc[pos]; starters = [ovr(p) for p in ps[:st]] + [5.0] * max(0, st - len(ps))
        weak = max(0, 8.2 - min(starters)) + .5 * max(0, 7.8 - sum(starters) / st)
        thin = .35 * max(0, (n - 1) - len(ps))
        old = .25 * sum(1 for p in ps[:st] if age(p, YEAR) >= 31)
        out[pos] = weak + thin + old
        if pos in ('K', 'P'): out[pos] = 1.2 if not ps else (.6 if ovr(ps[0]) < 7.0 else 0)
    if S['clubs'][t].get('drafted_qb'): out['QB'] = 0
    return out

def pick_order():
    order = S['draft_order']; slots = []
    for r in range(1, ROUNDS + 1):
        for orig in order:
            owner = next(t for t in clubs if [r, orig] in S['clubs'][t]['picks'][str(YEAR)])
            slots.append((r, orig, owner))
    return slots

def add_rookie(q, t, draft, salary, years, kind='rookie'):
    pid = new_pid(S)
    p = dict(pid=pid, cfb_pid=q['cfb_pid'], name=q['name'], pos=q['pos'], born=q['born'], college=q['college'], conf=q['conf'], tier=q['tier'], abil=q['abil'], pot=max(q['pot'], q['abil']),
             dur=q['dur'], arch=q['arch'], attrs=q['attrs'], club=t, status='active', real=not q['sub'], draft=draft, career=[[YEAR, t, YEAR]], honors=[], rings=[],
             contract=dict(salary=int(salary), years=years, left=years, signed=YEAR, kind=kind), cls=q['cls'], udfa=kind == 'undrafted')
    S['players'][str(pid)] = p; S['clubs'][t]['roster'].append(pid); return p

def run_draft(pool):
    picks = []; avail = list(pool)
    for i, (r, orig, owner) in enumerate(pick_order(), 1):
        gm = S['clubs'][owner]['gm']; nd = needs(owner)
        best = max(avail, key=lambda q: grade(gm, q, nd['QB'] > .8) * (1 + .09 * min(nd[q['pos']], 3.0)) - (1.4 if q['pos'] in ('K', 'P') and r < 3 else 0))
        if best['pos'] == 'QB': S['clubs'][owner]['drafted_qb'] = True
        avail.remove(best)
        pl = add_rookie(best, owner, dict(year=YEAR, round=r, pick=i, club=owner), rookie_salary(YEAR, i), 4 if r == 1 else 3)
        picks.append(dict(overall=i, round=r, pick=(i - 1) % 40 + 1, club=owner, via=None if owner == orig else orig, prospect=best, pid=pl['pid']))
    return picks, avail

def sign_udfas(avail):
    """Seniors go first (underclassmen mostly return to school); clubs fill holes to ~60 for camp."""
    signed = []; seniors = [q for q in avail if not q['early']]; seniors.sort(key=lambda q: -(q['abil'] + .5 * (q['pot'] - q['abil'])))
    for q in seniors:
        cands = [t for t in clubs if len(S['clubs'][t]['roster']) < 62]
        if not cands: break
        t = max(cands, key=lambda t: needs(t)[q['pos']] + random.Random(sha(t + q['name'])).random() * .6)
        if needs(t)[q['pos']] < .15 and q['abil'] < 6.6: continue
        add_rookie(q, t, None, .004 * cap_for(YEAR), 2, 'undrafted'); signed.append((q, t))
    return signed

def cuts():
    out = []
    for t in clubs:
        c = S['clubs'][t]
        while len(c['roster']) > ROSTER_MAX:
            dc = depth_chart(S, t); cand = []
            for pos, (n, st) in DEPTH.items():
                keep = max(n, st + 1) if pos not in ('K', 'P') else 1
                for p in dc[pos][keep:]: cand.append(p)
            if not cand:
                for pos, (n, st) in DEPTH.items():
                    if len(dc[pos]) > (st + 1 if pos not in ('K', 'P') else 1): cand += dc[pos][st + 1:]
            p = min(cand, key=lambda p: ovr(p) + .4 * max(0, p['pot'] - p['abil']) * (1 if age(p, YEAR) <= 25 else 0) + (.3 if p['contract']['kind'] == 'rookie' and p['draft'] else 0))
            c['roster'].remove(p['pid']); p['club'] = None; p['status'] = 'out'; p['contract'] = None; out.append((t, p))
    return out

if __name__ == '__main__':
    assert 'draft' not in S['offseason']['done'], 'draft already run'
    S['draft_order'] = draft_order(S)
    pool = load_pool(f'{ROOT}/data/draft_pool_{YEAR}.json'); print('pool', len(pool), '| order top5', S['draft_order'][:5], '| last', S['draft_order'][-1])
    picks, avail = run_draft(pool)
    udfa = sign_udfas(avail); cut = cuts()
    for t in clubs: S['clubs'][t].pop('drafted_qb', None)
    pj = lambda x: int(x) if str(x).isdigit() else x
    ret = dict(season=YEAR - 2026, picks=[dict(overall=k['overall'], round=k['round'], pick=k['pick'], rfl_team=k['club'], pid=pj(k['prospect']['cfb_pid']), name=k['prospect']['name'], via=k['via']) for k in picks],
               undrafted_signed=[dict(pid=pj(q['cfb_pid']), name=q['name'], rfl_team=t) for q, t in udfa],
               note='Picks in the order the RFL made them; "via" is the club whose slot it originally was. Undrafted seniors listed were signed as free agents; undrafted underclassmen returned to school.')
    book = dict(order=S['draft_order'], note=f'Live {YEAR} draft from the college sim\'s declared pool (rebuilt engine).',
                picks=[dict(ovr=k['overall'], round=k['round'], pick_in_round=k['pick'], club=k['club'], via=k['via'], name=k['prospect']['name'], pos=k['prospect']['pos'], pro_pos=k['prospect']['pos'], cls=k['prospect']['cls'], college=k['prospect']['college'], conf=k['prospect']['conf'], tier=k['prospect']['tier'],
                            guest=k['prospect']['sub'], abil=k['prospect']['abil'], pot=k['prospect']['pot'], dur=k['prospect']['dur'], arch=k['prospect']['arch'], attrs=' '.join(f'{a} {v}' for a, v in k['prospect']['attrs'].items()), prod=k['prospect']['prod'], early=k['prospect']['early'], udfa=False, cfb_pid=k['prospect']['cfb_pid'], college_grade=k['prospect']['stock']) for k in picks],
                udfa=[dict(ovr=None, round=None, pick_in_round=None, club=t, via=None, name=q['name'], pos=q['pos'], pro_pos=q['pos'], cls=q['cls'], college=q['college'], conf=q['conf'], tier=q['tier'], guest=q['sub'], abil=q['abil'], pot=q['pot'], dur=q['dur'], arch=q['arch'], attrs=' '.join(f'{a} {v}' for a, v in q['attrs'].items()), prod=q['prod'], early=q['early'], udfa=True, cfb_pid=q['cfb_pid'], college_grade=q['stock']) for q, t in udfa])
    S['offseason']['draft'] = dict(order=S['draft_order'], picks=[(k['overall'], k['club'], k['pid']) for k in picks], udfa=len(udfa), cuts=len(cut))
    S['offseason']['done'].append('draft'); S['phase'] = 'post-draft'
    if not DRY:
        json.dump(ret, open(f'{ROOT}/data/rfl_draft_{YEAR}_picks.json', 'w'), indent=0)
        json.dump(book, open(f'{ROOT}/data/draft_book_{YEAR}.json', 'w'), separators=(',', ':'))
        save(S, f'{ROOT}/data/state_2042.json'); write_project_state(S, f'{ROOT}/data/rfl_state_2042.z64')
    json.dump([[k['overall'], k['round'], k['club'], k['via'], k['prospect']['name'], k['prospect']['pos'], k['prospect']['college'], k['prospect']['abil'], k['prospect']['pot'], k['prospect']['cls']] for k in picks], open('/tmp/picks43.json', 'w'))
    print('by position', collections.Counter(k['prospect']['pos'] for k in picks).most_common())
    print('udfa signed', len(udfa), '| cuts', len(cut), '| roster sizes', sorted(collections.Counter(len(S['clubs'][t]['roster']) for t in clubs).items()))
    top = sorted(pool, key=lambda q: -q['abil'])[:15]; print('best talents:', [(q['name'], q['pos'], q['abil'], next((k['overall'] for k in picks if k['prospect'] is q), 'UDFA/ret')) for q in top])
