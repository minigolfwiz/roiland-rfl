"""Offseason step 4: trades for picks and staff moves (YEAR = the season being built; 2044 after the 2043 season). Usage: python3 rfl/trades.py [dry]
Trades: cap-tight clubs with surplus talent sell to clubs with a real need and room; payment is the buyer's 2043 pick (round by rating).
Staff: head coaches/GMs are fired, resign or retire; replacements are promoted coordinators/assistant GMs from other clubs (coaching doc updated).
Also creates 2043 pick ownership for every club. Guarded: runs once. Writes S['offseason']['trades'] and ['staff'] and data/rfl_coaching.json."""
import json, sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import season as SE
from rfl.freeagency import club_pos, MINROSTER

YEAR = 2045
SEASON = YEAR - 1          # the season just played; staff records and honours close on it
COACHING = f'{ROOT}/data/rfl_coaching.json'

# ------------------------------------------------------------------ trades
def pick_round(p):
    o = ovr(p)
    return 1 if o >= 9.3 else (2 if o >= 8.5 else 3)

def run_trades(S, rnd, target=7):
    P = S['players']; cap = cap_for(YEAR); log = []
    for t, c in S['clubs'].items(): c['picks'][str(YEAR)] = [[r, t] for r in range(1, 8)]
    def st(t): return payroll(S, t) / cap
    def starters(t, pos): return club_pos(S, t, pos)
    def need(t, p):
        pl = starters(t, p['pos']); n = DEPTH[p['pos']][0]
        if len(pl) < n: return 1.0
        return ovr(p) - ovr(pl[n - 1])
    def surplus(t, p):
        pl = starters(t, p['pos']); n = DEPTH[p['pos']][0]
        if any(y >= YEAR - 3 for y, _ in p.get('honors', [])): return False        # recent award winners are never shopped (Dan, 29 Oct 2026: the two-time MVP was traded)
        if p['pos'] == 'QB': return len(pl) > n and p in pl[n:]                      # a starting QB is never surplus, only the backup behind him
        return len(pl) > n and p in pl[n - 1:]
    done = set()
    def trade(seller, buyer, p, why):
        r = pick_round(p)
        mine = [x for x in S['clubs'][buyer]['picks'][str(YEAR)] if x[0] == r and x[1] == buyer]
        if not mine: return False
        pk = mine[0]; S['clubs'][buyer]['picks'][str(YEAR)].remove(pk); S['clubs'][seller]['picks'][str(YEAR)].append(pk)
        S['clubs'][seller]['roster'].remove(p['pid']); S['clubs'][buyer]['roster'].append(p['pid']); p['club'] = buyer
        # the buyer's pick now belongs to the seller
        log.append(f"{seller} trade {p['name']} ({p['pos']}, {ovr(p):.1f}) to {buyer} for a {YEAR} round-{r} pick"); done.add(p['pid'])
        return True
    # (b) general market: tight clubs shed surplus, needy clubs with room buy
    sellers = [t for t in S['clubs'] if st(t) > .93]
    rnd.shuffle(sellers); tries = 0
    while len(log) < target and tries < 400:
        tries += 1
        t = rnd.choice(sellers)
        ps = [P[str(i)] for i in S['clubs'][t]['roster'] if P[str(i)]['pid'] not in done and ovr(P[str(i)]) >= 8.2 and P[str(i)]['pos'] not in ('K', 'P') and surplus(t, P[str(i)])]
        if not ps: continue
        p = rnd.choice(ps); sal = p['contract']['salary']
        buyers = [(need(b, p), b) for b in S['clubs'] if b != t and len(S['clubs'][b]['roster']) < 53 and payroll(S, b) + sal < .92 * cap and need(b, p) > .5]
        if not buyers: continue
        buyers.sort(reverse=True); b = buyers[0][1] if rnd.random() < .6 else rnd.choice(buyers)[1]
        trade(t, b, p, 'market')
    return log

# ------------------------------------------------------------------ staff
def ageof(person): return YEAR - person['born']
def sync_2042(S, D, rnd):
    """The coaching doc was generated through 2041; bring it in line with the 2042 hires already made in the state (state is canon)."""
    C = D['coaches']; G = D['gms']; n = 0
    cidx = {v['name']: v for v in C.values()}; gidx = {v['name']: v for v in G.values()}
    nid = dict(c=max(int(k) for k in C) + 1, g=max(int(k) for k in G) + 1)
    hist = json.load(open(f'{ROOT}/data/rfl_history_1951_2040.json'))['offseason_2042']['conduct']
    for t, c in S['clubs'].items():
        for role, key, idx, store, nk in (('HC', 'coach', cidx, C, 'c'), ('GM', 'gm', gidx, G, 'g')):
            cur = [v for v in store.values() if v['stints'][-1][0] == t and v['stints'][-1][1] == role and v['stints'][-1][3] is None]
            want = c[key]['name']
            if cur and cur[0]['name'] == want: continue
            old = cur[0] if cur else None
            if old:
                resigned = any(old['name'] in x and 'resign' in x for x in hist)
                old['stints'][-1][3] = 2041; old['stints'][-1][4] = 'resigned' if resigned else 'fired'
            new = idx.get(want)
            if new is None:
                new = dict(name=want, born=rnd.randint(1978, 1992), stints=[], **({'hc': [0, 0, 0], 'titles': [], 'coy': []} if role == 'HC' else {'origin': 'scout', 'rec': [0, 0, 0], 'titles': []}))
                store[str(nid[nk])] = new; nid[nk] += 1; idx[want] = new
            else:
                s = new['stints'][-1]
                if s[3] is None: s[3] = 2041; s[4] = f"hired as {role} by {t}"
                else: new['stints'].append([t, role, 2042, None, None]); continue
                # vacated coordinator/assistant slot at the old club
                vac, vrole = s[0], s[1]
                v = dict(name=None, born=rnd.randint(1980, 1992), stints=[], **({'hc': [0, 0, 0], 'titles': [], 'coy': []} if role == 'HC' else {'origin': 'scout', 'rec': [0, 0, 0], 'titles': []}))
                fn = sorted({x['name'].split(' ')[0] for x in C.values()}); ln = sorted({x['name'].split(' ', 1)[1] for x in C.values() if ' ' in x['name']})
                while True:
                    nm = f"{rnd.choice(fn)} {rnd.choice(ln)}"
                    if nm not in cidx and nm not in gidx: break
                v['name'] = nm; store[str(nid[nk])] = v; nid[nk] += 1; idx[nm] = v; v['stints'].append([vac, vrole, 2042, None, None])
            new['stints'].append([t, role, 2042, None, None]); n += 1
    return n

def run_staff(S, rnd, D):
    moves = []; conduct = []; C = D['coaches']; G = D['gms']
    rec = S['season']['records']; champ = S['season']['playoffs']['champion']
    pc = lambda t: rec[t]['w'] / max(1, rec[t]['w'] + rec[t]['l'] + rec[t]['t'])
    ids = {n: int(k) for k, n in ((k, v['name']) for k, v in C.items())}
    cidx = {v['name']: v for v in C.values()}; gidx = {v['name']: v for v in G.values()}
    nxt = dict(c=max(int(k) for k in C) + 1, g=max(int(k) for k in G) + 1)
    first = sorted({v['name'].split(' ')[0] for v in C.values()}); last = sorted({v['name'].split(' ', 1)[1] for v in C.values() if ' ' in v['name']})
    used = {v['name'] for v in C.values()} | {v['name'] for v in G.values()}
    def newname():
        while True:
            n = f"{rnd.choice(first)} {rnd.choice(last)}"
            if n not in used: used.add(n); return n
    # close the season on the incumbents: records, titles, awards
    coy = S['season']['awards']['Coach of the Year']['finalists'][0]['name']
    for t, c in S['clubs'].items():
        h = cidx[c['coach']['name']]; g = gidx[c['gm']['name']]; r = rec[t]
        h['hc'] = [h['hc'][0] + r['w'], h['hc'][1] + r['l'], h['hc'][2] + r['t']]; g['rec'] = [g['rec'][0] + r['w'], g['rec'][1] + r['l'], g['rec'][2] + r['t']]
        if t == champ: h['titles'].append(SEASON); g['titles'].append(SEASON)
        if h['name'] == coy: h['coy'].append(SEASON)
    D['coy'][str(SEASON)] = dict(name=coy, club=S['season']['awards']['Coach of the Year']['finalists'][0]['club'])
    def stint(person, role, club):   # current open stint
        s = person['stints'][-1]; assert s[0] == club and s[1] == role and s[3] is None, (person['name'], s)
        return s
    def close(person, role, club, why):
        s = stint(person, role, club); s[3] = SEASON; s[4] = why
    def openst(person, role, club): person['stints'].append([club, role, YEAR, None, None])
    # who leaves
    leave = {}
    for t, c in S['clubs'].items():
        h = cidx[c['coach']['name']]; g = gidx[c['gm']['name']]; p = pc(t)
        tenure_h = YEAR - stint(h, 'HC', t)[2]; tenure_g = YEAR - stint(g, 'GM', t)[2]
        skill = c['coach']['skill']
        hz = .5 if p < .25 else .32 if p < .35 else .16 if p < .45 else .04 if p < .6 else .0
        hz += max(0, -skill) * .6 + min(.1, tenure_h * .01 if p < .5 else 0)
        if t == champ or p >= .65: hz = 0
        gz = (.22 if p < .3 else .12 if p < .4 else .04 if p < .55 else 0) + (.06 if tenure_g >= 8 and p < .5 else 0)
        if t == champ or p >= .65: gz = 0
        # retirement/resignation chances (age, personal reasons) hit any club
        hr = {True: .5, False: .0}[ageof(h) >= 68] if ageof(h) >= 68 else (.18 if ageof(h) >= 65 else .01)
        gr = (.4 if ageof(g) >= 68 else .15 if ageof(g) >= 65 else .01)
        u = rnd.random()
        if u < hr: leave[(t, 'HC')] = 'retired' if ageof(h) >= 64 else 'resigned'
        elif rnd.random() < hz: leave[(t, 'HC')] = 'fired'
        u = rnd.random()
        if u < gr: leave[(t, 'GM')] = 'retired' if ageof(g) >= 64 else 'resigned'
        elif rnd.random() < gz: leave[(t, 'GM')] = 'fired'
    # coordinators/assistants: the promotion pool (not at a club losing its own man this round is fine; they leave their slot)
    oc = [(v, s[0], s[1]) for v in C.values() for s in v['stints'][-1:] if s[3] is None and s[1] in ('OC', 'DC')]
    agm = [(v, v['stints'][-1][0]) for v in G.values() if v['stints'][-1][3] is None and v['stints'][-1][1] == 'AGM']
    # unemployed coaches (last stint ended, not retired) refill coordinator slots
    free = [v for v in C.values() if v['stints'][-1][3] is not None and v['stints'][-1][4] != 'retired' and v['born'] >= 1962 and v['stints'][-1][3] >= 2036]
    refill = []
    reasons_res = ['for personal reasons', 'to spend more time with family', 'citing health reasons in the family', 'to take a role in broadcasting', 'to become a college analyst']
    for (t, role), how in sorted(leave.items()):
        c = S['clubs'][t]
        if role == 'HC':
            old = cidx[c['coach']['name']]; wording = {'fired': 'fired', 'resigned': f'resigns {rnd.choice(reasons_res)}', 'retired': 'retires'}[how]
            why = {'fired': 'fired', 'resigned': 'resigned', 'retired': 'retired'}[how]
            close(old, 'HC', t, why)
            if how != 'fired': conduct.append(f"{t} head coach {old['name']} {wording}")
        else:
            old = gidx[c['gm']['name']]; wording = {'fired': 'fired', 'resigned': f'resigns {rnd.choice(reasons_res)}', 'retired': 'retires'}[how]
            close(old, 'GM', t, how if how != 'resigned' else 'resigned')
            if how != 'fired': conduct.append(f"{t} general manager {old['name']} {wording}")
        leave[(t, role)] = (how, old['name'])
    # hire head coaches from the OC/DC pool, never from a club that is itself hiring; weaker clubs hire first
    order = sorted(leave, key=lambda k: pc(k[0]))
    taken = set()
    for (t, role) in order:
        how, oldname = leave[(t, role)]; c = S['clubs'][t]
        if role == 'HC':
            pool = [x for x in oc if x[0]['name'] not in taken and x[1] != t and ageof(x[0]) <= 62]
            new, from_club, from_role = rnd.choice(pool); taken.add(new['name'])
            new['stints'][-1][3] = SEASON; new['stints'][-1][4] = f"hired as HC by {t}"; openst(new, 'HC', t)
            c['coach'] = coach_profile(new['name'])
            refill.append((from_club, from_role))
            moves.append(f"{t}: {new['name']} replaces {oldname} as head coach")
        else:
            pool = [x for x in agm if x[0]['name'] not in taken and x[1] != t]
            new, from_club = rnd.choice(pool); taken.add(new['name'])
            new['stints'][-1][3] = SEASON; new['stints'][-1][4] = f"hired as GM by {t}"; openst(new, 'GM', t)
            c['gm'] = gm_profile(new['name'])
            S['_agm_vac'] = S.get('_agm_vac', []) + [from_club]
            moves.append(f"{t}: {new['name']} replaces {oldname} as general manager")
    # refill vacated coordinator and assistant-GM slots
    for club, role in refill:
        cand = [v for v in free if v['name'] not in taken and v['stints'][-1][0] != club]
        if cand and rnd.random() < .6: v = rnd.choice(cand); taken.add(v['name'])
        else:
            n = newname(); v = dict(name=n, born=rnd.randint(1980, 1992), stints=[], hc=[0, 0, 0], titles=[], coy=[]); C[str(nxt['c'])] = v; nxt['c'] += 1; cidx[n] = v
        openst(v, role, club)
    for club in S.pop('_agm_vac', []):
        n = newname(); v = dict(name=n, born=rnd.randint(1982, 1998), origin='scout', stints=[], rec=[0, 0, 0], titles=[]); G[str(nxt['g'])] = v; nxt['g'] += 1
        openst(v, 'AGM', club)
    return sorted(moves), conduct

if __name__ == '__main__':
    path = STATE; S = load(path); dry = len(sys.argv) > 1 and sys.argv[1] == 'dry'
    assert 'fa' in S['offseason']['done'] and 'trades' not in S['offseason']['done'], 'run free agency first / trades already run'
    rnd = random.Random(2045003); D = load(COACHING)
    trades = run_trades(S, rnd); moves, conduct = run_staff(S, rnd, D)
    S['offseason']['trades'] = trades; S['offseason']['staff'] = dict(moves=moves, conduct=conduct); S['offseason']['done'].append('trades')
    print(len(trades), 'trades'); [print(' ', x) for x in trades]
    print(len(moves), 'staff moves'); [print(' ', x) for x in moves]; [print(' ', x) for x in conduct]
    if not dry:
        save(S, path); write_project_state(S, Z64); json.dump(D, open(COACHING, 'w'), separators=(',', ':'), ensure_ascii=False); print('saved')
