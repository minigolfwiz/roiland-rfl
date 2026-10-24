"""Weekly media Top 40 — a deliberately biased human poll, separate from objective NET.
Over-weights: blueblood pedigree, on-paper rosters, star power, flashy win totals,
recency/ranked buzz, and the defending champ. Early season leans preseason bias;
as real games accrue, results pull it (slowly — voters are stubborn) toward reality."""
import sys, random, pickle, collections; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E

def compute_media_poll(s, db=None, seed=None):
    """From 2040 the poll is sixty named voters (media_pool.py); the old single-formula
    poll below is kept as `compute_media_poll_legacy` for the record."""
    if db is None:
        from games_db import load_db; db = load_db()
    import media_pool as MPL
    return MPL.compute_poll(s, db, seed=seed)


def compute_media_poll_legacy(s, db=None, seed=None):
    if db is None:
        from games_db import load_db; db = load_db()
    rng = random.Random(seed if seed is not None else (2026 + s.get("next_week",1)*7))
    prestige = E.U["prestige"]
    hist = s.get("history", {}); book = hist.get("book", {})
    # SEASON-AWARE (2035 rebuild fix): this block was hardcoded to Season 1, so from
    # Season 2 on the poll's "defending champion" bonus pointed at a stale archive and
    # the prior playoff field was empty. Both now follow the current season.
    seas = s.get("season", 1)
    # `s['archives']` has never existed in the rebuilt state; the rollover writes
    # `season_archive[str(season)]` with `standings`, not `records`. So "last season's
    # record" and "defending champion" were both reading an empty dict and contributing
    # nothing. Mapped onto the real archive. (2039 week 1.)
    _sa = (s.get("season_archive", {}) or {}).get(str(seas-1), {}) or {}
    arch = {"champion": _sa.get("champion"), "records": _sa.get("standings", {}) or {}}
    champ = arch.get("champion")
    if champ is None:                       # fall back to the canon champions ledger
        ch = s.get("history", {}).get("champ", {})
        last = 2025 + seas - 1
        ent = ch.get(last)
        if ent:
            champ = ent[0] if not isinstance(ent[0], tuple) else ent[0][0]
    runnerup = None
    ch = s.get("history", {}).get("champ", {})
    ent = ch.get(2025 + seas - 1)
    if ent and len(ent) > 1 and ent[1]:
        runnerup = ent[1]
    else:
        for gid, b in db.items():
            if gid == "S%dPO_CHAMP" % (seas-1):
                runnerup = b["away"] if b["home"] == champ else b["home"]
    po = {}
    for cand in ('state/playoff_s%d.pkl' % (seas-1), 'state/playoff_s1.pkl'):
        try:
            po = pickle.load(open('/home/claude/cfb2/' + cand, 'rb')); break
        except Exception:
            continue
    s1_field = set(po.get("field", []))

    # PEDIGREE WAS THE WHOLE POLL. This counted every title in the history book, and
    # since the 1929 canon was wired in (2038) that book runs 110 seasons: North Hatesei's
    # 21 titles were worth +142 points, with no fade, against a 2-0 start worth about
    # +44. A 0-2 preseason #1, beaten at home twice, stayed #1 -- which is how it was
    # found. Voters remember a generation, not a century: titles and finals inside the
    # last 25 years count, the total is capped, and it fades with the preseason weight
    # like every other reputation term.
    _year_now = 2025 + seas
    def pedigree(t):
        b = book.get(t, {})
        rec_t = sum(1 for y in b.get("titles", []) if _year_now - y <= 25)
        rec_r = sum(1 for y in b.get("runnerup", []) if _year_now - y <= 25)
        return min(12.0, rec_t*3 + rec_r*1.5 + len(b.get("playoff_app",[]))*0.5)
    # returning/paper talent & star power (recomputed each week; rosters may shift via injury)
    talent = {}; star = {}
    _fbs = set(E.U["teams"])
    for t, roster in E.ROSTERS.items():
        if t not in _fbs: continue      # subdivision guests are never polled
        avail = [pl for pl in roster if s.get("inj_out",{}).get(pl["pid"],0)==0]
        top = sorted((pl["abil"] for pl in avail), reverse=True)[:25]
        talent[t] = sum(top)/max(1,len(top))
        star[t] = max((pl["abil"] for pl in avail), default=5)

    _pfx = f"S{s.get('season',1)}W"
    # WEEKS PLAYED. This was `next_week - 1`, which assumes the calendar opens at week 1.
    # It has opened at week 0 since 2035, so the poll ran one week behind all along:
    # after week 0 it believed nothing had been played and ignored every result, and the
    # result weight was a week short for the rest of the year. Found 2039 week 1 when a
    # 0-2 North Hatesei, beaten at home twice, was still ranked #1. Counted from the
    # results now, so it is right whatever week the calendar opens on.
    wk = s.get("next_week",1)
    played = len({w for w, _g in (s.get("results") or [])})
    rec = s["record"]
    net = SE.net_ratings(s, db) if played >= 1 else None

    media = {}
    for t in E.U["teams"]:
        r = rec[t]; gp = r["W"]+r["L"]
        score = 0.0
        score += prestige[t]*0.9
        # PRESEASON bias fades as real games accrue
        preseason_w = max(0.15, 1.0 - played*0.09)
        score += pedigree(t)*2.2*preseason_w
        score += talent[t]*5.5
        score += star[t]*3.0
        recency = arch.get("records",{}).get(t,{}).get("W",0)*1.6
        if t in s1_field: recency += 6
        if t == champ: recency += 22
        if t == runnerup: recency += 12
        score += recency * preseason_w
        # THIS SEASON results pull the poll (grows with games played); voters love wins & margin
        if played >= 1:
            wins = r["W"]; margin = (r["PF"]-r["PA"])
            result_w = min(1.0, played*0.16)
            cur = wins*9.0 + margin*0.30 + (net["em"][t]*0.8 if net else 0)
            if gp>0 and r["L"]==0: cur += 8            # undefeated flashy bonus
            # "quality loss" forgiveness: losing to a strong team, or being a pedigree program
            # expected to bounce back, barely dents you. Bad losses by hype teams hurt more.
            if r["L"] > 0 and net is not None:
                # find worst loss opponent strength via db scan
                opp_em_sum = 0.0; nlost = 0
                for bb in db.values():
                    if not bb.get("game_id","").startswith(_pfx): continue
                    if t not in (bb["home"], bb["away"]): continue
                    won = (bb["home"]==t) == (bb["home_score"]>bb["away_score"])
                    if not won:
                        opp = bb["away"] if bb["home"]==t else bb["home"]
                        opp_em_sum += net["em"].get(opp,0); nlost += 1
                avg_loss_opp = opp_em_sum/max(1,nlost)
                # forgiveness scales with opponent strength and own prestige (bounce-back faith)
                forgiveness = max(0, avg_loss_opp)*0.6 + (prestige[t]-55)*0.10
                cur += min(9, forgiveness)             # cushions the loss, never a bonus above ~parity
            if gp>0 and r["W"]==0 and prestige[t] < 60: cur -= 8   # only unpedigreed winless teams crater
            score += cur * result_w * 3.2
        score += rng.gauss(0, 4.5*max(0.4, 1-played*0.05))   # voter noise, shrinks a bit over year
        media[t] = score

    # ---- VOTER INERTIA (restored in the 2035 rebuild) ----
    # Real poll voters move their existing ballot rather than rebuilding it weekly. Blend
    # this week's raw score with last week's standing so movement is gradual: a ranked team
    # has to lose, or be passed, to fall far. Without this the poll is a ratings re-sort and
    # a 2-1 team can leap 27 spots in a week.
    prev = {t: r for r, t in (s.get("media_poll_current") or [])}
    if prev and played >= 1:
        vals = sorted(media.values(), reverse=True)
        hi, lo = (vals[0], vals[-1]) if vals else (1.0, 0.0)
        span = max(1e-6, hi - lo)
        INERTIA = 0.42
        for t in list(media):
            p = prev.get(t)
            # an unranked team is treated as just outside the published ballot
            pos = p if p is not None else (len(prev) + 8)
            prev_equiv = hi - (span * (pos - 1) / max(1, len(prev) + 12))
            media[t] = (1 - INERTIA) * media[t] + INERTIA * prev_equiv

    top40 = sorted(E.U["teams"], key=lambda t:-media[t])[:40]
    return [(i+1, t) for i,t in enumerate(top40)], media
