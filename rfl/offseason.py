"""Offseason steps between seasons. Usage (after the Mega Bowl and awards):
    python3 rfl/offseason.py close      # write the finished season into the history file + player honours/rings/careers
    python3 rfl/offseason.py retire     # age + progress every player, then retirements (writes state + prints the class)
Each step is guarded by S['offseason']['done'] so it cannot be run twice."""
import json, sys, os, random, collections, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import season as SE
from rfl import discipline as _disc

HIST = f'{ROOT}/data/rfl_history_1951_2040.json'
AW_ORDER = ['MVP', 'Offensive Player of the Year', 'Defensive Player of the Year', 'Rookie of the Year', 'Coach of the Year']

# ------------------------------------------------------------------ close the books
def close_books(S, H):
    se = S['season']; yr = str(se['year']); P = se['playoffs']; rec = se['records']
    assert yr not in H['seasons'], 'season already in history'
    st = SE.standings(S)
    win = {c: {d: st[c][d][0] for d in st[c]} for c in st}
    names = dict(first='First round', second='Second round', conference='Conference championship', megabowl='Mega Bowl')
    po = []
    for k in SE.STAGES:
        for r in P['rounds'].get(k, []):
            nm = names[k]
            if k == 'conference': nm = f"{r['conf']} final"
            if k == 'megabowl':
                rc = P['alive']['Regal'][0]; a, b = (r['home'], r['away']) if r['home'] == rc else (r['away'], r['home'])
                ap, bp = (r['home_pts'], r['away_pts']) if r['home'] == rc else (r['away_pts'], r['home_pts'])
                po.append([nm, a, ap, b, bp])
            else: po.append([nm, r['home'], r['home_pts'], r['away'], r['away_pts']])
    aw = {}
    for k in AW_ORDER:
        f = se['awards'][k]['finalists'][0]
        aw[k] = f"{f['name']} ({f['club']})" if k != 'Coach of the Year' else f"{f['name']} ({f['club']})"
    aw['Mega Bowl MVP'] = f"{P['mvp']['name']} ({P['mvp']['club']})"
    H['seasons'][yr] = dict(res={t: [v['w'], v['l'], v['t']] for t, v in rec.items()}, win=win, seeds=P['seeds'], po=po, champ=P['champion'], site=(P.get('site') or {}).get('city'), aw=aw, r1=[])
    confs = [r['winner'] for r in P['rounds']['conference']]
    for t, c in H['clubs'].items():
        v = rec[t]; c['w'] += v['w']; c['l'] += v['l']; c['t'] += v['t']
        if any(t in s for s in P['seeds'].values()): c['po'] += 1
        if t in [x for d in win.values() for x in d.values()]: c['dt'] += 1
        if t in confs: c['ct'].append(int(yr))
        if t == P['champion']: c['titles'].append(int(yr))
    H['note'] = H['note'].replace('1951-2041', '1951-2042') if '1951-2042' not in H['note'] else H['note']
    # players: honours, rings, career stints
    P_ = S['players']; y = int(yr)
    for k in AW_ORDER[:4]:
        pid = se['awards'][k]['finalists'][0]['pid']; P_[str(pid)].setdefault('honors', []).append([y, k])
    P_[str(P['mvp']['pid'])].setdefault('honors', []).append([y, 'Mega Bowl MVP'])
    for t in S['clubs']:
        for pid in S['clubs'][t]['roster']:
            p = P_[str(pid)]
            if t == P['champion']: p.setdefault('rings', []).append(y)
            cr = p.setdefault('career', [])
            if cr and cr[-1][1] == t: cr[-1][2] = y
            else: cr.append([y, t, y])

# ------------------------------------------------------------------ ageing and progression
POSF = dict(QB=.55, K=.4, P=.4, OL=.95, DL=1.0, TE=1.0, LB=1.1, WR=1.1, S=1.25, CB=1.3, RB=1.35)   # decline speed
def progress(S, rnd):
    yr = S['season']['year']
    for p in S['players'].values():
        if p.get('status') == 'retired': continue
        a = yr - p['born']; d = 0.0; ab, pot = p['abil'], p['pot']
        if a <= 25: d = max(0, pot - ab) * (.55 if a <= 23 else .4) + rnd.gauss(0, .16)
        elif a <= 29: d = max(0, pot - ab) * .25 + rnd.gauss(.0, .17)
        else: d = -(.1 + .12 * (a - 30)) * POSF[p['pos']] + rnd.gauss(0, .2)
        new = round(max(1.0, min(10.0, ab + d)), 2); real = new - ab
        p['abil'] = new; p['pot'] = round(max(new, pot if a <= 26 else new), 2)
        if p.get('attrs'):
            p['attrs'] = {k: round(max(1.0, min(10.0, v + real + rnd.gauss(0, .08))), 2) for k, v in p['attrs'].items()}
        p['delta'] = round(real, 2)
        if p.get('inj') and p['inj']['kind'] not in ('suspended indefinitely', 'exempt list'):
            p['inj']['weeks'] -= 30                                  # the offseason heals about 30 weeks
            if p['inj']['weeks'] <= 0: p.pop('inj')
    _disc.progress_traits(S, random.Random(f"disc-progress-{yr}"))   # hidden discipline traits mature (or, for a few, slide); own stream so nothing else shifts

# ------------------------------------------------------------------ retirements
# Position-specific career curves (Dan, 29 Oct 2026, from real football career lengths): RBs have the shortest careers (most are gone before 30), WRs and
# defensive backs peak and retire in their early 30s, linemen/LBs/TEs last a little longer, kickers and punters last longest, QBs play well into their mid-to-late
# 30s or early 40s with top QBs pushing past 37-39. Each list is (age at the coming season <=, yearly retirement chance).
CURVES = dict(
    RB=[(24, .012), (25, .04), (26, .07), (27, .10), (28, .15), (29, .22), (30, .35), (31, .50), (99, .70)],
    WR=[(26, .008), (28, .015), (29, .03), (30, .06), (31, .12), (32, .22), (33, .35), (34, .50), (35, .65), (99, .80)],
    CB=[(26, .008), (28, .015), (29, .03), (30, .06), (31, .12), (32, .22), (33, .35), (34, .50), (35, .65), (99, .80)],
    S=[(26, .008), (28, .015), (29, .03), (30, .06), (31, .12), (32, .22), (33, .35), (34, .50), (35, .65), (99, .80)],
    OL=[(27, .006), (29, .01), (30, .02), (31, .035), (32, .06), (33, .10), (34, .17), (35, .27), (36, .40), (37, .55), (99, .70)],
    DL=[(27, .006), (29, .01), (30, .02), (31, .035), (32, .06), (33, .10), (34, .17), (35, .27), (36, .40), (37, .55), (99, .70)],
    TE=[(27, .006), (29, .01), (30, .02), (31, .035), (32, .06), (33, .10), (34, .17), (35, .27), (36, .40), (37, .55), (99, .70)],
    LB=[(26, .008), (28, .012), (29, .025), (30, .04), (31, .07), (32, .12), (33, .19), (34, .30), (35, .42), (36, .55), (99, .70)],
    QB=[(30, .004), (33, .015), (34, .03), (35, .05), (36, .08), (37, .12), (38, .20), (39, .30), (40, .42), (41, .55), (99, .75)],
    K=[(30, .004), (34, .01), (36, .03), (38, .06), (40, .12), (41, .22), (42, .35), (99, .6)],
    P=[(30, .004), (34, .01), (36, .03), (38, .06), (40, .12), (41, .22), (42, .35), (99, .6)])
def hazard(p, yr):
    a = yr + 1 - p['born']                                  # age at the coming season, as in the 2042 offseason list
    h = next(v for lim, v in CURVES[p['pos']] if a <= lim)
    ov = ovr(p)
    h *= 1.8 if ov < 6.5 else (.5 if ov >= 8.5 else 1.0)
    if p.get('starter') and a <= 30: h *= .4                    # producers/starters rarely walk away early (Neraini rule, 23 Oct 2026)
    if any(y >= yr - 2 for y, _ in p.get('honors', [])) and a <= 31: h *= .4
    if p.get('inj') and p['inj']['weeks'] > 40 and a >= 28: h += .12
    return min(h, .95)


EARLY_MAX = 29   # age at the coming season; anyone this young or younger retiring gets a stated reason (Dan, 23 Oct 2026)
GENERAL = ['to spend more time with family', 'to pursue a career in broadcasting', 'to move into coaching', 'to finish a university degree', 'after losing the desire to keep playing',
           'to start a business', 'to take a job in a club front office', 'to become a player agent', 'to move home and be near family', 'to pursue a career outside football']
def early_reason(S, p, rnd):
    log = [i for i in S['season']['injuries_log'] if i['pid'] == p['pid']]
    worst = max(log, key=lambda i: i['weeks'], default=None)
    if p.get('inj') and p['inj']['weeks'] > 20:
        return f"after a {p['inj']['kind']} injury that never fully healed"
    if worst and worst['weeks'] >= 6:
        return rnd.choice([f"after a long recovery from a {worst['kind']} injury", f"after a {worst['kind']} injury changed how they saw the game"])
    if not p.get('retired_from') and not p.get('club') and ovr(p) < 7: return 'after no club offered a contract'   # only for unsigned free agents
    return rnd.choice(GENERAL)

def retire(S, rnd):
    yr = S['season']['year']; out = []
    for pid, p in S['players'].items():
        if p.get('status') == 'retired': continue
        if rnd.random() < hazard(p, yr):
            club = p['club']
            if club: S['clubs'][club]['roster'].remove(p['pid'])
            p['status'] = 'retired'; p['retired'] = yr; p['retired_from'] = club; p['club'] = None; p['contract'] = None; p.pop('starter', None)
            out.append(p)
    return out

def unretire(S, pid, contract):
    """Dan's veto: put a retired player back on the club he left, with the contract he had."""
    p = S['players'][str(pid)]; club = p['retired_from']
    p['status'] = 'active'; p['club'] = club; p['contract'] = contract
    for k in ('retired', 'retired_from', 'retire_reason'): p.pop(k, None)
    S['clubs'][club]['roster'].append(p['pid'])
    S['offseason']['retired'] = [r for r in S['offseason']['retired'] if r['pid'] != pid]

def step_retire(S):
    rnd = random.Random(2043001)
    progress(S, rnd); out = retire(S, rnd)
    S['offseason'] = dict(done=['close', 'retire'], retired=[])
    for p in out:
        a = S['season']['year'] + 1 - p['born']; r = dict(pid=p['pid'], name=p['name'], pos=p['pos'], club=p['retired_from'], age=a)
        if a <= EARLY_MAX: r['reason'] = early_reason(S, p, random.Random(p['pid'])); p['retire_reason'] = r['reason']
        S['offseason']['retired'].append(r)
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]; path = STATE; S = load(path); S.setdefault('offseason', dict(done=[]))
    if cmd == 'close':
        assert 'close' not in S['offseason']['done']
        H = load(HIST); close_books(S, H); S['offseason']['done'].append('close')
        json.dump(H, open(HIST, 'w'), separators=(',', ':'), ensure_ascii=False); save(S, path); write_project_state(S, Z64); print('closed', S['season']['year'])
    elif cmd == 'retire':
        assert 'close' in S['offseason']['done'] and 'retire' not in S['offseason']['done']
        out = step_retire(S); save(S, path); write_project_state(S, Z64); print(len(out), 'retired')
