"""Data for the team-marks specimen page.

Written after I hand-typed thirty colour pairs into that page from memory and got most
of them wrong. Every field here is a lookup: name, mascot, conference and the two colours
Dan chose, straight out of the universe file, which has been verified identical to the
canon site snapshot for all 152 programs.
"""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E

U = E.U


def build(out='/home/claude/cfb2/state/marks.json'):
    teams = []
    for t in sorted(U["teams"]):
        g = U["geo"][t]
        teams.append({
            "name": t,
            "mascot": g.get("mascot", ""),
            "full": g.get("full_name", t),
            "conf": U["team_conf"][t],
            "col": list(U["team_colors"][t]),
        })
    payload = {
        "teams": teams,
        "conferences": sorted(U["conferences"].keys()),
        # the five from the first round, so the comparison stays honest
        "featured": ["Eona", "North Hatesei", "Hatesei", "Rogaela State", "Will Tech"],
    }
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


def verify():
    """Re-check the universe against the canon snapshot before anything is published."""
    h = open('/mnt/user-data/outputs/roiland_SNAPSHOT_s10w02_DO_NOT_OVERWRITE.html').read()
    i = h.index('const D = ') + len('const D = ')
    D, _ = json.JSONDecoder().raw_decode(h, i)
    C = D["colors"]
    bad = [t for t, c in U["team_colors"].items()
           if [x.lower() for x in (C.get(t) or [])] != [x.lower() for x in c]]
    return len(U["team_colors"]), bad


if __name__ == "__main__":
    n, bad = verify()
    print("colour check: %d/152 match the canon snapshot%s"
          % (n - len(bad), "" if not bad else "  MISMATCHED: %s" % bad[:8]))
    if bad:
        raise SystemExit("refusing to export with colours that disagree with canon")
    p = build()
    print("exported %d programs across %d conferences"
          % (len(p["teams"]), len(p["conferences"])))
