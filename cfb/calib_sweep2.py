import sys, importlib; sys.path.insert(0,'/home/claude/cfb2')
import scouting as SC, sandbox_scoring as SB
SC.ENABLE.update({"shift":True,"quick":True,"commit":True})
print("baseline (scouting off): 25.07 on this 160-game slate")
for pw,aw in ((0.16,0.14),(0.10,0.09),(0.07,0.06),(0.05,0.04),(0.03,0.03)):
    SC.PLAN_WEIGHT, SC.ADAPT_WEIGHT = pw, aw
    r=SB.run(160)
    print("  PLAN %.2f  ADAPT %.2f -> pts/team %.2f"%(pw,aw,r["pts_per_team"]))
