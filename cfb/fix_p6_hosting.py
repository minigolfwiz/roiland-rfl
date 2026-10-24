"""Host repair for the non-conference board (Dan, 2042): power programmes should
not be on the road at non-power programmes except by exception.

Local search over host flips on AUTO, non-guest games only (Dan's bookings and locked
rivalries are never touched). Cost: a P6 visiting an L6 = 3; a slate that is all-home or
all-road = 10; flipping against an owed return ground = 2. Single flips, then pairs of
flips that share a programme.
"""
import sys, json, itertools
sys.path.insert(0, '/home/claude/cfb2')
import fill_noncon as F

def run(board_path, payload=F.PAYLOAD, write=True, w_away=2.4, w_allhome=1.2, w_oneP6=0.6):
    bd = F.Board(board_path, payload)
    T = bd.BY
    def bad(t):
        h, n = bd.home_(t), bd.filled(t)
        if n != F.SLOTS:
            return 0
        if h == 0:
            return 10
        if h == 1 and T[t]['tier'] == 'P6':
            return w_oneP6
        if h == F.SLOTS:
            # hosting all three is tolerable for a power programme (it makes up for
            # guaranteed road dates elsewhere); it stays a real cost for everyone else
            return w_allhome if T[t]['tier'] == 'P6' else 10
        return 0
    def gcost(g):
        h, v = g['host'], g['visitor']
        c = 0
        if v in T and h in T and T[v]['tier'] == 'P6' and T[h]['tier'] == 'L6':
            c += w_away
        at, _ = bd.owed(h, v) if h in T and v in T else (None, None)
        if at == 'away':          # h owes a trip to v, yet hosts
            c += 2
        return c
    def local(gs):
        teams = set()
        for g in gs:
            teams.add(g['host']);
            if g['visitor'] in T: teams.add(g['visitor'])
        return sum(gcost(g) for g in gs) + sum(bad(t) for t in teams)
    def flip(g):
        g['host'], g['visitor'] = g['visitor'], g['host']
    # index games by team for the pair moves
    def games_of(t): return [g for g in bd.games if g['host'] == t or g['visitor'] == t]
    flexible = [g for g in bd.games if g.get('auto') and not g['sub']]
    def total():
        return sum(gcost(g) for g in bd.games) + sum(bad(t) for t in T)
    start = total()
    for _ in range(50):
        improved = False
        for g in flexible:
            affected = list({id(x): x for t in (g['host'], g['visitor']) for x in games_of(t)}.values())
            before = local(affected)
            flip(g)
            if local(affected) < before:
                improved = True
            else:
                flip(g)
        if improved: continue
        for g1, g2 in itertools.combinations(flexible, 2):
            if not ({g1['host'], g1['visitor']} & {g2['host'], g2['visitor']}):
                continue
            affected = list({id(x): x for g in (g1, g2) for t in (g['host'], g['visitor']) for x in games_of(t)}.values())
            before = local(affected)
            flip(g1); flip(g2)
            if local(affected) < before:
                improved = True
            else:
                flip(g1); flip(g2)
        if not improved:
            break
    end = total()
    if write:
        bd.B['games'] = bd.games
        json.dump(bd.B, open(board_path, 'w'))
    return start, end

if __name__ == '__main__':
    print(run(F.BOARD))
