"""Season 1 -> 2 coaching carousel. Organic wave: interim verdicts, retirements,
poaching chains (a hire from another school opens THAT school's seat too),
and marginal-seat firings. No forced count; the wave rides until it settles."""
import sys, os, random, pickle; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E
from names_v2 import pick_name_v2

def _assign_background(rng, U, rec):
    """Give a coach an alma mater and a dream job.

    These are what make a carousel feel human: a coordinator who would leave a better
    job to run his alma mater, a career assistant quietly waiting for one specific
    chair. Assigned once and carried for the coach's whole career.
    """
    teams = U["teams"]
    if not rec.get("alma_mater"):
        rec["alma_mater"] = rng.choice(teams)
    if not rec.get("dream_job"):
        # usually the alma mater, sometimes a blueblood, sometimes nowhere in particular
        roll = rng.random()
        if roll < 0.42:
            rec["dream_job"] = rec["alma_mater"]
        elif roll < 0.72:
            elite = sorted(teams, key=lambda t: -U["prestige"][t])[:18]
            rec["dream_job"] = rng.choice(elite)
        else:
            rec["dream_job"] = None
    return rec


def new_name(rng, used, sur):
    return pick_name_v2(rng, used, surname_usage=sur, surname_cap=2)[0]

def run_carousel(seed=99010):
    # ---------- STAGE 1, STEP 0: PRESTIGE MOVES ----------
    # The first thing that happens in an offseason, so everything downstream -- who can
    # hire whom, who recruits whom, who the portal rates -- sees what the season just
    # finished actually proved. State still holds the finished season at this point;
    # `rollover.py` does not reset it until stage 7.
    #
    # It lived at the end of the pipeline until 2040, which delayed every movement by a
    # full cycle. Three separate bugs kept it from moving at all before that; see
    # PENDING under stage 7 of the 2038-39 offseason.
    try:
        import prestige as _PR, pickle as _pk2
        from games_db import load_db as _ldb
        _s0 = SE.load_state()
        _season_done = _s0.get("season", 1)
        if E.U.get("prestige_recal_season") == _season_done:
            print("[prestige] recalibrated by hand for season %d; yearly step skipped" % _season_done)
        elif _s0.get("next_week", 0) != 0 or not _s0.get("results"):
            _moved = _PR.step(E.U, _ldb(), _s0, _season_done, write=True)
            _pk2.dump(E.U, open('/home/claude/cfb2/state/universe.pkl', 'wb'))
            print("[prestige] %d programmes moved on %d results"
                  % (len(_moved), len(_s0.get("results") or [])))
    except Exception as _ex:
        print("[prestige] SKIPPED:", _ex)

    # COACH-FOLLOWING SUPPORT: snapshot who coaches where BEFORE the carousel spins, so
    # the cycle can emit a machine-readable list of every coach who changed schools.
    # The portal reads it so players can follow a departed coach to his new job.
    import pickle as _pk
    _pre = _pk.load(open('/home/claude/cfb2/state/coaches.pkl','rb'))
    _pre_map = {}
    for _t, _staff in _pre.items():
        for _r in ("HC", "OC", "DC"):
            _nm = (_staff.get(_r) or {}).get("name")
            if _nm: _pre_map[_nm] = (_t, _r)
    rng = random.Random(seed)
    s = SE.load_state()
    C = E.COACHES
    U = E.U
    prestige = U["prestige"]
    interims = s.get("interims", {})
    db_teams = list(C.keys())

    # post-firing performance for interims (tracked via record since firing week)
    from games_db import load_db
    db = load_db()
    # "S1" would also prefix "S10..." and "S11...", so the tag must be followed by a
    # non-digit. Game ids read S11W03..., S11CCG..., S11PO_R1_...
    import re as _re
    _tag = _re.compile(r"^S%d(?!\d)" % s.get("season", 1))
    def interim_form(team):
        """The interim's own stint: games THIS season after the week he took over.

        This used to filter on week number alone against the whole games database,
        which holds every season ever played. A firing in week 6 therefore counted
        week 7+ of all eleven seasons -- Leafette's interim was judged on 49-25 when
        he had actually gone 4-2. The record drives `retain_p`, so the bug decided
        verdicts, not just the text: men who earned the job were let go and men who
        had not been kept. The season tag is the fix.
        """
        fw = next((f["week"] for f in s["firings"] if f["team"]==team), 6)
        w=l=0
        for gid, b in db.items():
            if not _tag.match(str(gid)):
                continue
            if b["week"]>fw and not b.get("postseason") and team in (b["home"],b["away"]):
                own = b["home_score"] if b["home"]==team else b["away_score"]
                opp = b["away_score"] if b["home"]==team else b["home_score"]
                w += own>opp; l += own<=opp
        return w, l

    used = set(); sur = {}
    for t in C:
        for role in ("HC","OC","DC"):
            nm = C[t][role]["name"]; used.add(nm)
            ln = nm.split()[-1]; sur[ln] = sur.get(ln,0)+1
    from collections import defaultdict
    sur = defaultdict(int, sur)

    # AGE every coach one year for the new offseason (retirements keyed to age)
    for _t in C:
        for _r in ("HC","OC","DC"):
            if C[_t].get(_r) and "age" in C[_t][_r]:
                C[_t][_r]["age"] += 1

    events = []            # (type, team, detail)
    openings = set()       # teams needing an HC
    coordinator_openings = []  # (team, role) needing a coordinator

    # 1) INTERIM VERDICTS
    for team, it in interims.items():
        w, l = interim_form(team)
        winpct = w/max(1,w+l) if (w+l) else 0.35
        pat = C[team]["patience"]
        # interims inherited a losing team; judge them generously vs that baseline.
        # competitiveness (any wins) + program patience both help them keep the job.
        retain_p = 0.32 + 0.75*winpct + 0.25*(pat-0.5)
        if w >= 2: retain_p += 0.12          # multiple wins in a bad spot = real credit
        if w+l == 0: retain_p = 0.30
        retain_p = min(0.85, max(0.08, retain_p))
        if rng.random() < retain_p:
            C[team]["HC"] = {"name": it["name"], "skill": round(max(2.0, it.get("skill",3.0)+0.3),2),
                             "tenure": 1, "aggression": round(min(0.95,max(0.05,rng.gauss(0.5,0.2))),2),
                             "age": it.get("age", int(rng.gauss(47,6))), "retire_age": int(max(58,min(74,rng.gauss(66,3.2))))}
            events.append(("interim_retained", team, f"{it['name']} ({w}-{l}) keeps the job"))
        else:
            openings.add(team)
            events.append(("interim_out", team, f"{it['name']} ({w}-{l}) not retained"))

    # 2) RETIREMENTS (age-driven: coaches retire as they approach their personal target age)
    for team in db_teams:
        if team in openings: continue
        hc = C[team]["HC"]
        ten = hc.get("tenure",1)
        age = hc.get("age", 50)
        target = hc.get("retire_age", 66)
        gap = target - age   # years until their intended retirement
        # probability ramps up sharply as they near/exceed their target age
        if gap >= 6:
            retire_p = 0.005                       # young/mid-career: very rare (health, life)
        elif gap >= 3:
            retire_p = 0.05
        elif gap >= 1:
            retire_p = 0.22
        elif gap == 0:
            retire_p = 0.45
        else:
            retire_p = min(0.92, 0.55 + (-gap)*0.18)   # past target: increasingly likely each year
        # OFFSEASON DISMISSAL (rewritten 2036 for realism). This used to key off
        # hc["skill"] -- a hidden rating no athletic director can see -- so good coaches
        # at bad programs were safe and bad coaches who won were not. Real firings follow
        # RESULTS AGAINST EXPECTATIONS: a blueblood expects ten wins, a bottom-tier
        # program expects five, and the same 7-5 season gets one coach extended and the
        # other dismissed.
        pat = C[team]["patience"]
        _w, _l = s["record"][team]["W"], s["record"][team]["L"]
        _gp = _w + _l
        if _gp >= 8:
            expected_w = 3.4 + (prestige[team] / 100.0) * 7.2
            shortfall = expected_w - _w
            # patience shifts the bar; a long-tenured coach has credit in the bank, and a
            # recent hire is protected by his buyout and the cost of starting over.
            tol = 1.4 + pat
            over = shortfall - tol
            marginal_p = 0.0
            if over > 0:
                marginal_p = min(0.80, 0.22 * over)
                if ten <= 1:
                    marginal_p *= 0.18        # year one or two: almost never
                elif ten <= 3:
                    marginal_p *= 0.65
                if ten >= 7:
                    marginal_p *= 0.70        # track record buys another year
                if _w == 0:
                    marginal_p = min(0.92, marginal_p + 0.25)
        else:
            marginal_p = 0.0
        roll = rng.random()
        if roll < retire_p:
            openings.add(team)
            events.append(("retire", team, f"{hc['name']} retires at {age} after {ten} yrs"))
        elif roll < retire_p + marginal_p:
            openings.add(team); events.append(("fired_offseason", team, f"{hc['name']} dismissed (offseason)"))

    # 3) CANDIDATE POOL
    # external candidates: rising coordinators, POACHED successful HCs, retreads, fresh names
    def build_candidates():
        cands = []
        # Coordinators become head-coaching candidates ON MERIT. The old version rolled a
        # flat 14% for anyone over 3.6, so a 9.0 coordinator was no likelier to get a shot
        # than a 3.7 one. The best assistants in the league are now the ones in demand.
        for t in db_teams:
            if t in openings: continue
            for role in ("OC","DC"):
                co = C[t][role]
                if co["skill"] < 3.4: continue
                # a unit at a winning program gets more interview traction
                _w = s["record"][t]["W"]; _l = s["record"][t]["L"]
                buzz = 0.55 if (_w + _l) and _w / max(1, _w + _l) >= 0.65 else 0.0
                p_shot = min(0.85, 0.04 + (co["skill"] - 3.4) * 0.11 + buzz * 0.25)
                if rng.random() < p_shot:
                    cands.append({"name":co["name"],"skill":round(co["skill"]+rng.uniform(-0.1,0.5),2),
                                  "from":(t,role),"kind":"coordinator",
                                  "alma_mater":co.get("alma_mater"),"dream_job":co.get("dream_job"),
                                  "age":co.get("age")})
        # SUCCESSFUL HEAD COACHES poachable from smaller programs. A sitting HC who won big
        # this season at a lower-prestige job is a hot commodity for a bigger opening.
        for t in db_teams:
            if t in openings: continue
            hc = C[t]["HC"]
            w = s["record"][t]["W"]; l = s["record"][t]["L"]
            if (w + l) < 8: continue
            win_pct = w / max(1, w + l)
            # strong season + decent coach + not already at an elite job = poachable.
            # 2039-40 (Dan): the gate was .700, which admitted ~11 coaches a year and
            # produced 8 sitting-HC hires in 100 against a real rate near half of all
            # P5 hires. Any winning season at a lower-division job now qualifies, and
            # .600 anywhere below the elite.
            tier_l6 = U["tiers"][U["team_conf"][t]] == "L6"
            overachieved = hc.get("skill", 5) >= 4.5 and prestige[t] < 78 and \
                           (win_pct >= 0.60 or (tier_l6 and win_pct > 0.5))
            if overachieved and rng.random() < 0.85:
                cands.append({"name": hc["name"],
                              "skill": round(hc["skill"] + rng.uniform(0.1, 0.6), 2),  # stock rises on success
                              "from": (t, "HC"), "kind": "poached_hc",
                              "record": f"{w}-{l}", "prev_prestige": prestige[t]})
        # SUBDIVISION HEAD COACHES -- the FCS-to-FBS route (2039-40). About one in
        # eight real G5 hires is an FCS head coach; the guest programmes have staffs
        # (state/sub_coaches.pkl), so their best head coaches are on the board.
        try:
            import subdivision as _SUB
            _subC = _pk.load(open(_SUB.SUB_COACH_PATH, "rb"))
        except Exception:
            _subC = {}
        for g, st_ in _subC.items():
            hc = st_.get("HC") or {}
            if hc.get("skill", 0) >= 4.0 and rng.random() < 0.7:
                cands.append({"name": hc["name"], "skill": round(hc["skill"] + rng.uniform(0.0, 0.4), 2),
                              "from": (g, "SUB_HC"), "kind": "sub_hc", "age": hc.get("age"),
                              "alma_mater": hc.get("alma_mater"), "dream_job": hc.get("dream_job")})
        # retreads: previously-fired HCs looking for another chair
        for f in s["firings"]:
            if rng.random() < 0.70:
                cands.append({"name":f["fired"],"skill":round(rng.uniform(3.0,4.6),2),
                              "from":None,"kind":"retread"})
        # Head coaches dismissed THIS cycle also look for work rather than vanishing from
        # the sport. Most drop back to a coordinator chair (handled below); the better ones
        # get another head job somewhere smaller.
        for _ev, _tm, _txt in events:
            if _ev in ("fired_offseason",) and rng.random() < 0.45:
                _old = _pre.get(_tm, {}).get("HC", {})
                if _old.get("name"):
                    cands.append({"name":_old["name"],
                                  "skill":round(max(2.0, _old.get("skill",3.5) - rng.uniform(0.1,0.6)),2),
                                  "from":None,"kind":"retread","age":_old.get("age"),
                                  "alma_mater":_old.get("alma_mater"),"dream_job":_old.get("dream_job")})
        # fresh blood
        for _ in range(60):
            cands.append({"name":new_name(rng,used,sur),"skill":round(rng.uniform(2.2,4.3),2),
                          "from":None,"kind":"first_time"})
        # Every candidate needs an alma mater and an ambition BEFORE the weighting runs --
        # otherwise the pull of home can never fire, which is what happened on the first
        # 2036 pass: thirty-six hires, not one homecoming.
        for c in cands:
            _assign_background(rng, U, c)
        # ONE ENTRY PER PERSON. A fired head coach could enter as a retread and again as
        # a sitting coordinator, and then be hired at two schools in the same wave -- the
        # uniqueness guard was cleaning that up after the fact instead of preventing it.
        _byname, _uniq = set(), []
        for c in cands:
            if c["name"] in _byname: continue
            _byname.add(c["name"]); _uniq.append(c)
        return _uniq

    # 4) FILL — highest-prestige openings hire first; poaching cascades
    def fill_wave():
        cands = build_candidates()
        queue = sorted(openings, key=lambda t: -prestige[t])   # big jobs hire first
        filled = []
        n_open = len(queue)
        hired_by_kind = {"coordinator":0, "retread":0, "first_time":0, "poached_hc":0, "sub_hc":0}
        # realistic targets: a couple retreads and a few first-timers should surface
        # (first-timer quota 0.28 -> 0.15 in 2039-40: coordinators are first-time head
        # coaches too, and the real no-HC-experience share is ~45% of ALL hires)
        target_retread   = max(1, round(n_open*0.18))
        target_firsttime = max(1, round(n_open*0.15))
        processed = 0
        guard = 0
        while queue and guard < 300:
            guard += 1
            # re-sort remaining openings each pass so a cascade opening slots by prestige
            queue = sorted([t for t in queue if t in openings], key=lambda t: -prestige[t])
            if not queue: break
            team = queue.pop(0)
            if team not in openings: continue
            idx = processed; processed += 1
            pn = prestige[team] / 100.0
            pool_floor = 2.4 + pn*2.2
            # 2039-40: a retread, a first-timer or a subdivision coach has to clear the
            # job's bar outright (coordinators and sitting HCs get the old 0.7 of
            # slack). Kaji Kita, 11-4 at prestige 78, had just hired a 3.60 retread
            # fired after 2-8 at Milharvey.
            viable = [c for c in cands if c["skill"] >= (pool_floor - 0.7 if c["kind"] in ("coordinator", "poached_hc")
                                                         else pool_floor + 0.4)] or cands[:]
            depth = min(1.0, idx / max(1, n_open-1))   # 0 (top job) .. 1 (bottom job)
            need_retread   = hired_by_kind["retread"]   < target_retread
            need_firsttime = hired_by_kind["first_time"] < target_firsttime
            # after the first wave of openings, later cascades are usually smaller replacements —
            # allow poaches to cascade but they get rarer as the chain deepens (no infinite churn)
            chain_damp = 1.0 if idx < n_open else 0.4
            # 2039-40: sitting head coaches are weighted as a CLASS, not per head. 300
            # coordinators were being weighted one by one against ~11 head coaches, so
            # the head-coach share of a P6 opening's hiring weight was 5%. Real P5 jobs
            # go to sitting head coaches about half the time (34% G5 HCs, 14% P5 HCs,
            # 2014-21); real G5 jobs take an FCS head coach about one time in eight.
            SHARE_HC  = 0.05 + 0.48*pn          # P6 (~.72) -> 40%, L6 (~.33) -> 21%
            SHARE_SUB = max(0.01, 0.14 - 0.18*pn)  # L6 -> ~8%, P6 -> ~1%
            def wt(c):
                base = c["skill"]**1.4
                if c["kind"]=="coordinator":
                    base *= (0.65 + 0.9*pn)
                elif c["kind"]=="poached_hc":
                    step_up = pn*100 - c.get("prev_prestige", 50)
                    if step_up < -3 and c.get("dream_job") != team and c.get("alma_mater") != team:
                        return 0.0            # nobody leaves a bigger job for a smaller one
                    if step_up <= 4:
                        base *= 0.4           # reluctant to leave for a lateral job
                    else:
                        base *= (1.0 + min(0.6, step_up/60))   # chain damping dropped for HCs
                elif c["kind"]=="sub_hc":
                    base *= 1.0
                elif c["kind"]=="retread":
                    base *= (1.0 + 0.5*pn)
                    if need_retread and depth > 0.35: base *= 3.2
                elif c["kind"]=="first_time":
                    # an unknown with no job does not get an elite chair: scaled by
                    # (1-pn)^1.5 in 2039-40 after Kaji Kita (11-4, prestige 78) drew a 4.22
                    base *= (1.4 - 0.8*pn) * (1.0 - pn) ** 1.5
                    if need_firsttime and depth > 0.45: base *= 3.6
                # THE PULL OF HOME. A coach takes his dream job, or a job at his alma
                # mater, over a better one somewhere else -- the single most human thing
                # in a carousel and previously not modelled at all.
                if c.get("dream_job") == team:
                    base *= 4.0
                elif c.get("alma_mater") == team:
                    base *= 2.2
                if base <= 0.0: return 0.0
                return max(0.05, base + rng.gauss(0, 0.5))
            weights = [wt(c) for c in viable]
            # rescale the sitting-HC and subdivision-HC classes to their target share
            # of the whole opening's weight (the per-head weights above keep the order
            # WITHIN each class)
            for kind, share in (("poached_hc", SHARE_HC), ("sub_hc", SHARE_SUB)):
                w_k = sum(w for c, w in zip(viable, weights) if c["kind"] == kind)
                w_o = sum(w for c, w in zip(viable, weights) if c["kind"] != kind)
                if w_k > 0 and w_o > 0:
                    f = share * w_o / ((1.0 - share) * w_k)
                    weights = [w * f if c["kind"] == kind else w for c, w in zip(viable, weights)]
            if os.environ.get("CAROUSEL_DEBUG"):
                _tot = sum(weights); _bk = {}
                for c, w in zip(viable, weights): _bk[c["kind"]] = _bk.get(c["kind"], 0) + w
                print("  [debug] %s pn=%.2f viable=%d shares %s" % (team, pn, len(viable),
                      {k: "%.0f%%" % (100 * v / _tot) for k, v in sorted(_bk.items(), key=lambda x: -x[1])}))
            pick = rng.choices(viable, weights=weights)[0]
            cands.remove(pick)
            hired_by_kind[pick["kind"]] = hired_by_kind.get(pick["kind"],0)+1
            # new hire age depends on kind: first-timers younger, retreads/poaches established
            if pick["kind"]=="first_time":
                _age=int(max(33,min(52,rng.gauss(41,5))))
            elif pick["kind"] in ("poached_hc", "sub_hc"):
                _age=pick.get("age") or int(rng.gauss(50,6))
            elif pick["kind"]=="retread":
                _age=int(max(45,min(66,rng.gauss(55,5))))
            else:  # coordinator stepping up
                _age=int(max(36,min(58,rng.gauss(46,5))))
            C[team]["HC"] = {"name":pick["name"], "skill":round(pick["skill"],2), "tenure":0,
                             "aggression":round(min(0.95,max(0.05,rng.gauss(0.5,0.2))),2),
                             "age":_age, "retire_age":int(max(58,min(74,rng.gauss(66,3.2)))),
                             "alma_mater":pick.get("alma_mater"), "dream_job":pick.get("dream_job")}
            _assign_background(rng, U, C[team]["HC"])
            if C[team]["HC"].get("dream_job") == team:
                events.append(("dream_job", team, f"{pick['name']} lands his dream job"))
            elif C[team]["HC"].get("alma_mater") == team:
                events.append(("coming_home", team, f"{pick['name']} returns to his alma mater"))
            C[team]["new_hire_protection"] = True
            openings.discard(team)
            detail = pick["kind"]
            if pick["from"]:
                src, role = pick["from"]
                if role == "SUB_HC":
                    detail = f"hired from {src} (subdivision HC)"
                    _sub_hired.append((src, pick["name"]))
                elif role == "HC":
                    detail = f"POACHED from {src} (HC, went {pick.get('record','')})"
                    if src not in openings:
                        openings.add(src)
                        queue.append(src)
                        events.append(("hc_poached_away", src, f"{pick['name']} left for {team}"))
                else:
                    detail = f"hired from {src} ({role})"
                    if src == team:
                        # promoted from within: his old chair is vacant immediately
                        detail = f"promoted from within ({role})"
                        C[team][role] = {"name": new_name(rng, used, sur),
                                         "skill": round(rng.uniform(2.3, 4.1), 2), "tenure": 0,
                                         "aggression": round(min(0.95, max(0.05, rng.gauss(0.5, 0.2))), 2),
                                         "age": int(max(31, min(60, rng.gauss(44, 7))))}
                        _assign_background(rng, U, C[team][role])
                    else:
                        coordinator_openings.append((src, role))
            filled.append((team, pick["name"], round(pick["skill"],2), detail))
        return filled

    _sub_hired = []
    filled = fill_wave()
    # a subdivision programme that lost its head coach promotes a fresh one
    if _sub_hired:
        import subdivision as _SUB
        _subC = _pk.load(open(_SUB.SUB_COACH_PATH, "rb"))
        for g, nm in _sub_hired:
            if g in _subC and _subC[g]["HC"]["name"] == nm:
                _subC[g]["HC"] = {"name": new_name(rng, used, sur), "skill": round(rng.uniform(2.4, 4.4), 2),
                                  "tenure": 0, "aggression": round(min(0.95, max(0.05, rng.gauss(0.5, 0.2))), 2),
                                  "age": int(max(33, min(58, rng.gauss(45, 6)))), "retire_age": 66}
        _pk.dump(_subC, open(_SUB.SUB_COACH_PATH, "wb"))

    # 5) RESOLVE COORDINATOR OPENINGS (may cascade again if filled from yet another school)
    coord_events = []
    guard = 0
    while coordinator_openings and guard < 200:
        guard += 1
        team, role = coordinator_openings.pop(0)
        # promote internal position coach OR hire external coordinator; small poach chance
        if rng.random() < 0.25:
            # poach a coordinator from a lower-prestige school -> opens that seat
            donors = [t for t in db_teams if t != team and prestige[t] < prestige[team]]
            if donors:
                src = rng.choice(donors); srole = rng.choice(["OC","DC"])
                moved = C[src][srole]
                C[team][role] = {"name":moved["name"],"skill":round(moved["skill"]+0.1,2),"tenure":0,
                                 "aggression":round(min(0.95,max(0.05,rng.gauss(0.5,0.2))),2)}
                coordinator_openings.append((src, srole))
                coord_events.append((team, role, f"poached {moved['name']} from {src}"))
                continue
        # otherwise fresh/promoted coordinator
        C[team][role] = {"name":new_name(rng,used,sur),"skill":round(rng.uniform(2.3,4.1),2),
                         "tenure":0,"aggression":round(min(0.95,max(0.05,rng.gauss(0.5,0.2))),2)}
        coord_events.append((team, role, "new coordinator hired/promoted"))

    # ------------------------------------------------------------------
    # 6) PROACTIVE COORDINATOR RAIDS
    # Backfilling vacancies is only half a carousel. Strong programs go out and TAKE the
    # best assistants in the sport, which is how a staff like Kaji Daun's 2035 superstaff
    # gets assembled -- and how a quiet program that built its identity on one brilliant
    # coordinator loses it. A raided school backfills, which can cascade.
    # ------------------------------------------------------------------
    MAX_RAIDS = 12
    # One job per coach per cycle, and anyone who just took a job is off the market:
    # on the first 2036 pass a coach was hired as Dietsche's head coach and poached away
    # as a coordinator in the same offseason.
    _taken = {C[t]["HC"]["name"] for t, _n, _s, _d in
              [(f[0], f[1], f[2], f[3]) for f in filled]}
    raids = 0
    raid_order = sorted(db_teams, key=lambda t: -prestige[t])
    for team in raid_order:
        if raids >= MAX_RAIDS: break
        for role in ("OC", "DC"):
            if raids >= MAX_RAIDS: break
            here = C[team][role]
            if here["name"] in _taken: continue
            # who is clearly better, and reachable? A raid needs a real gap and a step up.
            pool = []
            for t2 in db_teams:
                if t2 == team or prestige[t2] >= prestige[team] - 4: continue
                for r2 in ("OC", "DC"):
                    cand = C[t2][r2]
                    if cand["name"] in _taken: continue
                    if cand["skill"] >= here["skill"] + 1.2:
                        pool.append((cand["skill"], t2, r2))
                # a successful head coach at a small school will step DOWN to coordinate
                # at a giant -- real, and the most interesting raid of all
                hc2 = C[t2]["HC"]
                if hc2["name"] in _taken: continue
                # 2039-40: lower-division head coaches only. The 2039-40 cycle pulled a
                # 9.62 head coach out of a Power North job (Marblehead) and an 8.99 out
                # of Parchynt to be coordinators -- coaches that good at a P6 school
                # are head-coaching candidates, not step-down candidates.
                if U["tiers"][U["team_conf"][t2]] != "L6": continue
                if hc2["skill"] >= here["skill"] + 2.0 and prestige[t2] < prestige[team] - 18:
                    pool.append((hc2["skill"] - 0.2, t2, "HC"))
            if not pool: continue
            pool.sort(reverse=True)
            sk, src, srole = pool[0]
            if rng.random() > 0.55: continue
            moved = dict(C[src][srole])
            _taken.add(moved["name"])
            moved["tenure"] = 0
            moved["skill"] = round(min(9.9, moved["skill"] + 0.3), 2)   # a bigger job, a raise
            C[team][role] = moved
            raids += 1
            verb = "lured HC" if srole == "HC" else "raided coordinator"
            coord_events.append((team, role, f"{verb} {moved['name']} from {src}"))
            if srole == "HC":
                # the donor school now needs a head coach; promote from within
                promo = max(("OC", "DC"), key=lambda r: C[src][r]["skill"])
                newhc = dict(C[src][promo])
                newhc["tenure"] = 0
                C[src]["HC"] = newhc
                _taken.add(newhc["name"])
                C[src][promo] = {"name": new_name(rng, used, sur),
                                 "skill": round(rng.uniform(2.3, 4.1), 2), "tenure": 0,
                                 "aggression": round(min(0.95, max(0.05, rng.gauss(0.5, 0.2))), 2),
                                 "age": int(max(31, min(60, rng.gauss(44, 7))))}
                _assign_background(rng, U, C[src][promo])
                s.setdefault("hc_changes_extra", []).append(
                    (src, f"{moved['name']} left for {team} {role}; promoted {newhc['name']} to HC"))
            else:
                C[src][srole] = {"name": new_name(rng, used, sur),
                                 "skill": round(rng.uniform(2.3, 4.1), 2), "tenure": 0,
                                 "aggression": round(min(0.95, max(0.05, rng.gauss(0.5, 0.2))), 2),
                                 "age": int(max(31, min(60, rng.gauss(44, 7))))}
                _assign_background(rng, U, C[src][srole])
                coord_events.append((src, srole, "new coordinator (backfill after raid)"))

    # ------------------------------------------------------------------
    # 7) GUARDS: every coach holds exactly one job, and every record is complete.
    # ------------------------------------------------------------------
    _seen = {}
    for _t2 in C:
        for _r2 in ("HC", "OC", "DC"):
            _rec = C[_t2].get(_r2)
            if not _rec: continue
            _assign_background(rng, U, _rec)
            _rec.setdefault("age", int(max(32, min(64, rng.gauss(46, 8)))))
            _rec.setdefault("retire_age", int(max(_rec["age"] + 3, min(74, rng.gauss(66, 3.2)))))
            _rec.setdefault("aggression", round(min(0.95, max(0.05, rng.gauss(0.5, 0.2))), 2))
            _nm = _rec["name"]
            if _nm in _seen:
                print(f"[carousel guard] {_nm} held {_seen[_nm]} and {(_t2,_r2)} -- clearing the junior seat")
                _ct, _cr = (_t2, _r2) if _r2 != "HC" else _seen[_nm]
                C[_ct][_cr] = {"name": new_name(rng, used, sur),
                               "skill": round(rng.uniform(2.3, 4.1), 2), "tenure": 0,
                               "aggression": round(min(0.95, max(0.05, rng.gauss(0.5, 0.2))), 2),
                               "age": int(max(31, min(60, rng.gauss(44, 7))))}
                _assign_background(rng, U, C[_ct][_cr])
            else:
                _seen[_nm] = (_t2, _r2)

    # completeness pass AFTER the dedup, so records the guard replaced are filled in too
    for _t2 in C:
        for _r2 in ("HC", "OC", "DC"):
            _rec = C[_t2].get(_r2)
            if not _rec: continue
            _assign_background(rng, U, _rec)
            _rec.setdefault("age", int(max(32, min(64, rng.gauss(46, 8)))))
            _rec.setdefault("retire_age", int(max(_rec["age"] + 3, min(74, rng.gauss(66, 3.2)))))
            _rec.setdefault("aggression", round(min(0.95, max(0.05, rng.gauss(0.5, 0.2))), 2))
            _rec.setdefault("tenure", 0)

    # ------------------------------------------------------------------
    # 8) COACH MOVES: diff against the pre-carousel snapshot so the transfer portal can
    # let players FOLLOW a coach who changed schools, in any role.
    # ------------------------------------------------------------------
    _moves = []
    for _t2, _staff2 in C.items():
        for _r2 in ("HC", "OC", "DC"):
            _nm = (_staff2.get(_r2) or {}).get("name")
            if not _nm: continue
            _was = _pre_map.get(_nm)
            if _was and _was[0] != _t2:
                _moves.append({"coach": _nm, "from": _was[0], "from_role": _was[1],
                               "to": _t2, "to_role": _r2,
                               "skill": _staff2[_r2].get("skill", 5.0)})
    s["coach_moves"] = _moves

    # persist
    # new hires: give team_discipline based on their skill (disciplined coaches -> fewer flags)
    for t in C:
        if "team_discipline" not in C[t]:
            sk = C[t]["HC"].get("skill",5.0)
            C[t]["team_discipline"] = round(max(0.8, min(1.25, 1.0-(sk-5.0)*0.03)),3)
    with open('/home/claude/cfb2/state/coaches.pkl','wb') as f: pickle.dump(C, f)
    s["carousel_s%d"%s.get("season",1)] = {"events":events, "filled":filled,
                                           "coord_events":coord_events, "raids":raids,
                                           "coach_moves":_moves}
    s.pop("interims", None)   # interims resolved
    SE.save_state(s)
    return events, filled, coord_events

if __name__ == "__main__":
    events, filled, coord = run_carousel()
    from collections import Counter
    ec = Counter(e[0] for e in events)
    print("VACANCY SOURCES:", dict(ec))
    print("HC HIRES:", len(filled), "| COORDINATOR MOVES:", len(coord))
