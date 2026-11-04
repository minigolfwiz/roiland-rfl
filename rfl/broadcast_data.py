"""Data for the Broadcast Desk section of the League Office (Thursday and Monday night picks, set before the season).

  build(S) -> dict(games=[{id, week, host, visitor, kind, juice}], hist={club: {...rows...}}, teams={club: {conf, div, city, state, stadium}}, champion=club)

juice is the old desk's rough draw score, recovered exactly from the 2042 desk (it fits to the second decimal):
  juice(game) = score(host) + score(visitor) + 0.25 if division game
  score(club) = last season's win percentage (ties count half) + a playoff bonus: first round .15, second round .30, conference final .45, Mega Bowl runner-up .60, champion .80
hist is every club's season-by-season history through the season just played (the latest out/rfl_primetime_<yr>.html desk carries it through the year before; the last season is appended from the history file)."""
import os, re, json, glob
from rfl.engine import *

BONUS = (('champion', .8), ('runner', .6), ('conference', .45), ('second', .3), ('semi', .3), ('first', .15), ('wild', .15))
def playoff_bonus(exit_):
    e = (exit_ or '').lower()
    for k, v in BONUS:
        if k in e: return v
    return 0.0

def _desk_hist(last):
    cands = sorted(glob.glob(f'{ROOT}/out/rfl_primetime_*.html'), key=lambda p: int(re.search(r'(\d{4})', os.path.basename(p)).group(1)))
    cands = [p for p in cands if int(re.search(r'(\d{4})', os.path.basename(p)).group(1)) <= last]
    html = open(cands[-1], encoding='utf-8').read()
    return json.loads(re.search(r'<script type="application/json" id="hist-data">(.*?)</script>', html, re.S).group(1))

def hist_through(S):
    """Season rows through the season just played (year - 1), with current coach and GM."""
    year = S['season']['year']; LAST = year - 1
    HD = _desk_hist(LAST); sd = json.load(open(f'{ROOT}/data/rfl_history_1951_2040.json'))['seasons'][str(LAST)]
    exit_of = {}; conf_champ = set()
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
        h['w'] = sum(r['w'] for r in h['rows']); h['l'] = sum(r['l'] for r in h['rows']); h['t'] = sum(r['t'] for r in h['rows'])
        h['po'] = sum(1 for r in h['rows'] if r['seed']); h['dt'] = sum(1 for r in h['rows'] if r['div'])
        if t == sd['champ'] and LAST not in h['titles']: h['titles'].append(LAST)
        if t in conf_champ and LAST not in h['ct']: h['ct'].append(LAST)
        h['gm'] = S['clubs'][t]['gm']['name']; h['coach'] = S['clubs'][t]['coach']['name']
    return HD, sd['champ']

def build(S):
    se = S['season']; L = json.load(open(f'{ROOT}/data/league.json'))['teams']
    HD, champ = hist_through(S)
    def score(t):
        r = HD[t]['rows'][-1]; return (r['w'] + r['t'] / 2) / (r['w'] + r['l'] + r['t']) + playoff_bonus(r['exit'])
    games = []
    for w in sorted(se['schedule'], key=int):
        for g in se['schedule'][w]:
            games.append(dict(id=g['id'], week=int(w), host=g['host'], visitor=g['visitor'], kind=g['kind'],
                              juice=round(score(g['host']) + score(g['visitor']) + (.25 if g['kind'] == 'division' else 0), 2)))
    teams = {t: dict(conf=v['conf'], div=v['div'], city=v['city'], state=v['state'], stadium=v['stadium']) for t, v in L.items()}
    return dict(year=se['year'], weeks=list(range(1, 21)), games=games, hist=HD, teams=teams, champion=champ)
