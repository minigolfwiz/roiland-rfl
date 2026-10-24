import sys; sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E, sandbox_scoring as SB
# Absorb the scouting gain on the completion-lift knob, which is the constant that was
# raised to reach 24.4 in the first place. Scouting should change the DISTRIBUTION of
# points, not the league's level.
for v in (0.055, 0.040, 0.030, 0.022):
    E.CAL_COMP_BASE = v
    print("  CAL_COMP_BASE %.3f -> pts/team %.2f"%(v, SB.run(240)["pts_per_team"]))
