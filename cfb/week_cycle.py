"""One weekly turn: record the Gameview pick, play the week, print the report, rebuild
the Media Pool page, print the headline box scores, and the next week's candidates.
Usage: python3 week_cycle.py <week> <gameview host>
(The two artifacts still have to be published afterwards: season_viewer.html, media_pool.html.)"""
import sys, subprocess, shutil
sys.path.insert(0, '/home/claude/cfb2')
H = '/home/claude/cfb2'


def headline_boxes(week, gv_host):
    import season as SE, pbp_engine as E
    from games_db import load_db
    db = load_db(); s = SE.load_state()
    rk = {t: r for r, t in s['media_poll_prev'] if r <= 25}
    if s.get('committee_official') and s.get('committee_poll_current'):
        rk = {t: r for r, t in s['committee_poll_current'] if r <= 25}
    for w, gid in s['results']:
        if w != week: continue
        b = db[gid]; h, a = b['home'], b['away']
        upset = (h in rk or a in rk) and ((b['home_score'] > b['away_score']) != (rk.get(h, 99) < rk.get(a, 99)))
        both = h in rk and a in rk
        if not (h == gv_host or upset or both): continue
        st = b['stats']; P = {p['pid']: p for t in (h, a) for p in E.ROSTERS.get(t, [])}
        rows = []
        for pid, x in st.items():
            p = P.get(pid)
            if not p: continue
            rows.append((p['team'], p['name'], p['pos'], x.get('PassYds', 0), x.get('PassTD', 0), x.get('INT', 0),
                         x.get('RushYds', 0), x.get('RushTD', 0), x.get('RecYds', 0), x.get('RecTD', 0),
                         x.get('INT_def', 0), x.get('Sacks', 0)))
        tag = lambda t: ('#%d ' % rk[t] if t in rk else '') + t
        print('%s %d, %s %d%s%s  inj: %s' % (tag(h), b['home_score'], tag(a), b['away_score'], ' OT' if b.get('ot') else '',
              '  [GAMEVIEW]' if h == gv_host else '', [(i['name'], i['pos'], i['weeks_out']) for i in b['injuries'] if i['weeks_out'] >= 3]))
        for r in sorted(rows, key=lambda r: -(r[3] + r[6] + r[8] + 40 * r[10] + 30 * r[11]))[:3]:
            print('    %-16s %-22s %-2s pass %d/%d/%d rush %d/%d rec %d/%d int %d sk %d' % r)


if __name__ == '__main__':
    week = int(sys.argv[1]); host = ' '.join(sys.argv[2:])
    subprocess.run(['python3', H + '/gameview.py', 'pick', str(week), host], check=True)
    shutil.copy(H + '/state/season_state.pkl', H + '/state/season_state.pkl.pre_w%d' % week)
    subprocess.run(['python3', H + '/play_week.py', str(week)], check=True)
    print('=' * 70)
    subprocess.run(['python3', H + '/week_report.py', str(week)], check=True)
    print('=' * 70)
    headline_boxes(week, host)
    subprocess.run(['python3', H + '/export_media_pool.py'], check=True, capture_output=True)
    subprocess.run(['python3', '-c', "import sys; sys.path.insert(0,'%s'); import build_pages; build_pages.build('%s/media_pool_template.html','%s/state/media_pool_view.json','%s/media_pool.html')" % (H, H, H, H)], check=True)
    print('=' * 70)
    subprocess.run(['python3', H + '/gameview.py', str(week + 1)], check=True)
