"""Drive the remaining regular season, one week at a time.

Keeps the weekly rhythm the canon flow had:
  * simulate the week (with the expect_week guard)
  * recompute the media poll, carrying last week's ballot as the inertia anchor
  * from week 10, the selection committee's ranking runs alongside the media poll
  * the Ryskamp pools are captured at the week 6 and week 10 checkpoints and are
    STRICT SUBSETS: twenty -> ten -> four finalists
"""
import sys, pickle
sys.path.insert(0, '/home/claude/cfb2')
# Dan's rule, 2039: the first committee ranking comes out AFTER WEEK 8 (it was week 6 in
# 2038 by hand, week 10 in the engine before that). The media poll is the ranking of
# record until then.
COMMITTEE_START = 8
import season as SE, media_poll as MP, pbp_engine as E, subdivision as SUB
from games_db import load_db


def poll_update(s, db, seed):
    prev = list(s.get('media_poll_current') or [])
    ranking, _pts = MP.compute_media_poll(s, db, seed=seed)
    s['media_poll_prev'] = [(int(r), t) for r, t in prev]
    s['media_poll_current'] = [(int(r), t) for r, t in ranking]
    return s


def ryskamp_pool(s, db, n, restrict=None):
    """Rank candidates on season stats so far; optionally only within an existing pool."""
    import committee as CM
    # The board has to be at least as deep as the pool asked for -- the default is five,
    # which could never fill a twenty -- and each entry is (pid, player, stats, points),
    # so the NAME is on the player record, not at index 0 (that is the pid). Both were
    # wrong here; fixed 2039 when the pools were rebuilt.
    aw = CM.compute_awards(s, n_heisman=max(n, 40))
    ent = aw.get('heisman') or []
    rows = []
    for e in ent:
        pl = e[1] if isinstance(e, (list, tuple)) and len(e) > 1 else None
        nm = pl['name'] if isinstance(pl, dict) and pl.get('name') else (e[0] if isinstance(e, (list, tuple)) else e)
        rows.append(nm if isinstance(nm, str) else str(nm))
    if restrict is not None:
        rows = [r for r in rows if r in restrict]
    return rows[:n]


def run(upto=14, start_seed=10000):
    SUB.register(E)
    s = SE.load_state()
    while s['next_week'] <= upto:
        wk = s['next_week']
        SE.simulate_window(1, expect_week=wk)
        s = SE.load_state()
        db = load_db()
        s = poll_update(s, db, seed=start_seed + wk)
        # keep the ballot after every week, so the viewer can badge a game with the rank a
        # team held going INTO it (Dan, 2039)
        s.setdefault('media_history', {})[wk] = [t for _r, t in s['media_poll_current']][:25]
        if wk >= COMMITTEE_START:
            import committee as CM
            try:
                rank = CM.committee_rank(s, db)
                cur = rank[0] if isinstance(rank, tuple) else rank
                s['committee_poll_prev'] = list(s.get('committee_poll_current') or [])
                s['committee_poll_current'] = [(i + 1, t) for i, t in enumerate(
                    [x[1] if isinstance(x, (list, tuple)) else x for x in cur])][:40]
            except Exception as ex:
                print('  [committee] %s' % ex)
        SE.save_state(s)
        top = s['media_poll_current'][:3]
        print('week %-2d done | top3: %s' % (
            wk, ', '.join('%s (%d-%d)' % (t, s['record'][t]['W'], s['record'][t]['L']) for _r, t in top)))
    return s


if __name__ == '__main__':
    upto = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    run(upto)
