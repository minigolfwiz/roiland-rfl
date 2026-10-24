"""Payload for the Media Pool page: the season's sixty voters, their bios and trait
readouts, plus every weekly ballot filed so far and the composite each week."""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E


def trait_chips(tr):
    chips = []
    def lvl(v, lo, hi, name_lo, name_hi):
        if v >= hi: chips.append(name_hi)
        elif v <= lo: chips.append(name_lo)
    lvl(tr["w_last"], 0.6, 1.55, "last year: shrug", "last year: gospel")
    lvl(tr["w_recruit"], 0.6, 1.55, "recruiting: skeptic", "recruiting: believer")
    lvl(tr["w_talent"], 0.6, 1.55, "roster: results only", "roster: on paper")
    lvl(tr["w_results"], 0.75, 1.3, "slow to move", "overreacts")
    if tr["homer"] < 0: chips.append("underrates own school")
    elif tr["homer"] > 11: chips.append("homer")
    if tr["rival"] < -8: chips.append("rival grudge")
    if tr["contrarian"] > 0: chips.append("contrarian")
    if tr["inertia"] > 0.55: chips.append("sticky ballot")
    elif tr["inertia"] < 0.22: chips.append("rebuilds weekly")
    if tr["noise"] > 6.5: chips.append("erratic")
    if tr.get("surprise", 0) >= 0.3: chips.append("surprise picks")
    return chips


def main(out='/home/claude/cfb2/state/media_pool_view.json'):
    s = SE.load_state(); U = E.U
    season = s["season"]; year = 2025 + season
    voters = s.get("media_pool_s%d" % season) or []
    rows = []
    for v in voters:
        rows.append({"id": v["id"], "name": v["name"], "age": v["age"], "team": v["team"], "conf": v["conf"],
                     "tier": U["tiers"][v["conf"]], "role": v["role"], "outlet": v["outlet"], "bio": v["bio"],
                     "chips": trait_chips(v["traits"]), "colors": U["team_colors"].get(v["team"], ["#444", "#999"])})
    ballots = {str(w): b for w, b in (s.get("media_ballots") or {}).items()}
    hist = {str(w): lst for w, lst in (s.get("media_history") or {}).items()}
    cur = [t for _r, t in (s.get("media_poll_current") or [])][:25]
    payload = {"season": season, "year": year, "voters": rows, "ballots": ballots, "composite": hist,
               "current": cur, "prev": [t for _r, t in (s.get("media_poll_prev") or [])][:25],
               "prev_label": ("preseason" if len(s.get("media_history") or {}) <= 2 else "last week"),
               "points": s.get("media_points_current") or {}, "firsts": s.get("media_firsts_current") or {},
               "confs": list(U["tiers"]), "record": {t: [r["W"], r["L"]] for t, r in s["record"].items()},
               "colors": {t: U["team_colors"].get(t, ["#444", "#999"]) for t in U["teams"]}}
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


if __name__ == '__main__':
    p = main()
    print(len(p["voters"]), "voters;", len(p["ballots"]), "weeks of ballots")
