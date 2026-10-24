"""Phase 4: selection committee (in-season efficiency + resume), named venues w/ proximity,
and end-of-season awards (Ryskamp Trophy [Player of the Year], DPOY, CoY, FoY, All-America, All-Rookie)."""
import math, collections
import sys; sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E

U = E.U; TEAMS = U["teams"]; CONF = U["team_conf"]; TIERS = U["tiers"]; COORDS = U["state_coords"]
GEO = U["geo"]

# ---------------- named venues (spec 10) ----------------
# ---------------------------------------------------------------------------
# THE BOWLS (canon, recovered from the geography export after the 2035 reset).
# Six neutral bowl sites host the quarterfinals and semifinals; the national
# championship is played in a rotating host city, separate from the bowls.
#
# Dan's ruling, 2035: neutral-round sites go to the NEAREST UNUSED BOWL to the
# higher seed. The per-season rotation the pre-reset engine used was lost (box
# scores never stored the venue), so this replaces it going forward.
#
# The championship city advances one step through the host-city roll each year.
# That rule is anchored on the two most recent known title sites -- 2033 Denning
# (Diveo) and 2034 Perth (Eona), consecutive entries in the roll -- which puts
# 2035 at the next city. Disclosed as a reconstruction, not recovered logic.
# ---------------------------------------------------------------------------
# The pool is universe data, not a second copy here. It was hardcoded in this module AND
# stored in `U["bowls"]`, which is two sources of truth for one list; Dan's 2037 changes
# to the pool would have had to be made twice and would have drifted the moment one was
# missed. `U["bowl_roll"]` is the published order the rotation walks.
BOWLS = [{"name": n, "city": c, "state": s}
         for n, (c, s) in ((n, E.U["bowls"][n])
                           for n in E.U.get("bowl_roll") or list(E.U["bowls"]))]
VENUES = BOWLS
assert len(BOWLS) == 6, [b["name"] for b in BOWLS]


# ---------------------------------------------------------------------------
# Dan's 2037 ruling, replacing the 2035 nearest-unused-bowl rule for the neutral
# rounds: the six bowls rotate on a PUBLISHED schedule -- four to the quarterfinals,
# two to the semifinals -- so the sites are knowable years ahead and no bowl is a
# semifinal site more often than every three seasons.
#
# Two semifinal slots into six bowls is exactly a three-season cycle, which is why six
# is the number the rule wants. The arithmetic also forces a consequence worth stating:
# exact three-season periodicity with two slots partitions the six into three fixed
# pairs, so the semifinal bowls always come as the same partners.
#
# Anchored on 2038 (season 13), the first season played under the ruling. 2037 and
# earlier stay as played, on the old rule.
# ---------------------------------------------------------------------------
ROTATION_FROM = 13          # season 13 == 2038
SEMI_PAIRS_FROM = 18        # season 18 == 2043: semifinal pairs fixed (Dan, 2042)
# 2043 Redwood-501, 2044 Lumber-Star, 2045 Copper-Steam, then repeating. Chosen so that no
# semifinal city collides with an awarded national-title city (2044 is Coachville, the
# Steam Bowl's city, so Copper-Steam cannot be 2044) and no bowl repeats inside two seasons.
SEMI_PAIR_ROLL = ["Redwood Bowl", "501 Bowl", "Lumber Bowl", "Star Bowl", "Copper Bowl", "Steam Bowl"]


def semi_title_overlap(season):
    """The semifinal bowl cities that are also this season's awarded title city (empty = fine)."""
    try:
        tc = champ_venue(season)["city"]
    except SystemExit:
        return None          # no title site awarded yet
    return [b["name"] for b in bowl_rotation(season)["semis"] if b["city"] == tc]


def title_site_check(season, city):
    """Rule (Dan, 2037, restated 2042): a title game may sit in a rotation bowl's city ONLY in a
    year that bowl hosts a QUARTERFINAL. Returns [] when the city is fine, else the reason."""
    rot = bowl_rotation(season)
    bowl = [b for b in BOWLS if b["city"] == city]
    if not bowl:
        return []                       # not a rotation city: unrestricted
    b = bowl[0]
    if any(x["city"] == city for x in rot["semis"]):
        return ["%s is a %d semifinal site (%s)" % (city, 2025 + season, b["name"])]
    if not any(x["city"] == city for x in rot["quarters"]):
        return ["%s (%s) hosts no quarterfinal in %d" % (city, b["name"], 2025 + season)]
    return []


def bowl_rotation(season):
    """Which bowls host which neutral round in a given season.

    Returns {"semis": [two bowl dicts], "quarters": [four bowl dicts]}. Pure lookup --
    no state, no randomness -- so it answers for any season, past or future.
    """
    by_name = {b["name"]: b for b in BOWLS}
    if season >= SEMI_PAIRS_FROM:
        # Dan, 2042: from 2043 the semifinal bowls always come as one of three fixed
        # pairs -- Copper-Steam, Lumber-Star, Redwood-501 -- cycling every three seasons.
        # 2038-2042 stay as played on the old roll.
        roll = [by_name[n] for n in SEMI_PAIR_ROLL]
        i = (2 * (season - SEMI_PAIRS_FROM)) % len(roll)
        n = len(roll)
    else:
        roll = [by_name[n] for n in (E.U.get("bowl_roll") or list(E.U["bowls"]))]
        n = len(roll)
        i = (2 * (season - ROTATION_FROM)) % n
    semis = [roll[i % n], roll[(i + 1) % n]]
    quarters = [roll[(i + 2 + k) % n] for k in range(4)]
    return {"semis": semis, "quarters": quarters}


def _opp_home(v, opponent):
    """True when the bowl sits in the opponent's own state: a de facto home game for them."""
    return bool(opponent) and v["state"] == GEO[opponent]["state"]


def rotation_venue(season, rnd, high_seed_team, used, opponent=None):
    """The site for one neutral game: the nearest bowl to the higher seed among the ones
    this season's rotation assigns to this round and that are still free.

    `rnd` is "QF" or "SF". Seeding still decides WHICH of the round's bowls a given game
    gets -- the rotation decides which bowls are in play at all.
    """
    pool = bowl_rotation(season)["semis" if rnd == "SF" else "quarters"]
    cands = [v for v in pool if v["city"] not in used] or list(pool)   # cities, see above
    # Dan, 2042: the higher seed will not pick a bowl that is a de facto home game for the
    # opponent (a bowl in the opponent's own state). Only if every free bowl is one does
    # the rule fall back to the plain nearest.
    fair = [v for v in cands if not _opp_home(v, opponent)]
    v = min(fair or cands, key=lambda v: vdist(v, high_seed_team))
    used.add(v["city"])
    return v
def vdist(venue, team):
    """Travel distance from a team's campus to a bowl's host city, on the map.

    Dan, 2042: neutral sites go by SCHOOL distance, not state distance. Until then this
    measured between state label positions, which put e.g. Tasson nearer Lumber than
    Redwood although its campus is nearer Redwood. Falls back to the state label only if
    a campus or city has no placement. Forward-only: games already played keep their sites.
    """
    cc = (E.U.get("city_coords") or {}).get("%s|%s" % (venue["city"], venue["state"]))
    sc = (E.U.get("school_coords") or {}).get(team)
    if cc and sc:
        (x1, y1) = cc["xy"]; (x2, y2) = sc
    else:
        (x1, y1) = COORDS[venue["state"]]; (x2, y2) = COORDS[GEO[team]["state"]]
    return math.hypot(x2-x1, y2-y1)

def assign_venue(high_seed_team, used):
    """Nearest unused bowl to the higher seed (Dan, 2035).

    `used` holds CITIES, not bowl names. Dan renamed three bowls in 2037 and dropped a
    fourth, and history is not rewritten -- so a box score can say "Steampower Bowl"
    for the site the pool now calls the Steam Bowl, and "Lumber Bowl" can mean either
    Burke Bay (defunct) or Port Logan. Names moved; the city did not.
    """
    cands = [v for v in BOWLS if v["city"] not in used]
    if not cands:
        cands = list(BOWLS)
    v = min(cands, key=lambda v: vdist(v, high_seed_team))
    used.add(v["city"])
    return v


def champ_venue(season=None):
    """The national championship site for a season.

    Dan's 2037 ruling: **sites are AWARDED, in five-year blocks. There is no rotation.**
    So this is a lookup in `U["champ_sites"]` and nothing else. A season with no award
    raises, because the alternative is inventing a site and calling it canon.

    What was here before was a reconstruction written after the 2035 container reset:
    a 15-city roll stepping one city per season, fitted to 2035 (Diamond City) and 2036
    (Sarkady). It reproduced those two and NOTHING else. The two oldest stored title
    venues contradict it outright -- 2026 was played at Sarkady where the roll says
    Ediville, and 2027 at Lornaman where the roll says Burke Bay -- and the 2033 Denning
    / 2034 Perth anchor its comment claimed as canon is unverifiable: neither season has
    a venue stored anywhere in the project. Removed, not kept as a fallback.
    """
    sites = E.U.get("champ_sites") or {}
    year = 2025 + season if season is not None else None
    if year is None or year not in sites:
        raise SystemExit(
            "no championship site awarded for %s. Sites are awarded in five-year "
            "blocks (Dan, 2037); add it to U['champ_sites'] before the title game."
            % (year if year else "that season"))
    city, state = sites[year]
    return {"name": city, "city": city, "state": state, "champ": True}


def champ_sites_awarded():
    """Every awarded title-game site, oldest first -- the published schedule."""
    return sorted((E.U.get("champ_sites") or {}).items())


# ---------------- in-season efficiency (SRS-lite) ----------------
def srs(db, cap=24, iters=8):
    """Simple rating system. Subdivision opponents are unrated, so games against
    them are excluded -- otherwise the iteration tries to rate a guest school and
    the committee's whole board fails on a KeyError."""
    _FBS = set(TEAMS)
    margins = collections.defaultdict(list)
    for box in db.values():
        if box["home"] not in _FBS or box["away"] not in _FBS: continue
        m = box["home_score"] - box["away_score"]
        m = max(-cap, min(cap, m))
        margins[box["home"]].append((m - 1.8, box["away"]))   # remove rough HFA
        margins[box["away"]].append((-m + 1.8, box["home"]))
    r = {t: 0.0 for t in TEAMS}
    for _ in range(iters):
        r2 = {}
        for t in TEAMS:
            g = margins.get(t, [])
            r2[t] = (sum(m + r[o] for m, o in g)/len(g)) if g else 0.0
        r = r2
    return r

def committee_rank(state, db):
    """Resume = in-season efficiency + record + quality wins - bad losses + a dash of talent."""
    eff = srs(db)
    prelim = sorted(TEAMS, key=lambda t: -(eff[t] + state["preseason"][t]*0.4))
    tier_rank = {t: i for i, t in enumerate(prelim)}
    scores = {}
    for t in TEAMS:
        r = state["record"][t]
        qw = bl = 0.0
        for wk, gid in state["results"]:
            box = db.get(gid)
            if not box or t not in (box["home"], box["away"]): continue
            won = (box["home"] == t) == (box["home_score"] > box["away_score"])
            opp = box["away"] if box["home"] == t else box["home"]
            if opp not in tier_rank: continue   # subdivision guest: no resume credit either way
            if won and tier_rank[opp] < 30: qw += 0.40
            if (not won) and tier_rank[opp] > 90: bl -= 0.55
        # recency: weight the final 4 games (incl CCG) — how you finish matters
        recent = []
        allg = list(state["results"])
        for gid, box2 in db.items():
            if gid.startswith(f"S{state.get('season',1)}CCG") and t in (box2["home"], box2["away"]):
                recent.append(("CCG", gid))
        team_games = [(wk,gid) for wk,gid in allg if db.get(gid) and t in (db[gid]["home"], db[gid]["away"])]
        team_games = team_games[-4:] + recent
        late = 0.0
        for wk, gid in team_games:
            box2 = db.get(gid)
            if not box2: continue
            won = (box2["home"] == t) == (box2["home_score"] > box2["away_score"])
            margin = (box2["home_score"]-box2["away_score"]) * (1 if box2["home"]==t else -1)
            late += (1.4 if won else -1.2)
            # blowout losses late are especially damning; blowout wins a modest plus
            if margin <= -21: late -= 1.8
            elif margin >= 21: late += 0.6
            # a conference-title-game blowout loss is a season-defining black mark
            if gid.startswith(f"S{state.get('season',1)}CCG") and margin <= -21:
                late -= 2.5
        scores[t] = eff[t]*0.55 + state["preseason"][t]*0.24 + r["W"]*0.55 - r["L"]*0.55 + qw + bl + late*0.9
    ranked = sorted(TEAMS, key=lambda t: -scores[t])
    return ranked, scores, eff

def select_playoff_field(state, db, conf_champs):
    """24-team field: 12 auto (conference champs) + 12 at-large (winning record).
    Committee order seeds; P6 champs get a seeding floor of 12."""
    ranked, scores, eff = committee_rank(state, db)
    champ_set = set(conf_champs.values())
    at_large = [t for t in ranked if t not in champ_set
                and state["record"][t]["W"] > state["record"][t]["L"]][:12]
    field = list(champ_set) + at_large
    field.sort(key=lambda t: ranked.index(t))
    # seeding floor: P6 conference champions never seeded worse than 12
    floor = [t for t in field if t in champ_set and TIERS[CONF[t]] == "P6"]
    seeds = {}
    order = list(field)
    for t in floor:
        idx = order.index(t)
        if idx >= 12:
            order.remove(t)
            order.insert(11, t)
    for i, t in enumerate(order):
        seeds[t] = i + 1
    return order, seeds, ranked, scores

# ---------------- awards (spec 12) ----------------
def _prod_points(pos, s):
    if pos == "QB":
        return s.get("PassYds",0)*0.045 + s.get("PassTD",0)*4.2 - s.get("INT",0)*2.4 \
             + s.get("RushYds",0)*0.09 + s.get("RushTD",0)*5.5
    if pos == "RB":
        return s.get("RushYds",0)*0.105 + s.get("RushTD",0)*6 + s.get("RecYds",0)*0.05 + s.get("RecTD",0)*3
    if pos in ("WR","TE","ATH"):
        return s.get("RecYds",0)*0.10 + s.get("RecTD",0)*6 + s.get("Rec",0)*0.35
    if pos == "DL":
        return s.get("Sacks",0)*6.5 + s.get("Tackles",0)*0.9 + s.get("FumRec",0)*4
    if pos == "LB":
        return s.get("Tackles",0)*1.0 + s.get("Sacks",0)*5 + s.get("INT_def",0)*5 + s.get("DefTD",0)*6
    if pos in ("CB","S"):
        return s.get("INT_def",0)*7.5 + s.get("Tackles",0)*0.55 + s.get("DefTD",0)*7
    if pos == "K":
        return s.get("FGMade",0)*3.2 + (s.get("FGMade",0)/s.get("FGAtt",1) if s.get("FGAtt",0) else 0)*10
    if pos == "P":
        return (s.get("PuntYds",0)/s.get("Punts",1) if s.get("Punts",0) else 0)*1.6
    return 0.0

AWARD_NAMES = {
    "heisman": "The Ryskamp Trophy",   # Player of the Year (renamed from Heisman)
    "dpoy": "Defensive Player of the Year",
    "foy": "Freshman of the Year",
    "coy": "Coach of the Year",
}

def compute_awards(state, n_heisman=5, db_basis=None):
    """Season awards.

    n_heisman widens the player-of-the-year board, which the Ryskamp pool process
    needs: the week-6 TWENTY, the week-10 TEN and the four finalists must each be a
    STRICT SUBSET of the one before it, so the board has to be deep enough to rank
    the whole standing pool rather than just a top five.
    """
    P = {p["pid"]: p for tm in E.ROSTERS.values() for p in tm}
    rows = []
    for pid, s in state["season_stats"].items():
        pl = P.get(pid)
        if not pl: continue
        rows.append((pid, pl, s, _prod_points(pl["pos"], s)))
    def top(filt, n=5):
        c = [r for r in rows if filt(r[1], r[2])]
        c.sort(key=lambda r: -r[3])
        return c[:n]
    heisman = top(lambda pl, s: pl["pos"] in ("QB","RB","WR","TE"), n_heisman)
    dpoy    = top(lambda pl, s: pl["pos"] in ("DL","LB","CB","S"), 5)
    foy     = top(lambda pl, s: pl["cls"] == "Fr", 5)
    # coach of the year: wins over preseason expectation
    exp_rank = sorted(TEAMS, key=lambda t: -state["preseason"][t])
    exp_idx = {t: i for i, t in enumerate(exp_rank)}
    coy = sorted(TEAMS, key=lambda t: -(state["record"][t]["W"] - state["record"][t]["L"]
                                        + exp_idx[t]*0.045))[:5]
    # All-America / All-Rookie by positional slots
    SLOTS = [("QB",1),("RB",2),("WR",3),("TE",1),("DL",3),("LB",3),("CB",2),("S",2),("K",1),("P",1)]
    def team_select(pool):
        first, second, used = [], [], set()
        for pos, n in SLOTS:
            c = [r for r in pool if r[1]["pos"] == pos and r[0] not in used]
            c.sort(key=lambda r: -r[3])
            first += c[:n]; used.update(x[0] for x in c[:n])
            second += c[n:2*n]; used.update(x[0] for x in c[n:2*n])
        return first, second
    aa1, aa2 = team_select(rows)
    rook1, _ = team_select([r for r in rows if r[1]["cls"] == "Fr"])
    return {"heisman": heisman, "dpoy": dpoy, "foy": foy, "coy": coy,
            "aa1": aa1, "aa2": aa2, "all_rookie": rook1}


def finalize_season(state, playoff, save_fn=None, award_state=None):
    """Auto-canonize a completed season: champion, record books, and awards.
    Idempotent — safe to call more than once for the same season. Meant to run at the
    end of the playoff so the user never has to manually 'lock in' a season.

    - state: the season state dict
    - playoff: the playoff dict (must have 'champion' and 'champ_result')
    - save_fn: optional callable to persist state after canonizing
    Returns a summary dict of what was canonized.
    """
    season = state.get("season", 1)
    year = 2025 + season   # S1 = 2026, S2 = 2027, ...
    hist = state.setdefault("history", {})
    champ_hist = hist.setdefault("champ", {})
    book = hist.setdefault("book", {})
    awards_hist = hist.setdefault("awards", {})

    champ = playoff.get("champion")
    runnerup = (playoff.get("champ_result") or {}).get("loser") or playoff.get("runnerup")

    def _bk(t):
        # The rebuilt (2035) history book carries only titles/runnerup, so backfill the
        # other keys on existing entries instead of assuming setdefault shaped them.
        e = book.setdefault(t, {})
        for k in ("titles", "runnerup", "semis", "playoff_app"):
            e.setdefault(k, [])
        return e

    # champion + runner-up
    if champ and year not in champ_hist:
        champ_hist[year] = (champ, runnerup)
        if year not in _bk(champ)["titles"]:
            _bk(champ)["titles"].append(year)
        if runnerup and year not in _bk(runnerup)["runnerup"]:
            _bk(runnerup)["runnerup"].append(year)
        # semifinalists
        for r in playoff.get("sf_results", []):
            l = r.get("loser")
            if l and year not in _bk(l)["semis"]:
                _bk(l)["semis"].append(year)
        # all playoff participants
        for t in (playoff.get("field") or playoff.get("order") or []):
            if year not in _bk(t)["playoff_app"]:
                _bk(t)["playoff_app"].append(year)

    # AWARD BASIS (canon): regular season + conference championship games ONLY --
    # the playoff is excluded. The caller passes the reg+CCG stat aggregate as
    # `award_state`; without one this falls back to the full-season state.
    if year not in awards_hist:
        aw = compute_awards(award_state if award_state is not None else state, n_heisman=40)  # deep enough that every pooled finalist is found (2039 left a None)
        def top1(cat):
            pid, pl, st, score = aw[cat][0]
            return {"pid": pid, "name": pl["name"], "team": pl["team"], "pos": pl["pos"], "cls": pl["cls"]}
        # Dan's 2037 ruling: the Ryskamp comes out of the nomination pools (twenty at
        # week 6, ten at week 10, four finalists), not the open board. When the pools
        # exist for this season, the winner and the finalists are theirs.
        pools = state.get("ryskamp_s%d" % season) or {}
        by_name = {pl["name"]: (pid, pl, st, sc) for pid, pl, st, sc in aw["heisman"]}
        def pooled(name):
            e = by_name.get(name)
            return {"pid": e[0], "name": e[1]["name"], "team": e[1]["team"], "pos": e[1]["pos"], "cls": e[1]["cls"]} if e else None
        rysk = pooled(pools.get("winner")) if pools.get("winner") else None
        awards_hist[year] = {
            "ryskamp": rysk or top1("heisman"),
            "dpoy": top1("dpoy"),
            "foy": top1("foy"),
            "coy": aw["coy"][0] if aw.get("coy") else None,
            "finalists": {
                "ryskamp": ([pooled(n) and {"name": pooled(n)["name"], "team": pooled(n)["team"]} for n in pools["four"]]
                            if pools.get("four") else
                            [{"name": pl["name"], "team": pl["team"]} for _, pl, _, _ in aw["heisman"][:5]]),
                "dpoy": [{"name": pl["name"], "team": pl["team"]} for _, pl, _, _ in aw["dpoy"][:4]],
                "foy": [{"name": pl["name"], "team": pl["team"]} for _, pl, _, _ in aw["foy"][:4]],
            },
        }

    state[f"champion_s{season}"] = champ
    if save_fn:
        save_fn(state)
    return {"year": year, "champion": champ, "runnerup": runnerup,
            "awards": awards_hist.get(year)}
