"""Build the data payload for Dan's non-conference scheduling tool.

Every structural claim here is a LOOKUP: conferences, tiers, states, prestige, the
locked rivalry pairs and last season's hosts all come out of the universe and state
files, never from recall.

What the tool needs to know:
  * all 152 FBS programs, with everything useful for deciding who to play
  * the 217 subdivision programs that can be invited as guests
  * the 6 CROSS-CONFERENCE locked rivalries, which already occupy a non-conference
    slot and cannot be moved -- pre-filled and locked in the tool
  * the 35 IN-CONFERENCE locked rivalries, shown as information only since they are
    conference games and the engine places them
  * who hosted each rivalry last season, so hosts alternate
  * the last FIVE seasons of non-conference opponents, so Dan can see a series in full
    rather than a single year and continue or break it on purpose
  * UNRETURNED VISITS -- pairs met exactly ONCE in the last five seasons and not at all
    in the five before that, so the return leg is still owed. Dan's rule, 2038. See the
    note on `owed` below.

Everything historical is read from the GAMES DATABASE and the season archive, not from
`s['sched']` and `s['record']`. Those two are cleared by the rollover -- which is the
whole point of running this tool after it -- so an exporter that read them would see an
empty schedule and a table of 0-0 records. Box scores record their own week, home and
away, so the database can rebuild any past season's slate on demand.
"""
import sys, json, collections, math, re
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db

U = E.U
TEAMS = list(U["teams"])
TSET = set(TEAMS)
TC = U["team_conf"]
TIERS = U["tiers"]
PRES = U["prestige"]
GEO = U["geo"]
COORDS = U["state_coords"]
COLORS = U["team_colors"]
SCHOOLS = U["schools"]

NONCONF_SLOTS = 3
HISTORY_SEASONS = 5          # how many past years of non-conference slate to carry

# Dan's 2038 rule for suggesting opponents: a programme met exactly ONCE in the last
# five seasons is owed the return leg, so the pairing is worth suggesting at the other
# site. The exclusion is what makes it mean something -- a pair that ALSO met in the
# five seasons before that is a recurring series, not an unreturned visit, so it is
# dropped. Taken together the test is "exactly one meeting in ten seasons", and the
# single meeting's host decides which way the suggestion points.
#
# This is deliberately separate from `nc_history`, which stays a five-year display and
# is not touched: the windows answer different questions. History is for reading a
# series; this is for finding a debt.
RETURN_WINDOW = 5            # "played once in the last five"
SERIES_WINDOW = 10           # "...and not more than once in the last ten"


def build(out='/home/claude/cfb2/state/schedule_board.json'):
    s = SE.load_state()
    db = load_db()
    # The rollover has already advanced the season, so s["season"] IS the year being
    # built. Taking season+1 here is the mistake install_schedule.py made in the 2036
    # cycle -- it filed the audit a year late.
    new_season = s.get("season", 12)
    season_done = new_season - 1
    year = 2025 + new_season
    rec = (s.get("season_archive", {}).get(str(season_done), {}) or {}).get("standings", {})

    # ---- rebuild past seasons' slates from the games database ----
    # A game id looks like S11W03_Home_Away; the season tag must be matched with a
    # trailing non-digit or "S1" also catches S10 and S11.
    def season_of(gid):
        m = re.match(r"^S(\d+)[WCP]", str(gid))
        return int(m.group(1)) if m else None

    hosts_by_season = collections.defaultdict(dict)     # season -> pairkey -> host
    nc_by_season = collections.defaultdict(lambda: collections.defaultdict(list))
    meetings = collections.defaultdict(list)            # pairkey -> [(season, host)]
    for gid, b in db.items():
        sn = season_of(gid)
        if sn is None or b.get("postseason") or "CCG" in str(gid) or "PO" in str(gid):
            continue
        h, a = b.get("home"), b.get("away")
        if not h or not a:
            continue
        hosts_by_season[sn]["|".join(sorted((h, a)))] = h
        # Every NON-CONFERENCE FBS-vs-FBS meeting in the ten-season window, for the
        # owed-return test and the series state.
        #
        # Two exclusions, both load-bearing. Subdivision guests: a guarantee game is
        # one-directional -- in twelve seasons of canon no FBS programme has ever
        # travelled to a subdivision host -- so there is no return leg to owe.
        # Same-conference games: they are placed by the engine, not booked here, and
        # leaving them in was a real bug. Conference rivals meet most years, so they
        # swamped the series counts (346 pairs reading "met five years running") and
        # polluted the owed totals. The owed test survived it only by luck, since a
        # conference pair cannot have exactly one meeting in ten seasons.
        if (h in TSET and a in TSET and TC.get(h) != TC.get(a)
                and sn > season_done - SERIES_WINDOW):
            meetings["|".join(sorted((h, a)))].append((sn, h))
        # Non-conference means the two are not in the same conference, which includes
        # any game against a subdivision guest. Conference membership is taken as it
        # stands today; realignment would make an old game read wrong, and nothing in
        # Roiland has realigned.
        same_conf = h in TSET and a in TSET and TC.get(h) == TC.get(a)
        if same_conf:
            continue
        if h in TSET:
            nc_by_season[sn][h].append({"opp": a, "home": True, "sub": a not in TSET})
        if a in TSET:
            nc_by_season[sn][a].append({"opp": h, "home": False, "sub": h not in TSET})

    # hosts alternate off the most recently played meeting
    last_host = hosts_by_season.get(season_done, {})

    # newest first, and only seasons that actually exist in the database
    hist_seasons = [sn for sn in range(season_done, season_done - HISTORY_SEASONS, -1)
                    if sn in nc_by_season]
    nonconf_history = {}
    for t in TEAMS:
        rows = []
        for sn in hist_seasons:
            games = nc_by_season[sn].get(t, [])
            if games:
                rows.append({"season": sn, "year": 2025 + sn, "games": games})
        nonconf_history[t] = rows
    # the most recent year on its own, so anything already reading `last_nonconf` keeps
    # working unchanged
    # ---- unreturned visits ----
    # Exactly one meeting in the whole ten-season window, and that meeting inside the
    # last five. Two consequences worth stating: a pair that met twice in six years is
    # a series and is dropped, and the locked annual rivalries fall out on their own
    # (ten meetings each) without being special-cased. `at` is from the point of view
    # of the programme whose list it is, matching the tool's home/away buttons: the side
    # that hosted the one meeting owes the trip.
    owed = collections.defaultdict(list)
    for pk, ms in meetings.items():
        if len(ms) != 1:
            continue
        sn, host = ms[0]
        if sn <= season_done - RETURN_WINDOW:
            continue
        x, y = pk.split("|")
        visitor = y if host == x else x
        owed[host].append({"opp": visitor, "at": "away", "season": sn, "year": 2025 + sn})
        owed[visitor].append({"opp": host, "at": "home", "season": sn, "year": 2025 + sn})
    for t in owed:                      # freshest debt first
        owed[t].sort(key=lambda o: -o["season"])

    # ---- the state of every series inside the five-year window ----
    # Dan's refinement, 2038: the last-meeting badge is a nudge to turn a series around,
    # so it should only appear when there is something to turn around. Two programmes
    # that have met twice home and away are SETTLED and the badge is noise -- worse than
    # noise, since it points at a venue flip that already happened.
    #
    # The exception is the one that makes the rule worth having: two or more meetings
    # ALL AT THE SAME GROUND means one side has never hosted, so the visit is still
    # owed however many times they have played. That case is a debt, not a series, and
    # is marked as one.
    #
    # `home` is whether this programme hosted the MOST RECENT meeting; with `same` true
    # it describes every meeting, which is what lets the tool name the side that owes.
    series = collections.defaultdict(dict)
    for pk, ms in meetings.items():
        inwin = sorted([m for m in ms if m[0] > season_done - RETURN_WINDOW])
        if not inwin:
            continue
        x, y = pk.split("|")
        hosts = {h for _sn, h in inwin}
        # NB: not `last_host` -- that name already holds the previous season's rivalry
        # hosts a few lines up, and rebinding it here silently broke host alternation.
        recent_sn, recent_host = inwin[-1]
        for t in (x, y):
            series[t][y if t == x else x] = {
                "n": len(inwin), "season": recent_sn, "year": 2025 + recent_sn,
                "home": recent_host == t, "same": len(hosts) == 1,
            }

    last_nonconf = {t: (nonconf_history[t][0]["games"]
                        if nonconf_history[t] and nonconf_history[t][0]["season"] == season_done
                        else []) for t in TEAMS}

    # ---- locked rivalries ----
    cross, in_conf = [], collections.defaultdict(list)
    for p in U["fixed_pairs"]:
        a, b = p["team_a"], p["team_b"]
        key = "|".join(sorted((a, b)))
        if p["is_conf"]:
            in_conf[a].append({"opp": b, "week": p["week"], "type": p["type"]})
            in_conf[b].append({"opp": a, "week": p["week"], "type": p["type"]})
        else:
            prev = last_host.get(key)
            # hosts alternate: whoever did not host last season hosts now
            host = b if prev == a else a
            cross.append({"a": a, "b": b, "week": p["week"], "type": p["type"],
                          "host": host, "prev_host": prev,
                          "record": U["rivalry_records"].get(key)})

    def dist(t1, t2):
        s1 = GEO.get(t1, {}).get("state") or SCHOOLS.get(t1, {}).get("state")
        s2 = GEO.get(t2, {}).get("state") or SCHOOLS.get(t2, {}).get("state")
        c1, c2 = COORDS.get(s1), COORDS.get(s2)
        if not c1 or not c2:
            return None
        return round(math.dist(c1, c2))

    # ---- week 14 availability ----
    # Rivalry week pins 68 programs into fixed games. Everyone else has to be paired off
    # among the remaining 84, and a program can only be paired with someone it actually
    # plays. So a program that is NOT in a pinned rivalry needs at least one opponent --
    # conference or non-conference -- who is also free. Where its conference has no other
    # free program, that partner can ONLY come from the non-conference slate Dan is
    # building, which makes it his constraint to satisfy and the tool's job to flag.
    w14_pinned = {t for p in U["fixed_pairs"] if p["week"] == 14
                  for t in (p["team_a"], p["team_b"])}
    conf_free = {c: sum(1 for t in tl if t not in w14_pinned)
                 for c, tl in U["conferences"].items()}

    # Dan (2040): the 4/5 conference home split swaps every season, so each programme's
    # count is known before a single conference game is placed: target = 9 - last
    # season's conference home count. Shown in the team panel.
    conf_home_last = {}
    for gid, b in db.items():
        m = re.match(r"S(\d+)W", gid)
        if not m or int(m.group(1)) != season_done:
            continue
        h, a = b["home"], b["away"]
        if TC.get(h) and TC.get(h) == TC.get(a):
            conf_home_last[h] = conf_home_last.get(h, 0) + 1
    conf_home_target = {t: 9 - conf_home_last[t] for t in TEAMS if conf_home_last.get(t) in (4, 5)}
    teams = []
    for t in TEAMS:
        r = rec.get(t, {})
        st = GEO.get(t, {}).get("state") or SCHOOLS.get(t, {}).get("state")
        teams.append({
            "conf_home_target": conf_home_target.get(t),
            "conf_home_last": conf_home_last.get(t),
            "w14_pinned": t in w14_pinned,
            "conf_free": conf_free[TC[t]] - (0 if t in w14_pinned else 1),
            "name": t,
            "full": GEO.get(t, {}).get("full_name", t),
            "mascot": GEO.get(t, {}).get("mascot", ""),
            "conf": TC.get(t),
            "tier": TIERS.get(TC.get(t), "L6"),
            "prestige": round(PRES.get(t, 50), 1),
            "state": st,
            "xy": COORDS.get(st),
            "colors": COLORS.get(t, ["#555555", "#999999"]),
            "last": {"W": r.get("W", 0), "L": r.get("L", 0)},
            "last_nonconf": last_nonconf.get(t, []),
            "nc_history": nonconf_history.get(t, []),
            "owed": owed.get(t, []),
            "series": series.get(t, {}),
            "conf_rivals": in_conf.get(t, []),
        })

    subs = []
    # `s['sub_opponents']` is cleared by the rollover along with the schedule, so who was
    # a guest last year comes out of the rebuilt slates instead.
    guests_last = {g["opp"] for t in TEAMS for g in last_nonconf.get(t, []) if g["sub"]}
    for name, info in SCHOOLS.items():
        if info.get("level") == "FBS" or name in TSET:
            continue
        if name in (U.get("no_football_schools") or []):
            continue
        st = info.get("state")
        subs.append({"name": name, "state": st, "xy": COORDS.get(st),
                     "guest_last": name in guests_last})
    subs.sort(key=lambda x: x["name"])

    payload = {
        "season": new_season, "year": year, "prev_year": year - 1,
        "slots": NONCONF_SLOTS,
        "hist_years": [2025 + sn for sn in hist_seasons],
        "return_window": RETURN_WINDOW, "series_window": SERIES_WINDOW,
        "conferences": {c: {"teams": list(tl), "tier": TIERS.get(c, "L6")}
                        for c, tl in U["conferences"].items()},
        "teams": teams,
        "subs": subs,
        "locked": cross,
        "calendar": {"weeks": 15, "first": 0, "last": 14, "byes": 3,
                     "rivalry_week": 14},
        "w14": {"pinned": len(w14_pinned), "free": 152 - len(w14_pinned),
                "conf_free": conf_free},
        "dist_matrix_note": "computed client-side from xy",
    }
    json.dump(payload, open(out, 'w'))
    return payload


if __name__ == "__main__":
    p = build()
    print("season %d (%d) | teams %d | subdivision pool %d | locked cross-conf %d"
          % (p["season"], p["year"], len(p["teams"]), len(p["subs"]), len(p["locked"])))
    need = len(p["teams"]) * p["slots"] - len(p["locked"]) * 2
    print("non-conference slots for Dan to fill: %d" % need)
    ow = sum(len(t["owed"]) for t in p["teams"])
    print("unreturned visits: %d pairs (%d programme entries), %.1f per programme"
          % (ow // 2, ow, ow / len(p["teams"])))
    rep = [(t["name"], o, v) for t in p["teams"] for o, v in t["series"].items() if v["n"] >= 2]
    print("series met 2+ times in %d years: %d pairs -- %d settled home-and-away "
          "(badge suppressed), %d all at one ground (still owed)"
          % (RETURN_WINDOW, len(rep) // 2,
             sum(1 for _t, _o, v in rep if not v["same"]) // 2,
             sum(1 for _t, _o, v in rep if v["same"]) // 2))
