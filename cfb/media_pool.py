"""The media poll as sixty people (Dan, 2040 preseason).

Until 2040 the media poll was one formula with a noise term. Now, every season, five
programmes are drawn from each power conference and four from each lower one, and a
media representative from each school joins the year's pool: sixty voters, each with a short bio and their
own quirks. Every voter files a top 25 each week from the same facts weighted their
own way, and the published poll is the composite (25 points for #1 down to 1 for #25).

What makes them differ -- each trait is drawn once, when the pool is formed:
  w_last      how much last season (record, title, playoff trip) still matters
  w_recruit   how much the signing class matters
  w_talent    how much the roster on paper matters
  w_results   how hard this season's results pull the ballot
  inertia     how slowly the voter moves their own ballot week to week
  homer       points for the voter's own school -- usually positive, sometimes negative
              (the ones who underrate their own team)
  rival       points taken from the school's locked rivals and conference rivals
  conf        a small bump for the voter's own conference
  surprise    a weekly propensity to slip one team nobody saw coming onto the ballot --
              a different team each time it happens, never a standing favourite
  contrarian  a dislike of the consensus top -- shaves points off the obvious picks
  noise       how erratic the ballot is week to week

State written:
  s['media_pool_s{N}']          the sixty voters (traits, bio)
  s['media_ballots'][week]      {voter_id: [25 teams]} for the week just polled
  s['media_voter_prev']         each voter's last ballot, for their inertia
"""
import sys, random, collections
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E
from names_v2 import pick_name_v2

PER_CONF = {"P6": 6, "L6": 4}
H2H_NUDGE = 3.0        # points each way when a ballot has a loser above the team that beat it      # Dan: six voters from each power conference, four from each lower one
PTS = {i + 1: 25 - i for i in range(25)}

ROLES = [
    ("TV anchor", "weeknight sports anchor at {outlet}; has covered {team} since {since}"),
    ("former SID", "ran {team}'s sports information office for {yrs} years before switching sides of the press box", 38),
    ("booster newsletter", "lifelong season-ticket holder who writes the {mascot} booster newsletter for {outlet}"),
    ("former walk-on", "walked on at {pos} for {team} ({span}) and never made the two-deep; now writes for {outlet}"),
    ("national writer", "national college football writer at {outlet} who grew up {a_team} fan"),
    ("former trainer", "was an athletic trainer on the {team} staff for {yrs} years; now a columnist at {outlet}", 36),
    ("high school coach", "coaches high school ball in {state} and files a weekly {team} column for {outlet}"),
    ("stats blogger", "runs the {mascot} analytics blog at {outlet}; came to football from a career in actuarial work"),
    ("retired referee", "officiated in the conference for {yrs} years; writes the rules-and-replay column at {outlet}", 48),
    ("play-by-play", "the {mascot} play-by-play voice on {outlet} since {since}"),
    ("parent", "parent of a former {team} {pos}; writes the family-section column at {outlet}", 46),
    ("beat writer", "covers {team} for {outlet}"),
    ("columnist", "columnist at {outlet}, on the {team} beat since {since}"),
    ("radio host", "hosts the {mascot} pregame show on {outlet}"),
    ("former player", "played {pos} at {team} ({span}); now calls games for {outlet}"),
    ("alumnus", "{team} class of {grad}; writes the newsletter at {outlet}"),
    ("sideline reporter", "sideline reporter for {outlet}'s {team} broadcasts"),
    ("podcaster", "runs the {mascot} podcast {outlet}"),
    ("sports editor", "ran the sports desk at the {team} student paper; turned pro at {outlet}"),
    ("photographer-turned-writer", "shot {team} games for {outlet} for a decade before moving to the keyboard", 34),
    ("retired coach", "coached high school ball in {state} for {yrs} years; writes about {team} for {outlet}", 50),
]
OUTLETS = ["The {state} Ledger", "{state} Public Radio", "The {city} Courier", "{mascot} Nation", "WRLD {state}",
           "The Daily {state}", "{city} Sports Weekly", "Roiland Sports Network", "The {mascot} Report",
           "{state} Press-Gazette", "KRSN {city}", "The {city} Standard"]
QUIRKS = {
    "w_last": ("still ranks off last year's standings deep into October", "treats last season as ancient history by week 2"),
    "w_recruit": ("reads signing day like scripture", "thinks recruiting rankings are a scam"),
    "w_talent": ("votes the roster on paper", "doesn't care who's on the roster, only who wins"),
    "w_results": ("overreacts to every Saturday", "needs to see it three weeks running before moving anyone"),
    "homer": ("an unapologetic homer", "famously harder on the home team than anyone"),
    "rival": ("has never once ranked a rival where they belong", None),
    "contrarian": ("allergic to consensus", None),
    "noise": ("ballot changes with the weather", "the most stable ballot in the pool"),
}
POSITIONS = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P"]


def _lognorm(rng, sd):
    return max(0.25, min(3.0, rng.lognormvariate(0.0, sd)))


def pick_role(rng, age):
    ok = [r for r in ROLES if len(r) < 3 or age >= r[2]]
    r = rng.choice(ok)
    return r[0], r[1]


def draw_traits(rng):
    """One voter's personality. Spreads widened in the 2040 redraw (Dan: 'slightly more
    diverse'); two eyes added -- a regional pull toward same-state programmes and an
    offense/defense lean in how this season's results are read."""
    return {
        "w_last": _lognorm(rng, 0.6), "w_recruit": _lognorm(rng, 0.75), "w_talent": _lognorm(rng, 0.5),
        "w_results": _lognorm(rng, 0.35), "inertia": max(0.05, min(0.8, rng.gauss(0.4, 0.18))),
        "homer": (rng.gauss(-6, 3) if rng.random() < 0.25 else abs(rng.gauss(7, 6))),
        "rival": (-abs(rng.gauss(6, 4)) if rng.random() < 0.55 else 0.0),
        "conf": max(0.0, rng.gauss(2.0, 2.0)),
        "contrarian": (abs(rng.gauss(5, 2.5)) if rng.random() < 0.2 else 0.0),
        "noise": max(1.0, rng.gauss(4.5, 2.3)),
        "surprise": rng.choices([0.0, 0.12, 0.3, 0.55], weights=[40, 35, 18, 7])[0],
        "regional": max(0.0, rng.gauss(2.5, 2.5)) if rng.random() < 0.4 else 0.0,
        # how much a voter notices the lower division: the mid-major darling term
        # (a 12-1 L6 conference champion) times this. Lower-division voters get it x1.6.
        "w_l6": _lognorm(rng, 0.55),
        "style": rng.choices(["balanced", "offense", "defense"], weights=[55, 25, 20])[0],
    }


def make_pool(s, seed=None):
    """Draw the season's sixty voters. Deterministic for a season."""
    U = E.U
    season = s.get("season", 1)
    rng = random.Random(seed if seed is not None else 777000 + season)
    used, sur = set(), collections.defaultdict(int)
    voters = []
    locked = collections.defaultdict(set)
    for p in U["fixed_pairs"]:
        locked[p["team_a"]].add(p["team_b"]); locked[p["team_b"]].add(p["team_a"])
    all_teams = list(U["teams"])
    # Dan, 2041 preseason: half the schools carry over from last year's pool (3 of 6 in a
    # P6 conference, 2 of 4 in an L6), and no school holds a seat more than two years
    # running. A carried-over school keeps the same voter, a year older.
    prev = {v["team"]: v for v in (s.get("media_pool_s%d" % (season - 1)) or [])}
    hist = s.setdefault("media_pool_teams", {})            # season -> [teams]
    two_ago = set(hist.get(season - 2, []))
    this_year = []
    for conf in U["tiers"]:
        teams = list(U["conferences"][conf]); n = PER_CONF[U["tiers"][conf]]
        last = [t for t in teams if t in prev]
        keepable = [t for t in last if t not in two_ago]       # a third straight year is not allowed
        keep = rng.sample(keepable, min(n // 2, len(keepable)))
        fresh_pool = [t for t in teams if t not in prev] or [t for t in teams if t not in keep]
        chosen = keep + rng.sample(fresh_pool, n - len(keep))
        this_year.extend(chosen)
        for t in chosen:
            if t in prev:
                v = dict(prev[t]); v["age"] = v["age"] + 1; v["id"] = "V%02d_%s" % (len(voters), t.replace(" ", ""))
                v["bio"] = v["bio"].replace("%s, %d" % (v["name"], v["age"] - 1), "%s, %d" % (v["name"], v["age"]), 1)
                v["returning"] = True
                voters.append(v); used.add(v["name"]); continue
            geo = U["geo"].get(t, {})
            state = geo.get("state", t); mascot = geo.get("mascot", "Football")
            city = U["host_cities"].get(t) or state
            age = int(max(24, min(78, rng.gauss(46, 12))))
            role, tmpl = pick_role(rng, age)
            outlet = rng.choice(OUTLETS).format(state=state, city=city, mascot=mascot)
            yrs = max(5, min(age - 25, int(rng.gauss(18, 6))))
            grad = (2025 + season) - (age - 22)
            span = "%d-%d" % (grad - 4, grad - 1)
            desc = tmpl.format(team=t, a_team=("an " if t[0] in "AEIOU" else "a ") + t, outlet=outlet, mascot=mascot, state=state, since=max(grad, (2025 + season) - yrs),
                               pos=rng.choice(POSITIONS), span=span, grad=grad, yrs=yrs)
            # traits
            tr = draw_traits(rng)
            if U["tiers"][conf] == "L6": tr["w_l6"] = round(tr["w_l6"] * 1.6, 3)
            # surprise: not a fixed set of teams (Dan, 2040) but a weekly PROPENSITY. Each
            # week, with this probability, the voter slips one team from outside the
            # consensus top 20 onto the ballot -- a different team every time it happens.
            # bio: role line + the two most distinctive quirks
            quirks = []
            for k, (hi, lo) in QUIRKS.items():
                v = tr[k]
                if k in ("w_last", "w_recruit", "w_talent", "w_results"):
                    if v > 1.55: quirks.append((v - 1, hi))
                    elif v < 0.6 and lo: quirks.append((1 - v, lo))
                elif k == "homer":
                    if v > 11: quirks.append((v / 10, hi))
                    elif v < 0: quirks.append((-v / 4, lo))
                elif k == "rival" and v < -8: quirks.append((-v / 8, hi))
                elif k == "contrarian" and v > 0: quirks.append((v / 5, hi))
                elif k == "noise":
                    if v > 7.5: quirks.append((v / 6, hi))
                    elif v < 2.5: quirks.append((1.0, lo))
            if tr["regional"] > 4: quirks.append((tr["regional"] / 5, "votes the whole state of %s up" % state))
            if tr["style"] == "offense": quirks.append((0.7, "falls for any team that scores 40"))
            elif tr["style"] == "defense": quirks.append((0.7, "won't rank a team that can't stop anyone"))
            if tr["surprise"] >= 0.3:
                quirks.append((tr["surprise"] * 2, "liable to rank a team nobody saw coming" if tr["surprise"] < 0.5 else "a surprise pick almost every week"))
            quirks.sort(key=lambda q: -q[0])
            qtext = "; ".join(q[1] for q in quirks[:3])
            name = pick_name_v2(rng, used, surname_usage=sur, surname_cap=1)[0]
            bio = "%s, %d — %s. %s" % (name, age, desc, (qtext[0].upper() + qtext[1:] + ".") if qtext else "Plays it straight.")
            voters.append({"id": "V%02d_%s" % (len(voters), t.replace(" ", "")), "name": name, "age": age,
                           "team": t, "conf": conf, "role": role, "outlet": outlet, "bio": bio,
                           "traits": tr, "rivals": sorted(locked.get(t, set())), "returning": False})
    hist[season] = this_year
    return voters


def redraw_personalities(voters, s, seed=None):
    """Keep every voter's name, age, school and conference; redraw their background
    and personality (Dan, 2040 preseason: 'more diverse')."""
    U = E.U
    season = s.get("season", 1)
    rng = random.Random(seed if seed is not None else 778000 + season)
    for v in voters:
        t = v["team"]; geo = U["geo"].get(t, {})
        state = geo.get("state", t); mascot = geo.get("mascot", "Football")
        city = U["host_cities"].get(t) or state
        age = v["age"]
        role, tmpl = pick_role(rng, age)
        outlet = rng.choice(OUTLETS).format(state=state, city=city, mascot=mascot)
        yrs = max(5, min(age - 25, int(rng.gauss(18, 6))))
        grad = (2025 + season) - (age - 22); span = "%d-%d" % (grad - 4, grad - 1)
        desc = tmpl.format(team=t, a_team=("an " if t[0] in "AEIOU" else "a ") + t, outlet=outlet, mascot=mascot, state=state, since=max(grad, (2025 + season) - yrs),
                           pos=rng.choice(POSITIONS), span=span, grad=grad, yrs=yrs)
        tr = draw_traits(rng)
        if U["tiers"][v["conf"]] == "L6": tr["w_l6"] = round(tr["w_l6"] * 1.6, 3)
        v.update({"role": role, "outlet": outlet, "traits": tr})
        v["bio"] = "%s, %d — %s. %s" % (v["name"], age, desc, quirk_text(tr, state))
    return voters


def quirk_text(tr, state):
    quirks = []
    for k, (hi, lo) in QUIRKS.items():
        v = tr[k]
        if k in ("w_last", "w_recruit", "w_talent", "w_results"):
            if v > 1.55: quirks.append((v - 1, hi))
            elif v < 0.6 and lo: quirks.append((1 - v, lo))
        elif k == "homer":
            if v > 11: quirks.append((v / 10, hi))
            elif v < 0: quirks.append((-v / 4, lo))
        elif k == "rival" and v < -8: quirks.append((-v / 8, hi))
        elif k == "contrarian" and v > 0: quirks.append((v / 5, hi))
        elif k == "noise":
            if v > 7.5: quirks.append((v / 6, hi))
            elif v < 2.5: quirks.append((1.0, lo))
    if tr["regional"] > 4: quirks.append((tr["regional"] / 5, "votes the whole state of %s up" % state))
    if tr["style"] == "offense": quirks.append((0.7, "falls for any team that scores 40"))
    elif tr["style"] == "defense": quirks.append((0.7, "won't rank a team that can't stop anyone"))
    if tr["surprise"] >= 0.3:
        quirks.append((tr["surprise"] * 2, "liable to rank a team nobody saw coming" if tr["surprise"] < 0.5 else "a surprise pick almost every week"))
    quirks.sort(key=lambda q: -q[0])
    qtext = "; ".join(q[1] for q in quirks[:3])
    return (qtext[0].upper() + qtext[1:] + ".") if qtext else "Plays it straight."


def team_components(s, db):
    """The facts every voter sees, computed once a week. Returns per-team dicts."""
    import pickle, season as SE
    U = E.U; prestige = U["prestige"]
    seas = s.get("season", 1); year_now = 2025 + seas
    book = (s.get("history") or {}).get("book", {})
    sa = (s.get("season_archive", {}) or {}).get(str(seas - 1), {}) or {}
    last_rec = sa.get("standings", {}) or {}
    ch = (s.get("history") or {}).get("champ", {}).get(year_now - 1)
    champ, runnerup = (ch[0], ch[1]) if ch and len(ch) > 1 else (sa.get("champion"), None)
    try:
        po = pickle.load(open('/home/claude/cfb2/state/playoff_s%d.pkl' % (seas - 1), 'rb'))
        field = set(po.get("seeds", {}))
    except Exception:
        field = set()
    try:
        cc = pickle.load(open('/home/claude/cfb2/state/conf_champs_s%d.pkl' % (seas - 1), 'rb'))
        l6_champs = {t for c, t in cc.items() if U["tiers"].get(c) == "L6"}
    except Exception:
        l6_champs = set()
    signed = (s.get("recruiting_s%d" % (seas - 1), {}) or {}).get("signed", {})
    recruit = {t: sum(r.get("stars", 2) for r in signed.get(t, [])) + 4 * sum(1 for r in signed.get(t, []) if r.get("stars", 0) >= 4)
               for t in U["teams"]}
    played = len({w for w, _g in (s.get("results") or [])})
    rec = s["record"]
    net = SE.net_ratings(s, db) if played >= 1 else None
    pfx = "S%dW" % seas
    losses_opp = collections.defaultdict(list)
    # THE LOSS ITSELF (2040 week 0). The results term ramps in with games played, so one
    # week in it weighed 16% and a #5 shut out 13-0 by an unranked team stayed #5. A
    # loss is a headline the moment it happens: each one costs a fixed amount -- more
    # to an unranked opponent, more by margin, more for a shutout -- at full weight,
    # scaled only by the voter's own reaction trait.
    rk_now = {t: r for r, t in (s.get("media_poll_current") or []) if r <= 25}
    loss_pen = collections.defaultdict(float)
    h2h = []                                   # (winner, loser) this season, top-division pairs
    if played >= 1:
        for gid, b in db.items():
            if not gid.startswith(pfx): continue
            h, a = b["home"], b["away"]; hw = b["home_score"] > b["away_score"]
            l = a if hw else h; w = h if hw else a
            if l not in rec: continue
            if w in rec: h2h.append((w, l))
            if net: losses_opp[l].append(net["em"].get(w, 0.0))
            margin = abs(b["home_score"] - b["away_score"])
            pen = 12.0 + min(12.0, margin * 0.4)
            if w not in rk_now: pen += 8.0                     # lost to an unranked team
            elif rk_now[w] <= 10: pen -= 5.0                    # lost to a top-ten team: forgivable
            if (b["home_score"] if l == h else b["away_score"]) == 0: pen += 4.0   # shut out
            if w not in U["teams"]: pen += 10.0                 # lost to a subdivision guest
            loss_pen[l] += pen
            # and the win over a ranked team is a headline too
            if w in rec and l in rk_now:
                loss_pen[w] -= 12.0 if rk_now[l] <= 10 else 7.0
    comp = {}
    for t in U["teams"]:
        b = book.get(t, {})
        ped = min(12.0, 3 * sum(1 for y in b.get("titles", []) if year_now - y <= 25)
                  + 1.5 * sum(1 for y in b.get("runnerup", []) if year_now - y <= 25))
        roster = [pl for pl in E.ROSTERS.get(t, []) if s.get("inj_out", {}).get(pl["pid"], 0) == 0]
        top = sorted((pl["abil"] for pl in roster), reverse=True)[:25]
        talent = sum(top) / max(1, len(top)); star = max((pl["abil"] for pl in roster), default=5)
        last = last_rec.get(t, {}).get("W", 0) * 1.6 + (6 if t in field else 0) + (22 if t == champ else 0) + (12 if t == runnerup else 0) + ped * 2.2
        r = rec[t]; gp = r["W"] + r["L"]
        cur = 0.0
        if played >= 1:
            cur = r["W"] * 9.0 + (r["PF"] - r["PA"]) * 0.30 + (net["em"][t] * 0.8 if net else 0)
            if gp and r["L"] == 0: cur += 8
            if r["L"] and net:
                avg = sum(losses_opp[t]) / max(1, len(losses_opp[t]))
                cur += min(9, max(0, avg) * 0.6 + (prestige[t] - 55) * 0.10)
            if gp and r["W"] == 0 and prestige[t] < 60: cur -= 8
        # the mid-major darling: a lower-division programme off a big year. Without this
        # only two L6 teams drew a single vote in the 2040 preseason poll; real polls
        # carry three to six. Fades with the preseason weight like the other reputation
        # terms, and this season's results take over.
        darling = 0.0
        if U["tiers"][U["team_conf"][t]] == "L6":
            lw = last_rec.get(t, {}).get("W", 0)
            darling = max(0, lw - 8) * 1.6 + (4.0 if t in l6_champs else 0.0) + (3.0 if t in field else 0.0)
        comp[t] = {"prestige": prestige[t] * 0.9, "last": last, "talent": talent * 5.5 + star * 3.0, "darling": darling,
                   "recruit": recruit[t] * 0.45, "cur": cur, "loss_pen": loss_pen.get(t, 0.0),
                   "ppg": (r["PF"] / gp if gp else 0.0), "papg": (r["PA"] / gp if gp else 0.0),
                   "state": U["geo"].get(t, {}).get("state")}
    meta = {"played": played, "preseason_w": max(0.15, 1.0 - played * 0.09), "result_w": min(1.0, played * 0.16),
            "h2h": h2h}
    return comp, meta


def vote(voter, comp, meta, consensus_prev, prev_ballot, rng):
    """One voter's top 25."""
    tr = voter["traits"]; team = voter["team"]
    pw, rw = meta["preseason_w"], meta["result_w"]
    U = E.U
    conf_mates = set(U["conferences"][voter["conf"]])
    home_state = U["geo"].get(team, {}).get("state")
    style = tr.get("style", "balanced")
    score = {}
    for t, c in comp.items():
        v = c["prestige"] + c["last"] * tr["w_last"] * pw + c["talent"] * tr["w_talent"] \
            + c["recruit"] * tr["w_recruit"] * pw + c["cur"] * tr["w_results"] * rw * 3.2 \
            - c["loss_pen"] * tr["w_results"]
        if c["darling"]: v += c["darling"] * tr.get("w_l6", 1.0) * pw
        if style == "offense": v += (c["ppg"] - 28.0) * 0.9 * rw
        elif style == "defense": v += (20.0 - c["papg"]) * 0.9 * rw
        if tr.get("regional") and c["state"] == home_state and t != team: v += tr["regional"]
        if t == team: v += tr["homer"]
        elif t in voter["rivals"]: v += tr["rival"] * 1.5
        elif t in conf_mates: v += tr["conf"] + tr["rival"] * 0.4
        if tr["contrarian"] and consensus_prev.get(t, 99) <= 5: v -= tr["contrarian"]
        v += rng.gauss(0, tr["noise"] * max(0.4, 1 - meta["played"] * 0.05))
        score[t] = v
    # HEAD TO HEAD (Dan, 2040 week 1): every voter respects it a little. Where this
    # ballot would put a team above one that beat it this season, the two are nudged
    # toward each other -- a small, flat push, the same for every voter, so a one-score
    # loss on the road doesn't flip a ballot but a close call usually does.
    for w, l in meta.get("h2h", []):
        if w in score and l in score and score[l] > score[w]:
            score[w] += H2H_NUDGE; score[l] -= H2H_NUDGE
    # the weekly surprise: one team from outside the consensus top 20 (a different one
    # whenever it fires), lifted to somewhere between 12th and 24th on this ballot
    surprise_pick = None
    if tr["surprise"] and rng.random() < tr["surprise"]:
        ranked = sorted(score, key=lambda t: -score[t])
        outside = [t for t in ranked[20:70] if consensus_prev.get(t, 99) > 20 and t != team]
        if outside:
            surprise_pick = rng.choice(outside)
            slot = rng.randint(12, 24)
            score[surprise_pick] = score[ranked[slot - 1]] + 0.01
    if prev_ballot and meta["played"] >= 1:
        vals = sorted(score.values(), reverse=True); hi, lo = vals[0], vals[-1]; span = max(1e-6, hi - lo)
        pos = {t: i + 1 for i, t in enumerate(prev_ballot)}
        for t in score:
            if t == surprise_pick: continue        # the surprise is this week's whim, not inertia's
            p = pos.get(t, len(prev_ballot) + 8)
            pe = hi - span * (p - 1) / (len(prev_ballot) + 12)
            score[t] = (1 - tr["inertia"]) * score[t] + tr["inertia"] * pe
    top = sorted(score, key=lambda t: -score[t])[:25]
    if surprise_pick and surprise_pick not in top:
        top = top[:24] + [surprise_pick]
    return top, score


def compute_poll(s, db, seed=None):
    """The composite poll: (ranking [(rank, team)] top 40, points dict)."""
    season = s.get("season", 1)
    key = "media_pool_s%d" % season
    if not s.get(key):
        s[key] = make_pool(s)
    voters = s[key]
    rng = random.Random(seed if seed is not None else 4040 + season * 131 + s.get("next_week", 0) * 7)
    comp, meta = team_components(s, db)
    consensus_prev = {t: r for r, t in (s.get("media_poll_current") or [])}
    prevs = s.get("media_voter_prev") or {}
    ballots, points, mean_score = {}, collections.Counter(), collections.Counter()
    firsts = collections.Counter()
    for v in voters:
        top, sc = vote(v, comp, meta, consensus_prev, prevs.get(v["id"]), rng)
        ballots[v["id"]] = top
        for i, t in enumerate(top): points[t] += PTS[i + 1]
        firsts[top[0]] += 1
        for t, x in sc.items(): mean_score[t] += x / len(voters)
    order = sorted(E.U["teams"], key=lambda t: (-points[t], -firsts[t], -mean_score[t]))[:40]
    s["media_voter_prev"] = ballots
    s.setdefault("media_ballots", {})[s.get("next_week", 0)] = ballots
    s["media_points_current"] = {t: p for t, p in points.items() if p > 0}   # everyone who got a vote
    s["media_firsts_current"] = dict(firsts)
    return [(i + 1, t) for i, t in enumerate(order)], dict(mean_score)
