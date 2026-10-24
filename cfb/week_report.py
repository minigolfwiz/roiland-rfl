"""Print the week just played: ranked losers, top-10 winners, closest games, guest
record, and the media poll (ranks shown are the ballot going INTO the week).
Usage: python3 week_report.py <week>"""
import sys
sys.path.insert(0, '/home/claude/cfb2')
import season as SE
from games_db import load_db


def main(week):
    s = SE.load_state(); db = load_db(); T = set(s['record'])
    # ranks shown are the ranking of record going INTO the week: the committee board once
    # one exists, the media poll before that
    if s.get('committee_official') and s.get('committee_poll_current'):
        prev = {t: r for r, t in s['committee_poll_current']}
    else:
        prev = {t: r for r, t in s['media_poll_prev']}
    tag = lambda t: ('#%d ' % prev[t] if t in prev else '') + t + ('' if t in T else ' (guest)')
    rows = []
    for wk, gid in s['results']:
        if wk != week: continue
        b = db[gid]; h, a = b['home'], b['away']; hs, as_ = b['home_score'], b['away_score']
        win, lose = (h, a) if hs > as_ else (a, h)
        rows.append(dict(w=win, l=lose, ws=max(hs, as_), ls=min(hs, as_), m=abs(hs - as_),
                         rw=prev.get(win, 99), rl=prev.get(lose, 99), home=h,
                         guest=(h not in T or a not in T), ot=b.get('ot', 0)))
    line = lambda r: '%-28s %2d-%-2d  %-28s %s%s' % (tag(r['w']), r['ws'], r['ls'], tag(r['l']),
                                                     'at ' + r['home'] if r['home'] == r['l'] else '',
                                                     ' OT' if r.get('ot') else '')
    print('--- ranked losers ---')
    for r in sorted(rows, key=lambda r: r['rl']):
        if r['rl'] <= 25: print(line(r))
    print('--- top-10 winners vs unranked ---')
    for r in sorted(rows, key=lambda r: r['rw']):
        if r['rw'] <= 10 and r['rl'] > 25: print(line(r))
    print('--- closest (<=3) ---')
    for r in sorted(rows, key=lambda r: r['m']):
        if r['m'] <= 3: print(line(r))
    g = [r for r in rows if r['guest']]; gl = [r for r in g if r['w'] not in T]
    print('guest games %d, guest wins %d, avg margin %.1f' % (len(g), len(gl), sum(r['m'] for r in g) / max(1, len(g))))
    for r in gl: print('  GUEST WIN:', line(r))
    if s.get('committee_official'):
        return
    print('--- poll ---')
    for r, t in s['media_poll_current'][:25]:
        rec = s['record'][t]; p = prev.get(t)
        print('%2d. %-20s %d-%d  %s' % (r, t, rec['W'], rec['L'], ('(%+d)' % (p - r) if p else '(new)')))
    out = [t for t in prev if prev[t] <= 25 and t not in {x for _r, x in s['media_poll_current'][:25]}]
    print('dropped out:', out)


if __name__ == '__main__':
    main(int(sys.argv[1]))
