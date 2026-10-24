"""Subdivision (non-FBS) opponents.

Rebuilt after the 2035 container reset. The original module and its rosters were
lost; this regenerates guest programs from the canon school roll so FBS teams can
keep scheduling them.

CANON BEHAVIOUR these must preserve:
  * guests ALWAYS travel -- a subdivision school never hosts an FBS team
  * they are clearly below the L6 floor: FBS hosts win the large majority, often
    by three or four scores, shutouts are common, and an upset is a genuine event
  * their results count in the record but they are not ranked or polled

Guest talent is set from a low pseudo-prestige band, deliberately beneath the
weakest FBS program, keeping the intentionally wide tier gap intact.
"""
import pickle, random, os

SUB_ROSTER_PATH = '/home/claude/cfb2/state/sub_rosters.pkl'
SUB_COACH_PATH = '/home/claude/cfb2/state/sub_coaches.pkl'

TEMPLATE = [("QB", 3), ("RB", 4), ("WR", 7), ("TE", 3), ("OL", 9),
            ("DL", 7), ("LB", 6), ("CB", 5), ("S", 4), ("K", 2), ("P", 2), ("ATH", 1)]
CLASSES = ["Fr", "So", "Jr", "Sr"]
CLASS_W = [.30, .27, .23, .20]
CLASS_AB = {"Fr": -0.45, "So": -0.15, "Jr": 0.12, "Sr": 0.30}


def _arch(pos, rng):
    import gen_rosters_lib as _lib  # noqa: F401  (kept for parity if present)
    table = {
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
    return rng.choice(table[pos])


# Subdivision talent band. SUB_CEILING is the strongest guest roster the league can
# produce and is deliberately unchanged; SUB_FLOOR and SUB_WEAK_SHARE govern how deep
# and how often the weak tail reaches below the old floor of 2.
SUB_CEILING = 18.0
SUB_FLOOR = -10.0
SUB_WEAK_SHARE = 0.20

def generate(guests, seed=20351000, derive_attrs=None, name_fn=None):
    """Build rosters + staffs for the named guest schools."""
    rng = random.Random(seed)
    rosters, coaches = {}, {}
    pid = 900000
    for g in sorted(guests):
        # Pseudo-prestige band, CALIBRATED against the 304 subdivision games in the
        # recovered history (S4-S10): canon = +22.1 mean margin, 89.8% FBS host wins.
        #
        # 2026-10-07: RE-CALIBRATED from 16-36 to 2-18. The old band was absolute while
        # FBS talent kept drifting upward, so the gap closed year by year without anyone
        # noticing: margin fell +22.8 (S6) -> +17.3 (S10) -> +15.6 (S11) -> +8.9 (S12),
        # and guests were winning 31% of their games against FBS programs. The strongest
        # guest roster had overtaken the weakest FBS program outright. 2-18 restores
        # +21.5 margin and 89.5% FBS wins against the canon targets above.
        #
        # THIS BAND IS ABSOLUTE AND FBS TALENT MOVES. Re-measure it every few seasons,
        # or make it relative to the live FBS distribution.
        #
        # 2026-10-09, Dan: lower the floor without lowering the ceiling. Uniform 2-18 made
        # the subdivision a narrow block -- the worst guest on a schedule was barely weaker
        # than the best, so a guarantee game always landed in much the same place and a bad
        # guest was never the walkover it ought to be.
        #
        # Most guests are drawn exactly as before; one in five comes from a much lower
        # band. That is deliberate rather than a blanket skew: bending the whole curve
        # downward also pulled the top quartile with it, which is the half of the
        # distribution Dan asked to leave alone. Measured over 20,000 draws, this keeps
        # p75 at 13.0 against 14.0 and p90 at 16.0 against 16.4, with the ceiling
        # untouched at 18, while the floor falls from 2 to -10.
        if rng.random() < SUB_WEAK_SHARE:
            p = rng.uniform(SUB_FLOOR, 2)
        else:
            p = rng.uniform(2, SUB_CEILING)
        base = 3.95 + (p / 100) * 3.2
        players = []
        for pos, n in TEMPLATE:
            for _ in range(n):
                cls = rng.choices(CLASSES, weights=CLASS_W)[0]
                abil = max(1.2, min(8.6, rng.gauss(base + CLASS_AB[cls], 0.95)))
                if rng.random() < 0.012:       # the occasional overlooked star
                    abil = min(8.8, abil + rng.uniform(1.0, 2.1))
                arch = _arch(pos, rng)
                pid += 1
                attrs = derive_attrs(pos, round(abil, 2), arch, cls) if derive_attrs else {}
                players.append({
                    'pid': pid, 'name': (name_fn() if name_fn else 'Sub Player %d' % pid),
                    'team': g, 'pos': pos, 'cls': cls, 'arch': arch,
                    'abil': round(abil, 2), 'pot': round(min(9.0, abil + rng.uniform(.2, 1.1)), 2),
                    'dur': round(max(.15, min(.95, rng.gauss(0.60, 0.15))), 3),
                    'rep': 0.0, 'inj_hist': [],
                    'discipline': round(max(.45, min(1.9, rng.gauss(1.05, 0.25))), 3),
                    'attrs': attrs, 'mob': attrs.get('mob', 3.5),
                    'subdivision': True,
                })
        rosters[g] = players
        sk = rng.uniform(2.0, 4.8)
        staff = {}
        for role in ('HC', 'OC', 'DC'):
            age = int(max(32, min(64, rng.gauss(46, 8))))
            staff[role] = {'name': (name_fn() if name_fn else '%s %s' % (g, role)),
                           'skill': round(max(1.0, rng.gauss(sk, 0.6)), 2),
                           'tenure': rng.randint(0, 9),
                           'aggression': round(rng.uniform(.1, .9), 2),
                           'age': age, 'retire_age': int(min(72, max(age + 3, rng.gauss(65, 3))))}
        staff.update({'patience': 0.0, 'hfa_base': 2.5, 'team_discipline': 1.0,
                      'off_scheme': 'Pro-Style', 'def_scheme': '4-3 Base'})
        coaches[g] = staff
    return rosters, coaches


def save(rosters, coaches):
    pickle.dump(rosters, open(SUB_ROSTER_PATH, 'wb'))
    pickle.dump(coaches, open(SUB_COACH_PATH, 'wb'))


def register(E):
    """Merge the guest programs into the live engine tables (idempotent)."""
    if not os.path.exists(SUB_ROSTER_PATH):
        return 0
    R = pickle.load(open(SUB_ROSTER_PATH, 'rb'))
    C = pickle.load(open(SUB_COACH_PATH, 'rb'))
    n = 0
    for t, r in R.items():
        if t not in E.ROSTERS:
            E.ROSTERS[t] = r; n += 1
        if t not in E.COACHES:
            E.COACHES[t] = C[t]
    return n
