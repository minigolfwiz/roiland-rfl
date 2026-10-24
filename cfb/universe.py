"""Roiland CFB Universe v2 - foundation. Fresh start; no prior season history."""
import pickle, sys
sys.path.insert(0,'/home/claude/cfb')  # only to import static team/conference definitions
from data2 import conferences, tiers

with open('/home/claude/cfb/team_prestige.pkl','rb') as f:
    prestige = pickle.load(f)
with open('/home/claude/cfb/team_geo.pkl','rb') as f:
    team_geo = pickle.load(f)
with open('/home/claude/cfb/school_directory.pkl','rb') as f:
    directory = pickle.load(f)
with open('/home/claude/cfb/map_data.pkl','rb') as f:
    STATE_COORDS, ADJ = pickle.load(f)
with open('/home/claude/cfb/s3_fixed_pairs.pkl','rb') as f:
    FIXED_PAIRS = pickle.load(f)  # user-mandated rivalry week + fixed-week matchups (universe rules)

team_conf = {}
for conf, tl in conferences.items():
    for t in tl: team_conf[t] = conf

teams = sorted(team_conf.keys())
assert len(teams) == 152

UNIVERSE = {
    "teams": teams, "conferences": conferences, "tiers": tiers, "team_conf": team_conf,
    "prestige": prestige, "geo": team_geo, "directory": directory,
    "state_coords": STATE_COORDS, "state_adj": ADJ, "fixed_pairs": FIXED_PAIRS,
}
if __name__ == "__main__":
    with open('/home/claude/cfb2/state/universe.pkl','wb') as f:
        pickle.dump(UNIVERSE, f)
    print("universe.pkl written:", len(teams), "teams,", len(conferences), "conferences,",
          sum(len(v) for v in directory.values()), "directory schools,", len(FIXED_PAIRS), "locked matchups")
