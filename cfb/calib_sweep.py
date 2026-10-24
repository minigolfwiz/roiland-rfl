import sys; sys.path.insert(0,'/home/claude/cfb2')
import scouting as SC, sandbox_scoring as SB
combos=[("all off",{"shift":False,"quick":False,"commit":False}),
        ("shift only",{"shift":True,"quick":False,"commit":False}),
        ("quick only",{"shift":False,"quick":True,"commit":False}),
        ("commit only",{"shift":False,"quick":False,"commit":True}),
        ("all on",{"shift":True,"quick":True,"commit":True})]
for label,cfg in combos:
    SC.ENABLE.update(cfg)
    r=SB.run(160)
    print("  %-12s pts/team %.2f"%(label,r["pts_per_team"]))
