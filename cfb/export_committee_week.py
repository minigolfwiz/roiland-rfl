"""Data for the weekly committee ranking tool.

All 152 FBS programs in computer-rating order, each with the résumé the committee would
actually look at: the record, every game played with the opponent's rating rank and the
score, and the quality-win / bad-loss marks the engine itself uses.

Everything is a lookup. Ratings come from `committee_rank`, which is the same function the
engine uses to seed the playoff, so the order Dan is handed is the order the computer
would pick if left alone.
"""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, committee as CM
import resume_marks as RM
from games_db import load_db

U = E.U
TEAMS = list(U["teams"])
TSET = set(TEAMS)
TC = U["team_conf"]
TIERS = U["tiers"]
GEO = U["geo"]
COLORS = U["team_colors"]


def build(out='/home/claude/cfb2/state/committee_week.json'):
    s = SE.load_state()
    db = load_db()
    season = s.get("season", 11)
    week = s.get("next_week", 11) - 1          # the week just completed
    ranked, scores, eff = CM.committee_rank(s, db)
    rank_of = {t: i + 1 for i, t in enumerate(ranked)}
    rating_rank = {t: i + 1 for i, t in enumerate(sorted(TEAMS, key=lambda x: -eff[x]))}
    poll_rank = RM.current_rank(s)            # the marks are judged against THIS (Dan, 2041)

    # every team's season, game by game
    games = {t: [] for t in TEAMS}
    for wk, gid in s["results"]:
        b = db.get(gid)
        if not b: continue
        for t, opp in ((b["home"], b["away"]), (b["away"], b["home"])):
            if t not in TSET: continue
            won = (b["home"] == t) == (b["home_score"] > b["away_score"])
            ps = b["home_score"] if b["home"] == t else b["away_score"]
            pa = b["away_score"] if b["home"] == t else b["home_score"]
            games[t].append({
                "w": wk, "opp": opp, "home": b["home"] == t, "won": won,
                "ps": ps, "pa": pa,
                "oppRank": rating_rank.get(opp),            # None for subdivision guests
                "oppPoll": poll_rank.get(opp),
                "mark": RM.mark(won, opp, poll_rank, rating_rank.get(opp)),
                "sub": opp not in TSET,
                "ot": b.get("ot") or 0,
            })
    # Conference title games are not in `s["results"]` -- `ccg.run_ccgs` writes them
    # straight to the database under S{season}CCG_. They belong on the résumé: a final
    # ballot that cannot see who won their conference is missing the last thing that
    # happened. `committee_rank` already weighs them, so this only brings the page level
    # with the engine.
    champs = {}
    pre = "S%dCCG" % season
    for gid, b in db.items():
        if not str(gid).startswith(pre):
            continue
        hw = b["home_score"] > b["away_score"]
        champs[b["home"] if hw else b["away"]] = True
        for t, opp in ((b["home"], b["away"]), (b["away"], b["home"])):
            if t not in TSET:
                continue
            won = (b["home"] == t) == hw
            games[t].append({
                "w": 15, "opp": opp, "home": b["home"] == t, "won": won,
                "ps": b["home_score"] if b["home"] == t else b["away_score"],
                "pa": b["away_score"] if b["home"] == t else b["home_score"],
                "oppRank": rating_rank.get(opp), "sub": opp not in TSET,
                "oppPoll": poll_rank.get(opp),
                "mark": RM.mark(won, opp, poll_rank, rating_rank.get(opp)),
                "ot": b.get("ot") or 0, "ccg": True,
                # P6 title games are at named neutral bowls; L6 are hosted by the top seed
                "neutral": "(campus)" not in str(b.get("venue", "")),
            })
    for t in games:
        games[t].sort(key=lambda g: g["w"])

    teams = []
    for t in ranked:
        r = s["record"][t]
        g = games[t]
        # judged against the current rankings, not the rating (resume_marks.py)
        qw = sum(1 for x in g if x["mark"] == "qw")
        bl = sum(1 for x in g if x["mark"] == "bl")
        ql = sum(1 for x in g if x["mark"] == "ql")
        teams.append({
            "name": t, "conf": TC[t], "tier": TIERS.get(TC[t], "L6"),
            "mascot": GEO.get(t, {}).get("mascot", ""),
            "full": GEO.get(t, {}).get("full_name", t),
            "col": list(COLORS.get(t, ["#555", "#999"])),
            "W": r["W"], "L": r["L"], "cW": r.get("confW", 0), "cL": r.get("confL", 0),
            "pf": r.get("PF", 0), "pa": r.get("PA", 0),
            "cRank": rank_of[t],                 # committee's own order
            "rating": round(eff[t], 2),          # the efficiency rating itself
            "ratingRank": rating_rank[t],
            "score": round(scores[t], 2),
            "qw": qw, "ql": ql, "bl": bl,
            "champ": bool(champs.get(t)),
            "games": g,
        })

    payload = {
        "season": season, "year": 2025 + season, "week": week,
        # the selection ballot is the one taken after the title games
        "stage": "CCG" if champs else "WEEK",
        "marks_source": RM.source_label(s),
        "teams": teams,
        "conferences": sorted(U["conferences"].keys()),
        "media_poll": [list(x) for x in (s.get("media_poll_current") or [])][:25],
        # the committee's own standing board going into this ballot -- a better starting
        # point than the raw computer order, since it is the list Dan has been moving.
        "prior": [t for _r, t in sorted(s.get("committee_poll_current") or [])][:25],
        # Which week that board was taken after. On the page it decides whether the
        # reference number on each row reads "committee #" (this same week's board,
        # already installed) or "last week #" (the board being moved).
        "priorWeek": max((int(k) for k in (s.get("committee_history") or {})), default=None),
    }
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


if __name__ == "__main__":
    p = build()
    print("season %d week %d | %d teams ranked by computer rating"
          % (p["season"], p["week"], len(p["teams"])))
    for t in p["teams"][:10]:
        print("  %2d. %-22s %2d-%-2d  rating %6.2f   qw %d  ql %d  bl %d"
              % (t["cRank"], t["name"], t["W"], t["L"], t["rating"],
                 t["qw"], t["ql"], t["bl"]))
