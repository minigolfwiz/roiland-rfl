# roiland-rfl
Roiland Football League sim engine. Layout: `rfl/` (engine, game, season, build_page, weekly), `data/` (league.json, compressed state `rfl_state_2042.z64`), `out/season_template.html` (stripped copy of the published 2042 Season page).

Restore: `python3 -c "import sys; sys.path.insert(0,'.'); from rfl.engine import *; save(read_project_state('data/rfl_state_2042.z64'),'data/state_2042.json')"`, then `python3 rfl/weekly.py N`.
State is at 2042 week 9 played; week 10 is next. See the claude.ai project doc `claude/rfl_restore_2042.md` for the full recipe.
