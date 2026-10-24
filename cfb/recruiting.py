"""Season 1->2 recruiting + transfer portal.
Recruit class: realistic 1-5 star pyramid. Signing priority by prestige + recent
success (hot teams). Gem cap keeps freshmen below elite-vet tier. Portal valuations
chase OBSERVED production, not hidden ability."""
import sys, random, pickle, collections; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E
from names_v2 import pick_name_v2

POSITIONS = ["QB","RB","WR","TE","OL","DL","LB","CB","S","K","P"]
# Dan's ruling, 2036 offseason: recruit enough specialists to replace the ones who
# graduate. The old weights gave K 0.02 and P 0.01, which in a signed class of ~1775 is
# 0.32 kickers and 0.14 punters per program per year. A team carries about 2.26 kickers
# and 2.12 punters over four-year careers, so replacement demand is ~0.55 and ~0.53 a
# year -- punters were being supplied at roughly a QUARTER of it. The shortfall fell to
# `roster_final`'s position floors, which fill with ability 3.0-4.8 bodies, so 43% of
# the league's punters and 27% of its kickers were walk-ons and no specialist could ever
# develop into a star. Safety had the same problem one tier down.
# The +0.08 is taken off OL, WR and LB, which were signing 2.12, 1.70 and 1.48 per team.
# 2040: OL raised 0.13 -> 0.18, RB cut 0.10 -> 0.06, QB 0.08 -> 0.07.
# The class mix did not match the shape a roster needs. A roster's position floors want
# OL to be 17.4% of it (8 of the 46 floor slots) and the country was recruiting 13%,
# while running backs took 10% for a floor share of 6.5%. Measured on real, non-walk-on
# bodies after the 2038 finalisation, OL was short by 122 across 55 programmes -- more
# than any other position -- and RB was over-recruited by almost exactly that amount.
# This is the recruiting instance of the same bug already fixed in draft valuation and
# portal valuation: linemen generate no box-score statistics and are undervalued
# everywhere they are counted. Forward only; takes effect at the next class.
POS_WEIGHTS = [0.07,0.06,0.13,0.06,0.18,0.14,0.10,0.09,0.085,0.045,0.04]
assert abs(sum(POS_WEIGHTS) - 1.0) < 1e-9, sum(POS_WEIGHTS)

# How many high-school recruits exist nationally in a given year. Dan's ruling, 2036
# offseason: this is its own number, not a function of how many roster spots happen to
# be open.
#
# It used to be sized to the exact sum of every program's need, which had two
# consequences. Every recruit in the country signed somewhere -- `leftover` came out at
# exactly 0 every single year, so nobody ever missed on a prospect. And the pool shrank
# whenever rosters ran full: 2035 produced 2800 recruits, 2036 wanted only 1775, which
# left 189 blue-chips where 293 were needed for the hoarding caps in `cap_for` to bite
# at all. The top twenty programs are allowed six each, 120 between them, so a shallow
# class spreads the stars flat across all 152 teams instead of concentrating them, and
# the L6's blue-chip share came out at 7.9% against a canon series of 4, 4, 3, 2, 3.2%.
#
# 2800 is the figure the 2035 class actually carried, which is the one cycle that hit
# canon on the nose. The jitter keeps it from being a dead constant; it is drawn from
# the season number so a cycle is reproducible.
NATIONAL_CLASS = 2800
CLASS_JITTER = 0.025            # +/- 2.5%, so classes breathe without lurching


def national_class_size(season, needs_total=0):
    """The size of this year's national recruiting class.

    `needs_total` is a floor, not the target: if the league somehow needed more bodies
    than the country produced, roster finalisation would paper the gap with walk-ons,
    and that should never be the reason a class is short.
    """
    rng = random.Random(90210 + season)
    n = round(NATIONAL_CLASS * (1.0 + rng.uniform(-CLASS_JITTER, CLASS_JITTER)))
    return max(n, needs_total)

# National star pyramid (real CFB shape): a few dozen 5*, ~300 4*, thousands 2-3*
def star_to_ability(stars, rng):
    # ability bands; 5* cap at gem cap 8.6, most freshmen land 3.5-6.5
    if stars == 5:   return round(min(8.6, rng.uniform(7.6, 8.6)), 2)
    if stars == 4:   return round(rng.uniform(6.6, 7.7), 2)
    if stars == 3:   return round(rng.uniform(5.4, 6.7), 2)
    if stars == 2:   return round(rng.uniform(4.2, 5.5), 2)
    return round(rng.uniform(2.8, 4.3), 2)   # 1*

def make_class(n_total, seed=63001):
    rng = random.Random(seed)
    # target national star counts scaled to class size (~2800)
    # real ratios: ~0.1% 5*, ~10% 4*, ~35% 3*, ~40% 2*, ~15% 1*
    # Five-stars are genuinely scarce: canon classes carried about thirteen, not the
    # twenty-five an 0.9% rate produced.
    n5 = max(11, round(n_total*0.0047))
    n4 = round(n_total*0.10)
    n3 = round(n_total*0.35)
    n2 = round(n_total*0.40)
    n1 = n_total - n5 - n4 - n3 - n2
    star_list = [5]*n5 + [4]*n4 + [3]*n3 + [2]*n2 + [1]*n1
    rng.shuffle(star_list)
    used = set(); sur = collections.defaultdict(int)
    # seed used-names from existing rosters to avoid collisions
    for r in E.ROSTERS.values():
        for pl in r:
            used.add(pl["name"]); sur[pl["name"].split()[-1]] += 1
    recruits = []
    for i, stars in enumerate(star_list):
        pos = rng.choices(POSITIONS, weights=POS_WEIGHTS)[0]
        # 2041 classes on: no five-star punters. A specialist drawn at 4-5* is re-rolled
        # to a position that actually gets rated that high (the 2040 class had a 5*
        # punter at Leafette and a 5* kicker at Crayellan State).
        if stars >= 4 and pos in ("K", "P"):
            pos = rng.choices(POSITIONS[:9], weights=POS_WEIGHTS[:9])[0]
        abil = star_to_ability(stars, rng)
        nm = pick_name_v2(rng, used, surname_usage=sur, surname_cap=2)[0]
        used.add(nm)
        # QB mobility archetype (feeds S2 QB-rush build)
        arch = None; mob = None
        if pos == "QB":
            arch = rng.choices(["Pocket Passer","Gunslinger","Game Manager","Dual-Threat"],
                               weights=[0.32,0.26,0.20,0.22])[0]
            mob = round({"Dual-Threat":rng.uniform(7,9.5),"Gunslinger":rng.uniform(3,6),
                         "Game Manager":rng.uniform(3,6),"Pocket Passer":rng.uniform(1.5,4.5)}[arch],1)
        recruits.append({"rid":f"R{i:04d}","name":nm,"pos":pos,"stars":stars,"abil":abil,
                         "arch":arch,"mob":mob,"signed":None})
    return recruits

PULL_PRESTIGE = 0.6     # Dan, 2039 end: recruit on results, not reputation
PULL_FINISH = 0.25      # conference finish percentile (0-100) -> up to 25 points

def signing_priority(s):
    """Order teams by recruiting pull: prestige, last-season success, and where the
    programme finished in its own conference.

    Until 2039 pull was prestige + ~1.26 a win, so a 6-6 Great Fourteen programme at
    84 out-pulled a 12-1 Jyras Bay champion at 70, and ten of the twenty 6-blue-chip
    slots went to the G14 every year whatever it had done. Prestige now carries 60%
    of its old weight and a conference finish is worth up to 25 points: the same two
    programmes come out near 68 and 78."""
    from prestige import conf_finish
    prestige = E.U["prestige"]
    rec = s["record"]
    finish = conf_finish(E.U, rec)
    pull = {}
    for t in E.ROSTERS:
        r = rec[t]
        wins = r["W"]; margin = (r["PF"]-r["PA"])
        # recent success bump; champions/playoff teams recruit hotter
        success = wins*0.9 + margin*0.02
        pull[t] = PULL_PRESTIGE*prestige[t] + success*1.0 + PULL_FINISH*finish.get(t, 50.0) + s["heat"][t]*2.0
    return sorted(E.ROSTERS, key=lambda t: -pull[t]), pull


# Starting jobs by position: a recruit counts the players ahead of him who will still
# be there when he is (Fr/So/RS, and this cycle's earlier signees). Dan, 2039 end:
# playing-time recruiting. A 4-star does not sign into a room with two better, younger
# players already in it -- he goes where he can start.
STARTERS = {"QB": 1, "RB": 1, "WR": 3, "TE": 1, "OL": 5, "DL": 4, "LB": 3, "CB": 2, "S": 2, "K": 1, "P": 1}
YOUNG = ("Fr", "So", "RS")

CROWD_SKIPS = collections.Counter()      # diagnostics: picks redirected by playing time

def room_crowded(t, r, signed_here):
    """Would this recruit sit? True when the programme already has a full set of
    starters at his position who are at least as good and will outlast him."""
    need = STARTERS.get(r["pos"], 2)
    ahead = sum(1 for p in E.ROSTERS.get(t, []) if p["pos"] == r["pos"] and not p.get("_leaving")
                and p.get("cls") in YOUNG and p.get("abil", 0) >= r["abil"])
    ahead += sum(1 for x in signed_here if x["pos"] == r["pos"] and x["abil"] >= r["abil"])
    return ahead >= need

def run_recruiting(recruits, needs, s, seed=64010):
    rng = random.Random(seed)
    order, pull = signing_priority(s)
    signed_by_team = collections.defaultdict(list)
    remaining_need = dict(needs)
    # cap blue-chips per team so a handful of powers don't hoard the entire 4-5* pool,
    # but strongly concentrate them at the top of the pull order.
    pv = sorted(pull.values(), reverse=True)
    # concentrate the ~300 blue-chips among stronger programs; weak teams get 0-1.
    TIERS = E.U["tiers"]; CONF = E.U["team_conf"]

    def cap_for(t):
        """How many blue-chips a program can land.

        Ranked pull sets the base, but TIER matters independently and used not to be
        considered at all: an L6 program that got hot could out-recruit most of the P6,
        and the lower division's blue-chip share came out at 11.8% against a canon
        series running 4, 4, 3, 2, 3.2%. A strong L6 program does poach the occasional
        blue-chip -- that is the fun of it -- but it cannot recruit like a blueblood.
        """
        rank = order.index(t)
        if rank < 20:  base = 6   # bluebloods/hot teams load up
        elif rank < 45: base = 5   # 4 -> 5 at 2039 end: capacity lost to the tighter L6 windows
        elif rank < 75: base = 3   # 2 -> 3, same reason
        elif rank < 110: base = 1
        else: base = 0            # bottom third: essentially no blue-chips
        if TIERS[CONF[t]] == "L6":
            # the lower division competes for the leftovers, and only its very best
            # programs sign more than one
            # 2039 end: pull is results-heavy now and hot L6 programmes rank high on
            # it, so the windows tighten (25/92 -> 14/70) to hold the canon share
            base = 2 if rank < 14 else (1 if rank < 70 else 0)
        return base
    bluechip_cap = {t: cap_for(t) for t in order}

    # PHASE 1: blue-chips (4-5*), claimed strictly in pull order
    blue = sorted([r for r in recruits if r["stars"]>=4], key=lambda r:(-r["stars"],-r["abil"]))
    bc_signed = collections.defaultdict(int)
    bi = 0
    # multiple passes so top teams fill a full blue-chip haul before lesser teams get seconds
    while blue:
        progressed = False
        for t in order:
            if not blue: break
            if remaining_need[t] <= 0: continue
            if bc_signed[t] >= bluechip_cap[t]: continue
            # playing time: the best blue-chip left who would not be buried here
            pick = next((r for r in blue if not room_crowded(t, r, signed_by_team[t])), None)
            if pick is None: continue
            if pick is not blue[0]:
                CROWD_SKIPS[t] += 1          # he passed on at least one better room
            blue.remove(pick)
            pick["signed"] = t
            signed_by_team[t].append(pick)
            remaining_need[t] -= 1; bc_signed[t]+=1; progressed=True
        if not progressed: break
    # A blue-chip nobody had a starting job for still signs somewhere: with any programme
    # that has need and cap room, in pull order (he would rather sit at a big school than
    # go unsigned). Playing time decides where the fight is, not whether he plays at all.
    for t in order:
        while blue and remaining_need[t] > 0 and bc_signed[t] < bluechip_cap[t]:
            pick = blue.pop(0); pick["signed"] = t
            signed_by_team[t].append(pick); remaining_need[t] -= 1; bc_signed[t] += 1

    # PHASE 2: general pool (2-3*, 1*), teams fill remaining needs from a windowed board
    avail = sorted([r for r in recruits if r["signed"] is None], key=lambda r:(-r["stars"],-r["abil"]))
    # THE BLUE-CHIP CAP LEAK, fixed. `avail` is everyone still unsigned, which includes
    # any 4-5* phase 1 did not place, and the weights are `stars**2` -- so a blue-chip
    # that survived phase 1 was the most attractive thing on the board and phase 2 handed
    # it over with NO cap check at all. It has never actually fired, because every class
    # so far carried fewer blue-chips (287 in 2038) than the league's total cap capacity
    # (293), so phase 1 absorbed them all. It would fire the first year a class ran rich
    # at the top, or whenever need at the top of the order ran out before the pool did.
    # The cap is now enforced in both phases and `bc_signed` keeps counting through.
    while any(remaining_need[t] > 0 for t in order) and avail:
        progressed = False
        for t in order:
            if remaining_need[t] <= 0 or not avail: continue
            rank = order.index(t)
            win = max(4, int(6 + rank*0.9))
            at_cap = bc_signed[t] >= bluechip_cap[t]
            window = [r for r in avail if not (at_cap and r["stars"] >= 4)][:win]
            if not window: continue
            weights = [ (r["stars"]**2) + rng.gauss(0,0.6) for r in window ]
            pick = window[max(range(len(window)), key=lambda i: weights[i])]
            avail.remove(pick); pick["signed"]=t
            if pick["stars"] >= 4:
                bc_signed[t] += 1
            signed_by_team[t].append(pick); remaining_need[t]-=1
            progressed = True
        if not progressed:
            break
    return signed_by_team, avail

if __name__ == "__main__":
    s = SE.load_state()
    # compute needs
    sizes = {t: len(r) for t, r in E.ROSTERS.items()}
    leaving_by_team = collections.defaultdict(int)
    for t, r in E.ROSTERS.items():
        for pl in r:
            if pl.get("_leaving"): leaving_by_team[t]+=1
    # 63, not 62. `roster_final.ROSTER_MIN` is 63, so a 62 target left 151 of 152
    # programmes exactly one player short and stage 6 manufactured a walk-on for almost
    # every team in the league, every single year -- ~152 phantom players a cycle to
    # paper over a one-player disagreement between two constants, while hundreds of real
    # recruits went unsigned. Raised rather than lowering ROSTER_MIN so the spot goes to
    # an actual recruit. (Dan, 2038.)
    TARGET=63
    needs = {t: max(0, TARGET-(sizes[t]-leaving_by_team[t])) for t in E.ROSTERS}
    needs_total = sum(needs.values())
    n_total = national_class_size(s.get("season", 1), needs_total)
    recruits = make_class(n_total)
    from collections import Counter
    print("class star distribution:", dict(sorted(Counter(r["stars"] for r in recruits).items(), reverse=True)))
    print("national class:", len(recruits), "| roster spots open:", needs_total,
          "| will go unsigned:", len(recruits) - needs_total)
