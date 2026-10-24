"""Special teams as a real phase for the Roiland CFB engine.

Adds, on top of the basic punt/FG the engine already had:
  - Punts with a real net + hang time, coverage, and a live RETURN (yards, occasional TD)
  - Punt blocks and muffed punts (turnovers)
  - Kickoff returns (yards + occasional TD) and touchbacks
  - Onside kicks (recovery odds keyed to situation)
  - Fake punts / fake FGs (rare, coach-aggression driven)
  - Blocked field goals

All functions are pure-ish helpers that take the game's rng and the kicking/receiving
TeamGame objects and return structured results the engine applies. Kicker/punter quality
(leg, accy) and returner speed drive the outcomes, so investing in specialists matters.

Weather is passed in as a dict {wind, precip, cold, dome} and dampens kicking.
"""

# ---- helpers -------------------------------------------------------------

def _leg(p): return p.get("attrs", {}).get("leg", p.get("abil", 5.0)) if p else 4.0
def _accy(p): return p.get("attrs", {}).get("accy", p.get("abil", 5.0)) if p else 4.0
def _spd(p): return p.get("attrs", {}).get("speed", p.get("abil", 5.0)) if p else 5.0


def best_returner(team_game):
    """Fastest skill player available to return kicks/punts."""
    pool = (getattr(team_game, "wrs", []) or []) + (getattr(team_game, "rbs", []) or []) \
        + (getattr(team_game, "cbs", []) or [])
    pool = [p for p in pool if p]
    if not pool:
        return None
    return max(pool, key=_spd)


def punt(rng, kicking, receiving, spot, weather=None):
    """Return a dict describing a punt outcome.
    keys: type ('punt'|'block'|'muff'|'fake_run'|'return_td'), net, ret, new_spot (offense-relative
    for the receiving team = yards from THEIR own goal), turnover(bool), punter, returner, ret_yards.
    spot = kicking team's yard line (0-100, their own goal = 0)."""
    weather = weather or {}
    p = kicking.punter()

    # --- block chance (rushed punt) ---
    if rng.random() < 0.010:
        return {"type": "block", "turnover": True, "punter": p,
                "new_spot": max(1, min(99, spot + rng.randint(-3, 8)))}

    # --- net punt distance (leg + hang), weather-dampened ---
    leg = _leg(p)
    base = 41.0 + (leg - 5) * 2.1
    wind_pen = weather.get("wind", 0) * 1.3
    net = rng.gauss(base - wind_pen, 5.5)
    net = max(20, min(70, net))

    landing = spot + net  # absolute field position of the catch (from kicking team's goal)
    if landing >= 100:  # touchback
        return {"type": "punt", "net": int(net), "ret": 0, "punter": p,
                "new_spot": 20, "turnover": False, "returner": None, "ret_yards": 0}

    # --- muffed punt (receiving team fumbles the catch) ---
    if rng.random() < 0.007:
        return {"type": "muff", "turnover": True, "punter": p,
                "new_spot": int(100 - landing) + rng.randint(-2, 2)}

    # --- return ---
    r = best_returner(receiving)
    fair_catch = rng.random() < 0.34  # many punts are fair-caught
    ret_yards = 0
    if not fair_catch and r:
        ret_yards = max(0, int(rng.gauss(8 + (_spd(r) - 5) * 1.6, 7)))
        # occasional house call: fast returner takes it back
        house_p = min(0.004, 0.0012 + _spd(r) * 0.0004)
        if rng.random() < house_p:
            return {"type": "return_td", "net": int(net), "ret": r, "punter": p,
                    "ret_yards": int(100 - (100 - landing)), "turnover": False,
                    "new_spot": None, "return_td": True}
    catch_spot = 100 - landing  # receiving team's own yard line at the catch
    new_spot = min(99, catch_spot + ret_yards)
    return {"type": "punt", "net": int(net), "ret": ret_yards, "punter": p,
            "new_spot": int(new_spot), "turnover": False, "returner": r if ret_yards else None,
            "ret_yards": int(ret_yards)}


def fake_punt(rng, kicking, coach_agg):
    """Rare fake punt attempt; returns True/False on whether to attempt."""
    return rng.random() < 0.004 * (0.5 + coach_agg)


def kickoff_return(rng, kicking, receiving, weather=None):
    """Return (new_spot, return_td_player_or_None). new_spot = receiving team's own yard line."""
    weather = weather or {}
    # touchback likelihood (strong-legged kickers + no wind)
    k = kicking.kicker()
    tb_p = 0.62 + (_leg(k) - 5) * 0.03 - weather.get("wind", 0) * 0.02
    if rng.random() < max(0.35, min(0.85, tb_p)):
        return 25, None
    r = best_returner(receiving)
    ret = max(0, int(rng.gauss(23 + (_spd(r) - 5) * 1.7, 9))) if r else 22
    start = max(1, min(40, ret))
    # kickoff return TD (rare)
    house_p = min(0.010, 0.002 + (_spd(r) - 5) * 0.0011) if r else 0
    if rng.random() < house_p:
        return None, r   # signals a return TD
    return start, None


def onside_kick(rng, kicking, trailing_and_late):
    """Onside kick. Returns dict {recovered_by_kicking(bool), spot}.
    Surprise onsides are rare; desperation onsides (late & trailing) succeed ~20-25%."""
    if trailing_and_late:
        recovered = rng.random() < 0.22
    else:
        recovered = rng.random() < 0.13  # surprise onside
    spot = rng.randint(45, 55)  # onsides travel ~10-15 yards
    return {"recovered_by_kicking": recovered, "spot": spot}


def fg_block(rng, kicking, dist):
    """Chance a field goal is blocked (rises with distance/bad line)."""
    return rng.random() < min(0.03, 0.008 + max(0, dist - 45) * 0.0012)


# ---- 4th down decision analytics -----------------------------------------

def fourth_down_decision(rng, spot, dist, q, clock, margin, coach_agg, k_leg, ot=False,
                         def_timeouts=3, own_timeouts=3):
    """Decide go / punt / field_goal on 4th down.

    2035 endgame overhaul. The old version judged late downs by a flat five-minute
    window and a hardcoded list of margins, which meant it could not tell a one-score
    deficit from a two-score one and ignored whether the clock could even be stopped.
    It now reasons about HOW MANY SCORES the team is behind and how much clock the
    trailing side can still preserve with timeouts.

    spot = offense yard line (0-100, own goal=0; opponent goal=100).
    Returns one of 'go', 'punt', 'field_goal'.
    """
    fg_dist = (100 - spot) + 17
    makeable = fg_dist <= min(60, 45 + (k_leg - 5) * 3.0)
    yards_to_go = dist
    time_left = clock + (0 if q >= 4 else (4 - q) * 900)

    # --- how many possessions is this, really? ---
    fg_ties_or_wins = -3 <= margin <= 0          # three points is enough
    need_td = margin <= -4                       # a field goal cannot catch up
    two_scores_down = margin <= -9               # even a TD leaves them behind
    # Roughly how long until they would need the ball back. A team that can stop the
    # clock has more real time than the game clock suggests.
    clock_power = def_timeouts if margin > 0 else own_timeouts
    urgency_window = 300 + (120 if two_scores_down else 0) - 25 * clock_power
    desperate = (q == 4 and clock < max(120, urgency_window) and margin < 0)
    ice_game = (q == 4 and clock < 300 and margin > 0)

    if ot:
        # In OT you never punt. A field goal only helps if it TIES or WINS: the branch
        # used to ignore the score entirely, so a team trailing by more than three would
        # kick a field goal that could not tie. Under the Roiland rule (two-point
        # conversion required from the first OT) an eight-point hole is the common case,
        # which made this frequent: 43 of canon's 389 overtime games ended on a futile
        # kick by the losing team. Found in the 2035 quarterfinal round; fixed forward.
        if margin < -3:
            return "go"
        if makeable and not (yards_to_go <= 2 and spot >= 60):
            return "field_goal"
        return "go"

    # --- trailing late ---
    if desperate:
        # A field goal that cannot tie is a wasted possession, however makeable.
        if need_td:
            return "go"
        if makeable and fg_ties_or_wins:
            # Inside the last minute, take the tie or the win from anywhere in range --
            # the old rule refused on 4th-and-short and kept playing for a touchdown.
            if clock <= 70:
                return "field_goal"
            # Earlier than that, a short fourth down is still worth the first down,
            # because there is time for the drive to reach a better kick.
            if yards_to_go > 3 or clock <= 150:
                return "field_goal"
        return "go"

    # --- protecting a lead late ---
    if ice_game:
        # Converting ends the game outright when the defense cannot stop the clock.
        can_run_it_out = def_timeouts == 0 and clock <= 130
        if yards_to_go <= 2 and spot >= 45 and can_run_it_out:
            return "go"
        if makeable and spot >= 60:
            return "field_goal"
        if yards_to_go <= 1 and spot >= 55:
            return "go" if rng.random() < 0.4 * coach_agg else "punt"
        return "punt"

    # normal-game analytics by field zone
    # deep in own territory: punt
    if spot < 40:
        # rare aggressive 4th-and-1 go
        if yards_to_go <= 1 and rng.random() < 0.12 * coach_agg:
            return "go"
        return "punt"

    # midfield (40-59): go on short, else punt; aggression matters a lot here
    if spot < 60:
        if yards_to_go <= 2:
            base = 0.45 + 0.4 * coach_agg
            return "go" if rng.random() < base else "punt"
        if yards_to_go <= 4:
            return "go" if rng.random() < 0.25 * coach_agg else "punt"
        return "punt"

    # opponent territory but outside comfy FG (60-67): the "no man's land"
    if spot < 68:
        if yards_to_go <= 3:
            return "go" if rng.random() < 0.55 + 0.35 * coach_agg else ("field_goal" if makeable else "punt")
        if makeable:
            return "field_goal"
        return "go" if rng.random() < 0.4 * coach_agg else "punt"

    # clear FG range (68+): short yardage sometimes goes, else kick
    if yards_to_go <= 1 and spot >= 75:
        return "go" if rng.random() < 0.35 * coach_agg else "field_goal"
    if makeable:
        return "field_goal"
    # too close to punt effectively, out of FG range somehow -> go
    return "go"
