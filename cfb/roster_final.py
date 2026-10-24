"""Roster finalisation: clear the departures, sign the class, fill the holes.

Rebuilt for 2036. Recruiting marks who signed where but never puts anyone on a roster,
and nothing in the bundle removed departed players, so this stage owns the whole
transition from last season's roster to next season's.

Order matters: departures leave first so the class has room, then the signed recruits
arrive, then position floors are checked, then walk-ons fill any remaining space.
"""
import sys, random, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
import names_v2 as NV

U = E.U
TEAMS = U["teams"]
ROSTER_CAP = 70
ROSTER_MIN = 63
# a team cannot take the field without these
FLOORS = {"QB": 3, "RB": 3, "WR": 6, "TE": 3, "OL": 8, "DL": 6, "LB": 5, "CB": 4, "S": 4,
          "K": 2, "P": 2}

ARCH = {
    "QB": ["Pocket Passer", "Dual-Threat", "Gunslinger", "Game Manager"],
    "RB": ["Power Back", "Speed Back", "All-Purpose", "Short-Yardage Bruiser"],
    "WR": ["Deep Threat", "Possession", "Slot Technician", "Contested-Catch"],
    "TE": ["Receiving TE", "Blocking TE", "Hybrid"],
    "OL": ["Pass Protector", "Run Mauler", "Balanced"],
    "DL": ["Edge Rusher", "Run Stuffer", "Interior Penetrator"],
    "LB": ["Coverage LB", "Run-Stopping LB", "Blitzer"],
    "CB": ["Shutdown", "Ball-Hawk", "Press"],
    "S": ["Center Fielder", "Box Safety", "Hybrid Safety"],
    "K": ["Big Leg", "Accurate"], "P": ["Big Leg", "Directional"],
    "ATH": ["Return Ace", "Gadget"],
}
DISC_MU = {"OL": 1.22, "DL": 1.20, "CB": 1.15, "S": 1.10, "LB": 1.05, "TE": 0.95,
           "WR": 0.92, "RB": 0.88, "ATH": 0.90, "QB": 0.72, "K": 0.60, "P": 0.60}


def _derive_attrs():
    """Reuse the engine's own archetype attribute derivation."""
    src = open('/home/claude/cfb2/gen_rosters.py').read()
    a = src.index('def derive_attrs('); b = src.index('rosters = {}', a)
    return src[a:b]


def run_finalization(seed=67020):
    rng = random.Random(seed)
    ns = {'rng': rng}
    exec(_derive_attrs(), ns)
    derive_attrs = ns['derive_attrs']

    s = SE.load_state()
    signed = (s.get("recruiting_s%d" % s.get("season", 1), {}) or {}).get("signed", {})

    used = {p["name"] for r in E.ROSTERS.values() for p in r}
    used |= {c[r]["name"] for c in E.COACHES.values() for r in ("HC", "OC", "DC") if c.get(r)}
    sur = collections.Counter(n.split()[-1] for n in used)

    def fresh_name():
        n = NV.pick_name_v2(rng, used, surname_usage=sur, surname_cap=2)
        n = n[0] if isinstance(n, (tuple, list)) else n
        used.add(n); sur[n.split()[-1]] += 1
        return n

    pid = max((p["pid"] for r in E.ROSTERS.values() for p in r if isinstance(p["pid"], int)),
              default=100000) + 1

    def make(team, pos, abil, cls="Fr", arch=None, mob=None, walkon=False):
        nonlocal pid
        arch = arch or rng.choice(ARCH[pos])
        attrs = derive_attrs(pos, round(abil, 2), arch, cls)
        p = {"pid": pid, "name": fresh_name(), "team": team, "pos": pos, "cls": cls,
             "arch": arch, "abil": round(abil, 2),
             "pot": round(min(9.95, abil + rng.uniform(0.55, 1.85)), 2),
             "dur": round(max(.15, min(.95, rng.gauss(0.62, 0.15))), 3),
             "rep": 0.0, "inj_hist": [],
             "discipline": round(max(.45, min(1.9, rng.gauss(DISC_MU.get(pos, 1.0), 0.22))), 3),
             "attrs": attrs, "mob": mob if mob is not None else attrs.get("mob", 3.5),
             "freshman": True}
        if walkon: p["walkon"] = True
        pid += 1
        return p

    departed = added = walkons = floor_fills = trimmed = 0

    for t in TEAMS:
        roster = [p for p in E.ROSTERS[t] if not p.get("_leaving")]
        departed += len(E.ROSTERS[t]) - len(roster)

        # the signed class arrives
        for r in signed.get(t, []):
            p = make(t, r["pos"], r["abil"], arch=r.get("arch"), mob=r.get("mob"))
            # THE RECRUIT USED TO BE THROWN AWAY HERE. `make` drew a fresh random name, so
            # the player who arrived on the roster was never the one recruiting signed --
            # "Hugh Ha-Rim, the five-star back Eona signed" did not exist under that name
            # anywhere, and no star rating survived, so a class could never be audited
            # for busts and gems. The signee's name, star rating and recruit id now ride
            # along. Forward only: every class already on a roster keeps the name it has
            # played under. (Found 2039, Dan's question about busts.)
            if r.get("name"):
                p["name"] = r["name"]
            p["stars"] = r.get("stars")
            p["rid"] = r.get("rid")
            p["signed_abil"] = r["abil"]
            roster.append(p)
            added += 1

        # position floors: a roster that cannot field a unit gets emergency bodies
        counts = collections.Counter(p["pos"] for p in roster)
        for pos, need in FLOORS.items():
            while counts[pos] < need:
                roster.append(make(t, pos, rng.uniform(3.0, 4.8), walkon=True))
                counts[pos] += 1; floor_fills += 1

        # walk-ons up to a workable size
        while len(roster) < ROSTER_MIN:
            pos = rng.choices(list(FLOORS), weights=[FLOORS[p] for p in FLOORS])[0]
            roster.append(make(t, pos, rng.uniform(2.6, 4.4), walkon=True))
            counts[pos] += 1; walkons += 1

        # Trim to the cap. Walk-ons and marginal players go first; if that is not enough
        # the weakest player at any position still above its floor is cut, so the cap is
        # actually enforced rather than merely attempted.
        if len(roster) > ROSTER_CAP:
            counts = collections.Counter(p["pos"] for p in roster)
            for group in (sorted([p for p in roster if p.get("walkon") or p["abil"] < 4.2],
                                 key=lambda p: p["abil"]),
                          sorted(roster, key=lambda p: p["abil"])):
                for p in group:
                    if len(roster) <= ROSTER_CAP: break
                    if p not in roster: continue
                    if counts[p["pos"]] <= FLOORS.get(p["pos"], 0): continue
                    roster.remove(p); counts[p["pos"]] -= 1; trimmed += 1
                if len(roster) <= ROSTER_CAP: break

        E.ROSTERS[t] = roster

    sizes = [len(r) for r in E.ROSTERS.values()]
    summary = {"departed": departed, "recruits_added": added, "walkons": walkons,
               "floor_fills": floor_fills, "trimmed": trimmed,
               "min": min(sizes), "max": max(sizes), "total": sum(sizes)}
    s["roster_final_s%d" % s.get("season", 1)] = summary
    E.persist_rosters()
    SE.save_state(s)
    return summary


if __name__ == "__main__":
    print(run_finalization())
