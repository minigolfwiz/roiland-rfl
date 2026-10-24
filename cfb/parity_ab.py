import sys; sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E, scouting as SC, parity_test as PT
# OLD model: no scouting, and the calibration it had before scouting went in
SC.ENABLE.update({"shift":False,"quick":False,"commit":False}); E.CAL_COMP_BASE=0.055
PT.show("OLD model  (blind play-calling)", PT.run(300))
print()
# NEW model
SC.ENABLE.update({"shift":True,"quick":True,"commit":True}); E.CAL_COMP_BASE=0.030
PT.show("NEW model  (offensive + defensive scouting)", PT.run(300))
