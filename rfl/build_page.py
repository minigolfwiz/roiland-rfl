"""Build the RFL Season page by splicing fresh data into the recovered 2041 page template (same tabs, same brand chips,
same player sheets). Usage: python3 rfl/build_page.py [state_path] → out/rfl_season_<year>.html"""
import json, sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import season as SE
TEMPLATE = f'{ROOT}/out/season_template.html'
L = load(f'{ROOT}/data/league.json'); T = L['teams']
KIND = {'td': 'TD', 'fg': 'FG', 'fgmiss': 'MISS', 'onside': 'ONSIDE', 'ot': 'OT', 'tie': 'OT', '2pt': 'TD', '2ptfail': 'TD', 'xpmiss': 'TD', 'injury': None, 'inc': None}
TOT = ['cmp', 'att', 'pass_yds', 'pass_td', 'ints', 'car', 'rush_yds', 'rush_td', 'rec', 'rec_yds', 'rec_td', 'sacks', 'int_made', 'fr', 'def_td', 'fg', 'fga', 'xp', 'pts']

def game_view(S, r, seeds=None):
    out = []
    raw = [x for x in r['plays'] if x['kind'] not in ('injury', 'inc')]
    # the engine logs the XP only when it misses, so a TD not followed by xpmiss/2pt/2ptfail is worth 7
    trail = [0, 0]
    for j, p in enumerate(raw):
        i = 0 if p['side'] == 'H' else 1; k = p['kind']
        if k == 'td':
            trail[i] += 6; nxt = raw[j + 1]['kind'] if j + 1 < len(raw) else None
            if nxt not in ('xpmiss', '2pt', '2ptfail') and not p.get('noxp'): trail[i] += 1
        elif k == 'fg': trail[i] += 3
        elif k == '2pt': trail[i] += 2
        q = p['q']; clock = f"{'OT' if q == 'OT' else 'Q' + str(q)} {p['t']}"
        if k == 'turnover': out.append(dict(side=p['side'], team=p['team'], q=q, clock=clock, kind='INT' if 'INTERCEPTED' in p['text'] else 'FUM', text=p['text'], pts=0, score=list(trail)))
        elif k in ('td', 'fg', 'fgmiss', 'onside', 'ot', 'tie', '2pt', '2ptfail', 'xpmiss'):
            text = p['text'] + ({'xpmiss': '', '2pt': '', '2ptfail': ''}.get(k, ''))
            if k == 'td' and j + 1 < len(raw) and raw[j + 1]['kind'] in ('xpmiss', '2pt', '2ptfail'):
                text += {'xpmiss': ' (XP no good)', '2pt': ' (two-point GOOD)', '2ptfail': ' (two-point fails)'}[raw[j + 1]['kind']]
            if k in ('xpmiss', '2pt', '2ptfail'): continue
            out.append(dict(side=p['side'], team=p['team'], q=q, clock=clock, kind=KIND.get(k, k.upper()), text=text, pts={'td': 6, 'fg': 3}.get(k, 0), score=list(trail)))
    box = {}
    for side in ('H', 'A'):
        st = r['stats'][side]; b = dict(yards=0, pass_yds=0, rush_yds=0, to=0, drives=r.get('drives', {}).get(side, 0), tds=0, fgs=0, sacks=0)
        for pid, v in st.items():
            b['pass_yds'] += v.get('pass_yds', 0); b['rush_yds'] += v.get('rush_yds', 0); b['to'] += v.get('ints', 0) + v.get('fum', 0); b['tds'] += v.get('pass_td', 0) + v.get('rush_td', 0); b['fgs'] += v.get('fg', 0)
        b['yards'] = b['pass_yds'] + b['rush_yds']
        b['sacks'] = sum(v.get('sacks', 0) for v in r['stats']['A' if side == 'H' else 'H'].values())
        box[side] = b
    def lead(cat):
        rows = []
        for side, team in (('H', r['home']), ('A', r['away'])):
            for pid, v in r['stats'][side].items():
                p = S['players'][str(pid)]
                if cat == 'passing' and v.get('att'): rows.append((v.get('pass_yds', 0), dict(name=p['name'], club=team, line=f"{v.get('cmp', 0)}/{v['att']}, {v.get('pass_yds', 0)} yds" + (f", {v['pass_td']} TD" if v.get('pass_td') else '') + (f", {v['ints']} INT" if v.get('ints') else ''))))
                if cat == 'rushing' and v.get('car', 0) >= 3: rows.append((v.get('rush_yds', 0), dict(name=p['name'], club=team, line=f"{v['car']} car, {v.get('rush_yds', 0)} yds" + (f", {v['rush_td']} TD" if v.get('rush_td') else ''))))
                if cat == 'receiving' and v.get('rec'): rows.append((v.get('rec_yds', 0), dict(name=p['name'], club=team, line=f"{v['rec']} rec, {v.get('rec_yds', 0)} yds" + (f", {v['rec_td']} TD" if v.get('rec_td') else ''))))
                if cat == 'defence' and (v.get('sacks') or v.get('int_made')): rows.append((3 * v.get('sacks', 0) + 4 * v.get('int_made', 0), dict(name=p['name'], club=team, line=', '.join(x for x in [f"{v['sacks']} sack" + ('s' if v['sacks'] > 1 else '') if v.get('sacks') else '', f"{v['int_made']} INT" if v.get('int_made') else ''] if x))))
        rows.sort(key=lambda x: -x[0]); return [x[1] for x in rows[:3 if cat != 'passing' else 2]]
    g = dict(id=r.get('id', ''), week=r.get('week'), slot=r.get('slot', 'po'), kind=r.get('kind', r.get('stage')), home=r['home'], away=r['away'], home_pts=r['home_pts'], away_pts=r['away_pts'], ot=r['ot'], winner=r['winner'],
             plays=out, turnovers=[x for x in out if x['kind'] in ('INT', 'FUM')], box=box, injuries=r['injuries'], leaders={c: lead(c) for c in ('passing', 'rushing', 'receiving', 'defence')},
             stadium=(r.get('site') or {}).get('stadium') or T[r['home']]['stadium'], city=(r.get('site') or {}).get('city') or T[r['home']]['city'])
    if r.get('stage'):
        g['seeds'] = {r['home']: r.get('home_seed'), r['away']: r.get('away_seed')} if r.get('home_seed') else None
        g['stats'] = {str(pid): dict(name=S['players'][str(pid)]['name'], pos=S['players'][str(pid)]['pos'], club=team, **v) for side, team in (('H', r['home']), ('A', r['away'])) for pid, v in r['stats'][side].items()}
    return g

def build(S):
    se = S['season']; year = se['year']; wd = se['week_done']
    results = [dict(week=int(w), games=[game_view(S, r) for r in se['results'][w]]) for w in sorted(se['results'], key=int)]
    records = {t: [v['w'], v['l'], v['t']] for t, v in se['records'].items()}
    lead = {}
    for k in ('pass_yds', 'pass_td', 'rush_yds', 'rush_td', 'rec_yds', 'rec', 'rec_td', 'sacks', 'int_made', 'fg'):
        rows = sorted(((v.get(k, 0), pid) for pid, v in se['stats'].items() if v.get(k)), reverse=True)[:12]
        lead[k] = [dict(name=S['players'][pid]['name'], club=S['players'][pid]['club'], pos=S['players'][pid]['pos'], v=v, pid=int(pid)) for v, pid in rows]
    injuries = [dict(team=p['club'], name=p['name'], pos=p['pos'], left=p['inj']['weeks'], kind=p['inj']['kind'], since=next((i['week'] for i in reversed(se['injuries_log']) if i['pid'] == p['pid']), wd)) for p in S['players'].values() if p.get('inj') and p['club']]
    players = {}
    for pid, v in se['stats'].items():
        p = S['players'][pid]; tot = {k: v.get(k, 0) for k in TOT}
        players[pid] = dict(name=p['name'], pos=p['pos'], club=p['club'], tot=tot, gp=v.get('gp', 0), games=se['games_by_player'].get(pid, []))
    P = se['playoffs']; pgames = None; playoffs = None
    if P:
        playoffs = dict(seeds=P['seeds'], records=records)
        names = dict(first='First round', second='Second round', conference='Conference championships', megabowl='Mega Bowl')
        pgames = dict(rounds=[dict(key=k, name=names[k], games=[dict(game_view(S, r), week=21 + i, slot='po', kind=k) for r in P['rounds'][k]]) for i, k in enumerate(SE.STAGES) if k in P['rounds']],
                      champion=P.get('champion'), mvp=P.get('mvp'), site=P.get('site'))
    awards = se.get('awards') or {}
    if P and P.get('mvp') and awards:
        awards = dict(awards); mb = P['rounds']['megabowl'][0]; side = 'H' if mb['home'] == P['champion'] else 'A'; v = mb['stats'][side].get(P['mvp']['pid'], mb['stats'][side].get(str(P['mvp']['pid']), {}))
        line = ', '.join(x for x in [f"{v.get('cmp', 0)}/{v['att']}, {v.get('pass_yds', 0)} yds, {v.get('pass_td', 0)} TD" if v.get('att') else '', f"{v['car']} car, {v.get('rush_yds', 0)} yds" + (f", {v['rush_td']} TD" if v.get('rush_td') else '') if v.get('car', 0) >= 3 else '', f"{v['rec']} rec, {v.get('rec_yds', 0)} yds" + (f", {v['rec_td']} TD" if v.get('rec_td') else '') if v.get('rec') else '', f"{v['sacks']} sacks" if v.get('sacks') else '', f"{v['int_made']} INT" if v.get('int_made') else ''] if x)
        awards['Mega Bowl MVP'] = dict(award='Standinghorse Trophy', finalists=[dict(P['mvp'], line=line)])
    if awards.get('Coach of the Year'):
        awards['Coach of the Year'] = dict(awards['Coach of the Year'], finalists=[dict(f, line=f.get('line') or f.get('record', '')) for f in awards['Coach of the Year']['finalists']])
    D = dict(year=year, week_done=wd, results=results, records=records, al=L['divisions'] and {c: {d: next(x['roster'] for x in L['divisions'] if x['conf'] == c and x['div'] == d) for d in ('North', 'West', 'South', 'East')} for c in ('Regal', 'Majestic')},
             sched={w: [dict(id=g['id'], host=g['host'], visitor=g['visitor'], slot=g['slot'], kind=g['kind']) for g in gs] for w, gs in se['schedule'].items()},
             lead=lead, injuries=injuries, players=players, playoffs=playoffs, pgames=pgames, awards=awards)
    h = open(TEMPLATE, encoding='utf-8').read()
    def splice(h, name, obj):
        i = h.index(f'const {name} = '); j = json.JSONDecoder().raw_decode(h, i + len(f'const {name} = '))[1]
        return h[:i] + f'const {name} = ' + json.dumps(obj, separators=(',', ':'), ensure_ascii=False) + h[j:]
    # BRAND (slugs, nicknames, colours, fonts, wordmarks) is kept as published in the template — it never changes in-season
    h = splice(h, 'D', D)
    import re
    h = re.sub(r'RFL 20\d\d Season', f'RFL {year} Season', h); h = re.sub(r'20\d\d season', f'{year} season', h)
    return h

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else STATE
    S = load(path); h = build(S); out = f'{ROOT}/out/rfl_season_{S["season"]["year"]}.html'
    open(out, 'w', encoding='utf-8').write(h); print(out, len(h) // 1024, 'KB')
