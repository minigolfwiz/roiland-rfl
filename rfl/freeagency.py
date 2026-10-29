"""Free agency for the coming season (offseason step 3; YEAR = the season being built, 2044 after the 2043 season). Usage: python3 rfl/freeagency.py [dry] | street
The veteran market and re-signings run BEFORE the draft; the street-signing fill-in (anonymous journeymen for true holes) runs AFTER the draft and undrafted signings: `python3 rfl/freeagency.py street`.
Order: contracts tick → clubs decide who to re-sign → the open market (need-based bidding by cap room, GM aggression/discipline)
→ (after the draft) street signings fill any remaining holes up to 46. Writes S['offseason']['fa'] (log lines + stats). Guarded: runs once.
Price curve fitted to the 2041–42 free-agent and re-sign deals (salary as a share of the cap by ability and position)."""
import json, sys, os, random, collections, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *

YEAR = 2045
ANCH = [(6.8, .0038), (7.25, .0045), (7.75, .0069), (8.25, .0146), (8.75, .0239), (9.25, .0483), (9.75, .095), (10.0, .13)]
PMULT = dict(QB=1.65, OL=1.0, DL=1.0, WR=.9, CB=.9, LB=.9, TE=.9, RB=.75, S=.75, K=.1, P=.1)
MINROSTER = dict(QB=3, RB=3, WR=5, TE=2, OL=8, DL=7, LB=6, CB=5, S=3, K=1, P=1)   # 44; + 2 extras = 46 before the draft
TARGET = 46

def share(abil):
    if abil <= ANCH[0][0]: return ANCH[0][1]
    for (a0, v0), (a1, v1) in zip(ANCH, ANCH[1:]):
        if abil <= a1: return math.exp(math.log(v0) + (abil - a0) / (a1 - a0) * (math.log(v1) - math.log(v0)))
    return ANCH[-1][1]
def minsal(): return int(.004 * cap_for(YEAR))
def price(p, rnd=None):
    a = YEAR - 1 - p['born']                                    # age in the season just played
    v = share(p['abil']) * PMULT[p['pos']]
    if a >= 31: v *= .85
    if a >= 33: v *= .8
    if p['pos'] in ('K', 'P'): v = max(v, .004)
    if p.get('honors'):
        yrs_ago = YEAR - 1 - max(y for y, _ in p['honors'])
        if yrs_ago <= 2: v *= 2.0 if any(k == 'MVP' for y, k in p['honors'] if y >= YEAR - 2) else 1.4
    if rnd: v *= math.exp(rnd.gauss(0, .2))
    return int(max(minsal(), min(.17 * cap_for(YEAR), v * cap_for(YEAR))))
def years_for(p, rnd):
    a = YEAR - 1 - p['born']
    if a <= 26: return rnd.choice([3, 3, 4, 4])
    if a <= 29: return rnd.choice([2, 3, 3, 4]) if p['pos'] != 'QB' else rnd.choice([3, 4, 4])
    if a <= 31: return rnd.choice([1, 2, 2, 3])
    return rnd.choice([1, 1, 2])

def club_pos(S, t, pos, exclude=()):
    return sorted([S['players'][str(i)] for i in S['clubs'][t]['roster'] if S['players'][str(i)]['pos'] == pos and i not in exclude], key=lambda p: -ovr(p))
def sign(S, p, t, salary, years, kind, log=None, verb=None):
    p['club'] = t; p['contract'] = dict(salary=salary, years=years, left=years, signed=YEAR, kind=kind); p['status'] = 'active'
    if p['pid'] not in S['clubs'][t]['roster']: S['clubs'][t]['roster'].append(p['pid'])

def run(S, rnd):
    P = S['players']; cap = cap_for(YEAR); log = []; stats = collections.Counter()
    notable = lambda p: p['abil'] >= 8.7 or (p['pos'] == 'QB' and p['abil'] >= 8.2)
    S['clubs'][S['season']['playoffs']['champion']]['_champ'] = True
    # 1. contracts tick: those with one year left expire; everyone else loses a year
    expiring = {t: [] for t in S['clubs']}
    for t, c in S['clubs'].items():
        for pid in list(c['roster']):
            p = P[str(pid)]
            if p['contract']['left'] <= 1: p['_prev'] = t; expiring[t].append(p); c['roster'].remove(pid)
            else: p['contract']['left'] -= 1
    stats['expired'] = sum(len(v) for v in expiring.values())
    def payroll_now(t): return payroll(S, t)
    # 2. re-sign decisions
    expids = {p['pid'] for v in expiring.values() for p in v}
    pool = [p for p in P.values() if p['status'] == 'active' and not p['club'] and p['pid'] not in expids]
    for t, exp in expiring.items():
        g = S['clubs'][t]['gm']; gp = gm_profile(g['name'] if isinstance(g, dict) else g)
        for p in sorted(exp, key=lambda p: -p['abil']):
            roster_others = club_pos(S, t, p['pos']); st, n = DEPTH[p['pos']]
            rank = sum(1 for q in roster_others if ovr(q) > ovr(p)) + sum(1 for q in exp if q is not p and q['pos'] == p['pos'] and q['abil'] > p['abil'] and q.get('_kept'))
            a = YEAR - 1 - p['born']; pr = price(p, rnd); pctc = pr / cap
            base = .55 if rank < st else (.15 if rank < n else .03)
            if a >= 31: base *= .55
            elif a <= 25: base = min(.95, base * 1.15)
            if pctc > .08: base *= max(.3, .85 - .3 * gp['discipline'] + .3 * gp['aggression'])
            if p['abil'] >= 9.2: base = min(.9, base + .1)
            if any(y >= YEAR - 2 for y, _ in p.get('honors', [])) or (p['pos'] == 'QB' and rank == 0 and S['clubs'][t].get('_champ')): base = max(base, .93)   # award winners and the champions' QB are kept
            tests = p['abil'] >= 9 and rnd.random() < .15 and a >= 25            # stars sometimes test the market
            if rnd.random() < base and not tests and payroll_now(t) + pr + max(0, TARGET - len(S['clubs'][t]['roster'])) * minsal() <= .93 * cap:
                disc = rnd.uniform(.92, 1.0); sal = max(minsal(), int(pr * disc)); yrs = years_for(p, rnd)
                sign(S, p, t, sal, yrs, 're-sign'); p['_kept'] = True; stats['resigned'] += 1
                if notable(p): log.append(f"{p['name']} ({p['pos']}) re-signs with {t}, {yrs} yr")
            else: pool.append(p)
    for p in pool: p['club'] = None
    stats['pool'] = len(pool)
    # 3. open market: biggest names first; each club bids if the player fills a real need and the cap allows
    prest = {t: 0 for t in S['clubs']}
    for r in S['season']['playoffs']['rounds'].values():
        for g in r: prest[g['home']] += .01; prest[g['away']] += .01
    def need(t, p):
        pl = club_pos(S, t, p['pos']); st, n = DEPTH[p['pos']]; mn = MINROSTER[p['pos']]
        if len(pl) < mn - 1 and p['abil'] > 7.0: return 1.0        # real hole
        better = sum(1 for q in pl if ovr(q) >= ovr(p))
        if better < st:
            worse = pl[st - 1] if len(pl) >= st else None
            gain = ovr(p) - ovr(worse) if worse else 1.0
            return gain if gain > .25 else 0
        return 0
    market = sorted([p for p in pool if p['abil'] >= 7.6], key=lambda p: -price(p))
    for p in market:
        pr = price(p, rnd); best = None
        for t in S['clubs']:
            roster = len(S['clubs'][t]['roster'])
            if roster >= 50: continue
            if pr > .06 * cap and (sum(1 for i in S['clubs'][t]['roster'] if P[str(i)]['contract']['salary'] > .06 * cap and P[str(i)]['contract']['signed'] == YEAR) >= 2 or any(P[str(i)]['pos'] == p['pos'] and P[str(i)]['contract']['salary'] > .06 * cap and P[str(i)]['contract']['signed'] == YEAR for i in S['clubs'][t]['roster'])): continue   # at most 2 big new deals per club, one per position
            nd = need(t, p)
            if nd <= 0: continue
            g = S['clubs'][t]['gm']; gp = gm_profile(g['name'] if isinstance(g, dict) else g)
            bid = pr * (.93 + .22 * gp['aggression'] + rnd.uniform(-.04, .06)) * (1 + prest[t])
            reserve = max(0, 53 - roster) * minsal()
            if payroll_now(t) + bid + reserve > .985 * cap: continue
            if p['pos'] in gp['bias']: bid *= 1.04
            score = bid * (1 + .05 * min(nd, 1.5))
            if best is None or score > best[0]: best = (score, t, bid)
        if best:
            _, t, bid = best; yrs = years_for(p, rnd); sal = int(min(.17 * cap, bid))
            sign(S, p, t, max(minsal(), sal), yrs, 'free agent'); stats['signed'] += 1
            if notable(p): log.append(f"{p['name']} ({p['pos']}) " + (f"re-signs with {t}, {yrs} yr" if p.get('_prev') == t else f"signs with {t}, {yrs} yr"))
    for p in P.values(): p.pop('_kept', None); p.pop('_prev', None)
    for c in S['clubs'].values(): c.pop('_champ', None)
    stats['unsigned_left'] = sum(1 for p in P.values() if p['status'] == 'active' and not p['club'])
    return log, stats

def street_fill(S, rnd):
    """After the draft: fill every club to the camp roster with street signings (best cheap player available, else a generated journeyman)."""
    P = S['players']; stats = collections.Counter()
    left = [p for p in P.values() if p['status'] == 'active' and not p['club']]
    for t in S['clubs']:
        roster = S['clubs'][t]['roster']
        while True:
            cnt = collections.Counter(P[str(i)]['pos'] for i in roster)
            miss = [pos for pos, m in MINROSTER.items() if cnt[pos] < m]
            if (len(roster) >= TARGET and not miss) or len(roster) >= 53: break
            if miss: pos = max(miss, key=lambda x: MINROSTER[x] - cnt[x])
            else:
                pos = max(DEPTH, key=lambda x: DEPTH[x][1] / max(1, cnt[x]) if x not in ('K', 'P') else 0)
            cands = sorted([q for q in left if q['pos'] == pos and not q['club']], key=lambda q: -q['abil'])
            q = None
            for c in cands[:3]:
                if rnd.random() < .6 or c is cands[0]: q = c; break
            if q is None: q = gen_player(S, pos, YEAR, max(6.0, min(7.4, rnd.gauss(6.8, .35))), rnd, club=None, age_=rnd.randint(24, 31))
            sign(S, q, t, minsal(), 1, 'street'); stats['street'] += 1
            if q in left: left.remove(q)
    return stats

def fix_minimums(S, rnd):
    """A full 53-man roster cannot hide a missing K/P/QB: release the weakest player from the most overstocked position and sign one."""
    P = S['players']; fixed = []
    for t, c in S['clubs'].items():
        cnt = collections.Counter(P[str(i)]['pos'] for i in c['roster'])
        for pos, m in MINROSTER.items():
            while cnt[pos] < m:
                if len(c['roster']) >= 53:
                    over = max((x for x in MINROSTER if x not in ('QB', 'K', 'P') and x != pos), key=lambda x: cnt[x] - MINROSTER[x])
                    cut = min((P[str(i)] for i in c['roster'] if P[str(i)]['pos'] == over), key=lambda q: q['abil'])
                    c['roster'].remove(cut['pid']); cut['club'] = None; cut['contract'] = None; cnt[over] -= 1
                cands = sorted([q for q in P.values() if q['status'] == 'active' and not q['club'] and q['pos'] == pos], key=lambda q: -q['abil'])
                q = cands[0] if cands else gen_player(S, pos, YEAR, max(6.0, min(7.4, rnd.gauss(6.8, .35))), rnd, club=None, age_=rnd.randint(24, 31))
                sign(S, q, t, minsal(), 1, 'street'); cnt[pos] += 1; fixed.append((t, pos, q['name']))
    return fixed

if __name__ == '__main__':
    path = STATE; S = load(path); cmd = sys.argv[1] if len(sys.argv) > 1 else ''; dry = cmd == 'dry'
    if cmd == 'street':
        assert 'draft' in S['offseason']['done'] and 'street' not in S['offseason']['done'], 'run after the draft, once'
        rnd = random.Random(2045004); st = street_fill(S, rnd); fx = fix_minimums(S, rnd)
        S['offseason']['street'] = dict(stats=dict(st), fixed=[list(x) for x in fx]); S['offseason']['done'].append('street')
        print(dict(st), 'min-roster fixes', fx); save(S, path); write_project_state(S, Z64); print('saved')
    else:
        assert 'fa' not in S['offseason']['done'], 'free agency already run'
        rnd = random.Random(2045002); log, stats = run(S, rnd)
        S['offseason']['fa'] = dict(log=log, stats=dict(stats)); S['offseason']['done'].append('fa')
        print(dict(stats), len(log))
        if not dry: save(S, path); write_project_state(S, Z64); print('saved')
