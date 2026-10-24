import sys; sys.path.insert(0,'/home/claude/cfb2')
import scouting as SC, sandbox_scoring as SB
print("baseline (scouting off): 25.07")
for pw,aw in ((0.16,0.14),(0.12,0.11),(0.16,0.0)):
    SC.PLAN_WEIGHT, SC.ADAPT_WEIGHT = pw, aw
    print("  PLAN %.2f ADAPT %.2f -> %.2f"%(pw,aw,SB.run(160)["pts_per_team"]))
