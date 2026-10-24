"""Install a committee ranking Dan built in the Committee Ballot.

From 2038 the weekly committee ranking is Dan's, not the computer's. `committee_poll.py`
can still produce one and `committee_rank` still seeds the playoff, but the board of
record is the hand-off this script reads.

What it writes into the season state, matching what `run_weeks_committee.py` has always
written so every downstream page keeps working:

    committee_poll_prev     the board before this ballot
    committee_poll_current  [(rank, team)] -- this ballot
    committee_history[wk]   [team, ...] in order, kept per week

The audit is strict on purpose. A ballot is typed by hand into a browser and handed back
as JSON; a duplicated team or a skipped rank would propagate silently into the playoff
seeding six weeks later.

Usage:
    python3 install_committee.py ballot.json            # dry run
    python3 install_committee.py ballot.json --commit
"""
import sys, json, os
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E

U = E.U
TSET = set(U["teams"])
EXPECT = 25


def audit(data, s):
    fails = []
    ballot = data.get("ballot") or []
    if data.get("season") != s.get("season"):
        fails.append("ballot is season %s, state is season %s"
                     % (data.get("season"), s.get("season")))
    done = s.get("next_week", 0) - 1
    if data.get("week") != done:
        fails.append("ballot is week %s, the week just completed is %s"
                     % (data.get("week"), done))
    if len(ballot) != EXPECT:
        fails.append("%d teams on the ballot, expected %d" % (len(ballot), EXPECT))
    if not data.get("complete"):
        fails.append("the ballot is not marked complete")

    ranks = [e.get("rank") for e in ballot]
    if sorted(r for r in ranks if isinstance(r, int)) != list(range(1, len(ballot) + 1)):
        fails.append("ranks are not 1..%d exactly: %s" % (len(ballot), ranks))

    names = [e.get("team") for e in ballot]
    unknown = [n for n in names if n not in TSET]
    if unknown:
        fails.append("not programmes in this league: %s" % unknown)
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        fails.append("ranked more than once: %s" % dupes)

    # The record the page sent must still match the record in the state. If it does not,
    # the ballot was built against a different week and installing it would backdate the
    # board -- which is exactly the failure this check exists to catch.
    stale = []
    for e in ballot:
        t = e.get("team")
        if t not in TSET:
            continue
        r = s["record"][t]
        want = "%d-%d" % (r["W"], r["L"])
        if e.get("rec") and e["rec"] != want:
            stale.append("%s on the ballot as %s, now %s" % (t, e["rec"], want))
    if stale:
        fails.append("records have moved on: %s" % stale[:4])
    return fails, [e["team"] for e in sorted(ballot, key=lambda x: x["rank"])]


def install(path, commit=False):
    s = SE.load_state()
    data = json.load(open(path))
    fails, order = audit(data, s)

    print("%s -- season %s week %s, %d teams"
          % (os.path.basename(path), data.get("season"), data.get("week"),
             len(data.get("ballot") or [])))
    prior = [t for _r, t in sorted(s.get("committee_poll_current") or [])]
    if prior:
        moves = []
        for i, t in enumerate(order):
            was = prior.index(t) + 1 if t in prior else None
            if was is None:
                moves.append("%s NEW at %d" % (t, i + 1))
            elif was != i + 1:
                moves.append("%s %d->%d" % (t, was, i + 1))
        print("  movement: %s" % (", ".join(moves[:6]) or "none"))
        gone = [t for t in prior if t not in order]
        if gone:
            print("  dropped out: %s" % ", ".join(gone))
    else:
        print("  this is the first committee board of the season")
    print("  1-5: %s" % ", ".join(order[:5]))

    if fails:
        print("\nREFUSING TO INSTALL:")
        for f in fails:
            print("   * %s" % f)
        return fails
    print("  audit: CLEAN")
    if not commit:
        print("\nDRY RUN. Re-run with --commit.")
        return fails

    s["committee_poll_prev"] = list(s.get("committee_poll_current") or [])
    s["committee_poll_current"] = [(i + 1, t) for i, t in enumerate(order)]
    s.setdefault("committee_history", {})[str(data["week"])] = list(order)
    s["committee_official"] = True        # the board is hand-built; nothing may overwrite it
    SE.save_state(s)
    print("\nINSTALLED -- week %d committee board of record, %d teams."
          % (data["week"], len(order)))
    return fails


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    install(sys.argv[1], commit='--commit' in sys.argv)
