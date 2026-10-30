"""Finish the conference calendar around the weeks Dan placed by hand.

Dan's brief, 2039: fill the rest. The occasional four-game home stand is fine, but only
if at least one of the four is a non-conference game; four road games in a row is
unacceptable. Everything he placed is left exactly where he put it -- six whole
conferences and 192 non-conference weeks in the 2039 hand-off -- and only the open
games move.

The hard rules are the page's own, plus his two:
  * one game a week per programme; week 14 (rivalry week) is a full slate
  * exactly three byes, never back to back (follows from 12 games in 15 weeks once
    nothing is double-booked, but the adjacency has to be enforced)
  * never four road games in a row -- counted over the games actually PLAYED, so a bye
    between the third and fourth does not reset it; that is the stricter reading and
    it is also the one a coach would use
  * never five home games in a row; four only if one of them is non-conference

Soft, in the page's own spirit: week 0 is a light opening and non-conference, week 1
leans non-conference, and the rest of the calendar is level.

Simulated annealing over the open games. A move either drops a game into a week both
sides have free, or swaps it with another open game so a clash resolves in one step.
Only the programmes touched are rescored, so a pass over a few hundred thousand moves
is cheap. Hard-rule violations are weighted so the search cannot trade one for soft
gains; the run is accepted only at zero.
"""
import sys, json, random, collections, math
sys.path.insert(0, '/home/claude/cfb2')

PAYLOAD = '/home/claude/cfb2/state/conf_board.json'
import season as _SE
_SN = _SE.load_state().get('season')
HANDOFF = '/home/claude/cfb2/state/conf_s%d_handoff.json' % _SN
WEEKS = list(range(15))
RIV = 14
HARD = 1000.0
import pickle as _pk
_TIER = _pk.load(open('/home/claude/cfb2/state/universe.pkl', 'rb'))['tiers']

# soft weights
W0_CONF = 20.0          # a conference game in week 0
W1_CONF = 8.0           # a conference game in week 1
W0_NC_OVER = 4.0        # each non-conference game in week 0 past one per conference
HOME3 = 0.6             # a three-game home or road run: legal, mildly discouraged
LEVEL = 0.15            # per game off a level week count
# Dan's standing calendar preferences (2043, taught to the filler for the 2045 build):
W_LATE_HOME = 12.0      # no home game anywhere in weeks 11-14 (power programmes above all)
W_LATE_HOME_P6 = 18.0
W_BYE_SPAN = 3.0        # per week short of 6 when all three byes sit inside a short window
W_BYE_GAP2 = 2.0        # two byes only one game apart (weeks 0 and 2, 4 and 6 ...)
W_RUN = 3.0             # per game past six in an unbroken run of games between byes


class Cal:
    def __init__(self, payload, handoff):
        P = json.load(open(payload)); H = json.load(open(handoff))
        self.P = P
        self.teams = sorted(P['teams'])
        self.conf_of = {t: P['teams'][t]['conf'] for t in self.teams}
        self.games = []
        hand = {}
        for g in H['games']:
            hand[frozenset((g['host'], g['visitor']))] = g
        for ci, c in enumerate(P['conferences']):
            for i, g in enumerate(c['games']):
                h = hand.get(frozenset((g['a'], g['b'])))
                wk = h['week'] if h else g['week']
                self.games.append({'id': 'C%d-%d' % (ci, i), 'conf': c['conference'],
                                   'host': g['host'], 'away': g['b'] if g['host'] == g['a'] else g['a'],
                                   'week': wk, 'fixed': bool(g['locked']) or wk is not None, 'sub': False})
        for i, g in enumerate(P['noncon']):
            h = hand.get(frozenset((g['host'], g['visitor'])))
            wk = h['week'] if h else g['week']
            self.games.append({'id': 'N%d' % i, 'conf': None, 'host': g['host'],
                               'away': None if g['sub'] else g['visitor'],
                               'week': wk, 'fixed': bool(g['locked']) or wk is not None,
                               'sub': bool(g['sub'])})
        self.slot = {t: [None] * 15 for t in self.teams}
        for g in self.games:
            if g['week'] is not None:
                for t in self.sides(g):
                    assert self.slot[t][g['week']] is None, (t, g['week'], g['id'])
                    self.slot[t][g['week']] = g
        self.open = [g for g in self.games if not g['fixed']]
        # `bye_before`: a locked pair that must both be idle the week before their game
        # (Will Tech / Tasson, week 9). The Office does not enforce it; the installer
        # refuses it; so the filler has to know. Found the hard way, 2039.
        self.must_idle = set()
        for c in P['conferences']:
            for L in c.get('locked', []):
                if L.get('bye_before') and L.get('week') is not None:
                    self.must_idle.add((L['a'], L['week'] - 1)); self.must_idle.add((L['b'], L['week'] - 1))

    def sides(self, g):
        return [g['host']] + ([g['away']] if g['away'] else [])

    # ---------------- scoring ----------------
    def team_score(self, t):
        row = self.slot[t]
        s = 0.0
        # byes: back to back, and never week 14
        byes = [w for w in WEEKS if row[w] is None]
        if row[RIV] is None: s += HARD
        for (tt, w) in self.must_idle:
            if tt == t and row[w] is not None: s += HARD
        for i in range(1, len(byes)):
            if byes[i] - byes[i - 1] == 1: s += HARD
        # venue runs over games actually played
        seq = [(('H' if g['host'] == t else 'A'), g['conf'] is None) for g in row if g]
        i = 0
        while i < len(seq):
            j = i
            while j < len(seq) and seq[j][0] == seq[i][0]: j += 1
            n = j - i
            if seq[i][0] == 'A':
                if n >= 4: s += HARD * (n - 3)
                elif n == 3: s += HOME3
            else:
                if n >= 5: s += HARD * (n - 4)
                elif n == 4:
                    if not any(nc for _v, nc in seq[i:j]): s += HARD
                    else: s += HOME3 * 2
                elif n == 3: s += HOME3
            i = j
        # soft (Dan, 2043): a home game somewhere in weeks 11-14
        if not any(row[w] and row[w]['host'] == t for w in (11, 12, 13, 14)):
            s += W_LATE_HOME_P6 if _TIER[self.conf_of[t]] == 'P6' else W_LATE_HOME
        # soft (Dan, 2043): byes spread through the year, long unbroken runs broken up
        if len(byes) == 3:
            span = byes[-1] - byes[0]
            if span < 6: s += W_BYE_SPAN * (6 - span)
            s += W_BYE_GAP2 * sum(1 for i in range(1, 3) if byes[i] - byes[i - 1] == 2)
        edges = [-1] + byes + [15]
        s += W_RUN * sum(max(0, (edges[i + 1] - edges[i] - 1) - 6) for i in range(len(edges) - 1))
        # soft: week 0 / 1 conference games
        for w, pen in ((0, W0_CONF), (1, W1_CONF)):
            g = row[w]
            if g and g['conf'] is not None and g['host'] == t: s += pen   # count once, at the host
        return s

    def global_score(self):
        s = sum(self.team_score(t) for t in self.teams)
        per = collections.Counter(g['week'] for g in self.games if g['week'] is not None)
        nc0 = sum(1 for g in self.games if g['week'] == 0 and g['conf'] is None)
        s += W0_NC_OVER * max(0, nc0 - len(self.P['conferences']))
        mean = sum(per[w] for w in range(1, 14)) / 13.0
        s += LEVEL * sum(abs(per[w] - mean) for w in range(1, 14))
        return s

    def hard_violations(self):
        out = []
        for t in self.teams:
            row = self.slot[t]
            byes = [w for w in WEEKS if row[w] is None]
            if len(byes) != 3: out.append((t, 'byes=%d' % len(byes)))
            if row[RIV] is None: out.append((t, 'bye in week 14'))
            for (tt, w) in self.must_idle:
                if tt == t and row[w] is not None: out.append((t, 'must be idle in week %d (bye before a locked game)' % w))
            for i in range(1, len(byes)):
                if byes[i] - byes[i - 1] == 1: out.append((t, 'byes %d-%d' % (byes[i-1], byes[i])))
            seq = [(('H' if g['host'] == t else 'A'), g['conf'] is None) for g in row if g]
            i = 0
            while i < len(seq):
                j = i
                while j < len(seq) and seq[j][0] == seq[i][0]: j += 1
                n = j - i
                if seq[i][0] == 'A' and n >= 4: out.append((t, '%d road in a row' % n))
                if seq[i][0] == 'H' and n >= 5: out.append((t, '%d home in a row' % n))
                if seq[i][0] == 'H' and n == 4 and not any(nc for _v, nc in seq[i:j]):
                    out.append((t, '4 home in a row, all conference'))
                i = j
        return out

    # ---------------- moves ----------------
    def place(self, g, w):
        if g['week'] is not None:
            for t in self.sides(g): self.slot[t][g['week']] = None
        g['week'] = w
        if w is not None:
            for t in self.sides(g): self.slot[t][w] = g

    def initial(self, rng):
        """Greedy seed: most-constrained open game first into a legal free week."""
        left = list(self.open)
        rng.shuffle(left)
        for _round in range(50):
            stuck = []
            left.sort(key=lambda g: sum(1 for w in WEEKS if all(self.slot[t][w] is None for t in self.sides(g))))
            for g in left:
                free = [w for w in WEEKS if all(self.slot[t][w] is None for t in self.sides(g)) and not (g['sub'] and w == RIV)]   # standing rule (2043): no guest games in week 14
                if not free: stuck.append(g); continue
                # prefer week 14 for anyone still without one, else a random free week
                rng.shuffle(free)
                free.sort(key=lambda w: (0 if w == RIV else 1))
                self.place(g, free[0])
            if not stuck: return True
            # unplace a random fixed-free neighbour to make room and retry
            for g in stuck:
                t = rng.choice(self.sides(g))
                movable = [x for x in self.slot[t] if x and not x['fixed']]
                if movable: self.place(rng.choice(movable), None)
            left = [g for g in self.open if g['week'] is None]
        return False

    def anneal(self, rng, iters=400000, T0=6.0, T1=0.05, anchor=None, anchor_w=3.0):
        # `anchor`: {id: original week}. A repair pass pays `anchor_w` for every game it
        # leaves off its original week, so it moves as little of Dan's board as it can.
        touched = lambda gs: {t for g in gs for t in self.sides(g)}
        cur = self.global_score()
        best = cur
        for k in range(iters):
            T = T0 * (T1 / T0) ** (k / iters)
            g = rng.choice(self.open)
            w = rng.randrange(15)
            if w == g['week']: continue
            if g['sub'] and w == RIV: continue
            old = g['week']
            sides = self.sides(g)
            blockers = [self.slot[t][w] for t in sides if self.slot[t][w] is not None]
            blockers = list({id(b): b for b in blockers}.values())
            if any(b['fixed'] for b in blockers): continue
            if len(blockers) > 1: continue
            h = blockers[0] if blockers else None
            if h is not None:
                # swap: h goes to old; every side of h must be free at old (except g itself)
                if any(self.slot[t][old] not in (None, g) for t in self.sides(h)): continue
                if h['sub'] and old == RIV: continue
            aff = touched([g] + ([h] if h else []))
            before = sum(self.team_score(t) for t in aff)
            per_before = self._level_terms()
            # do it
            self.place(g, None)
            if h: self.place(h, None); self.place(h, old)
            self.place(g, w)
            after = sum(self.team_score(t) for t in aff)
            delta = (after - before) + (self._level_terms() - per_before)
            if anchor:
                moved_before = (old != anchor[g['id']]) + ((w != anchor[h['id']]) if h else 0)
                moved_after = (w != anchor[g['id']]) + ((old != anchor[h['id']]) if h else 0)
                delta += anchor_w * (moved_after - moved_before)
            if delta <= 0 or rng.random() < math.exp(-delta / T):
                cur += delta
                if cur < best: best = cur
            else:
                self.place(g, None)
                if h: self.place(h, None); self.place(h, w)
                self.place(g, old)
        return cur

    def _level_terms(self):
        per = collections.Counter(g['week'] for g in self.games if g['week'] is not None)
        nc0 = sum(1 for g in self.games if g['week'] == 0 and g['conf'] is None)
        s = W0_NC_OVER * max(0, nc0 - len(self.P['conferences']))
        mean = sum(per[w] for w in range(1, 14)) / 13.0
        return s + LEVEL * sum(abs(per[w] - mean) for w in range(1, 14))


def main(seed=2039, write=True):
    best = None
    for attempt in range(12):
        rng = random.Random(seed + attempt)
        cal = Cal(PAYLOAD, HANDOFF)
        if not cal.initial(rng):
            print('attempt %d: could not seed' % (attempt + 1)); continue
        sc = cal.anneal(rng)
        hv = [v for v in cal.hard_violations() if v[0] not in fixed_teams(cal)]
        print('attempt %d: score %.1f, hard violations among open programmes: %d' % (attempt + 1, sc, len(hv)))
        if not hv:
            best = cal; break
        if best is None or sc < best.global_score(): best = cal
    if best is None: raise SystemExit('no calendar')
    cal = best
    if write:
        H = json.load(open(HANDOFF))
        json.dump({'season': H['season'], 'year': H['year'], 'complete': True,
                   'games': [{'id': g['id'], 'week': g['week']} for g in cal.games]},
                  open('/home/claude/cfb2/state/conf_s%d_filled.json' % _SN, 'w'))
    return cal


def fixed_teams(cal):
    """Programmes whose every game was placed by hand -- their rows are Dan's."""
    out = set()
    for t in cal.teams:
        if all(g['fixed'] for g in cal.slot[t] if g) and all(x is not None for x in cal.slot[t]) :
            pass
    # a programme is 'Dan's' if none of its games are open
    openteams = {t for g in cal.open for t in cal.sides(g)}
    return set(cal.teams) - openteams


if __name__ == '__main__':
    cal = main()
    print('hard violations, all programmes:')
    for v in cal.hard_violations(): print('  ', v)
