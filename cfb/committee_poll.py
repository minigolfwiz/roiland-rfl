"""The weekly committee ranking, anchored on Dan's ballot.

Dan ranks the top 25 himself at the first reveal. Every week after that, this carries HIS
board forward rather than recomputing from scratch — which is how a real committee works:
they argue from last week's list and move teams on what just happened, they do not
re-derive the whole thing from a rating every Tuesday.

Three inputs per team:
  * where Dan (or last week's committee) had them — weighted heaviest
  * where the engine's own resume ranking has them, which is what lets a team Dan left off
    climb into the picture on merit
  * what they actually did this week, which is what moves anybody at all

A team that does not play holds its place. A ranked team that loses falls, and falls
much further for losing to somebody poor. Beating a highly ranked team is the only way
to move up a long way in one week.
"""
import sys, collections
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E, committee as CM

U = E.U
TEAMS = list(U["teams"])
TSET = set(TEAMS)

INERTIA = 0.72          # how much of last week's board survives


def _points(prior, eng_rank):
    """Seed every team with a starting score: ranked teams from their place on the board,
    everyone else from the engine, pitched to sit just below the ballot."""
    pri = {}
    for i, t in enumerate(prior):
        pri[t] = 100.0 - i * 2.5                    # 1st = 100, 25th = 40
    for t in TEAMS:
        if t not in pri:
            r = eng_rank.get(t, 152)
            pri[t] = max(0.0, 38.0 - (r - 1) * 0.45)
    return pri


def weekly(state, db, prior, week):
    """Return the new top 25 plus a per-team note of what moved them."""
    ranked, scores, eff = CM.committee_rank(state, db)
    eng_rank = {t: i + 1 for i, t in enumerate(ranked)}
    prior_rank = {t: i + 1 for i, t in enumerate(prior)}
    pri = _points(prior, eng_rank)

    # what each team did this week
    result = {}
    for wk, gid in state["results"]:
        if wk != week:
            continue
        b = db.get(gid)
        if not b:
            continue
        for t, opp in ((b["home"], b["away"]), (b["away"], b["home"])):
            if t not in TSET:
                continue
            won = (b["home"] == t) == (b["home_score"] > b["away_score"])
            margin = (b["home_score"] - b["away_score"]) * (1 if b["home"] == t else -1)
            result[t] = {"won": won, "opp": opp, "margin": margin,
                         "oppPrior": prior_rank.get(opp),
                         "oppEng": eng_rank.get(opp) if opp in TSET else None}

    delta, why = {}, {}
    for t in TEAMS:
        r = result.get(t)
        if not r:
            delta[t] = 0.0
            why[t] = "idle"
            continue
        op, oe = r["oppPrior"], r["oppEng"]
        # Polls are driven by LOSSES. Wins move a team a little; a loss is what actually
        # reorders the board, and losing to somebody poor is what buries a team. Keeping
        # the win side small also stops an idle team bleeding out of the rankings just
        # because everyone below it played.
        if r["won"]:
            if op:
                d = 3.0 + (26 - op) * 0.22          # beating the #1 team is worth ~+8.5
                w = "beat #%d %s" % (op, r["opp"])
            elif oe is None:
                d = 0.2
                w = "beat a subdivision guest"
            elif oe <= 50:
                d = 1.6
                w = "beat %s" % r["opp"]
            else:
                d = 0.8
                w = "beat %s" % r["opp"]
            if r["margin"] >= 21:
                d += 0.5
        else:
            if op:
                d = -(13.0 + (26 - op) * 0.25)      # a top-5 loss costs 7-8 places
                w = "lost to #%d %s" % (op, r["opp"])
            elif oe is None:
                d = -40.0
                w = "LOST TO A SUBDIVISION GUEST"
            elif oe <= 60:
                d = -20.0
                w = "lost to %s" % r["opp"]
            else:
                d = -27.0
                w = "lost to %s, outside the top 60" % r["opp"]
            if r["margin"] <= -21:
                d -= 3.0
        delta[t] = d
        why[t] = w

    final = {}
    for t in TEAMS:
        eng_pts = 100.0 - (eng_rank[t] - 1) * 0.60
        final[t] = INERTIA * pri[t] + (1 - INERTIA) * eng_pts + delta[t]

    order = sorted(TEAMS, key=lambda t: (-final[t], t))
    top = order[:25]

    # A committee does not drop an undefeated team out of the rankings. Where one has been
    # squeezed out by everybody below it winning, it takes the place of the lowest-ranked
    # team carrying two or more losses. It keeps its computed position otherwise, so this
    # protects a perfect record without overriding how highly anyone rates the schedule.
    rec = state["record"]
    unbeaten = [t for t in TEAMS if rec[t]["L"] == 0 and rec[t]["W"] >= 5 and t not in top]
    for t in unbeaten:
        swap = next((x for x in reversed(top) if rec[x]["L"] >= 2), None)
        if swap is None:
            break
        top[top.index(swap)] = t
        top.sort(key=lambda x: -final[x])
    moves = []
    for i, t in enumerate(top):
        was = prior_rank.get(t)
        moves.append({"rank": i + 1, "team": t, "was": was,
                      "move": (was - (i + 1)) if was else None, "why": why[t]})
    dropped = [t for t in prior if t not in top]
    return top, moves, dropped


def render(moves, dropped, state, week, year):
    rec = state["record"]
    out = ["=== COMMITTEE RANKING · AFTER WEEK %d · %d ===" % (week, year), ""]
    for m in moves:
        t = m["team"]; r = rec[t]
        mv = "  NEW" if m["was"] is None else ("   —" if m["move"] == 0 else "%+4d" % m["move"])
        out.append("  %2d. %-22s %2d-%-2d %s   %s"
                   % (m["rank"], t, r["W"], r["L"], mv, m["why"]))
    if dropped:
        out.append("")
        out.append("  dropped out: " + ", ".join(dropped))
    return "\n".join(out)
