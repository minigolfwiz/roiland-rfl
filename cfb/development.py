"""Offseason player development.

Rebuilt for 2036. The version inside offseason.py grew players purely on class and
headroom -- coaching had no effect whatsoever, which cannot be right in a sport whose
whole offseason drama is who hired whom. Canon ran a coach-driven model with a
correlation around +0.49 between a staff's quality and how much its roster improved.

Each player grows toward his CEILING, at a rate set by his class, multiplied by the
quality of the staff actually responsible for him: the offensive coordinator develops
the offense, the defensive coordinator the defense, and the head coach contributes to
both. That is what makes a coordinator raid matter a year later.
"""
import sys, random, statistics, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E

U = E.U
TEAMS = U["teams"]
OFFENSE = {"QB", "RB", "WR", "TE", "OL"}

# growth by class, before coaching and headroom
# Calibrated against canon's class means (Fr +0.518, So +0.251, Jr +0.125, Sr 0.000)
# using the measured headroom of each class and the average staff multiplier.
GROW = {"Fr": 0.368, "So": 0.232, "Jr": 0.172, "Sr": 0.0, "RS": 0.205}


def coach_mult(team, pos):
    """How much this staff is worth to this player.

    The coordinator on his side of the ball carries most of the weight; the head coach
    sets the floor for the whole program. Returns roughly 0.85 for a poor staff and
    1.35 for an elite one.
    """
    st = E.COACHES.get(team, {})
    hc = st.get("HC", {}).get("skill", 5.0)
    unit = st.get("OC" if pos in OFFENSE else "DC", {}).get("skill", 5.0)
    staff = 0.42 * hc + 0.58 * unit
    return round(max(0.72, min(1.45, 0.715 + staff * 0.0735)), 3)


def run_development(seed=66020):
    rng = random.Random(seed)
    s = SE.load_state()
    deltas, by_class, by_team = [], collections.defaultdict(list), collections.defaultdict(list)
    breakouts, busts = [], []

    # Players flagged `_leaving` are seniors and drafted underclassmen; stage 6 deletes
    # them. They used to be developed anyway -- 2,850 of the 9,810 in 2038 -- which was
    # pointless work and, worse, it was what made `r_coach` lie, because they all grow
    # exactly 0.0 and a team's share of them has nothing to do with its staff.
    by_team_cls = collections.defaultdict(lambda: collections.defaultdict(list))
    for t in TEAMS:
        for pl in E.ROSTERS[t]:
            if pl.get("freshman"):          # incoming class develops next offseason
                continue
            if pl.get("_leaving"):          # gone in stage 6; do not develop or count
                continue
            cls = pl.get("cls", "So")
            base = GROW.get(cls, 0.03)
            if base <= 0:
                pl["rep"] = pl.get("rep", 0.0) * 0.5
                deltas.append(0.0); by_class[cls].append(0.0); by_team[t].append(0.0)
                continue
            ceiling = pl.get("pot", pl["abil"] + 0.6)
            head = max(0.0, ceiling - pl["abil"])
            m = coach_mult(t, pl["pos"])
            # growth is proportional to the room left: a player at his ceiling stops
            # Two channels. The multiplicative one scales a player's own remaining room;
            # the flat one is the staff's direct contribution, which keeps the coaching
            # signal from being drowned out by how much headroom a roster happens to
            # have. Without it the correlation came out at +0.17 against canon's +0.51.
            g = rng.gauss(base * head * m + (m - 1.0) * 0.165, 0.17)
            # the tails: a rare player outgrows his projection, a rare one regresses
            if rng.random() < 0.016:
                g += rng.uniform(0.35, 1.05)
                pl["pot"] = round(min(9.95, ceiling + rng.uniform(0.2, 0.7)), 2)
            elif rng.random() < 0.012:
                g -= rng.uniform(0.25, 0.70)
            g = max(-0.55, g)
            new = round(max(1.2, min(9.95, pl["abil"] + g)), 2)
            real = round(new - pl["abil"], 3)
            pl["abil"] = new
            pl["rep"] = pl.get("rep", 0.0) * 0.5
            deltas.append(real); by_class[cls].append(real); by_team[t].append(real)
            by_team_cls[cls][t].append(real)
            if real >= 0.80:
                breakouts.append({"name": pl["name"], "team": t, "pos": pl["pos"],
                                  "cls": cls, "jump": real, "abil": new})
            elif real <= -0.30:
                busts.append({"name": pl["name"], "team": t, "pos": pl["pos"], "drop": real})

    # Correlation between staff quality and how much a roster actually improved.
    #
    # THE OLD NUMBER WAS A COMPOSITION ARTEFACT, not a measure of coaching. Growth is
    # set almost entirely by class (Fr ~0.50, So ~0.20, Jr ~0.11, Sr 0.0), so a team's
    # mean growth mostly reports its class mix: in 2038 the share of a roster that was
    # seniors correlated with team "development" at -0.392, about as strongly as
    # coaching did. The headline fell 0.609 -> 0.566 -> 0.170 across three cycles and
    # none of that was the engine getting worse.
    #
    # It is reported WITHIN CLASS now, which removes composition entirely. On 2038's
    # data that gave Fr +0.437, So +0.376, Jr +0.219 -- a healthy, intact coaching
    # signal that the single league number was hiding. `r_coach` is kept as the
    # all-class figure for continuity with s10-s12, but `r_coach_by_class` is the one
    # to read. This changes no simulation output, only what the number means.
    def _corr(pairs):
        if len(pairs) < 3:
            return None
        xs = [a for a, _b in pairs]; ys = [b for _a, b in pairs]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        den = (sum((a - mx) ** 2 for a in xs) ** .5) * (sum((b - my) ** 2 for b in ys) ** .5)
        return round(num / den, 3) if den else 0.0

    r = _corr([(coach_mult(t, "QB"), statistics.mean(v))
               for t, v in by_team.items() if len(v) > 25]) or 0.0
    r_by_class = {}
    for cls, teams in by_team_cls.items():
        if GROW.get(cls, 0.03) <= 0:
            continue                       # a class that cannot grow carries no signal
        rc = _corr([(coach_mult(t, "QB"), statistics.mean(v))
                    for t, v in teams.items() if len(v) >= 5])
        if rc is not None:
            r_by_class[cls] = {"r": rc, "teams": sum(1 for v in teams.values() if len(v) >= 5),
                               "mean": round(statistics.mean(
                                   [x for v in teams.values() for x in v]), 3)}

    summary = {
        "n": len(deltas), "mean": round(statistics.mean(deltas), 3),
        "by_class": {k: round(statistics.mean(v), 3) for k, v in by_class.items()},
        "r_coach": r, "r_coach_by_class": r_by_class,
        "breakouts": len(breakouts), "busts": len(busts),
        "team_means": {t: round(statistics.mean(v), 3) for t, v in by_team.items() if v},
    }
    s["development_s%d" % s.get("season", 1)] = summary
    E.persist_rosters()
    SE.save_state(s)
    return summary, breakouts, busts


if __name__ == "__main__":
    summ, b, z = run_development()
    print(summ["n"], summ["mean"], summ["by_class"], "r=", summ["r_coach"])
