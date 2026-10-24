"""Build the conference schedule around Dan's non-conference board, then place the
whole season on the calendar.

Dan picks the 3 non-conference dates for all 152 programs in the Scheduling Office.
This module does everything else:

  1. CONFERENCE OPPONENTS -- 9 per team, drawn so that every one of the 35 locked
     in-conference rivalries is included rather than left to chance.
  2. HOSTS -- locked rivalry hosts alternate against last season, and every other
     conference game is oriented so each program hosts exactly 4 or 5 of them.
  3. THE CALENDAR -- 15 weeks (0-14). Dan's spec: 12 games, exactly 3 byes, most of
     them absorbed by a small week 0, and never two byes in a row. Weeks 1 and 14 are
     full slates; week 14 is rivalry week and carries the 34 pinned rivalry games.
  4. POLISH -- local search that breaks up long home or away runs without disturbing
     anything pinned.

The S11 scheduler was lost in the reset, so this is a rebuild measured against the
2035 calendar rather than against the old code: 11 games in week 0, 86% of the league
taking a week-0 bye, no consecutive byes anywhere, conference home games exactly 4 or 5,
and non-conference play front-loaded into the opening month.
"""
import sys, json, random, collections, itertools
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E
import networkx as nx

U = E.U
TEAMS = list(U["teams"])
TSET = set(TEAMS)
CONF = U["team_conf"]
PRESTIGE = U["prestige"]

WEEKS = list(range(15))
BYE_OK = [0] + list(range(2, 14))      # weeks 1 and 14 are full slates
MID = list(range(2, 14))
WEEK0_GAMES = 11                       # canon 2035: a small opening week

# locked rivalries, split by whether they are a conference game
RIV_CONF, RIV_NONCONF, FIXED_WEEK = {}, {}, {}
for _p in U["fixed_pairs"]:
    _k = frozenset((_p["team_a"], _p["team_b"]))
    FIXED_WEEK[_k] = _p["week"]
    (RIV_CONF if _p["is_conf"] else RIV_NONCONF)[_k] = _p
RIVAL_PAIRS = set(FIXED_WEEK)

# Some rivalries get an open week in front of them -- both programmes idle the week
# before, so the game is the only thing either has been pointing at. Dan's rule, set
# 2026-10-07 for Will Tech / Tasson. A pair listed here carries `bye_before: true` on
# its entry in `U["fixed_pairs"]`; this reads that flag rather than naming teams, so a
# second such rivalry needs no code change.
#
# IDLE_BEFORE maps a team to the week it must NOT play in. It is enforced as a hard
# constraint everywhere a game is placed or moved: `assign_weeks`, the ejection
# fallback, and both calendar optimisers. Missing any one of them would let a later
# pass quietly fill the week back in.
IDLE_BEFORE = {}
for _p in U["fixed_pairs"]:
    if _p.get("bye_before"):
        for _t in (_p["team_a"], _p["team_b"]):
            IDLE_BEFORE.setdefault(_t, set()).add(_p["week"] - 1)


def idle_ok(team, wk):
    """False when this team is required to be on bye that week."""
    return wk not in IDLE_BEFORE.get(team, ())


# Weeks 1 and 14 are full slates -- every programme plays -- and week 0 cannot be a bye
# for a team that also needs two more byes elsewhere without risking consecutive ones.
# A `bye_before` rivalry placed in week 1, 2 or 15 is therefore unsatisfiable, and it is
# far better to say so here than to hand back a calendar that quietly broke the rule.
for _t, _wks in IDLE_BEFORE.items():
    for _w in _wks:
        if _w in (1, 14):
            raise RuntimeError(
                "%s is required idle in week %d, but that is a full slate. A bye_before "
                "rivalry cannot sit in week %d." % (_t, _w, _w + 1))
        if not 0 <= _w <= 14:
            raise RuntimeError("%s: idle week %d is outside the calendar" % (_t, _w))


# ---------------------------------------------------------------- opponents
def build_conf_opponents(rng, tries=4000):
    """9 conference opponents each. Built as the COMPLEMENT: pick the (n-10) games each
    team will NOT play, as a union of perfect matchings that never touches a locked
    rivalry, so every rivalry survives into the real slate."""
    conf_opp = {}
    for conf, tl in U["conferences"].items():
        tl = list(tl)
        n = len(tl)
        miss = n - 10                      # 10-team league: everyone plays everyone
        if miss == 0:
            for t in tl:
                conf_opp[t] = set(tl) - {t}
            continue
        for _ in range(tries):
            comp = collections.defaultdict(set)
            ok = True
            for _round in range(miss):
                pairs, fail = None, True
                for _attempt in range(600):
                    pool = tl[:]
                    rng.shuffle(pool)
                    stack, pairs, fail = pool[:], [], False
                    while stack:
                        a = stack.pop(0)
                        cands = [b for b in stack
                                 if b not in comp[a] and frozenset((a, b)) not in RIVAL_PAIRS]
                        if not cands:
                            fail = True
                            break
                        b = rng.choice(cands)
                        stack.remove(b)
                        pairs.append((a, b))
                    if not fail:
                        break
                if fail:
                    ok = False
                    break
                for a, b in pairs:
                    comp[a].add(b); comp[b].add(a)
            if ok:
                full = {t: set(tl) - {t} - comp[t] for t in tl}
                if all(len(v) == 9 for v in full.values()):
                    conf_opp.update(full)
                    break
        else:
            raise RuntimeError("conference opponents failed for " + conf)
    # sanity: every locked conference rivalry must be on the slate
    for k in RIV_CONF:
        a, b = tuple(k)
        if b not in conf_opp[a]:
            raise RuntimeError("locked rivalry dropped: %s / %s" % (a, b))
    return conf_opp


# ---------------------------------------------------------------- hosts
def orient_conference(rng, conf_opp, prev_host, tries=600):
    """Each program hosts exactly 4 or 5 conference games. Locked rivalry hosts are
    pinned first -- they alternate against last season -- and the rest are oriented
    around them."""
    out = []
    for conf, tl in U["conferences"].items():
        tl = list(tl)
        pairs = sorted({frozenset((t, o)) for t in tl for o in conf_opp[t]},
                       key=lambda f: sorted(f))
        pairs = [tuple(sorted(p)) for p in pairs]
        n, G = len(tl), len(pairs)
        fives = max(0, min(n, G - 4 * n))          # how many programs host five

        pinned = {}
        for i, (u, v) in enumerate(pairs):
            k = frozenset((u, v))
            if k in RIV_CONF:
                prev = prev_host.get("|".join(sorted((u, v))))
                pinned[i] = v if prev == u else u   # whoever did not host last year

        best = None
        for _ in range(tries):
            order = list(tl); rng.shuffle(order)
            targets = {t: (5 if i < fives else 4) for i, t in enumerate(order)}
            # a pinned host must not blow its own target
            if any(collections.Counter(pinned.values())[t] > targets[t] for t in tl):
                continue
            home = _orient(pairs, tl, targets, pinned, rng)
            if home is None:
                continue
            hc = collections.Counter(home.values())
            if all(hc[t] == targets[t] for t in tl):
                best = home
                break
        if best is None:
            raise RuntimeError("could not orient conference hosts for " + conf)
        for i, (u, v) in enumerate(pairs):
            host = best[i]
            out.append((host, v if host == u else u, True))
    return out


def _orient(pairs, teams, targets, pinned, rng):
    """Degree-constrained orientation: host = whoever has the greater relative need."""
    remaining = dict(targets)
    deg_left = collections.Counter()
    for u, v in pairs:
        deg_left[u] += 1; deg_left[v] += 1
    home = {}
    for i, host in pinned.items():
        u, v = pairs[i]
        home[i] = host
        remaining[host] -= 1
        deg_left[u] -= 1; deg_left[v] -= 1
        if remaining[host] < 0:
            return None
    order = [i for i in range(len(pairs)) if i not in home]
    rng.shuffle(order)
    for i in order:
        u, v = pairs[i]
        if remaining[u] <= 0 and remaining[v] <= 0:
            return None
        if remaining[u] <= 0:
            host = v
        elif remaining[v] <= 0:
            host = u
        else:
            uu = remaining[u] / max(1, deg_left[u])
            vv = remaining[v] / max(1, deg_left[v])
            host = u if uu > vv else v if vv > uu else (u if rng.random() < .5 else v)
        home[i] = host
        remaining[host] -= 1
        deg_left[u] -= 1; deg_left[v] -= 1
    return home


# ---------------------------------------------------------------- calendar
def assign_weeks(rng, games):
    """Place every game in a week.

    Order of operations matters: the pinned rivalry weeks go down first, then the two
    full slates (14 and 1) via maximum matching, then the small week 0, then everything
    else spreads across 2-13. Because weeks 1 and 14 are full and week 0 is tiny, each
    team's bye count falls out arithmetically -- what needs repairing afterwards is only
    where the byes LAND.
    """
    week_of = {}
    busy = collections.defaultdict(set)

    def pin(i, wk):
        h, a, ic = games[i]
        week_of[i] = wk
        busy[wk].add(h); busy[wk].add(a)

    def free(i, wk):
        h, a, _ = games[i]
        return (h not in busy[wk] and a not in busy[wk]
                and idle_ok(h, wk) and idle_ok(a, wk))

    # 1) pinned rivalry weeks
    for i, (h, a, ic) in enumerate(games):
        k = frozenset((h, a))
        if k in FIXED_WEEK:
            pin(i, FIXED_WEEK[k])

    # 2) full slates: week 14 then week 1, each a maximum matching over who is still free
    stranded = {}
    for wk, prefer_conf in ((14, True), (1, False)):
        need = [t for t in TEAMS if t not in busy[wk] and idle_ok(t, wk)]
        G = nx.Graph()
        G.add_nodes_from(sorted(need))
        for i in range(len(games)):
            if i in week_of:
                continue
            h, a, ic = games[i]
            if h in G and a in G:
                w = (2.0 if ic == prefer_conf else 1.0) + rng.random() * 0.1
                if G.has_edge(h, a) and G[h][a]["weight"] >= w:
                    continue
                G.add_edge(h, a, gi=i, weight=w)
        M = nx.max_weight_matching(G, maxcardinality=True)
        if 2 * len(M) < len(need):
            # The board cannot fill this slate. Rather than fail blind, place everyone who
            # CAN play and name the programs that cannot, with the reason: every opponent
            # on their 12-game slate is already committed that week. The caller decides
            # whether to retry with a different conference draw or report it to Dan.
            covered = {t for e in M for t in e}
            stranded[wk] = sorted(t for t in need if t not in covered)
        for h, a in M:
            pin(G[h][a]["gi"], wk)

    # 3) week 0: a small opening slate, drawn from non-conference games by preference
    pool = [i for i in range(len(games)) if i not in week_of]
    rng.shuffle(pool)
    pool.sort(key=lambda i: (games[i][2], rng.random()))     # non-conference first
    placed0 = 0
    for i in pool:
        if placed0 >= WEEK0_GAMES:
            break
        if free(i, 0):
            pin(i, 0); placed0 += 1

    # 4) the rest across weeks 2-13, non-conference aimed at the opening month.
    # A plain greedy reliably strands one or two games right at the end -- both teams
    # already booked in all twelve middle weeks -- so a game that cannot be placed gets
    # one round of ejection: shift a game already sitting in a candidate week somewhere
    # else, then take the slot it vacated. Week 0 is the last resort, which grows the
    # opening slate by a game or two rather than losing a fixture.
    rest = [i for i in range(len(games)) if i not in week_of]
    rest.sort(key=lambda i: (games[i][2], rng.random()))
    in_week = collections.defaultdict(set)
    for i, wk in week_of.items():
        in_week[wk].add(i)

    def place(i, wk):
        pin(i, wk)
        in_week[wk].add(i)

    def unplace(i):
        wk = week_of.pop(i)
        in_week[wk].discard(i)
        h, a, _ = games[i]
        # the week is only free of a team once no other game there uses it
        for t in (h, a):
            if not any(t in games[j][:2] for j in in_week[wk]):
                busy[wk].discard(t)
        return wk

    pinned_games = {i for i in range(len(games)) if frozenset(games[i][:2]) in FIXED_WEEK}

    for i in rest:
        ic = games[i][2]
        pref = MID if ic else [2, 3, 4, 5] + MID
        order = sorted(set(pref), key=lambda w: (pref.index(w), len(busy[w])))
        for wk in order:
            if free(i, wk):
                place(i, wk)
                break
        else:
            if not _eject(i, games, week_of, busy, in_week, pinned_games, place, unplace, free, rng):
                return None
    return week_of, stranded


def _eject(i, games, week_of, busy, in_week, pinned_games, place, unplace, free, rng):
    """Make room for game i by moving the games that block it somewhere else.

    Tries one candidate week at a time. The blockers are lifted out, each looked a new
    home, and if any of them cannot be rehoused the whole attempt is rolled back to
    exactly where it started before the next week is tried.
    """
    h, a, _ = games[i]
    for wk in MID + [0]:                 # week 0 last: it is meant to be a small slate
        blockers = [j for j in sorted(in_week[wk])
                    if j not in pinned_games and (h in games[j][:2] or a in games[j][:2])]
        if not blockers or len(blockers) > 2:
            continue
        snapshot = {j: week_of[j] for j in blockers}
        rng.shuffle(blockers)
        for j in blockers:
            unplace(j)
        ok = True
        for j in blockers:
            for w2 in sorted(MID + [0], key=lambda w: len(busy[w])):
                if w2 != wk and free(j, w2):
                    place(j, w2)
                    break
            else:
                ok = False
                break
        if ok and free(i, wk):
            place(i, wk)
            return True
        # roll back: lift whatever got rehoused, then restore every blocker
        for j in blockers:
            if j in week_of:
                unplace(j)
        for j, w in snapshot.items():
            place(j, w)
    return False


# ---------------------------------------------------------------- polish
def _byes(team_weeks):
    return sorted(set(WEEKS) - team_weeks)


def cost_of(games, week_of, teams=None):
    """What we are trying to minimise, per team:
         consecutive byes  -- Dan's rule, weighted hardest
         3+ game home or away runs
         non-conference games played after the opening month
    """
    tg = collections.defaultdict(list)
    for i, (h, a, ic) in enumerate(games):
        if h in TSET: tg[h].append(i)
        if a in TSET: tg[a].append(i)
    total = {}
    for t in (teams or TEAMS):
        gs = sorted(tg[t], key=lambda i: week_of[i])
        wks = {week_of[i] for i in gs}
        c = 0
        b = _byes(wks)
        c += 14 * sum(1 for j in range(len(b) - 1) if b[j + 1] - b[j] == 1)
        run, last = 0, None
        for i in gs:
            ha = "H" if games[i][0] == t else "A"
            run = run + 1 if ha == last else 1
            last = ha
            if run >= 3:
                c += 3
        total[t] = c
    return total


def reduce_cost(games, week_of, rng, rounds=40000):
    """Local search. Two moves: shift one game to another legal week, or swap the weeks
    of two games. Pinned rivalry weeks and the full slates are never touched, so nothing
    the rules fixed can drift."""
    pinned = {i for i, (h, a, ic) in enumerate(games) if frozenset((h, a)) in FIXED_WEEK}
    locked_wk = {0, 1, 14}
    movable = [i for i in range(len(games)) if i not in pinned and week_of[i] not in locked_wk]
    if not movable:
        return week_of

    busy = collections.defaultdict(set)
    for i, (h, a, ic) in enumerate(games):
        busy[week_of[i]].add(h); busy[week_of[i]].add(a)

    cost = cost_of(games, week_of)
    total = sum(cost.values())

    def touched(i, j=None):
        ts = set(games[i][:2])
        if j is not None:
            ts |= set(games[j][:2])
        return {t for t in ts if t in TSET}

    for _ in range(rounds):
        if total == 0:
            break
        i = rng.choice(movable)
        h, a, ic = games[i]
        w0 = week_of[i]
        if rng.random() < 0.55:
            w1 = rng.choice(MID)
            if (w1 == w0 or h in busy[w1] or a in busy[w1]
                    or not idle_ok(h, w1) or not idle_ok(a, w1)):
                continue
            ts = touched(i)
            before = sum(cost[t] for t in ts)
            busy[w0].discard(h); busy[w0].discard(a)
            week_of[i] = w1
            busy[w1].add(h); busy[w1].add(a)
            after_c = cost_of(games, week_of, ts)
            after = sum(after_c.values())
            if after <= before:
                cost.update(after_c); total += after - before
            else:
                busy[w1].discard(h); busy[w1].discard(a)
                week_of[i] = w0
                busy[w0].add(h); busy[w0].add(a)
        else:
            j = rng.choice(movable)
            if j == i:
                continue
            h2, a2, _ = games[j]
            w1 = week_of[j]
            if w0 == w1:
                continue
            # the swap is legal only if each pair is free in the other's week
            if (h in busy[w1] or a in busy[w1] or h2 in busy[w0] or a2 in busy[w0]
                    or not idle_ok(h, w1) or not idle_ok(a, w1)
                    or not idle_ok(h2, w0) or not idle_ok(a2, w0)):
                continue
            ts = touched(i, j)
            before = sum(cost[t] for t in ts)
            for (x, wx, wy) in ((i, w0, w1), (j, w1, w0)):
                hh, aa, _ = games[x]
                busy[wx].discard(hh); busy[wx].discard(aa)
                week_of[x] = wy
                busy[wy].add(hh); busy[wy].add(aa)
            after_c = cost_of(games, week_of, ts)
            after = sum(after_c.values())
            if after <= before:
                cost.update(after_c); total += after - before
            else:
                for (x, wx, wy) in ((i, w1, w0), (j, w0, w1)):
                    hh, aa, _ = games[x]
                    busy[wx].discard(hh); busy[wx].discard(aa)
                    week_of[x] = wy
                    busy[wy].add(hh); busy[wy].add(aa)
    return week_of


# ---------------------------------------------------------------- driver
def smooth_weeks(games, week_of, rng, rounds=30000):
    """Even out the slates. The bye rule and the run reducer together will happily leave
    one mid-season week with 45 teams idle and another with 17 -- legal, but a weekend
    that thin reads wrong. This moves games from crowded weeks into sparse ones, and only
    ever accepts a move that leaves every affected team's own cost no worse than it was.
    """
    pinned = {i for i, (h, a, ic) in enumerate(games) if frozenset((h, a)) in FIXED_WEEK}
    movable = [i for i in range(len(games)) if i not in pinned and week_of[i] in MID]
    if not movable:
        return week_of
    # Load is measured in FBS programs on the field, not games: a guest game occupies one
    # program, an FBS pairing two, and it is programs idle that Dan sees as a thin week.
    busy = collections.defaultdict(set)
    load = collections.Counter()

    def wt(i):
        h, a, _ = games[i]
        return (1 if h in TSET else 0) + (1 if a in TSET else 0)

    for i, (h, a, ic) in enumerate(games):
        busy[week_of[i]].add(h); busy[week_of[i]].add(a)
        load[week_of[i]] += wt(i)
    target = sum(load[w] for w in MID) / len(MID)
    cost = cost_of(games, week_of)

    def spread():
        return sum(abs(load[w] - target) for w in MID)

    cur = spread()
    for _ in range(rounds):
        i = rng.choice(movable)
        h, a, ic = games[i]
        w0 = week_of[i]
        # aim at the thinnest week this game could legally move to
        cands = [w for w in MID if w != w0 and h not in busy[w] and a not in busy[w]
                 and idle_ok(h, w) and idle_ok(a, w)]
        if not cands:
            continue
        w1 = min(cands, key=lambda w: load[w])
        k = wt(i)
        if load[w1] + k > load[w0] - k:
            continue                                    # would not actually level anything
        ts = {t for t in (h, a) if t in TSET}
        before = sum(cost[t] for t in ts)
        busy[w0].discard(h); busy[w0].discard(a); load[w0] -= k
        week_of[i] = w1
        busy[w1].add(h); busy[w1].add(a); load[w1] += k
        after_c = cost_of(games, week_of, ts)
        new = spread()
        if sum(after_c.values()) <= before and new < cur:
            cost.update(after_c); cur = new
        else:
            busy[w1].discard(h); busy[w1].discard(a); load[w1] -= k
            week_of[i] = w0
            busy[w0].add(h); busy[w0].add(a); load[w0] += k
    return week_of


def load_noncon(path):
    """Dan's board: a list of host/visitor pairs. Subdivision guests keep their names;
    they are not FBS teams and own no slate of their own."""
    d = json.load(open(path)) if isinstance(path, str) else path
    rows = d["games"] if isinstance(d, dict) else d
    out, seen = [], set()
    for g in rows:
        h, v = g["host"], g["visitor"]
        k = frozenset((h, v))
        if k in seen:
            raise ValueError("duplicate non-conference matchup: %s / %s" % (h, v))
        seen.add(k)
        if h in TSET and v in TSET and CONF[h] == CONF[v]:
            raise ValueError("%s and %s share a conference" % (h, v))
        out.append((h, v, False))
    per = collections.Counter()
    for h, v, _ in out:
        if h in TSET: per[h] += 1
        if v in TSET: per[v] += 1
    bad = {t: per[t] for t in TEAMS if per[t] != 3}
    if bad:
        raise ValueError("these programs do not have exactly 3 non-conference games: %s"
                         % dict(list(bad.items())[:12]))
    return out


def prev_schedule(season):
    """Rebuild a past season's regular-season slate from the games database.

    The rollover clears `s['sched']`, so by the time a new schedule is built the previous
    one is gone from state -- and it is needed, because locked rivalry hosts alternate
    against it. Box scores carry their own week, home and away, so the database is the
    durable record. Without this, every one of the 35 in-conference rivalries would be
    hosted by the same program two years running and nothing would flag it.
    """
    import re
    from games_db import load_db
    tag = re.compile(r"^S%d(?!\d)" % season)
    out = []
    for gid, b in load_db().items():
        gid = str(gid)
        if not tag.match(gid) or b.get("postseason") or "CCG" in gid or "PO" in gid:
            continue
        out.append((b.get("week", 0), b.get("home"), b.get("away"), False))
    return out


def build(noncon_path, prev_sched, seed=770011, attempts=40):
    """Returns (sched, report). sched is the engine's own [(week, home, away, is_conf)]."""
    prev_host = {}
    for wk, h, a, ic in prev_sched:
        prev_host["|".join(sorted((h, a)))] = h

    noncon = load_noncon(noncon_path)
    rng = random.Random(seed)
    last = None

    for attempt in range(attempts):
        conf_opp = build_conf_opponents(rng)
        conf_games = orient_conference(rng, conf_opp, prev_host)
        games = noncon + conf_games
        res = assign_weeks(rng, games)
        if res is None:
            continue
        week_of, stranded = res
        for r in range(3):
            week_of = reduce_cost(games, week_of, random.Random(seed + 7919 * (r + 1)))
            if sum(cost_of(games, week_of).values()) == 0:
                break
        # level the slates, then re-run the reducer in case levelling cost us a run
        for r in range(2):
            week_of = smooth_weeks(games, week_of, random.Random(seed + 104729 * (r + 1)))
            week_of = reduce_cost(games, week_of, random.Random(seed + 611953 * (r + 1)),
                                  rounds=20000)
        sched = sorted((week_of[i], games[i][0], games[i][1], games[i][2])
                       for i in range(len(games)))
        rep = audit(sched)
        rep["stranded"] = stranded
        rep["attempt"] = attempt + 1
        if rep["ok"] and not stranded:
            return sched, rep
        if last is None or len(rep["fails"]) < len(last[1]["fails"]):
            last = (sched, rep)
    if last is None:
        raise RuntimeError("no calendar could be built from this non-conference board")
    return last


# ---------------------------------------------------------------- audit
def audit(sched, verbose=False):
    per = collections.defaultdict(list)
    for wk, h, a, ic in sched:
        if h in TSET: per[h].append((wk, "H", ic, a))
        if a in TSET: per[a].append((wk, "A", ic, h))

    fails = []
    games12 = sorted({len(v) for v in per.values()})
    if games12 != [12]:
        fails.append("games per team: %s" % games12)
    conf9 = sorted({sum(1 for x in v if x[2]) for v in per.values()})
    if conf9 != [9]:
        fails.append("conference games per team: %s" % conf9)
    if len(per) != 152:
        fails.append("teams scheduled: %d" % len(per))

    dbl = [t for t, v in per.items() if len({x[0] for x in v}) != 12]
    if dbl:
        fails.append("double-booked: %s" % dbl[:5])

    byes = collections.Counter()
    bye_week = collections.Counter()
    consec = []
    for t, v in per.items():
        wks = {x[0] for x in v}
        b = sorted(set(WEEKS) - wks)
        byes[len(b)] += 1
        for x in b:
            bye_week[x] += 1
        if any(b[j + 1] - b[j] == 1 for j in range(len(b) - 1)):
            consec.append(t)
    if list(byes) != [3]:
        fails.append("byes per team: %s" % dict(byes))
    if consec:
        fails.append("consecutive byes: %d teams %s" % (len(consec), consec[:5]))
    if bye_week[1] or bye_week[14]:
        fails.append("byes in a full slate week: wk1=%d wk14=%d" % (bye_week[1], bye_week[14]))

    # locked matchups in their proper weeks
    placed = {frozenset((h, a)): wk for wk, h, a, ic in sched}
    miss = [(tuple(k), FIXED_WEEK[k], placed.get(k)) for k in FIXED_WEEK
            if placed.get(k) != FIXED_WEEK[k]]
    if miss:
        fails.append("locked rivalry misplaced: %s" % miss[:4])

    # rivalries that require an open week in front of them
    for t, wks in IDLE_BEFORE.items():
        played = {x[0] for x in per.get(t, [])}
        busy_when_idle = sorted(wks & played)
        if busy_when_idle:
            fails.append("%s must be idle in week(s) %s but has a game there"
                         % (t, busy_when_idle))

    conf_home = collections.Counter()
    home = collections.Counter()
    for wk, h, a, ic in sched:
        if h in TSET:
            home[h] += 1
            if ic: conf_home[h] += 1
    ch = sorted(set(conf_home.values()))
    if ch and (min(ch) < 4 or max(ch) > 5):
        fails.append("conference home games out of the 4-5 band: %s" % ch)

    runs = collections.Counter()
    for t, v in per.items():
        gs = sorted(v)
        best = cur = 0; last = None
        for _w, ha, _ic, _o in gs:
            cur = cur + 1 if ha == last else 1
            last = ha; best = max(best, cur)
        runs[best] += 1

    wkg = collections.Counter(wk for wk, _h, _a, _ic in sched)
    nonconf_wk = collections.Counter(wk for wk, _h, _a, ic in sched if not ic)

    rep = {
        "ok": not fails, "fails": fails, "games": len(sched),
        "byes": dict(byes), "bye_week": {w: bye_week[w] for w in WEEKS},
        "week0_games": wkg[0], "week0_byes": bye_week[0],
        "consecutive_byes": len(consec),
        "conf_home": dict(sorted(collections.Counter(conf_home.values()).items())),
        "home_total": dict(sorted(collections.Counter(home.values()).items())),
        "runs": dict(sorted(runs.items())),
        "games_per_week": {w: wkg[w] for w in WEEKS},
        "nonconf_per_week": {w: nonconf_wk[w] for w in WEEKS},
    }
    if verbose:
        # the year was hard-coded to 2036 and would have mislabelled every season after it
        import season as _SE
        print("=== %d SCHEDULE AUDIT ===" % (2025 + _SE.load_state().get("season", 11)))
        print("  games %d | %s" % (rep["games"], "ALL CHECKS PASS" if rep["ok"] else "FAILURES"))
        for f in fails:
            print("   ✗", f)
        print("  byes/team            %s" % rep["byes"])
        print("  week 0               %d games, %d byes (%.0f%% of the league)"
              % (rep["week0_games"], rep["week0_byes"], 100 * rep["week0_byes"] / 152))
        print("  consecutive byes     %d" % rep["consecutive_byes"])
        print("  conference home      %s" % rep["conf_home"])
        print("  total home games     %s" % rep["home_total"])
        print("  worst H/A run        %s" % rep["runs"])
        print("  games per week       %s" % rep["games_per_week"])
        print("  non-conference/week  %s" % rep["nonconf_per_week"])
    return rep


def explain_stranded(stranded):
    """Say WHY a program could not be placed, in terms Dan can act on."""
    out = []
    for wk, teams in sorted(stranded.items()):
        for t in teams:
            conf = CONF[t]
            mates = [x for x in U["conferences"][conf] if x != t]
            pinned_wk = {a for k, v in FIXED_WEEK.items() if v == wk for a in k}
            free_mates = [x for x in mates if x not in pinned_wk]
            out.append(
                "%s has no available opponent in week %d. %s"
                % (t, wk,
                   ("Every other program in %s is locked into a week-%d rivalry, so their "
                    "partner has to come from the non-conference slate — and all three of "
                    "their non-conference opponents are locked into week-%d games too."
                    % (conf, wk, wk)) if not free_mates else
                   ("All %d of their opponents are already committed in week %d."
                    % (12, wk))))
    return out


if __name__ == "__main__":
    import season as SE
    s = SE.load_state()
    path = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/cfb2/state/noncon_fixture.json'
    sched, rep = build(path, s["sched"])
    audit(sched, verbose=True)
    if rep.get("stranded"):
        print("\n  COULD NOT PLACE:")
        for line in explain_stranded(rep["stranded"]):
            print("   •", line)
    print("  solved on attempt  %s" % rep.get("attempt", "—"))
