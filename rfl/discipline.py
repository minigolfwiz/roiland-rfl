"""Discipline traits (Dan, 27 Oct 2026). Hidden, never shown in narrative or on any page.

Every player carries two 1-100 traits, higher = better behaved, league average about 50:
  disc  on-field discipline: drives in-game penalties (and the personal-foul side of League Office cases)
  cond  off-field conduct:  drives League Office cases (PED, DUI, firearm, criminal, comments, ...)
They share one latent "temperament" (correlation RHO), so a penalty magnet is somewhat more likely to be in trouble off the
field too, but the two lists are not the same names. Both are deterministic from the player's name and birth year.
  dgr   personal development rate (points a year while there is room to grow); about 8% of players carry a NEGATIVE rate
        (a slow decline arc) instead of maturing.
Coaches carry `disc` as well: a team-wide on-field baseline, plus a small culture effect on their players' conduct drift.

Penalty / case weights are exp(beta * zbad) with zbad = how far BELOW the league average a player sits (in league SDs), normalised so
the league-wide rate does not move: the traits decide who gets the flags and how teams differ, not how many flags there are.
"""
import random, math, hashlib

RHO = .45           # correlation between on-field and off-field discipline (shared temperament)
MU, SD = 50.0, 15.0
DECLINE_SHARE = .08
BETA_SEL = .35      # who gets flagged inside a unit
BETA_TEAM = .10     # unit average -> a team's penalty rate
BETA_COACH = .05    # coach discipline -> a team's penalty rate
BETA_LO = .55       # League Office case odds (cond / blend)
LO_MIN, LO_MAX = .35, 3.0
ZCAP = 2.5          # nobody is treated as more than 2.5 league-SDs from average, so no single player becomes an extreme outlier

def _sha(s): return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
def clamp(x, a, b): return max(a, min(b, x))

def gen_traits(name, born, year):
    """Deterministic traits for a player: {'disc','cond','dgr'}."""
    r = random.Random(_sha(f"disc|{name}|{born}"))
    t, e1, e2 = r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1)
    zd = math.sqrt(RHO) * t + math.sqrt(1 - RHO) * e1
    zc = math.sqrt(RHO) * t + math.sqrt(1 - RHO) * e2
    a = year - born; mat = clamp(1.1 * (a - 27), -6, 7)          # a 21-year-old starts lower than a 31-year-old
    g = max(.15, r.gauss(1.7, .9))
    if r.random() < DECLINE_SHARE: g = -round(.6 + r.random() * 1.4, 1)
    return dict(disc=int(clamp(round(MU + 2 + SD * zd + mat), 3, 99)), cond=int(clamp(round(MU + 2 + SD * zc + mat), 3, 99)), dgr=round(g, 2))

def gen_coach_disc(name):
    r = random.Random(_sha(f"cdisc|{name}")); return int(clamp(round(MU + 12 * r.gauss(0, 1)), 15, 92))

def trait_for_rookie(name, born, year, supplied=None):
    """Rookies take whatever the college sim supplies (disc / cond / discipline / conduct, 1-100); anything missing is generated."""
    t = gen_traits(name, born, year); s = supplied or {}
    d = s.get('disc', s.get('discipline')); c = s.get('cond', s.get('conduct'))
    if d is not None: t['disc'] = int(clamp(round(float(d)), 1, 100))
    if c is not None: t['cond'] = int(clamp(round(float(c)), 1, 100))
    elif d is not None and s.get('cond') is None and s.get('conduct') is None:   # only an on-field number came in: derive the other from it, keeping the shared-temperament link
        r = random.Random(_sha(f"cond|{name}|{born}")); z = (t['disc'] - MU) / SD
        t['cond'] = int(clamp(round(MU + SD * (math.sqrt(RHO) * z + math.sqrt(1 - RHO) * r.gauss(0, 1))), 3, 99))
    return t

def ensure_traits(S):
    """Idempotent migration: give every player and coach who lacks traits a deterministic set. Returns (players, coaches) filled."""
    year = S['season']['year'] if S.get('season') else S.get('year', 2043); n = m = 0
    for p in S['players'].values():
        if 'disc' in p: continue
        p.update(gen_traits(p['name'], p['born'], year)); n += 1
    for c in S['clubs'].values():
        co = c.get('coach')
        if co is not None and 'disc' not in co: co['disc'] = gen_coach_disc(co['name']); m += 1
    return n, m

# ------------------------------------------------------------------------------ league norms (so the traits never change league-wide totals)
_CACHE = {}
def norms(S):
    key = (id(S), len(S['players']), (S.get('season') or {}).get('year'), (S.get('season') or {}).get('week_done'))
    if key in _CACHE: return _CACHE[key]
    act = [p for c in S['clubs'].values() for pid in c['roster'] for p in [S['players'][str(pid)]] if 'disc' in p]
    if not act: N = dict(mu_d=MU, sd_d=SD, mu_c=MU, sd_c=SD, mu_k=MU, sd_k=SD, Msel=1.0, Mteam=1.0, Mcoach=1.0)
    else:
        dv = [p['disc'] for p in act]; cv = [p['cond'] for p in act]
        mu_d = sum(dv) / len(dv); sd_d = max(5.0, (sum((x - mu_d) ** 2 for x in dv) / len(dv)) ** .5)
        mu_c = sum(cv) / len(cv); sd_c = max(5.0, (sum((x - mu_c) ** 2 for x in cv) / len(cv)) ** .5)
        zs = [clamp(-(x - mu_d) / sd_d, -ZCAP, ZCAP) for x in dv]
        ks = [c['coach'].get('disc', MU) for c in S['clubs'].values()]; mu_k = sum(ks) / len(ks); sd_k = max(4.0, (sum((x - mu_k) ** 2 for x in ks) / len(ks)) ** .5)
        zk = [clamp(-(x - mu_k) / sd_k, -ZCAP, ZCAP) for x in ks]
        N = dict(mu_d=mu_d, sd_d=sd_d, mu_c=mu_c, sd_c=sd_c, mu_k=mu_k, sd_k=sd_k,
                 Msel=sum(math.exp(BETA_SEL * z) for z in zs) / len(zs), Mteam=sum(math.exp(BETA_TEAM * z) for z in zs) / len(zs), Mcoach=sum(math.exp(BETA_COACH * z) for z in zk) / len(zk))
    if len(_CACHE) > 8: _CACHE.clear()
    _CACHE[key] = N; return N

def z_disc(N, p): return clamp(-(p.get('disc', MU) - N['mu_d']) / N['sd_d'], -ZCAP, ZCAP)      # positive = worse behaved than average
def z_cond(N, p): return clamp(-(p.get('cond', MU) - N['mu_c']) / N['sd_c'], -ZCAP, ZCAP)
def z_mix(N, p, w=.5): return w * z_disc(N, p) + (1 - w) * z_cond(N, p)
def z_coach(N, coach): return clamp(-(coach.get('disc', MU) - N['mu_k']) / N['sd_k'], -ZCAP, ZCAP)

def lo_weight(N, p, kind='cond'):
    """League Office odds multiplier. kind: 'cond' (off-field cases), 'mix' (on-field conduct cases that are part temperament). Capped both ways."""
    z = z_cond(N, p) if kind == 'cond' else z_mix(N, p, .5)
    return clamp(math.exp(BETA_LO * z), LO_MIN, LO_MAX)

# ------------------------------------------------------------------------------ yearly drift
def progress_traits(S, rnd):
    """Called once a year with the other offseason progression. Most players mature, at their own pace; a few slide. Large League Office
    cases leave a mark on conduct (see mark_case)."""
    year = S['season']['year']; ensure_traits(S)
    for p in S['players'].values():
        if p.get('status') == 'retired': continue
        a = year - p['born']; g = p.get('dgr', 1.5)
        if g >= 0:
            g *= max(.3, 1 - max(0, a - 31) * .15)                       # growth tapers in the thirties
            dd = g * (95 - p['disc']) / 45 + rnd.gauss(0, 1.2)            # diminishing returns near the top
            dc = .8 * g * (95 - p['cond']) / 45 + rnd.gauss(0, 1.5)
        else:
            dd = g * (p['disc'] - 10) / 45 + rnd.gauss(0, 1.2)
            dc = .9 * g * (p['cond'] - 10) / 45 + rnd.gauss(0, 1.5)
        co = S['clubs'].get(p.get('club') or '', {}).get('coach') if p.get('club') else None
        if co is not None: dc += .02 * (co.get('disc', MU) - MU)         # a well-run locker room: +-0.5 a year at the extremes
        p['disc'] = int(clamp(round(p['disc'] + dd), 1, 99)); p['cond'] = int(clamp(round(p['cond'] + dc), 1, 99))

def mark_case(p, tier, games, rnd):
    """A serious ruling leaves a mark: usually a hit to conduct, occasionally a wake-up call instead."""
    if tier not in ('serious', 'major') and not (tier == 'moderate' and games): return
    if rnd.random() < .25: p['cond'] = int(clamp(p.get('cond', MU) + rnd.randint(2, 5), 1, 99)); p['disc'] = int(clamp(p.get('disc', MU) + rnd.randint(1, 3), 1, 99))
    else: p['cond'] = int(clamp(p.get('cond', MU) - rnd.randint(3, 6), 1, 99)); p['disc'] = int(clamp(p.get('disc', MU) - rnd.randint(0, 3), 1, 99))
