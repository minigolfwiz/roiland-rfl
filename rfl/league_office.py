"""League Office: the weekly between-games desk for Dan.

Two jobs, both decided by Dan before the next week is played:
  1. Players of the Week (offense, defense, special teams) from the week just played.
  2. Disciplinary cases that reach the commissioner's desk. The number and severity are drawn at random from the realistic
     weekly rates below (there is no quota; many weeks have one or none).

Usage:
  python3 rfl/league_office.py ballot N        # build the ballot for the week just played (once; saved to data/office/)
  python3 rfl/league_office.py apply N file    # apply Dan's decisions (json from the page's db doc) to the state
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *
from rfl import discipline as DISC
from rfl.game import PERSONAL_FOULS

# ----------------------------------------------------------------------------- weekly rates (cases per week across the 40-club league)
# Reference: the real NFL hands out hundreds of small fines a year and perhaps 20-40 suspensions (most of them PED or conduct policy).
# Only cases worth the commissioner's attention are drawn here. Expected cases per week and per 20-week season:
RATES = [  # tier, mean per week
    ('minor',    0.90),   # a fine-level matter (about 18 a season)
    ('moderate', 0.25),   # ejection-level conduct, brawls, repeat fines (about 5)
    ('serious',  0.08),   # PED, DUI, firearm: games-missed matters (about 1-2)
    ('major',    0.015),  # serious criminal charges: indefinite-suspension matters (about one every three seasons)
    ('club',     0.02),   # tampering, illegal filming, cap games (about one every two to three seasons)
]
POSW = {  # who is likely to be involved in an on-field case, by position
    'late_hit': {'DL': 5, 'LB': 4, 'S': 2, 'CB': 1}, 'taunt': {'WR': 4, 'TE': 2, 'RB': 2, 'CB': 3, 'DL': 2, 'S': 1, 'LB': 1},
    'defenseless': {'S': 5, 'LB': 3, 'CB': 3}, 'helmet': {'LB': 4, 'S': 4, 'DL': 3, 'CB': 2, 'RB': 1},
    'comments': {'QB': 3, 'WR': 4, 'DL': 2, 'CB': 3, 'RB': 1, 'TE': 1, 'LB': 1, 'S': 1}, 'equip': {p: 1 for p in POS},
    'flagrant': {'S': 5, 'LB': 4, 'DL': 3, 'CB': 2}, 'fight': {'DL': 4, 'OL': 5, 'LB': 3, 'S': 1, 'CB': 1, 'TE': 1},
}
FINES = {'k10': 10000, 'k25': 25000, 'k50': 50000, 'k75': 75000, 'k100': 100000, 'k250': 250000, 'k500': 500000, 'm1': 1000000}

def poisson(rnd, mean):
    L = math.exp(-mean); k = 0; p = 1.0
    while True:
        p *= rnd.random()
        if p <= L: return k
        k += 1

def opt(key, label, games=0, fine=0, status='ok', suggested=False, **kw):
    return dict(key=key, label=label, games=games, fine=fine, status=status, suggested=suggested, **kw)

def money(n): return f"${n // 1000}K" if n < 1000000 else f"${n / 1000000:g}M"

def pick(rnd, d): ks = list(d); return rnd.choices(ks, [d[k] for k in ks])[0]

def eligible(S, club=None, pos=None):
    out = []
    for t, c in S['clubs'].items():
        if club and t != club: continue
        for pid in c['roster']:
            p = S['players'][str(pid)]
            if p.get('status') != 'active' or p.get('inj') or (pos and p['pos'] not in pos): continue
            out.append(p)
    return out

def prior(S, pid): return [d for d in S['season'].get('discipline', []) if d.get('pid') == pid or pid in d.get('pids', [])]

# ----------------------------------------------------------------------------- discipline traits: who ends up on the desk
# Hidden traits (rfl/discipline.py) tilt the odds. Off-field matters (comments, equipment, PED, DUI, firearm, criminal) follow conduct; on-field
# conduct cases follow a blend of on-field discipline and conduct, and are anchored to personal fouls that were actually flagged that week.
# Weights are capped both ways, so the worst-behaved players are likelier but never certain, and clean players keep a real chance.
def lw(S, p, kind='cond'): return DISC.lo_weight(DISC.norms(S), p, kind)
ANCHOR = {'late_hit': ('unnecessary roughness', 'roughing the passer'), 'defenseless': ('roughing the passer', 'unnecessary roughness'),
          'helmet': ('roughing the passer', 'unnecessary roughness'), 'taunt': ('unnecessary roughness',)}
def flagged(S, res, types):
    """(game, penalty) pairs for personal fouls of the given types in the week's games, for players still active and not otherwise unavailable."""
    out = []
    for g in res:
        for x in g.get('pens', []):
            if x['type'] not in types: continue
            p = S['players'].get(str(x['pid']))
            if p and p.get('status') == 'active' and not p.get('inj'): out.append((g, x))
    return out
def _when(x):
    return 'in overtime' if x['q'] == 'OT' else f"with {x['t']} left in the {['first', 'second', 'third', 'fourth'][int(x['q']) - 1]} quarter"
def _flags_note(S, pid):
    n = S['season']['stats'].get(str(pid), {}).get('pen', 0)
    return f" It was his {n}th flag of the season." if n >= 6 else ''

# ----------------------------------------------------------------------------- incident builders
def mk_minor(S, rnd, week, res):
    typ = rnd.choice(['late_hit', 'taunt', 'defenseless', 'helmet', 'comments', 'equip', 'sideline'])
    g = rnd.choice(res); side = rnd.choice(['home', 'away']); club = g[side]; opp = g['away' if side == 'home' else 'home']
    where = f"{g['away']} at {g['home']}, week {week}"
    if typ == 'sideline':
        c = S['clubs'][club]['coach']['name']
        return dict(type=typ, title='Sideline conduct', who=[dict(name=c, pos='HC', club=club, pid=None, coach=True)], game=g['id'], where=where,
                    text=f"Head coach {c} was flagged for berating officials over a no-call and followed it with heated comments on the field after the final whistle.",
                    options=[opt('none', 'No action'), opt('warn', 'Warning'), opt('k25', 'Fine $25K', fine=25000, suggested=True), opt('k50', 'Fine $50K', fine=50000)])
    anchored = None
    if typ in ANCHOR:
        fl = flagged(S, res, ANCHOR[typ])
        if not fl: typ = rnd.choice(['comments', 'equip'])       # nothing was actually flagged this week, so no on-field case is invented
        else:
            ws = [lw(S, S['players'][str(x['pid'])], 'mix') for g_, x in fl]
            g, anchored = rnd.choices(fl, ws)[0]; club = anchored['team']; where = f"{g['away']} at {g['home']}, week {week}"
    if anchored: p = S['players'][str(anchored['pid'])]
    else:
        pool = eligible(S, club, POSW[typ].keys())
        if not pool: return None
        p = rnd.choices(pool, [POSW[typ][q['pos']] * (1.6 if q.get('starter') else 1) * lw(S, q, 'cond') for q in pool])[0]
    pr = prior(S, p['pid'])
    texts = {
        'late_hit': f"{p['name']} ({p['pos']}) drove the quarterback into the turf well after the throw and drew an unnecessary roughness flag.",
        'taunt': f"{p['name']} ({p['pos']}) stood over an opponent and taunted him after a play, drawing a flag and a fine notice.",
        'defenseless': f"{p['name']} ({p['pos']}) hit a receiver in the air before the ball arrived; the officials flagged it as a hit on a defenseless player.",
        'helmet': f"{p['name']} ({p['pos']}) was penalized for helmet-to-helmet contact on a crossing route; the player on the other end stayed in the game.",
        'comments': f"{p['name']} ({p['pos']}) told reporters after the game that the officiating crew 'decided the outcome', in comments that went public the same night.",
        'equip': f"{p['name']} ({p['pos']}) wore non-approved gear on the field after being warned in the pregame check.",
    }
    base = {'late_hit': 'k25', 'taunt': 'k10', 'defenseless': 'k25', 'helmet': 'k25', 'comments': 'k10', 'equip': 'k10'}[typ]
    if anchored:
        flag = anchored['type']
        texts[typ] = {'late_hit': f"{p['name']} ({p['pos']}) was flagged for {flag} {_when(anchored)} on a hit the officials ruled came well after the play was over.",
                      'taunt': f"{p['name']} ({p['pos']}) was flagged for {flag} {_when(anchored)} after standing over an opponent and taunting him.",
                      'defenseless': f"{p['name']} ({p['pos']}) was flagged for {flag} {_when(anchored)} on a hit the officials ruled was on a defenseless player.",
                      'helmet': f"{p['name']} ({p['pos']}) was flagged for {flag} {_when(anchored)} for helmet-to-helmet contact; the player on the other end stayed in the game."}[typ] + _flags_note(S, p['pid'])
    txt = texts[typ] + (f" It is his {['second', 'third', 'fourth'][min(len(pr) - 1, 2)]} case this season. Earlier ruling: {pr[-1]['ruling']}" + (f" (your note: {pr[-1]['note']})" if pr[-1].get('note') else '') + '.' if pr else '')
    sug = base if not pr else ('k50' if base == 'k25' else 'k25')
    return dict(type=typ, title={'late_hit': 'Late hit', 'taunt': 'Taunting', 'defenseless': 'Hit on a defenseless player', 'helmet': 'Helmet-to-helmet contact', 'comments': 'Comments about the officials', 'equip': 'Equipment violation'}[typ],
                who=[dict(name=p['name'], pos=p['pos'], club=club, pid=p['pid'])], game=g['id'], where=where, text=txt, prior=len(pr),
                options=[opt('none', 'No action'), opt('warn', 'Warning')] + [opt(k, f"Fine {money(FINES[k])}", fine=FINES[k], suggested=(k == sug)) for k in ('k10', 'k25', 'k50')])

def mk_moderate(S, rnd, week, res):
    typ = rnd.choice(['flagrant', 'fight', 'fight', 'repeat'])
    g = rnd.choice(res); where = f"{g['away']} at {g['home']}, week {week}"
    if typ == 'fight':
        a = eligible(S, g['home'], POSW['fight'].keys()); b = eligible(S, g['away'], POSW['fight'].keys())
        if not a or not b: return None
        pa = rnd.choices(a, [POSW['fight'][q['pos']] * lw(S, q, 'mix') for q in a])[0]; pb = rnd.choices(b, [POSW['fight'][q['pos']] * lw(S, q, 'mix') for q in b])[0]
        return dict(type='fight', title='Fight and ejections', who=[dict(name=pa['name'], pos=pa['pos'], club=g['home'], pid=pa['pid']), dict(name=pb['name'], pos=pb['pos'], club=g['away'], pid=pb['pid'])],
                    game=g['id'], where=where, pids=[pa['pid'], pb['pid']],
                    text=f"A scrum after a goal-line stand turned into a fight. {pa['name']} ({g['home'].split()[-1]}) and {pb['name']} ({g['away'].split()[-1]}) were ejected, and the benches cleared briefly. The ruling applies to both players.",
                    options=[opt('none', 'No action'), opt('k25', 'Fine each $25K', fine=25000), opt('k50', 'Fine each $50K', fine=50000, suggested=True), opt('g1', 'Each sits 1 game + $25K', games=1, fine=25000)])
    if typ == 'repeat':
        cand = [d for d in S['season'].get('discipline', []) if d.get('pid') and d.get('fine') and not d.get('games')]
        if not cand: return None
        d = rnd.choices(cand, [lw(S, S['players'][str(x['pid'])], 'mix') if str(x['pid']) in S['players'] else 1 for x in cand])[0]; p = S['players'].get(str(d['pid']))
        if not p or p.get('inj') or p.get('status') != 'active': return None
        return dict(type='repeat', title='Repeat offender', who=[dict(name=p['name'], pos=p['pos'], club=p['club'], pid=p['pid'])], game=g['id'], where=where,
                    text=f"{p['name']} ({p['pos']}) has now been fined {len(prior(S, p['pid'])) + 1} times this season for conduct on the field. The league office has asked for a ruling on whether the fines are working.", prior=len(prior(S, p['pid'])),
                    options=[opt('none', 'No action'), opt('k75', 'Fine $75K', fine=75000), opt('g1', '1 game + $50K', games=1, fine=50000, suggested=True), opt('g2', '2 games', games=2)])
    fl = [(g_, x) for g_, x in flagged(S, res, PERSONAL_FOULS) if x['pos'] in POSW['flagrant']]
    if fl:      # a flagrant case grows out of a personal foul that was actually flagged this week
        g, x = rnd.choices(fl, [lw(S, S['players'][str(x_['pid'])], 'mix') for g_, x_ in fl])[0]; club = x['team']; p = S['players'][str(x['pid'])]; where = f"{g['away']} at {g['home']}, week {week}"
        why = f"was flagged for {x['type']} {_when(x)} and ejected after a review of a hit to the head of a defenseless quarterback."
    else:
        side = rnd.choice(['home', 'away']); club = g[side]
        pool = eligible(S, club, POSW['flagrant'].keys())
        if not pool: return None
        p = rnd.choices(pool, [POSW['flagrant'][q['pos']] * lw(S, q, 'mix') for q in pool])[0]
        why = "was ejected for a hit to the head of a defenseless quarterback."
    return dict(type='flagrant', title='Flagrant hit, ejection', who=[dict(name=p['name'], pos=p['pos'], club=club, pid=p['pid'])], game=g['id'], where=where,
                text=f"{p['name']} ({p['pos']}) {why} The opposing player left the game and returned later." + _flags_note(S, p['pid']),
                options=[opt('none', 'No action'), opt('k50', 'Fine $50K', fine=50000), opt('k75', 'Fine $75K', fine=75000), opt('g1', '1 game + $25K', games=1, fine=25000, suggested=True), opt('g2', '2 games', games=2)])

def mk_serious(S, rnd, week, res):
    typ = rnd.choice(['ped', 'ped', 'dui', 'firearm'])
    pool = eligible(S)
    p = rnd.choices(pool, [(1.5 if q.get('starter') else 1) * lw(S, q, 'cond') for q in pool])[0]; who = [dict(name=p['name'], pos=p['pos'], club=p['club'], pid=p['pid'])]
    if typ == 'ped':
        return dict(type='ped', title='Performance-enhancing substance', who=who, where='League drug-testing program',
                    text=f"{p['name']} ({p['pos']}, {p['club'].split()[-1]}) tested positive for a banned substance. He says the source was an over-the-counter supplement. The program's first-offense range is 2 to 6 games.",
                    options=[opt('g2', '2 games', games=2), opt('g4', '4 games', games=4, suggested=True), opt('g6', '6 games', games=6), opt('g8', '8 games', games=8)])
    if typ == 'dui':
        return dict(type='dui', title='Arrest, driving under the influence', who=who, where='Off the field',
                    text=f"{p['name']} ({p['pos']}, {p['club'].split()[-1]}) was arrested early Tuesday for driving under the influence. The club has issued a short statement and says it is cooperating with the league.",
                    options=[opt('k100', 'Fine $100K', fine=100000), opt('g1', '1 game + $100K', games=1, fine=100000, suggested=True), opt('g2', '2 games + $100K', games=2, fine=100000), opt('g4', '4 games', games=4)])
    return dict(type='firearm', title='Firearm at the facility', who=who, where='Club facility',
                text=f"{p['name']} ({p['pos']}, {p['club'].split()[-1]}) brought a licensed firearm into the team facility in violation of league policy. The club reported it to the league itself.",
                options=[opt('k100', 'Fine $100K', fine=100000), opt('g1', '1 game + $100K', games=1, fine=100000, suggested=True), opt('g2', '2 games', games=2), opt('g4', '4 games', games=4)])

def mk_major(S, rnd, week, res):
    pool = eligible(S); p = rnd.choices(pool, [(2 if q.get('starter') else 1) * lw(S, q, 'cond') for q in pool])[0]
    return dict(type='criminal', title='Criminal charges', who=[dict(name=p['name'], pos=p['pos'], club=p['club'], pid=p['pid'])], where='Off the field',
                text=f"Prosecutors have filed serious criminal charges against {p['name']} ({p['pos']}, {p['club'].split()[-1]}). The club says it is gathering facts. Under the conduct policy the league can act before the case is resolved.",
                options=[opt('none', 'No action while the case proceeds'), opt('exempt', 'Exempt list: out until the case resolves', games=99, suggested=True), opt('g6', '6 games pending review', games=6), opt('indef', 'Suspended indefinitely', games=99, status='indef')])

def mk_club(S, rnd, week, res):
    t = rnd.choice(list(S['clubs'])); c = S['clubs'][t]
    typ = rnd.choice(['tamper', 'filming', 'cap'])
    txt = {'tamper': f"The {t} are accused of contacting a player under contract with another club before the window opened. The league's investigators say they have text records.",
           'filming': f"A video staffer for the {t} was found filming an opponent's walkthrough from an unauthorized spot. The club says it was a mistake by one employee.",
           'cap': f"The league found that the {t} paid a player through a side arrangement that was not reported to the cap office. GM {c['gm']['name']} says it was a paperwork error."}[typ]
    return dict(type=typ, title={'tamper': 'Tampering', 'filming': 'Illegal filming', 'cap': 'Undisclosed payment'}[typ], who=[dict(name=t, pos='CLUB', club=t, pid=None, club_level=True)], where='League investigation', text=txt,
                options=[opt('none', 'No action'), opt('k250', 'Fine club $250K', fine=250000), opt('k500p', 'Fine $500K + lose a 4th-round pick', fine=500000, pick_round=4, suggested=True), opt('m1p', 'Fine $1M + lose a 2nd-round pick', fine=1000000, pick_round=2)])

BUILD = {'minor': mk_minor, 'moderate': mk_moderate, 'serious': mk_serious, 'major': mk_major, 'club': mk_club}

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
    res = se['results'][str(week)]
    rnd = random.Random(f"league-office-{se['year']}-{week}")
    cases = []
    for tier, mean in RATES:
        for _ in range(poisson(rnd, mean)):
            for _try in range(6):
                c = BUILD[tier](S, rnd, week, res)
                if c: break
            if not c: continue
            c.update(id=f"W{week}-{len(cases) + 1}", tier=tier, week=week); cases.append(c)
    sev = {'major': 0, 'serious': 1, 'club': 2, 'moderate': 3, 'minor': 4}
    cases.sort(key=lambda c: sev[c['tier']])
    for i, c in enumerate(cases): c['id'] = f"W{week}-{i + 1}"
    B = dict(year=se['year'], week=week, potw=potw(S, week, res), cases=cases, rates=[dict(tier=t, mean=m) for t, m in RATES])
    os.makedirs(f'{ROOT}/data/office', exist_ok=True)
    path = f'{ROOT}/data/office/ballot_{se["year"]}_w{week}.json'
    if os.path.exists(path): raise SystemExit(f'ballot already exists: {path} (never re-draw a ballot)')
    json.dump(B, open(path, 'w'), indent=1); return B

# ----------------------------------------------------------------------------- applying Dan's decisions
def span_for_games(S, club, week, n):
    """Calendar weeks that cover n games of `club` after `week` (byes burn a week)."""
    if n >= 99: return 99
    cnt = 0
    for w in range(week + 1, 21):
        if any(g['host'] == club or g['visitor'] == club for g in S['season']['schedule'][str(w)]): cnt += 1
        if cnt == n: return w - week
    return 99

def apply(S, week, dec):
    se = S['season']; B = json.load(open(f'{ROOT}/data/office/ballot_{se["year"]}_w{week}.json'))
    se.setdefault('discipline', []); se.setdefault('potw', {})
    if str(week) in se['potw']: raise SystemExit('decisions for this week were already applied')
    P = S['players']; out = []
    cats = {'off': 'Offensive Player of the Week', 'defense': 'Defensive Player of the Week', 'st': 'Special Teams Player of the Week'}
    win = {}
    for k, label in cats.items():
        pid = dec['potw'].get(k)
        if pid is None: continue
        c = next(x for x in B['potw'][k] if x['pid'] == int(pid)); win[k] = dict(pid=c['pid'], name=c['name'], pos=c['pos'], club=c['club'], line=c['line'])
        out.append(f"{label}: {c['name']} ({c['pos']}, {c['club']}) {c['line']}")
    se['potw'][str(week)] = win
    for c in B['cases']:
        d = dec['rulings'].get(c['id']);
        if not d: raise SystemExit(f"missing ruling for {c['id']}")
        o = next(x for x in c['options'] if x['key'] == d['key'])
        rec = dict(week=week, id=c['id'], tier=c['tier'], type=c['type'], title=c['title'], who=[w['name'] for w in c['who']], clubs=[w['club'] for w in c['who']],
                   pid=c['who'][0]['pid'], pids=[w['pid'] for w in c['who'] if w['pid']], ruling=o['label'], key=o['key'], fine=o['fine'], games=o['games'], note=d.get('note', ''))
        for w in c['who']:
            if not w.get('pid') or not o['games']: continue
            p = P[str(w['pid'])]; span = span_for_games(S, w['club'], week, o['games'])
            p['inj'] = {'weeks': span, 'kind': 'suspended' if o['games'] < 99 else 'suspended indefinitely'}
            se['injuries_log'].append(dict(week=week, team=w['club'], pid=p['pid'], name=p['name'], pos=p['pos'], weeks=span, kind=p['inj']['kind']))
        if o.get('pick_round'):
            S.setdefault('pick_penalties', []).append(dict(club=c['who'][0]['club'], round=o['pick_round'], draft=se['year'] + 1, week=week, reason=c['title']))
        if o['key'] not in ('none', 'warn'):
            for w in c['who']:
                if w.get('pid'): DISC.mark_case(P[str(w['pid'])], c['tier'], o['games'], random.Random(f"mark|{c['id']}|{se['year']}"))
        se['discipline'].append(rec)
        out.append(f"{c['title']}: {', '.join(w['name'] for w in c['who'])} - {o['label']}")
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]; S = load(STATE)
    if cmd == 'ballot':
        B = ballot(S, int(sys.argv[2])); print(json.dumps({'cases': [(c['id'], c['tier'], c['title'], [w['name'] for w in c['who']]) for c in B['cases']],
                                                           'potw': {k: [(x['name'], x['pos'], x['club'].split()[-1], x['line']) for x in v] for k, v in B['potw'].items()}}, indent=1))
    elif cmd == 'apply':
        lines = apply(S, int(sys.argv[2]), json.load(open(sys.argv[3]))); save(S, STATE); write_project_state(S, Z64); print('\n'.join(lines))
