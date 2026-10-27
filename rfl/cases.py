"""League Office case engine (Dan, 27 Oct 2026): fact-rolled cases, severity 1-10, option ladders built around severity, precedent, probation,
appeals, multi-week storylines with hidden truths, reinstatement reviews, and a felony policy much harsher than the real NFL's.

State kept in S['office'] (persisted with the rest of the state, never put on the page):
  history  : every ruling (for precedent, repeat-offender checks, appeals)
  pending  : stage-1 storyline data for the current ballot, keyed by case id (hidden truths live here)
  stories  : open storylines after Dan has ruled (hidden truth + due tick)
  due      : follow-ups waiting for a week (findings, court/felony resolutions, reinstatement reviews, appeals)
  sigs     : fingerprints of every case ever drawn (the uniqueness guard)
"""
import random, math, re, json, os, collections
from rfl import case_catalog as CC
from rfl.case_catalog import CATALOG, FELONY, FELONY_CUES
from rfl import discipline as DISC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAMS = json.load(open(f'{ROOT}/data/league.json'))['teams']
WEEKS = 20
PLAYOFF_HEALS = 4          # heal() also runs once per playoff round
OFFSEASON_HEAL = 30        # offseason.progress() takes 30 weeks off every injury
UNHEALED = ('suspended indefinitely', 'exempt list')

# ----------------------------------------------------------------------------------------------------------------------------- small utilities
def tick(S, week=None):
    se = S['season']; return se['year'] * WEEKS + (se['week_done'] if week is None else week)
def _brand_nicks():
    try:
        h = open(f'{ROOT}/out/season_template.html', encoding='utf-8').read(); i = h.index('const BRAND = ') + len('const BRAND = ')
        return {k: v['nick'] for k, v in json.JSONDecoder().raw_decode(h, i)[0].items()}
    except Exception: return {}
NICKS = _brand_nicks()
def nick(club): return NICKS.get(club) or club.split()[-1]
def money(n): return f"${n // 1000}K" if n < 1000000 else f"${n / 1000000:g}M"
def clamp(x, a, b): return max(a, min(b, x))
NICE_FINES = [5, 10, 15, 25, 40, 50, 75, 100, 150, 250, 350, 500, 750, 1000, 1500]
def nice(v):
    k = v / 1000; return min(NICE_FINES, key=lambda n: abs(math.log(n / max(k, 1))))* 1000
def fine_for(sev): return nice(8000 * 1.6 ** (sev - 1))
def cap_word(s): return s[:1].upper() + s[1:] if s else s
def sev_word(s): return 'low' if s < 3.5 else ('moderate' if s < 5.5 else ('high' if s < 7.5 else 'severe'))
class SafeDict(dict):
    def __missing__(self, k): return '{' + k + '}'
def fmt(t, ctx):
    s = re.sub(r'  +', ' ', t.format_map(SafeDict(ctx)))
    return re.sub(r'\b([Aa]) (?=(?:[aeio]|u(?!ni))\w)', lambda m: m.group(1) + 'n ', s)
OFFICIALS = ['Marek Delvanne', 'Ruth Ozolins', 'Tobias Quillfeather', 'Anneliese Brandt', 'Corwin Teague', 'Isidro Valmont', 'Petra Hollowell', 'Gideon Marsh', 'Yusra Penhaligon', 'Lowell Dresden']
REPORTERS = ['Hana Voskuijlen', 'Dmitri Aldersgate', 'Camille Rourke-Bell', 'Teodor Maximilian', 'Odalys Finch', 'Brannock Yee']
AGENTS = ['Sol Terrance', 'Imogen Valdez', 'Rafferty Ng', 'Dalia Okonkwo-Pryce', 'Harlan Quist', 'Beatrix Lund']
SUBST = ['an anabolic agent', 'a stimulant on the banned list', 'a diuretic that is on the banned list', 'a banned peptide', 'a steroid metabolite', 'a banned growth agent']
DOW = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']
ORD = ['first', 'second', 'third', 'fourth']
POSW = {'late_hit': {'DL': 5, 'LB': 4, 'S': 2, 'CB': 1}, 'taunt': {'WR': 4, 'TE': 2, 'RB': 2, 'CB': 3, 'DL': 2, 'S': 1, 'LB': 1},
        'defenseless': {'S': 5, 'LB': 3, 'CB': 3}, 'helmet': {'LB': 4, 'S': 4, 'DL': 3, 'CB': 2, 'RB': 1},
        'comments': {'QB': 3, 'WR': 4, 'DL': 2, 'CB': 3, 'RB': 1, 'TE': 1, 'LB': 1, 'S': 1}, 'flagrant': {'S': 5, 'LB': 4, 'DL': 3, 'CB': 2},
        'fight': {'DL': 4, 'OL': 5, 'LB': 3, 'S': 1, 'CB': 1, 'TE': 1}, 'bench_clear': {'DL': 3, 'OL': 4, 'LB': 3, 'S': 2, 'CB': 2, 'WR': 2},
        'social': {'WR': 4, 'QB': 2, 'CB': 3, 'RB': 2, 'DL': 2, 'LB': 1, 'S': 1, 'TE': 1}}
VICTIM_POS = {'roughing the passer': ('QB',), 'unnecessary roughness': ('QB', 'RB', 'WR', 'TE', 'CB', 'S', 'LB')}

# ----------------------------------------------------------------------------------------------------------------------------- office state
def office(S):
    """The persistent store. First call also backfills history from the earlier ledger of rulings (so 2043 cases count as precedent)."""
    o = S.setdefault('office', dict(history=[], pending={}, stories={}, due=[], sigs=[], backfilled=False))
    if not o['backfilled']:
        se = S['season']
        for d in se.get('discipline', []):
            spec = CATALOG.get(d['type'])
            sev = {'minor': 2.8, 'moderate': 5.0, 'serious': 5.2, 'major': 8.0, 'club': 5.0}.get(d['tier'], 3.0) if not spec else spec['base']
            g = d.get('games', 0)
            if g and spec: sev = clamp(sev + (g - 1) * .35, 1, 10)
            yr = d.get('year', se['year']); o['history'].append(dict(tick=yr * WEEKS + d['week'], year=yr, week=d['week'], id=d['id'], type=d['type'], tier=d['tier'], title=d['title'], sev=round(sev, 1),
                                     key=d['key'], label=d['ruling'], games=d.get('games', 0), fine=d.get('fine', 0), pid=d.get('pid'), pids=d.get('pids', []), club=(d.get('clubs') or [None])[0], name=(d.get('who') or [''])[0]))
        # open-ended suspensions from before the case system get a review date
        for p in S['players'].values():
            inj = p.get('inj')
            if inj and inj['kind'] == 'suspended indefinitely' and not p.get('indef'):
                rec = next((h for h in reversed(o['history']) if h.get('pid') == p['pid']), None)
                since = rec['tick'] if rec else tick(S)
                p['indef'] = dict(since=since, min_games=16, case=rec['id'] if rec else None)
                o['due'].append(dict(tick=max(since + 16, tick(S) + 1), kind='review', pid=p['pid']))
        o['backfilled'] = True
    return o

def open_pids(S):
    o = office(S); out = set()
    for s in list(o['stories'].values()) + list(o['pending'].values()):
        out.update(s.get('pids', []))
    return out

def span_for_games(S, club, week, n):
    """Calendar weeks that cover n of the club's games after `week` (byes burn a week). Games past the end of the season carry over."""
    cnt = 0
    for w in range(week + 1, WEEKS + 1):
        if any(g['host'] == club or g['visitor'] == club for g in S['season']['schedule'].get(str(w), [])): cnt += 1
        if cnt == n: return w - week
    return (WEEKS - week) + PLAYOFF_HEALS + OFFSEASON_HEAL + (n - cnt)

# ----------------------------------------------------------------------------------------------------------------------------- subjects
def lw(S, p, kind='cond'): return DISC.lo_weight(DISC.norms(S), p, kind)
def _who(p, club): return dict(name=p['name'], pos=p['pos'], club=club, pid=p['pid'])
def eligible(S, club=None, pos=None, used=()):
    out = []; blocked = open_pids(S)
    for t, c in S['clubs'].items():
        if club and t != club: continue
        for pid in c['roster']:
            p = S['players'][str(pid)]
            if p.get('status') != 'active' or p.get('inj') or p['pid'] in used or p['pid'] in blocked or (pos and p['pos'] not in pos): continue
            out.append(p)
    return out
def wpick(rnd, S, pool, posw=None, kind='cond', star=1.5):
    ws = [(posw.get(q['pos'], 0) if posw else 1) * (star if q.get('starter') else 1) * lw(S, q, kind) for q in pool]
    if not any(ws): return None
    return rnd.choices(pool, ws)[0]

def base_ctx(S, rnd, club=None):
    c = dict(official=rnd.choice(OFFICIALS), reporter=rnd.choice(REPORTERS), agent=rnd.choice(AGENTS), dow=rnd.choice(DOW), subst=rnd.choice(SUBST))
    if club:
        cl = S['clubs'][club]; c.update(club=club, nick=nick(club), coach=cl['coach']['name'], gm=cl['gm']['name'])
    return c
def when_of(x):
    return 'in overtime' if x['q'] == 'OT' else f"with {x['t']} left in the {ORD[int(x['q']) - 1]} quarter"

def flagged(S, res, types, used=()):
    out = []; blocked = open_pids(S)
    for g in res:
        for x in g.get('pens', []):
            if x['type'] not in types: continue
            p = S['players'].get(str(x['pid']))
            if p and p.get('status') == 'active' and not p.get('inj') and p['pid'] not in used and p['pid'] not in blocked: out.append((g, x))
    return out

def subject(S, rnd, spec, week, res, used, key):
    """-> (who list, game id or None, where, ctx, pids) or None. ctx carries everything the text templates need."""
    kind = spec['subject']; tier = spec['tier']
    if kind in ('flag', 'flag_injury'):
        fl = flagged(S, res, spec['anchor'], used)
        if kind == 'flag_injury':       # only a play with a real injury to an opponent in that game
            fl = [(g, x) for g, x in fl if any(i['team'] != x['team'] for i in g['injuries'])]
        if not fl: return None
        g, x = rnd.choices(fl, [lw(S, S['players'][str(x_['pid'])], 'mix') * (1.0 + .05 * S['season']['stats'].get(str(x_['pid']), {}).get('pen', 0)) for g_, x_ in fl])[0]
        p = S['players'][str(x['pid'])]; club = x['team']; oppc = g['away'] if club == g['home'] else g['home']
        ctx = base_ctx(S, rnd, club); ctx.update(name=p['name'], last=p['name'].split()[-1], pos=p['pos'], opp=nick(oppc), oppclub=oppc, flag=x['type'], when=when_of(x), onick=nick(oppc), game=g['id'])
        injs = [i for i in g['injuries'] if i['team'] == oppc]
        want = VICTIM_POS[x['type']]
        victim = None
        for i in injs:        # a real injury to an opponent in this game is the victim when the position fits
            if i['pos'] in want or kind == 'flag_injury':
                victim = S['players'][str(i['pid'])]; ctx.update(inj_kind=i['kind'] if re.search(r'sprain|strain|tear|fracture|concussion|dislocation|injury|broken', i['kind']) else i['kind'] + ' injury', inj_weeks=i['weeks'], weeks_word='week' if i['weeks'] == 1 else 'weeks'); break
        if not victim:
            cand = [S['players'][str(pid)] for pid, v in g['stats']['H' if oppc == g['home'] else 'A'].items() if S['players'][str(pid)]['pos'] in want and (v.get('att') or v.get('car') or v.get('rec') or v.get('tkl') or v.get('sacks'))]
            victim = rnd.choice(cand) if cand else None
        if not victim: return None
        ctx.update(victim=victim['name'], vlast=victim['name'].split()[-1], vpos=victim['pos'], pids_extra=[victim['pid']])
        return [_who(p, club)], g['id'], f"{g['away']} at {g['home']}, week {week}", ctx, [p['pid']]
    if kind == 'duel':
        g = rnd.choice(res); pw = POSW[key]
        a = wpick(rnd, S, eligible(S, g['home'], pw, used), pw, 'mix'); b = wpick(rnd, S, eligible(S, g['away'], pw, used), pw, 'mix')
        if not a or not b: return None
        ctx = base_ctx(S, rnd, g['home']); q = rnd.choice([2, 3, 4])
        ctx.update(name=a['name'], last=a['name'].split()[-1], pos=a['pos'], nick=nick(g['home']), other=b['name'], opos=b['pos'], othernick=nick(g['away']), when2=f"in the {ORD[q - 1]} quarter", game=g['id'], opp=nick(g['away']))
        return [_who(a, g['home']), _who(b, g['away'])], g['id'], f"{g['away']} at {g['home']}, week {week}", ctx, [a['pid'], b['pid']]
    if kind == 'player':
        pw = POSW.get(key)
        if tier == 'minor' or tier == 'moderate':
            g = rnd.choice(res); side = rnd.choice(['home', 'away']); club = g[side]; oppc = g['away' if side == 'home' else 'home']
            pool = eligible(S, club, pw.keys() if pw else None, used); p = wpick(rnd, S, pool, pw, 'cond')
            if not p: return None
            ctx = base_ctx(S, rnd, club); ctx.update(name=p['name'], last=p['name'].split()[-1], pos=p['pos'], opp=nick(oppc), oppclub=oppc, onick=nick(oppc), game=g['id'])
            return [_who(p, club)], g['id'], f"{g['away']} at {g['home']}, week {week}", ctx, [p['pid']]
        pool = eligible(S, None, None, used); p = wpick(rnd, S, pool, None, 'cond')
        if not p: return None
        ctx = base_ctx(S, rnd, p['club']); ctx.update(name=p['name'], last=p['name'].split()[-1], pos=p['pos'])
        return [_who(p, p['club'])], None, 'Off the field' if key not in ('ped',) else 'League drug-testing program', ctx, [p['pid']]
    if kind in ('coach', 'gm'):
        g = rnd.choice(res); club = g[rnd.choice(['home', 'away'])]; oppc = g['away' if club == g['home'] else 'home']; cl = S['clubs'][club]
        person = cl['coach'] if kind == 'coach' else cl['gm']
        ctx = base_ctx(S, rnd, club); ctx.update(name=person['name'], last=person['name'].split()[-1], opp=nick(oppc), oppclub=oppc, game=g['id'])
        return [dict(name=person['name'], pos='HC' if kind == 'coach' else 'GM', club=club, pid=None, coach=True)], g['id'], f"{g['away']} at {g['home']}, week {week}", ctx, []
    if kind == 'club':
        g = rnd.choice(res); club = g[rnd.choice(['home', 'away'])]; oppc = g['away' if club == g['home'] else 'home']
        ctx = base_ctx(S, rnd, club); ctx.update(name=club, last=nick(club), opp=nick(oppc), oppclub=oppc, game=g['id'])
        return [dict(name=club, pos='CLUB', club=club, pid=None, club_level=True)], g['id'], 'League investigation', ctx, []
    return None

# ----------------------------------------------------------------------------------------------------------------------------- fact rolls
def roll_facts(rnd, facts, ctx, sev, cap_sentences=5):
    chosen = []; groups = set()
    for f in facts:
        if f['grp'] in groups: continue
        if f['req'] and not f['req'](ctx): continue
        p = f['p'](ctx) if callable(f['p']) else f['p']
        if rnd.random() >= p: continue
        groups.add(f['grp']); chosen.append(f)
        sev += f['ds'](ctx) if callable(f['ds']) else f['ds']
    return chosen, sev

def history_for(S, pid, club=None, within=60):
    t = tick(S); o = office(S)
    return [h for h in o['history'] if pid is not None and (h.get('pid') == pid or pid in h.get('pids', [])) and t - h['tick'] <= within]

def history_lines(rec):
    return f"{rec['title']} ({rec['year']}, week {rec['week']}): {rec['label']}"

def precedent_for(S, spec_type, sev, pid, club=None, n=3):
    t = tick(S); o = office(S)
    cand = [h for h in o['history'] if h['type'] == spec_type and t - h['tick'] <= 60 and abs(h['sev'] - sev) <= 1.3 and not (pid is not None and h.get('pid') == pid)]
    cand.sort(key=lambda h: (abs(h['sev'] - sev), -h['tick']))
    return cand[:n]

# ----------------------------------------------------------------------------------------------------------------------------- options
def O(key, label, games=0, fine=0, status='ok', sug=False, blurb='', **eff):
    return dict(key=key, label=label, games=games, fine=fine, status=status, suggested=sug, blurb=blurb, **eff)
def glabel(games, fine=0, extra=''):
    parts = []
    if games: parts.append(f"{games} game{'s' if games != 1 else ''}")
    if fine: parts.append(money(fine) if games else f"Fine {money(fine)}")
    s = ' + '.join(parts) if parts else 'No action'
    return s + (f" + {extra}" if extra else '')
def blurb_of(o):
    b = []
    if o['games'] and o['games'] < 99 and o['status'] == 'ok': b.append(f"Out {o['games']} game{'s' if o['games'] != 1 else ''}")
    if o.get('fine'): b.append(f"fined {money(o['fine'])}")
    if o.get('program'): b.append('conduct program')
    if o.get('probation'): b.append('one year of probation')
    if o.get('coach_games'): b.append(f"coach off the sideline {o['coach_games']} game{'s' if o['coach_games'] != 1 else ''}")
    if o.get('pick_round'): b.append(f"loses a round {o['pick_round']} pick")
    if o.get('ban'): b.append('permanent ban')
    if o.get('indef_min'): b.append(f"out indefinitely, review after {o['indef_min']} games")
    if o.get('exempt'): b.append('exempt list until resolved')
    return (b[0][0].upper() + b[0][1:] + (', ' + ', '.join(b[1:]) if len(b) > 1 else '')) if b else 'No penalty'

def _dedupe(opts):
    seen = set(); out = []
    for o in opts:
        if o['key'] in seen: continue
        seen.add(o['key']); out.append(o)
    return out
def games_for(sev, lo=3.8, step=1.1, top=6): return int(clamp(round((sev - lo) / step), 0, top))

def ladder(kind, sev, facts, ctx, spec):
    ids = {f['id'] for f in facts}; opts = [O('none', 'No action')]
    if kind == 'fine':
        opts.append(O('warn', 'Warning'))
        for d, tag in ((-1.6, 'a'), (0, 'b'), (1.6, 'c')):
            fv = fine_for(clamp(sev + d, 1, 10)); opts.append(O(f"k{fv // 1000}", f"Fine {money(fv)}", fine=fv, sug=(d == 0 and sev > 1.9)))
        if sev >= 6.2: opts.append(O('g1', f"1 game + {money(fine_for(sev))}", games=1, fine=fine_for(sev)))
        if sev <= 1.9: opts[1]['suggested'] = True
    elif kind == 'disc':
        n = games_for(sev)
        if n == 0: opts.append(O('warn', 'Warning'))
        fv = fine_for(sev - 1)
        opts.append(O(f"k{fine_for(sev - 2) // 1000}", f"Fine {money(fine_for(sev - 2))}", fine=fine_for(sev - 2)))
        for g in sorted({max(1, n - 1), max(1, n), n + 1, n + 2}):
            opts.append(O(f"g{g}", glabel(g, fv if g <= 3 else 0), games=g, fine=fv if g <= 3 else 0, sug=(g == max(1, n))))
    elif kind == 'ped':
        g = int(clamp(round(.9 * sev - .5), 2, 20))
        if 'second' in ids: g = max(g, 10)
        if 'masking' in ids: g += 2
        opts = []
        for gg in sorted({max(2, g - 2), g, g + 2, g + 4}):
            opts.append(O(f"g{gg}", f"{gg} games", games=gg, sug=(gg == g)))
        gp = O(f"g{g}p", f"{g} games + counseling and testing program", games=g, program=True, blurb='')
        if 'cooperating' in ids or 'admits' in ids:
            for o in opts: o['suggested'] = False
            gp['suggested'] = True
        opts.insert(2, gp)
        if 'second' in ids or sev >= 8.5: opts.append(O('indef16', 'Suspended indefinitely, review after 16 games', games=99, status='indef', indef_min=16))
    elif kind == 'conduct':
        n = games_for(sev, 3.2, 1.0, 10); fv = fine_for(sev)
        prog = spec['id'] in ('dui', 'assault_misd', 'firearm', 'reckless')
        opts.append(O(f"k{fv // 1000}", f"Fine {money(fv)}", fine=fv))
        if prog: opts.append(O(f"k{fv // 1000}p", f"Fine {money(fv)} + conduct program", fine=fv, program=True))
        for g in sorted({max(1, n - 1), max(1, n), n + 2, n + 4}):
            opts.append(O(f"g{g}", glabel(g, fv), games=g, fine=fv, program=prog and g >= 2, sug=(g == max(1, n))))
        if sev >= 6.8: opts.append(O(f"g{max(1, n)}pr", glabel(max(1, n), fv, 'probation'), games=max(1, n), fine=fv, program=prog, probation=True))
        if sev >= 8.6: opts.append(O('indef16', 'Suspended indefinitely, review after 16 games', games=99, status='indef', indef_min=16))
        if n == 0: opts[1]['suggested'] = True
    elif kind == 'coach':
        person_gm = spec['subject'] == 'gm'
        fv = fine_for(sev) * 2 if not person_gm else fine_for(sev) * 3
        opts.append(O('warn', 'Warning'))
        opts.append(O(f"k{nice(fv * .6) // 1000}", f"Fine {money(nice(fv * .6))}", fine=nice(fv * .6)))
        opts.append(O(f"k{nice(fv) // 1000}", f"Fine {money(nice(fv))}", fine=nice(fv), sug=True))
        opts.append(O(f"k{nice(fv * 1.8) // 1000}", f"Fine {money(nice(fv * 1.8))}", fine=nice(fv * 1.8)))
        if not person_gm and sev >= 5.2: opts.append(O('cg1', f"Fine {money(nice(fv))} + off the sideline 1 game", fine=nice(fv), coach_games=1))
        if not person_gm and sev >= 7: opts.append(O('cg2', f"Fine {money(nice(fv * 1.8))} + off the sideline 2 games", fine=nice(fv * 1.8), coach_games=2))
        if sev < 2.4: opts[1]['suggested'] = True; opts[3]['suggested'] = False
    elif kind == 'club':
        fv = nice(fine_for(sev) * 6); r = lambda s: int(clamp(round(9 - s), 1, 6))
        opts.append(O(f"k{fv // 1000}", f"Fine club {money(fv)}", fine=fv, sug=sev < 4.8))
        if sev >= 3.5: opts.append(O(f"k{nice(fv * 1.5) // 1000}p{r(sev)}", f"Fine {money(nice(fv * 1.5))} + lose a round {r(sev)} pick", fine=nice(fv * 1.5), pick_round=r(sev), sug=4.8 <= sev < 7.2))
        if sev >= 5: opts.append(O(f"k{nice(fv * 2.5) // 1000}p{r(sev + 1.6)}", f"Fine {money(nice(fv * 2.5))} + lose a round {r(sev + 1.6)} pick", fine=nice(fv * 2.5), pick_round=r(sev + 1.6), sug=sev >= 7.2))
        if sev >= 6.5 or ids & {'coach_aware', 'gm_aware', 'intent'}:
            cg = 2 if sev < 8 else 3
            opts.append(O(f"k{nice(fv * 2.5) // 1000}p{r(sev + 1.6)}c{cg}", f"Fine {money(nice(fv * 2.5))} + round {r(sev + 1.6)} pick + coach off the sideline {cg} games", fine=nice(fv * 2.5), pick_round=r(sev + 1.6), coach_games=cg))
    opts = _dedupe(opts)
    if not any(o['suggested'] for o in opts):
        mid = [o for o in opts if o['key'] not in ('none', 'warn')]
        if mid: mid[min(len(mid) - 1, 1)]['suggested'] = True
        else: opts[-1]['suggested'] = True
    for o in opts: o['blurb'] = blurb_of(o)
    return opts

def anchor_to_precedent(opts, prec, repeat):
    """Move the suggested flag to the option closest to what earlier, similar rulings did (a repeat offender goes one step harsher)."""
    if len(prec) < 2: return None
    gs = sorted(p['games'] for p in prec); fs = sorted(p['fine'] for p in prec)
    mg, mf = gs[len(gs) // 2], fs[len(fs) // 2]
    real = [o for o in opts if o['games'] < 99]
    best = min(real, key=lambda o: (abs(o['games'] - mg), abs(o['fine'] - mf)))
    if repeat:
        harsher = [o for o in real if (o['games'], o['fine']) > (best['games'], best['fine'])]
        if harsher: best = min(harsher, key=lambda o: (o['games'], o['fine']))
    for o in opts: o['suggested'] = (o is best)
    return best['key']

# ----------------------------------------------------------------------------------------------------------------------------- building a new case
def sigs_of(S): return set(office(S)['sigs'])
def build_case(S, rnd, key, week, res, used):
    """Build one new case of type `key`. Returns (case, story) or None. `story` is hidden data to store (never put on the page)."""
    spec = dict(CATALOG[key], id=key)
    if spec.get('felony'): return build_felony(S, rnd, key, spec, week, res, used)
    sub = subject(S, rnd, spec, week, res, used, key)
    if not sub: return None
    who, game, where, ctx, pids = sub
    pid = pids[0] if pids else None
    seen = sigs_of(S)
    for attempt in range(14):
        r2 = random.Random(rnd.random())
        op = r2.randrange(len(spec['openers']))
        facts, sev = roll_facts(r2, spec['factors'], ctx, spec['base'])
        sig = f"{key}|{who[0]['name']}|{op}|{'.'.join(sorted(f['id'] for f in facts))}|{round(sev)}"
        if sig not in seen: break
    # repeat offender and probation push severity up and show up in the text
    extra = []; prior = history_for(S, pid) if pid else []
    if pid:
        p = S['players'][str(pid)]
        if prior:
            sev += min(2.0, .55 * len(prior)); last = prior[-1]
            extra.append(f"He has {len(prior)} earlier case{'s' if len(prior) != 1 else ''} on the desk in the last three seasons. Most recent: {history_lines(last)}" + (f" (your note: {last['note']})" if last.get('note') else '') + '.')
        pr = p.get('probation')
        if pr and tick(S) <= pr['until']:
            sev += 1.0; extra.append(f"He is on conduct probation from the {pr['title']} ruling, so any further discipline is treated more seriously.")
        if p.get('program_done') and sev > 3: sev -= .4; extra.append("He completed a league conduct program earlier, which counts in his favor.")
    elif spec['subject'] in ('club', 'gm', 'coach'):
        cl = who[0]['club']; pc = [h for h in office(S)['history'] if h.get('club') == cl and h['tier'] in ('club',) and tick(S) - h['tick'] <= 60]
        if pc: sev += min(1.5, .6 * len(pc)); extra.append(f"The {nick(cl)} were disciplined {len(pc)} time{'s' if len(pc) != 1 else ''} in the last three seasons; the most recent was {pc[-1]['title']} ({pc[-1]['year']}).")
    sev = round(clamp(sev + r2.gauss(0, .35), 1.0, 10.0), 1)
    ctx = dict(ctx); [ctx.setdefault(k, v) for k, v in dict(weeks_word='weeks').items()]
    ctx['n'] = len(prior)
    title = r2.choice(spec['title'])
    body = fmt(spec['openers'][op], ctx)
    fact_txt = ' '.join(fmt(f['text'], ctx) for f in facts)
    closer = fmt(r2.choice(spec['closers']), ctx)
    text = '\n\n'.join(x for x in [(body + ' ' + fact_txt).strip(), ' '.join(extra + [closer])] if x)
    prec = precedent_for(S, key, sev, pid)
    story = None; opts = None
    st = spec.get('story')
    case = dict(type=key, title=title, who=who, game=game, where=where, text=text, severity=sev, prior=len(prior), stage='new', pids=pids + ctx.get('pids_extra', []),
                precedent=[f"{h['year']} wk {h['week']}, {h.get('name') or ''}: {h['label']} (severity {h['sev']})" for h in prec], facts=[f['id'] for f in facts])
    if st == 'investigation':
        p_sub = clamp(.25 + .07 * (sev - 3), .15, .8); roll = r2.random()
        truth = 'substantiated' if roll < p_sub else ('partial' if roll < p_sub + .22 else 'unfounded')
        story = dict(kind='investigation', type=key, truth=truth, sev=sev, due_in=r2.choice([2, 3, 3, 4]), club=who[0]['club'], pids=pids, facts=case['facts'], title=title, name=who[0]['name'])
        opts = [O('open', 'Open a formal investigation, rule on the findings', sug=True, open_story=True), O('dismiss', 'Close the matter: no action')]
        if spec['subject'] == 'player': opts.insert(1, O('open_s', 'Open an investigation and suspend pending findings (2 games)', games=2, open_story=True))
    elif st == 'court':
        roll = r2.random(); p_c = clamp(.18 + .07 * (sev - 4), .1, .6)
        outcome = 'convicted' if roll < p_c else ('plea' if roll < p_c + .3 else 'dismissed')
        story = dict(kind='court', type=key, outcome=outcome, sev=sev, due_in=r2.choice([3, 4, 5, 6]), club=who[0]['club'], pids=pids, facts=case['facts'], title=title, name=who[0]['name'])
    if opts is None: opts = ladder(spec['ladder'], sev, facts, ctx, spec)
    if st == 'court':
        pass
    anchored = None
    if st != 'investigation': anchored = anchor_to_precedent(opts, prec, bool(prior))
    case['options'] = opts; case['precedent_pick'] = anchored
    if story: story['next_kind'] = 'findings' if st == 'investigation' else 'court'
    office(S)['sigs'].append(sig)
    return case, story

# ----------------------------------------------------------------------------------------------------------------------------- felony: the league's own, much harsher standard
TOPIC = dict(domestic='a domestic violence complaint', assault='a felony assault complaint', sexual='a sexual assault complaint', dui_injury='a felony DUI crash that injured another driver',
             trafficking='a felony drug distribution case', weapons='a felony weapons case', robbery='a felony burglary case', fraud='a felony fraud case')
STATUS = dict(strong=["was arrested and charged in connection with {t}", "was taken into custody and formally charged in {t_}", "was arrested on a warrant and charged in {t_}"],
              mixed=["was arrested in connection with {t}; prosecutors are reviewing the case", "was taken into custody for questioning in {t_}; no formal charges have been filed"],
              weak=["is the subject of a police investigation into {t}; no arrest has been made", "has been questioned by police about {t}; no charges have been filed"])
def build_felony(S, rnd, key, spec, week, res, used):
    fk = spec['felony']; F = FELONY[fk]
    pool = eligible(S, None, None, used); p = wpick(rnd, S, pool, None, 'cond', star=2.0)
    if not p: return None
    club = p['club']; ctx = base_ctx(S, rnd, club); ctx.update(name=p['name'], pos=p['pos'])
    strength = rnd.choices(['strong', 'mixed', 'weak'], [.35, .4, .25])[0]
    seen = sigs_of(S)
    for attempt in range(14):
        r2 = random.Random(rnd.random())
        st = r2.choice(STATUS[strength]).format(t=TOPIC[fk], t_=TOPIC[fk])
        extra = r2.sample(F['extra'], r2.choice([1, 2])); cues = r2.sample(FELONY_CUES[strength], 2)
        sig = f"{key}|{p['name']}|{strength}|{st[:12]}|{'.'.join(sorted(extra))[:30]}|{'.'.join(cues)[:20]}"
        if sig not in seen: break
    sev = {'strong': 9.0, 'mixed': 8.2, 'weak': 7.4}[strength]
    prior = history_for(S, p['pid']); lines = []
    if prior: sev += min(1.0, .5 * len(prior)); lines.append(f"He has {len(prior)} earlier case{'s' if len(prior) != 1 else ''} on the desk. Most recent: {history_lines(prior[-1])}.")
    sev = round(clamp(sev + r2.gauss(0, .3), 1, 10), 1)
    body = f"{p['name']} ({p['pos']}, {nick(club)}) {st}. " + ' '.join(extra + cues)
    pol = "Under the league's conduct policy the commissioner can act before the court case ends, and the league applies its own standard to this kind of conduct whatever the courts decide."
    text = '\n\n'.join([body, ' '.join(lines + [f"The club says it is gathering facts. {pol}"])])
    # hidden: how the court case and the league's own investigation will end (correlated with the evidence, not determined by it)
    c_probs = dict(strong=(.6, .3, .1), mixed=(.3, .3, .4), weak=(.08, .17, .75))[strength]
    outcome = r2.choices(['convicted', 'plea', 'dropped'], c_probs)[0]
    finding = 'substantiated' if r2.random() < dict(strong=.8, mixed=.5, weak=.25)[strength] else 'not_substantiated'
    if outcome in ('convicted', 'plea') and finding == 'not_substantiated' and r2.random() < .7: finding = 'substantiated'
    prec = precedent_for(S, key, sev, p['pid'])
    sug = dict(strong='indef20', mixed='exempt', weak='exempt')[strength]
    opts = [O('none', 'No action while the case proceeds'), O('exempt', 'Exempt list: out until the case resolves', games=99, status='exempt', exempt=True),
            O('indef20', 'Suspended indefinitely, review after 20 games', games=99, status='indef', indef_min=20), O('indef40', 'Suspended indefinitely, review after 40 games', games=99, status='indef', indef_min=40)]
    for o in opts: o['suggested'] = (o['key'] == sug); o['blurb'] = blurb_of(o)
    story = dict(kind='felony', type=key, fk=fk, strength=strength, outcome=outcome, finding=finding, sev=sev, due_in=r2.choice([3, 4, 5, 6]), club=club, pids=[p['pid']], title=r2.choice(spec_titles(key)), name=p['name'], next_kind='felony')
    case = dict(type=key, title=story['title'], who=[_who(p, club)], game=None, where='Off the field', text=text, severity=sev, prior=len(prior), stage='new', pids=[p['pid']],
                precedent=[f"{h['year']} wk {h['week']}, {h.get('name') or ''}: {h['label']} (severity {h['sev']})" for h in prec], facts=[strength], options=opts, precedent_pick=None)
    office(S)['sigs'].append(sig)
    return case, story
def spec_titles(key): return CATALOG[key]['title'] if CATALOG[key]['title'] else [key]
for _k, _v in FELONY.items(): CATALOG['felony_' + _k]['title'] = _v['title']

# ----------------------------------------------------------------------------------------------------------------------------- follow-ups
FIND_WHAT = dict(bounty='a pay-for-injury program', hazing='a pattern of hazing', tampering='improper contact with a player under contract', cap='unreported payments', gambling='wagers on league games')
FIND_TEXT = dict(
    substantiated=["The league's investigators concluded the allegation of {what} is substantiated.", "After a review of records and interviews, the league found that {what} did occur."],
    partial=["The league's investigators substantiated part of the allegation of {what} and rejected the rest.", "Investigators found some evidence of {what} but could not confirm the full allegation."],
    unfounded=["The league's investigators found no evidence to support the allegation of {what}.", "After interviews and a review of records, the league could not substantiate the allegation of {what}."])
FIND_FACTS = [CC.F('coop', .45, -.6, 'a', "The club cooperated fully with the investigation."), CC.F('obstruct', .14, 1.2, 'a', "Investigators said some records were provided late and others were incomplete."),
              CC.F('senior', .18, 1.0, 'b', "Investigators said senior staff were aware of the conduct."), CC.F('lowlevel', .2, -.8, 'b', "Investigators said the conduct was limited to one individual."),
              CC.F('fix', .25, -.5, 'c', "The club has already changed its procedures."), CC.F('repeat', .1, .8, 'c', "Investigators noted a similar complaint from several years ago.")]
FELONY_RES = dict(
    convicted=["{name} was convicted at trial on the charge arising from {topic}.", "A jury found {name} guilty in the case arising from {topic}."],
    plea=["{name} pleaded guilty to a reduced charge arising from {topic}.", "{name} entered a plea to a lesser offense in the case arising from {topic}."],
    dropped=["Prosecutors dropped the charges against {name} arising from {topic}.", "The case against {name} arising from {topic} was dismissed before trial."])
LEAGUE_FINDING = dict(substantiated=["The league's own investigation found the conduct occurred, whatever the court result.", "Independent of the court, the league's investigators concluded the conduct occurred."],
                      not_substantiated=["The league's own investigation could not establish that the conduct occurred.", "The league's investigators did not find enough to support a finding of misconduct."])

def ref_line(h): return f"Week {h['week']}, {h['year']}: {h['title']}, {h['label']}"

def follow_up(S, rnd, item, week):
    """Build the case for one due item, or None when the subject is no longer available."""
    o = office(S); kind = item['kind']; now = tick(S, week)
    if kind == 'review': return build_review(S, rnd, item, week)
    if kind == 'appeal': return build_appeal(S, rnd, item, week)
    st = o['stories'].get(item['sid'])
    if not st: return None
    p = S['players'].get(str(st['pids'][0])) if st['pids'] else None
    if st['pids'] and (not p or p.get('status') != 'active'): o['stories'].pop(item['sid'], None); return None
    chain = list(st.get('chain', []))
    if st['kind'] == 'investigation': return build_findings(S, rnd, st, item, week, chain, p)
    if st['kind'] == 'court': return build_court(S, rnd, st, item, week, chain, p)
    if st['kind'] == 'felony': return build_resolution(S, rnd, st, item, week, chain, p)

def build_findings(S, rnd, st, item, week, chain, p):
    key = st['type']; spec = dict(CATALOG[key], id=key); r2 = random.Random(rnd.random())
    facts, d = roll_facts(r2, FIND_FACTS, {}, 0)
    sev = clamp(st['sev'] + {'substantiated': 1.4, 'partial': 0.0, 'unfounded': -9}[st['truth']] + d, 1, 10)
    what = FIND_WHAT[key]; text = fmt(r2.choice(FIND_TEXT[st['truth']]), dict(what=what))
    if st['truth'] != 'unfounded': text += ' ' + ' '.join(f['text'].format() for f in facts)
    lead = f"The league has finished its investigation of the {nick(st['club'])}" if spec['subject'] != 'player' else f"The league has finished its investigation of {st['name']} ({nick(st['club'])})"
    text = '\n\n'.join([lead + ' (opened in week ' + str(st['week']) + '). ' + text, 'Original matter: ' + st['summary']])
    if st['truth'] == 'unfounded':
        opts = [O('clear', 'Close the matter: no violation found', sug=True), O('warn', 'Close the matter with a warning about procedures')]
        fv = fine_for(3.0) * (6 if spec['subject'] != 'player' else 1)
        opts.append(O(f"k{fv // 1000}", f"Fine {money(fv)} for failing to cooperate fully", fine=fv))
    else:
        ids = {f['id'] for f in facts}
        kind = spec['ladder']; opts = ladder(kind, sev, [dict(id=i) for i in ids] + [dict(id=x) for x in st.get('facts', []) if x in ('coach_aware', 'intent', 'own', 'gm_aware')], {}, spec)
        opts = [o for o in opts if o['key'] != 'none'] + [O('none', 'No further action')]
    case = dict(type=key, title=f"Findings: {st['title']}", who=[dict(name=st['name'], pos=('CLUB' if spec['subject'] == 'club' else (S['players'][str(st['pids'][0])]['pos'] if st['pids'] else 'STAFF')), club=st['club'], pid=(st['pids'] or [None])[0], club_level=spec['subject'] == 'club')],
                game=None, where='League investigation', text=text, severity=round(sev if st['truth'] != 'unfounded' else 1.0, 1), prior=0, stage='findings', pids=st['pids'], precedent=[], chain=chain + [f"Week {st['week']}, {st['year']}: investigation opened"], facts=[st['truth']] + [f['id'] for f in facts], options=opts, precedent_pick=None, sid=item['sid'])
    return case

def build_court(S, rnd, st, item, week, chain, p):
    r2 = random.Random(rnd.random()); out = st['outcome']
    t = dict(convicted="A court found {name} guilty of the assault charge.", plea="{name} pleaded no contest to the assault charge and was given a suspended sentence and fine.", dismissed="The assault charge against {name} was dismissed.")
    text = fmt(t[out], dict(name=st['name']))
    adj = dict(convicted=2, plea=1, dismissed=-1)[out]
    facts = []
    if out != 'dismissed' and r2.random() < .35: facts.append("The court ordered anger-management counseling."); adj += 0
    if out == 'dismissed' and r2.random() < .4: facts.append("Prosecutors said the witness could not be located.")
    sev = clamp(st['sev'] + adj * .8, 1, 10)
    first = st.get('ruling_games', 0)
    opts = [O('keep', 'No further action; the earlier ruling stands', sug=out == 'dismissed'), O('add2', 'Add 2 games and a conduct program', games=2, adjust=True, program=True), O('add4', 'Add 4 games, a conduct program and probation', games=4, adjust=True, program=True, probation=True, sug=out == 'convicted'),
            O('add2p', 'Add 2 games, program and probation', games=2, adjust=True, program=True, probation=True, sug=out == 'plea')]
    if first: opts.append(O('trim', 'Reduce the earlier suspension by half', games=-(first // 2) if first > 1 else -1, adjust=True))
    for o in opts: o['blurb'] = blurb_of(o) if not o.get('adjust') else ('Reduces the remaining suspension' if o['games'] < 0 else f"Adds {o['games']} games" + (', conduct program' if o.get('program') else '') + (', probation' if o.get('probation') else ''))
    text = '\n\n'.join([text + ' ' + ' '.join(facts), 'Original matter: ' + st['summary'] + f" Your ruling then: {st.get('ruling', 'none')}."])
    return dict(type=st['type'], title=f"Court result: {st['title']}", who=[dict(name=st['name'], pos=p['pos'], club=st['club'], pid=p['pid'])], game=None, where='Off the field', text=text, severity=round(sev, 1), prior=0, stage='resolution', pids=st['pids'],
                precedent=[], chain=chain, facts=[out], options=opts, precedent_pick=None, sid=item['sid'])

def build_resolution(S, rnd, st, item, week, chain, p):
    r2 = random.Random(rnd.random()); F = FELONY[st['fk']]; out, fin = st['outcome'], st['finding']
    topic = TOPIC[st['fk']]
    text = fmt(r2.choice(FELONY_RES[out]), dict(name=st['name'], topic=topic)) + ' ' + r2.choice(LEAGUE_FINDING[fin])
    extra = []
    if out != 'dropped' and r2.random() < .5: extra.append(r2.choice(["He received a sentence that includes probation and court-ordered counseling.", "He was sentenced to time served and a period of supervised release.", "The court imposed restitution and a protective order."]))
    if out == 'dropped' and fin == 'substantiated' and r2.random() < .6: extra.append("Prosecutors said the decision was based on the complainant's wish not to proceed, not on the strength of the evidence.")
    if out == 'dropped' and fin == 'not_substantiated' and r2.random() < .6: extra.append("Prosecutors said new evidence contradicted the original complaint.")
    sev = {'convicted': 9.6, 'plea': 8.8, 'dropped': 7.8 if fin == 'substantiated' else 4.8}[out]
    text = '\n\n'.join([text + ' ' + ' '.join(extra), 'Original matter: ' + st['summary'] + f" Your ruling then: {st.get('ruling', 'none')}."])
    ban_ok = F['ban_on_conviction']
    opts = [O('ban', 'Permanent ban from the league', games=99, status='ban', ban=True), O('indef40', 'Suspended indefinitely, review after 40 games', games=99, status='indef', indef_min=40),
            O('indef20', 'Suspended indefinitely, review after 20 games', games=99, status='indef', indef_min=20),
            O('g16', '16 games, conduct program and probation', games=16, program=True, probation=True), O('g8', '8 games, conduct program and probation', games=8, program=True, probation=True),
            O('g4', '4 games and a conduct program', games=4, program=True), O('rein', 'Reinstate with no further discipline')]
    if out == 'convicted': sug = 'ban' if ban_ok else 'indef40'
    elif out == 'plea': sug = 'indef40'
    elif fin == 'substantiated': sug = 'indef20' if st['strength'] == 'strong' else 'g16'
    else: sug = 'g4' if st['strength'] == 'strong' else 'rein'
    for o in opts: o['suggested'] = (o['key'] == sug); o['blurb'] = blurb_of(o)
    return dict(type=st['type'], title=f"Resolution: {st['title']}", who=[dict(name=st['name'], pos=p['pos'], club=st['club'], pid=p['pid'])], game=None, where='Off the field', text=text, severity=round(sev, 1), prior=0, stage='resolution', pids=st['pids'],
                precedent=[], chain=chain, facts=[out, fin], options=opts, precedent_pick=None, sid=item['sid'])

REVIEW_FACTS = [CC.F('prog_full', .5, -1.0, 'p', "He completed every required session of the league's conduct program."), CC.F('prog_part', .25, .6, 'p', "He completed part of the league's conduct program."), CC.F('prog_missed', .1, 1.6, 'p', "He missed several required sessions."),
                CC.F('eval_good', .4, -1.0, 'e', "An independent evaluator recommended reinstatement."), CC.F('eval_bad', .15, 1.8, 'e', "An independent evaluator recommended continued suspension."),
                CC.F('clean', .55, -.5, 'c', "He has had no further incidents."), CC.F('incident', .08, 2.2, 'c', "He was cited for a minor offense while suspended."),
                CC.F('club', .4, -.3, 'd', "The {nick} say they would welcome him back."), CC.F('unionlet', .3, 0.0, 'f', "The players' union filed a letter asking for reinstatement.")]
def build_review(S, rnd, item, week):
    p = S['players'].get(str(item['pid']))
    if not p or p.get('status') != 'active' or not p.get('indef'): return None
    r2 = random.Random(rnd.random()); ind = p['indef']; o = office(S)
    rec = next((h for h in reversed(o['history']) if h.get('pid') == p['pid'] and (h['id'] == ind.get('case') or h.get('indef'))), None)
    ctx = dict(nick=nick(p['club'])) if p['club'] else dict(nick='club')
    facts, d = roll_facts(r2, REVIEW_FACTS, ctx, 5.0)
    sev = clamp(d, 1, 10)
    served = tick(S, week) - ind['since']
    text = f"{p['name']} ({p['pos']}, {ctx['nick']}) has served the minimum period of his indefinite suspension ({ind['min_games']} games) and is eligible for reinstatement. " + ' '.join(fmt(f['text'], ctx) for f in facts)
    if rec: text += f"\n\nOriginal matter: {history_lines(rec)}."
    opts = [O('reinstate', 'Reinstate now', sug=sev < 4, reinstate=True, probation=True), O('rein_p', 'Reinstate after 4 more games, with a conduct program', games=4, program=True, probation=True, reinstate=True, sug=4 <= sev < 6.2),
            O('defer8', 'Keep him out another 8 games, then review again', games=99, status='indef', indef_min=8, defer=8, sug=6.2 <= sev < 8.6), O('ban', 'Permanent ban from the league', games=99, status='ban', ban=True, sug=sev >= 8.6)]
    for x in opts: x['blurb'] = blurb_of(x)
    return dict(type='review', title='Reinstatement review', who=[_who(p, p['club'])], game=None, where='League office', text=text, severity=round(sev, 1), prior=0, stage='review', pids=[p['pid']], precedent=[],
                chain=[history_lines(rec)] if rec else [], facts=[f['id'] for f in facts], options=opts, precedent_pick=None)

APPEAL_GROUNDS = dict(
    procedural=("The players' union has appealed, arguing the required notice was not given before the ruling.", [CC.F('late', .4, -1.4, 'a', "A review found the notice went out one day late."), CC.F('fine', .6, .6, 'a', "A review found the notice was sent correctly.")]),
    evidence=("The player's side has appealed with new evidence.", [CC.F('credible', .35, -1.6, 'a', "The league's staff rated the new evidence credible."), CC.F('weak', .65, .7, 'a', "The league's staff rated the new evidence weak.")]),
    proportion=("The players' union has appealed, arguing the penalty is out of line with earlier rulings for similar conduct.", []),
    mitigation=("The player has appealed, pointing to his cooperation and his record.", [CC.F('coop', .6, -.8, 'a', "He has fully cooperated with every request from the league."), CC.F('hist', .4, -.5, 'b', "He has no earlier cases on the desk."), CC.F('defy', .12, 1.2, 'c', "He criticized the ruling publicly after it was announced.")]))
def build_appeal(S, rnd, item, week):
    o = office(S); h = next((x for x in o['history'] if x['id'] == item['rid'] and x['year'] == item['year']), None)
    p = S['players'].get(str(h['pid'])) if h and h.get('pid') else None
    if not h or not p or p.get('status') != 'active': return None
    r2 = random.Random(rnd.random()); g = r2.choice(list(APPEAL_GROUNDS)); lead, fl = APPEAL_GROUNDS[g]
    facts, d = roll_facts(r2, fl, {}, 5.0)
    prec = [x for x in o['history'] if x['type'] == h['type'] and x['id'] != h['id'] and abs(x['sev'] - h['sev']) <= 1.3 and x['tick'] < h['tick']][:3]
    if g == 'proportion':
        med = sorted(x['games'] for x in prec)[len(prec) // 2] if prec else None
        if med is not None and med < h['games']: d -= 1.4; facts.append(dict(text=f"Comparable earlier rulings (severity within a point) imposed a median of {med} game{'s' if med != 1 else ''}, against {h['games']} here."))
        elif med is not None: d += .7; facts.append(dict(text=f"Comparable earlier rulings imposed a median of {med} game{'s' if med != 1 else ''}, in line with this one."))
        else: facts.append(dict(text="There are no close precedents on the books."))
    sev = clamp(d, 1, 10)
    text = f"{lead} {p['name']} ({p['pos']}, {nick(p['club'])}) was ruled on in week {h['week']}, {h['year']}: {h['title']}, {h['label']}. " + ' '.join((f['text'] if isinstance(f, dict) else f['text']).format_map(SafeDict(dict(nick=nick(p['club'])))) for f in facts)
    games = h['games'] if h['games'] < 99 else 0
    opts = [O('uphold', 'Uphold the ruling', sug=sev >= 4.5)]
    if games >= 1: opts += [O('red', f"Reduce by {max(1, games // 3)} game{'s' if games // 3 > 1 else ''}", games=-max(1, games // 3), adjust=True, sug=3 <= sev < 4.5), O('over', 'Overturn the suspension (fine stands)', games=-games, adjust=True, sug=sev < 3)]
    elif h['fine']: opts += [O('redf', f"Halve the fine to {money(h['fine'] // 2)}", fine=-(h['fine'] // 2), adjust=True, sug=3 <= sev < 4.5), O('overf', 'Rescind the fine', fine=-h['fine'], adjust=True, sug=sev < 3)]
    for x in opts: x['blurb'] = x['label']
    if not any(x['suggested'] for x in opts): opts[0]['suggested'] = True
    return dict(type='appeal', title=f"Appeal: {h['title']}", who=[_who(p, p['club'])], game=None, where='League office', text=text, severity=round(sev, 1), prior=0, stage='appeal', pids=[p['pid']], precedent=[], chain=[ref_line(h)],
                facts=[g] + [f.get('id', 'x') for f in facts], options=opts, precedent_pick=None, rid=h['id'], ryear=h['year'])

# ----------------------------------------------------------------------------------------------------------------------------- weekly draw
RATES = [('minor', 0.90), ('moderate', 0.25), ('serious', 0.08), ('major', 0.015), ('club', 0.05)]
def tier_types(tier):
    return [(k, v['w']) for k, v in CATALOG.items() if v['tier'] == tier]

def poisson(rnd, mean):
    L = math.exp(-mean); k = 0; p = 1.0
    while True:
        p *= rnd.random()
        if p <= L: return k
        k += 1

def draw(S, week, res):
    """All cases for the ballot after `week`: due follow-ups first (they use up that tier's weekly draw), then new cases. Hidden storyline data goes to
    S['office']['pending'] and nowhere else."""
    o = office(S); se = S['season']; year = se['year']; now = tick(S, week)
    rnd = random.Random(f"league-office-{year}-{week}")
    cases = []; used = set(); netted = collections.Counter()
    due = [d for d in o['due'] if d['tick'] <= now]; o['due'] = [d for d in o['due'] if d['tick'] > now]
    for it in due:
        c = follow_up(S, rnd, it, week)
        if not c: continue
        c['_it'] = it
        st = c['stage']
        if st == 'review': tier = 'review'
        elif st == 'appeal': tier = 'appeal'
        elif c['type'].startswith('felony'): tier = 'major'
        else: tier = CATALOG[c['type']]['tier']
        c['tier'] = tier
        if tier in dict(RATES): netted[tier] += 1
        cases.append(c); used.update(c['pids'])
    for tier, mean in RATES:
        n = max(0, poisson(rnd, mean) - netted[tier]); types = tier_types(tier)
        for _ in range(n):
            for _try in range(16):
                key = rnd.choices([k for k, w in types], [w for k, w in types])[0]
                r = build_case(S, rnd, key, week, res, used)
                if r: break
            else: continue
            c, story = r; c['tier'] = tier; c['_story'] = story; cases.append(c); used.update(c['pids'])
    order = {'major': 0, 'review': 1, 'serious': 2, 'club': 3, 'moderate': 4, 'appeal': 5, 'minor': 6}
    cases.sort(key=lambda c: order[c['tier']])
    for i, c in enumerate(cases):
        c['id'] = f"W{week}-{i + 1}"; c['week'] = week
        story = c.pop('_story', None); it = c.pop('_it', None)
        sid = f"{year}:{c['id']}"
        if story:
            story.update(week=week, year=year, summary=c['text'].split('\n\n')[0], chain=[]); o['pending'][sid] = story; c['sid'] = sid
        c.pop('facts', None)
    return cases

# ----------------------------------------------------------------------------------------------------------------------------- applying rulings
def _drop_reviews(S, pid):
    of = office(S); of['due'] = [d for d in of['due'] if not (d['kind'] == 'review' and d.get('pid') == pid)]

def _clear_hold(p):
    if p.get('inj') and p['inj']['kind'] in UNHEALED + ('suspended',): p.pop('inj')
    p.pop('indef', None)

def suspend(S, p, club, week, games, kind='suspended'):
    span = span_for_games(S, club, week, games)
    p['inj'] = {'weeks': span, 'kind': kind}
    S['season']['injuries_log'].append(dict(week=week, team=club, pid=p['pid'], name=p['name'], pos=p['pos'], weeks=span, kind=kind))

def ban_player(S, p, week, reason):
    club = p['club']
    if club and p['pid'] in S['clubs'][club]['roster']: S['clubs'][club]['roster'].remove(p['pid'])
    p.pop('inj', None); p.pop('indef', None); p.pop('starter', None)
    p.update(status='retired', retired=S['season']['year'], retired_from=club, club=None, contract=None, retire_reason='banned by the league', banned=dict(year=S['season']['year'], week=week, reason=reason))

def apply_case(S, week, c, d):
    """Apply one ruling with real effects. Returns (record, notes)."""
    se = S['season']; of = office(S); year = se['year']; now = tick(S, week); P = S['players']
    o = next(x for x in c['options'] if x['key'] == d['key']); notes = []
    rnd = random.Random(f"office-apply|{year}|{week}|{c['id']}")
    stage = c.get('stage', 'new'); sev = c.get('severity') or {'minor': 2.8, 'moderate': 5.0, 'serious': 5.2, 'major': 8.0, 'club': 5.0}.get(c['tier'], 3.0)
    clubs = [w['club'] for w in c['who']]
    status = o.get('status', 'ok'); indef_min = o.get('indef_min') or (16 if status == 'indef' else 0)
    rec = dict(year=year, week=week, id=c['id'], tier=c['tier'], type=c['type'], title=c['title'], who=[w['name'] for w in c['who']], clubs=clubs, pid=c['who'][0].get('pid'),
               pids=[w['pid'] for w in c['who'] if w.get('pid')], ruling=o['label'], key=o['key'], fine=max(0, o['fine']), games=o['games'], note=d.get('note', ''), sev=round(sev, 1), stage=stage)
    adjust = o.get('adjust') or o.get('reinstate') or o.get('defer')
    for w in c['who']:
        pid = w.get('pid')
        if not pid:      # coach, GM or the club itself
            cl = S['clubs'].get(w['club'])
            if cl and o.get('coach_games'):
                cl['coach_out'] = dict(weeks=span_for_games(S, w['club'], week, o['coach_games']), games=o['coach_games']); notes.append(f"{nick(w['club'])} head coach {cl['coach']['name']} is off the sideline for {o['coach_games']} game{'s' if o['coach_games'] != 1 else ''}")
            continue
        p = P[str(pid)]; club = w['club']
        if stage == 'review':
            _drop_reviews(S, pid)
            if o.get('ban'): ban_player(S, p, week, c['title']); notes.append(f"{p['name']} is banned from the league")
            elif o.get('defer'):
                p['indef'] = dict(since=now, min_games=o['defer'], case=c['id']); of['due'].append(dict(tick=now + o['defer'], kind='review', pid=pid)); notes.append(f"{p['name']} stays out; next review in {o['defer']} games")
            else:
                _clear_hold(p)
                if o['games']: suspend(S, p, club, week, o['games'])
                notes.append(f"{p['name']} is reinstated" + (f" after {o['games']} more games" if o['games'] else ''))
        elif stage == 'appeal':
            h = next((x for x in of['history'] if x['id'] == c['rid'] and x['year'] == c['ryear']), None)
            if o['games'] < 0 and p.get('inj') and p['inj']['kind'] == 'suspended':
                p['inj']['weeks'] += o['games']
                if p['inj']['weeks'] <= 0: p.pop('inj'); notes.append(f"{p['name']} is cleared to play")
                else: notes.append(f"{p['name']}'s suspension is shortened")
            if h:
                h['games'] = max(0, h['games'] + o['games']) if h['games'] < 99 else h['games']; h['fine'] = max(0, h['fine'] + o['fine'])
                if o['key'] != 'uphold': h['label'] += ' (changed on appeal)'
        elif stage == 'resolution' and c['type'].startswith('felony') or (stage == 'resolution' and o.get('adjust') is None and False):
            _clear_hold(p)
            _apply_penalty(S, p, club, week, now, o, c, rnd, notes, status, indef_min)
        elif o.get('adjust') and stage == 'resolution':     # court result adds to or trims the earlier ruling
            if o['games'] < 0 and p.get('inj') and p['inj']['kind'] == 'suspended':
                p['inj']['weeks'] += o['games']
                if p['inj']['weeks'] <= 0: p.pop('inj')
                notes.append(f"{p['name']}'s suspension is shortened")
            elif o['games'] > 0:
                span = span_for_games(S, club, week, o['games'])
                if p.get('inj') and p['inj']['kind'] == 'suspended': p['inj']['weeks'] += span
                else: suspend(S, p, club, week, o['games'])
                notes.append(f"{p['name']} is out {o['games']} more game{'s' if o['games'] != 1 else ''}")
            if o.get('program'): _program(p, rnd, notes)
            if o.get('probation'): _probation(p, c, now, year, week, notes)
        else:
            if stage == 'findings': pass
            _apply_penalty(S, p, club, week, now, o, c, rnd, notes, status, indef_min)
        if o['key'] not in ('none', 'warn', 'dismiss', 'clear', 'keep', 'uphold', 'rein', 'reinstate') and c['tier'] in ('minor', 'moderate', 'serious', 'major', 'club'):
            DISC.mark_case(p, c['tier'], max(0, o['games']), random.Random(f"mark|{c['id']}|{year}"))
    if o.get('pick_round'):
        S.setdefault('pick_penalties', []).append(dict(club=clubs[0], round=o['pick_round'], draft=year + 1, week=week, reason=c['title'], year=year)); notes.append(f"{nick(clubs[0])} lose a round {o['pick_round']} pick in the {year + 1} draft")
    # storylines: a ruling on a new case may open one; findings/resolutions close it
    sid = c.get('sid')
    if stage == 'new' and sid and sid in of['pending']:
        story = of['pending'].pop(sid)
        if o['key'] != 'dismiss':
            story.update(ruling=o['label'], ruling_games=o['games'] if o['games'] < 99 else 0)
            of['stories'][sid] = story; of['due'].append(dict(tick=now + story['due_in'], kind=story['next_kind'], sid=sid))
    elif stage in ('findings', 'resolution') and sid:
        of['stories'].pop(sid, None)
    of['history'].append(dict(tick=now, year=year, week=week, id=c['id'], type=c['type'], tier=c['tier'], title=c['title'], sev=round(sev, 1), key=o['key'], label=o['label'], games=o['games'], fine=max(0, o['fine']),
                              pid=rec['pid'], pids=rec['pids'], club=clubs[0] if clubs else None, name=(rec['who'] or [''])[0], note=d.get('note', ''), stage=stage, indef=bool(indef_min)))
    # appeals: a real chance after anything with teeth
    if stage in ('new', 'findings', 'resolution') and not o.get('adjust') and (1 <= o['games'] < 99 or o['fine'] >= 50000) and not (o.get('ban') or indef_min or o.get('exempt')) and rec['pid']:
        pa = clamp(.08 + .03 * sev, .08, .45)
        if rnd.random() < pa: of['due'].append(dict(tick=now + 1, kind='appeal', rid=c['id'], year=year))
    se['discipline'].append(rec)
    return rec, notes

def _program(p, rnd, notes):
    p['program_done'] = True; p['cond'] = min(100, p.get('cond', 50) + rnd.uniform(2, 8)); notes.append(f"{p['name']} enters a league conduct program")
def _probation(p, c, now, year, week, notes):
    p['probation'] = dict(until=now + 40, title=c['title'], year=year, week=week); notes.append(f"{p['name']} is on conduct probation for a year")

def _apply_penalty(S, p, club, week, now, o, c, rnd, notes, status, indef_min):
    year = S['season']['year']; of = office(S)
    _drop_reviews(S, p['pid'])
    if o.get('ban'):
        ban_player(S, p, week, c['title']); notes.append(f"{p['name']} is banned from the league"); return
    if o.get('exempt'):
        p['inj'] = {'weeks': 99, 'kind': 'exempt list'}; S['season']['injuries_log'].append(dict(week=week, team=club, pid=p['pid'], name=p['name'], pos=p['pos'], weeks=99, kind='exempt list')); notes.append(f"{p['name']} goes on the exempt list until the case resolves")
    elif status == 'indef' or o['games'] >= 99:
        p['inj'] = {'weeks': 99, 'kind': 'suspended indefinitely'}; p['indef'] = dict(since=now, min_games=indef_min or 16, case=c['id'])
        S['season']['injuries_log'].append(dict(week=week, team=club, pid=p['pid'], name=p['name'], pos=p['pos'], weeks=99, kind='suspended indefinitely'))
        of['due'].append(dict(tick=now + (indef_min or 16), kind='review', pid=p['pid'])); notes.append(f"{p['name']} is suspended indefinitely; first review after {indef_min or 16} games")
    elif o['games'] > 0:
        suspend(S, p, club, week, o['games']); notes.append(f"{p['name']} is out {o['games']} game{'s' if o['games'] != 1 else ''}")
    if o.get('program'): _program(p, rnd, notes)
    if o.get('probation'): _probation(p, c, now, year, week, notes)
