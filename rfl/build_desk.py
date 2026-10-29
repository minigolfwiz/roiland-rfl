"""Build the RFL Primetime Desk page for the NEXT season (the Schedule Office + Broadcast Desk in one page).
Usage: python3 rfl/build_desk.py [template.html]   (default: out/desk_template_2044.html, the 2044 desk as published)
Reads the live state (the season just finished, offseason done), the history file and the coaching file, and writes out/rfl_primetime_<year>.html with:
  DATA       the year's rotation games (rfl/matchups_engine.games_for), ids G0..G359
  hist-data  every club's season-by-season record through the season just played, with current GM and head coach
  intr-data  one-line storylines per game (revenge spots, playoff rematches, QB duels, former players, ...); the page ranks the ten key ones itself
The page saves Dan's picks to the db doc rfl/primetime<year>."""
import sys, os, re, json, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import matchups_engine as ME
from rfl import cases as CS

TEMPLATE = sys.argv[1] if len(sys.argv) > 1 else f'{ROOT}/out/desk_template_2044.html'
S = load(STATE); se = S['season']; LAST = se['year']; YEAR = LAST + 1
H = json.load(open(f'{ROOT}/data/rfl_history_1951_2040.json')); HS = H['seasons']
C = json.load(open(f'{ROOT}/data/rfl_coaching.json'))
P = S['players']; NICK = CS._brand_nicks()
nk = lambda t: NICK.get(t, t.split()[-1])
html = open(TEMPLATE, encoding='utf-8').read()

# ------------------------------------------------------------------ DATA
d0 = html.index('const DATA = ') + len('const DATA = '); D, d1 = json.JSONDecoder().raw_decode(html[d0:])
games = ME.games_for(YEAR)
assert len(games) == 360, len(games)
D['year'] = YEAR; D['games'] = [dict(host=g['host'], visitor=g['visitor'], kind=g['kind'], id=f'G{i}') for i, g in enumerate(games)]
html = html[:d0] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + html[d0 + d1:]

# ------------------------------------------------------------------ hist-data (append the season just played)
hs = re.search(r'(<script type="application/json" id="hist-data">)(.*?)(</script>)', html, re.S)
HD = json.loads(hs.group(2)); sd = HS[str(LAST)]
exit_of = {}; conf_champ = set(); mb = None
for nm, a, ap, b, bp in sd['po']:
    w, l = (a, b) if ap > bp else (b, a)
    if nm == 'Mega Bowl': exit_of[w] = 'Mega Bowl champion'; exit_of[l] = 'Mega Bowl runner-up'; conf_champ |= {w, l}
    elif nm.endswith('final'): exit_of[l] = 'Conference final'
    elif nm == 'Second round': exit_of[l] = 'Second round'
    elif nm == 'First round': exit_of[l] = 'First round'
seed_of = {t: i + 1 for c in sd['seeds'] for i, t in enumerate(sd['seeds'][c])}
divwin = {t for c in sd['win'].values() for t in c.values()}
for t, h in HD.items():
    if h['rows'][-1]['y'] == LAST: h['rows'].pop()
    w, l, tt = sd['res'][t]
    h['rows'].append(dict(y=LAST, w=w, l=l, t=tt, exit=exit_of.get(t, 'none'), div=t in divwin, seed=seed_of.get(t)))
    # totals rebuilt from the rows so they always agree
    h['w'] = sum(r['w'] for r in h['rows']); h['l'] = sum(r['l'] for r in h['rows']); h['t'] = sum(r['t'] for r in h['rows'])
    h['po'] = sum(1 for r in h['rows'] if r['seed']); h['dt'] = sum(1 for r in h['rows'] if r['div'])
    if t == sd['champ'] and LAST not in h['titles']: h['titles'].append(LAST)
    if t in conf_champ and LAST not in h['ct']: h['ct'].append(LAST)
    h['gm'] = S['clubs'][t]['gm']['name']; h['coach'] = S['clubs'][t]['coach']['name']
html = html[:hs.start(2)] + json.dumps(HD, ensure_ascii=False, separators=(',', ':')) + html[hs.end(2):]

# ------------------------------------------------------------------ intr-data
rec = {t: tuple(sd['res'][t]) for t in sd['res']}
gp = {t: sum(rec[t]) for t in rec}
wp = lambda t: (rec[t][0] + rec[t][2] / 2) / gp[t]
rs = lambda t: f"{rec[t][0]}-{rec[t][1]}" + (f"-{rec[t][2]}" if rec[t][2] else '')
order = sorted(rec, key=lambda t: -wp(t)); top8 = set(order[:8]); bottom6 = set(order[-6:])
pf = {t: se['records'][t]['pf'] / gp[t] for t in rec}; pa = {t: se['records'][t]['pa'] / gp[t] for t in rec}
best_off = set(sorted(pf, key=lambda t: -pf[t])[:4]); best_def = set(sorted(pa, key=lambda t: pa[t])[:4])
meet = collections.defaultdict(list); st = collections.defaultdict(collections.Counter)
for w, gs in se['results'].items():
    for g in gs:
        meet[frozenset((g['home'], g['away']))].append((int(w), g['home'], g['away'], g['home_pts'], g['away_pts']))
        for side in 'HA':
            for pid, v in g['stats'][side].items():
                for k, x in v.items():
                    if isinstance(x, (int, float)): st[str(pid)][k] += x
playoff_meet = collections.defaultdict(list)       # all playoff meetings, every season
for y in sorted(HS, key=int):
    for nm, a, ap, b, bp in HS[y].get('po') or []: playoff_meet[frozenset((a, b))].append((int(y), nm, a, ap, b, bp))
last_po = {frozenset((a, b)): (nm, a, ap, b, bp) for nm, a, ap, b, bp in sd['po']}
def starter_qb(t):
    qs = [P[str(i)] for i in S['clubs'][t]['roster'] if P[str(i)]['pos'] == 'QB' and P[str(i)].get('status') == 'active']
    return max(qs, key=lambda q: q['abil'], default=None)
def qb_line(t):
    q = starter_qb(t)
    if not q: return None
    s = st.get(str(q['pid']))
    return (q, s['pass_yds'], s['pass_td']) if s and s['pass_yds'] >= 4300 else None
def rusher(t):
    best = max((P[str(i)] for i in S['clubs'][t]['roster'] if st.get(str(i), {}).get('sacks', 0) >= 12), key=lambda p: st[str(p['pid'])]['sacks'], default=None)
    return best, (st[str(best['pid'])]['sacks'] if best else 0)
def passer(t):
    best = max((P[str(i)] for i in S['clubs'][t]['roster'] if st.get(str(i), {}).get('pass_yds', 0) >= 4800), key=lambda p: st[str(p['pid'])]['pass_yds'], default=None)
    return best, (st[str(best['pid'])]['pass_yds'] if best else 0)
last_po_year = {}
for t in rec:
    ys = [r['y'] for r in HD[t]['rows'] if r['seed']]; last_po_year[t] = max(ys) if ys else None
drought = lambda t: LAST - last_po_year[t] if last_po_year[t] else LAST - HD[t]['joined'] + 1
state_of = {t: D['teams'][t]['state'] for t in D['teams']}
# players that changed clubs this offseason, with the club and span they left
movers = collections.defaultdict(list)
for p in P.values():
    if p.get('status') != 'active' or not p.get('club') or len(p.get('career', [])) < 2: continue
    cur = p['career'][-1]
    if cur[1] != p['club'] or cur[0] != YEAR and cur[0] != LAST + 1 and cur[2] < LAST: continue
    prev = p['career'][-2]
    if prev[1] != p['club'] and prev[2] >= LAST - 1 and prev[2] - prev[0] >= 1 and p['abil'] >= 8.4: movers[p['club']].append((p, prev))
rookies = [p for p in P.values() if p.get('draft') and p['draft'].get('year') == YEAR and p.get('club')]
top5 = {p['club']: p for p in rookies if p['draft']['round'] == 1 and p['draft']['pick'] <= 5}
coll = collections.defaultdict(list)
for p in rookies:
    if p['draft']['round'] <= 2 and p.get('college'): coll[(p['college'], p['club'])].append(p)
coaches = {v['name']: v for v in C['coaches'].values()}
def stint_vs(coach_name, opp):
    c = coaches.get(coach_name)
    if not c: return None
    for cl, role, a, b, why in c['stints']:
        if cl == opp and role == 'HC' and (b or 9999) < YEAR and b is not None: return (a, b)
INTR = {}
def add(gid, kind, text): INTR.setdefault(gid, []).append([kind, text])
for g in D['games']:
    a, b, gid = g['host'], g['visitor'], g['id']; pair = frozenset((a, b)); A, B = nk(a), nk(b)
    for w, h_, v_, hp, vp in sorted(meet.get(pair, []))[-1:]:
        if abs(hp - vp) >= 14:
            win, lose, wp_, lp_ = (h_, v_, hp, vp) if hp > vp else (v_, h_, vp, hp)
            add(gid, 'last', f"Revenge spot: the {nk(win)} beat the {nk(lose)} {wp_}–{lp_} last year (week {w}).")
    if pair in last_po:
        nm, h_, hp, v_, vp = last_po[pair]; win, lose, wp_, lp_ = (h_, v_, hp, vp) if hp > vp else (v_, h_, vp, hp)
        rnd_ = nm.replace('Regal final', 'conference final').replace('Majestic final', 'conference final').lower()
        add(gid, 'rematch', f"Playoff rematch: the {nk(win)} beat the {nk(lose)} {wp_}–{lp_} in the {LAST} {rnd_}.")
    pm = playoff_meet.get(pair, [])
    if len(pm) >= 5:
        wa = sum(1 for y, nm, h_, hp, v_, vp in pm if (h_ == a) == (hp > vp)); wb = len(pm) - wa
        lead = f"the {A} lead the playoff series {wa}–{wb}" if wa > wb else (f"the {B} lead the playoff series {wb}–{wa}" if wb > wa else f"the playoff series is tied {wa}–{wb}")
        add(gid, 'series', f"Postseason history: {len(pm)} playoff meetings, {lead} (last in {pm[-1][0]}).")
    if a in top8 and b in top8:
        add(gid, 'top', f"Two of last year's best: the {A} ({rs(a)}) and the {B} ({rs(b)}) both finished top eight.")
    for x, y in ((a, b), (b, a)):
        if x in best_off and y in best_def:
            add(gid, 'unit', f"Unstoppable force: the {nk(x)} averaged {pf[x]:.1f} points last year; the {nk(y)} allowed just {pa[y]:.1f}."); break
    if a in bottom6 and b in bottom6:
        add(gid, 'cellar', f"Cellar clash: last year's {rs(a)} {A} and {rs(b)} {B} — two of the league's six worst records.")
    if drought(a) >= 6 and drought(b) >= 6:
        add(gid, 'drought', f"Two clubs starved for January football: playoff droughts of {drought(a)} years ({A}) and {drought(b)} ({B}).")
    if state_of[a] == state_of[b]:
        add(gid, 'derby', f"In-state rivals: both clubs call {state_of[a]} home.")
    qa, qb = qb_line(a), qb_line(b)
    if qa and qb:
        add(gid, 'qb', f"Quarterback duel: {qa[0]['name']} ({A}, {qa[1]:,} yards and {qa[2]} TDs last year) vs {qb[0]['name']} ({B}, {qb[1]:,} yards and {qb[2]} TDs last year).")
    for x, y in ((a, b), (b, a)):
        ps, py = passer(x); rp, sk = rusher(y)
        if ps and rp:
            add(gid, 'lead', f"Passer vs pass rusher: {ps['name']} ({nk(x)}) threw for {py:,} yards last year; {rp['name']} ({nk(y)}) had {sk} sacks."); break
    if a in top5 and b in top5:
        pa_, pb_ = top5[a], top5[b]
        add(gid, 'draft', f"Top-five picks meet: No. {pa_['draft']['pick']} {pa_['name']} ({A}) and No. {pb_['draft']['pick']} {pb_['name']} ({B}).")
    for x, y in ((a, b), (b, a)):
        for p, prev in movers.get(x, []):
            if prev[1] == y:
                add(gid, 'former', f"{p['name']} ({p['pos']}) joined the {nk(x)} this year and faces former club the {nk(y)} ({prev[0]}–{prev[2]})."); break
    for (cl, club), ps in coll.items():
        if club == a:
            for (cl2, club2), ps2 in coll.items():
                if club2 == b and cl2 == cl:
                    add(gid, 'class', f"College teammates, now rivals: {ps[0]['name']} ({A}) and {ps2[0]['name']} ({B}) both came out of {cl} in this year's draft.")
    for x, y in ((a, b), (b, a)):
        s_ = stint_vs(S['clubs'][x]['coach']['name'], y)
        if s_: add(gid, 'staff', f"{nk(x)} head coach {S['clubs'][x]['coach']['name']} faces the {nk(y)}, whom they led as head coach {s_[0]}–{s_[1]}."); break
ip = re.search(r'(<script type="application/json" id="intr-data">)(.*?)(</script>)', html, re.S)
html = html[:ip.start(2)] + json.dumps(INTR, ensure_ascii=False, separators=(',', ':')) + html[ip.end(2):]
html = html.replace(f'Records are {LAST - 1} results', f'Records are {LAST} results')
out = f'{ROOT}/out/rfl_primetime_{YEAR}.html'; open(out, 'w', encoding='utf-8').write(html)
print(out, len(html) // 1024, 'KB', len(D['games']), 'games', len(INTR), 'games with a storyline;', collections.Counter(k for v in INTR.values() for k, _ in v))
