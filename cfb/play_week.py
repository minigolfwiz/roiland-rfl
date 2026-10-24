"""Play one week and leave every artifact payload current.

Written because the season page went stale twice: the week was simulated, the page was
not rebuilt, and Dan opened a viewer showing the previous week. Simulating and exporting
are now one action, so the only step left outside this script is publishing the file.

Usage:  python3 play_week.py <week>
"""
import sys, subprocess
sys.path.insert(0, '/home/claude/cfb2')
# Dan's rule, 2039: the first committee ranking comes out AFTER WEEK 8 (it was week 6 in
# 2038 by hand, week 10 in the engine before that). The media poll is the ranking of
# record until then.
COMMITTEE_START = 8


def main(week):
    import season as SE
    s = SE.load_state()
    if s["next_week"] != week:
        raise SystemExit("WEEK GUARD: state is at week %d, you asked for %d"
                         % (s["next_week"], week))
    s = SE.simulate_window(1, expect_week=week)

    # The media poll, and from week 10 the committee, are part of playing a week -- not a
    # separate chore. The first version of this script left them out and the season ran
    # six weeks with no poll at all before anyone noticed.
    import run_season as RS
    from games_db import load_db
    s = SE.load_state()
    s = RS.poll_update(s, load_db(), seed=10000 + week)
    # keep the ballot after every week, so the viewer can badge a game with the rank a
    # team held going INTO it (Dan, 2039)
    s.setdefault('media_history', {})[week] = [t for _r, t in s['media_poll_current']][:25]
    # From 2038 the committee board is Dan's, built by hand in the Committee Ballot and
    # written by `install_committee.py`. This script used to generate one from
    # `committee_rank` at week 10, which would now silently overwrite the board of
    # record the moment the season reached week 10. The computer order is still
    # available -- `export_committee_week.py` recomputes it every week as the starting
    # point for the ballot -- it just no longer gets stored as if it were the ranking.
    if s.get("committee_official"):
        cur = s.get("committee_poll_current") or []
        print("  committee: hand-built board of record kept (%d teams, top: %s)"
              % (len(cur), cur[0][1] if cur else "-"))
    elif week >= COMMITTEE_START:
        import committee as CM
        db = load_db()
        try:
            rank = CM.committee_rank(s, db)
            cur = rank[0] if isinstance(rank, tuple) else rank
            s["committee_poll_prev"] = list(s.get("committee_poll_current") or [])
            s["committee_poll_current"] = [(i + 1, t) for i, t in enumerate(
                [x[1] if isinstance(x, (list, tuple)) else x for x in cur])][:40]
        except Exception as ex:
            print("  [committee] %s" % ex)
    # Ryskamp nomination checkpoints (Dan's 2037 ruling): the twenty after week 6, the
    # ten after week 10 as a strict subset. 2039 ran without either because this script
    # never took them; they had to be rebuilt from the box scores. Never again.
    try:
        from games_db import load_db as _ldb
        _db = _ldb(); _key = 'ryskamp_s%d' % s.get('season', 1)
        if week == 6:
            s[_key] = {'twenty': RS.ryskamp_pool(s, _db, 20), 'week': 6, 'closed': False}
            print("  ryskamp: twenty named")
        elif week == 10 and s.get(_key, {}).get('twenty'):
            s[_key]['ten'] = RS.ryskamp_pool(s, _db, 10, restrict=set(s[_key]['twenty']))
            print("  ryskamp: cut to ten")
    except Exception as ex:
        print("  [ryskamp] %s" % ex)
    SE.save_state(s)
    print("played week %d | next_week %d | %d results" % (week, s["next_week"], len(s["results"])))
    print("  poll: %s" % ", ".join("%d %s" % (r, t) for r, t in s["media_poll_current"][:5]))
    for cmd in (['python3', 'export_schedule_view.py'],):
        subprocess.run(cmd, cwd='/home/claude/cfb2', check=True)
    from build_pages import build
    n, sz = build('season_viewer_template.html', 'state/schedule_view.json', 'season_viewer.html')
    print("rebuilt %s (%.1f KB) -- NOW PUBLISH IT" % (n, sz / 1024))
    return s


if __name__ == "__main__":
    main(int(sys.argv[1]))
