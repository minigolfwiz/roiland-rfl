"""Finish Dan's 2038 non-conference board around the games he booked by hand.

Dan's brief: fill the rest, and land as close as possible to 90% of the league playing
a subdivision guest. Everything he booked is untouched; everything this adds is marked
`auto: true`, so the Scheduling Office can show which games are its own and clear them
wholesale without disturbing his.

THE 90% TARGET IS PARITY-CONSTRAINED, which is why it cannot be hit exactly. There are
152 x 3 = 456 FBS dates. A guest game burns one date, an FBS-vs-FBS game burns two, so
the number of guest games must leave an EVEN remainder -- an odd count strands one FBS
date with nobody to pair against. 90% of 152 is 136.8, and 137 is odd, so the two legal
neighbours are 136 (89.47%) and 138 (90.79%). 136 is the closer of the two to 90%, and
that is what this aims at.

The hard rules are the ones the tool itself enforces, replicated here exactly rather
than approximated (see `why_not` / `why_not_sub` against the template's versions):
  * never the same conference -- that is a conference game
  * never a repeat pairing, and never more than three dates for anyone
  * at most TWO opponents from any one conference
  * one subdivision guest per programme, and each guest invited once in the league
Guests always travel, so a guest game is a home date for the host.

Soft goals, in the order they are traded off:
  1. nobody left hosting all three or travelling for all three
  2. two opponents from one conference avoided where an alternative exists
  3. regional games over cross-country ones, competitive matchups over mismatches,
     and an unreturned visit preferred -- the same instincts as the tool's own
     suggestion score, so the auto-filled games look like the hand-picked ones
"""
import sys, json, math, random, collections
sys.path.insert(0, '/home/claude/cfb2')


# The board for the season the state says is OPEN. This was pinned to s13 and would
# have filled the 2038 board again on top of 2039's bookings; derived from state now.
def _season_board(suffix):
    import season as _SE
    return '/home/claude/cfb2/state/noncon_s%d%s.json' % (_SE.load_state().get("season"), suffix)
BOARD = _season_board('_partial')
PAYLOAD = '/home/claude/cfb2/state/schedule_board.json'
SLOTS = 3
GUEST_SHARE = 0.90
SEED = 20380208


class Board:
    def __init__(self, board_path, payload_path):
        self.P = json.load(open(payload_path))
        self.B = json.load(open(board_path))
        self.BY = {t['name']: t for t in self.P['teams']}
        self.SUBBY = {s['name']: s for s in self.P['subs']}
        self.conf = {t['name']: t['conf'] for t in self.P['teams']}
        self.games = list(self.B['games'])
        self._index()

    # ---------------------------------------------------------------- indexing
    def _index(self):
        self.by_team = collections.defaultdict(list)
        self.pairs = set()
        self.subs_used = set()
        for g in self.games:
            h, v = g['host'], g['visitor']
            self.pairs.add(frozenset((h, v)))
            if v in self.SUBBY:
                self.subs_used.add(v)
                self.by_team[h].append(g)
            else:
                self.by_team[h].append(g)
                self.by_team[v].append(g)

    def filled(self, t):  return len(self.by_team[t])
    def open_(self, t):   return SLOTS - self.filled(t)
    def home_(self, t):   return sum(1 for g in self.by_team[t] if g['host'] == t)
    def away_(self, t):   return sum(1 for g in self.by_team[t] if g['host'] != t)
    def has_sub(self, t): return any(g['visitor'] in self.SUBBY for g in self.by_team[t])

    def conf_count(self, t, c):
        n = 0
        for g in self.by_team[t]:
            o = g['visitor'] if g['host'] == t else g['host']
            if o in self.BY and self.conf[o] == c:
                n += 1
        return n

    # ---------------------------------------------------------- the hard rules
    def why_not(self, a, b):
        if a == b:                                  return 'same team'
        if b not in self.BY:                        return 'unknown'
        if self.conf[a] == self.conf[b]:            return 'same conference'
        if frozenset((a, b)) in self.pairs:         return 'already scheduled'
        if self.open_(a) <= 0:                      return 'no openings (a)'
        if self.open_(b) <= 0:                      return 'no openings (b)'
        if self.conf_count(a, self.conf[b]) >= 2:   return 'already two from ' + self.conf[b]
        if self.conf_count(b, self.conf[a]) >= 2:   return 'they already have two'
        return None

    def why_not_sub(self, a, name):
        if self.has_sub(a):                         return 'already hosting a guest'
        if name in self.subs_used:                  return 'guest already booked'
        if self.open_(a) <= 0:                      return 'no openings'
        return None

    # ------------------------------------------------------------------ adding
    def add(self, host, visitor, is_sub):
        g = {'host': host, 'visitor': visitor, 'sub': bool(is_sub),
             'locked': False, 'auto': True, 'week': None}
        self.games.append(g)
        self.pairs.add(frozenset((host, visitor)))
        self.by_team[host].append(g)
        if is_sub:
            self.subs_used.add(visitor)
        else:
            self.by_team[visitor].append(g)
        return g

    def undo(self, g):
        self.games.remove(g)
        self.pairs.discard(frozenset((g['host'], g['visitor'])))
        self.by_team[g['host']].remove(g)
        if g['sub']:
            self.subs_used.discard(g['visitor'])
        else:
            self.by_team[g['visitor']].remove(g)

    # ------------------------------------------------------------------ geometry
    def dist(self, a, b):
        x = (self.BY.get(a) or self.SUBBY.get(a) or {}).get('xy')
        y = (self.BY.get(b) or self.SUBBY.get(b) or {}).get('xy')
        return None if not x or not y else math.hypot(x[0] - y[0], x[1] - y[1])

    def owed(self, a, b):
        o = next((x for x in self.BY[a]['owed'] if x['opp'] == b), None)
        if o:
            return o['at'], o['year']
        s = (self.BY[a].get('series') or {}).get(b)
        if s and s['n'] >= 2 and s['same']:
            return ('away' if s['home'] else 'home'), s['year']
        return None, None


# ------------------------------------------------------------------- the target
def guest_target(bd):
    """How many programmes should end up hosting a guest, given parity."""
    open_dates = sum(bd.open_(t) for t in bd.BY)
    have = sum(1 for t in bd.BY if bd.has_sub(t))
    ideal = GUEST_SHARE * len(bd.BY)
    best = None
    for k in range(0, open_dates + 1):
        if (open_dates - k) % 2:            # the FBS remainder must be pairable
            continue
        total = have + k
        if total > len(bd.BY):
            break
        score = abs(total - ideal)
        if best is None or score < best[0]:
            best = (score, k, total)
    return best[1], best[2], have, open_dates


# ------------------------------------------------------------------ guest stage
def place_guests(bd, k, rng):
    """Give k more programmes a subdivision guest.

    Chosen by who most needs a home date: a guest always travels, so this is the one
    booking that is guaranteed to be a home game, and spending them on programmes
    already hosting enough would force road-heavy slates elsewhere. Each host then
    takes the nearest guest nobody has claimed, which keeps guarantee games regional.
    """
    cands = [t for t in bd.BY if bd.open_(t) > 0 and not bd.has_sub(t)]
    cands.sort(key=lambda t: (bd.home_(t) - bd.away_(t), -bd.open_(t), rng.random()))
    placed = 0
    for t in cands:
        if placed >= k:
            break
        pool = [s for s in bd.SUBBY if s not in bd.subs_used]
        if not pool:
            break
        pool.sort(key=lambda s: bd.dist(t, s) if bd.dist(t, s) is not None else 1e9)
        for s in pool[:12]:
            if bd.why_not_sub(t, s) is None:
                bd.add(t, s, True)
                placed += 1
                break
    return placed


# -------------------------------------------------------------------- FBS stage
def pair_score(bd, a, b):
    """Mirrors the tool's own suggestion score, plus the balance terms."""
    A, B = bd.BY[a], bd.BY[b]
    d = bd.dist(a, b)
    d = 250 if d is None else d
    s = max(0, 120 - d) * 0.42
    if A['state'] == B['state']:
        s += 34
    s -= abs(A['prestige'] - B['prestige']) * 0.52
    at, year = bd.owed(a, b)
    if at:
        s += 22 + (year - 2025 - (bd.P['season'] - 1 - bd.P['return_window'])) * 4
    if A['tier'] == 'P6' and B['tier'] == 'P6':
        s += 12
    # keep the conference mix wide: a second from one conference is legal but duller
    if bd.conf_count(a, B['conf']) >= 1: s -= 60
    if bd.conf_count(b, A['conf']) >= 1: s -= 60
    s += bd.open_(b) * 7
    return s


def choose_host(bd, a, b):
    """Whoever has hosted least; the owed side overrides, then the bigger brand."""
    at, _ = bd.owed(a, b)
    if at == 'home': return a
    if at == 'away': return b
    ha, hb = bd.home_(a), bd.home_(b)
    if ha != hb:
        return a if ha < hb else b
    return a if bd.BY[a]['prestige'] >= bd.BY[b]['prestige'] else b


def fill_fbs(bd, rng, tries=400):
    """Most-constrained-first with restarts.

    A programme with three dates open and few legal partners has to be served before
    one with a single date and the whole league to choose from, or the last few teams
    are left holding dates only each other can fill -- and they are usually in the
    same conference. Restarting on a dead end is cheaper than unwinding one.
    """
    added = []
    while True:
        need = [t for t in bd.BY if bd.open_(t) > 0]
        if not need:
            return added, True
        # fewest legal partners first, then most dates open
        def options(t):
            return [o for o in need if o != t and bd.why_not(t, o) is None]
        ranked = sorted(need, key=lambda t: (len(options(t)), -bd.open_(t), rng.random()))
        a = ranked[0]
        opts = options(a)
        if not opts:
            return added, False
        opts.sort(key=lambda b: -pair_score(bd, a, b))
        b = opts[0]
        host = choose_host(bd, a, b)
        added.append(bd.add(host, b if host == a else a, False))


def main(write=True):
    rng = random.Random(SEED)
    k, total, have, open_dates = guest_target(Board(BOARD, PAYLOAD))
    print("guest target: %d programmes (%.2f%%) -- %d already, %d to add"
          % (total, 100 * total / 152, have, k))
    print("   90%% of 152 is %.1f; 137 is odd and would strand an FBS date, so the legal "
          "neighbours are 136 and 138" % (GUEST_SHARE * 152))

    for attempt in range(60):
        bd = Board(BOARD, PAYLOAD)
        rng = random.Random(SEED + attempt)
        placed = place_guests(bd, k, rng)
        added, ok = fill_fbs(bd, rng)
        if ok and placed == k:
            print("   solved on attempt %d: %d guests + %d FBS games added"
                  % (attempt + 1, placed, len(added)))
            break
    else:
        raise SystemExit("could not complete the board")

    bd.B['games'] = bd.games
    bd.B['complete'] = all(bd.open_(t) == 0 for t in bd.BY)
    bd.B['open_dates'] = sum(bd.open_(t) for t in bd.BY)
    if write:
        json.dump(bd.B, open(BOARD, 'w'))
    return bd


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------- repair
def rebalance(bd, rounds=400):
    """Flip hosts to cut the all-home and all-road slates.

    Only AUTO, non-guest games are ever flipped. Dan's own bookings carry his venue
    choices and are left exactly as he made them, and a guest cannot be flipped at all
    because subdivision programmes always travel. So the repair works with whatever
    slack the auto games happen to provide, and stops when there is none left.
    """
    def bad(t):
        h, n = bd.home_(t), bd.filled(t)
        return 1 if (n == SLOTS and h in (0, SLOTS)) else 0

    def total():
        return sum(bad(t) for t in bd.BY)

    before = total()
    for _ in range(rounds):
        moved = False
        for g in bd.games:
            if not g.get('auto') or g['sub']:
                continue
            h, v = g['host'], g['visitor']
            was = bad(h) + bad(v)
            g['host'], g['visitor'] = v, h
            now = bad(v) + bad(h)
            if now < was:
                moved = True
            else:
                g['host'], g['visitor'] = h, v
        if not moved:
            break
    return before, total()
