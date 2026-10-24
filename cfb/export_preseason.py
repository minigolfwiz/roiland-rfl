"""Payload for the preseason top-25 preview.

Everything is a lookup or a computed figure, never a recall: the order comes from
`s['preseason']`, the projected win total is summed from `SE.win_prob` over the installed
schedule, rosters and staffs come from the engine, and the offseason movement comes from
the records each stage wrote (`carousel_s{N-1}`, `draft_s{N-1}`, `portal_s{N-1}`,
`recruiting_s{N-1}`).

The projection is an EXPECTED WIN TOTAL -- the sum of win probabilities across the twelve
scheduled games -- not a simulation. It says what the schedule and the roster are worth
before a ball is thrown, which is the honest thing to show in August.
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
PRESTIGE = U["prestige"]

TOP_N = 25
OFFENSE = {"QB", "RB", "WR", "TE", "OL"}


def build(out='/home/claude/cfb2/state/preseason.json', top_n=TOP_N):
    # Guest programmes live in their own tables until a simulation window registers them,
    # so `win_prob` cannot see a subdivision opponent before week 0 has run. Registering
    # them here is what the sim does anyway, and it is read-only for our purposes.
    import subdivision as _SUB
    _SUB.register(E)
    s = SE.load_state()
    season = s["season"]
    year = 2025 + season
    prev = season - 1
    pre = s["preseason"]
    eng_order = sorted(TEAMS, key=lambda t: -pre[t])
    eng_rank = {t: i + 1 for i, t in enumerate(eng_order)}
    # 2040 on: the preview runs in MEDIA POLL order (the ranking of record before the
    # committee), with the engine's own rank shown alongside
    poll = [t for _r, t in (s.get("media_poll_current") or [])]
    order = (poll + [t for t in eng_order if t not in poll]) if poll else eng_order
    rank_of = {t: i + 1 for i, t in enumerate(order)}
    top = order[:top_n]

    # ---- last season, from the archive (season state has been reset) ----
    arch = (s.get("season_archive", {}).get(str(prev), {}) or {})
    standings = arch.get("standings", {})
    champion = arch.get("champion")
    hist = s.get("history", {})
    book = hist.get("book", {})
    champ_hist = hist.get("champ", {})

    # ---- the schedule, and what it is worth ----
    sched = collections.defaultdict(list)
    for wk, h, a, ic in s["sched"]:
        if h in TSET:
            sched[h].append({"w": wk, "opp": a, "home": True, "conf": bool(ic),
                             "sub": a not in TSET})
        if a in TSET:
            sched[a].append({"w": wk, "opp": h, "home": False, "conf": bool(ic),
                             "sub": h not in TSET})
    for t in sched:
        sched[t].sort(key=lambda g: g["w"])

    proj, sos = {}, {}
    for t in TEAMS:
        wins, opp_rank = 0.0, []
        for g in sched[t]:
            p = SE.win_prob(s, t if g["home"] else g["opp"],
                            g["opp"] if g["home"] else t,
                            site="home")
            wins += p if g["home"] else (1.0 - p)
            if not g["sub"]:
                opp_rank.append(pre[g["opp"]])
        proj[t] = round(wins, 1)
        sos[t] = round(sum(opp_rank) / len(opp_rank), 2) if opp_rank else 0.0
    sos_rank = {t: i + 1 for i, t in enumerate(sorted(TEAMS, key=lambda x: -sos[x]))}

    # ---- offseason movement ----
    carousel = s.get("carousel_s%d" % prev, {}) or {}
    new_hc = {f[0]: {"name": f[1], "skill": f[2], "how": f[3]}
              for f in carousel.get("filled", [])}
    coach_moves = carousel.get("coach_moves", [])
    moved_out = collections.defaultdict(list)
    for m in coach_moves:
        moved_out[m["from"]].append(m)

    drafted = collections.defaultdict(list)
    for p in (s.get("draft_s%d" % prev, {}) or {}).get("picks", []):
        if not p.get("subdivision") and p["team"] in TSET:
            drafted[p["team"]].append({"name": p["name"], "pos": p["pos"],
                                       "ov": p["overall"], "rd": p["round"],
                                       "early": bool(p.get("early"))})

    portal = s.get("portal_s%d" % prev, {}) or {}
    tr_in, tr_out = collections.defaultdict(list), collections.defaultdict(list)
    for x in portal.get("transfers", []):
        row = {"name": x["name"], "pos": x["pos"], "cls": x["cls"],
               "from": x["from"], "to": x["to"], "reason": x["reason"]}
        if x["to"] in TSET: tr_in[x["to"]].append(row)
        if x["from"] in TSET: tr_out[x["from"]].append(row)

    signed = (s.get("recruiting_s%d" % prev, {}) or {}).get("signed", {})

    dev = (s.get("development_s%d" % prev, {}) or {}).get("team_means", {})
    dev_rank = {t: i + 1 for i, t in enumerate(
        sorted(dev, key=lambda x: -dev[x]))} if dev else {}

    rows = []
    for t in top:
        roster = E.ROSTERS[t]
        # Best players on the roster, incoming freshmen included -- a 8.6 true freshman is
        # exactly who to watch. NOTE: the `freshman` flag cannot be used to find the new
        # class here, because the rollover pops it when it advances everyone else; after
        # stage 7 the incoming class is simply everyone still listed as "Fr".
        best = sorted(roster, key=lambda p: -p["abil"])
        stars = [{"name": p["name"], "pos": p["pos"], "cls": p["cls"],
                  "transfer": bool(p.get("transfer"))}
                 for p in best[:5]]
        frosh = [p for p in best if p["cls"] == "Fr"][:3]
        c = E.COACHES[t]
        rec = standings.get(t, {})
        bk = book.get(t, {})
        titles = bk.get("titles", [])
        sig = [r for r in signed.get(t, []) if r["stars"] >= 4]
        rows.append({
            "rank": rank_of[t], "name": t,
            "full": GEO.get(t, {}).get("full_name", t),
            "mascot": GEO.get(t, {}).get("mascot", ""),
            "conf": TC[t], "tier": TIERS.get(TC[t], "L6"),
            "col": list(COLORS.get(t, ["#555", "#999"])),
            "rating": round(pre[t], 2), "engRank": eng_rank[t], "pollPts": (s.get("media_points_current") or {}).get(t, 0),
            "prestige": round(PRESTIGE.get(t, 50), 1),
            "proj": proj[t], "sos": sos[t], "sosRank": sos_rank[t],
            "lastW": rec.get("W", 0), "lastL": rec.get("L", 0),
            "lastConfW": rec.get("confW", 0), "lastConfL": rec.get("confL", 0),
            "titles": titles, "lastTitle": max(titles) if titles else None,
            "defending": t == champion,
            # ratings stay behind the curtain (Dan): names and tenure only on the page
            "hc": {"name": c["HC"]["name"], "tenure": c["HC"].get("tenure", 0),
                   "new": t in new_hc, "how": new_hc.get(t, {}).get("how")},
            "oc": {"name": c["OC"]["name"], "tenure": c["OC"].get("tenure", 0)},
            "dc": {"name": c["DC"]["name"], "tenure": c["DC"].get("tenure", 0)},
            "lost_coaches": moved_out.get(t, []),
            "stars": stars,
            "frosh": [{"name": p["name"], "pos": p["pos"], "stars": p.get("stars")} for p in frosh],
            "drafted": sorted(drafted.get(t, []), key=lambda x: x["ov"]),
            "in": tr_in.get(t, []), "out": tr_out.get(t, []),
            "bluechips": len(sig), "class_size": len(signed.get(t, [])),
            "dev": dev.get(t), "devRank": dev_rank.get(t),
            "sched": sched[t],
        })

    # the written take on each team, kept beside the data rather than inside the page so
    # it can be edited without rebuilding anything
    notes = {}
    try:
        notes = json.load(open('/home/claude/cfb2/state/preseason_notes.json'))
    except FileNotFoundError:
        pass
    missing = [r["name"] for r in rows if r["name"] not in notes]
    if missing:
        print("  [no note written for: %s]" % ", ".join(missing))
    for r in rows:
        r["note"] = notes.get(r["name"], "")

    return _dump(out, {
        "season": season, "year": year, "prev_year": year - 1,
        "champion_prev": champion,
        "teams": rows,
        "ranks": {t: rank_of[t] for t in TEAMS},
        "proj_all": proj,
        "conferences": sorted(U["conferences"].keys()),
    })


def _dump(out, payload):
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


if __name__ == "__main__":
    p = build()
    print("%d preseason preview | %d teams" % (p["year"], len(p["teams"])))
    for t in p["teams"]:
        print("  %2d. %-22s %-16s proj %4.1f  (%d-%d last year)"
              % (t["rank"], t["name"], t["conf"], t["proj"], t["lastW"], t["lastL"]))
