"""Travel the last known non-conference board inside the page itself.

Version 1 of the Scheduling Office was published without the `db` capability
declared, so `claude.use('db')` resolved null and nothing Dan entered was ever saved.
The capability is declared now, but a board whose only copy lives behind a runtime
call has no floor when that call fails. This writes the last known board into the page
payload as `seed`, which the page lays down ONLY when the database has nothing for the
season or cannot be read -- a restored board always wins, since the seed cannot know
what was deleted.

Converts the hand-off shape {host, visitor} to the page's internal {a, b, host}, and
validates every name against the payload so a stale board cannot inject a programme
that is not in this season's universe.
"""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')


# The board for the season the state says is OPEN. This was pinned to s13 and would
# have filled the 2038 board again on top of 2039's bookings; derived from state now.
def _season_board(suffix):
    import season as _SE
    return '/home/claude/cfb2/state/noncon_s%d%s.json' % (_SE.load_state().get("season"), suffix)
BOARD = _season_board('_partial')
PAYLOAD = '/home/claude/cfb2/state/schedule_board.json'


def main(board=BOARD, payload=PAYLOAD, write=True):
    b = json.load(open(board))
    p = json.load(open(payload))
    if b.get('season') != p.get('season'):
        raise SystemExit('season mismatch: board %s, payload %s'
                         % (b.get('season'), p.get('season')))
    FBS = {t['name'] for t in p['teams']}
    SUB = {s['name'] for s in p['subs']}
    seed, dropped = [], []
    for g in b['games']:
        if g.get('locked'):
            continue                      # re-seeded from canon by the page
        h, v = g['host'], g['visitor']
        if h not in FBS or (v not in FBS and v not in SUB):
            dropped.append((h, v)); continue
        seed.append({'a': h, 'b': v, 'host': h, 'sub': bool(g.get('sub')),
                     'auto': bool(g.get('auto')), 'week': g.get('week')})
    p['seed'] = seed
    p['seed_from'] = board.rsplit('/', 1)[-1]
    if write:
        json.dump(p, open(payload, 'w'))
    return seed, dropped


if __name__ == '__main__':
    seed, dropped = main()
    print('seeded %d unlocked games into the payload' % len(seed))
    if dropped:
        print('DROPPED (not in this season\'s universe):')
        for h, v in dropped:
            print('   %s vs %s' % (h, v))
