"""Ten-year conference plan (Dan, 2026-10-24): conference opponents and hosts for every
season in the window are drawn in advance, so a team's page can show exactly who it
plays in the conference for any year -- the way real CFB publishes conference slates
years ahead.

It reuses the SAME rules as the yearly Conference Office draw (export_conf_board):
  * choose_slate     -- each programme skips n-10 conference foes; the most-worn pairings
                         (played most often / most recently) are skipped first
  * locked rivalries -- never skipped; host alternates every year; split-venue rule kept
  * host alternation -- a pair that met last season turns around; the 4/5 home split
                         SWAPS every season; lopsided historic series bleed back
Year 1 reads the real games database. Every later year reads the plan's OWN previous
year as history, so the ten drawn seasons stay mutually fair (no pair skipped forever,
no venue repeated).

    python3 conf_plan.py [first_season=18] [years=10]   -> state/conf_plan.json
export_conf_board.build() uses state/conf_plan.json for the season it is building when
the plan has it, so the plan IS the season's conference slate, not a suggestion.
"""
import sys, json, collections
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E
import export_conf_board as X
from games_db import load_db

U = E.U
OUT = '/home/claude/cfb2/state/conf_plan.json'


def history(done):
    """Real history through season `done`: last-season hosts, five-season play counts,
    whole-era venue ledger, last meeting."""
    db = load_db()
    hosts, played = {}, collections.defaultdict(set)
    series_home = collections.defaultdict(collections.Counter)
    last_meet = {}
    for gid, b in db.items():
        sn, wk = X.season_week(gid)
        if sn is None or b.get("postseason"):
            continue
        h, a = b.get("home"), b.get("away")
        if h is None or a is None or U["team_conf"].get(h) != U["team_conf"].get(a):
            continue
        pk = "|".join(sorted((h, a)))
        if sn == done:
            hosts[pk] = h
        if sn > done - X.HISTORY:
            played[pk].add(sn)
        series_home[pk][h] += 1
        if sn >= last_meet.get(pk, (0, None))[0]:
            last_meet[pk] = (sn, h)
    return hosts, played, series_home, last_meet


def draw_conference(conf, season, hosts, played, series_home, last_meet, seed):
    teams = list(U["conferences"][conf])
    TS = set(teams)
    done = season - 1
    locked = []
    for p in U["fixed_pairs"]:
        if p["is_conf"] and p["team_a"] in TS and p["team_b"] in TS:
            pk = "|".join(sorted((p["team_a"], p["team_b"])))
            prev = hosts.get(pk)
            host = p["team_b"] if prev == p["team_a"] else p["team_a"]
            locked.append({"a": p["team_a"], "b": p["team_b"], "week": p["week"],
                           "type": p["type"], "host": host, "prev_host": prev,
                           "bye_before": bool(p.get("bye_before"))})
    locked = X.split_locked_venues(locked)
    locked_pairs = {"|".join(sorted((L["a"], L["b"]))) for L in locked}
    pairs = X.choose_slate(teams, locked_pairs, played, done, seed)
    games = []
    for pk in sorted(pairs):
        x, y = pk.split("|")
        L = next((l for l in locked if {l["a"], l["b"]} == {x, y}), None)
        if L:
            games.append({"a": L["a"], "b": L["b"], "host": L["host"],
                          "week": L["week"], "locked": True, "type": L["type"]})
            continue
        prev = hosts.get(pk)
        if prev:
            host = y if prev == x else x
        else:
            hx, hy = series_home[pk][x], series_home[pk][y]
            if hx != hy:
                host = x if hx < hy else y
            else:
                lh = last_meet.get(pk, (0, None))[1]
                host = y if lh == x else x
        games.append({"a": x, "b": y, "host": host, "week": None, "locked": False})
    prev_home = collections.Counter(hosts.values())
    target = {t: X.CONF_GAMES - prev_home[t] for t in teams
              if prev_home[t] in (X.CONF_GAMES // 2, X.CONF_GAMES - X.CONF_GAMES // 2)}
    games = X.balance_hosts(games, teams, locked_pairs, hosts, target, series_home=series_home)
    return games


# Dan 2026-10-27: Western Coast has three teams with no week-14 rival. Each season one existing
# conference game among them is locked to week 14 so the third team is free for a week-14 non-con game.
W14_ROT = {"Western Coast": ["Skylar Rose", "Kaji Kita State", "Barhold Valley"]}   # left-out team, in rotation

W14_OVERRIDE = {2047: "Kaji Kita State"}   # Dan booked Southern Tengus at KKS in wk 14, 2047

def apply_w14_rotation(plan, first):
    for ci, (conf, trio) in enumerate(W14_ROT.items()):
        for year, p in plan.items():
            left = W14_OVERRIDE.get(int(year), trio[(int(year) - 2044) % 3])
            gs = [g for g in p["conferences"][conf] if g["a"] in trio and g["b"] in trio and left not in (g["a"], g["b"])]
            assert len(gs) == 1, (year, conf, left, gs)
            gs[0]["week"] = 14; gs[0]["locked"] = True; gs[0]["type"] = "w14_rotation"

def main(first=18, years=10, seed=13):
    hosts, played, series_home, last_meet = history(first - 1)
    plan = {}
    for season in range(first, first + years):
        year = 2025 + season
        plan[str(year)] = {"season": season, "conferences": {}}
        new_hosts = {}
        for conf in U["conferences"]:
            g = draw_conference(conf, season, hosts, played, series_home, last_meet,
                                seed + season)
            plan[str(year)]["conferences"][conf] = [
                {"a": x["a"], "b": x["b"], "host": x["host"], "week": x.get("week"),
                 "locked": bool(x.get("locked")), "type": x.get("type")} for x in g]
            for x in g:
                pk = "|".join(sorted((x["a"], x["b"])))
                new_hosts[pk] = x["host"]
        # roll the simulated season into history for the next draw
        for pk, h in new_hosts.items():
            a, b = pk.split("|")
            played[pk].add(season)
            series_home[pk][h] += 1
            last_meet[pk] = (season, h)
        hosts = new_hosts
        for pk in list(played):
            played[pk] = {s for s in played[pk] if s > season - X.HISTORY}
    apply_w14_rotation(plan, first)
    json.dump(plan, open(OUT, "w"))
    return plan


def audit(plan):
    probs = []
    yrs = sorted(plan)
    for y in yrs:
        for conf, gs in plan[y]["conferences"].items():
            n = collections.Counter(); home = collections.Counter()
            for g in gs:
                n[g["a"]] += 1; n[g["b"]] += 1; home[g["host"]] += 1
            for t in U["conferences"][conf]:
                if n[t] != 9: probs.append((y, t, "games", n[t]))
                if home[t] not in (4, 5): probs.append((y, t, "home", home[t]))
    # series turnaround and gaps
    for conf in U["conferences"]:
        seen = collections.defaultdict(list)
        for y in yrs:
            for g in plan[y]["conferences"][conf]:
                seen["|".join(sorted((g["a"], g["b"])))].append((y, g["host"]))
        for pk, ms in seen.items():
            for (y1, h1), (y2, h2) in zip(ms, ms[1:]):
                if int(y2) == int(y1) + 1 and h1 == h2:
                    probs.append((pk, y2, "same host back-to-back"))
    return probs


if __name__ == "__main__":
    first = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    years = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    plan = main(first, years)
    pr = audit(plan)
    print("planned %d seasons: %s" % (len(plan), ", ".join(sorted(plan))))
    print("problems:", len(pr))
    for p in pr[:25]:
        print("  ", p)
