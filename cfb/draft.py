"""Season 1 -> 2 NFL-style draft. 7 rounds x 30 picks = 210 selections.
Draft stock blends true ability, production, class/age, and position value, with
scouting noise so the order is NOT a clean stat ranking. Early-entry declarations
are probabilistic: most stay, stars leave, and a few leave who shouldn't."""
import sys, random, pickle; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E

ROUNDS, PICKS = 7, 40   # Dan, 2040 postseason: drafts are 280 players from the 2041 draft on (40-team pro league). 2036-40 were 210.
def statistics_mean(v): return sum(v)/len(v) if v else 0.0
def statistics_pstdev(v):
    if len(v) < 2: return 1.0
    m = sum(v)/len(v); return (sum((x-m)**2 for x in v)/len(v))**0.5
# Positional premium. OL was MISSING entirely and fell to the 0.9 default -- the lowest
# of any position, below running back -- which is backwards: blockers are premium.
POS_VALUE = {"QB":1.18,"OL":1.10,"DL":1.08,"CB":1.07,"WR":1.06,"S":1.00,"LB":1.00,
             "TE":0.94,"RB":0.92,"ATH":0.90,"K":0.55,"P":0.50}

def prod_score(pos, st, pl=None):
    """Production grade for draft stock.

    OL and P produce no box-score statistics, so they used to score a flat 0.00 while
    every other position earned several points of production credit. Standardising
    within position does not rescue them, because a lineman with no production spread
    also rarely clears the early-declaration bar, so they fell out of the pool before
    the draft even started: 12 OL drafted in 2036 against canon's 32.

    The engine that tracked pass-protection and run-blocking grades died with the
    2035 reset, so blockers are scored from their blocking ATTRIBUTES instead. It is a
    proxy, not a stat line, and it is deliberately scaled below the skill positions'
    ceiling -- linemen do not have breakout statistical games.
    """
    if pos in ("OL", "P") and pl is not None:
        a = pl.get("attrs") or {}
        if pos == "OL":
            grade = (a.get("pblk", pl.get("abil", 5.0)) + a.get("rblk", pl.get("abil", 5.0))) / 2.0
            return max(0.0, (grade - 4.5) * 3.0)
        return max(0.0, (a.get("leg", pl.get("abil", 5.0)) - 4.5) * 1.2)
    if not st: return 0.0
    if pos=="QB": return st.get("PassYds",0)*0.010 + st.get("PassTD",0)*0.9 - st.get("INT",0)*0.8 + st.get("RushYds",0)*0.004
    if pos=="RB": return st.get("RushYds",0)*0.012 + (st.get("RushTD",0)+st.get("RecTD",0))*0.7 + st.get("RecYds",0)*0.006
    if pos in ("WR","TE"): return st.get("RecYds",0)*0.013 + st.get("RecTD",0)*0.9 + st.get("Rec",0)*0.05
    if pos in ("DL","LB"): return st.get("Sacks",0)*1.3 + st.get("Tackles",0)*0.05 + st.get("TFL",0)*0.3
    if pos in ("CB","S"): return st.get("INT_def",0)*1.6 + st.get("Tackles",0)*0.05 + st.get("PBU",0)*0.3
    if pos in ("K","P"): return st.get("FGMade",0)*0.4
    return 0.0

def schedule_strength(s):
    """Production discount by the competition it came against (Dan, 2040 draft).

    Draft stock graded a Low Sixteen stat line exactly like a Great Fourteen one, and
    the L6 share of picks climbed 62 -> 70 -> 80 of ~200 over three drafts (11 of 30
    first-rounders in the first 2040 run) against a real G5 share near 15-20%. Each
    programme's production is scaled by the mean Elo of the opponents it faced this
    season: factor = 1 + (opp_elo - league_mean) / SOS_SCALE, clamped to [0.65, 1.25].
    """
    import prestige as PR
    from games_db import load_db
    db = load_db()
    season = s.get("season", 1)
    elo = PR.elo_history(db, E.U["teams"], through=season)
    now = elo.get(season) or elo[max(elo)]
    mean = sum(now.values()) / max(1, len(now))
    opp = {t: [] for t in E.U["teams"]}
    for _wk, gid in s.get("results", []):
        b = db.get(gid)
        if not b: continue
        h, a = b["home"], b["away"]
        if h in opp: opp[h].append(now.get(a, SOS_GUEST_ELO))
        if a in opp: opp[a].append(now.get(h, SOS_GUEST_ELO))
    out = {}
    for t, v in opp.items():
        m = sum(v) / len(v) if v else mean
        out[t] = max(0.65, min(1.25, 1.0 + (m - mean) / SOS_SCALE))
    return out

SOS_SCALE = 300.0
SOS_GUEST_ELO = 1180.0

def run_draft(seed=770001):
    rng = random.Random(seed)
    s = SE.load_state()
    stats = s["season_stats"]
    # eligibility
    # DAN'S 2040 RULING: "RS" is a REDSHIRT FRESHMAN -- a player who sat out a year
    # and returns as a sophomore, which is what `rollover.py` has always said it is
    # (UP = {"Fr":"So", "RS":"So", ...}). It was listed here alongside Sr and RS5 as
    # eligibility-exhausted, which is the fifth-year reading, and the two modules had
    # been disagreeing silently since the rebuild: every redshirt in the league was
    # flagged as leaving after one year and rollover's RS->So promotion was dead code.
    # 854 players a cycle. "RS5" is the fifth-year class and stays here.
    #
    # FORWARD ONLY. The 2039 draft is canon as played, redshirts and all; this takes
    # effect from 2040.
    seniors = {"Sr","RS5"}            # out of eligibility -> auto draft-eligible
    upper = {"Jr","RS4"}
    # 1) raw talent index per player (ability + production), computed per position
    raw = {}
    per_pos = {}
    sos = schedule_strength(s)
    for team, roster in E.ROSTERS.items():
        for p in roster:
            stx = stats.get(p["pid"], {})
            r = 0.62*p["abil"] + 0.9*prod_score(p["pos"], stx, p) * sos.get(team, 1.0)
            raw[p["pid"]] = r
            per_pos.setdefault(p["pos"], []).append(r)
    # 2) within-position mean/std so an elite DL competes with an elite QB
    pos_mu = {pos: statistics_mean(v) for pos, v in per_pos.items()}
    pos_sd = {pos: (statistics_pstdev(v) or 1.0) for pos, v in per_pos.items()}
    GLOBAL_MU = 7.0   # common draft-grade midpoint
    pool = []
    for team, roster in E.ROSTERS.items():
        for p in roster:
            stx = stats.get(p["pid"], {})
            z = (raw[p["pid"]] - pos_mu[p["pos"]]) / pos_sd[p["pos"]]   # standardized within position
            grade = GLOBAL_MU + 1.35*z + (POS_VALUE.get(p["pos"],0.9)-1.0)*1.6  # positional premium modest
            scout = grade + rng.gauss(0, 1.1)          # scouting noise
            entry = {"pid":p["pid"],"name":p["name"],"team":team,"pos":p["pos"],
                     "cls":p["cls"],"abil":p["abil"],"prod":prod_score(p["pos"],stx,p),
                     "stock":scout,"base":grade}
            cls = p["cls"]
            if cls in seniors or cls == "Sr":
                entry["eligible"]=True; entry["declared"]=True; pool.append(entry)
            elif cls in upper or cls=="Jr":
                # juniors: high stock likely declares, else usually returns
                pdecl = 1/(1+2.71828**(-(scout-7.2)))    # logistic on stock
                pdecl = min(0.96, pdecl*1.05)
                if rng.random() < pdecl:
                    entry["eligible"]=True; entry["declared"]=True; entry["early"]=True; pool.append(entry)
            else:
                # DAN'S 2039 RULING: real eligibility. A player must be three years
                # removed from high school, so true freshmen and sophomores cannot
                # declare at all -- they are not in the pool, at any stock.
                #
                # This had been unruled since 2038, when 47 of 210 picks were Fr/So and
                # Barhold lost the freshman quarterback who had just taken it to the
                # national championship game. The 2039 board would have done the same
                # thing to Eona: Chiara Marshworth, the freshman who won the title, graded
                # 30th overall. Forward only -- every draft already played stays canon.
                pass
    # subdivision (lower-division, off-roster) sprinkle: ~8% of picks come from "FCS-like" schools
    fbs_board = sorted((e["stock"] for e in pool), reverse=True)
    cutoff = fbs_board[ROUNDS*PICKS - 1]   # stock of the ~210th FBS player
    n_sub = int(ROUNDS*PICKS*0.085)
    import json as _json, os as _os
    _subpath = '/home/claude/cfb2/state/subdivision_schools.json'
    if _os.path.exists(_subpath):
        SUBS = _json.load(open(_subpath))   # real subdivision schools (from RCBA universe)
    else:
        SUBS = ["Verano A&M","Hollowmere","Tinsdale","Cape Ferro","Wexley Poly","Grasmere St",
                "Duncart","Ilbridge","Malloran","Petrichor Col","Yasminka Tech","Osfeld",
                "Rundlecrest","Vanterpool","Ashkoro St","Bellchant","Northreef","Quillon"]
    from names_v2 import pick_name_v2
    import collections as _c
    used_names=set(); surname_usage=_c.defaultdict(int)
    for i in range(n_sub):
        bg_rng = rng
        nm = pick_name_v2(rng, used_names, surname_usage=surname_usage, surname_cap=2)[0]
        pos = rng.choices(list(POS_VALUE), weights=[POS_VALUE[p] for p in POS_VALUE])[0]
        # these are the vetted small-school draftees; give them stock in the drafted band,
        # most late (day 3), a couple higher. Calibrated to the FBS pick cutoff.
        tier = rng.random()
        if tier < 0.15:   stock = rng.gauss(cutoff+0.6, 0.4)   # day-2 riser
        elif tier < 0.55: stock = rng.gauss(cutoff+0.15, 0.3)  # solid day-3
        else:             stock = rng.gauss(cutoff-0.1, 0.35)  # fringe, may not stick
        pool.append({"pid":f"SUB_{i}","name":nm,"team":rng.choice(SUBS),"pos":pos,
                     "cls":"Sr","abil":round(rng.uniform(6.0,8.2),1),"prod":0.0,
                     "stock":stock,"base":stock,"declared":True,"eligible":True,"subdivision":True})
    # board: sort by stock, add per-pick jitter so it's not monotonic
    board = sorted(pool, key=lambda e:-e["stock"])
    picks = []
    overall = 0
    available = board[:]
    for rnd in range(1, ROUNDS+1):
        for pk in range(1, PICKS+1):
            overall += 1
            # teams look at top of board but with a reach/slide window
            window = available[:(4 + rnd*2)]   # window widens later; more surprises on day 3
            if not available: break
            weights = [max(0.05, w["stock"] + rng.gauss(0,0.6)) for w in window]
            chosen = rng.choices(window, weights=[max(0.01,x) for x in weights])[0]
            available.remove(chosen)
            picks.append({"overall":overall,"round":rnd,"pick":pk, **chosen})
    return s, picks, pool

if __name__ == "__main__":
    s, picks, pool = run_draft()
    early = [p for p in picks if p.get("early")]
    subs = [p for p in picks if p.get("subdivision")]
    reaches = [p for p in picks if p.get("reach")]
    print(f"pool: {len(pool)} declared | picks: {len(picks)} | early entrants drafted: {len(early)} | subdivision: {len(subs)} | questionable early declares drafted: {len(reaches)}")

def mark_departures(s, picks, pool, seed=99880):
    """Flag every player leaving college, so roster finalisation can clear them out.

    Rebuilt for 2036 -- the original died with the 2035 reset. Three groups leave:

      * seniors (and RS seniors), whose eligibility is gone whether drafted or not
      * any underclassman who was actually drafted
      * a minority of undrafted early entrants who leave anyway

    The large majority of undrafted early entrants WITHDRAW and return to school, which
    is what keeps an early-declaration year from gutting rosters. Players are flagged
    with `_leaving` rather than deleted here, so the roster stage owns the removal and
    the ledger stays auditable.
    """
    rng = random.Random(seed)
    drafted = {p["pid"] for p in picks}
    declared_early = {e["pid"] for e in pool
                      if e["cls"] not in ("Sr", "RS", "RS5") and e.get("declared")}
    SENIOR = ("Sr", "RS5")        # see the eligibility note in run_draft: RS returns

    leaving, withdrew = set(), []
    for t, roster in E.ROSTERS.items():
        for pl in roster:
            pid = pl["pid"]
            if pl["cls"] in SENIOR:
                leaving.add(pid)                       # eligibility exhausted
            elif pid in drafted:
                leaving.add(pid)                       # went pro early
            elif pid in declared_early:
                if rng.random() < 0.85:
                    withdrew.append((pl["name"], t, pl["pos"]))   # returns to school
                else:
                    leaving.add(pid)

    for t, roster in E.ROSTERS.items():
        for pl in roster:
            if pl["pid"] in leaving:
                pl["_leaving"] = True

    s["departures_s%d" % s.get("season", 1)] = {
        "n": len(leaving), "drafted": len(drafted), "withdrew": len(withdrew)}
    E.persist_rosters()
    SE.save_state(s)
    return leaving, withdrew
