"""Roiland Sports Network's "Morning Gameview" -- where the show sets up this week.

Dan, 2040 week 0: before each week, offer a few candidates for game of the week. The
show tries not to visit the same campus twice in a season, so a campus with a bigger
game later in the year is passed over now even when its game this week is good.

  python3 gameview.py <week>              candidates for the week
  python3 gameview.py pick <week> <host>  record where the show went

Game quality is built from the ranking of record (committee once it exists, media
before), records, rivalry and conference flags. The look-ahead uses the current
ranking for games not yet played, which is the best anyone can do in August.
State: s['gameview'] = {week: {"host": ..., "away": ...}}
ROLLOVER NOTE (2041): the visit list is per season -- archive it as gameview_s<N> and clear it at
rollover, or the look-ahead penalties carry last year's road trip into the new year (bitten 2041).
"""
import sys, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E

UNRANKED = 40


def ranking(s):
    if s.get("committee_official") and s.get("committee_poll_current"):
        return {t: r for r, t in s["committee_poll_current"] if r <= 25}
    return {t: r for r, t in (s.get("media_poll_current") or []) if r <= 25}


def quality(rk, rec, h, a, wk, rival):
    """Higher is better. Two top-ten teams ~ 60+; a ranked-vs-unranked ~ 25-35."""
    rh, ra = rk.get(h, UNRANKED), rk.get(a, UNRANKED)
    q = (UNRANKED - min(rh, UNRANKED)) + (UNRANKED - min(ra, UNRANKED))
    q += 10 if max(rh, ra) <= 10 else 0           # both top ten
    q += 6 if max(rh, ra) <= 25 else 0            # both ranked
    for t in (h, a):
        r = rec.get(t, {}); gp = r.get("W", 0) + r.get("L", 0)
        if gp and r.get("L", 0) == 0: q += 3     # unbeaten
    if rival: q += 8
    if wk == 14: q += 3
    return q


def games_by_week(s):
    out = collections.defaultdict(list)
    T = set(E.U["teams"])
    rivals = set()
    for p in E.U["fixed_pairs"]:
        rivals.add(frozenset((p["team_a"], p["team_b"])))
    for wk, h, a, ic in s["sched"]:
        if h in T and a in T:
            out[wk].append({"w": wk, "host": h, "away": a, "conf": bool(ic),
                            "rival": frozenset((h, a)) in rivals})
    return out


def candidates(s, week, n=4):
    rk = ranking(s); rec = s["record"]
    gw = games_by_week(s)
    visits = s.get("gameview") or {}
    visited = {v["host"] for v in visits.values()}
    played = {wk for wk, _g in (s.get("results") or [])}
    # best future game at each campus, on today's ranking
    future_best = collections.defaultdict(float)
    for wk, gl in gw.items():
        if wk <= week: continue
        for g in gl:
            future_best[g["host"]] = max(future_best[g["host"]], quality(rk, rec, g["host"], g["away"], wk, g["rival"]))
    rows = []
    for g in gw.get(week, []):
        q = quality(rk, rec, g["host"], g["away"], week, g["rival"])
        notes = []
        adj = q
        if g["host"] in visited:
            adj -= 25; notes.append("already visited %s" % g["host"])
        fb = future_best.get(g["host"], 0)
        if fb > q + 4:
            adj -= min(12, (fb - q) * 0.6)
            notes.append("bigger game at %s later" % g["host"])
        rows.append(dict(g, q=q, adj=adj, notes=notes,
                         rh=rk.get(g["host"]), ra=rk.get(g["away"])))
    rows.sort(key=lambda r: -r["adj"])
    return rows[:n], rows


def outlook(s, t, week, rk):
    """Record, conference place, and the rest of the schedule read as an expected finish.

    Dan, 2041 wk 7: candidates come with each team's record and outlook. The outlook is
    the remaining games (this week's included) summed as win probabilities -- a projection,
    the same arithmetic as the preseason page -- plus who is still to come and where the
    team sits in its conference. No ratings on the page, as always.
    """
    import subdivision as _SUB
    _SUB.register(E)
    U = E.U; T = set(U["teams"]); rec = s["record"]
    r = rec[t]; conf = U["team_conf"][t]
    left = []
    for wk, h, a, ic in s["sched"]:
        if wk < week or t not in (h, a): continue
        home = h == t; opp = a if home else h
        pw = SE.win_prob(s, t if home else opp, opp if home else t, site="home")
        left.append({"w": wk, "opp": opp, "home": home, "p": pw if home else 1 - pw,
                     "sub": opp not in T, "rk": rk.get(opp)})
    left.sort(key=lambda g: g["w"])
    exp = sum(g["p"] for g in left)
    pw_, pl_ = r["W"] + exp, r["L"] + len(left) - exp
    # conference standing by conference record
    members = [x for x in T if U["team_conf"][x] == conf]
    order = sorted(members, key=lambda x: (-(rec[x]["confW"] - rec[x]["confL"]), -rec[x]["confW"], -rec[x]["W"]))
    place = order.index(t) + 1
    lead = rec[order[0]]
    gb = ((lead["confW"] - lead["confL"]) - (r["confW"] - r["confL"])) / 2
    ranked_left = [g for g in left if g["rk"]]
    nxt = ", ".join(("#%d " % g["rk"] if g["rk"] else "") + ("" if g["home"] else "@") + g["opp"]
                    for g in left[1:4])
    bits = ["%d-%d (%d-%d %s, %s%s)" % (r["W"], r["L"], r["confW"], r["confL"], conf,
            {1: "1st", 2: "2nd", 3: "3rd"}.get(place, "%dth" % place),
            "" if gb <= 0 else ", %g back" % gb)]
    bits.append("projects %.1f-%.1f" % (pw_, pl_))
    bits.append("%d left, %d vs ranked" % (len(left), len(ranked_left)))
    if nxt: bits.append("then " + nxt)
    return "; ".join(bits)


def fmt(r, rec):
    def tag(t, rnk):
        w = rec.get(t, {}); return ("#%d " % rnk if rnk else "") + t + " (%d-%d)" % (w.get("W", 0), w.get("L", 0))
    line = "%s at %s" % (tag(r["away"], r["ra"]), tag(r["host"], r["rh"]))
    if r["rival"]: line += "  [rivalry]"
    if r["notes"]: line += "   -- " + "; ".join(r["notes"])
    return line


def pick(s, week, host):
    gw = games_by_week(s)
    g = next((x for x in gw.get(week, []) if x["host"] == host), None)
    if not g:
        raise SystemExit("no game hosted by %s in week %d" % (host, week))
    s.setdefault("gameview", {})[week] = {"host": host, "away": g["away"]}
    SE.save_state(s)
    return g


if __name__ == "__main__":
    s = SE.load_state()
    if sys.argv[1] == "pick":
        g = pick(s, int(sys.argv[2]), " ".join(sys.argv[3:]))
        print("Gameview week %d: %s at %s" % (int(sys.argv[2]), g["away"], g["host"]))
    else:
        wk = int(sys.argv[1])
        top, allrows = candidates(s, wk)
        print("Morning Gameview candidates, week %d:" % wk)
        rk = ranking(s)
        for i, r in enumerate(top, 1):
            print("  %d. %s" % (i, fmt(r, s["record"])))
            for t in (r["away"], r["host"]):
                print("        %-20s %s" % (t + ":", outlook(s, t, wk, rk)))
        skipped = [r for r in allrows[len(top):] if r["q"] >= (top[-1]["q"] if top else 0)]
        if skipped:
            print("  passed over this week:")
            for r in skipped[:3]: print("     %s" % fmt(r, s["record"]))
        v = s.get("gameview") or {}
        if v: print("  visited so far:", ", ".join("wk %s %s" % (k, x["host"]) for k, x in sorted(v.items())))
