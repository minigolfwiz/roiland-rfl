"""Stage 7 — season rollover. Close 2035, open 2036.

Nothing in the bundle did this. The monolith's "class rollover" only bumped player
classes; every piece of season state (records, streaks, hot seats, injuries, stat lines,
polls) was reset somewhere in the lost engine. So this stage owns the whole turn of the
year, in the order that matters:

  1. ARCHIVE what the finished season is the only record of -- final standings and the
     closing polls. Results and box scores already live in the games database, and the
     champion is already in the history book, so this is the thin layer on top.
  2. CLASS ROLLOVER. Incoming freshmen keep their class and lose their freshman flag;
     everyone else moves up one.
  3. COACHES age into the new season. The carousel already added a year to everyone's
     age when it ran, so only tenure moves here, and a coach hired this cycle goes from
     0 to 1 -- their first season.
  4. RESET the season. Records to zero, injuries cleared, stat lines emptied, polls
     dropped, hot seats cooled.
  5. PRESEASON RATINGS recomputed from the rosters that now exist, which is the whole
     point of running this after development, recruiting and roster finalisation.

A note on redshirts. The monolith sent 7% of freshmen to an "RS" class and then never
moved them again -- "RS" was missing from its promotion table, so a redshirt would have
sat in that class forever, never graduating, never leaving. No player is currently in it
(nothing has run this stage since the reset), so the dead end is fixed here rather than
inherited: a redshirt spends one year in RS and then rejoins as a sophomore, which is
what a redshirt year is.
"""
import sys, os, pickle, random, collections, copy
STATE = '/home/claude/cfb2/state'
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E

U = E.U
TEAMS = list(U["teams"])
PRESTIGE = U["prestige"]

UP = {"Fr": "So", "RS": "So", "So": "Jr", "Jr": "Sr"}
REDSHIRT_RATE = 0.07


def run_rollover(seed=360011, commit=False):
    rng = random.Random(seed)
    s = SE.load_state()
    done = s.get("season", 10)          # the season being closed
    nxt = done + 1
    year = 2025 + done

    report = {"closing": done, "closing_year": year, "opening": nxt,
              "opening_year": year + 1}

    # ---------- 1) archive ----------
    standings = {t: dict(r) for t, r in s["record"].items()}
    archive = {
        "year": year,
        "champion": s.get("champion_s%d" % done),
        "standings": standings,
        "final_media_poll": list(s.get("media_poll_current") or [])[:25],
        "final_committee_poll": list(s.get("committee_poll_current") or [])[:25],
        "firings": len(s.get("firings") or []),
        # weekly polls, by week (and "pre"), so a season's ranks can be looked up later
        # (the 2040 Gameview map needed them and had to dig them out of a backup)
        "media_history": {str(k): v for k, v in (s.get("media_history") or {}).items()},
        "committee_history": {str(k): v for k, v in (s.get("committee_history") or {}).items()},
    }
    report["archived"] = {"champion": archive["champion"],
                          "teams_in_standings": len(standings),
                          "media_poll_rows": len(archive["final_media_poll"])}

    # ---------- 2) classes ----------
    moved = collections.Counter()
    redshirts = 0
    for t in TEAMS:
        for pl in E.ROSTERS[t]:
            if pl.pop("freshman", None):        # this year's signing class
                moved["stayed Fr (incoming)"] += 1
                continue
            cls = pl.get("cls")
            if cls == "Fr" and rng.random() < REDSHIRT_RATE:
                pl["cls"] = "RS"
                redshirts += 1
                moved["Fr -> RS"] += 1
            elif cls in UP:
                pl["cls"] = UP[cls]
                moved["%s -> %s" % (cls, UP[cls])] += 1
            else:
                moved["unchanged (%s)" % cls] += 1
            pl.pop("transfer", None)            # last cycle's label, not this season's
    report["class_moves"] = dict(moved)
    report["redshirts"] = redshirts

    # ---------- 3) coaches ----------
    staffs = 0
    for t in TEAMS:
        st = E.COACHES.get(t) or {}
        for role in ("HC", "OC", "DC"):
            c = st.get(role)
            if c:
                c["tenure"] = c.get("tenure", 0) + 1
                staffs += 1
    report["coach_records_advanced"] = staffs

    # ---------- 3b) PRESTIGE ----------
    # MOVED TO STAGE 1 (Dan, 2040). Prestige used to step here, at the end of the
    # offseason, which meant a programme's rise or fall reached the recruiting class
    # signed the cycle AFTER the season that earned it. It now runs at the TOP of the
    # offseason, in `carousel.py`, so the season just finished is reflected in the staff
    # hired and the class signed in the same cycle. Nothing to do here.

    # ---------- 4) reset ----------
    s["season"] = nxt
    s["next_week"] = 0                   # the calendar opens at week 0
    s["record"] = {t: {"W": 0, "L": 0, "confW": 0, "confL": 0, "PF": 0, "PA": 0} for t in TEAMS}
    s["results"] = []
    s["season_stats"] = collections.defaultdict(dict)
    s["weekly_perf"] = []                # a LIST -- the poll and storyline code appends
    s["inj_out"] = {}
    s["inj_recent"] = {}
    s["inj_log"] = []
    s["heat"] = {t: 0.0 for t in TEAMS}
    s["pressure"] = {t: 0.0 for t in TEAMS}
    s["patience"] = {t: 0.0 for t in TEAMS}
    s["streak"] = {t: 0 for t in TEAMS}
    s["firings"] = []
    s["interims"] = {}
    s["storylines"] = []
    s["hc_changes_extra"] = []
    for k in ("media_poll_current", "media_poll_prev",
              "committee_poll_current", "committee_poll_prev"):
        s[k] = []
    # The hand-built-board flag belongs to the season that set it. Left True, the guard
    # in `play_week` keeps an EMPTY committee board "of record" from week 10 on and the
    # automatic ranking never runs. Found in the 2039 pre-season audit, 2026-10-11.
    s["committee_official"] = False
    # Gameview's visit list is per season: archive it, or the "already visited" penalty
    # carries last year's road trip into the new schedule (bitten at 2041 week 0).
    s["gameview_s%d" % (s["season"] - 1)] = dict(s.get("gameview") or {})
    s["gameview"] = {}
    # The finished season's FIXTURES go too. This was missed in the 2035 rollover and
    # found at the end of the 2036 one: every other piece of season state was cleared,
    # but `sched` still held the 948 games just played, so simulating week 0 of the new
    # year would have quietly replayed the old season's matchups. There is no error to
    # trip over -- `install_schedule`'s guard only checks that no results exist, which
    # is exactly the state a fresh rollover leaves. The schedule has to be rebuilt by
    # hand anyway (Dan builds the non-conference board, the conference games are filled
    # in after), so keeping the stale one has no value and one real failure mode.
    s["sched"] = []
    s["sub_opponents"] = {}
    # The weekly committee boards belong to the season that just ended. `season_archive`
    # already keeps its final 25, so this is safe to drop -- and it MUST be dropped,
    # because `export_playoff_board` reads `committee_history` for the board the seeding
    # starts from. Left behind, the 2037 playoff would have been seeded off the 2036
    # committee's last ranking with nothing to flag it. Found 2026-10-07.
    s["committee_history"] = {}
    s["media_history"] = {}
    # the media pool is drawn fresh each season (media_pool.py); ballots belong to the old year
    s["media_voter_prev"] = {}
    s["media_ballots"] = {}
    s["media_points_current"] = {}
    s["media_firsts_current"] = {}
    s.setdefault("season_archive", {})[str(done)] = archive

    # ---------- 5) preseason ----------
    # Same formula the engine has always used: top-30 talent, the head coach, the
    # program's standing, and a little noise.
    rngp = random.Random(313131 + nxt * 1009)
    pre = {}
    for t in TEAMS:
        top = sorted((p["abil"] for p in E.ROSTERS[t]), reverse=True)[:30]
        talent = sum(top) / len(top)
        pre[t] = round(talent
                       + E.COACHES[t]["HC"]["skill"] * 0.18
                       + PRESTIGE[t] * 0.012
                       + rngp.gauss(0, 0.25), 2)
    s["preseason"] = pre
    ranked = sorted(TEAMS, key=lambda t: -pre[t])
    report["preseason_top10"] = [(i + 1, t, pre[t]) for i, t in enumerate(ranked[:10])]
    report["preseason_range"] = (min(pre.values()), max(pre.values()))

    sizes = [len(E.ROSTERS[t]) for t in TEAMS]
    report["roster_sizes"] = (min(sizes), max(sizes))
    report["class_counts"] = dict(collections.Counter(
        p["cls"] for t in TEAMS for p in E.ROSTERS[t]))

    if commit:
        E.persist_rosters()
        # COACHES WERE NEVER SAVED. Step 3 above has been adding a year to every
        # coach's tenure since 2035 and then throwing it away at process exit, because
        # this block persisted rosters and the season state and nothing else. Three
        # cycles of tenure were lost that way; by 2038 every tenure in the league still
        # read its 2035 value, which is why the coaching board can only date a job
        # exactly from 2036 on. The increments cannot be recovered retroactively -- this
        # only stops the leak from here.
        with open(os.path.join(STATE, 'coaches.pkl'), 'wb') as f:
            pickle.dump(E.COACHES, f)
        SE.save_state(s)
        report["committed"] = True
    else:
        report["committed"] = False
    return report


if __name__ == "__main__":
    import json
    r = run_rollover(commit="--commit" in sys.argv)
    print("=== STAGE 7 — ROLLOVER %d -> %d (%d -> %d) ===" %
          (r["closing"], r["opening"], r["closing_year"], r["opening_year"]))
    print("  archived            %s champion=%s, %d teams' standings, %d poll rows"
          % (r["closing_year"], r["archived"]["champion"],
             r["archived"]["teams_in_standings"], r["archived"]["media_poll_rows"]))
    print("  class moves         %s" % r["class_moves"])
    print("  redshirts           %d" % r["redshirts"])
    print("  class counts        %s" % r["class_counts"])
    print("  roster sizes        %d-%d" % r["roster_sizes"])
    print("  staff records       %d advanced a year" % r["coach_records_advanced"])
    print("  preseason range     %.2f - %.2f" % r["preseason_range"])
    print("  preseason top 10:")
    for i, t, v in r["preseason_top10"]:
        print("     %2d. %-22s %.2f" % (i, t, v))
    print("  committed           %s" % r["committed"])
