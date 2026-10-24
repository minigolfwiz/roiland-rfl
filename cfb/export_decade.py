"""Ten seasons of win totals for every program, with how each year ended.

Everything is derived from the games database rather than from any stored standings:
`season_archive` only goes back two seasons, and `history.book[...]['playoff_app']` was
backfilled and only carries 2035-36, so it cannot answer "did they make it in 2029".
Box scores carry their own week, home and away, and playoff games carry PO in the id, so
the database can answer all of it for every season it holds.

The BAR is regular-season wins only -- a flat 0-12 scale every program and every season
shares. Conference finals and playoff games are deliberately left out of the height,
because counting them would make a team's bar taller for having been good enough to play
more games, which is the thing the colour is already saying.
"""
import sys, json, re, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db

U = E.U
TEAMS = sorted(U["teams"])
TSET = set(TEAMS)
TC = U["team_conf"]
TIERS = U["tiers"]
GEO = U["geo"]
COLORS = U["team_colors"]

N_SEASONS = 10


def build(out='/home/claude/cfb2/state/decade.json'):
    s = SE.load_state()
    db = load_db()
    champ_hist = s.get("history", {}).get("champ", {})

    def season_of(gid):
        m = re.match(r"^S(\d+)[WCP]", str(gid))
        return int(m.group(1)) if m else None

    rec = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    playoff = collections.defaultdict(set)
    finals = collections.defaultdict(set)
    seasons_seen = collections.Counter()

    for gid, b in db.items():
        sn = season_of(gid)
        if sn is None:
            continue
        gid = str(gid)
        seasons_seen[sn] += 1
        post = b.get("postseason") or "CCG" in gid or "PO" in gid
        if "PO" in gid:
            for t in (b.get("home"), b.get("away")):
                if t in TSET:
                    playoff[sn].add(t)
            if "CHAMP" in gid:
                for t in (b.get("home"), b.get("away")):
                    if t in TSET:
                        finals[sn].add(t)
        if post:
            continue
        hw = b.get("home_score", 0) > b.get("away_score", 0)
        for t, won in ((b.get("home"), hw), (b.get("away"), not hw)):
            if t in TSET:
                rec[sn][t][0 if won else 1] += 1

    # the ten most recent COMPLETE seasons. A season still being played would show
    # short bars for everyone and make the whole comparison lie.
    complete = [sn for sn in sorted(seasons_seen) if len(playoff.get(sn, ())) >= 24]
    use = complete[-N_SEASONS:]

    teams = []
    for t in TEAMS:
        years = []
        for sn in use:
            w, l = rec[sn].get(t, [0, 0])
            year = 2025 + sn
            champ = champ_hist.get(year)
            champ_name = champ[0] if isinstance(champ, (list, tuple)) else champ
            if isinstance(champ_name, (list, tuple)):          # old shared-title rows
                won_it = t in champ_name
            else:
                won_it = (t == champ_name)
            years.append({
                "y": year, "w": w, "l": l,
                "o": "champ" if won_it else ("final" if t in finals.get(sn, ())
                     else ("po" if t in playoff.get(sn, ()) else "out")),
            })
        tot = sum(x["w"] for x in years)
        teams.append({
            "name": t, "conf": TC[t], "tier": TIERS.get(TC[t], "L6"),
            "full": GEO.get(t, {}).get("full_name", t),
            "mascot": GEO.get(t, {}).get("mascot", ""),
            "col": list(COLORS.get(t, ["#555", "#999"])),
            "years": years,
            "tot": tot, "best": max(x["w"] for x in years),
            "po": sum(1 for x in years if x["o"] != "out"),
            "titles": sum(1 for x in years if x["o"] == "champ"),
        })

    return _dump(out, {
        "years": [2025 + sn for sn in use],
        "teams": teams,
        "conferences": sorted(U["conferences"].keys()),
        "games_per_season": 12,
    })


def _dump(out, payload):
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


if __name__ == "__main__":
    p = build()
    print("%d seasons (%d-%d) | %d programmes"
          % (len(p["years"]), p["years"][0], p["years"][-1], len(p["teams"])))
    top = sorted(p["teams"], key=lambda x: -x["tot"])[:6]
    for t in top:
        print("  %-22s %3d wins | %d playoffs | %d titles"
              % (t["name"], t["tot"], t["po"], t["titles"]))
    import collections as C
    print("  outcome mix:", dict(C.Counter(y["o"] for t in p["teams"] for y in t["years"])))
