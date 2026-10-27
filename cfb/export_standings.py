"""All-time standings page (Roiland CFB Standings artifact): national titles since 1929
(history.champ, shared titles count in full), 24-team playoff record 2026 on (games_db
PO_ games, plus state/playoff_s<N>.pkl for any season whose playoff games are not in the
db), and both rolled up by CURRENT conference. Output: state/standings.json."""
import sys, re, json, pickle, os, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db
U = E.U
ROUNDS = {'R1': 1, 'R2': 2, 'QF': 3, 'SF': 4, 'CHAMP': 5}

def main(out='/home/claude/cfb2/state/standings.json'):
    s = SE.load_state(); db = load_db()
    champ = s['history']['champ']
    last_done = max(champ)
    tconf = U['team_conf']
    # ---- titles ----
    ti = collections.Counter(); ru = collections.Counter(); last = {}; since = collections.Counter(); years = []
    for y in sorted(champ):
        w, r = champ[y]
        ws = list(w) if isinstance(w, (tuple, list)) else [w]
        for t in ws:
            ti[t] += 1; last[t] = y
            if y >= 2026: since[t] += 1
        rs = list(r) if isinstance(r, (tuple, list)) else ([r] if r else [])
        for t in rs: ru[t] += 1
        if y >= 2026: years.append({'y': y, 'w': ws[0], 'r': rs[0] if rs else None})
    # ---- playoff games ----
    games = []   # (season, round, winner, loser)
    seasons_in_db = set()
    for gid, b in db.items():
        m = re.match(r'S(\d+)PO_(R1|R2|QF|SF|CHAMP)', gid)
        if not m: continue
        sn = int(m.group(1)); seasons_in_db.add(sn)
        hw = b['home_score'] > b['away_score']
        w, l = (b['home'], b['away']) if hw else (b['away'], b['home'])
        games.append((sn, ROUNDS[m.group(2)], w, l))
    for sn in range(1, s['season'] + 1):
        p = '/home/claude/cfb2/state/playoff_s%d.pkl' % sn
        if sn in seasons_in_db or not os.path.exists(p): continue
        P = pickle.load(open(p, 'rb'))
        if not P.get('champion'): continue
        for key, rnd in (('r1_results', 1), ('r2_results', 2), ('qf_results', 3), ('sf_results', 4)):
            for g in P.get(key) or []: games.append((sn, rnd, g['winner'], g['loser']))
        games.append((sn, 5, P['champion'], P['runnerup']))
    # every playoff appearance as (year, depth, wins, losses); depth 3 = quarterfinal ...
    # 5 = title game, 6 = champion. The 24-team era adds R1 (1) and R2 (2).
    entries = collections.defaultdict(dict)          # team -> year -> [depth, W, L]
    for sn, r, w, l in games:
        y = 2025 + sn
        for t, d, won in ((w, r + 1, 1), (l, r, 0)):
            e = entries[t].setdefault(y, [0, 0, 0])
            e[0] = max(e[0], d); e[1] += won; e[2] += 1 - won
    # canon 8-team playoff, 2016-2025: history.playoff[year] = [(team, wins)], 3 wins = title
    pre = s['history'].get('playoff', {})
    for y, field in pre.items():
        for t, n in field:
            entries[t][y] = [3 + n, n, 0 if n == 3 else 1]
    def table(y0):
        out = []
        for t, ys in entries.items():
            ys = {y: e for y, e in ys.items() if y >= y0}
            if not ys: continue
            ds = [e[0] for e in ys.values()]
            out.append({'t': t, 'c': tconf.get(t), 'apps': len(ys), 'W': sum(e[1] for e in ys.values()),
                        'L': sum(e[2] for e in ys.values()), 'qf': sum(d >= 3 for d in ds), 'sf': sum(d >= 4 for d in ds),
                        'fin': sum(d >= 5 for d in ds), 'ti': sum(d >= 6 for d in ds), 'last': max(ys), 'first': min(ys)})
        out.sort(key=lambda r: (-r['ti'], -r['fin'], -r['sf'], -r['W'], r['L'], r['t']))
        return out
    po_all, po = table(min(pre) if pre else 2026), table(2026)
    pre_years = [{'y': y, 'w': next(t for t, n in pre[y] if n == 3), 'r': next(t for t, n in pre[y] if n == 2), 'era': 8} for y in sorted(pre)]
    years = pre_years + [dict(r, era=24) for r in years]
    titles = [{'t': t, 'c': tconf.get(t), 'ti': ti[t], 'ru': ru[t], 'last': last.get(t), 'since': since[t]}
              for t in set(ti) | set(ru)]
    titles.sort(key=lambda r: (-r['ti'], -r['ru'], -(r['last'] or 0), r['t']))
    # ---- conferences (current membership) ----
    confs = []
    for key, tab in (('all', po_all), ('24', po)):
        POT = {r['t']: r for r in tab}
        for ci, (c, members) in enumerate(U['conferences'].items()):
            ms = list(members)
            if key == 'all':
                confs.append({'c': c, 'tier': U['tiers'].get(c), 'n': len(ms),
                              'ti': sum(ti[m] for m in ms), 'since': sum(since[m] for m in ms),
                              'champs': sorted([m for m in ms if ti[m]], key=lambda m: -ti[m])[:4]})
            confs[ci][key] = {'apps': sum(POT[m]['apps'] for m in ms if m in POT), 'W': sum(POT[m]['W'] for m in ms if m in POT),
                              'L': sum(POT[m]['L'] for m in ms if m in POT), 'sf': sum(POT[m]['sf'] for m in ms if m in POT),
                              'fin': sum(POT[m]['fin'] for m in ms if m in POT)}
    marks = {t: {'m': U['geo'][t].get('mascot', ''), 'c': U['team_conf'][t], 'col': list(U['team_colors'][t])} for t in U['teams']}
    out_d = {'marks': marks, 'through': last_done, 'champ': champ[last_done], 'titles': titles, 'po': po, 'years': years,
             'confs': confs, 'po_all': po_all, 'po_years': '2026–%d' % last_done, 'all_years': '%d–%d' % (min(pre), last_done)}
    json.dump(out_d, open(out, 'w'))
    return out_d

if __name__ == '__main__':
    d = main()
    print(d['through'], d['champ'])
    print([(r['t'], r['ti'], r['ru'], r['last']) for r in d['titles'][:8]])
    print([(r['t'], r['apps'], r['W'], r['L'], r['ti']) for r in d['po_all'][:6]])
    for c in d['confs']: print(c['c'], c['ti'], c['all'], c['24'])
