"""Generate fresh rosters (~62/team) with archetypes + hidden durability, and coaching staffs
with per-program patience profiles. Universe v2, Season 1 (fresh start)."""
import pickle, random, sys
sys.path.insert(0,'/home/claude/cfb')
from names import FIRST_NAMES, LAST_NAMES

with open('/home/claude/cfb2/state/universe.pkl','rb') as f:
    U = pickle.load(f)

rng = random.Random(770001)  # master generation seed (recorded)

ROSTER_TEMPLATE = [("QB",4),("RB",5),("WR",8),("TE",4),("OL",10),
                   ("DL",8),("LB",7),("CB",6),("S",5),("K",2),("P",2),("ATH",1)]
# ATH = flex athlete (returns/gadget), counts as WR-lite

ARCHETYPES = {
 "QB": [("Pocket Passer",.34),("Dual-Threat",.28),("Gunslinger",.18),("Game Manager",.20)],
 "RB": [("Power Back",.28),("Speed Back",.28),("All-Purpose",.30),("Short-Yardage Bruiser",.14)],
 "WR": [("Deep Threat",.26),("Possession",.30),("Slot Technician",.26),("Contested-Catch",.18)],
 "TE": [("Receiving TE",.40),("Blocking TE",.32),("Hybrid",.28)],
 "OL": [("Pass Protector",.36),("Run Mauler",.36),("Balanced",.28)],
 "DL": [("Edge Rusher",.36),("Run Stuffer",.34),("Interior Penetrator",.30)],
 "LB": [("Coverage LB",.30),("Run-Stopping LB",.40),("Blitzer",.30)],
 "CB": [("Shutdown",.25),("Ball-Hawk",.35),("Press",.40)],
 "S":  [("Center Fielder",.35),("Box Safety",.35),("Hybrid Safety",.30)],
 "K":  [("Big Leg",.45),("Accurate",.55)],
 "P":  [("Big Leg",.5),("Directional",.5)],
 "ATH":[("Return Ace",.6),("Gadget",.4)],
}
CLASSES = ["Fr","So","Jr","Sr","RS"]
CLASS_W  = [ .27, .25, .22, .18, .08]
CLASS_AB = {"Fr":-0.45,"So":-0.15,"Jr":0.12,"Sr":0.30,"RS":0.22}

def pick_arch(pos):
    r = rng.random(); acc = 0
    for a,w in ARCHETYPES[pos]:
        acc += w
        if r <= acc: return a
    return ARCHETYPES[pos][-1][0]

used_names = set()
def new_name():
    for _ in range(60):
        n = rng.choice(FIRST_NAMES)+" "+rng.choice(LAST_NAMES)
        if n not in used_names:
            used_names.add(n); return n
    # fallback middle initial
    while True:
        n = f"{rng.choice(FIRST_NAMES)} {chr(rng.randint(65,90))}. {rng.choice(LAST_NAMES)}"
        if n not in used_names:
            used_names.add(n); return n

def derive_attrs(pos, abil, arch, cls):
    """Sub-attributes on 1-10-ish scale derived from hidden ability + archetype flavor."""
    j = lambda s=0.55: rng.gauss(0, s)
    a = {}
    if pos == "QB":
        a["acc"] = abil + j(); a["arm"] = abil + j(); a["mob"] = 3.5 + j(1.0)
        if arch == "Dual-Threat": a["mob"] = abil*0.75 + 2.2 + j(0.6)
        if arch == "Gunslinger": a["arm"] += 0.9; a["acc"] -= 0.35
        if arch == "Game Manager": a["acc"] += 0.55; a["arm"] -= 0.5
        if arch == "Pocket Passer": a["acc"] += 0.25
    elif pos == "RB":
        a["run"] = abil + j(); a["spd"] = abil + j(0.8); a["hands"] = abil - 1.1 + j(0.9)
        if arch == "Power Back": a["run"] += 0.45; a["spd"] -= 0.6
        if arch == "Speed Back": a["spd"] += 0.9; a["run"] -= 0.2
        if arch == "All-Purpose": a["hands"] += 1.0
        if arch == "Short-Yardage Bruiser": a["run"] += 0.2; a["spd"] -= 1.2
    elif pos in ("WR","TE","ATH"):
        a["hands"] = abil + j(); a["spd"] = abil + j(0.8); a["route"] = abil + j()
        if arch == "Deep Threat": a["spd"] += 1.0; a["hands"] -= 0.35
        if arch == "Possession": a["hands"] += 0.7; a["spd"] -= 0.5
        if arch == "Contested-Catch": a["hands"] += 0.45
        if arch == "Blocking TE": a["route"] -= 1.0; a["blk"] = abil + 0.8 + j()
        if pos == "TE": a["spd"] -= 0.8
    elif pos == "OL":
        a["pblk"] = abil + j(); a["rblk"] = abil + j()
        if arch == "Pass Protector": a["pblk"] += 0.55
        if arch == "Run Mauler": a["rblk"] += 0.55
    elif pos == "DL":
        a["rush"] = abil + j(); a["rdef"] = abil + j()
        if arch == "Edge Rusher": a["rush"] += 0.7; a["rdef"] -= 0.3
        if arch == "Run Stuffer": a["rdef"] += 0.7; a["rush"] -= 0.3
        if arch == "Interior Penetrator": a["rush"] += 0.25
    elif pos == "LB":
        a["tkl"] = abil + j(); a["cov"] = abil - 0.8 + j(); a["rush"] = abil - 1.0 + j()
        if arch == "Coverage LB": a["cov"] += 1.1
        if arch == "Blitzer": a["rush"] += 1.3
        if arch == "Run-Stopping LB": a["tkl"] += 0.6
    elif pos in ("CB","S"):
        a["cov"] = abil + j(); a["tkl"] = abil - 1.0 + j(); a["ball"] = abil - 0.5 + j(0.9)
        if arch == "Shutdown": a["cov"] += 0.8
        if arch == "Ball-Hawk": a["ball"] += 1.0
        if arch == "Box Safety": a["tkl"] += 1.1; a["cov"] -= 0.4
        if arch == "Center Fielder": a["ball"] += 0.5
    elif pos == "K":
        a["leg"] = abil + j(0.7); a["accy"] = abil + j(0.7)
        if arch == "Big Leg": a["leg"] += 0.9; a["accy"] -= 0.3
        if arch == "Accurate": a["accy"] += 0.7
    elif pos == "P":
        a["leg"] = abil + j(0.7); a["ctl"] = abil + j(0.7)
        if arch == "Big Leg": a["leg"] += 0.9
        if arch == "Directional": a["ctl"] += 0.8
    return {k: round(max(0.5, min(10.0, v)), 2) for k, v in a.items()}

rosters = {}
pid_counter = 0
for team in U["teams"]:
    p = U["prestige"][team]
    talent_base = 4.15 + (p/100)*3.3          # ~4.8 (P21) to ~7.4 (P98)
    players = []
    for pos, n in ROSTER_TEMPLATE:
        for _ in range(n):
            cls = rng.choices(CLASSES, weights=CLASS_W)[0]
            abil = rng.gauss(talent_base + CLASS_AB[cls], 1.05)
            # rare gems everywhere; rare busts at bluebloods
            if rng.random() < 0.015: abil += rng.uniform(1.2, 2.4)
            abil = max(1.5, min(9.95, abil))
            arch = pick_arch(pos)
            pid_counter += 1
            players.append({
                "pid": pid_counter, "name": new_name(), "team": team, "pos": pos,
                "cls": cls, "arch": arch, "abil": round(abil, 2),
                "dur": round(max(0.15, min(0.95, rng.gauss(0.62, 0.15))), 3),  # HIDDEN
                "rep": 0.0,   # reputation feedback state (Phase 2)
                "inj_hist": [],
            })
    rosters[team] = players

# ---- coaches ----
COACH_ROLES = ["HC","OC","DC"]
coaches = {}
for team in U["teams"]:
    p = U["prestige"][team]
    staff = {}
    for role in COACH_ROLES:
        skill = max(1.0, min(9.5, rng.gauss(4.9 + (p/100)*1.3, 1.35)))
        tenure = rng.choices([0,1,2,3,4,5,6,8,10,13,17], weights=[14,13,13,12,11,9,8,8,6,4,2])[0]
        staff[role] = {"name": new_name(), "skill": round(skill,2), "tenure": tenure}
    # patience profile (spec 6): per program+coach
    base = rng.gauss(0, 1.0)
    tier_pressure = -0.85 if U["tiers"][U["team_conf"][team]] == "P6" else 0.0
    prestige_pressure = -max(0, (p-70))/38.0
    low_exp_patience = 0.55 if p < 40 else 0.0
    tenure_factor = -0.05 * max(0, staff["HC"]["tenure"] - 8)   # very long tenure: less rope when it sours
    patience = round(base + tier_pressure + prestige_pressure + low_exp_patience + tenure_factor, 3)
    staff["patience"] = patience
    staff["new_hire_protection"] = staff["HC"]["tenure"] < 2
    # program HFA base (spec 7): quality-correlated but randomized
    staff["hfa_base"] = round(max(0.8, min(4.5, rng.gauss(2.3 + (p/100)*1.3, 0.65))), 2)
    coaches[team] = staff

with open('/home/claude/cfb2/state/rosters.pkl','wb') as f:
    pickle.dump(rosters, f)
with open('/home/claude/cfb2/state/coaches.pkl','wb') as f:
    pickle.dump(coaches, f)
with open('/home/claude/cfb2/state/gen_seed.pkl','wb') as f:
    pickle.dump({"master_gen_seed": 770001}, f)

n_players = sum(len(v) for v in rosters.values())
print(f"players generated: {n_players} across {len(rosters)} teams ({n_players/len(rosters):.0f}/team)")
samp = rosters["Lornaman"]
best = sorted(samp, key=lambda x: -x["abil"])[:5]
print("\nSample - Lornaman top 5 by hidden ability:")
for pl in best:
    print(f"  {pl['name']:22s} {pl['pos']:3s} {pl['cls']:2s} {pl['arch']:22s} abil={pl['abil']} dur={pl['dur']}")
qbs = sorted([x for x in samp if x['pos']=='QB'], key=lambda x:-x['abil'])
print("QB room:", [(q['name'], q['arch'], q['abil']) for q in qbs])
import statistics
all_ab = [pl['abil'] for tm in rosters.values() for pl in tm]
all_dur = [pl['dur'] for tm in rosters.values() for pl in tm]
print(f"\nability: mean {statistics.mean(all_ab):.2f} sd {statistics.stdev(all_ab):.2f} | 9.0+ talents: {sum(1 for a in all_ab if a>=9.0)}")
print(f"durability: mean {statistics.mean(all_dur):.3f} sd {statistics.stdev(all_dur):.3f} min {min(all_dur)} max {max(all_dur)}")
print("\nSample coach + patience: Lornaman:", coaches['Lornaman']['HC'], "| patience:", coaches['Lornaman']['patience'], "| HFA:", coaches['Lornaman']['hfa_base'])
print("Sample: Stanton patience:", coaches['Stanton']['patience'], "| Harrell patience:", coaches['Harrell']['patience'])
