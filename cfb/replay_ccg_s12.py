"""One-off: re-run the three 2037 conference title games that sent the wrong team.

Dan's ruling: the three games whose PARTICIPANTS were wrong are re-run with the
head-to-head tiebreak working; the other nine stay exactly as played, Broad South
included (right pair, wrong host -- kept as canon).

The nine kept games are NOT re-simulated. Their box scores are copied verbatim from
the pre-CCG backup database, because the rosters have already absorbed reputation
updates from the first pass and a fresh simulation would no longer reproduce them.
Copying guarantees canon is preserved byte for byte.

Residue, disclosed: `E.update_reputation` ran once for the three voided games before
they were voided, and reputation is an EWMA with no stored history, so it cannot be
unwound. Six rosters (Barhold, Skeenerland State, Orlot, Eona, UN Steelbridge,
West Hatesei St) carry a small unremovable trace of a game that no longer happened.
This is the same class of residue as the 2035 R2 replay.
"""
import sys, pickle, zlib, json
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, ccg
from committee import assign_venue
from games_db import load_db, load_reg, save_db, save_reg, assign_seed

BASE = '/home/claude/cfb2/state'
SEAS = 12
# the three whose participants were wrong; everything else is kept as played
REDO = {"Power North", "Great Fourteen", "Brass Belt"}


def main():
    # ---- restore the pre-title-game state and database -------------------------
    s = pickle.load(open(f'{BASE}/season_state.pkl.pre_s12_ccg', 'rb'))
    db = pickle.load(open(f'{BASE}/games_db.pkl.pre_s12_ccg', 'rb'))
    played = pickle.load(open(f'{BASE}/games_db.pkl', 'rb'))      # the first pass
    reg = load_reg()

    assert s["next_week"] == 15, s["next_week"]
    assert not any(str(g).startswith(f"S{SEAS}CCG") for g in db), "backup is not pre-CCG"

    # ---- clear the roster history the voided games wrote ------------------------
    # inj_hist is a plain log and can be cleaned; reputation cannot (see docstring).
    wiped = 0
    for tl in E.ROSTERS.values():
        for pl in tl:
            n = len(pl["inj_hist"])
            # a handful of pre-2035 entries are bare year strings, not dicts
            pl["inj_hist"] = [h for h in pl["inj_hist"]
                              if not (isinstance(h, dict)
                                      and h.get("season") == SEAS and h.get("week") == 15)]
            wiped += n - len(pl["inj_hist"])
    print(f"cleared {wiped} week-15 injury-history entries from the first pass")

    # the three gids need their seeds released; the consumed seeds are left spent,
    # which is honest -- those games were simulated, then voided.
    for conf in REDO:
        gid = f"S{SEAS}CCG_{conf.replace(' ', '')}"
        reg["assigned"].pop(gid, None)

    # ---- venues already spoken for by the nine kept games -----------------------
    used_venues = set()
    for conf in E.U["conferences"]:
        if conf in REDO:
            continue
        gid = f"S{SEAS}CCG_{conf.replace(' ', '')}"
        b = played[gid]
        if "(campus)" not in b["venue"]:
            used_venues.add(b["venue"].split(" (")[0])

    unavailable = frozenset(pid for pid, w in s["inj_out"].items() if w > 0)
    recent = frozenset(s["inj_recent"].keys())

    def apply_effects(box, home, away):
        hw = box["home_score"] > box["away_score"]
        wt, lt = (home, away) if hw else (away, home)
        s["record"][wt]["W"] += 1
        s["record"][lt]["L"] += 1
        s["record"][home]["PF"] += box["home_score"]
        s["record"][home]["PA"] += box["away_score"]
        s["record"][away]["PF"] += box["away_score"]
        s["record"][away]["PA"] += box["home_score"]
        for inj in box["injuries"]:
            s["inj_out"][inj["pid"]] = inj["weeks_out"] if inj["weeks_out"] < 99 else 99
            s["inj_log"].append(dict(inj, week=15))
            for pl in E.ROSTERS[inj["team"]]:
                if pl["pid"] == inj["pid"]:
                    pl["inj_hist"].append({"season": SEAS, "week": 15,
                                           "desc": inj["desc"], "weeks": inj["weeks_out"]})
        SE.merge_stats(s["season_stats"], box)
        E.update_reputation(box)
        return wt, lt

    results = []
    for conf, tl in E.U["conferences"].items():
        gid = f"S{SEAS}CCG_{conf.replace(' ', '')}"
        tier = E.U["tiers"][conf]

        if conf not in REDO:
            box = played[gid]                       # verbatim: canon, untouched
            db[gid] = box
            wt, lt = apply_effects(box, box["home"], box["away"])
            results.append((conf, tier, wt, lt, box, box["venue"], "kept"))
            continue

        one, two = ccg.conf_top2(s, db, conf, tl)   # now with head-to-head working
        if tier == "P6":
            v = assign_venue(one, used_venues)
            site, home, away = "neutral", one, two
            venue_name = f'{v["name"]} ({v["state"]})'
            hfa = None
        else:
            site, home, away = "home", one, two
            venue_name = f"{home} (campus)"
            hfa = SE.dyn_hfa(s, home)
        seed = assign_seed(reg, gid)
        wp = SE.win_prob(s, home, away, site=site)
        box, pbp = E.simulate_game(home, away, seed, site=site, keep_pbp=True,
                                   postseason=True,
                                   unavailable_home=unavailable, unavailable_away=unavailable,
                                   recently_returned_home=recent, recently_returned_away=recent,
                                   hfa_override=hfa)
        box["pbp_z"] = zlib.compress(json.dumps(pbp).encode(), 6)
        box["game_id"] = gid
        box["week"] = 15
        box["venue"] = venue_name
        box["pregame_home_wp"] = round(wp, 3)
        box["unav_h"] = sorted(unavailable, key=str)
        box["unav_a"] = sorted(unavailable, key=str)
        if hfa is not None:
            box["hfa_used"] = round(hfa, 3)
        db[gid] = box
        wt, lt = apply_effects(box, home, away)
        results.append((conf, tier, wt, lt, box, venue_name, "RE-RUN"))

    # weekly injury tick before the playoff
    healed = [pid for pid, w in s["inj_out"].items() if w - 1 <= 0 and w < 99]
    s["inj_out"] = {pid: (w - 1 if w < 99 else 99) for pid, w in s["inj_out"].items()
                    if (w - 1 > 0 or w >= 99)}
    s["inj_recent"] = {pid: c + 1 for pid, c in s["inj_recent"].items() if c + 1 <= 2}
    for pid in healed:
        s["inj_recent"][pid] = 1

    champs = {conf: wt for conf, tier, wt, lt, box, vn, how in results}
    pickle.dump(champs, open(f'{BASE}/conf_champs_s{SEAS}.pkl', 'wb'))
    save_db(db)
    save_reg(reg)
    SE.save_state(s)
    E.persist_rosters()

    # ---- verify the nine kept games are identical to what was played ------------
    for conf, tier, wt, lt, box, vn, how in results:
        if how != "kept":
            continue
        gid = f"S{SEAS}CCG_{conf.replace(' ', '')}"
        old = played[gid]
        assert (old["home"], old["away"], old["home_score"], old["away_score"],
                old["venue"]) == (box["home"], box["away"], box["home_score"],
                                  box["away_score"], box["venue"]), conf
    print("verified: all nine kept games are byte-identical to the first pass\n")

    for conf, tier, wt, lt, box, vn, how in results:
        sc = (f"{box['home_score']}-{box['away_score']}"
              if box["home_score"] > box["away_score"]
              else f"{box['away_score']}-{box['home_score']}")
        ot = f" ({box['ot']}OT)" if box["ot"] else ""
        print(f"[{tier}] {'%-6s' % how} {conf}: {wt} def. {lt} {sc}{ot} @ {vn}")
    return results


if __name__ == "__main__":
    main()
