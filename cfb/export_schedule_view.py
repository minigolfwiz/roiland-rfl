"""Build the payload for the season schedule viewer.

Re-run this after every sim window; it reads whatever has been played so far and leaves
the rest as fixtures. A full season of box scores is ~19MB raw, which will not fit in an
artifact, so the export is trimmed: the fields that are None for regular-season games are
dropped, player lines are packed as arrays rather than objects, and only players who
actually did something are carried.

Records, standings and head-to-head are NOT exported -- the viewer computes them from the
games, so there is one source of truth and no chance of the two disagreeing.
"""
import sys, json, collections, zlib, re
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db

U = E.U
TEAMS = list(U["teams"])
TSET = set(TEAMS)
TC = U["team_conf"]
TIERS = U["tiers"]
GEO = U["geo"]
COLORS = U["team_colors"]

# the order a box score should read in, and which stats belong to each unit
UNITS = [
    ("Passing",   ["Att", "Comp", "PassYds", "PassTD", "INT", "SackedFor"]),
    ("Rushing",   ["RushAtt", "RushYds", "RushTD"]),
    ("Receiving", ["Targets", "Rec", "RecYds", "RecTD"]),
    ("Defense",   ["Tackles", "Sacks", "INT_def", "FumRec", "DefTD", "Safety"]),
    ("Kicking",   ["FGMade", "FGAtt", "XPMade", "XPAtt"]),
    ("Punting",   ["Punts", "PuntYds"]),
    ("Returns",   ["PuntRetYds"]),
    ("Penalties", ["Penalties", "PenYds"]),
]
STAT_KEYS = [k for _u, ks in UNITS for k in ks]

# Postseason weeks. The regular season ends at 14 and conference finals sit at 15, so each
# playoff round takes the next slot up. Order matters: "CCG" is checked before "PO_" only
# because the two never appear in the same game id, but CHAMP must beat the bare "PO_".
PO_ROUNDS = [("CCG", 15), ("PO_R1", 16), ("PO_R2", 17), ("PO_QF", 18),
             ("PO_SF", 19), ("PO_CHAMP", 20)]


def _playoff_seeds(season):
    import os, pickle
    p = '/home/claude/cfb2/state/playoff_s%d.pkl' % season
    if not os.path.exists(p):
        return {}
    try:
        return {t: int(v) for t, v in (pickle.load(open(p, 'rb')).get('seeds') or {}).items()}
    except Exception:
        return {}


def pack_box(b):
    """A game's detail, as small as it can be without losing anything worth seeing."""
    lines = []
    for pid, st in (b.get("stats") or {}).items():
        vals = {k: st[k] for k in STAT_KEYS if st.get(k)}
        if not vals:
            continue                      # dressed but did nothing
        lines.append([st.get("name", "?"), st.get("pos", ""), st.get("cls", ""),
                      st.get("team", ""), vals])
    # The timeline carries scores AND turnovers, interleaved in game order. A row is
    # [q, clock, team, desc, score, kind]; `kind` is "" for a score and "int"/"fum" for a
    # turnover, which has no score to show. Turnovers that ended in points -- a pick six,
    # a fumble returned -- are already in scoring_plays and are NOT repeated here.
    sp = [[p.get("q"), p.get("clock"), p.get("team"), p.get("desc"),
           list(p.get("score") or []), ""] for p in (b.get("scoring_plays") or [])]
    tos = b.get("turnovers")
    if tos is None:
        tos = _turnovers_from_pbp(b)      # games played before the engine recorded them
    sp += [[p.get("q"), p.get("clock"), p.get("team"), p.get("desc"), [], p.get("kind", "to")]
           for p in tos]
    # within a quarter the clock counts DOWN, so descending clock is chronological
    sp.sort(key=lambda r: (r[0] or 0, -(r[1] or 0)))
    out = {"sp": sp, "pl": lines}
    for k in ("venue", "weather", "site", "ot", "pregame_home_wp"):
        v = b.get(k)
        if v not in (None, 0, "", "home"):
            out[k] = v
    return out


_TO_INT = re.compile(r"INTERCEPTED - (.+?) picks off (.+?), returns(?: it)? (\d+)")
_TO_FUM = re.compile(r"FUMBLE - (.+?) loses it; (.+?) recovers")


def _turnovers_from_pbp(b):
    """Recover non-scoring turnovers from a box score written before the engine kept them.

    Every game ever played already describes its turnovers in the play-by-play; only the
    structured list is new. Rather than leave the timeline blank for weeks 0-2 of 2038 --
    and for all twelve previous seasons -- they are parsed back out of the commentary.

    A pick six reads "returns it N the distance" and is already a scoring play, so the
    pattern requires the plain "returns N" form and those are skipped.
    """
    z = b.get("pbp_z")
    if not z:
        return []
    try:
        plays = json.loads(zlib.decompress(z).decode())
    except Exception:
        return []
    out = []
    for p in plays:
        if not isinstance(p, dict):
            continue
        d = p.get("desc") or ""
        if "the distance!" in d:
            continue                      # returned for a touchdown: already a scoring play
        clock = p.get("clock")
        if isinstance(clock, str) and ":" in clock:
            mm, ss = clock.split(":")[:2]
            try:
                clock = int(mm) * 60 + int(ss)
            except ValueError:
                clock = 0
        m = _TO_INT.search(d)
        if m:
            out.append({"q": p.get("q"), "clock": clock, "team": p.get("team"), "kind": "int",
                        "desc": "%s intercepted by %s%s" % (
                            m.group(2), m.group(1),
                            (", returns %s" % m.group(3)) if m.group(3) != "0" else "")})
            continue
        m = _TO_FUM.search(d)
        if m:
            out.append({"q": p.get("q"), "clock": clock, "team": p.get("team"), "kind": "fum",
                        "desc": "%s fumbles, recovered by %s" % (m.group(1), m.group(2))})
    return out


def build(out='/home/claude/cfb2/state/schedule_view.json', season=None):
    """season=None builds the live season from the installed schedule, so unplayed games
    still appear as fixtures. Naming an OLD season builds it from the games database
    instead -- its schedule is long overwritten, but every box score records its own
    week, which is enough to rebuild the season as it was played."""
    s = SE.load_state()
    db = load_db()
    live = season is None or season == s.get("season")
    season = s.get("season", 11) if season is None else season
    year = 2025 + season
    tag = "S%d" % season

    # Regular-season games only, keyed by the pairing. Postseason is kept out of this map
    # on purpose: a conference final is often a rematch, and keying both by (home, away)
    # let the title game overwrite the regular-season meeting and vanish from the viewer.
    played, post = {}, []
    for gid, b in db.items():
        gid = str(gid)
        if not gid.startswith(tag):
            continue
        if b.get("postseason") or "CCG" in gid or "PO" in gid:
            post.append((gid, b))
        else:
            played[(b.get("home"), b.get("away"))] = (gid, b)

    games, boxes = [], {}
    if live:
        rows = [(wk, h, a, ic) for wk, h, a, ic in s["sched"]]
    else:
        rows = []
        for (h, a), (gid, b) in played.items():
            if b.get("postseason"):
                continue
            ic = (h in TSET and a in TSET and TC.get(h) == TC.get(a))
            rows.append((b.get("week", 0), h, a, ic))
        rows.sort()

    for wk, h, a, ic in rows:
        rec = played.get((h, a))
        g = {"w": wk, "h": h, "a": a, "c": 1 if ic else 0}
        if h not in TSET or a not in TSET:
            g["sub"] = 1
        if rec:
            gid, b = rec
            g["id"] = gid
            g["hs"] = b.get("home_score")
            g["as"] = b.get("away_score")
            if b.get("ot"):
                g["ot"] = b["ot"]
            boxes[gid] = pack_box(b)
        games.append(g)

    # The postseason carries no schedule row, so it is appended on its own. Each round gets
    # its own week number past 14 so the viewer's existing week machinery labels and
    # navigates it -- one undifferentiated "Playoff" bucket of 23 games tells you nothing.
    for gid, b in post:
        wk = next((w for frag, w in PO_ROUNDS if frag in gid), 99)
        games.append({"w": wk, "h": b.get("home"), "a": b.get("away"),
                      "c": 0, "id": gid, "hs": b.get("home_score"),
                      "as": b.get("away_score"), "post": 1,
                      **({"ot": b["ot"]} if b.get("ot") else {})})
        boxes[gid] = pack_box(b)

    teams = {}
    for t in TEAMS:
        teams[t] = {"conf": TC[t], "tier": TIERS.get(TC[t], "L6"),
                    "full": GEO.get(t, {}).get("full_name", t),
                    "mascot": GEO.get(t, {}).get("mascot", ""),
                    "col": COLORS.get(t, ["#555", "#999"])}
    # guest programs appear in the schedule but have no FBS entry
    for g in games:
        for side in ("h", "a"):
            n = g[side]
            if n not in teams:
                teams[n] = {"conf": "Subdivision", "tier": "SUB", "full": n,
                            "mascot": "", "col": ["#6b6355", "#938b78"], "sub": 1}

    payload = {
        "season": season, "year": year, "live": live,
        "next_week": s.get("next_week", 0) if live else 99,
        "teams": teams,
        "conferences": {c: list(tl) for c, tl in U["conferences"].items()},
        "games": games,
        "boxes": boxes,
        "units": UNITS,
        "poll": [list(x) for x in (s.get("media_poll_current") or [])][:25],
        # The committee board as it stood after each week. A game played in week W was
        # played against the board from week W-1, which is the one that should decide
        # whether "#4" appears beside a name -- using the final board retroactively would
        # rank teams by what they did later.
        "committee": {str(k): list(v) for k, v in (s.get("committee_history") or {}).items()},
        # the media poll after each week, same shape -- the ranking of record until the
        # committee's first board (Dan, 2039)
        "media": {("-1" if k == "pre" else str(k)): [x[1] if isinstance(x, (list, tuple)) else x for x in v]
                  for k, v in (s.get("media_history") or {}).items()},   # 'pre' = the preseason poll, filed as week -1 so week 0 games are ranked against it (Dan, 2045)
        # the playoff seeds, once a field is installed: during the postseason the viewer
        # badges teams by SEED rather than committee rank (Dan, 2039)
        "seeds": _playoff_seeds(season),
        "champion_prev": (s.get("season_archive", {}).get(str(season - 1), {}) or {}).get("champion"),
    }
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload, out


if __name__ == "__main__":
    import os
    sn = int(sys.argv[1]) if len(sys.argv) > 1 else None
    p, path = build(out=('/home/claude/cfb2/state/schedule_view%s.json'
                         % ('' if sn is None else '_s%d' % sn)), season=sn)
    n_played = sum(1 for g in p["games"] if "id" in g)
    print("season %d (%d) | %d games, %d played | %d box scores | %.1f MB"
          % (p["season"], p["year"], len(p["games"]), n_played, len(p["boxes"]),
             os.path.getsize(path) / 1e6))
