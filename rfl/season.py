"""Season layer: weekly runner, records/standings with tiebreakers, playoffs, awards.
State keys added: S['season'] = {year, schedule: {week: [game...]}, results: {week: [result...]}, records: {club: {w,l,t,pf,pa,div:[w,l,t],conf:[w,l,t],h2h:{opp:[w,l,t]}}},
stats: {pid: {totals}}, games_by_player: {pid: [{week, opp, ha, res, st}]}, week_done, playoffs, awards}
Usage: python3 rfl/season.py week 1 | standings | playoffs first|second|conference|megabowl | awards"""
import json, sys, os, random, collections, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl.game import play_game
L = load(f'{ROOT}/data/league.json')
TEAMS = L['teams']; CLUBS = sorted(TEAMS)
def conf_of(t): return TEAMS[t]['conf']
def div_of(t): return TEAMS[t]['div']
HOLD = .18   # incumbent hold: a starter keeps the job unless the challenger is this much better on form-adjusted overall

def init_season(S, year, schedule):
    """schedule: list of {id, host, visitor, week, slot, kind}"""
    sched = collections.defaultdict(list)
    for g in schedule: sched[str(g['week'])].append(g)
    S['season'] = dict(year=year, schedule=dict(sched), results={}, records={t: dict(w=0, l=0, t=0, pf=0, pa=0, div=[0, 0, 0], conf=[0, 0, 0], h2h={}) for t in CLUBS},
                       stats={}, games_by_player={}, week_done=0, playoffs=None, awards=None, injuries_log=[])
    for p in S['players'].values(): p.pop('form', None); p.pop('inj', None)
    return S

def heal(S):
    for p in S['players'].values():
        if p.get('inj') and p['inj']['kind'] not in ('suspended indefinitely', 'exempt list'):    # open-ended holds end only by a ruling
            p['inj']['weeks'] -= 1
            if p['inj']['weeks'] <= 0: p.pop('inj')
    for c in S['clubs'].values():                      # head-coach sideline bans run down the same way
        co = c.get('coach_out')
        if co:
            co['weeks'] -= 1
            if co['weeks'] <= 0: c.pop('coach_out')

def apply_result(S, r, week, playoff=False):
    se = S['season']; h, a = r['home'], r['away']
    if not playoff:
        rec = se['records']
        for me, opp, pf, pa in ((h, a, r['home_pts'], r['away_pts']), (a, h, r['away_pts'], r['home_pts'])):
            R_ = rec[me]; R_['pf'] += pf; R_['pa'] += pa
            k = 'w' if pf > pa else ('l' if pf < pa else 't'); R_[k] += 1
            idx = {'w': 0, 'l': 1, 't': 2}[k]
            if conf_of(me) == conf_of(opp):
                R_['conf'][idx] += 1
                if div_of(me) == div_of(opp): R_['div'][idx] += 1
            R_['h2h'].setdefault(opp, [0, 0, 0])[idx] += 1
    # stats
    for side, team, opp, ha in (('H', h, a, 'vs'), ('A', a, h, '@')):
        pts_for = r['home_pts'] if side == 'H' else r['away_pts']; pts_ag = r['away_pts'] if side == 'H' else r['home_pts']
        res = ('W' if pts_for > pts_ag else 'L' if pts_for < pts_ag else 'T') + f" {pts_for}–{pts_ag}" + (' OT' if r['ot'] else '')
        for pid, st in r['stats'][side].items():
            tot = se['stats'].setdefault(str(pid), {});
            for k, v in st.items(): tot[k] = tot.get(k, 0) + v
            tot['gp'] = tot.get('gp', 0) + 1
            se['games_by_player'].setdefault(str(pid), []).append(dict(w=week if not playoff else playoff, opp=opp, ha=ha, res=res, st=st))
    for inj in r['injuries']: se['injuries_log'].append(dict(week=week, **inj))

def update_form(S, r):
    """Form drifts with performance; benching happens on the depth chart through ovr+form with an incumbent hold."""
    rnd = random.Random(hash((r['home'], r['away'], r['home_pts'])) & 0xffff)
    for side, team in (('H', r['home']), ('A', r['away'])):
        won = (r['home_pts'] > r['away_pts']) == (side == 'H') and r['home_pts'] != r['away_pts']
        for pid, st in r['stats'][side].items():
            p = S['players'][str(pid)]; f = p.get('form', 0.0); perf = 0.0
            if p['pos'] == 'QB' and st.get('att', 0) >= 10:
                perf = (st.get('pass_yds', 0) / max(1, st['att']) - 7.2) / 3 + .25 * st.get('pass_td', 0) - .35 * st.get('ints', 0)
            elif p['pos'] == 'RB' and st.get('car', 0) >= 6: perf = (st.get('rush_yds', 0) / st['car'] - 4.3) / 2.5 + .3 * st.get('rush_td', 0)
            elif p['pos'] in ('WR', 'TE') and st.get('rec', 0) >= 2: perf = (st.get('rec_yds', 0) - 50) / 60 + .3 * st.get('rec_td', 0)
            elif p['pos'] in ('DL', 'LB'): perf = .4 * st.get('sacks', 0) + .3 * st.get('ff', 0)
            elif p['pos'] in ('CB', 'S'): perf = .5 * st.get('int_made', 0)
            elif p['pos'] == 'K' and st.get('fga', 0): perf = (st.get('fg', 0) / st['fga'] - .82) * 2
            perf += .08 if won else -.05
            p['form'] = round(clamp_(f * .7 + .3 * clamp_(perf, -1.2, 1.2) * .5, -.45, .45), 3)
def clamp_(x, a, b): return max(a, min(b, x))

def set_lineups(S):
    """Enforce the incumbent hold: a bench player only overtakes when ovr+form beats the starter's by HOLD. Implemented by nudging form."""
    for t in CLUBS:
        dc = depth_chart(S, t)
        for pos, (n, st) in DEPTH.items():
            ps = sorted([S['players'][str(pid)] for pid in S['clubs'][t]['roster'] if S['players'][str(pid)]['pos'] == pos and not S['players'][str(pid)].get('inj')], key=lambda p: -(ovr(p) + p.get('form', 0)))
            inc = [p for p in ps if p.get('starter')][:st]
            for p in ps: p.pop('starter', None)
            chosen = []
            for p in inc:
                chall = [q for q in ps if q not in inc and (ovr(q) + q.get('form', 0)) > (ovr(p) + p.get('form', 0)) + HOLD]
                if chall and len(chosen) < st: pass
                else: chosen.append(p)
            for q in ps:
                if len(chosen) >= st: break
                if q not in chosen: chosen.append(q)
            for q in chosen[:st]: q['starter'] = True
            # push starters to the top of the depth chart by a small form credit so Side picks them
            for q in ps:
                if q.get('starter') and (ovr(q) + q.get('form', 0)) < max((ovr(x) + x.get('form', 0)) for x in ps): q['form'] = round(max((ovr(x) + x.get('form', 0)) for x in ps) - ovr(q) + .001, 3)

FLEX_FROM = 15
def flex_check(S, week):
    """League rule (Dan, 2042): from week 15 on, in dire circumstances a Sunday night game can be switched for another Sunday game
    the league deems worthier. 'Dire' = both clubs have losing records and at least one is well out of the race (≥4 games behind
    its division lead with the weeks left), while a Sunday game with two winning clubs exists. Returns a note or None."""
    se = S['season']; w = str(week)
    if week < FLEX_FROM: return None
    rec = se['records']; L = load(f'{ROOT}/data/league.json')['teams']
    def pct(t): r = rec[t]; return (r['w'] + .5 * r['t']) / max(1, r['w'] + r['l'] + r['t'])
    def behind(t):
        lead = max(rec[x]['w'] + .5 * rec[x]['t'] for x in rec if L[x]['conf'] == L[t]['conf'] and L[x]['div'] == L[t]['div'])
        return lead - (rec[t]['w'] + .5 * rec[t]['t'])
    left = 20 - week + 1
    notes = []
    nxt = se['schedule'].get(str(week + 1), [])
    thu_next = {t for x in nxt if x['slot'] == 'thu' for t in (x['host'], x['visitor'])}   # clubs on short rest if moved to Monday night
    for slot, label in (('snf', 'Sunday night'), ('mnf', 'Monday night')):
        for g in [x for x in se['schedule'][w] if x['slot'].startswith(slot)]:
            a, b = g['host'], g['visitor']
            dire = pct(a) < .5 and pct(b) < .5 and max(behind(a), behind(b)) >= min(4, left + 1)
            if not dire: continue
            cands = [x for x in se['schedule'][w] if x['slot'] == 'sun' and pct(x['host']) > .5 and pct(x['visitor']) > .5]
            if slot == 'mnf':   # Dan, 28 Oct 2026: MNF can flex too, but neither incoming club may play the next Thursday
                cands = [x for x in cands if x['host'] not in thu_next and x['visitor'] not in thu_next]
            if not cands: continue
            best = max(cands, key=lambda x: pct(x['host']) + pct(x['visitor']) + (.1 if x['kind'] == 'division' else 0))
            best['slot'], g['slot'] = g['slot'], 'sun'
            notes.append(f"week {week}: {g['visitor']} at {g['host']} flexed out of {label} for {best['visitor']} at {best['host']}")
    se.setdefault('flexes', []).extend(notes)
    return notes or None

def run_week(S, week, seed_base=None):
    se = S['season']; year = se['year']; w = str(week)
    assert se['week_done'] == week - 1, f"week {se['week_done']} done; play {se['week_done'] + 1} next"
    fx = flex_check(S, week)
    if fx: print('FLEX', *fx, sep='\n  ')
    set_lineups(S)
    order = {'thu': 0, 'sun': 1, 'snf': 2, 'snf2': 3, 'mnf': 4}
    games = sorted(se['schedule'][w], key=lambda g: (order.get(g['slot'], 1), random.Random(g['id']).random()))
    out = []
    for g in games:
        r = play_game(S, g['host'], g['visitor'], year, (seed_base or year * 1000) + week * 100 + int(g['id'][1:]))
        r.update(id=g['id'], week=week, slot=g['slot'], kind=g['kind'])
        apply_result(S, r, week); update_form(S, r); out.append(r)
    se['results'][w] = out; se['week_done'] = week
    heal(S)
    return out

# ---------------------------------------------------------------- standings
def pct(R): g = R['w'] + R['l'] + R['t']; return (R['w'] + .5 * R['t']) / g if g else 0
def rank(S, teams):
    """Tiebreak among teams: pct, head-to-head (among all tied), division record, conference record, point differential."""
    rec = S['season']['records']
    def h2h(t, group):
        w = l = 0
        for o in group:
            if o == t: continue
            x = rec[t]['h2h'].get(o, [0, 0, 0]); w += x[0] + .5 * x[2]; l += x[1] + .5 * x[2]
        return (w / (w + l)) if (w + l) else .5
    def subpct(x): g = sum(x); return (x[0] + .5 * x[2]) / g if g else 0
    teams = sorted(teams, key=lambda t: -pct(rec[t]))
    out = []; i = 0
    while i < len(teams):
        j = i
        while j < len(teams) and pct(rec[teams[j]]) == pct(rec[teams[i]]): j += 1
        group = teams[i:j]; members = tuple(group)   # list.sort() empties `group` while keys are computed, so h2h must read a copy
        group.sort(key=lambda t: (-h2h(t, members), -subpct(rec[t]['div']), -subpct(rec[t]['conf']), -(rec[t]['pf'] - rec[t]['pa']), -rec[t]['pf'], t))
        out += group; i = j
    return out
def standings(S):
    out = {}
    for conf in ('Regal', 'Majestic'):
        out[conf] = {}
        for d in ('North', 'West', 'South', 'East'):
            out[conf][d] = rank(S, [t for t in CLUBS if conf_of(t) == conf and div_of(t) == d])
    return out
def seeds(S):
    st = standings(S); out = {}
    for conf in ('Regal', 'Majestic'):
        winners = [st[conf][d][0] for d in ('North', 'West', 'South', 'East')]
        others = [t for t in CLUBS if conf_of(t) == conf and t not in winners]
        field = rank(S, winners + others)[:8]
        for wnr in winners:
            if wnr not in field: field = field[:7] + [wnr]
        out[conf] = rank(S, field)
    return out

# ---------------------------------------------------------------- playoffs
STAGES = ['first', 'second', 'conference', 'megabowl']
def run_playoff(S, stage, sites):
    se = S['season']; year = se['year']
    if se['playoffs'] is None: se['playoffs'] = dict(seeds=seeds(S), rounds={}, alive={c: list(seeds(S)[c]) for c in ('Regal', 'Majestic')})
    P = se['playoffs']; games = []
    if stage in ('first', 'second', 'conference'):
        for conf in ('Regal', 'Majestic'):
            alive = [t for t in P['seeds'][conf] if t in P['alive'][conf]]  # seed order
            n = len(alive); pairs = [(alive[i], alive[n - 1 - i]) for i in range(n // 2)]
            for hi, lo in pairs:
                r = play_game(S, hi, lo, year, year * 1000 + 900 + STAGES.index(stage) * 20 + P['seeds'][conf].index(hi), playoff=True)
                r.update(stage=stage, conf=conf, home_seed=P['seeds'][conf].index(hi) + 1, away_seed=P['seeds'][conf].index(lo) + 1)
                apply_result(S, r, None, playoff=stage); games.append(r)
                loser = lo if r['winner'] == hi else hi; P['alive'][conf].remove(loser)
    else:
        rc, mc = P['alive']['Regal'][0], P['alive']['Majestic'][0]
        site = sites.get(str(year), {}); home, away = (rc, mc) if random.Random(year).random() < .5 else (mc, rc)
        r = play_game(S, home, away, year, year * 1000 + 999, playoff=True); r.update(stage='megabowl', site=site, neutral=True)
        apply_result(S, r, None, playoff='megabowl'); games.append(r); P['champion'] = r['winner']; P['site'] = site
        P['mvp'] = mega_bowl_mvp(S, r)
    P['rounds'][stage] = games; heal(S); return games
def mega_bowl_mvp(S, r):
    best = None
    for side in ('H', 'A'):
        team = r['home'] if side == 'H' else r['away']
        if team != r['winner']: continue
        for pid, st in r['stats'][side].items():
            v = st.get('pass_yds', 0) / 25 + 4 * st.get('pass_td', 0) - 3 * st.get('ints', 0) + st.get('rush_yds', 0) / 10 + 5 * st.get('rush_td', 0) + st.get('rec_yds', 0) / 10 + 5 * st.get('rec_td', 0) + 4 * st.get('sacks', 0) + 6 * st.get('int_made', 0) + 2 * st.get('fg', 0)
            if best is None or v > best[0]: best = (v, pid, team)
    p = S['players'][str(best[1])]; return dict(pid=best[1], name=p['name'], pos=p['pos'], club=best[2])

# ---------------------------------------------------------------- awards
def awards(S):
    se = S['season']; rec = se['records']
    st = collections.defaultdict(collections.Counter)   # awards judge the regular season only (weeks 1-20); playoff games are excluded (Mega Bowl MVP is separate)
    for w in se['results']:
        for g in se['results'][w]:
            for side in ('H', 'A'):
                for pid, v in g['stats'][side].items():
                    for k, x in v.items():
                        if isinstance(x, (int, float)): st[str(pid)][k] += x
    def z(vals):
        m = sum(vals) / len(vals); sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** .5 or 1; return m, sd
    rows = []
    for pid, s in st.items():
        p = S['players'][str(pid)]; club = p['club']
        if not club: continue
        succ = pct(rec[club])
        v = dict(QB=lambda: s.get('pass_yds', 0) / 100 + 2.5 * s.get('pass_td', 0) - 2.5 * s.get('ints', 0) + s.get('rush_yds', 0) / 40 + 2 * s.get('rush_td', 0),
                 RB=lambda: s.get('rush_yds', 0) / 50 + 2.5 * s.get('rush_td', 0) + s.get('rec_yds', 0) / 60, WR=lambda: s.get('rec_yds', 0) / 50 + 2.5 * s.get('rec_td', 0),
                 TE=lambda: s.get('rec_yds', 0) / 45 + 2.5 * s.get('rec_td', 0), DL=lambda: 3 * s.get('sacks', 0) + 2 * s.get('ff', 0), LB=lambda: 3 * s.get('sacks', 0) + 4 * s.get('int_made', 0) + 2 * s.get('ff', 0),
                 CB=lambda: 4 * s.get('int_made', 0) + .3 * s.get('pd', 0), S=lambda: 4 * s.get('int_made', 0) + .3 * s.get('pd', 0), K=lambda: 1.2 * s.get('fg', 0) - 2 * (s.get('fga', 0) - s.get('fg', 0)), P=lambda: 0, OL=lambda: 0)[p['pos']]()
        rows.append(dict(pid=int(pid), name=p['name'], pos=p['pos'], club=club, v=v, succ=succ, rookie=bool(p.get('draft') and p['draft'].get('year') == se['year']) or (p.get('contract') and p['contract'].get('kind') == 'undrafted' and p['contract'].get('signed') == se['year']), s=s))
    bypos = collections.defaultdict(list)
    for r in rows: bypos[r['pos']].append(r['v'])
    for r in rows:
        m, sd = z(bypos[r['pos']]); r['z'] = (r['v'] - m) / sd + (.9 if r['pos'] == 'QB' else 0) - (.6 if r['pos'] in ('CB', 'S') else 0) + 1.2 * (r['succ'] - .5)
    off = [r for r in rows if r['pos'] in ('QB', 'RB', 'WR', 'TE')]; de = [r for r in rows if r['pos'] in ('DL', 'LB', 'CB', 'S')]
    top = lambda rs, n=4: sorted(rs, key=lambda r: -r['z'])[:n]
    def line(r):
        s = r['s']
        if r['pos'] == 'QB': return f"{s.get('pass_yds', 0):,} yds, {s.get('pass_td', 0)} TD, {s.get('ints', 0)} INT"
        if r['pos'] == 'RB': return f"{s.get('rush_yds', 0):,} rush yds, {s.get('rush_td', 0)} TD, {s.get('rec_yds', 0)} rec yds"
        if r['pos'] in ('WR', 'TE'): return f"{s.get('rec', 0)} rec, {s.get('rec_yds', 0):,} yds, {s.get('rec_td', 0)} TD"
        if r['pos'] in ('DL', 'LB'): return f"{s.get('sacks', 0)} sacks, {s.get('ff', 0)} FF, {s.get('int_made', 0)} INT"
        if r['pos'] in ('CB', 'S'): return f"{s.get('int_made', 0)} INT"
        return ''
    fmt = lambda rs: [dict(pid=r['pid'], name=r['name'], pos=r['pos'], club=r['club'], line=line(r)) for r in rs]
    for r in rows: r['mz'] = r['z'] * (.75 if r['pos'] in ('DL', 'LB', 'CB', 'S') else 1) - (9 if r['pos'] in ('K', 'P') else 0)
    mvp = sorted(rows, key=lambda r: -r['mz'])[:4]; opoy = top(off); dpoy = top(de); roy = sorted([r for r in rows if r['rookie']], key=lambda r: -r['mz'])[:4]
    # coach of the year: biggest overperformance vs preseason strength, weighted by record
    cy = sorted(CLUBS, key=lambda t: -(pct(rec[t]) - .5) * 1.0 - .25 * (strength(S, t) - 8.3) * -1)[:4]
    coy = [dict(name=S['clubs'][t]['coach']['name'], club=t, record=f"{rec[t]['w']}-{rec[t]['l']}" + (f"-{rec[t]['t']}" if rec[t]['t'] else '')) for t in cy]
    se['awards'] = {'MVP': dict(award='Rocaverde Award', finalists=fmt(mvp)), 'Offensive Player of the Year': dict(award='Hasselbach Award', finalists=fmt(opoy)),
                    'Defensive Player of the Year': dict(award='Fjelltveit Award', finalists=fmt(dpoy)), 'Rookie of the Year': dict(award='Rookie of the Year', finalists=fmt(roy)),
                    'Coach of the Year': dict(award='Yuanlin Award', finalists=coy)}
    return se['awards']

def leaders(S, n=10):
    st = S['season']['stats']; P = S['players']; out = {}
    cats = [('Passing yards', 'pass_yds'), ('Passing TD', 'pass_td'), ('Rushing yards', 'rush_yds'), ('Rushing TD', 'rush_td'), ('Receiving yards', 'rec_yds'), ('Receptions', 'rec'), ('Receiving TD', 'rec_td'), ('Sacks', 'sacks'), ('Interceptions', 'int_made'), ('Field goals', 'fg')]
    for label, k in cats:
        rows = sorted(((v.get(k, 0), pid) for pid, v in st.items() if v.get(k)), reverse=True)[:n]
        out[label] = [dict(pid=int(pid), name=P[pid]['name'], pos=P[pid]['pos'], club=P[pid]['club'], v=v) for v, pid in rows]
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]; path = STATE
    S = load(path)
    if cmd == 'week':
        wk = int(sys.argv[2]); res = run_week(S, wk); save(S, path)
        for r in res: print(f"{r['slot']:4} {r['away']} {r['away_pts']} @ {r['home']} {r['home_pts']}{' (OT)' if r['ot'] else ''}")
    elif cmd == 'standings':
        st = standings(S); rec = S['season']['records']
        for c in st:
            for d in st[c]: print(c, d, ', '.join(f"{t.split()[-1]} {rec[t]['w']}-{rec[t]['l']}{('-' + str(rec[t]['t'])) if rec[t]['t'] else ''}" for t in st[c][d]))
    elif cmd == 'playoffs':
        sites = {str(s['year']): s for s in load(f'{ROOT}/data/mega_bowl_sites.json')['sites']} if os.path.exists(f'{ROOT}/data/mega_bowl_sites.json') else {}
        gs = run_playoff(S, sys.argv[2], sites); save(S, path)
        for r in gs: print(r.get('conf', 'MB'), r['away'], r['away_pts'], '@', r['home'], r['home_pts'], 'OT' if r['ot'] else '')
    elif cmd == 'awards':
        a = awards(S); save(S, path); print(json.dumps(a, indent=1)[:3000])
