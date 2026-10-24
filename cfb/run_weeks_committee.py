"""Simulate a week, then move Dan's committee board on what happened."""
import sys
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, media_poll as MP, pbp_engine as E, subdivision as SUB
import committee_poll as CP
from games_db import load_db


def run(upto, start_seed=360000):
    SUB.register(E)
    out = []
    while True:
        s = SE.load_state()
        wk = s['next_week']
        if wk > upto:
            break
        SE.simulate_window(1, expect_week=wk)
        s = SE.load_state()
        db = load_db()
        prev = list(s.get('media_poll_current') or [])
        ranking, _ = MP.compute_media_poll(s, db, seed=start_seed + wk)
        s['media_poll_prev'] = [(int(r), t) for r, t in prev]
        s['media_poll_current'] = [(int(r), t) for r, t in ranking]
        prior = [t for _r, t in sorted(s.get('committee_poll_current') or [])]
        top, moves, dropped = CP.weekly(s, db, prior, wk)
        s['committee_poll_prev'] = list(s.get('committee_poll_current') or [])
        s['committee_poll_current'] = [(i + 1, t) for i, t in enumerate(top)]
        s.setdefault('committee_history', {})[str(wk)] = top
        SE.save_state(s)
        out.append(CP.render(moves, dropped, s, wk, 2025 + s['season']))
    return out


if __name__ == '__main__':
    for block in run(int(sys.argv[1]) if len(sys.argv) > 1 else 14):
        print(block)
        print()
