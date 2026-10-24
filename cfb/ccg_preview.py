"""Preview the twelve conference finals without playing them.
Matchups from ccg.conf_top2 (the same call run_ccgs uses), the fixed site, both records,
the committee rank, this season's meeting if there was one, and the all-time series."""
import sys, re, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db
import ccg as C

def series(db, a, b):
    w = collections.Counter(); last = None
    for gid, box in db.items():
        if not isinstance(box, dict) or {box.get('home'), box.get('away')} != {a, b}: continue
        m = re.match(r'S(\d+)', str(gid)); sn = int(m.group(1)) if m else 0
        hw = box['home_score'] > box['away_score']
        win = box['home'] if hw else box['away']
        w[win] += 1
        key = (sn, 99 if 'PO' in str(gid) else (50 if 'CCG' in str(gid) else box.get('week', 0)))
        if last is None or key > last[0]: last = (key, win, box)
    return w, last

def preview():
    s = SE.load_state(); db = load_db(); U = E.U
    rk = {t: r for r, t in (s.get('committee_poll_current') or [])}
    sites = U.get('ccg_sites') or {}
    for conf, tl in U['conferences'].items():
        one, two = C.conf_top2(s, db, conf, tl)
        tier = U['tiers'][conf]; site = sites.get(conf)
        def tag(t):
            r = s['record'][t]
            return '%s%s (%d-%d, %d-%d)' % (('#%d ' % rk[t]) if t in rk else '', t, r['W'], r['L'], r['confW'], r['confL'])
        w, last = series(db, one, two)
        this = [box for gid, box in db.items() if str(gid).startswith('S%dW' % s['season']) and {box.get('home'), box.get('away')} == {one, two}]
        line = '[%s] %-15s %s vs %s @ %s' % (tier, conf + ':', tag(one), tag(two), ('%s, %s' % tuple(site)) if site else 'top seed')
        n = sum(w.values())
        if n:
            lead = max(w, key=w.get)
            lk, lw, lb = last
            line += '\n      series: %d meetings, %s leads %d-%d; last: %s won %d-%d (%d%s)' % (
                n, lead, w[lead], n - w[lead], lw, max(lb['home_score'], lb['away_score']), min(lb['home_score'], lb['away_score']),
                2025 + lk[0], ' playoff' if lk[1] == 99 else (' final' if lk[1] == 50 else ''))
        else:
            line += '\n      series: first meeting'
        if this:
            b = this[0]; hw = b['home_score'] > b['away_score']; win = b['home'] if hw else b['away']
            line += ' | this year: %s %d-%d (wk %d)' % (win, max(b['home_score'], b['away_score']), min(b['home_score'], b['away_score']), b.get('week', 0))
        print(line)

if __name__ == '__main__':
    preview()
