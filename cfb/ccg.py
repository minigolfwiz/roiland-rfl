"""Conference championship week: P6 at neutral named venues, L6 hosted by #1 seed."""
import sys, pickle; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E
from committee import assign_venue
from games_db import load_db, load_reg, save_db, save_reg, assign_seed

def conf_order(s, db, conf, tl):
    """Full conference order: conference mark, then head-to-head inside the tied group,
    then overall wins, then net rating.

    Two bugs lived here for twelve seasons and are both fixed below.

    1. The tiebreak was written `grp.sort(key=lambda t: (-h2h_wins(t, set(grp)), ...))`.
       CPython's `list.sort()` swaps the list out for an empty one while the sort runs,
       so `set(grp)` inside the key function was ALWAYS empty: `h2h_wins` found no
       opponents in the group and returned 0 for everybody. The sort being stable, the
       term was a no-op and head-to-head never applied. Fixed by snapshotting the group
       before sorting and using `sorted()` rather than sorting in place.
    2. `h2h_wins` filtered only on `postseason`, never on season, so it would have
       counted every previous meeting between the tied teams across the whole database.
       Fixed by restricting the scan to this season's games.
    """
    this_season = {gid for _wk, gid in s["results"]}

    def mark(t): return s["record"][t]["confW"] - s["record"][t]["confL"]

    def h2h_wins(t, group):
        w = 0
        for gid in this_season:
            b = db.get(gid)
            if not b or b.get("postseason"):
                continue
            if t not in (b["home"], b["away"]):
                continue
            opp = b["away"] if b["home"] == t else b["home"]
            if opp not in group:
                continue
            own = b["home_score"] if b["home"] == t else b["away_score"]
            o = b["away_score"] if b["home"] == t else b["home_score"]
            if own > o:
                w += 1
        return w

    R = SE.net_ratings(s, db)
    order = sorted(tl, key=lambda t: -mark(t))
    final = []
    i = 0
    while i < len(order):
        grp = [t for t in order if mark(t) == mark(order[i]) and t not in final]
        group = frozenset(grp)          # snapshot: see bug 1 above
        final.extend(sorted(grp, key=lambda t: (-h2h_wins(t, group),
                                                -s["record"][t]["W"], -R["net"][t])))
        i = len(final)
    return final


def conf_top2(s, db, conf, tl):
    o = conf_order(s, db, conf, tl)
    return o[0], o[1]

def run_ccgs():
    s = SE.load_state()
    _seas = s.get('season', 1)
    db, reg = load_db(), load_reg()
    unavailable = frozenset(pid for pid, w in s["inj_out"].items() if w > 0)
    recent = frozenset(s["inj_recent"].keys())
    used_venues = set()
    results = []
    for conf, tl in E.U["conferences"].items():
        one, two = conf_top2(s, db, conf, tl)
        tier = E.U["tiers"][conf]
        # Dan's 2038 rule: every conference title game is played at that conference's
        # own fixed site, in a state hosting none of its members. This replaces two
        # things: the P6 games drawing from the playoff BOWL pool (drift that started in
        # 2036 and had the title games eating bowl slots ever since), and the L6 games
        # being hosted on the top seed's campus. All twelve are now neutral, so the L6
        # #1 seed loses a home advantage it used to have -- intended, since Dan named a
        # site for all twelve conferences.
        _sites = E.U.get("ccg_sites") or {}
        _from = E.U.get("ccg_sites_from_season", 10**9)
        if _seas >= _from and conf in _sites:
            _city, _state = _sites[conf]
            site = "neutral"; home, away = one, two
            venue_name = f"{_city}, {_state}"
            hfa = None
        elif tier == "P6":
            v = assign_venue(one, used_venues)
            site = "neutral"; home, away = one, two
            venue_name = f'{v["name"]} ({v["state"]})'
            hfa = None
        else:
            site = "home"; home, away = one, two
            venue_name = f"{home} (campus)"
            hfa = SE.dyn_hfa(s, home)
        gid = f"S{_seas}CCG_{conf.replace(' ','')}"
        if gid in db: raise RuntimeError("CCG already played: "+gid)
        seed = assign_seed(reg, gid)
        wp = SE.win_prob(s, home, away, site=site)
        box, pbp = E.simulate_game(home, away, seed, site=site, keep_pbp=True, postseason=True,
                                   unavailable_home=unavailable, unavailable_away=unavailable,
                                   recently_returned_home=recent, recently_returned_away=recent,
                                   hfa_override=hfa)
        import zlib, json
        box["pbp_z"] = zlib.compress(json.dumps(pbp).encode(), 6)
        box["game_id"] = gid; box["week"] = 15; box["venue"] = venue_name
        box["pregame_home_wp"] = round(wp,3); box["unav_h"]=sorted(unavailable, key=str); box["unav_a"]=sorted(unavailable, key=str)
        if hfa is not None: box["hfa_used"] = round(hfa,3)
        db[gid] = box
        hw = box["home_score"] > box["away_score"]
        wt, lt = (home, away) if hw else (away, home)
        s["record"][wt]["W"] += 1; s["record"][lt]["L"] += 1
        s["record"][home]["PF"] += box["home_score"]; s["record"][home]["PA"] += box["away_score"]
        s["record"][away]["PF"] += box["away_score"]; s["record"][away]["PA"] += box["home_score"]
        for inj in box["injuries"]:
            s["inj_out"][inj["pid"]] = inj["weeks_out"] if inj["weeks_out"] < 99 else 99
            s["inj_log"].append(dict(inj, week=15))
            for pl in E.ROSTERS[inj["team"]]:
                if pl["pid"] == inj["pid"]:
                    pl["inj_hist"].append({"season": _seas, "week": 15, "desc": inj["desc"], "weeks": inj["weeks_out"]})
        SE.merge_stats(s["season_stats"], box)
        E.update_reputation(box)
        results.append((conf, tier, wt, lt, box, venue_name))
    # weekly injury tick before playoffs
    healed = [pid for pid, w in s["inj_out"].items() if w-1 <= 0 and w < 99]
    s["inj_out"] = {pid: (w-1 if w < 99 else 99) for pid, w in s["inj_out"].items() if (w-1 > 0 or w >= 99)}
    s["inj_recent"] = {pid: c+1 for pid, c in s["inj_recent"].items() if c+1 <= 2}
    for pid in healed: s["inj_recent"][pid] = 1
    champs = {conf: wt for conf, tier, wt, lt, box, vn in results}
    with open(f'/home/claude/cfb2/state/conf_champs_s{_seas}.pkl','wb') as f: pickle.dump(champs, f)
    save_db(db); save_reg(reg); SE.save_state(s); E.persist_rosters()
    return results

if __name__ == "__main__":
    # GUARD (2041): running this file plays and COMMITS all twelve finals. It was run by
    # mistake while looking for a preview and had to be unwound by hand. Preview with
    # `python3 ccg.py --preview`; play with `--commit`.
    import sys as _sys
    if "--preview" in _sys.argv or "--commit" not in _sys.argv:
        import season as _SE
        _s = _SE.load_state()
        for conf in _SE.U["conferences"] if hasattr(_SE, "U") else E.U["conferences"]:
            pass
        print("DRY RUN -- nothing played. Use --commit to play the conference finals.")
        try:
            from ccg_preview import preview as _pv
            _pv()
        except Exception as _ex:
            print("(no preview module: %s)" % _ex)
        raise SystemExit(0)
    for conf, tier, wt, lt, box, vn in run_ccgs():
        sc = f"{box['home_score']}-{box['away_score']}" if box["home_score"]>box["away_score"] else f"{box['away_score']}-{box['home_score']}"
        ot = f" ({box['ot']}OT)" if box["ot"] else ""
        print(f"[{tier}] {conf}: {wt} def. {lt} {sc}{ot} @ {vn}")
