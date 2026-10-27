# RFL 2043 schedule build: hand-off for a fresh conversation (26 Oct 2026)

State: 2042 season complete, 2043 offseason complete through the draft. Archive republished with the draft. Dan has finished choosing primetime games.

## What Dan decided (final, "we're good")
- Primetime desk artifact: https://claude.ai/artifact/7MgHs7s4b3QDRy8hb3rnEm (db doc `rfl/primetime2043`, version 83). Repo copy: `data/rfl_primetime_2043.json`.
- 60 primetime games (weeks 1-19: Thursday, Sunday night, Monday night; week 20: Thursday + two Sunday nights, no Monday) plus 7 pinned Sunday-afternoon games (G183 wk3, G199 wk2, G9 wk1, G348 wk19, G319 wk11, G7 wk20, G188 wk19).
- Two same-pair double primetimes were seen and kept: Commodores/Silverbacks (wk 8 Thu, wk 12 Mon) and Rangers/Sea Lions (wk 6 Mon, wk 18 SNF). Dan said fine.
- Format: 18 games / 20 weeks, exactly 2 byes (first in weeks 4-11, second in 12-18, at least 3 games between), no 3 home or 3 road in a row (byes do not reset), division rematches not in consecutive weeks. Rotation formula is in `rfl/matchups_engine.py`; `data/matchups_2043.json` (360 games G0-G359) matches the desk's ids exactly.

## Files ready in the repo (minigolfwiz/roiland-rfl)
- `data/matchups_2043.json`, `data/db/rfl/schedule2043.json` (67 fixed id->week entries from the desk: 60 primetime + 7 pins), `rfl/fill_anneal.py` (FIXW env var sets the penalty for moving a fixed game; default 2).
- `rfl/primetime_intrigue.py` made the star reasons (not needed for the build).

## Feasibility test already run (26 Oct)
`python3 rfl/fill_anneal.py 2043 <seed> 270` with FIXW=8, four seeds in parallel:
- seed 2: SOLVED with 0 rule violations but moved 2 fixed games: G92 (Hope at Redwoods, SNF wk19 -> wk6) and G183 (Renegades at Rangers, pin wk3 -> wk20).
- seeds 4 and 5: 0 fixed games moved but 2 clubs each left with one rule violation (cost 4). Seed 3: 1 moved, 1 violation.
- With the default FIXW=2 the solver moved 11 fixed games. Use FIXW=8 or higher.
- Plan: run more seeds / longer (e.g. 8 seeds, 600 s) and prefer a solution with zero moved primetime games. If a primetime pick must move, move a pin before a primetime game, and tell Dan exactly which game moved and why. Weeks 1-3 and 19-20 must have all 20 games (no byes), so those weeks are the tight ones.

## Steps for the new conversation
1. Restore: `add_repo minigolfwiz/roiland-rfl` (push), clone to `/home/claude/roiland-rfl`, copy to the working layout `/home/claude/rfl/{rfl,data,out}`; state via `engine.read_project_state('data/rfl_state_2042.z64')` (see `docs/rfl_restore_2042.md`).
2. Re-read the desk db doc (`ArtifactData get`, collection `rfl`, doc `primetime2043`) in case Dan changed anything after version 83; rebuild `data/db/rfl/schedule2043.json` from `prime` + `pins`.
3. Run the filler (see above) until a clean schedule is found. Output: `data/schedule_2043.json` and `data/db/rfl/schedule2043_filled.json`.
4. Build `rfl_broadcast_slots_2043.json` from the desk picks (shape as `claude/rfl_broadcast_slots_2042.json`: `{year, note, slots: {week: {thu, snf, mnf | snf2}}}` with "Visitor at Host" strings).
5. Fill the existing Schedule Office artifact (https://claude.ai/artifact/9Ta63BvZSLGk8z7WTZNF4V, db doc `rfl/schedule2043`, shape `{year, weeks:[{id, week}], saved}`) so Dan can look at it.
6. Check how 2042 loaded the schedule and slots into the season (`rfl/season.py`, `rfl/weekly.py`, `rfl/build_page.py`) and update any hard-coded 2042 names for 2043 (state file name, page template, slots file). Publish a new 2043 Season page (new artifact; keep the 2042 page).
7. Standing rules: ratings stay invisible in narrative; one playoff round at a time with stop-and-report; previews name venue and series history; report any prime-time flex (from week 15, a Sunday night can be swapped if both clubs are under .500 and one is out of its division race); give reasons when someone retires early.
8. Project is at its 2 MB cap: repo-only files are `rfl_2042_season.json`, 2043 draft picks and book, `rfl_primetime_2043.json`. Ask Dan to clear space before writing new project docs.
