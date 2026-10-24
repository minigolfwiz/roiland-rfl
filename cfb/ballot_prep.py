"""The weekly hand-ranking sheet (Dan, 2039 week 8 on).

Prints last week's committee board with what each team did this week, then the
candidate pool: 20-30 unranked programmes ordered by the committee computer's score,
with record, this week's result and the quality/bad marks. Reads the ballot payload
`export_committee_week.py` writes, so run that first.
Usage: python3 ballot_prep.py
"""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import season as SE
from games_db import load_db

POOL = 28


def main():
    s = SE.load_state(); db = load_db()
    P = json.load(open('/home/claude/cfb2/state/committee_week.json'))
    week = P['week'] if P.get('stage') != 'CCG' else 15     # title games sit at week 15
    by = {t['name']: t for t in P['teams']}
    if s.get('committee_history') and s.get('committee_poll_current'):
        board = [t for _r, t in sorted(s['committee_poll_current'])][:25]
        prev_wk = max(int(k) for k in s['committee_history'])
        label = 'YOUR BOARD after week %d' % prev_wk
    else:   # first committee week: start from the media poll going into this week
        board = [t for _r, t in (s.get('media_poll_prev') or [])][:25]
        label = 'MEDIA POLL going into week %d (no committee board yet)' % week
    rank = {t: i + 1 for i, t in enumerate(board)}

    def this_week(t):
        g = [x for x in by[t]['games'] if x['w'] == week]
        if not g: return 'idle'
        x = g[0]
        opp = x['opp'] + (' (guest)' if x['sub'] else '') + (' [CCG]' if x.get('ccg') else '')
        r = ('#%d ' % rank[x['opp']] if x['opp'] in rank else '') + opp
        return '%s %d-%d %s %s%s' % ('W' if x['won'] else 'L', x['ps'], x['pa'], 'vs' if x['home'] else 'at', r,
                                     ' OT' if x.get('ot') else '')

    def marks(t):
        d = by[t]
        return 'QW %d  QL %d  BL %d' % (d['qw'], d['ql'], d['bl'])

    print('=== %s, with %s results ===' % (label, 'conference-final' if week == 15 else 'week %d' % week))
    for i, t in enumerate(board, 1):
        d = by[t]
        print('%2d. %-20s %d-%d  %-40s %s  comp #%d' % (i, t, d['W'], d['L'], this_week(t), marks(t), d['cRank']))
    print()
    print('=== CANDIDATES (not on your board), computer order ===')
    pool = [t for t in P['teams'] if t['name'] not in rank][:POOL]
    for t in pool:
        print('    %-20s %d-%d  %-40s %s  comp #%d  %s' % (t['name'], t['W'], t['L'], this_week(t['name']),
                                                        marks(t['name']), t['cRank'], t['conf']))


if __name__ == '__main__':
    main()
