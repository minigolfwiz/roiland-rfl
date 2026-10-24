"""Playoff runner: R1/R2 at higher seed's home; QF/SF/Champ at rotation cities."""
import sys, pickle, zlib, json; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db, load_reg, save_db, save_reg, assign_seed

def _play(s, db, reg, gid, home, away, site, venue_label, hfa):
    if gid in db: raise RuntimeError("already played: "+gid)
    unavailable = frozenset(pid for pid, w in s["inj_out"].items() if w > 0)
    recent = frozenset(s["inj_recent"].keys())
    seed = assign_seed(reg, gid)
    wp = SE.win_prob(s, home, away, site=site)
    box, pbp = E.simulate_game(home, away, seed, site=site, keep_pbp=True, postseason=True,
                               unavailable_home=unavailable, unavailable_away=unavailable,
                               recently_returned_home=recent, recently_returned_away=recent,
                               hfa_override=hfa)
    box["pbp_z"] = zlib.compress(json.dumps(pbp).encode(), 6)
    box["game_id"] = gid; box["week"] = 16; box["venue"] = venue_label
    box["pregame_home_wp"] = round(wp,3)
    box["unav_h"] = sorted(unavailable, key=str); box["unav_a"] = sorted(unavailable, key=str)
    if hfa is not None: box["hfa_used"] = round(hfa, 3)
    db[gid] = box
    hw = box["home_score"] > box["away_score"]
    wt, lt = (home, away) if hw else (away, home)
    s["record"][wt]["W"] += 1; s["record"][lt]["L"] += 1
    s["record"][home]["PF"] += box["home_score"]; s["record"][home]["PA"] += box["away_score"]
    s["record"][away]["PF"] += box["away_score"]; s["record"][away]["PA"] += box["home_score"]
    for inj in box["injuries"]:
        s["inj_out"][inj["pid"]] = inj["weeks_out"] if inj["weeks_out"] < 99 else 99
        s["inj_log"].append(dict(inj, week=box["week"]))
        for pl in E.ROSTERS[inj["team"]]:
            if pl["pid"] == inj["pid"]:
                pl["inj_hist"].append({"season": s.get("season", 1), "week": box["week"],
                                       "desc": inj["desc"], "weeks": inj["weeks_out"]})
    SE.merge_stats(s["season_stats"], box)
    E.update_reputation(box)
    return box, wt, lt

def week_tick(s):
    healed = [pid for pid, w in s["inj_out"].items() if w-1 <= 0 and w < 99]
    s["inj_out"] = {pid: (w-1 if w < 99 else 99) for pid, w in s["inj_out"].items() if (w-1 > 0 or w >= 99)}
    s["inj_recent"] = {pid: c+1 for pid, c in s["inj_recent"].items() if c+1 <= 2}
    for pid in healed: s["inj_recent"][pid] = 1

def run_round1():
    s = SE.load_state()
    _seas = s.get('season',1)
    with open(f'state/playoff_s{_seas}.pkl','rb') as f: P = pickle.load(f)
    db, reg = load_db(), load_reg()
    P["r1_results"] = []
    for home, away in P["r1"]:
        gid = f"S{_seas}PO_R1_{home.replace(' ','')}_{away.replace(' ','')}"
        hfa = SE.dyn_hfa(s, home)
        box, wt, lt = _play(s, db, reg, gid, home, away, "home", f"{home} (campus)", hfa)
        P["r1_results"].append({"gid": gid, "winner": wt, "loser": lt,
                                "score": (box["home_score"], box["away_score"]), "ot": box["ot"]})
        sd = P["seeds"]
        print(f"({sd[away]}) {away} {box['away_score']} at ({sd[home]}) {home} {box['home_score']}" + (f" ({box['ot']}OT)" if box["ot"] else "") + f"  -> {wt} advances")
    week_tick(s)
    with open(f'state/playoff_s{_seas}.pkl','wb') as f: pickle.dump(P, f)
    save_db(db); save_reg(reg); SE.save_state(s); E.persist_rosters()
    return P

# ---------------------------------------------------------------------------
# Rounds 2 through the title game. The recovered module carried only run_round1;
# these were rebuilt to the canon structure after the 2035 container reset:
#   R2  -- the eight bye teams host, RESEEDED (1 draws the lowest surviving seed)
#   QF  -- four neutral bowl sites, nearest unused venue to the higher seed
#   SF  -- two neutral sites, same rule
#   Championship -- the fixed championship venue
# ---------------------------------------------------------------------------
def _reseed(P, survivors):
    """Order survivors by their committee seed, best first."""
    return sorted(survivors, key=lambda t: P["seeds"][t])


def _pair_host(P, hosts, visitors):
    """Best host draws the worst visitor, and so on down."""
    hosts = _reseed(P, hosts)
    visitors = list(reversed(_reseed(P, visitors)))
    return list(zip(hosts, visitors))


def _neutral_round(P, pairs, tag, label_round):
    """Play a neutral-site round; returns the winners in seed order."""
    import committee as CM
    s = SE.load_state()
    _seas = s.get("season", 1)
    db, reg = load_db(), load_reg()
    # Dan's 2035 ruling is the NEAREST UNUSED BOWL. `used` was a fresh set on every
    # call, so it only held within a round: the semifinals drew from all seven bowls
    # again and happily reused a quarterfinal site. It now carries across the whole
    # postseason, stored on P so it survives between rounds. Backfilled from whatever
    # bowls earlier rounds already played in, so a postseason mid-flight is corrected
    # rather than restarted.
    # Tracked by CITY, not bowl name: Dan's 2037 renames mean a name in an old box
    # score need not match the name the pool uses for the same place.
    used = P.get("venues_used")
    if used is None:
        used = set()
        for key in ("qf_results", "sf_results"):
            for r in P.get(key, []):
                b = db.get(r["gid"])
                v = str(b.get("venue", "")) if b else ""
                if v and "(campus)" not in v and "(" in v:
                    used.add(v.split("(", 1)[1].split(",")[0].strip())
    used = set(used)
    # From 2038 the sites come off the published rotation (four bowls to the
    # quarterfinals, two to the semifinals). Before that, the old nearest-unused rule,
    # so seasons already played are untouched.
    rotating = _seas >= CM.ROTATION_FROM
    # A ruling can pin the sites for a round: P["venue_override"][tag] is a list of bowl
    # names, one per pair in order. Used when Dan overrides the computed assignment --
    # 2037's semifinals were swapped because the nearest-bowl rule sent Barhold the
    # wrong way. Anything pinned is recorded so the reason survives in the bracket.
    pinned = (P.get("venue_override") or {}).get(tag)
    by_name = {b["name"]: b for b in CM.BOWLS}
    if pinned is not None and len(pinned) != len(pairs):
        raise RuntimeError("venue_override[%s] has %d sites for %d games"
                           % (tag, len(pinned), len(pairs)))
    results, winners = [], []
    for idx, (high, low) in enumerate(pairs):
        if pinned is not None:
            venue = by_name[pinned[idx]]
            used.add(venue["city"])
        else:
            venue = (CM.rotation_venue(_seas, tag, high, used, low) if rotating
                     else CM.assign_venue(high, used))
        gid = f"S{_seas}PO_{tag}_{high.replace(' ','')}_{low.replace(' ','')}"
        label = f"{venue['name']} ({venue['city']}, {venue['state']})"
        box, wt, lt = _play(s, db, reg, gid, high, low, "neutral", label, 0.0)
        results.append({"gid": gid, "winner": wt, "loser": lt, "venue": label,
                        "score": (box["home_score"], box["away_score"]), "ot": box["ot"]})
        winners.append(wt)
        sd = P["seeds"]
        print(f"({sd[low]}) {low} {box['away_score']} vs ({sd[high]}) {high} {box['home_score']}"
              + (f" ({box['ot']}OT)" if box["ot"] else "")
              + f" @ {label}  -> {wt} advances")
    week_tick(s)
    P[tag.lower() + "_results"] = results
    P["venues_used"] = sorted(used)          # carried into the next neutral round
    save_db(db); save_reg(reg); SE.save_state(s); E.persist_rosters()
    return _reseed(P, winners)


def run_round2():
    s = SE.load_state(); _seas = s.get("season", 1)
    with open(f'state/playoff_s{_seas}.pkl', 'rb') as f: P = pickle.load(f)
    db, reg = load_db(), load_reg()
    survivors = [r["winner"] for r in P["r1_results"]]
    pairs = _pair_host(P, P["byes"], survivors)
    P["r2"] = pairs
    results, winners = [], []
    for home, away in pairs:
        gid = f"S{_seas}PO_R2_{home.replace(' ','')}_{away.replace(' ','')}"
        hfa = SE.dyn_hfa(s, home)
        box, wt, lt = _play(s, db, reg, gid, home, away, "home", f"{home} (campus)", hfa)
        results.append({"gid": gid, "winner": wt, "loser": lt,
                        "score": (box["home_score"], box["away_score"]), "ot": box["ot"]})
        winners.append(wt)
        sd = P["seeds"]
        print(f"({sd[away]}) {away} {box['away_score']} at ({sd[home]}) {home} {box['home_score']}"
              + (f" ({box['ot']}OT)" if box["ot"] else "") + f"  -> {wt} advances")
    week_tick(s)
    P["r2_results"] = results
    w = _reseed(P, winners)
    P["qf"] = list(zip(w[:4], list(reversed(w))[:4]))
    with open(f'state/playoff_s{_seas}.pkl', 'wb') as f: pickle.dump(P, f)
    save_db(db); save_reg(reg); SE.save_state(s); E.persist_rosters()
    return P


def run_qf():
    s = SE.load_state(); _seas = s.get("season", 1)
    with open(f'state/playoff_s{_seas}.pkl', 'rb') as f: P = pickle.load(f)
    w = _neutral_round(P, P["qf"], "QF", "quarterfinal")
    P["sf"] = list(zip(w[:2], list(reversed(w))[:2]))
    with open(f'state/playoff_s{_seas}.pkl', 'wb') as f: pickle.dump(P, f)
    return P


def run_sf():
    s = SE.load_state(); _seas = s.get("season", 1)
    with open(f'state/playoff_s{_seas}.pkl', 'rb') as f: P = pickle.load(f)
    w = _neutral_round(P, P["sf"], "SF", "semifinal")
    P["final"] = (w[0], w[1])
    with open(f'state/playoff_s{_seas}.pkl', 'wb') as f: pickle.dump(P, f)
    return P


def run_champ():
    import committee as CM
    s = SE.load_state(); _seas = s.get("season", 1)
    with open(f'state/playoff_s{_seas}.pkl', 'rb') as f: P = pickle.load(f)
    db, reg = load_db(), load_reg()
    high, low = P["final"]
    v = CM.champ_venue(_seas)
    label = f"{v['city']} ({v['state']})"
    gid = f"S{_seas}PO_CHAMP"
    box, wt, lt = _play(s, db, reg, gid, high, low, "neutral", label, 0.0)
    sd = P["seeds"]
    print(f"({sd[low]}) {low} {box['away_score']} vs ({sd[high]}) {high} {box['home_score']}"
          + (f" ({box['ot']}OT)" if box["ot"] else "") + f" @ {label}")
    print(f"*** NATIONAL CHAMPION: {wt} ***")
    P["champion"] = wt; P["runnerup"] = lt; P["champ_venue"] = label
    P["champ_score"] = (box["home_score"], box["away_score"])
    with open(f'state/playoff_s{_seas}.pkl', 'wb') as f: pickle.dump(P, f)
    save_db(db); save_reg(reg); SE.save_state(s); E.persist_rosters()
    # The canon award basis is regular season + conference title games ONLY; the playoff
    # is excluded. `finalize_season` honours that but only if it is HANDED that stat
    # aggregate -- left to default it falls back to `s`, which by now includes every
    # playoff game, and the awards silently go to whoever had the best January.
    # `state/season_state.pkl.pre_s{N}_po_r1` is that aggregate: the snapshot taken
    # after the title games and before round one.
    try:
        aw_state = None
        try:
            with open(f'state/season_state.pkl.pre_s{_seas}_po_r1', 'rb') as f:
                aw_state = pickle.load(f)
        except FileNotFoundError:
            print("[finalize] WARNING: no pre-round-one snapshot; awards would include "
                  "playoff statistics, which is not the canon basis. Awards NOT written.")
        if aw_state is not None:
            CM.finalize_season(s, P, SE.save_state, award_state=aw_state)
            print("season canonized:", 2025 + _seas, "champion", wt, "| runner-up", lt)
    except Exception as ex:
        print("[finalize]", ex)
    return P


if __name__ == "__main__":
    run_round1()
