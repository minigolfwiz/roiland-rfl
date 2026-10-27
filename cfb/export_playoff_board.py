"""Data for the playoff selection board.

Twenty-four seeds. All twelve conference champions qualify automatically, but Dan places
them — a champion can be seeded anywhere he judges, the only requirement is that all
twelve are in the field. Everything here is a lookup: ratings from `committee_rank`,
champions from the conference finals actually played, résumés from the games database
including the championship games.
"""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, committee as CM
from games_db import load_db

U = E.U
TEAMS = list(U["teams"])
TSET = set(TEAMS)
TC = U["team_conf"]
TIERS = U["tiers"]
GEO = U["geo"]
COLORS = U["team_colors"]


def build(out='/home/claude/cfb2/state/playoff_board.json'):
    s = SE.load_state()
    db = load_db()
    season = s.get("season", 11)
    tag = "S%d" % season
    ranked, scores, eff = CM.committee_rank(s, db)
    rank_of = {t: i + 1 for i, t in enumerate(ranked)}
    rating_rank = {t: i + 1 for i, t in enumerate(sorted(TEAMS, key=lambda x: -eff[x]))}
    champs = s.get("conf_champs_s%d" % season) or {}
    if not champs:   # ccg.py writes the champions to a pickle, not to season state
        import pickle, os
        pp = '/home/claude/cfb2/state/conf_champs_s%d.pkl' % season
        if os.path.exists(pp): champs = pickle.load(open(pp, 'rb'))
    champ_of = {t: c for c, t in champs.items()}

    # every game, regular season and conference final alike
    games = {t: [] for t in TEAMS}
    rows = [(wk, gid) for wk, gid in s["results"]]
    rows += [(15, gid) for gid in db if str(gid).startswith(tag + "CCG")]
    for wk, gid in rows:
        b = db.get(gid)
        if not b: continue
        for t, opp in ((b["home"], b["away"]), (b["away"], b["home"])):
            if t not in TSET: continue
            won = (b["home"] == t) == (b["home_score"] > b["away_score"])
            games[t].append({
                "w": wk, "opp": opp, "home": b["home"] == t, "won": won,
                "ps": b["home_score"] if b["home"] == t else b["away_score"],
                "pa": b["away_score"] if b["home"] == t else b["home_score"],
                "oppRank": rating_rank.get(opp), "sub": opp not in TSET,
                "ot": b.get("ot") or 0, "ccg": wk == 15,
            })
    for t in games:
        games[t].sort(key=lambda g: g["w"])

    teams = []
    for t in ranked:
        r = s["record"][t]
        g = games[t]
        teams.append({
            "name": t, "conf": TC[t], "tier": TIERS.get(TC[t], "L6"),
            "mascot": GEO.get(t, {}).get("mascot", ""),
            "full": GEO.get(t, {}).get("full_name", t),
            "col": list(COLORS.get(t, ["#555", "#999"])),
            "W": r["W"], "L": r["L"], "cW": r.get("confW", 0), "cL": r.get("confL", 0),
            "pf": r.get("PF", 0), "pa": r.get("PA", 0),
            "cRank": rank_of[t], "rating": round(eff[t], 2), "ratingRank": rating_rank[t],
            "champ": champ_of.get(t),                       # conference won, or None
            "qw": sum(1 for x in g if x["won"] and x["oppRank"] and x["oppRank"] <= 30),
            "bl": sum(1 for x in g if not x["won"] and x["oppRank"] and x["oppRank"] > 90),
            "games": g,
        })

    hist = s.get("committee_history") or {}
    last = hist.get(str(max((int(k) for k in hist), default=14)), [])
    return _dump(out, {
        "season": season, "year": 2025 + season, "seeds": 24, "byes": 8,
        "teams": teams,
        "conferences": sorted(U["conferences"].keys()),
        "champions": [{"conf": c, "team": t} for c, t in sorted(champs.items())],
        "final_committee": last,           # the week-14 board, as a starting reference
    })


def _dump(out, payload):
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


if __name__ == "__main__":
    p = build()
    print("season %d | %d teams | %d champions | %d seeds (%d byes)"
          % (p["season"], len(p["teams"]), len(p["champions"]), p["seeds"], p["byes"]))
    for c in p["champions"]:
        t = next(x for x in p["teams"] if x["name"] == c["team"])
        print("  %-16s %-22s %2d-%-2d  computer #%d" % (c["conf"], c["team"], t["W"], t["L"], t["cRank"]))
