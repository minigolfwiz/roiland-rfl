"""Calibration for the penalty system: same matchups and seeds played with (A) no penalties, (B) penalties with all traits equal, (C) penalties with traits.
Usage: python3 rfl/calibrate_discipline.py [games=300]"""
import sys, os, random, statistics as st, collections, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import game as G
from rfl import discipline as DISC

def run(S, cfg, n, seed0=7000):
    G.PENALTIES, G.TRAITS = cfg
    clubs = sorted(S['clubs']); rnd = random.Random(seed0); out = []
    for i in range(n):
        h, a = rnd.sample(clubs, 2)
        for t in (h, a):
            for pid in S['clubs'][t]['roster']: S['players'][str(pid)].pop('inj', None)
        out.append(G.play_game(S, h, a, 2043, seed0 + i))
    return out

def summarize(S, res, label):
    pts = [r['home_pts'] + r['away_pts'] for r in res]; ties = sum(1 for r in res if r['home_pts'] == r['away_pts'])
    yds = []; plays = []; pen_n = []; pen_y = []; byteam = collections.defaultdict(lambda: [0, 0]); byp = collections.Counter(); types = collections.Counter()
    for r in res:
        y = sum(v.get('pass_yds', 0) + v.get('rush_yds', 0) for side in 'HA' for v in r['stats'][side].values()); yds.append(y)
        n = len(r['pens']); pen_n.append(n); pen_y.append(sum(x['yds'] for x in r['pens']))
        for x in r['pens']: byteam[x['team']][0] += 1; byp[x['pid']] += 1; types[x['type']] += 1
        for t in (r['home'], r['away']): byteam[t][1] += 1
    print(f"[{label}] games {len(res)} | pts/game {st.mean(pts) / 2:.2f} per team | yards/game {st.mean(yds) / 2:.0f} per team | ties {ties} | OT {sum(1 for r in res if r['ot'])}")
    print(f"      flags/team-game {st.mean(pen_n) / 2:.2f} | penalty yds/team-game {st.mean(pen_y) / 2:.1f}")
    return dict(pts=st.mean(pts) / 2, yds=st.mean(yds) / 2, flags=st.mean(pen_n) / 2, byteam=byteam, byp=byp, types=types)

def by_quintile(S, res):
    """Flags per starter-season (18 games) by on-field discipline quintile among starters, using the depth charts the games were played with."""
    games = collections.Counter()
    for r in res:
        games[r['home']] += 1; games[r['away']] += 1
    flags = collections.Counter(x['pid'] for r in res for x in r['pens'])
    rows = []
    for t in S['clubs']:
        dc = depth_chart(S, t)
        for pos, (n, stt) in DEPTH.items():
            if pos in ('K', 'P', 'QB', 'RB', 'TE'): continue
            for p in dc[pos][:stt]: rows.append((p['disc'], flags[p['pid']] / max(1, games[t]) * 18, pos, p['cond']))
    rows.sort(); k = len(rows) // 5
    print('starter flags per 18 games by discipline quintile (worst-behaved first):', [round(sum(r[1] for r in rows[i * k:(i + 1) * k]) / k, 2) for i in reversed(range(5))])
    top = sorted(((flags[p['pid']], p['name'], p['pos'], p['disc'], p['cond']) for p in S['players'].values() if p.get('club')), reverse=True)[:10]
    print('most-flagged players in the sample (flags, pos, disc, cond):', [(f, pos, d, c) for f, nm, pos, d, c in top])


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    if len(sys.argv) > 3: G.PEN_ADJ.update(cmp=float(sys.argv[2]), run=float(sys.argv[3]))
    if len(sys.argv) > 4: G.PEN_SCALE = float(sys.argv[4])
    S0 = load(STATE); DISC.ensure_traits(S0)
    import copy
    results = {}
    for label, cfg in (('A old engine', (False, False)), ('B penalties, traits equal', (True, False)), ('C penalties + traits', (True, True))):
        S = copy.deepcopy(S0); t0 = time.time(); res = run(S, cfg, n); results[label] = summarize(S, res, label); print(f"      ({time.time() - t0:.0f}s)")
    C = results['C penalties + traits']; B = results['B penalties, traits equal']
    rate = {t: C['byteam'][t][0] / max(1, C['byteam'][t][1]) for t in C['byteam']}; rb = {t: B['byteam'][t][0] / max(1, B['byteam'][t][1]) for t in B['byteam']}
    print('team flags per game, traits ON : min %.2f max %.2f sd %.2f' % (min(rate.values()), max(rate.values()), st.pstdev(rate.values())))
    print('team flags per game, traits OFF: min %.2f max %.2f sd %.2f  (pure noise at this sample size)' % (min(rb.values()), max(rb.values()), st.pstdev(rb.values())))
    print('types (traits on):', dict(C['types'].most_common()))
    by_quintile(S, res)

