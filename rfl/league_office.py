"""League Office: the weekly between-games desk for Dan.

Two jobs, both decided by Dan before the next week is played:
  1. Players of the Week (offense, defense, special teams) from the week just played.
  2. Cases that reach the commissioner's desk. The case system lives in rfl/cases.py (engine) and rfl/case_catalog.py (types and facts): every case is
     rolled from facts, has a severity, an option ladder built around that severity, precedent, and (for some) follow-ups weeks later.

Usage:
  python3 rfl/league_office.py ballot N        # build the ballot for the week just played (once; saved to data/office/; also saves the state)
  python3 rfl/league_office.py apply N file    # apply Dan's decisions (json from the page's db doc) to the state
"""
import sys, os, json, math, random, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import cases as CS

RATES = CS.RATES

# ----------------------------------------------------------------------------- Players of the Week
import re
def _tm(c): return c.split()[-1]
def _margin(score, club_is_home):
    h, a = [int(x) for x in score.split('-')]; return (h - a) if club_is_home else (a - h)
def _clock_txt(pl): return f"Q{pl['q']} {pl['t']}" if pl['q'] != 'OT' else f"OT {pl['t']}"
def _situation(m, pl):
    """How the game stood from the player's side when the play happened (score string is taken at the play)."""
    late = pl['q'] == 'OT' or (pl['q'] == 4 and int(pl['t'].split(':')[0]) < 6)
    if m > 0: s = f"up {m}"
    elif m < 0: s = f"down {-m}"
    else: s = "tied"
    return s + (", late" if late and abs(m) <= 8 else '')

def defender_plays(g, side, p, club):
    """Turnovers this defender made, with the clock, the score at that moment, and whether it led to points."""
    out = []; pl = g['plays']; home = (side == 'H'); nm = p['name']
    for i, e in enumerate(pl):
        if e['kind'] != 'turnover' or nm not in e['text']: continue
        txt = e['text']
        if f"INTERCEPTED by {nm}" in txt: kind = 'interception' + (f" returned {re.search(r'returned (\d+)', txt).group(1)} yds" if 'returned' in txt else '')
        elif f"sacked by {nm}" in txt and 'FUMBLES' in txt: kind = 'sack and forced fumble'
        else: continue
        m = _margin(e['score'], home)  # the log is written before the turnover changes the score
        led = ''
        for f in pl[i + 1:]:
            if f['kind'] in ('td', 'fg', 'fgmiss', 'turnover'):
                if f['kind'] in ('td', 'fg') and f['team'] == club: led = ', led to a ' + ('touchdown' if f['kind'] == 'td' else 'field goal')
                break
        out.append(f"{_clock_txt(e)} {kind} ({_situation(m, e)}){led}")
    return out


def offense_plays(g, side, p, club):
    """Touchdowns this player scored or threw, plus costly turnovers, each with the clock, the score situation and what it meant."""
    pl = g['plays']; home = (side == 'H'); nm = p['name']; won = g['winner'] == club; out = []; bonus = 0
    for i, e in enumerate(pl):
        if e['team'] != club or nm not in e['text']: continue
        if e['kind'] == 'td':
            m = re.match(r'(.+?) (\d+)\s?yd TD (?:pass to (.+)|run)', e['text'])
            if m and m.group(3): lab = f"{m.group(2)}-yd TD pass to {m.group(3)}" if m.group(1) == nm else f"{m.group(2)}-yd TD catch from {m.group(1)}"
            elif m: lab = f"{m.group(2)}-yd TD run"
            else: lab = 'touchdown'
            after = _margin(e['score'], home); before = after - 6; tag = ''
            late = e['q'] == 'OT' or (e['q'] == 4 and int(e['t'].split(':')[0]) < 8)
            later_opp = any(f['kind'] in ('td', 'fg') and f['team'] != club for f in pl[i + 1:])
            if (e['q'] == 4 or e['q'] == 'OT') and before <= 0 < after:
                tag = ', go-ahead' + (' and decisive, never answered' if won and not later_opp else ', later answered'); bonus += 3 if (won and not later_opp) else 1.5
            elif (e['q'] == 4 or e['q'] == 'OT') and after == 0: tag = ', tied the game'; bonus += 1
            elif late and before < 0 and after > -9: tag = ', cut the deficit late'; bonus += .75
            elif won and not later_opp and e['q'] == 4 and 0 < after <= 8: tag = ', put the game away'; bonus += 1
            out.append(f"{_clock_txt(e)} {lab} (was {_situation(before, e)}){tag}")
        elif e['kind'] == 'turnover' and (f"{nm} INTERCEPTED" in e['text'] or f"{nm} FUMBLES" in e['text'] or f"{nm} sacked" in e['text'] and 'FUMBLES' in e['text']):
            m = _margin(e['score'], home); kind = 'interception thrown' if 'INTERCEPTED' in e['text'] else 'fumble lost'
            led = ''
            for f in pl[i + 1:]:
                if f['kind'] in ('td', 'fg', 'fgmiss', 'turnover'):
                    if f['kind'] in ('td', 'fg') and f['team'] != club: led = ', led to a ' + ('touchdown' if f['kind'] == 'td' else 'field goal')
                    break
            late = e['q'] == 'OT' or (e['q'] == 4 and int(e['t'].split(':')[0]) < 6)
            if led or (late and abs(m) <= 8): bonus -= 1.5
            out.append(f"{_clock_txt(e)} {kind} ({_situation(m, e)}){led}")
    return out, bonus

def kicker_plays(g, side, club, k):
    """Every field-goal attempt with distance, result, clock and what it meant for the game."""
    pl = g['plays']; home = (side == 'H'); out = []; made = []; miss = []
    won = g['winner'] == club
    for i, e in enumerate(pl):
        if e['team'] != club or e['kind'] not in ('fg', 'fgmiss') or k['name'] not in e['text']: continue
        d = int(re.search(r'(\d+)-yd', e['text']).group(1)); good = e['kind'] == 'fg'
        tag = ''
        if good:
            made.append(d); after = _margin(e['score'], home); before = after - 3
            later_opp = any(f['kind'] in ('td', 'fg') and f['team'] != club for f in pl[i + 1:])
            if (e['q'] == 4 or e['q'] == 'OT') and before <= 0 < after:
                tag = ', go-ahead' + (' and decisive, never answered' if won and not later_opp else ', later answered')
            elif (e['q'] == 4 or e['q'] == 'OT') and after == 0: tag = ', tied the game'
            elif won and not later_opp and 0 < after <= 3 and e['q'] == 4: tag = ', final margin'
        else: miss.append(d)
        out.append(f"{_clock_txt(e)} {d}-yd {'GOOD' if good else 'MISSED'}{tag}")
    return out, made, miss

def potw(S, week, res):
    P = S['players']; offs, defs, sts = [], [], []
    for g in res:
        for side, team in (('H', g['home']), ('A', g['away'])):
            won = (g['home_pts'] > g['away_pts']) == (side == 'H') and g['home_pts'] != g['away_pts']
            score_line = f"{'W' if won else ('T' if g['home_pts'] == g['away_pts'] else 'L')} {g['home_pts'] if side == 'H' else g['away_pts']}-{g['away_pts'] if side == 'H' else g['home_pts']}"
            opp = g['away'] if side == 'H' else g['home']; res_txt = f"{score_line} vs {opp.split()[-1]}" if side == 'H' else f"{score_line} at {opp.split()[-1]}"
            has_tkl = any('tkl' in v for v in g['stats'][side].values())
            for pid, st in g['stats'][side].items():
                p = P[str(pid)]; line = []; sc = 0
                if p['pos'] == 'QB' and st.get('att', 0) >= 10:
                    sc = st.get('pass_yds', 0) / 25 + st.get('pass_td', 0) * 4 + st.get('rush_td', 0) * 5 + st.get('rush_yds', 0) / 15 - st.get('ints', 0) * 3 - st.get('fum', 0) * 2
                    line = [f"{st.get('cmp', 0)}/{st.get('att', 0)}, {st.get('pass_yds', 0)} yds"] + ([f"{st['pass_td']} TD"] if st.get('pass_td') else []) + ([f"{st['ints']} INT"] if st.get('ints') else []) + ([f"{st['rush_yds']} rush yds"] if st.get('rush_yds', 0) >= 25 else [])
                elif p['pos'] in ('RB', 'WR', 'TE', 'QB'):
                    sc = st.get('rush_yds', 0) / 10 + st.get('rec_yds', 0) / 10 + (st.get('rush_td', 0) + st.get('rec_td', 0)) * 6 - st.get('fum', 0) * 3
                    if st.get('car', 0) >= 5 and p['pos'] != 'QB': line.append(f"{st['car']} car, {st.get('rush_yds', 0)} yds")
                    if st.get('rec', 0): line.append(f"{st['rec']} rec, {st.get('rec_yds', 0)} yds")
                    if st.get('rush_td', 0) + st.get('rec_td', 0): line.append(f"{st.get('rush_td', 0) + st.get('rec_td', 0)} TD")
                    if p['pos'] == 'QB': sc = 0
                if sc > 0:
                    pv, bn = offense_plays(g, side, p, team); sc += bn
                    offs.append(dict(pid=p['pid'], name=p['name'], pos=p['pos'], club=team, line=', '.join(line), res=res_txt, score=round(sc, 2), plays=pv))
                if p['pos'] in ('DL', 'LB', 'CB', 'S') and (st.get('sacks', 0) or st.get('int_made', 0) or st.get('ff', 0) or st.get('tkl', 0) >= 7):
                    pv = defender_plays(g, side, p, team)
                    sc = st.get('tkl', 0) * .6 + st.get('sacks', 0) * 5 + st.get('int_made', 0) * 6 + st.get('ff', 0) * 4 + sum(2 for x in pv if 'led to' in x) + sum(1.5 for x in pv if 'late' in x)
                    line = ([f"{st['tkl']} tackles"] if st.get('tkl') else []) + ([f"{st['sacks']:g} sack{'s' if st['sacks'] != 1 else ''}"] if st.get('sacks') else []) + ([f"{st['int_made']} INT"] if st.get('int_made') else []) + ([f"{st['ff']} forced fumble{'s' if st['ff'] != 1 else ''}"] if st.get('ff') else [])
                    if not has_tkl: line.append('tackles not tracked this week')
                    defs.append(dict(pid=p['pid'], name=p['name'], pos=p['pos'], club=team, line=', '.join(line), res=res_txt, score=sc, plays=pv))
                if p['pos'] == 'K' and st.get('fga', 0) + st.get('xp', 0):
                    ks, made, miss = kicker_plays(g, side, team, p)
                    xpm = sum(1 for e in g['plays'] if e['team'] == team and e['kind'] == 'xpmiss')
                    dec = sum(1 for x in ks if 'decisive' in x) * 3 + sum(1 for x in ks if 'go-ahead' in x) * 1.5
                    sc = st.get('fg', 0) * 3 + st.get('xp', 0) * .5 - (st.get('fga', 0) - st.get('fg', 0)) * 2 + sum(max(0, d - 44) for d in made) * .25 + dec
                    ln = f"{st.get('fg', 0)}/{st.get('fga', 0)} FG" + (f", long {max(made)}" if made else '') + f", {st.get('xp', 0)}/{st.get('xp', 0) + xpm} XP"
                    sts.append(dict(pid=p['pid'], name=p['name'], pos='K', club=team, line=ln, res=res_txt, score=sc, plays=ks))
                if p['pos'] == 'P' and st.get('punts', 0) >= 3:
                    avg = st.get('punt_yds', 0) / st['punts']; ln = f"{st['punts']} punts, {avg:.1f} avg" + (f", {st['in20']} inside the 20" if st.get('in20') else (', inside-20 not tracked this week' if not has_tkl else ', none inside the 20'))
                    sts.append(dict(pid=p['pid'], name=p['name'], pos='P', club=team, line=ln, res=res_txt, score=(avg - 40) * st['punts'] / 6 + st.get('in20', 0) * 1.5, plays=[]))
    top = lambda L, n: sorted(L, key=lambda x: -x['score'])[:n]
    qbs = top([o for o in offs if o['pos'] == 'QB'], 2); skill = top([o for o in offs if o['pos'] != 'QB'], 3)
    off = sorted(qbs + skill, key=lambda x: -x['score'])
    return dict(off=off, defense=top(defs, 6), st=top(sts, 5))

# ----------------------------------------------------------------------------- ballot
def ballot(S, week):
    se = S['season']; assert se['week_done'] == week, f"week {week} not the last played ({se['week_done']})"
    path = f'{ROOT}/data/office/ballot_{se["year"]}_w{week}.json'
    if os.path.exists(path): raise SystemExit(f'ballot already exists: {path} (never re-draw a ballot)')
    res = se['results'][str(week)]
    cases = CS.draw(S, week, res)
    B = dict(year=se['year'], week=week, potw=potw(S, week, res), cases=cases, rates=[dict(tier=t, mean=m) for t, m in RATES], open=open_storylines(S))
    os.makedirs(f'{ROOT}/data/office', exist_ok=True)
    json.dump(B, open(path, 'w'), indent=1); return B

def offseason_ballot(S, week=21):
    """Special ballot between seasons: only the follow-ups that are still due (no Players of the Week, no new cases)."""
    se = S['season']; path = f'{ROOT}/data/office/ballot_{se["year"]}_w{week}.json'
    if os.path.exists(path): raise SystemExit(f'ballot already exists: {path}')
    o = CS.office(S); rnd = random.Random(f"league-office-{se['year']}-{week}"); cases = []
    due = [d for d in o['due'] if d['kind'] in ('findings', 'felony', 'court')]; o['due'] = [d for d in o['due'] if d not in due]
    for it in due:
        c = CS.follow_up(S, rnd, it, week)
        if not c: continue
        c['_it'] = it; c['tier'] = 'major' if c['type'].startswith('felony') else CS.CATALOG[c['type']]['tier']; cases.append(c)
    for i, c in enumerate(cases):
        c['id'] = f"W{week}-{i + 1}"; c['week'] = week; c.pop('_story', None); c.pop('_it', None); c.pop('facts', None)
    B = dict(year=se['year'], week=week, potw=dict(off=[], defense=[], st=[]), cases=cases, rates=[dict(tier=t, mean=m) for t, m in RATES], open=open_storylines(S))
    json.dump(B, open(path, 'w'), indent=1); return B

def open_storylines(S):
    """Public one-liners about matters still open (never the hidden truth)."""
    o = CS.office(S); now = CS.tick(S); out = []
    for sid, st in o['stories'].items():
        out.append(dict(title=st['title'], who=st['name'], club=st['club'], since=f"week {st['week']}, {st['year']}", ruling=st.get('ruling', '')))
    for p in S['players'].values():
        if p.get('inj') and p['inj']['kind'] in CS.UNHEALED and p.get('club'):
            out.append(dict(title=p['inj']['kind'].capitalize(), who=p['name'], club=p['club'], since='', ruling=''))
    return out

# ----------------------------------------------------------------------------- applying Dan's decisions
def apply(S, week, dec):
    se = S['season']; B = json.load(open(f'{ROOT}/data/office/ballot_{se["year"]}_w{week}.json'))
    se.setdefault('discipline', []); se.setdefault('potw', {}); CS.office(S)
    if str(week) in se['potw']: raise SystemExit('decisions for this week were already applied')
    out = []
    cats = {'off': 'Offensive Player of the Week', 'defense': 'Defensive Player of the Week', 'st': 'Special Teams Player of the Week'}
    win = {}
    for k, label in cats.items():
        pid = dec['potw'].get(k)
        if pid is None: continue
        c = next(x for x in B['potw'][k] if x['pid'] == int(pid)); win[k] = dict(pid=c['pid'], name=c['name'], pos=c['pos'], club=c['club'], line=c['line'])
        out.append(f"{label}: {c['name']} ({c['pos']}, {c['club']}) {c['line']}")
    se['potw'][str(week)] = win
    for c in B['cases']:
        d = dec['rulings'].get(c['id'])
        if not d: raise SystemExit(f"missing ruling for {c['id']}")
    for c in B['cases']:
        rec, notes = CS.apply_case(S, week, c, dec['rulings'][c['id']])
        out.append(f"{c['title']}: {', '.join(w['name'] for w in c['who'])} - {rec['ruling']}" + (' (' + '; '.join(notes) + ')' if notes else ''))
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]; S = load(STATE)
    if cmd == 'ballot':
        B = ballot(S, int(sys.argv[2])); save(S, STATE); write_project_state(S, Z64)
        print(json.dumps({'cases': [(c['id'], c['tier'], c['title'], [w['name'] for w in c['who']], c['severity']) for c in B['cases']],
                          'potw': {k: [(x['name'], x['pos'], x['club'].split()[-1], x['line']) for x in v] for k, v in B['potw'].items()}}, indent=1))
    elif cmd == 'offseason':
        B = offseason_ballot(S); save(S, STATE); write_project_state(S, Z64); print([(c['id'], c['title'], [w['name'] for w in c['who']], c['severity']) for c in B['cases']])
    elif cmd == 'apply':
        lines = apply(S, int(sys.argv[2]), json.load(open(sys.argv[3]))); save(S, STATE); write_project_state(S, Z64); print('\n'.join(lines))
