"""Season schedule generator (spec 9) - geography-aware.
- 14 weeks, 12 games/team (9 conf + 3 non-conf), 2 byes only in weeks 2-13
- User-locked matchups: 33 rivalry-week pairs (wk 14) + 7 fixed-week pairs
- Non-conference partner choice weighted by same-state >> adjacent-state >> distance
- Venue rule: prestige gap >= 22 => big school hosts ~95% (small school hosts ~5% "buy games")
- User rule: a prestigious team's non-conf slate should be all-road-vs-much-smaller <= ~2% of teams
- Conference venue balancing + max 2 consecutive home/road (audited)
"""
import pickle, random, math, itertools, collections

with open('/home/claude/cfb2/state/universe.pkl','rb') as f:
    U = pickle.load(f)
TEAMS = U["teams"]; CONF = U["team_conf"]; PRESTIGE = U["prestige"]
GEO = U["geo"]; COORDS = U["state_coords"]; ADJ = U["state_adj"]
FIXED = U["fixed_pairs"]
try:
    with open('/home/claude/cfb2/state/hh_pref_s2.pkl','rb') as f: HH_PREF = pickle.load(f)
except Exception: HH_PREF = {}

def state(t): return GEO[t]["state"]
def dist(t1, t2):
    (x1,y1),(x2,y2) = COORDS[state(t1)], COORDS[state(t2)]
    return math.hypot(x2-x1, y2-y1)
def adjacent(t1, t2):
    return state(t2) in ADJ[state(t1)] or state(t1) == state(t2)

RIVAL_PAIRS = {frozenset((p["team_a"], p["team_b"])) for p in FIXED}
FIXED_WEEK = {}   # frozenset pair -> week
for p in FIXED:
    FIXED_WEEK[frozenset((p["team_a"], p["team_b"]))] = 14 if p["type"] == "Rivalry Week" else p["week"]

def build_conf_opponents(rng):
    """Per conference: each team gets 9 conf opponents. Complement graph = (n-10)-regular,
    built from perfect matchings that avoid locked rivalry pairs."""
    conf_opp = collections.defaultdict(set)
    for conf, tl in U["conferences"].items():
        n = len(tl); comp_deg = n - 10
        if comp_deg == 0:
            for a, b in itertools.combinations(tl, 2):
                conf_opp[a].add(b); conf_opp[b].add(a)
            continue
        for attempt in range(4000):
            comp = collections.defaultdict(set); ok = True
            for _ in range(comp_deg):
                pool = tl[:]; rng.shuffle(pool)
                matched = {}
                for _try in range(600):
                    rng.shuffle(pool)
                    matched = {}; used = set(); fail = False
                    for i in range(0, n, 2):
                        pass
                    # simple pairing: pair pool[0] with a compatible partner, recurse greedily
                    stack = [t for t in pool]
                    pairs = []
                    while stack:
                        a = stack.pop(0)
                        cands = [b for b in stack if b not in comp[a]
                                 and frozenset((a,b)) not in RIVAL_PAIRS]
                        if not cands: fail = True; break
                        b = rng.choice(cands); stack.remove(b); pairs.append((a,b))
                    if not fail: break
                if fail: ok = False; break
                for a, b in pairs:
                    comp[a].add(b); comp[b].add(a)
            if ok:
                full = {t: set(tl) - {t} - comp[t] for t in tl}
                if all(len(v) == 9 for v in full.values()):
                    for t in tl: conf_opp[t] = full[t]
                    break
        else:
            raise RuntimeError(f"conf opponents failed for {conf}")
    return conf_opp

CROSS_DIST = 200   # "across the country" threshold on the map (max pairwise ~450)

def build_nonconf(rng, conf_opp):
    """3 non-conf opponents per team.
    - HARD: never a 3rd opponent from one conference; a 2nd is rare (heavy penalty)
    - ~40% of ALL teams get a same-state non-conf game (pre-planned pairs)
    - Cross-country: ~20% of teams 0 long-haul games, ~60% one, ~20% two
    - Remaining slots geography-weighted."""
    import collections as _c
    CROSS = 250.0
    need0 = {t: 3 for t in TEAMS}
    partners0 = {t: set() for t in TEAMS}
    games0 = []
    for fp, wk in FIXED_WEEK.items():
        a, b = tuple(fp)
        if CONF[a] != CONF[b]:
            partners0[a].add(b); partners0[b].add(a)
            need0[a] -= 1; need0[b] -= 1
            games0.append((a, b))

    # ---- pre-plan same-state pairs to hit ~40% of teams ----
    TARGET_TEAMS = round(0.40 * len(TEAMS))          # ~61 teams
    covered0 = set()
    for a, b in games0:
        if state(a) == state(b): covered0.update((a, b))
    by_state = _c.defaultdict(list)
    for t in TEAMS: by_state[state(t)].append(t)

    for attempt in range(8000):
        need = dict(need0)
        partners = {t: set(partners0[t]) for t in TEAMS}
        games = list(games0)
        confct = {t: _c.Counter() for t in TEAMS}
        farct = {t: 0 for t in TEAMS}
        for a, b in games0:
            confct[a][CONF[b]] += 1; confct[b][CONF[a]] += 1
            if dist(a, b) > CROSS: farct[a] += 1; farct[b] += 1
        covered = set(covered0)

        # phase 1: planned same-state pairings
        states_order = sorted(by_state.keys()); rng.shuffle(states_order)
        for st in states_order:
            if len(covered) >= TARGET_TEAMS: break
            tl = by_state[st][:]; rng.shuffle(tl)
            for t in tl:
                if len(covered) >= TARGET_TEAMS: break
                if t in covered or need[t] <= 0: continue
                cands = [o for o in tl if o != t and o not in covered and need[o] > 0
                         and CONF[o] != CONF[t] and o not in partners[t]
                         and confct[t][CONF[o]] < 2 and confct[o][CONF[t]] < 2]
                if not cands: continue
                o = rng.choice(cands)
                partners[t].add(o); partners[o].add(t)
                confct[t][CONF[o]] += 1; confct[o][CONF[t]] += 1
                need[t] -= 1; need[o] -= 1
                games.append((t, o)); covered.update((t, o))

        # phase 2: fill remaining slots
        # SAME-STATE PRE-PAIRING: target ~40% of all teams with a same-state NC game
        ss_have = set()
        for a, b in games:
            if state(a) == state(b): ss_have.add(a); ss_have.add(b)
        ss_target = 46   # pre-phase floor; organic matching adds the rest (tuned to land ~40%)
        elig = []
        for t in TEAMS:
            for o in TEAMS:
                if o <= t or state(o) != state(t) or CONF[o] == CONF[t]: continue
                elig.append((t, o))
        rng.shuffle(elig)
        for t, o in elig:
            if len(ss_have) >= ss_target: break
            if need[t] <= 0 or need[o] <= 0: continue
            if o in partners[t]: continue
            if confct[t][CONF[o]] >= 2 or confct[o][CONF[t]] >= 2: continue
            if t in ss_have and o in ss_have: continue
            partners[t].add(o); partners[o].add(t)
            confct[t][CONF[o]] += 1; confct[o][CONF[t]] += 1
            if dist(t, o) > CROSS: farct[t] += 1; farct[o] += 1
            need[t] -= 1; need[o] -= 1
            games.append((t, o))
            ss_have.add(t); ss_have.add(o)
        fail = False
        pool_order = list(TEAMS); rng.shuffle(pool_order)
        for t in sorted(pool_order, key=lambda x: -need[x]):
            while need[t] > 0:
                cands = [o for o in TEAMS if o != t and need[o] > 0 and CONF[o] != CONF[t]
                         and o not in partners[t]
                         and confct[t][CONF[o]] < 2 and confct[o][CONF[t]] < 2]
                if not cands: fail = True; break
                w = []
                for o in cands:
                    d = dist(t, o)
                    if d > CROSS:
                        if farct[t] == 0 and farct[o] <= 1: base = 11.0
                        elif farct[t] == 1 and farct[o] <= 1: base = 0.45
                        else: base = 0.05
                    else:
                        base = 1.0
                        if state(o) == state(t): base *= 0.55
                        elif adjacent(t, o):     base *= 6.0
                        base *= 1.0 / (1.0 + d/90.0)
                    if confct[t][CONF[o]] == 1 or confct[o][CONF[t]] == 1:
                        base *= 0.04
                    w.append(max(base, 1e-6))
                o = rng.choices(cands, weights=w)[0]
                partners[t].add(o); partners[o].add(t)
                confct[t][CONF[o]] += 1; confct[o][CONF[t]] += 1
                if dist(t, o) > CROSS: farct[t] += 1; farct[o] += 1
                need[t] -= 1; need[o] -= 1
                games.append((t, o))
            if fail: break
        if not fail and all(v == 0 for v in need.values()):
            return games
    raise RuntimeError("nonconf matching failed")

def assign_venues(rng, conf_opp, nonconf_games):
    """(home, away, is_conf). Adds: home-and-home flips (sparingly) for non-conf,
    and CONFERENCE home games constrained to exactly 4 or 5 per team."""
    home_ct = collections.Counter()       # total home
    conf_home = collections.Counter()     # conference-only home
    games = []
    # ---- non-conf venues (prestige buy-game rule + home-and-home flips) ----
    bigsmall_idx = [k for k,(a,b) in enumerate(nonconf_games) if abs(PRESTIGE[a]-PRESTIGE[b]) >= 22]
    n_buy = max(1, round(0.05*len(bigsmall_idx)))
    buy_set = set(rng.sample(bigsmall_idx, n_buy))
    hh_used = 0
    for k, (a, b) in enumerate(nonconf_games):
        pair = frozenset((a, b))
        gap = PRESTIGE[a] - PRESTIGE[b]
        # home-and-home flip takes priority when eligible AND it doesn't fight the buy rule.
        if pair in HH_PREF and abs(gap) < 22 and rng.random() < 0.55:
            home = HH_PREF[pair]; away = b if home == a else a
            hh_used += 1
        elif abs(gap) >= 22:
            big, small = (a, b) if gap > 0 else (b, a)
            if k in buy_set: home, away = small, big
            else:            home, away = big, small
        else:
            if home_ct[a] < home_ct[b]: home, away = a, b
            elif home_ct[b] < home_ct[a]: home, away = b, a
            else: home, away = (a, b) if rng.random() < 0.5 else (b, a)
        home_ct[home] += 1
        games.append((home, away, False))
    # ---- conference venues: each team hosts exactly 4 or 5 intra-conf games ----
    conf_pairs = set()
    for t, opps in conf_opp.items():
        for o in opps: conf_pairs.add(frozenset((t, o)))
    by_conf_pairs = collections.defaultdict(list)
    for fp in conf_pairs:
        a, b = tuple(fp)
        if CONF[a] == CONF[b]:
            by_conf_pairs[CONF[a]].append((a, b))
    for conf, pairs in by_conf_pairs.items():
        teams = sorted({t for p in pairs for t in p})
        n = len(teams); G = len(pairs)
        fives = max(0, min(n, G - 4*n))
        tteams = teams[:]; rng.shuffle(tteams)
        targets = {t: (5 if i < fives else 4) for i, t in enumerate(tteams)}
        home_map = _orient_conf(pairs, teams, targets, rng)
        for i, (u, v) in enumerate(pairs):
            host = home_map[i]; away = v if host == u else u
            conf_home[host] += 1; home_ct[host] += 1
            games.append((host, away, True))
    return games

def _orient_conf(pairs, teams, targets, rng, tries=400):
    """Degree-constrained orientation: each team hosts exactly targets[t] games.
    Feasible because sum(targets)==len(pairs). Greedy 'host = greater relative need'."""
    for _ in range(tries):
        remaining = {t: targets[t] for t in teams}
        deg_left = collections.Counter()
        for (u, v) in pairs: deg_left[u] += 1; deg_left[v] += 1
        home = {}
        order = list(range(len(pairs))); rng.shuffle(order)
        for i in order:
            u, v = pairs[i]
            if remaining[u] <= 0: host = v
            elif remaining[v] <= 0: host = u
            else:
                uu = remaining[u]/max(1, deg_left[u]); vv = remaining[v]/max(1, deg_left[v])
                if uu > vv: host = u
                elif vv > uu: host = v
                else: host = u if rng.random() < 0.5 else v
            home[i] = host; remaining[host] -= 1
            deg_left[u] -= 1; deg_left[v] -= 1
        hc = collections.Counter(home.values())
        if all(hc[t] == targets[t] for t in teams):
            return home
    # fallback: return best effort (should never hit for feasible inputs)
    return home

def assign_weeks(rng, games):
    """Weeks 1-14; every team plays wk1 and wk14 (byes only 2-13); fixed pairs pinned;
    non-conf front-loaded into weeks 1-5."""
    gkey = {}
    for i, (h, a, ic) in enumerate(games): gkey[i] = frozenset((h, a))
    week_of = {}
    busy = collections.defaultdict(set)     # week -> set(teams)
    gcount = collections.defaultdict(int)   # team -> games assigned

    def pin(i, wk):
        h, a, ic = games[i]
        week_of[i] = wk; busy[wk].add(h); busy[wk].add(a)
        gcount[h] += 1; gcount[a] += 1

    # 1) fixed pairs
    for i, (h, a, ic) in enumerate(games):
        fp = frozenset((h, a))
        if fp in FIXED_WEEK: pin(i, FIXED_WEEK[fp])
    # 2) week 14 coverage for everyone else via maximum matching
    import networkx as nx
    remaining = set(t for t in TEAMS if t not in busy[14])
    unassigned = [i for i in range(len(games)) if i not in week_of]
    G = nx.Graph()
    G.add_nodes_from(sorted(remaining))
    for i in unassigned:
        h, a, ic = games[i]
        if h in remaining and a in remaining:
            G.add_edge(h, a, gi=i, weight=(2.0 if ic else 1.0) + rng.random()*0.1)
    M = nx.max_weight_matching(G, maxcardinality=True)
    if 2*len(M) < len(remaining):
        return None
    for h, a in M:
        pin(G[h][a]["gi"], 14)
    # 3) week 1 coverage via maximum matching (non-conf weighted up for front-load)
    remaining1 = set(t for t in TEAMS if t not in busy[1])
    unassigned = [i for i in range(len(games)) if i not in week_of]
    G1 = nx.Graph()
    G1.add_nodes_from(sorted(remaining1))
    for i in unassigned:
        h, a, ic = games[i]
        if h in remaining1 and a in remaining1:
            G1.add_edge(h, a, gi=i, weight=(2.0 if not ic else 1.0) + rng.random()*0.1)
    M1 = nx.max_weight_matching(G1, maxcardinality=True)
    if 2*len(M1) < len(remaining1):
        return None
    for h, a in M1:
        pin(G1[h][a]["gi"], 1)
    # 4) the rest into weeks 2-13; non-conf tries 2-5 first
    unassigned = [i for i in range(len(games)) if i not in week_of]
    unassigned.sort(key=lambda i: (games[i][2], rng.random()))   # non-conf first
    for i in unassigned:
        h, a, ic = games[i]
        pref = ([2,3,4,5] if not ic else []) + list(range(2, 14))
        placed = False
        for wk in pref:
            if h not in busy[wk] and a not in busy[wk]:
                pin(i, wk); placed = True; break
        if not placed:
            return None
    return week_of

def enforce_run_length(games, week_of, rng=None, iters=500000):
    """Two-move local search with cached per-team costs.
    Cost = balance violations*4 + (3+ H/A run events)*3 + 0.5*non-conf outside wks 1-5."""
    import random as _r
    rng = rng or _r.Random(99)
    games = [list(g) for g in games]
    week_of = dict(week_of)
    busy = {}
    for i, wk in week_of.items():
        busy.setdefault(wk, set()).update((games[i][0], games[i][1]))
    team_games = {t: [] for t in TEAMS}
    for i in range(len(games)):
        team_games[games[i][0]].append(i)
        team_games[games[i][1]].append(i)

    def team_cost(t):
        gs = sorted(team_games[t], key=lambda i: week_of[i])
        homes = 0; last = None; cur = 0; maxrun = 0
        for i in gs:
            ha = "H" if games[i][0] == t else "A"
            if ha == "H": homes += 1
            cur = cur + 1 if ha == last else 1
            last = ha; maxrun = max(maxrun, cur)
        # escalating run penalty drives the search hard toward a worst-run of <=2
        run_pen = (maxrun - 2) ** 2 * 8.0 if maxrun >= 3 else 0.0
        wks = set(week_of[i] for i in gs)
        byes = sorted(w for w in range(2, 14) if w not in wks)
        bye_pen = 0.0
        if len(byes) == 2:
            if byes[1] - byes[0] == 1: bye_pen += 12.0                # back-to-back: near-forbidden
            if (byes[0] <= 7) == (byes[1] <= 7): bye_pen += 3.2       # prefer one bye per half
        return max(0, abs(homes - 6) - 1) * 2 + run_pen + bye_pen

    tc = {t: team_cost(t) for t in TEAMS}
    bad = set(t for t in TEAMS if tc[t] > 0)
    nc_pen = 0.5 * sum(1 for i in range(len(games)) if not games[i][2] and week_of[i] > 5)
    cost = sum(tc.values()) + nc_pen
    best_cost = cost; best = ([g[:] for g in games], dict(week_of))

    fixed_set = set(i for i in range(len(games)) if frozenset((games[i][0], games[i][1])) in FIXED_WEEK)
    flip_ok = set(i for i in range(len(games)) if i not in fixed_set
                  and not games[i][2]   # never flip conference venues (preserve 4/5 conf-home)
                  and abs(PRESTIGE[games[i][0]]-PRESTIGE[games[i][1]]) < 22)
    flippable = sorted(flip_ok)

    def refresh(ts):
        nonlocal cost
        for t in ts:
            old = tc[t]; new = team_cost(t)
            tc[t] = new; cost += new - old
            if new > 0: bad.add(t)
            else: bad.discard(t)

    bad_list_cache = None
    for it in range(iters):
        if best_cost <= 0: break
        use_bad = bad and rng.random() < 0.85
        if rng.random() < 0.5:
            if use_bad:
                tt = rng.choice(sorted(bad))
                cand = [x for x in team_games[tt] if x in flip_ok]
                if not cand: continue
                i = rng.choice(cand)
            else:
                i = rng.choice(flippable)
            h, a, _ = games[i]
            games[i][0], games[i][1] = games[i][1], games[i][0]
            old = tc[h] + tc[a]
            nh, na = team_cost(h), team_cost(a)
            if nh + na > old and rng.random() > 0.06:
                games[i][0], games[i][1] = games[i][1], games[i][0]
            else:
                refresh([h, a])
        else:
            t = rng.choice(sorted(bad)) if use_bad else rng.choice(TEAMS)
            gs = [i for i in team_games[t] if i not in fixed_set and 2 <= week_of[i] <= 13]
            if len(gs) < 2: continue
            i, j = rng.sample(gs, 2)
            wi, wj = week_of[i], week_of[j]
            if wi == wj: continue
            oi = games[i][0] if games[i][1] == t else games[i][1]
            oj = games[j][0] if games[j][1] == t else games[j][1]
            if oi in busy[wj] or oj in busy[wi]: continue
            # bucket guard: non-conf never leaves weeks 1-5
            if (not games[i][2] and wi <= 5 and wj > 5) or (not games[j][2] and wj <= 5 and wi > 5):
                continue
            dnc = 0.0
            for gi, wfrom, wto in ((i, wi, wj), (j, wj, wi)):
                if not games[gi][2]:
                    dnc += 0.5 * ((1 if wto > 5 else 0) - (1 if wfrom > 5 else 0))
            affected = [t, oi, oj]
            old = sum(tc[x] for x in affected)
            busy[wi].discard(oi); busy[wj].add(oi)
            busy[wj].discard(oj); busy[wi].add(oj)
            week_of[i], week_of[j] = wj, wi
            new = sum(team_cost(x) for x in affected)
            if new + dnc > old and rng.random() > 0.06:
                week_of[i], week_of[j] = wi, wj
                busy[wj].discard(oi); busy[wi].add(oi)
                busy[wi].discard(oj); busy[wj].add(oj)
            else:
                nc_pen += dnc; cost += dnc
                refresh(affected)
        if cost < best_cost:
            best_cost = cost; best = ([g[:] for g in games], dict(week_of))

    games, week_of = best
    tg2 = {t: [] for t in TEAMS}
    for i in range(len(games)):
        tg2[games[i][0]].append(i); tg2[games[i][1]].append(i)
    def max_run(t):
        gs = sorted(tg2[t], key=lambda i: week_of[i])
        b = cur = 0; last = None
        for i in gs:
            ha = "H" if games[i][0] == t else "A"
            cur = cur + 1 if ha == last else 1
            last = ha; b = max(b, cur)
        return b
    worst = max(max_run(t) for t in TEAMS)
    return [tuple(g) for g in games], week_of, worst

def final_polish(games, week_of):
    """(1) pull non-conf games forward into weeks 2-5 when both teams are free;
    (2) surgical repair of remaining 3+ runs via venue flips and single-game relocation."""
    games = [list(g) for g in games]
    week_of = dict(week_of)
    busy = {}
    for i, wk in week_of.items():
        busy.setdefault(wk, set()).update((games[i][0], games[i][1]))
    team_games = {t: [] for t in TEAMS}
    for i in range(len(games)):
        team_games[games[i][0]].append(i); team_games[games[i][1]].append(i)
    fixed_set = set(i for i in range(len(games)) if frozenset((games[i][0], games[i][1])) in FIXED_WEEK)
    flip_ok = set(i for i in range(len(games)) if i not in fixed_set
                  and not games[i][2]   # never flip conference venues (preserve 4/5 conf-home)
                  and abs(PRESTIGE[games[i][0]]-PRESTIGE[games[i][1]]) < 22)

    def relocate(i, wk_new):
        wk_old = week_of[i]
        h, a, _ = games[i]
        busy[wk_old].discard(h); busy[wk_old].discard(a)
        busy.setdefault(wk_new, set()).update((h, a))
        week_of[i] = wk_new

    def team_cost(t):
        gs = sorted(team_games[t], key=lambda i: week_of[i])
        homes = 0; last = None; cur = 0; maxrun = 0
        for i in gs:
            ha = "H" if games[i][0] == t else "A"
            if ha == "H": homes += 1
            cur = cur + 1 if ha == last else 1
            last = ha; maxrun = max(maxrun, cur)
        # escalating run penalty drives the search hard toward a worst-run of <=2
        run_pen = (maxrun - 2) ** 2 * 8.0 if maxrun >= 3 else 0.0
        wks = set(week_of[i] for i in gs)
        byes = sorted(w for w in range(2, 14) if w not in wks)
        bye_pen = 0.0
        if len(byes) == 2:
            if byes[1] - byes[0] == 1: bye_pen += 12.0                # back-to-back: near-forbidden
            if (byes[0] <= 7) == (byes[1] <= 7): bye_pen += 3.2       # prefer one bye per half
        return max(0, abs(homes - 6) - 1) * 2 + run_pen + bye_pen

    # (1) pull non-conf forward
    for i in range(len(games)):
        if games[i][2] or i in fixed_set or week_of[i] <= 5 or week_of[i] == 14: continue
        h, a, _ = games[i]
        for wk in (2, 3, 4, 5):
            if h not in busy[wk] and a not in busy[wk]:
                before = team_cost(h) + team_cost(a)
                old_wk = week_of[i]
                relocate(i, wk)
                if team_cost(h) + team_cost(a) > before:
                    relocate(i, old_wk)
                else:
                    break

    # (2) surgical repair to fixpoint
    for sweep in range(30):
        violators = [t for t in TEAMS if team_cost(t) > 0]
        if not violators: break
        progress = False
        for t in violators:
            fixed_it = False
            # try venue flips
            for i in team_games[t]:
                if i not in flip_ok: continue
                h, a, _ = games[i]
                before = team_cost(h) + team_cost(a)
                games[i][0], games[i][1] = games[i][1], games[i][0]
                if team_cost(h) + team_cost(a) < before:
                    fixed_it = True; break
                games[i][0], games[i][1] = games[i][1], games[i][0]
            if fixed_it: progress = True; continue
            # try relocating any of its movable games to any free week 2-13
            for i in team_games[t]:
                if i in fixed_set or not (2 <= week_of[i] <= 13): continue
                h, a, _ = games[i]
                before = team_cost(h) + team_cost(a)
                old_wk = week_of[i]
                for wk in range(2, 14):
                    if wk == old_wk: continue
                    if h in busy[wk] or a in busy[wk]: continue
                    if not games[i][2] and old_wk <= 5 and wk > 5: continue
                    relocate(i, wk)
                    penal = 0.5 if (not games[i][2] and wk > 5 and old_wk <= 5) else 0.0
                    if team_cost(h) + team_cost(a) + penal < before:
                        fixed_it = True; break
                    relocate(i, old_wk)
                if fixed_it: break
            if fixed_it: progress = True
        if not progress: break
    return [tuple(g) for g in games], week_of

def _run_reduce_neutral(games, week_of, rng, rounds=6):
    """Reduce H/A runs using ONLY moves that preserve every team's conf-home count:
    (a) flipping a non-conference game's venue (doesn't touch conf-home at all); and
    (b) week-swaps of two of a team's games (venue untouched, so conf-home is invariant).
    Never flips a lone conference venue (that would change conf-home).

    Uses a global run-penalty objective with simulated-annealing acceptance so the search
    can take lateral moves and escape the local optima that a strictly-greedy reducer hits
    (which is why last season stalled at a worst run of 6)."""
    games = [list(g) for g in games]
    week_of = dict(week_of)
    tg = collections.defaultdict(list)
    for i,(h,a,ic) in enumerate(games):
        tg[h].append(i); tg[a].append(i)
    fixed_set = set(i for i in range(len(games)) if frozenset((games[i][0],games[i][1])) in FIXED_WEEK)
    busy = {}
    for i, wk in week_of.items():
        busy.setdefault(wk, set()).update((games[i][0], games[i][1]))
    def runs(t):
        s=["H" if games[i][0]==t else "A" for i in sorted(tg[t], key=lambda x: week_of[x])]
        b=cur=0; last=None
        for x in s:
            cur=cur+1 if x==last else 1; last=x; b=max(b,cur)
        return b
    def byes_of(t):
        wks = sorted(week_of[i] for i in tg[t])
        return [w for w in range(1,15) if w not in wks]
    PREST = U["prestige"]
    def team_pen(t):
        r = runs(t)
        pen = 0 if r <= 2 else (r-2)**3 * 6   # run-length is the priority objective
        # back-to-back byes are near-forbidden
        bl = byes_of(t)
        if len(bl) == 2 and bl[1]-bl[0] == 1:
            pen += 30
        return pen
    def host_pen(i):
        # discourage a much-smaller school hosting a much-bigger one in non-conf
        if games[i][2]:
            return 0
        h,a = games[i][0], games[i][1]
        if PREST[a] - PREST[h] >= 22:   # away team much bigger than host
            return 4
        return 0
    def global_pen():
        return sum(team_pen(t) for t in TEAMS) + sum(host_pen(i) for i in range(len(games)) if not games[i][2])

    cur_pen = global_pen()
    # annealing schedule (sized to complete within the build time budget)
    total_iters = rounds * 900
    for it in range(total_iters):
        if cur_pen == 0: break
        T = max(0.02, 2.5 * (1 - it/total_iters))   # cooling
        # pick a team weighted toward the worst offenders
        cand_teams = [t for t in TEAMS if runs(t) > 2]
        if not cand_teams: break
        t = rng.choice(cand_teams)
        affected = set([t])
        move = None
        if rng.random() < 0.5:
            # (a) non-conf venue flip
            opts = [i for i in tg[t] if i not in fixed_set and not games[i][2]]
            if opts:
                i = rng.choice(opts)
                o = games[i][1] if games[i][0]==t else games[i][0]
                affected.add(o)
                before = sum(team_pen(x) for x in affected) + host_pen(i)
                games[i][0], games[i][1] = games[i][1], games[i][0]
                after = sum(team_pen(x) for x in affected) + host_pen(i)
                delta = after - before
                if delta <= 0 or rng.random() < pow(2.718, -delta/T):
                    cur_pen += delta; move = "flip"
                else:
                    games[i][0], games[i][1] = games[i][1], games[i][0]  # revert
        else:
            # (b) week swap of two of t's games
            gs = [i for i in tg[t] if i not in fixed_set and 2 <= week_of[i] <= 13]
            if len(gs) >= 2:
                i, j = rng.sample(gs, 2)
                wi, wj = week_of[i], week_of[j]
                if wi != wj:
                    oi = games[i][1] if games[i][0]==t else games[i][0]
                    oj = games[j][1] if games[j][0]==t else games[j][0]
                    if oi not in busy[wj] and oj not in busy[wi]:
                        affected.update([oi, oj])
                        before = sum(team_pen(x) for x in affected)
                        busy[wi].discard(oi); busy[wj].add(oi)
                        busy[wj].discard(oj); busy[wi].add(oj)
                        week_of[i], week_of[j] = wj, wi
                        after = sum(team_pen(x) for x in affected)
                        delta = after - before
                        if delta <= 0 or rng.random() < pow(2.718, -delta/T):
                            cur_pen += delta; move = "swap"
                        else:
                            week_of[i], week_of[j] = wi, wj
                            busy[wj].discard(oi); busy[wi].add(oi)
                            busy[wi].discard(oj); busy[wj].add(oj)
    return [tuple(g) for g in games], week_of

def build_schedule(master_seed=550001):
    rng = random.Random(master_seed)
    conf_opp = build_conf_opponents(rng)
    for attempt in range(300):
        nonconf = build_nonconf(rng, conf_opp)
        games = assign_venues(rng, conf_opp, nonconf)
        week_of = assign_weeks(rng, games)
        if week_of is not None:
            import random as _r2
            games, week_of, worst_run = enforce_run_length(games, week_of, rng=_r2.Random(99))
            if worst_run > 2:
                games, week_of, worst_run = enforce_run_length(games, week_of, rng=_r2.Random(1234))
            if worst_run > 2:
                games, week_of, worst_run = enforce_run_length(games, week_of, rng=_r2.Random(777))
            if worst_run > 2:
                games, week_of, worst_run = enforce_run_length(games, week_of, rng=_r2.Random(31337))
            for _pr in range(4):
                games, week_of = final_polish(games, week_of)
            # conf-home-NEUTRAL run reducer (non-conf flips + venue-preserving week swaps).
            # Interleave with polish; verify conf-home is untouched afterward.
            import random as _r3
            for _rn in range(3):
                games, week_of = _run_reduce_neutral(games, week_of, _r3.Random(4242+_rn), rounds=60)
                games, week_of = final_polish(games, week_of)
            tg = {}
            for gi in range(len(games)):
                tg.setdefault(games[gi][0], []).append(gi); tg.setdefault(games[gi][1], []).append(gi)
            def _mr(t):
                gs = sorted(tg[t], key=lambda x: week_of[x]); b=cur=0; last=None
                for x in gs:
                    ha = "H" if games[x][0]==t else "A"
                    cur = cur+1 if ha==last else 1
                    last=ha; b=max(b,cur)
                return b
            worst_run = max(_mr(t) for t in TEAMS)
            sched = [(week_of[i], games[i][0], games[i][1], games[i][2]) for i in range(len(games))]
            sched.sort()
            import pickle as _pk
            _pk.dump((sched, worst_run), open('/home/claude/cfb2/state/schedule_s3_cache.pkl','wb'))
            return sched, worst_run
    raise RuntimeError("schedule build failed")


def audit(sched, worst_run):
    print("=== SCHEDULE AUDIT ===")
    per = collections.defaultdict(list)
    for wk, h, a, ic in sched:
        per[h].append((wk, "H", ic, a)); per[a].append((wk, "A", ic, h))
    ok12 = all(len(v) == 12 for v in per.values())
    ok_conf = all(sum(1 for x in v if x[2]) == 9 for v in per.values())
    weeks_ok = True; byes_ok = True
    for t, v in per.items():
        wks = sorted(x[0] for x in v)
        if len(set(wks)) != 12: weeks_ok = False
        if 1 not in wks or 14 not in wks: byes_ok = False
    fixed_ok = True
    placed = {frozenset((h, a)): wk for wk, h, a, ic in sched}
    for fp, wk in FIXED_WEEK.items():
        if placed.get(fp) != wk:
            fixed_ok = False; print("  FIXED MISS:", tuple(fp), "wanted", wk, "got", placed.get(fp))
    print(f"12 games each: {ok12} | 9 conf + 3 non-conf: {ok_conf} | no double-book: {weeks_ok} | byes only wks 2-13: {byes_ok}")
    print(f"all 40 locked matchups in correct weeks: {fixed_ok}")
    # NEW: conference home games must be exactly 4 or 5 per team
    conf_home_ct = collections.Counter()
    for wk, h, a, ic in sched:
        if ic: conf_home_ct[h] += 1
    ch_vals = [conf_home_ct[t] for t in TEAMS]
    ch_ok = all(4 <= c <= 5 for c in ch_vals)
    ch_dist = collections.Counter(ch_vals)
    print(f"CONF HOME GAMES in {{4,5}} for ALL teams: {ch_ok}  (distribution: {dict(sorted(ch_dist.items()))})")
    if not ch_ok:
        offenders = [(t, conf_home_ct[t]) for t in TEAMS if not (4 <= conf_home_ct[t] <= 5)]
        print("   OFFENDERS:", offenders[:10])
    # NEW: home-and-home flips honored vs Season 1
    try:
        with open('/home/claude/cfb2/state/hh_pref_s2.pkl','rb') as f: hhp = pickle.load(f)
    except Exception: hhp = {}
    hh_hit = 0; hh_total_scheduled = 0
    for wk, h, a, ic in sched:
        pair = frozenset((h, a))
        if pair in hhp:
            hh_total_scheduled += 1
            if h == hhp[pair]: hh_hit += 1
    print(f"home-and-home: {hh_hit} S2 games flipped host vs S1 (of {hh_total_scheduled} eligible rematches scheduled)")
    nc = [(wk, h, a) for wk, h, a, ic in sched if not ic]
    n_nc = len(nc)
    front = sum(1 for wk, _, _ in nc if wk <= 5)
    same = sum(1 for _, h, a in nc if state(h) == state(a))
    adj = sum(1 for _, h, a in nc if state(h) != state(a) and adjacent(h, a))
    avg_d = sum(dist(h, a) for _, h, a in nc)/n_nc
    print(f"non-conf: {n_nc} games | in weeks 1-5: {100*front/n_nc:.0f}% | same-state: {100*same/n_nc:.0f}% | adjacent-state: {100*adj/n_nc:.0f}% | avg map dist {avg_d:.0f}px")
    import collections as _c
    nc_opp_conf = _c.defaultdict(list)
    nc_dist = _c.defaultdict(int)
    for _, h, a in nc:
        nc_opp_conf[h].append(CONF[a]); nc_opp_conf[a].append(CONF[h])
        if dist(h, a) >= 240: nc_dist[h] += 1; nc_dist[a] += 1
    max_same = {t: max(_c.Counter(v).values()) for t, v in nc_opp_conf.items()}
    n3 = sum(1 for m in max_same.values() if m >= 3)
    n2 = sum(1 for m in max_same.values() if m == 2)
    d0 = sum(1 for t in TEAMS if nc_dist.get(t,0) == 0)
    d1 = sum(1 for t in TEAMS if nc_dist.get(t,0) == 1)
    d2 = sum(1 for t in TEAMS if nc_dist.get(t,0) >= 2)
    # conference diversity + cross-country audits
    import collections as _c2
    per_nc = _c2.defaultdict(list)
    for _, h, a in nc:
        per_nc[h].append(a); per_nc[a].append(h)
    same3 = sum(1 for t, opps in per_nc.items() if len(set(CONF[o] for o in opps)) == 1 and len(opps) == 3)
    two_same = sum(1 for t, opps in per_nc.items()
                   if any(v == 2 for v in _c2.Counter(CONF[o] for o in opps).values()))
    cross_ct = {t: sum(1 for o in opps if dist(t, o) >= CROSS_DIST) for t, opps in per_nc.items()}
    n_t = len(per_nc)
    cross1 = sum(1 for v in cross_ct.values() if v >= 1)
    cross2 = sum(1 for v in cross_ct.values() if v >= 2)
    cross_games = [(t, o) for t, opps in per_nc.items() for o in opps if dist(t, o) >= CROSS_DIST]
    avg_cd = sum(dist(t, o) for t, o in cross_games)/max(1, len(cross_games))
    bigsmall = [(h, a) for _, h, a in nc if abs(PRESTIGE[h]-PRESTIGE[a]) >= 22]
    small_hosts = sum(1 for h, a in bigsmall if PRESTIGE[h] < PRESTIGE[a])
    print(f"big-vs-small games: {len(bigsmall)} | hosted by small school: {100*small_hosts/max(1,len(bigsmall)):.1f}% (target ~5%)")
    bad_slate = 0; elig = 0
    for t in TEAMS:
        if PRESTIGE[t] < 70: continue
        elig += 1
        mine = [(x[1], x[3]) for x in per[t] if not x[2]]
        if all(ha == "A" and PRESTIGE[t]-PRESTIGE[opp] >= 22 for ha, opp in mine):
            bad_slate += 1
    print(f"prestigious teams (70+) with ALL-ROAD-vs-much-smaller non-conf slates: {bad_slate}/{elig} = {100*bad_slate/max(1,elig):.1f}% (user target ~2%)")
    import collections as _c
    CROSS = 250.0
    conf_mix_bad3 = 0; conf_mix_2 = 0
    long_counts = _c.Counter()
    for t, v in per.items():
        opps = [x[3] for x in v if not x[2]]
        cc = _c.Counter(CONF[o] for o in opps)
        if cc and max(cc.values()) >= 3: conf_mix_bad3 += 1
        elif cc and max(cc.values()) == 2: conf_mix_2 += 1
        long_counts[sum(1 for o in opps if dist(t, o) >= CROSS)] += 1
    ss_teams = set()
    for _, h, a in nc:
        if state(h) == state(a): ss_teams.add(h); ss_teams.add(a)
    byes_by_team = {}
    for t, v in per.items():
        wks = set(x[0] for x in v)
        byes_by_team[t] = sorted(w for w in range(2, 14) if w not in wks)
    b2b = sum(1 for b in byes_by_team.values() if len(b) == 2 and b[1]-b[0] == 1)
    split = sum(1 for b in byes_by_team.values() if len(b) == 2 and (b[0] <= 7) != (b[1] <= 7))
    print(f"same-state NC: {len(ss_teams)} teams ({100*len(ss_teams)/len(TEAMS):.0f}%) have a same-state non-conf game (target ~40%)")
    print(f"byes: back-to-back: {b2b} (target 0) | one-per-half: {split}/{len(TEAMS)} ({100*split/len(TEAMS):.0f}%, exceptions OK)")
    print(f"non-conf conference diversity: teams w/ 3 from same conf: {conf_mix_bad3} (must be 0) | w/ 2 from same conf: {conf_mix_2} ({100*conf_mix_2/152:.0f}%, target rare)")
    print(f"cross-country games per team (>=250px): 0: {long_counts[0]} ({100*long_counts[0]/152:.0f}%) | 1: {long_counts[1]} ({100*long_counts[1]/152:.0f}%) | 2+: {sum(v for k,v in long_counts.items() if k>=2)} ({100*sum(v for k,v in long_counts.items() if k>=2)/152:.0f}%)  [target ~20/60/20]")
    homes = [sum(1 for x in v if x[1]=="H") for v in per.values()]
    print(f"home games per team: min {min(homes)} max {max(homes)} (target 6 +/- 1) | worst H/A run: {worst_run} (target <= 2)")

if __name__ == "__main__":
    sched, worst_run = build_schedule()
    with open('/home/claude/cfb2/state/schedule_s1.pkl','wb') as f:
        pickle.dump(sched, f)
    print(f"schedule built: {len(sched)} games\n")
    audit(sched, worst_run)
