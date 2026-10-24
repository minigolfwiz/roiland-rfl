"""Payload for the draft board.

Everything here is a lookup. The picks come from `s['draft_s{N}']['picks']` exactly as
the draft stored them; conferences, mascots and colours come from the universe so the
marks render the same way they do everywhere else. Subdivision picks carry no FBS entry,
so they get the plain Subdivision disc like guest programmes do in the season viewer.
"""
import sys, json, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E

U = E.U
TEAMS = list(U["teams"])
TSET = set(TEAMS)
TC = U["team_conf"]
TIERS = U["tiers"]
GEO = U["geo"]
COLORS = U["team_colors"]


def build(out='/home/claude/cfb2/state/draft_board.json'):
    s = SE.load_state()
    season = s.get("season", 11)
    picks = (s.get("draft_s%d" % season) or {}).get("picks") or []
    if not picks:
        raise RuntimeError("no picks stored for season %d -- run the draft first" % season)
    dep = s.get("departures_s%d" % season) or {}

    rows = []
    for p in picks:
        sub = bool(p.get("subdivision"))
        rows.append({
            "ov": p["overall"], "rd": p["round"], "pk": p["pick"],
            "name": p["name"], "pos": p["pos"], "cls": p.get("cls", ""),
            "team": p["team"], "sub": 1 if sub else 0,
            "early": 1 if p.get("early") else 0,
            "reach": 1 if p.get("reach") else 0,
            "abil": p.get("abil"),
            "prod": round(p.get("prod") or 0.0, 1),
        })

    # one entry per program that produced a pick, plus every FBS program so the
    # by-program view can show who came away with nothing
    prog = collections.Counter(r["team"] for r in rows if not r["sub"])
    subprog = collections.Counter(r["team"] for r in rows if r["sub"])

    teams = {}
    for t in TEAMS:
        teams[t] = {"conf": TC[t], "tier": TIERS.get(TC[t], "L6"),
                    "full": GEO.get(t, {}).get("full_name", t),
                    "mascot": GEO.get(t, {}).get("mascot", ""),
                    "col": list(COLORS.get(t, ["#555", "#999"])),
                    "n": prog.get(t, 0)}
    for t in subprog:
        teams[t] = {"conf": "Subdivision", "tier": "SUB", "full": t, "mascot": "",
                    "col": ["#6b6355", "#938b78"], "sub": 1, "n": subprog[t]}

    # conference totals, which is the quickest read on where the talent was
    byconf = collections.Counter(TC[r["team"]] for r in rows if not r["sub"])
    byconf["Subdivision"] = sum(subprog.values())

    return _dump(out, {
        "season": season, "year": 2025 + season,
        "rounds": max(r["rd"] for r in rows), "per_round": max(r["pk"] for r in rows),
        "picks": rows,
        "teams": teams,
        "conferences": sorted(U["conferences"].keys()),
        "byconf": dict(byconf),
        "departures": {"left": dep.get("n"), "drafted": dep.get("drafted"),
                       "withdrew": dep.get("withdrew")},
    })


def _dump(out, payload):
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


if __name__ == "__main__":
    p = build()
    import collections as C
    cls = C.Counter(r["cls"] for r in p["picks"])
    print("%d (%d) | %d picks over %d rounds | %d programmes"
          % (p["season"], p["year"], len(p["picks"]), p["rounds"],
             sum(1 for t in p["teams"].values() if t["n"])))
    print("  by class:", dict(cls))
    print("  early entrants:", sum(r["early"] for r in p["picks"]))
    print("  departures:", p["departures"])
