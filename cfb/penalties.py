"""Penalty system for the Roiland CFB engine.

Models the standard NCAA penalty set with realistic per-play rates, modulated by
per-player 'discipline' traits and per-team 'team_discipline' factors. Two hook points:
  - pre_snap_penalty(): false start / offside / encroachment / delay / illegal formation / illegal sub
  - live_penalty(): holding / PI / personal foul / face mask / block-in-back / illegal block / roughing

Effects: yardage (half-the-distance capped), automatic first downs, replay-the-down for
pre-snap offensive fouls, loss-of-down where appropriate. All flags are recorded to box stats
(team Pen / PenYds) and to the committing player (Penalties), so excessive fouling can feed a
workload/benching consequence upstream.

Real-CFB target: ~11-14 accepted penalties per GAME across both teams (~5.5-7 per team),
~55-70 penalty yards per team per game.
"""

# --- penalty catalog ---------------------------------------------------------
# Each entry: base per-eligible-play probability, yardage, and flags.
# Pre-snap fouls (checked once per play, before the snap):
PRE_SNAP = {
    "False Start":        {"p": 0.0166, "yds": -5, "side": "off", "replay": True},
    "Offside (D)":        {"p": 0.0077, "yds":  5, "side": "def", "replay": True, "auto_first_if_ge_dist": True},
    "Encroachment":       {"p": 0.0028, "yds":  5, "side": "def", "replay": True, "auto_first_if_ge_dist": True},
    "Delay of Game":      {"p": 0.0041, "yds": -5, "side": "off", "replay": True},
    "Illegal Formation":  {"p": 0.0023, "yds": -5, "side": "off", "replay": True},
    "Illegal Substitution":{"p": 0.0013, "yds":  5, "side": "def", "replay": True},
    "Illegal Shift/Motion":{"p": 0.0020, "yds": -5, "side": "off", "replay": True},
}

# Live fouls (checked after the play develops; may accept/decline vs the play result):
# 'phase' controls which plays they can occur on.
LIVE = {
    # 0.0294 produced 4.06 offensive holding calls per game against a real-CFB rate of
    # about 1.8, and it was the single largest drag on scoring in the 2037 audit: holding
    # is -10 AND replays the down, so each call wipes a gain and buries the offense. It
    # also pushed total penalties to 15.0/game, outside this module's own stated 11-14
    # target. At 0.0125 the league measures 1.9 holds and 12.1 total penalties per game.
    "Offensive Holding":      {"p": 0.0125, "yds": -10, "side": "off", "phase": "any",  "replay": True},
    "Defensive Holding":      {"p": 0.0070, "yds":   5, "side": "def", "phase": "pass", "auto_first": True},
    "Defensive Pass Interference":{"p": 0.0115,"yds": "spot","side":"def","phase":"pass_incomplete","auto_first": True},
    "Offensive Pass Interference":{"p": 0.0049,"yds":-10,"side":"off","phase":"pass","replay": True},
    "Illegal Block in the Back":{"p": 0.0077, "yds": -10, "side": "off", "phase": "return_or_run"},
    "Face Mask":              {"p": 0.0041, "yds":  15, "side": "either", "phase": "run_or_after"},
    "Roughing the Passer":    {"p": 0.0058, "yds":  15, "side": "def", "phase": "pass", "auto_first": True},
    "Personal Foul":          {"p": 0.0051, "yds":  15, "side": "either", "phase": "any"},
    "Targeting":              {"p": 0.0012, "yds":  15, "side": "def", "phase": "pass_or_run", "auto_first": True, "ejection": True},
    "Holding (D, illegal use of hands)":{"p": 0.0038,"yds":5,"side":"def","phase":"any","auto_first": True},
    "Illegal Block":          {"p": 0.0036, "yds": -10, "side": "off", "phase": "run_or_pass"},
}


def _pick_offender(unit, rng):
    """Choose which player drew the flag, weighted by individual (lack of) discipline."""
    if not unit:
        return None
    weights = [max(0.05, pl.get("discipline", 1.0)) for pl in unit]
    return rng.choices(unit, weights=weights)[0]


def pre_snap_penalty(rng, off_unit, def_unit, off_team_disc, def_team_disc):
    """Return (name, meta, offender) if a pre-snap foul occurs, else None.
    off_unit/def_unit: lists of players who could commit the foul (OL for false start, etc)."""
    for name, meta in PRE_SNAP.items():
        unit = off_unit if meta["side"] == "off" else def_unit
        tdisc = off_team_disc if meta["side"] == "off" else def_team_disc
        # scale base rate by the *unit's* average discipline and team discipline
        if unit:
            udisc = sum(pl.get("discipline", 1.0) for pl in unit) / len(unit)
        else:
            udisc = 1.0
        p = meta["p"] * udisc * tdisc
        if rng.random() < p:
            offender = _pick_offender(unit, rng)
            return name, meta, offender
    return None


def live_penalty(rng, phase, off_unit, def_unit, off_team_disc, def_team_disc):
    """Return (name, meta, offender) if a live foul occurs on a play of this phase, else None."""
    for name, meta in LIVE.items():
        if not _phase_ok(meta["phase"], phase):
            continue
        if meta["side"] == "off":
            unit, tdisc = off_unit, off_team_disc
        elif meta["side"] == "def":
            unit, tdisc = def_unit, def_team_disc
        else:  # either
            if rng.random() < 0.5:
                unit, tdisc = off_unit, off_team_disc
            else:
                unit, tdisc = def_unit, def_team_disc
        if unit:
            udisc = sum(pl.get("discipline", 1.0) for pl in unit) / len(unit)
        else:
            udisc = 1.0
        p = meta["p"] * udisc * tdisc
        if rng.random() < p:
            offender = _pick_offender(unit, rng)
            return name, meta, offender
    return None


def _phase_ok(foul_phase, play_phase):
    if foul_phase == "any":
        return True
    if foul_phase == play_phase:
        return True
    groups = {
        "pass": {"pass", "pass_incomplete", "pass_complete"},
        "run_or_pass": {"run", "pass", "pass_complete"},
        "run_or_after": {"run", "pass_complete"},
        "pass_or_run": {"pass", "pass_complete", "run"},
        "return_or_run": {"run", "return"},
    }
    return play_phase in groups.get(foul_phase, set())
