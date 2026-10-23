# roiland-rfl
Roiland Football League sim engine. Layout: `rfl/` (engine, game, season, build_page, weekly), `data/` (league.json, compressed state `rfl_state_2042.z64`), `out/season_template.html` (stripped copy of the published 2042 Season page).

Restore: `python3 -c "import sys; sys.path.insert(0,'.'); from rfl.engine import *; save(read_project_state('data/rfl_state_2042.z64'),'data/state_2042.json')"`, then `python3 rfl/weekly.py N`.
State is at the 2043 offseason: 2042 closed in history, ageing, retirements, free agency, trades and staff moves done; the 2043 draft is next.
