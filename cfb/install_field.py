"""Install Dan's committee field as the playoff bracket.

The engine's `committee.select_playoff_field` is only a suggestion. What `playoff.py`
actually reads is `state/playoff_s{N}.pkl`, so a hand-built field becomes canon by being
written there -- which is what this does, and what was missing when the Committee Room
was handed over.

Checked before anything is written, because a bad bracket is only discovered three
rounds in:
  * exactly 24 distinct FBS programmes, seeded 1 through 24 with no gaps
  * every one of the twelve conference champions present (automatic bids)
  * every at-large above .500
  * the record on each line matches the record in state
  * the season on the ballot matches the season in state
  * no bracket already on disk for this season

Structure: seeds 1-8 bye, 9-24 play round one at the higher seed's home, 9 drawing 24
down to 16 drawing 17. Later rounds are reseeded by `playoff.py` itself.
"""
import sys, json, pickle, os
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db

FIELD_SIZE = 24
BYES = 8


def install(ballot, force=False):
    s = SE.load_state()
    db = load_db()
    seas = s.get("season", 12)
    U = E.U
    FBS = set(U["teams"])

    if isinstance(ballot, str):
        ballot = json.loads(ballot)
    rows = ballot["field"] if isinstance(ballot, dict) else ballot

    if isinstance(ballot, dict) and ballot.get("season") not in (None, seas):
        raise SystemExit("ballot is for season %s; state is on season %d"
                         % (ballot.get("season"), seas))

    path = f'/home/claude/cfb2/state/playoff_s{seas}.pkl'
    if os.path.exists(path) and not force:
        raise SystemExit("a bracket already exists at %s -- refusing to overwrite" % path)

    # ---- shape ----------------------------------------------------------------
    if len(rows) != FIELD_SIZE:
        raise SystemExit("field has %d teams, needs %d" % (len(rows), FIELD_SIZE))
    seeds_given = sorted(int(r["seed"]) for r in rows)
    if seeds_given != list(range(1, FIELD_SIZE + 1)):
        raise SystemExit("seeds are not 1..%d with no gaps: %s" % (FIELD_SIZE, seeds_given))
    order = [r["team"] for r in sorted(rows, key=lambda r: int(r["seed"]))]
    if len(set(order)) != FIELD_SIZE:
        dupes = [t for t in set(order) if order.count(t) > 1]
        raise SystemExit("duplicate teams: %s" % dupes)
    unknown = [t for t in order if t not in FBS]
    if unknown:
        raise SystemExit("not FBS programmes: %s" % unknown)

    # ---- champions and records ------------------------------------------------
    champs = pickle.load(open(f'/home/claude/cfb2/state/conf_champs_s{seas}.pkl', 'rb'))
    champ_set = set(champs.values())
    missing = sorted(champ_set - set(order))
    if missing:
        raise SystemExit("conference champions left out of the field: %s" % missing)

    problems = []
    for r in rows:
        t = r["team"]
        rec = s["record"][t]
        if r.get("rec") and r["rec"] != "%d-%d" % (rec["W"], rec["L"]):
            problems.append("%s: ballot says %s, state says %d-%d"
                            % (t, r["rec"], rec["W"], rec["L"]))
        if t not in champ_set and rec["W"] <= rec["L"]:
            problems.append("%s is an at-large at %d-%d, not above .500"
                            % (t, rec["W"], rec["L"]))
    if problems:
        raise SystemExit("ballot does not match the season:\n  " + "\n  ".join(problems))

    # ---- the bracket ----------------------------------------------------------
    seeds = {t: i + 1 for i, t in enumerate(order)}
    byes = order[:BYES]
    play = order[BYES:]                       # seeds 9..24
    r1 = [(play[i], play[len(play) - 1 - i]) for i in range(len(play) // 2)]

    P = {"seeds": seeds, "order": order, "byes": byes, "r1": r1,
         "round_reached": None, "source": "human committee"}
    pickle.dump(P, open(path, 'wb'))
    return P, champs, s


if __name__ == "__main__":
    raw = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    P, champs, s = install(raw, force="--force" in sys.argv)
    sd, champ_set = P["seeds"], set(champs.values())
    print("installed: %d seeds, %d byes, %d first-round games | source: %s"
          % (len(sd), len(P["byes"]), len(P["r1"]), P["source"]))
    print("\nbyes (seeds 1-8):")
    for t in P["byes"]:
        r = s["record"][t]
        print("  %2d. %-21s %2d-%-2d %s" % (sd[t], t, r["W"], r["L"],
                                            "champion" if t in champ_set else ""))
    print("\nfirst round, at the higher seed:")
    for h, a in P["r1"]:
        rh, ra = s["record"][h], s["record"][a]
        # `r1` is (home, away) with the HIGHER seed first. The line used to read
        # "(24) Larksdale hosts (9) Ranroman", naming the visitor as the host.
        print("  (%2d) %-20s %d-%-2d  at  (%2d) %-20s %d-%-2d"
              % (sd[a], a, ra["W"], ra["L"], sd[h], h, rh["W"], rh["L"]))
