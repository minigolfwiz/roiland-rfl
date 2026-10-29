"""Make the 2044 freshman class real (Dan, 29 Oct 2026).

The 2043-44 offseason never signed its recruiting class, so all 2,020 freshmen of 2044 were
generated walk-ons (no stars, ability 2.6-4.8). Dan's ruling: make that class real, even though
every 2044 result stands. So the SAME players (pid, name, position, stat lines, box scores) are kept
and their recruiting profile is supplied after the fact: a signed class is drawn the way stage 4
draws one, matched to each programme's walk-on freshmen by position, and each player takes his
recruit's stars and ability (plus one year of freshman growth, since development already ran on him).
Results, stats, records and box scores are untouched.

    python3 retro_class_2044.py            # dry run
    python3 retro_class_2044.py --commit
"""
import sys, random, pickle, collections, shutil, statistics
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, recruiting as RC
H = '/home/claude/cfb2/state/'
commit = '--commit' in sys.argv
s = SE.load_state(); assert s['season'] == 20 and s['next_week'] == 0
assert 'recruiting_s18' not in s, 'already applied'
# the 2044 freshmen = every Fr on the post-carousel, pre-portal rosters (all 2,020 were walk-ons)
old = pickle.load(open(H + 'rosters.pkl.pre_s20_draft', 'rb'))
fr_pids = {p['pid'] for t in old for p in old[t] if p['cls'] == 'Fr'}
assert len(fr_pids) == 2020 and all(p.get('walkon') for t in old for p in old[t] if p['cls'] == 'Fr')
targets = collections.defaultdict(list)
for t, r in E.ROSTERS.items():
    for p in r:
        if p['pid'] in fr_pids: targets[t].append(p)
n_found = sum(len(v) for v in targets.values()); print('2044 freshmen found on rosters:', n_found)
assert n_found == 2020
# 2043 results decide who recruits well: use the archived 2043 standings, prestige as it stands
arch = s['season_archive']['18']['standings']
tmp = dict(s); tmp['record'] = {t: dict(arch[t]) for t in E.ROSTERS}; tmp['heat'] = {t: 0.0 for t in E.ROSTERS}
needs = {t: len(targets[t]) for t in E.ROSTERS}
RC.room_crowded = lambda *a, **k: False           # the rosters in hand are 2045's, not 2043's
n_total = 2816                                    # the class the 2043 log recorded
recruits = RC.make_class(n_total, seed=63018)
signed, unsigned = RC.run_recruiting(recruits, needs, tmp, seed=64018)
print('class', n_total, 'signed', sum(len(v) for v in signed.values()), 'unsigned', len(unsigned),
      dict(sorted(collections.Counter(r['stars'] for v in signed.values() for r in v).items(), reverse=True)))
src = open('/home/claude/cfb2/gen_rosters.py').read()
a = src.index('def derive_attrs('); b = src.index('rosters = {}', a)
rng = random.Random(70018); ns = {'rng': rng}; exec(src[a:b], ns); derive_attrs = ns['derive_attrs']
changes = []; stored = {}
for t in E.ROSTERS:
    rec = sorted(signed.get(t, []), key=lambda r: -r['abil']); pl = list(targets[t]); assign = []
    # same position first
    for r in list(rec):
        m = [p for p in pl if p['pos'] == r['pos']]
        if m:
            p = m[0]; pl.remove(p); rec.remove(r); assign.append((p, r))
    # the rest: best leftover recruits to non-specialists, weakest to K/P
    pl.sort(key=lambda p: p['pos'] in ('K', 'P')); rec.sort(key=lambda r: -r['abil'])
    for p in pl:
        r = rec.pop(0) if p['pos'] not in ('K', 'P') else rec.pop(-1)
        if p['pos'] in ('K', 'P') and r['stars'] >= 4: r = dict(r, stars=3, abil=min(r['abil'], 6.4))
        assign.append((p, r))
    out = []
    for p, r in assign:
        before = p['abil']
        grown = round(min(9.6, r['abil'] + max(0.0, rng.gauss(0.45, 0.2))), 2)   # development already ran on him
        p['abil'] = grown; p['pot'] = round(min(9.95, max(grown + 0.3, r['abil'] + rng.uniform(0.55, 1.85))), 2)
        p['attrs'] = derive_attrs(p['pos'], grown, p['arch'], p['cls'])
        if p['pos'] == 'QB': p['mob'] = p['attrs'].get('mob', p.get('mob', 3.5))
        p.pop('walkon', None); p['stars'] = r['stars']; p['rid'] = r['rid']; p['signed_abil'] = r['abil']
        p['class_made_real'] = 2044
        changes.append((before, grown, r['stars']))
        out.append({'rid': r['rid'], 'name': p['name'], 'pos': p['pos'], 'stars': r['stars'], 'abil': r['abil'],
                    'arch': p['arch'], 'mob': p.get('mob') if p['pos'] == 'QB' else None, 'signed': t, 'pid': p['pid']})
    stored[t] = out
print('abil before mean %.2f -> after %.2f | 4-5*: %d' % (statistics.mean(c[0] for c in changes), statistics.mean(c[1] for c in changes), sum(1 for c in changes if c[2] >= 4)))
byc = collections.Counter()
for t, v in stored.items():
    for r in v:
        if r['stars'] >= 4: byc[E.U['team_conf'][t]] += 1
print('blue-chips by conference', byc.most_common())
if commit:
    for f in ('season_state', 'rosters'): shutil.copy(H + f + '.pkl', H + f + '.pkl.pre_s20_retro')
    s['recruiting_s18'] = {'class_size': n_total, 'needs_total': 2020, 'signed': stored, 'unsigned': unsigned,
                           'made_real': 'Dan, 2026-10-29: the 2044 class was never signed in the 2043 offseason; supplied after the fact, results unchanged'}
    PRESTIGE = E.U['prestige']; rngp = random.Random(313131 + 20 * 1009); pre = {}
    for t in E.U['teams']:
        top = sorted((p['abil'] for p in E.ROSTERS[t]), reverse=True)[:30]
        pre[t] = round(sum(top) / len(top) + E.COACHES[t]['HC']['skill'] * 0.18 + PRESTIGE[t] * 0.012 + rngp.gauss(0, 0.25), 2)
    s['preseason'] = pre
    E.persist_rosters(); SE.save_state(s)
    rk = sorted(pre, key=lambda t: -pre[t]); print('NEW PRESEASON TOP 10:', [(t, pre[t]) for t in rk[:10]])
    print('9.0+ players now:', sum(1 for t in E.ROSTERS for p in E.ROSTERS[t] if p['abil'] >= 9.0))
