"""Correct four subdivision school names whose mascot leaked into the school name.

Dan's corrections, 2026-10-06. The subdivision generator appended part of each school's
mascot to its name and then truncated, so "Anderville Tech Hermit Crabs" became a school
called "Anderville Tech Hermit" with no mascot at all. Four schools were affected:

    Anderville Tech Hermit  ->  Anderville Tech     (Hermit Crabs)
    Lawiiri River           ->  Lawiiri             (River Rats)
    Gordon-Shipp River      ->  Gordon-Shipp        (River Dogs)
    Koli Ro Shuriken        ->  Koli Ro             (Shuriken)

The mascots are recorded on the school entry, which previously carried only `state` and
`level`. Nothing reads a subdivision mascot yet, but the data should be right.

This renames EVERYWHERE, including past box scores. That does not violate the permanence
rule: no result changes, only the label on one of the teams. Leaving the old name in the
games database would split a program's history across two spellings.

Run with --commit; it is a dry run otherwise.
"""
import sys, json, pickle, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db, save_db

RENAMES = {
    "Anderville Tech Hermit": ("Anderville Tech", "Hermit Crabs"),
    "Lawiiri River":          ("Lawiiri",         "River Rats"),
    "Gordon-Shipp River":     ("Gordon-Shipp",    "River Dogs"),
    "Koli Ro Shuriken":       ("Koli Ro",         "Shuriken"),
}

STATE_DIR = '/home/claude/cfb2/state'


def run(commit=False):
    hits = collections.Counter()
    U = E.U
    teams = set(U["teams"])

    # a corrected name must not collide with anything that already exists
    for old, (new, _m) in RENAMES.items():
        if old not in U["schools"]:
            raise RuntimeError("%r is not in the schools table" % old)
        if new in U["schools"] or new in teams:
            raise RuntimeError("cannot rename %r -> %r: the new name already exists" % (old, new))

    # ---- universe ----
    for old, (new, mascot) in RENAMES.items():
        rec = dict(U["schools"].pop(old))
        rec["mascot"] = mascot
        U["schools"][new] = rec
        hits["schools"] += 1

    # ---- season state: the installed schedule and the guest list ----
    s = SE.load_state()
    sched = []
    for wk, h, a, ic in s.get("sched") or []:
        if h in RENAMES: h = RENAMES[h][0]; hits["sched"] += 1
        if a in RENAMES: a = RENAMES[a][0]; hits["sched"] += 1
        sched.append((wk, h, a, ic))
    s["sched"] = sched
    # sub_opponents is a LIST of guest names for the season, not a map
    subopp = list(s.get("sub_opponents") or [])
    for i, n in enumerate(subopp):
        if n in RENAMES:
            subopp[i] = RENAMES[n][0]; hits["sub_opponents"] += 1
    s["sub_opponents"] = subopp

    # ---- the guest rosters and staffs generated for this season ----
    pkls = {}
    for fn in ("sub_rosters.pkl", "sub_coaches.pkl"):
        path = "%s/%s" % (STATE_DIR, fn)
        d = pickle.load(open(path, "rb"))
        for old, (new, _m) in RENAMES.items():
            if old in d:
                d[new] = d.pop(old); hits[fn] += 1
                if fn == "sub_rosters.pkl":
                    for pl in d[new]:
                        if pl.get("team") == old:
                            pl["team"] = new
        pkls[path] = d

    # ---- past box scores: the label on the team, never a result ----
    db = load_db()
    for gid, b in db.items():
        for side in ("home", "away"):
            if b.get(side) in RENAMES:
                b[side] = RENAMES[b[side]][0]; hits["games_db"] += 1
        for st in (b.get("stats") or {}).values():
            if st.get("team") in RENAMES:
                st["team"] = RENAMES[st["team"]][0]; hits["box_stats"] += 1

    # ---- Dan's own non-conference board, so a reload matches ----
    board_path = "%s/noncon_s12.json" % STATE_DIR
    board = json.load(open(board_path))
    for g in board["games"]:
        for side in ("host", "visitor"):
            if g[side] in RENAMES:
                g[side] = RENAMES[g[side]][0]; hits["board"] += 1

    print("replacements by location:")
    for k, v in sorted(hits.items()):
        print("  %-16s %d" % (k, v))

    if not commit:
        print("\nDRY RUN. Re-run with --commit.")
        return hits

    with open("%s/universe.pkl" % STATE_DIR, "wb") as f:
        pickle.dump(U, f)
    for path, d in pkls.items():
        with open(path, "wb") as f:
            pickle.dump(d, f)
    save_db(db)
    json.dump(board, open(board_path, "w"))
    SE.save_state(s)
    print("\nCOMMITTED.")
    return hits


if __name__ == "__main__":
    run(commit="--commit" in sys.argv)
