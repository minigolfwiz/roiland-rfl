"""Install a calendar Dan built by hand in the Conference Office.

`install_schedule.py` BUILDS a calendar: it takes a non-conference board and hands it to
`conf_builder` to invent the weeks. That path is now one of two, and this is the other.
Dan placed all 980 games of 2038 himself, so nothing is invented here -- the file is
validated against the slate it was built from and written as-is.

Three reasons this is a separate module rather than a flag on the old one:

  * `conf_builder.audit` still fails a board for any bye in week 1, which was a league
    rule until 2038 and is not one now. Running Dan's calendar through it would reject a
    legal season.
  * the old path owns the slate -- which 63 fixtures a conference plays, who hosts --
    and here that is already decided. The only open question is whether the file still
    matches the slate it came from, which is a different check.
  * a hand-built calendar deserves a stricter fixture audit, because a tool that moves
    games around can lose or duplicate one in a way a generator never would.

Usage:
    python3 install_hand_schedule.py state/conf_sched_s13.json            # dry run
    python3 install_hand_schedule.py state/conf_sched_s13.json --commit   # write it
"""
import sys, json, os, shutil, collections, random
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
import subdivision as SUB

U = E.U
TSET = set(U["teams"])
TC = U["team_conf"]
STATE_DIR = '/home/claude/cfb2/state'
BOARD = '/home/claude/cfb2/state/conf_board.json'

WEEKS = list(range(15))
BYES = 3
FULL_WEEKS = [14]          # Dan's 2038 rule: week 1 may now be a bye
GAMES_PER_TEAM = 12
CONF_GAMES = 9


def audit(games, board):
    """Everything that must be true before this becomes a season. Returns (fails, info).

    Written against the rules rather than against the generator, so it catches a file
    that has been edited by hand, by a tool, or by a tool with a bug in it.
    """
    fails = []
    teams = board["teams"]
    per = collections.defaultdict(list)
    for g in games:
        for t in (g["host"], g["visitor"]):
            if t in teams:
                per[t].append(g)

    if len(per) != len(teams):
        fails.append("programmes scheduled: %d, expected %d" % (len(per), len(teams)))

    # ---- per programme: load, byes, double-booking ----
    consec, byes_in_full, dbl, wrong_n, wrong_byes = [], [], [], [], []
    for t, gs in per.items():
        if len(gs) != GAMES_PER_TEAM:
            wrong_n.append((t, len(gs)))
        wks = [g["week"] for g in gs]
        if len(set(wks)) != len(wks):
            dbl.append(t)
        b = sorted(set(WEEKS) - set(wks))
        if len(b) != BYES:
            wrong_byes.append((t, len(b)))
        for w in b:
            if w in FULL_WEEKS:
                byes_in_full.append((t, w))
        if any(b[i + 1] - b[i] == 1 for i in range(len(b) - 1)):
            consec.append((t, b))
    for label, bad in (("games per programme", wrong_n), ("byes per programme", wrong_byes),
                       ("double-booked", dbl), ("byes in a full slate", byes_in_full),
                       ("consecutive byes", consec)):
        if bad:
            fails.append("%s: %d -- %s" % (label, len(bad), bad[:4]))

    # ---- the slate must be EXACTLY what the board specified ----
    want = collections.Counter()
    for c in board["conferences"]:
        for g in c["games"]:
            want[(c["conference"], frozenset((g["a"], g["b"])))] += 1
    for n in board["noncon"]:
        want[(None, frozenset((n["host"], n["visitor"])))] += 1
    got = collections.Counter((g.get("conf"), frozenset((g["host"], g["visitor"])))
                              for g in games)
    added, missing = got - want, want - got
    if added or missing:
        fails.append("the fixture list changed: %d added %s, %d missing %s"
                     % (sum(added.values()), [tuple(k[1]) for k in list(added)[:3]],
                        sum(missing.values()), [tuple(k[1]) for k in list(missing)[:3]]))

    # ---- conference shape ----
    for c in board["conferences"]:
        gs = [g for g in games if g.get("conf") == c["conference"]]
        deg = collections.Counter()
        host = collections.Counter()
        for g in gs:
            deg[g["host"]] += 1
            deg[g["visitor"]] += 1
            host[g["host"]] += 1
        if set(deg.values()) != {CONF_GAMES}:
            fails.append("%s: conference games per team %s"
                         % (c["conference"], sorted(set(deg.values()))))
        spread = sorted(host.get(t, 0) for t in c["roster"])
        if spread and spread[-1] - spread[0] > 1:
            fails.append("%s: conference home games %s" % (c["conference"], spread))

    # ---- locked games: right week, right host ----
    placed = {}
    for g in games:
        placed[frozenset((g["host"], g["visitor"]))] = g
    for c in board["conferences"]:
        for L in c["locked"]:
            g = placed.get(frozenset((L["a"], L["b"])))
            if not g:
                fails.append("locked rivalry missing: %s / %s" % (L["a"], L["b"]))
            elif g["week"] != L["week"]:
                fails.append("locked %s / %s on week %s, must be %d"
                             % (L["a"], L["b"], g["week"], L["week"]))
            elif g["host"] != L["host"]:
                fails.append("locked %s / %s hosted by %s, must be %s"
                             % (L["a"], L["b"], g["host"], L["host"]))
    for n in board["noncon"]:
        if not n["locked"]:
            continue
        g = placed.get(frozenset((n["host"], n["visitor"])))
        if g and g["week"] != n["week"]:
            fails.append("locked non-conference %s / %s on week %s, must be %s"
                         % (n["host"], n["visitor"], g["week"], n["week"]))

    # ---- a rivalry that demands an open week in front of it ----
    # The Conference Office does not enforce this, so it is checked here rather than
    # assumed. Will Tech / Tasson is the only pair carrying `bye_before` today; the
    # flag is read off the universe so a second one needs no code change.
    for p in U["fixed_pairs"]:
        if not p.get("bye_before"):
            continue
        for t in (p["team_a"], p["team_b"]):
            busy = [g for g in per.get(t, []) if g["week"] == p["week"] - 1]
            if busy:
                fails.append("%s must be idle in week %d (bye before the %s game) but plays"
                             % (t, p["week"] - 1, p["team_b"] if t == p["team_a"] else p["team_a"]))

    # ---- full slates ----
    for w in FULL_WEEKS:
        idle = [t for t in per if w not in {g["week"] for g in per[t]}]
        if idle:
            fails.append("week %d is a full slate but %d programmes are idle: %s"
                         % (w, len(idle), idle[:5]))

    # ---- information, not rules ----
    guests = sorted({t for g in games for t in (g["host"], g["visitor"]) if t not in TSET})
    runs = []
    for t, gs in per.items():
        seq = {g["week"]: ('H' if g["host"] == t else 'A') for g in gs}
        run = side = 0
        worst = 0
        for w in WEEKS:
            c = seq.get(w)
            if c is None:
                run = 0; side = 0; continue
            if c == side:
                run += 1
            else:
                side, run = c, 1
            worst = max(worst, run)
        if worst >= 4:
            runs.append((t, worst))
    info = {
        "games": len(games),
        "conference": sum(1 for g in games if g.get("conf")),
        "non_conference": sum(1 for g in games if not g.get("conf")),
        "guest_games": sum(1 for g in games if g["visitor"] not in TSET or g["host"] not in TSET),
        "guests": guests,
        "week0_playing": sum(1 for t in per if 0 in {g["week"] for g in per[t]}),
        "week1_byes": sum(1 for t in per if 1 not in {g["week"] for g in per[t]}),
        "long_runs": sorted(runs, key=lambda x: -x[1]),
        "by_week": {w: sum(1 for g in games if g["week"] == w) for w in WEEKS},
    }
    return fails, info


def install(path, commit=False, seed=909090):
    s = SE.load_state()
    new_season = s.get("season")
    if s.get("next_week", 0) != 0 or s.get("results"):
        raise RuntimeError("season %d is already underway (week %s, %d results) -- installing "
                           "now would overwrite a live schedule"
                           % (new_season, s.get("next_week"), len(s.get("results") or [])))

    board = json.load(open(BOARD))
    data = json.load(open(path))
    if data.get("season") != new_season:
        raise RuntimeError("file is season %s, state is season %s"
                           % (data.get("season"), new_season))
    if not data.get("complete"):
        raise RuntimeError("that board is not finished -- %d games still have no week"
                           % sum(1 for g in data["games"] if g.get("week") is None))
    games = data["games"]
    if any(g.get("week") is None for g in games):
        raise RuntimeError("the file says complete but some games have no week")

    fails, info = audit(games, board)
    print("%s -- season %d (%d)" % (os.path.basename(path), new_season, data["year"]))
    print("  %d games: %d conference, %d non-conference (%d against guests)"
          % (info["games"], info["conference"], info["non_conference"], info["guest_games"]))
    print("  subdivision guests invited : %d" % len(info["guests"]))
    print("  week 0 playing / week 1 byes: %d / %d" % (info["week0_playing"], info["week1_byes"]))
    print("  games by week: %s" % info["by_week"])
    if info["long_runs"]:
        print("  4+ home or road games in a row: %d programmes (worst %s)"
              % (len(info["long_runs"]), info["long_runs"][0]))
    if fails:
        print("\nREFUSING TO INSTALL:")
        for f in fails:
            print("   * %s" % f)
        return fails, info
    print("  audit: CLEAN")

    if not commit:
        print("\nDRY RUN. Re-run with --commit to install.")
        return fails, info

    # ---- backups before anything is written ----
    for f in ('state.pkl', 'sub_rosters.pkl', 'sub_coaches.pkl'):
        p = os.path.join(STATE_DIR, f)
        if os.path.exists(p):
            shutil.copy(p, p + '.pre_s%d_sched' % new_season)

    # ---- guest rosters, exactly as install_schedule.py builds them ----
    # `derive_attrs` is lifted out of gen_rosters.py rather than reimplemented, so a
    # guest roster is built by the same code as an FBS one.
    src = open('/home/claude/cfb2/gen_rosters.py').read()
    a = src.index('def derive_attrs('); b = src.index('rosters = {}', a)
    ns = {'rng': random.Random(seed)}
    exec(src[a:b], ns)
    import names_v2 as NV
    used = {p["name"] for r in E.ROSTERS.values() for p in r}
    sur = collections.Counter(n.split()[-1] for n in used)

    def fresh():
        n = NV.pick_name_v2(random.Random(), used, surname_usage=sur, surname_cap=2)
        n = n[0] if isinstance(n, (tuple, list)) else n
        used.add(n); sur[n.split()[-1]] += 1
        return n

    rosters, coaches = SUB.generate(info["guests"], seed=new_season * 1000 + 20250000,
                                    derive_attrs=ns['derive_attrs'], name_fn=fresh)
    SUB.save(rosters, coaches)

    # ---- the schedule itself: (week, home, away, is_conference) ----
    sched = [(g["week"], g["host"], g["visitor"], bool(g.get("conf"))) for g in games]
    sched.sort(key=lambda r: (r[0], r[1]))
    s["sched"] = [tuple(r) for r in sched]
    s["sub_opponents"] = info["guests"]
    s["schedule_audit_s%d" % new_season] = {
        "source": "hand-built in the Conference Office",
        "games": info["games"], "conference": info["conference"],
        "non_conference": info["non_conference"], "guests": len(info["guests"]),
        "week0_playing": info["week0_playing"], "week1_byes": info["week1_byes"],
        "long_runs": len(info["long_runs"]),
    }
    SE.save_state(s)
    print("\nINSTALLED -- %d games, %d guest programmes with fresh rosters." % (len(sched), len(info["guests"])))
    return fails, info


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    install(sys.argv[1], commit='--commit' in sys.argv)
