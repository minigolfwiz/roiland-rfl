"""Where do drives die?

Scoring fell from 26.3 points a team in 2030 to 19.1 in 2036 while scoring PLAYS per game
barely moved, so the question is not whether teams move the ball but what happens once
they are close. The engine logs every snap with down, distance and field position, so this
reconstructs drives from that and measures each stage: how often a drive reaches the red
zone, and what it comes away with when it does.

Field position in the log is yards from the offense's own goal line, so the opponent's
20 is spot 80 and the goal line is 100.
"""
import sys, collections, random, statistics
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E, subdivision as SUB


def drives_of(pbp):
    """Split the snap log into drives. A drive ends when possession changes or it scores."""
    out, cur = [], None
    for p in pbp:
        if not isinstance(p, dict):
            continue
        d = (p.get("desc") or "")
        low = d.lower()
        team, down, spot = p.get("team"), p.get("down"), p.get("spot")
        new = cur is None or team != cur["team"] or (down == 1 and p.get("dist") == 10
                                                     and spot is not None and cur["last_spot"] is not None
                                                     and spot < cur["last_spot"] - 25)
        if new:
            if cur: out.append(cur)
            cur = {"team": team, "start": spot, "best": spot or 0, "plays": 0,
                   "end": None, "last_spot": spot}
        cur["plays"] += 1
        if spot is not None:
            cur["best"] = max(cur["best"], spot)
            cur["last_spot"] = spot
        if "TOUCHDOWN" in d:
            cur["end"] = "TD"
        elif "FG GOOD" in d.upper() or ("fg" in low and "good" in low and "no good" not in low):
            cur["end"] = "FG"
        elif "no good" in low or "missed fg" in low:
            cur["end"] = "FGmiss"
        elif low.startswith("punt") or "punt -" in low:
            cur["end"] = "PUNT"
        elif "intercept" in low:
            cur["end"] = "INT"
        elif "fumble" in low and "lost" in low or "FUMBLE" in d and "recovered by" in low:
            cur["end"] = "FUM"
        elif "turnover on downs" in low or "downs" in low:
            cur["end"] = "DOWNS"
        elif "kneel" in low or "victory formation" in low:
            cur["end"] = "KNEEL"
    if cur: out.append(cur)
    return [d for d in out if d["plays"] > 0]


def run(n=160, seed0=77000000):
    SUB.register(E)
    FBS = list(E.U["teams"])
    rng = random.Random(11)
    pairs = []
    while len(pairs) < n:
        h, a = rng.choice(FBS), rng.choice(FBS)
        if h != a: pairs.append((h, a))

    ends = collections.Counter()
    rz_ends = collections.Counter()
    g10_ends = collections.Counter()
    n_drives = 0
    pts = []
    plays = collections.Counter()
    gains = []
    third = [0, 0]
    fourth_in_rz = collections.Counter()

    for i, (h, a) in enumerate(pairs):
        box, pbp = E.simulate_game(h, a, seed0 + i * 1013, keep_pbp=True)
        pts += [box["home_score"], box["away_score"]]
        for p in pbp:
            if not isinstance(p, dict): continue
            d = (p.get("desc") or ""); low = d.lower()
            if p.get("down") == 3 and p.get("dist") is not None:
                third[1] += 1
            if "rush for" in low:
                plays["rush"] += 1
                try: gains.append(int(low.split("rush for")[1].split()[0]))
                except Exception: pass
            elif "complete to" in low and "incomplete" not in low:
                plays["comp"] += 1
                try: gains.append(int(low.split(" for ")[-1].split()[0]))
                except Exception: pass
            elif "incomplete" in low:
                plays["inc"] += 1; gains.append(0)
            elif "sack" in low:
                plays["sack"] += 1
            if p.get("down") == 4 and (p.get("spot") or 0) >= 80:
                if "punt" in low: fourth_in_rz["punt"] += 1
                elif "fg" in low or "field goal" in low: fourth_in_rz["fg"] += 1
                elif "rush for" in low or "complete" in low or "incomplete" in low: fourth_in_rz["go"] += 1

        for dr in drives_of(pbp):
            if dr["end"] in (None, "KNEEL"): continue
            n_drives += 1
            ends[dr["end"]] += 1
            if dr["best"] >= 80:
                rz_ends[dr["end"]] += 1
            if dr["best"] >= 90:
                g10_ends[dr["end"]] += 1

    def pct(c, tot): return 100.0 * c / tot if tot else 0.0
    rz = sum(rz_ends.values()); g10 = sum(g10_ends.values())
    tot_plays = plays["rush"] + plays["comp"] + plays["inc"] + plays["sack"]
    return {
        "games": n,
        "pts_per_team": statistics.mean(pts),
        "drives_per_game": n_drives / n,
        "red_zone_trips_per_game": rz / n,
        "rz_TD_pct": pct(rz_ends["TD"], rz),
        "rz_FG_pct": pct(rz_ends["FG"], rz),
        "rz_empty_pct": pct(rz - rz_ends["TD"] - rz_ends["FG"], rz),
        "inside10_TD_pct": pct(g10_ends["TD"], g10),
        "drive_ends": {k: round(pct(v, n_drives), 1) for k, v in ends.most_common()},
        "pass_completion_pct": pct(plays["comp"], plays["comp"] + plays["inc"]),
        "run_share_pct": pct(plays["rush"], tot_plays),
        "mean_gain": statistics.mean(gains) if gains else 0,
        "sack_rate_pct": pct(plays["sack"], tot_plays),
        "fourth_down_in_rz": dict(fourth_in_rz),
    }


if __name__ == "__main__":
    r = run()
    for k, v in r.items():
        print("  %-26s %s" % (k, round(v, 2) if isinstance(v, float) else v))
