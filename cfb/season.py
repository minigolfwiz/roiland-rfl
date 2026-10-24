"""Season runner (spec 6,7,8): sim windows, persistent state, dynamic HFA, hot seats,
mid-season firings w/ named interims, Top 25, storylines. Double-sim guarded."""
import pickle, os, math, random, collections
import sys; sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E

ST = '/home/claude/cfb2/state/season_state.pkl'
U = E.U; TEAMS = U["teams"]; PRESTIGE = U["prestige"]; CONF = U["team_conf"]

def talent_proxy(team):
    top = sorted((p["abil"] for p in E.ROSTERS[team]), reverse=True)[:30]
    return sum(top)/len(top)

def new_state():
    with open('/home/claude/cfb2/state/schedule_s1.pkl','rb') as f:
        sched = pickle.load(f)
    rngp = random.Random(313131)
    preseason = {}
    for t in TEAMS:
        preseason[t] = talent_proxy(t) + E.COACHES[t]["HC"]["skill"]*0.18 + PRESTIGE[t]*0.012 + rngp.gauss(0, 0.25)
    return {
        "season": 1, "next_week": 1, "sched": sched,
        "record": {t: {"W":0,"L":0,"confW":0,"confL":0,"PF":0,"PA":0} for t in TEAMS},
        "results": [],                        # (wk, game_id)
        "inj_out": {},                        # pid -> weeks remaining
        "inj_recent": {},                     # pid -> weeks since return counter (<=2)
        "inj_log": [],
        "heat": {t: 0.0 for t in TEAMS},      # form for dynamic HFA
        "pressure": {t: 0.0 for t in TEAMS},  # hot seat (expected wins - actual)
        "preseason": preseason,
        "firings": [], "interims": {},        # team -> interim dict
        "streak": {t: 0 for t in TEAMS},      # + = W streak
        "season_stats": collections.defaultdict(dict),
        "weekly_perf": [],                    # storyline feed
    }

def load_state():
    if os.path.exists(ST):
        with open(ST,'rb') as f: s = pickle.load(f)
        for team, it in s.get("interims", {}).items():
            if E.COACHES[team]["HC"]["name"] != it["name"]:
                E.COACHES[team]["HC"] = {"name": it["name"], "skill": max(1.0, it["skill"]-0.4), "tenure": 0}
        return s
    return new_state()

def save_state(s):
    with open(ST,'wb') as f: pickle.dump(s, f)

def _talent(t):
    top = sorted((pl["abil"] for pl in E.ROSTERS[t]), reverse=True)[:22]
    return sum(top)/len(top)

def win_prob(s, home, away, site="home"):
    """Pre-game win probability from the talent gap.

    The coefficient was 1.85, chosen on the assumption that a 1.0 talent gap should mean
    an ~85% win. Measured against 881 canon 2037 games, that over-promised everywhere
    above a coin flip -- favourites it put at 80-90% won 71%, and the miss grew with the
    stated confidence. 1.426 is the maximum-likelihood fit on those games.

    This is a correction to the MODEL, not to the engine. Bucketing the same games by
    end-of-season net rating instead of talent gives 51% / 70% / 79% / 90%, a healthy
    separation curve, so the simulation distinguishes teams properly. The error was that
    `_talent` -- the mean ability of a roster's top 22, position-blind and coaching-blind
    -- correlates only 0.669 with what teams turn out to be. Alternatives were tried
    (positional starters, the engine's own unit strengths, unit strengths plus coaching)
    and all land between 0.65 and 0.70, so roughly half the variance in a season's net
    rating is schedule, form, injury and chance that no pre-game roster measure can see.
    The honest fix is for the model to claim only the confidence it has earned.

    REFIT ATTEMPTED AND DECLINED, 2038 (Dan asked for one after the end-of-season audit).
    The 2038 engine separates teams much better than the 2037 engine the 1.426/1.480 fit
    came from, so by the bucket table the model now UNDER-promises: 80-90% favourites
    won 88.4%, 60-70% favourites won 68.2%. That looks like a stale constant.

    Maximum likelihood on all 879 FBS-vs-FBS games of 2038 says otherwise. The best
    scale on the logit is 1.130 -- it would move this coefficient to 1.673 -- but the
    95% interval on that scale is [0.93, 1.35], which contains 1.0, and the likelihood
    ratio against changing nothing is chi2 = 1.55 on one degree of freedom (p ~ 0.46).
    One season is 879 games; the bucket misses live in the 80-90% and 90%+ buckets,
    which hold 69 and 13 games between them. The pattern is real-looking and not
    statistically distinguishable from noise.

    So the value stays at 1.480 BY DECISION, not by neglect, and it is now verified
    against the current engine rather than inherited from the previous one. Revisit
    after 2039, when the sample under this engine doubles; if the scale still lands
    near 1.13 on ~1,750 games the interval will exclude 1.0 and the refit is real.
    """
    gap = _talent(home) - _talent(away)
    # small nudges from current-season form (heat) and stadium.
    # Subdivision guests carry no season state, so their heat reads as neutral.
    gap += (s["heat"].get(home, 0.0) - s["heat"].get(away, 0.0)) * 0.05
    d = gap * 1.480   # jointly fitted on 881 canon games; was 1.85
    # 0.16 made home field worth far more than it is: home teams won 54.7% of the 881
    # canon games, and the fitted weight is 0.05. Fitting the gap alone left a 7-point
    # bias in the middle buckets that was really the home term over-promising.
    if site == "home": d += dyn_hfa(s, home) * 0.050
    return 1/(1+math.exp(-d))

def dyn_hfa(s, team):
    base = E.COACHES[team]["hfa_base"]
    return max(0.6, min(5.8, base * (1 + 0.10*max(-3, min(3, s["heat"].get(team, 0.0))))))

def pid_team():
    return {p["pid"]: p for tm in E.ROSTERS.values() for p in tm}

def merge_stats(agg, box):
    for pid, st in box["stats"].items():
        if pid not in agg:
            agg[pid] = {"name": st.get("name"), "team": st.get("team"),
                        "pos": st.get("pos"), "cls": st.get("cls")}
        d = agg[pid]
        for k, v in st.items():
            if isinstance(v, (int, float)): d[k] = d.get(k, 0) + v
            else: d[k] = v

def simulate_window(n_weeks=1, expect_week=None):
    """Simulate n weeks.

    expect_week (STANDING RULE, restored in the 2035 rebuild): assert the week about
    to run is the week intended. A mismatch means state drifted, and the window
    refuses rather than silently simulating the wrong slate into canon.
    """
    s = load_state()
    if expect_week is not None and s["next_week"] != expect_week:
        raise RuntimeError("WEEK GUARD: state is at week %d but expect_week=%d"
                           % (s["next_week"], expect_week))
    from games_db import load_db, load_reg, save_db, save_reg, assign_seed
    import subdivision as _SUB
    _SUB.register(E)          # guest programs join the engine tables for this window
    FBS = set(U["teams"])
    db, reg = load_db(), load_reg()
    P = pid_team()
    rivalset = {frozenset((p["team_a"], p["team_b"])) for p in U["fixed_pairs"]}
    window_lines = []
    for _ in range(n_weeks):
        wk = s["next_week"]
        if wk > 14:
            print("regular season complete"); break
        games = [(h, a, ic) for w, h, a, ic in s["sched"] if w == wk]
        unavailable = frozenset(pid for pid, w in s["inj_out"].items() if w > 0)
        recent = frozenset(s["inj_recent"].keys())
        wk_perf = []
        for h, a, ic in games:
            gid = f"S{s.get("season",1)}W{wk:02d}_{h}_{a}"
            if gid in db: raise RuntimeError(f"double-sim: {gid}")
            seed = assign_seed(reg, gid)
            pregame_wp = win_prob(s, h, a)
            riv = frozenset((h, a)) in rivalset
            box, _pbp = E.simulate_game(h, a, seed, site="home", rivalry=riv, keep_pbp=True,
                                     unavailable_home=unavailable, unavailable_away=unavailable,
                                     recently_returned_home=recent, recently_returned_away=recent,
                                     hfa_override=dyn_hfa(s, h))
            import zlib, json as _json
            box["pbp_z"] = zlib.compress(_json.dumps(_pbp).encode(), 6)
            box["hfa_used"] = round(dyn_hfa(s, h), 3)
            box["game_id"] = gid; box["week"] = wk; box["pregame_home_wp"] = round(pregame_wp,3)
            box["unav_h"] = sorted(unavailable, key=str); box["unav_a"] = sorted(unavailable, key=str)
            db[gid] = box
            s["results"].append((wk, gid))
            hw = box["home_score"] > box["away_score"]
            wt, lt = (h, a) if hw else (a, h)
            # Subdivision guests play, but hold no record, streak, heat or hot-seat
            # pressure of their own -- only the FBS side of the game is bookkept.
            if wt in FBS: s["record"][wt]["W"] += 1
            if lt in FBS: s["record"][lt]["L"] += 1
            if ic:
                if wt in FBS: s["record"][wt]["confW"] += 1
                if lt in FBS: s["record"][lt]["confL"] += 1
            if h in FBS:
                s["record"][h]["PF"] += box["home_score"]; s["record"][h]["PA"] += box["away_score"]
            if a in FBS:
                s["record"][a]["PF"] += box["away_score"]; s["record"][a]["PA"] += box["home_score"]
            if wt in FBS: s["streak"][wt] = s["streak"][wt]+1 if s["streak"][wt] > 0 else 1
            if lt in FBS: s["streak"][lt] = s["streak"][lt]-1 if s["streak"][lt] < 0 else -1
            # heat: outcome vs expectation
            res_h = 1.0 if hw else 0.0
            if h in FBS:
                s["heat"][h] = 0.80*s["heat"][h] + 1.6*(res_h - pregame_wp)
                s["pressure"][h] += (pregame_wp - res_h)
            if a in FBS:
                s["heat"][a] = 0.80*s["heat"][a] + 1.6*((1-res_h) - (1-pregame_wp))
                s["pressure"][a] += ((1-pregame_wp) - (1-res_h))
            for inj in box["injuries"]:
                s["inj_out"][inj["pid"]] = inj["weeks_out"] if inj["weeks_out"] < 99 else 99
                s["inj_log"].append(dict(inj, week=wk))
                for pl in E.ROSTERS[inj["team"]]:
                    if pl["pid"] == inj["pid"]:
                        pl["inj_hist"].append({"season": s.get("season", 1), "week": wk,
                                               "desc": inj["desc"], "weeks": inj["weeks_out"]})
            merge_stats(s["season_stats"], box)
            E.update_reputation(box)
            upset = (hw and pregame_wp < 0.25) or ((not hw) and pregame_wp > 0.75)
            wk_perf.append((gid, h, a, box["home_score"], box["away_score"], pregame_wp, upset, riv, box["ot"]))
        # week rollover: injuries heal
        healed = [pid for pid, w in s["inj_out"].items() if w-1 <= 0 and w < 99]
        s["inj_out"] = {pid: (w-1 if w < 99 else 99) for pid, w in s["inj_out"].items() if (w-1 > 0 or w >= 99)}
        s["inj_recent"] = {pid: c+1 for pid, c in s["inj_recent"].items() if c+1 <= 2}
        for pid in healed: s["inj_recent"][pid] = 1
        # mid-season firing checks (from week 4, not for protected new hires)
        if wk >= 4:
            frng = random.Random(909000 + wk)
            for t in TEAMS:
                if t in s.setdefault("interims", {}): continue
                cs = E.COACHES[t]
                if cs.get("new_hire_protection"): continue
                threshold = 2.1 + cs["patience"] + (0.4 if wk <= 6 else 0.0)
                over = s["pressure"][t] - threshold
                if over > 0 and frng.random() < min(0.55, 0.28*over):
                    hc = cs["HC"]
                    cand = max(("OC","DC"), key=lambda r: cs[r]["skill"])
                    interim = dict(cs[cand]); interim["interim"] = True
                    s["interims"][t] = {"name": interim["name"], "from_role": cand, "skill": interim["skill"], "wins_since": 0}
                    s["firings"].append({"week": wk, "team": t, "fired": hc["name"], "tenure": hc["tenure"],
                                         "record": f'{s["record"][t]["W"]}-{s["record"][t]["L"]}',
                                         "interim": interim["name"], "interim_from": cand})
                    cs["HC"] = {"name": interim["name"], "skill": max(1.0, interim["skill"]-0.4), "tenure": 0}
        s["weekly_perf"].append((wk, wk_perf))
        s["next_week"] = wk + 1
        if wk in (6, 10):
            print("[RYSKAMP CHECKPOINT] week %d complete -> %s "
                  "(closed pools: 20 -> 10 -> 4 finalists must be strict subsets)"
                  % (wk, "name the TWENTY nominees now" if wk == 6 else "cut the pool to TEN now"))
    # same split as rosters: guest staffs never enter the FBS coaching table
    _fbs_names = set(U["teams"])
    with open('/home/claude/cfb2/state/coaches.pkl','wb') as fcs:
        pickle.dump({t: c for t, c in E.COACHES.items() if t in _fbs_names}, fcs)
    _guest_staff = {t: c for t, c in E.COACHES.items() if t not in _fbs_names}
    if _guest_staff:
        with open('/home/claude/cfb2/state/sub_coaches.pkl','wb') as fgs:
            pickle.dump(_guest_staff, fgs)
    save_db(db); save_reg(reg); save_state(s)
    E.persist_rosters()
    return s

def net_ratings(s, db=None):
    """KenPom-style adjusted efficiency + NCAA-NET-flavored composite.
    AdjO/AdjD: opponent-adjusted points scored/allowed per game (iterative).
    AdjEM = AdjO - AdjD (predictive). SOS = avg opponent AdjEM.
    NET = predictive rating blended with results (W-L) and schedule strength."""
    if db is None:
        from games_db import load_db
        db = load_db()
    HFA_PTS = 1.6
    _FBS = set(TEAMS)
    games = collections.defaultdict(list)   # t -> [(pts_for, pts_against, opp)]
    _pfx = f"S{s.get("season",1)}W"
    for box in db.values():
        if box.get("postseason"): continue
        if not box.get("game_id","").startswith(_pfx): continue
        # Subdivision guests are unrated, so games against them are excluded from the
        # adjusted-efficiency math entirely -- the same way non-Division-I results are
        # left out of real rating systems. They still count in the W-L record.
        if box["home"] not in _FBS or box["away"] not in _FBS: continue
        hs, as_ = min(box["home_score"], 59), min(box["away_score"], 59)
        games[box["home"]].append((hs - HFA_PTS/2, as_ + HFA_PTS/2, box["away"]))
        games[box["away"]].append((as_ + HFA_PTS/2, hs - HFA_PTS/2, box["home"]))
    lg_o = statistics_mean([pf for g in games.values() for pf, pa, o in g]) if games else 25.0
    adjO = {t: lg_o for t in TEAMS}; adjD = {t: lg_o for t in TEAMS}
    for _ in range(12):
        nO, nD = {}, {}
        for t in TEAMS:
            g = games.get(t, [])
            if not g:
                nO[t], nD[t] = adjO[t], adjD[t]; continue
            nO[t] = sum(pf + (lg_o - adjD[o]) for pf, pa, o in g)/len(g)
            nD[t] = sum(pa + (lg_o - adjO[o]) for pf, pa, o in g)/len(g)
        adjO, adjD = nO, nD
    em = {t: adjO[t] - adjD[t] for t in TEAMS}
    sos = {}
    for t in TEAMS:
        opps = [o for _,_,o in games.get(t, [])]
        sos[t] = sum(em[o] for o in opps)/len(opps) if opps else 0.0
    # small early-season prior, fades by week 6
    gp = {t: len(games.get(t, [])) for t in TEAMS}
    pre_mu = statistics_mean(list(s["preseason"].values()))
    net = {}
    for t in TEAMS:
        r = s["record"][t]
        prior_w = max(0.0, (6 - gp[t]) / 6) * 2.2
        net[t] = (em[t]
                  + 0.85*(r["W"] - r["L"])
                  + 0.30*sos[t]
                  + prior_w*(s["preseason"][t] - pre_mu))
    return {"adjO": adjO, "adjD": adjD, "em": em, "sos": sos, "net": net, "gp": gp}

def statistics_mean(v):
    return sum(v)/len(v) if v else 0.0

def top40(s, db=None, with_ratings=False):
    R = net_ratings(s, db)
    ranked = sorted(TEAMS, key=lambda t: -R["net"][t])[:40]
    return (ranked, R) if with_ratings else ranked

def top25(s):
    return top40(s)[:25]

def storylines(s, n_weeks=1):
    P = pid_team()
    lines = []
    recent = s["weekly_perf"][-n_weeks:]
    for wk, perf in recent:
        for gid, h, a, hs, as_, wp, upset, riv, ot in perf:
            if upset:
                winner = h if hs > as_ else a
                wprob = wp if hs > as_ else 1-wp
                lines.append(f"UPSET (Wk {wk}): {winner} {'def.' } {a if winner==h else h} {max(hs,as_)}-{min(hs,as_)} - pregame win prob just {100*wprob:.0f}%" + (" [RIVALRY]" if riv else "") + (f" [{ot}OT]" if ot else ""))
    for f in s["firings"]:
        if f["week"] > s["next_week"] - 1 - n_weeks:
            lines.append(f"FIRED (Wk {f['week']}): {f['team']} dismissed HC {f['fired']} ({f['record']}, tenure {f['tenure']} yrs); {f['interim_from']} {f['interim']} named interim")
    pr = sorted(TEAMS, key=lambda t: -s["pressure"][t])[:5]
    lines.append("HOT SEATS: " + "; ".join(f"{t} ({E.COACHES[t]['HC']['name']}, {s['record'][t]['W']}-{s['record'][t]['L']}, pressure {s['pressure'][t]:+.1f})" for t in pr if s["pressure"][t] > 0.8))
    streaks = sorted(TEAMS, key=lambda t: -abs(s["streak"][t]))[:4]
    lines.append("STREAKS: " + "; ".join(f"{t} {'W' if s['streak'][t]>0 else 'L'}{abs(s['streak'][t])}" for t in streaks))
    hot = sorted(TEAMS, key=lambda t: -s["heat"][t])[:3]
    cold = sorted(TEAMS, key=lambda t: s["heat"][t])[:3]
    lines.append("STADIUMS HEATING UP (dynamic HFA): " + "; ".join(f"{t} ({dyn_hfa(s,t):.1f} pts, base {E.COACHES[t]['hfa_base']})" for t in hot))
    lines.append("GONE COLD: " + "; ".join(f"{t} ({dyn_hfa(s,t):.1f} pts, base {E.COACHES[t]['hfa_base']})" for t in cold))
    latest = {}
    for i in s["inj_log"]:
        if s["inj_out"].get(i["pid"], 0) > 0 and P[i["pid"]]["abil"] >= 7.6:
            if i["pid"] not in latest or i["week"] > latest[i["pid"]]["week"]:
                latest[i["pid"]] = i
    stars_out = list(latest.values())
    if stars_out:
        lines.append("STAR INJURY REPORT: " + "; ".join(f"{i['name']} ({i['team']} {i['pos']}) - {i['desc']}, {'season' if i['weeks_out']>=99 else str(s['inj_out'][i['pid']])+' more wks'}" for i in stars_out[:5]))
    return lines
