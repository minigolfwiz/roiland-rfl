"""Take Dan's finished non-conference board and install the 2036 season calendar.

Run this only after the rollover stage, since it writes the schedule the season will
actually be played on. Everything it touches is backed up first.

Usage:
    python3 install_schedule.py state/noncon_s11.json            # dry run + audit
    python3 install_schedule.py state/noncon_s11.json --commit   # write it to state
"""
import sys, json, shutil, collections, os
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
import conf_builder as CB
import subdivision as SUB

U = E.U
TSET = set(U["teams"])
STATE_DIR = '/home/claude/cfb2/state'


def guests_in(sched):
    """Which subdivision programs got invited, by the board rather than by assumption."""
    g = set()
    for wk, h, a, ic in sched:
        if h not in TSET:
            g.add(h)
        if a not in TSET:
            g.add(a)
    return sorted(g)


# Seed 909090 chosen from a sweep: it puts 11 games in week 0 with 88% of the league
# idle, which is where canon 2035 sat (11 games, 86%).
def install(board_path, seed=909090, commit=False):
    s = SE.load_state()
    # The rollover runs BEFORE this, so the state already holds the season about to be
    # played. Taking season+1 here (as the first cut did) files everything a year late.
    new_season = s.get("season")
    if s.get("next_week", 0) != 0 or s.get("results"):
        raise RuntimeError("season %d is already underway (week %s, %d results) — run the "
                           "rollover first, or this would overwrite a live schedule"
                           % (new_season, s.get("next_week"), len(s.get("results") or [])))

    # Locked rivalry hosts alternate against last season, but the rollover has already
    # cleared `s['sched']` by this point, so the previous slate is rebuilt from the games
    # database. Passing the empty `s['sched']` would silently hand every rivalry back to
    # the same host two years running.
    prev = s["sched"] or CB.prev_schedule(new_season - 1)
    sched, rep = CB.build(board_path, prev, seed=seed)
    CB.audit(sched, verbose=True)
    if not rep["ok"]:
        print("\nREFUSING TO INSTALL — the calendar did not pass its own checks.")
        return rep

    guests = guests_in(sched)
    print("\n  subdivision guests  %d" % len(guests))

    if not commit:
        print("\nDRY RUN. Re-run with --commit to install.")
        return rep

    # ---- backups before anything is written ----
    for f in ('state.pkl', 'sub_rosters.pkl', 'sub_coaches.pkl'):
        p = os.path.join(STATE_DIR, f)
        if os.path.exists(p):
            shutil.copy(p, p + '.pre_s%d_sched' % new_season)

    # ---- guest rosters for this season's invitees ----
    src = open('/home/claude/cfb2/gen_rosters.py').read()
    a = src.index('def derive_attrs('); b = src.index('rosters = {}', a)
    import random as _r
    ns = {'rng': _r.Random(seed)}
    exec(src[a:b], ns)
    import names_v2 as NV
    used = {p["name"] for r in E.ROSTERS.values() for p in r}
    sur = collections.Counter(n.split()[-1] for n in used)

    def fresh():
        n = NV.pick_name_v2(_r.Random(), used, surname_usage=sur, surname_cap=2)
        n = n[0] if isinstance(n, (tuple, list)) else n
        used.add(n); sur[n.split()[-1]] += 1
        return n

    rosters, coaches = SUB.generate(guests, seed=new_season * 1000 + 20250000,
                                    derive_attrs=ns['derive_attrs'], name_fn=fresh)
    SUB.save(rosters, coaches)

    s["sched"] = [tuple(r) for r in sched]
    s["sub_opponents"] = guests
    s["schedule_audit_s%d" % new_season] = {k: v for k, v in rep.items() if k != "fails"}
    SE.save_state(s)
    print("\nINSTALLED — %d games, %d guest programs with fresh rosters." % (len(sched), len(guests)))
    return rep


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    install(sys.argv[1], commit='--commit' in sys.argv)
