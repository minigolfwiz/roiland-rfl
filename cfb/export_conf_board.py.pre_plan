"""Data payload for Dan's conference-schedule builder. Power North first.

Dan builds the weeks himself, so this exports the things a week decision depends on
and nothing it does not. Every structural claim is a LOOKUP out of the universe, the
games database and the finished non-conference board -- never recall.

WHAT THE SHAPE OF THE PROBLEM ACTUALLY IS, for a 14-team conference:
  * 9 conference games each, so 14 x 9 / 2 = 63 games, and every programme SKIPS 4 of
    the other 13. The skipped set is a 4-regular graph on 14 nodes -- 28 skipped pairs,
    63 played -- which is why "who do we not play" has to be solved as a whole rather
    than team by team.
  * 15 weeks, 0 to 14. Twelve games, exactly three byes, never two in a row. Weeks 1
    and 14 are full slates, so no bye can sit in either.
  * Week 14 is rivalry week and in Power North it is ALREADY FULL: five locked
    conference rivalries account for ten programmes, and the other four -- Northlight,
    Roosevelt State, Kaji Kita, Southern Tengus -- are committed to locked
    cross-conference rivalries that same week. Nothing to decide, and it anchors
    everything else.
  * That leaves 58 conference games to place across weeks 0-13.

Because week 14 differs by programme, so does the rest of the load: a programme whose
week 14 is a conference game has 8 more to place, one whose week 14 is non-conference
has 9. Both end up with 11 games and 3 byes across weeks 0-13, which is the invariant
the builder checks against.

The non-conference board is finished and is read here as a commitment, not a
suggestion: those three dates are already booked and have to fit around whatever Dan
does with the conference slate.
"""
import sys, json, collections, math, re, random
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E
from games_db import load_db

U = E.U
TC = U["team_conf"]
GEO, COORDS, COLORS = U["geo"], U["state_coords"], U["team_colors"]
SCHOOL_XY = U.get("school_coords") or {}   # school-level placements (Dan, 2042); state seed is the fallback
PRES, TIERS, SCHOOLS = U["prestige"], U["tiers"], U["schools"]

CONF_GAMES = 9
WEEKS = list(range(15))
BYES = 3
# Dan's rule, 2038: week 1 MAY now be a bye. Only rivalry week is a full slate, so the
# opening weekend no longer forces all 152 programmes onto the field. This also makes
# weeks 0 and 1 adjacent for the no-consecutive-byes test, which they never were while
# week 1 was compulsory.
FULL_WEEKS = [14]
# Week 0 is a soft opening league-wide, not a full slate: canon 2035 ran 11 games
# across 12 conferences with 86% of programmes idle. One game is a conference's share.
WEEK0_GAMES = 1
RIVALRY_WEEK = 14
HISTORY = 5                   # seasons of matchup frequency to carry


def season_week(gid):
    m = re.match(r"^S(\d+)W(\d+)", str(gid))
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def build_all(out='/home/claude/cfb2/state/conf_board.json', seed=13):
    """Every conference in one payload.

    The non-conference board is carried ONCE for the whole league rather than copied
    into each conference. It has to be: a non-conference game belongs to two
    programmes in two different conferences, and giving each conference its own copy
    would let the same real fixture be scheduled into two different weeks depending on
    which conference Dan happened to be looking at. One row, two owners, one week.
    """
    import season as SE
    s = SE.load_state()
    new_season = s.get("season")
    nc = json.load(open("/home/claude/cfb2/state/noncon_s%d.json" % new_season))  # was pinned to s13
    confs = [build(c, seed=seed)[0] for c in U["conferences"]]
    teams = {}
    for c in confs:
        for t in c.pop("teams"):
            t["conf"] = c["conference"]
            teams[t["name"]] = t
    payload = {
        "season": new_season, "year": 2025 + new_season, "prev_year": 2024 + new_season,
        "conf_games": CONF_GAMES, "weeks": WEEKS, "byes": BYES,
        "full_weeks": FULL_WEEKS, "rivalry_week": RIVALRY_WEEK,
        "week0_games": WEEK0_GAMES,
        "conferences": [{k: c[k] for k in
                         ("conference", "tier", "ccg_site", "games", "locked", "roster")}
                        for c in confs],
        "teams": teams,
        "noncon": [{"host": g["host"], "visitor": g["visitor"], "sub": bool(g["sub"]),
                    "week": g.get("week"), "locked": bool(g.get("locked"))}
                   for g in nc["games"]],
    }
    json.dump(payload, open(out, "w"))
    return payload, out


def build(conf="Power North", out=None, seed=13):
    import season as SE
    s = SE.load_state()
    db = load_db()
    new_season = s.get("season")
    done = new_season - 1
    teams = list(U["conferences"][conf])
    TS = set(teams)
    rec = (s.get("season_archive", {}).get(str(done), {}) or {}).get("standings", {})

    # ---- history: who played whom, where, and how often ----
    hosts, played = {}, collections.defaultdict(set)
    # whole-era venue ledger per pair: series_home[pk][team] = times hosted, and the
    # most recent host whatever the season (Dan, 2039: bleed lopsided series back)
    series_home = collections.defaultdict(collections.Counter)
    last_meet = {}
    for gid, b in db.items():
        sn, wk = season_week(gid)
        if sn is None or b.get("postseason"):
            continue
        h, a = b.get("home"), b.get("away")
        if h in TS and a in TS:
            pk = "|".join(sorted((h, a)))
            if sn == done:
                hosts[pk] = h
            if sn > done - HISTORY:
                played[pk].add(sn)
            series_home[pk][h] += 1
            if sn >= last_meet.get(pk, (0, None))[0]:
                last_meet[pk] = (sn, h)

    # ---- locked conference rivalries ----
    locked = []
    for p in U["fixed_pairs"]:
        if p["is_conf"] and p["team_a"] in TS and p["team_b"] in TS:
            pk = "|".join(sorted((p["team_a"], p["team_b"])))
            prev = hosts.get(pk)
            host = p["team_b"] if prev == p["team_a"] else p["team_a"]
            locked.append({"a": p["team_a"], "b": p["team_b"], "week": p["week"],
                           "type": p["type"], "host": host, "prev_host": prev,
                           "bye_before": bool(p.get("bye_before")),
                           "record": U["rivalry_records"].get(pk)})
    locked = split_locked_venues(locked)
    locked_pairs = {"|".join(sorted((L["a"], L["b"]))) for L in locked}

    # ---- the slate: pick which 4 each programme skips ----
    pairs = choose_slate(teams, locked_pairs, played, done, seed)
    games = []
    for pk in sorted(pairs):
        x, y = pk.split("|")
        L = next((l for l in locked if {l["a"], l["b"]} == {x, y}), None)
        if L:
            games.append({"a": L["a"], "b": L["b"], "host": L["host"],
                          "week": L["week"], "locked": True})
        else:
            prev = hosts.get(pk)
            if prev:
                host = y if prev == x else x      # alternate off last season
            else:
                # not played last season: the programme behind in the historic venue
                # ledger hosts; level series alternate off the last meeting ever.
                # (Until 2039 this fell to the alphabetical team, which is how series
                # like Coachville College 0-10 at San Diego Valley happened.)
                hx, hy = series_home[pk][x], series_home[pk][y]
                if hx != hy:
                    host = x if hx < hy else y
                else:
                    lh = last_meet.get(pk, (0, None))[1]
                    host = y if lh == x else x
            games.append({"a": x, "b": y, "host": host, "week": None, "locked": False})
    # Dan's rule, 2039: the 4/5 split SWAPS every season. Last season's conference home
    # count is the number of pairings this programme hosted, and the target is its
    # complement. (Before this the balancer only enforced the shape, and 68 of 152
    # programmes kept the same count two years running by accident.)
    prev_home = collections.Counter(hosts.values())
    target = {t: CONF_GAMES - prev_home[t] for t in teams if prev_home[t] in
              (CONF_GAMES // 2, CONF_GAMES - CONF_GAMES // 2)}
    games = balance_hosts(games, teams, locked_pairs, hosts, target, series_home=series_home)

    def st(t):
        return GEO.get(t, {}).get("state") or SCHOOLS.get(t, {}).get("state")

    payload = {
        "conference": conf, "tier": TIERS.get(conf),
        "season": new_season, "year": 2025 + new_season, "prev_year": 2024 + new_season,
        "conf_games": CONF_GAMES, "weeks": WEEKS, "byes": BYES,
        "week0_games": WEEK0_GAMES,
        "full_weeks": FULL_WEEKS, "rivalry_week": RIVALRY_WEEK,
        "ccg_site": U.get("ccg_sites", {}).get(conf),
        "teams": [{
            "name": t, "full": GEO.get(t, {}).get("full_name", t),
            "mascot": GEO.get(t, {}).get("mascot", ""),
            "prestige": round(PRES.get(t, 50), 1), "state": st(t),
            "xy": [round(v) for v in (SCHOOL_XY.get(t) or COORDS.get(st(t)) or [])] or None, "colors": COLORS.get(t, ["#555", "#999"]),
            "last": {"W": rec.get(t, {}).get("W", 0), "L": rec.get(t, {}).get("L", 0)},
        } for t in teams],
        "games": games,
        "locked": locked,
    }
    payload["roster"] = teams
    if out:
        json.dump(payload, open(out, "w"))
    return payload, out


def choose_slate(teams, locked_pairs, played, done, seed):
    """Choose the 63 pairings by choosing the 28 to SKIP.

    Every programme skips exactly 4, so the skipped set is a 4-regular graph. Built by
    repeatedly taking the programme furthest from its quota and skipping its most-worn
    available pairing -- the one played most often in the last five seasons, and most
    recently as the tiebreak -- so the fixtures that come out are the ones the
    conference has seen least. A locked rivalry can never be skipped.
    """
    n = len(teams)
    skip_quota = n - 1 - CONF_GAMES
    rng = random.Random(seed)
    for attempt in range(500):
        rng = random.Random(seed + attempt)
        skipped = collections.defaultdict(set)
        ok = True
        while True:
            short = [t for t in teams if len(skipped[t]) < skip_quota]
            if not short:
                break
            short.sort(key=lambda t: (-(skip_quota - len(skipped[t])), rng.random()))
            a = short[0]
            cands = [b for b in teams
                     if b != a and b not in skipped[a]
                     and len(skipped[b]) < skip_quota
                     and "|".join(sorted((a, b))) not in locked_pairs]
            if not cands:
                ok = False
                break
            def wear(b):
                sns = played.get("|".join(sorted((a, b))), set())
                return (-len(sns), -(max(sns) if sns else 0), rng.random())
            cands.sort(key=wear)
            b = cands[0]
            skipped[a].add(b)
            skipped[b].add(a)
        if ok and all(len(skipped[t]) == skip_quota for t in teams):
            break
    else:
        raise SystemExit("could not build a legal slate")
    pairs = set()
    for i, x in enumerate(teams):
        for y in teams[i + 1:]:
            if y not in skipped[x]:
                pairs.add("|".join(sorted((x, y))))
    return pairs


def split_locked_venues(locked):
    """Dan's rule, 2039: a programme with TWO locked conference rivals hosts one and
    travels to the other, every season. Fiota Bay and Crayellan are the case: Crayellan
    plays Crayellan State and Fiota Bay, Fiota Bay plays UFNH and Crayellan, and with
    all three series alternating in lockstep the two of them were hosting both or
    visiting both -- in 2038 AND, uncorrected, in 2039.

    One series has to repeat a venue once to break the lockstep; after that plain
    alternation keeps the rule forever. Searched over every orientation of the locked
    games, minimising repeats, with a repeat in a plain 'Locked' game costing less
    than one on Rivalry Week -- the marquee game turns around, the week-9 one waits.
    """
    import itertools
    deg = collections.Counter()
    for L in locked:
        deg[L["a"]] += 1; deg[L["b"]] += 1
    multi = {x for x, n in deg.items() if n >= 2}
    if not multi:
        return locked
    idx = [i for i, L in enumerate(locked) if L["a"] in multi or L["b"] in multi]
    best, best_cost = None, None
    for flips in itertools.product((0, 1), repeat=len(idx)):
        trial = [dict(L) for L in locked]
        cost = 0
        for f, i in zip(flips, idx):
            if f:
                L = trial[i]
                L["host"] = L["b"] if L["host"] == L["a"] else L["a"]
                cost += 1 if L["type"] == "Locked" else 3
        ok = True
        for x in multi:
            mine = [L for L in trial if x in (L["a"], L["b"])]
            home = sum(1 for L in mine if L["host"] == x)
            if home == 0 or home == len(mine):
                ok = False; break
        if ok and (best_cost is None or cost < best_cost):
            best, best_cost = trial, cost
    if best is None:
        return locked                      # cannot be satisfied; leave alternation
    for L in best:
        if L["host"] != next(o["host"] for o in locked if (o["a"], o["b"]) == (L["a"], L["b"])):
            L["venue_note"] = "repeat venue: split-venue rule"
    return best


def balance_hosts(games, teams, locked_pairs, hosts, target=None, series_home=None):
    """Orient hosts so every programme hosts 4 or 5 of its 9, without moving a rivalry.

    63 games over 14 programmes is 4.5 each, so the only legal shape is seven on 4 and
    seven on 5. Alternation off last season sets the venue first -- a series turning
    around matters more than the count -- and this moves the fewest games it can to
    reach that shape.

    Done as an AUGMENTING PATH rather than a swap. A greedy pass that only flips a game
    when the opponent is directly under quota stalls constantly: the programme hosting
    too much is usually surrounded by others already on 5, and there is no single flip
    that helps. Walking a chain -- this one gives a game up, the next gives one up in
    turn, until the path reaches somebody genuinely short -- moves the surplus along
    the whole line at once. Locked rivalries are never on a path.
    """
    total = len(games)
    lo_quota = total // len(teams)
    MIN, MAX = lo_quota, lo_quota + (1 if total % len(teams) else 0)
    target = target or {}
    # a programme with a target is held to it exactly; one without keeps the band
    LO = {t: target.get(t, MIN) for t in teams}
    HI = {t: target.get(t, MAX) for t in teams}
    series_home = series_home or {}

    def skew_if(g, new_host):
        """Historic venue imbalance of this series if new_host hosts: positive means
        new_host is already ahead. The path search tries games in this order, so the
        home dates it has to move land with the programme behind in the series."""
        other = g["b"] if g["a"] == new_host else g["a"]
        c = series_home.get("|".join(sorted((g["a"], g["b"]))), {})
        return c.get(new_host, 0) - c.get(other, 0)

    def home_of():
        c = collections.Counter(g["host"] for g in games)
        return {t: c.get(t, 0) for t in teams}

    def shift(deficit_side):
        """Move one home date along a chain, into a short programme or out of a long one.

        Both directions are needed. Alternation can leave the conference with nobody
        ABOVE quota and two programmes below it -- which is exactly what Power North
        produced -- so a search that only drains surpluses finds nothing to do and
        stops with the board still lopsided.
        """
        c = home_of()
        starts = [t for t in teams if (c[t] < LO[t] if deficit_side else c[t] > HI[t])]
        if not starts:
            return False
        start = (min if deficit_side else max)(starts, key=lambda t: c[t])
        prev, seen, queue = {}, {start}, [start]
        while queue:
            x = queue.pop(0)
            cand = [g for g in games if not g["locked"] and x in (g["a"], g["b"])]
            # deficit: x would take the date; surplus: the other side would
            cand.sort(key=lambda g: skew_if(g, x if deficit_side else (g["b"] if g["a"] == x else g["a"])))
            for g in cand:
                y = g["b"] if g["a"] == x else g["a"]
                # deficit: x takes the date from y, so y must currently host it
                # surplus: x gives the date to y, so x must currently host it
                if (g["host"] != y) if deficit_side else (g["host"] != x):
                    continue
                if y in seen:
                    continue
                seen.add(y)
                prev[y] = (x, g)
                donor_ok = c[y] > LO[y] if deficit_side else c[y] < HI[y]
                if donor_ok:
                    node = y
                    while node in prev:
                        x2, g2 = prev[node]
                        g2["host"] = x2 if deficit_side else node
                        node = x2
                    return True
                queue.append(y)
        return False

    for _ in range(2000):
        if not (shift(True) or shift(False)):
            break

    # ---- venue-ledger repair (Dan, 2039): reverse host cycles ----
    # Flipping every game around a directed cycle host->visitor leaves every
    # programme's home count untouched, so this can chase the historic skew without
    # disturbing the 4/5 shape or a locked rivalry. Hill-climb over cycles of 2..4.
    if series_home:
        def cost():
            return sum(max(0, skew_if(g, g["host"])) for g in games if not g["locked"])
        # a pair that met last season keeps its alternation (Dan's yearly swap is the
        # senior rule); only pairs resuming after a gap are free to move
        free = lambda g: not g["locked"] and "|".join(sorted((g["a"], g["b"]))) not in hosts
        by_host = lambda: {t: [g for g in games if free(g) and g["host"] == t] for t in teams}
        improved = True
        while improved:
            improved = False
            base = cost()
            bh = by_host()
            for start in teams:
                # DFS for cycles start -> ... -> start of length <= 4
                stack = [(start, [])]
                found = None
                while stack and not found:
                    node, path = stack.pop()
                    for g in bh[node]:
                        v = g["b"] if g["a"] == node else g["a"]
                        if v == start and path:
                            cyc = path + [g]
                            for c in cyc: c["host"] = c["b"] if c["host"] == c["a"] else c["a"]
                            if cost() < base:
                                found = cyc; break
                            for c in cyc: c["host"] = c["b"] if c["host"] == c["a"] else c["a"]
                        elif len(path) < 3 and v != start and all(v not in (p["a"], p["b"]) for p in path):
                            stack.append((v, path + [g]))
                if found:
                    improved = True
                    break
    return games


if __name__ == "__main__":
    p, out = build_all()
    print("%d (%d) -- all %d conferences" % (p["season"], p["year"], len(p["conferences"])))
    print("  %-17s %5s %6s %7s %7s" % ("conference", "teams", "games", "locked", "hosts"))
    bad = []
    for c in p["conferences"]:
        deg = collections.Counter()
        for g in c["games"]:
            deg[g["a"]] += 1
            deg[g["b"]] += 1
        h = collections.Counter(g["host"] for g in c["games"])
        shape = collections.Counter(h.get(t, 0) for t in c["roster"])
        if set(deg.values()) != {CONF_GAMES}:
            bad.append("%s: games per team %s" % (c["conference"], sorted(set(deg.values()))))
        if max(shape) - min(shape) > 1:
            bad.append("%s: host spread %s" % (c["conference"], dict(shape)))
        print("  %-17s %5d %6d %7d %7s" % (c["conference"], len(c["roster"]),
                                           len(c["games"]), len(c["locked"]),
                                           dict(sorted(shape.items()))))
    print("  non-conference carried once for the league: %d games" % len(p["noncon"]))
    print("  PROBLEMS: %s" % (bad or "none"))
    print("  written to %s" % out)
