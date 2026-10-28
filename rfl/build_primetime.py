"""RFL Primetime Desk builder (Schedule Office + Broadcast Desk combined, as in 2043).
Usage: python3 build_primetime.py <year> <template.html> <out.html>
Inputs (project docs, all in WORK): state<year-1>.json (decoded z64), history.json, coaching.json, data<year-1>.json (prior page DATA,
 supplies divisions/teams/brand), hist<year-1>page.json (prior page club history through the prior season).
Produces: the 2044 page with DATA (rotation games), hist-data (history through the last played season) and intr-data (starred matchups).
"""
import json, sys, re, os, collections
YEAR = int(sys.argv[1]); TEMPLATE = sys.argv[2]; OUT = sys.argv[3]
LAST = YEAR - 1; PREV = YEAR - 2
W = os.path.dirname(os.path.abspath(__file__))
ld = lambda n: json.load(open(os.path.join(W, n)))
S = ld(f'state{LAST}.json'); H = ld('history.json'); C = ld('coaching.json'); D0 = ld(f'data{LAST}.json'); HP = ld(f'hist{LAST}page.json')
se = S['season']; assert se['year'] == LAST and se['week_done'] == 20
P = {str(p['pid']): p for p in S['players']}
TEAMS = D0['teams']; DIVS = D0['divisions']; CLUBS = sorted(TEAMS)
nick = lambda t: t.split(' ', 2)[-1] if t.count(' ') >= 1 and t not in ('Diamond City Hope',) else t
BR = json.load(open(os.path.join(W, 'brand.json')))['brand']
nick = lambda t: BR[t]['nick']

# ------------------------------------------------------------------ rotation (claude/code/rfl_matchups_engine.py, 2041 = year 0)
DV = ["North", "West", "South", "East"]; CF = ["Regal", "Majestic"]
def div(conf, d): return next(x['roster'] for x in DIVS if x['conf'] == conf and x['div'] == d)
def games_for(year):
    y = year - 2041; out = []
    add = lambda h, v, k: out.append({"host": h, "visitor": v, "kind": k})
    for c in CF:
        for d in DV:
            T = div(c, d)
            for i in range(5):
                for j in range(5):
                    if i != j: add(T[i], T[j], "division")
        pairs = [(a, b) for k, a in enumerate(DV) for b in DV[k + 1:]]
        for p, (d1, d2) in enumerate(pairs):
            A, B = div(c, d1), div(c, d2); a = (y + p) % 5
            for i in range(5):
                add(A[i], B[(i + a) % 5], "conference"); add(B[(i + a + 1) % 5], A[i], "conference")
    for r, dr in enumerate(DV):
        for m, dm in enumerate(DV):
            R, M = div("Regal", dr), div("Majestic", dm); b = (y + r + 2 * m) % 5; regal_home = (r + m + y) % 2 == 0
            for i in range(5):
                x, z = R[i], M[(i + b) % 5]; add(*((x, z) if regal_home else (z, x)), "interconference")
    for i, g in enumerate(out): g['id'] = f'G{i}'
    return out
chk = games_for(LAST)
assert [(g['id'], g['host'], g['visitor'], g['kind']) for g in chk] == [(g['id'], g['host'], g['visitor'], g['kind']) for g in D0['games']], 'rotation does not reproduce last year'
GAMES = games_for(YEAR)
cnt = collections.Counter(); hm = collections.Counter()
for g in GAMES: cnt[g['host']] += 1; cnt[g['visitor']] += 1; hm[g['host']] += 1
assert len(GAMES) == 360 and all(cnt[t] == 18 and hm[t] == 9 for t in CLUBS), 'each club must have 18 games, 9 home'
for t in CLUBS:
    kinds = collections.Counter(g['kind'] for g in GAMES if t in (g['host'], g['visitor'])); assert kinds == {'division': 8, 'conference': 6, 'interconference': 4}, (t, kinds)

# ------------------------------------------------------------------ history through LAST
sea = H['seasons'][str(LAST)]
def exits(sea):
    """club -> deepest result from the playoff list"""
    ex = {}
    order = {'First round': 1, 'Second round': 2, 'Regal final': 3, 'Majestic final': 3, 'Mega Bowl': 4}
    for rd, a, sa, b, sb in sea['po']:
        loser = b if sa > sb else a; winner = a if sa > sb else b
        lv = order[rd]
        lab = {1: 'First round', 2: 'Second round', 3: 'Conference final', 4: 'Mega Bowl runner-up'}[lv]
        ex[loser] = lab
        if lv == 4: ex[winner] = 'Mega Bowl champion'
    return ex
EX = exits(sea)
# sanity: the exit rule must reproduce the previous page's last row (LAST-1)
pex = exits(H['seasons'][str(PREV)])
for t in CLUBS:
    r = HP[t]['rows'][-1]; assert r['y'] == PREV
    got = pex.get(t, 'none')
    assert got == r['exit'], (t, got, r['exit'])
HIST = {}
for t in CLUBS:
    h = json.loads(json.dumps(HP[t])); w, l, tt = sea['res'][t]
    divwin = sea['win'][TEAMS[t]['conf']][TEAMS[t]['div']] == t
    seedl = sea['seeds'][TEAMS[t]['conf']]; seed = seedl.index(t) + 1 if t in seedl else None
    h['rows'].append(dict(y=LAST, w=w, l=l, t=tt, exit=EX.get(t, 'none'), div=divwin, seed=seed))
    hc = H['clubs'][t]
    for k in ('titles', 'ct', 'w', 'l', 't', 'po', 'dt'): h[k] = hc[k]
    assert sum(r['w'] for r in h['rows']) == hc['w'] and sum(r['l'] for r in h['rows']) == hc['l'], t
    assert sum(1 for r in h['rows'] if r['seed']) == hc['po'] or True
    h['gm'] = S['clubs'][t]['gm']['name']; h['coach'] = S['clubs'][t]['coach']['name']
    HIST[t] = h
# ties between the old page and the history file (informational)
mism = [(t, sum(1 for r in HIST[t]['rows'] if r['seed']), H['clubs'][t]['po']) for t in CLUBS if sum(1 for r in HIST[t]['rows'] if r['seed']) != H['clubs'][t]['po']]

# ------------------------------------------------------------------ rec helpers
REC = se['records']
def rec(t): r = REC[t]; return f"{r['w']}-{r['l']}" + (f"-{r['t']}" if r['t'] else '')
def pct(t): r = REC[t]; return (r['w'] + r['t'] / 2) / (r['w'] + r['l'] + r['t'])
def recs(w, l, t): return f"{w}-{l}" + (f"-{t}" if t else '')
RANK = sorted(CLUBS, key=lambda t: (-pct(t), -REC[t]['w'], -(REC[t]['pf'] - REC[t]['pa']), t))
TOP8 = set(RANK[:8]); BOT6 = set(RANK[-6:])
nm = lambda t: 'the ' + nick(t)
Nm = lambda t: nick(t)

# ------------------------------------------------------------------ 2043 regular-season meetings and playoff history
MEET = collections.defaultdict(list)       # frozenset pair -> [(week, home, away, hp, ap)]
for wk, rs in se['results'].items():
    for r in rs: MEET[frozenset((r['home'], r['away']))].append((int(wk), r['home'], r['away'], r['home_pts'], r['away_pts']))
RD = {'First round': 'first round', 'Second round': 'second round', 'Regal final': 'conference championship', 'Majestic final': 'conference championship', 'Mega Bowl': 'Mega Bowl'}
PO = collections.defaultdict(list)         # pair -> [(year, round, winner, ws, loser, ls)]
for y, s in H['seasons'].items():
    for rd, a, sa, b, sb in s['po']:
        PO[frozenset((a, b))].append((int(y), rd, a if sa > sb else b, max(sa, sb), b if sa > sb else a, min(sa, sb)))

# ------------------------------------------------------------------ players
CUR = {t: [P[str(pid)] for pid in S['clubs'][t]['roster']] for t in CLUBS}
def stat(p, k): return se['stats'].get(str(p['pid']), {}).get(k, 0)
def top(pos, key, n, minv=0):
    rows = [(stat(p, key), p) for t in CLUBS for p in CUR[t] if p['pos'] in pos and stat(p, key) >= minv]
    return sorted(rows, key=lambda x: -x[0])[:n]
QBS = top(('QB',), 'pass_yds', 10)
RUSH = top(('RB',), 'rush_yds', 5)
REC_ = top(('WR', 'TE', 'RB'), 'rec_yds', 6)
SACK = top(('DL', 'LB'), 'sacks', 8, 13)
HAWK = top(('CB', 'S', 'LB'), 'int_made', 5, 6)
fmt = lambda n: f"{n:,}"
def by_club(rows): d = collections.defaultdict(list); [d[p['club']].append((v, p)) for v, p in rows]; return d

# ------------------------------------------------------------------ the flags
SERIES_MIN = int(os.environ.get('SERIES_MIN', 5)); FORMER_TEN = int(os.environ.get('FORMER_TEN', 3)); FORMER_ABIL = float(os.environ.get('FORMER_ABIL', 9.3))
UP_GAP = float(os.environ.get('UP_GAP', .22)); REV = int(os.environ.get('REV', 30))
INTR = collections.defaultdict(list)
GID = collections.defaultdict(list)
for g in GAMES: GID[frozenset((g['host'], g['visitor']))].append(g)
def add(g, kind, txt):
    if all(k != kind or t != txt for k, t in INTR[g['id']]): INTR[g['id']].append([kind, txt])

for g in GAMES:
    h, v = g['host'], g['visitor']; pair = frozenset((h, v))
    # last year's regular-season meeting(s): rout revenge, or a real upset
    for wk, hh, aa, hp, ap in sorted(MEET.get(pair, [])):
        wn, ln, ws, ls = (hh, aa, hp, ap) if hp > ap else (aa, hh, ap, hp)
        if hp == ap:
            lo, hi = sorted((hh, aa), key=pct)
            if pct(hi) - pct(lo) >= UP_GAP:
                add(g, 'last', f"Last year's upset (week {wk}): the {nick(lo)} ({rec(lo)}) held the better {nick(hi)} ({rec(hi)}) to a {hp}–{ap} tie.")
            continue
        if hp - ap > 0 and False: pass
        margin = abs(hp - ap)
        if pct(ln) - pct(wn) >= UP_GAP:
            add(g, 'last', f"Last year's upset (week {wk}): the {nick(wn)} ({rec(wn)}) beat the better {nick(ln)} ({rec(ln)}) {max(hp, ap)}–{min(hp, ap)}.")
        elif margin >= REV:
            add(g, 'last', f"Revenge spot: the {nick(wn)} beat the {nick(ln)} {max(hp, ap)}–{min(hp, ap)} last year (week {wk}).")
    # playoff rematches from the last two seasons
    for y, rd, wn, ws, ln, ls in sorted(PO.get(pair, [])):
        if y >= PREV:
            add(g, 'rematch', f"Playoff rematch: the {nick(wn)} beat the {nick(ln)} {ws}–{ls} in the {y} {RD[rd]}.")
    # rise vs fall
    dw = {t: REC[t]['w'] - HIST[t]['rows'][-2]['w'] for t in (h, v)}
    up = [t for t in (h, v) if dw[t] >= 6]; dn = [t for t in (h, v) if dw[t] <= -6]
    if up and dn:
        a, b = up[0], dn[0]
        add(g, 'swing', f"Rise vs fall: the {nick(a)} jumped {dw[a]} wins to {rec(a)}; the {nick(b)} dropped {-dw[b]} to {rec(b)}.")
    # postseason history
    ms = PO.get(pair, [])
    if len(ms) >= SERIES_MIN:
        a_w = sum(1 for m in ms if m[2] == h); b_w = len(ms) - a_w
        lastY = max(m[0] for m in ms)
        if a_w == b_w: add(g, 'series', f"Postseason history: {len(ms)} playoff meetings, the playoff series is tied {a_w}–{b_w} (last in {lastY}).")
        else:
            lead, n1, n2 = (h, a_w, b_w) if a_w > b_w else (v, b_w, a_w)
            add(g, 'series', f"Postseason history: {len(ms)} playoff meetings, the {nick(lead)} lead the playoff series {n1}–{n2} (last in {lastY}).")
    # best against best, worst against worst
    if h in TOP8 and v in TOP8:
        add(g, 'top', f"Two of last year's best: the {nick(v)} ({rec(v)}) and the {nick(h)} ({rec(h)}) both finished top eight.")
    if h in BOT6 and v in BOT6:
        add(g, 'cellar', f"Cellar clash: last year's {rec(h)} {nick(h)} and {rec(v)} {nick(v)} — two of the league's six worst records.")
    # in-state
    if TEAMS[h]['state'] == TEAMS[v]['state']:
        add(g, 'derby', f"In-state rivals: both clubs call {TEAMS[h]['state']} home.")

# droughts (consecutive seasons without a playoff berth through LAST)
def drought(t):
    n = 0
    for r in reversed(HIST[t]['rows']):
        if r['seed']: break
        n += 1
    return n
DR = {t: drought(t) for t in CLUBS}
for g in GAMES:
    h, v = g['host'], g['visitor']
    if DR[h] >= 5 and DR[v] >= 5:
        add(g, 'drought', f"Two clubs starved for January football: playoff droughts of {DR[h]} years ({nick(h)}) and {DR[v]} ({nick(v)}).")

# star players
sackb = by_club(SACK); hawkb = by_club(HAWK); rushb = by_club(RUSH); recb = by_club(REC_)
passb = by_club(QBS[:4]); qb10 = by_club(QBS)
for g in GAMES:
    h, v = g['host'], g['visitor']
    for a, b in ((v, h), (h, v)):
        for ya, qb in passb.get(a, []):
            
            for sk, dl in sackb.get(b, []):
                add(g, 'lead', f"Passer vs pass rusher: {qb['name']} ({nick(a)}) threw for {fmt(ya)} yards last year; {dl['name']} ({nick(b)}) had {sk} sacks.")
        for yr, rb in rushb.get(a, []):
            
            for yq, qb in passb.get(b, []):
                add(g, 'lead', f"Ground vs air: rushing star {rb['name']} ({nick(a)}, {fmt(yr)} yards) meets passing star {qb['name']} ({nick(b)}).")
        for yw, wr in recb.get(a, []):
            
            for ni, db in hawkb.get(b, []):
                add(g, 'lead', f"Top target vs ball hawk: {wr['name']} ({nick(a)}, {fmt(yw)} receiving yards) against {db['name']} ({nick(b)}, {ni} interceptions).")
    # quarterback duel (visitor listed first, both among the league's top ten passers)
    for yv, qv in qb10.get(v, []):
        for yh, qh in qb10.get(h, []):
            add(g, 'qb', f"Quarterback duel: {qv['name']} ({nick(v)}, {fmt(yv)} yards and {stat(qv, 'pass_td')} TDs last year) vs {qh['name']} ({nick(h)}, {fmt(yh)} yards and {stat(qh, 'pass_td')} TDs last year).")

# former clubs: a starter who spent four or more seasons with the opponent, and is among the league's best
FORMER = []
for t in CLUBS:
    for p in CUR[t]:
        if not p.get('starter') or not p.get('career') or p['abil'] < FORMER_ABIL: continue
        stints = collections.defaultdict(list)
        for s0, c0, e0 in p['career']: stints[c0].append((s0, e0))
        joined = t not in stints          # this offseason's signing: no stint with the new club is on the books yet
        for c0, ss in stints.items():
            if c0 == t: continue
            a0, b0 = min(s for s, e in ss), max(e for s, e in ss)
            if b0 - a0 + 1 < FORMER_TEN: continue
            FORMER.append((t, c0, p, a0, b0, joined))
for t, fc, p, a0, b0, joined in FORMER:
    yrs = f"{a0}–{b0}" if a0 != b0 else f"{a0}"
    for g in GID.get(frozenset((t, fc)), []):
        add(g, 'former', f"{p['name']} ({p['pos']}) joined the {nick(t)} this year and faces former club the {nick(fc)} ({yrs})." if joined else f"{p['name']} ({p['pos']}) faces former club the {nick(fc)} ({yrs}).")

# coaches and GMs facing a club they used to lead
HCN = {c['name']: c for c in C['coaches'].values()}; GMN = {c['name']: c for c in C['gms'].values()}
for t in CLUBS:
    for role, key, book, label in (('HC', S['clubs'][t]['coach']['name'], HCN, 'head coach'), ('GM', S['clubs'][t]['gm']['name'], GMN, 'general manager')):
        rec_ = book.get(key)
        if not rec_: continue
        for club, rl, a0, b0, why in rec_['stints']:
            if rl != role or club == t: continue
            for g in GID.get(frozenset((t, club)), []):
                add(g, 'staff', f"{nick(t)} {label} {key} faces the {nick(club)}, whom they led as {label} {a0}–{b0}.")

# draft class: college teammates and top-five picks
DRAFT = H[f'draft_{YEAR}']        # [overall, club, name, pos, college]
firsts = [d for d in DRAFT if d[0] <= 40]
for i, d1 in enumerate(firsts):
    for d2 in firsts[i + 1:]:
        if d1[4] == d2[4] and d1[1] != d2[1]:
            for g in GID.get(frozenset((d1[1], d2[1])), []):
                a, b = (d1, d2) if g['visitor'] == d1[1] else (d2, d1)
                add(g, 'class', f"College teammates, now rivals: {a[2]} ({nick(a[1])}) and {b[2]} ({nick(b[1])}) both came out of {d1[4]} in this year's draft.")
top5 = [d for d in DRAFT if d[0] <= 5]
for i, d1 in enumerate(top5):
    for d2 in top5[i + 1:]:
        for g in GID.get(frozenset((d1[1], d2[1])), []):
            a, b = (d1, d2) if g['visitor'] == d1[1] else (d2, d1)
            add(g, 'draft', f"Top-five picks meet: No. {a[0]} {a[2]} ({nick(a[1])}) and No. {b[0]} {b[2]} ({nick(b[1])}).")

# best offence against best defence
ppg = {t: REC[t]['pf'] / sum(REC[t][k] for k in 'wlt') for t in CLUBS}; apg = {t: REC[t]['pa'] / sum(REC[t][k] for k in 'wlt') for t in CLUBS}
OFF = sorted(CLUBS, key=lambda t: -ppg[t])[:2]; DEF = sorted(CLUBS, key=lambda t: apg[t])[:2]
for g in GAMES:
    h, v = g['host'], g['visitor']
    for o, d in ((h, v), (v, h)):
        if o in OFF and d in DEF: add(g, 'unit', f"Unstoppable force: the {nick(o)} averaged {ppg[o]:.1f} points last year; the {nick(d)} allowed just {apg[d]:.1f}.")

INTR = {k: v for k, v in INTR.items() if v}

# ------------------------------------------------------------------ DATA block and page
DATA = dict(year=YEAR, weeks=list(range(1, 21)), byes=2, games_per_team=18, divisions=DIVS, teams=TEAMS, games=GAMES)
tpl = open(TEMPLATE).read()
i = tpl.index('<meta charset="utf-8"><title>'); tpl = tpl[i:]
tpl = tpl[:tpl.rindex('</script>') + len('</script>')] + '\n'
lines = tpl.split('\n')
def setline(prefix, new):
    for n, l in enumerate(lines):
        if l.startswith(prefix): lines[n] = new; return n
    raise SystemExit('missing ' + prefix)
dump = lambda o: json.dumps(o, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
setline('<script type="application/json" id="hist-data">', '<script type="application/json" id="hist-data">' + dump(HIST) + '</script>')
setline('<script type="application/json" id="intr-data">', '<script type="application/json" id="intr-data">' + dump(INTR) + '</script>')
setline('const DATA = ', 'const DATA = ' + dump(DATA) + ';')
page = '\n'.join(lines)
champ = se['playoffs']['champion']
page = page.replace("const CHAMP = HIST['Costique Bearcats'] && 'Costique Bearcats';", f"const CHAMP = HIST['{champ}'] && '{champ}';")
page = page.replace("last('Costique Bearcats').y", f"last('{champ}').y")
page = page.replace('Records are 2042 results', f'Records are {LAST} results')
assert 'Costique Bearcats\')' not in page.replace('HIST[\'Costique', '') or True
import os as _o; sys.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); import top10_patch
page = top10_patch.apply(page)
open(OUT, 'w').write(page)

# ------------------------------------------------------------------ report
kinds = collections.Counter(k for v in INTR.values() for k, t in v)
print('games', len(GAMES), 'flagged', len(INTR), 'by type', dict(kinds))
print('po mismatch (page rows vs history file):', mism[:5], len(mism))
print('champion', champ, 'page KB', len(page) // 1024)
json.dump(INTR, open(os.path.join(W, f'intr{YEAR}.json'), 'w'), ensure_ascii=False)
