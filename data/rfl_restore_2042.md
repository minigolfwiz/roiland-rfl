# RFL restore recipe (updated 23 Oct 2026, after the 2042 Mega Bowl and awards)

The cloud workspace can be wiped between sessions. Nothing is safe unless it is in this project, the published 2042 Season page, or the GitHub repo `minigolfwiz/roiland-rfl` (now linked; Dan connected GitHub on 23 Oct 2026).

## Fastest restore: from GitHub
1. `add_repo minigolfwiz/roiland-rfl` (access: push), then clone it to `/home/claude/roiland-rfl`. It holds `rfl/*.py` (engine, game, season, build_page, weekly), `data/league.json`, `data/rfl_state_2042.z64` (compressed full state), `out/season_template.html`, and a README with the current status line.
2. Copy the repo to the working layout: `rfl/` package folder at `/home/claude/rfl/rfl/`, plus `data/` and `out/` next to it.
3. State: `engine.read_project_state('data/rfl_state_2042.z64')` then `save(S, 'data/state_2042.json')`.
4. For the Mega Bowl site (only needed in a Mega Bowl round): `data/mega_bowl_sites.json` with `{"sites": [...]}`. The full list lives in the project doc `claude/rfl_mega_bowl_sites.json` (rules, expansion dates, hosts through 2050). On 23 Oct 2026 a one-entry file for 2042 was used.

## Restore from project docs (if GitHub is unavailable)
1. `claude/code/rfl_engine.py` → `/home/claude/rfl/rfl/engine.py`; `rfl_game.py` → `game.py`; `rfl_season.py` → `season.py`; `rfl_build_page.py` → `build_page.py`; `rfl_weekly.py` → `weekly.py`. Also make `data/` and `out/` next to the `rfl/` package folder.
2. `claude/rfl_league_engine.json` → `data/league.json`. This is the trimmed league file the engine needs (divisions plus teams with conf, div, city, state, stadium). The older `claude/rfl_league.json` has no slug/nick fields and is only the 2041 matchup record; do not use it as `data/league.json`.
3. Season page template: `Artifact read` of the published RFL 2042 Season page (https://claude.ai/artifact/TJuPpLAZ8dm5X9JZwGj8mC) with `page: true` saves the full HTML locally. Strip everything up to and including the first `<body>` + newline and the trailing `</body></html>`, save as `out/season_template.html`. `build_page.py` splices only the `D` const and leaves the template's `BRAND` untouched (slugs, nicknames, colours, fonts, wordmarks).
4. State: copy `claude/rfl_state_2042.z64` to `data/`, then `engine.read_project_state(path)` and `save(S, 'data/state_2042.json')`.

## Routine for each stage
- Week: `cd /home/claude/rfl && python3 rfl/weekly.py N` (state, page build and compressed state in one go).
- Playoff round: `python3 rfl/season.py playoffs first|second|conference|megabowl`, then `write_project_state` and `python3 rfl/build_page.py`. Stop and report after each round; preview each round first (see rfl_notes.md for the preview standard).
- Awards: `SE.awards(S)` (regular-season stats only).
- After every stage: republish `out/rfl_season_2042.html` to the 2042 Season page URL, `project_write` `data/rfl_state_2042.z64` to `claude/rfl_state_2042.z64`, copy the z64 into the repo, update the README status line, commit and push.
- Never re-run a played week or round. `season.week_done` guards double-advance for weeks.

## Status
2042 season is COMPLETE (Champions: Costique Bearcats, Mega Bowl 17-10 over the San Saltadac Sea Lions, Tealcoat Stadium, Bruca Beach).
2043 offseason, steps done (each guarded by S['offseason']['done'] = close, retire, fa, trades, draft):
1. `python3 rfl/offseason.py close` (history + honours), `retire` (ageing + retirements; early retirees <=29 get a stated reason; starters <=30 and recent award winners have reduced hazard; Neraini's retirement was reversed by Dan).
2. `python3 rfl/freeagency.py` (re-sign, open market, street fill; then `fix_minimums`).
3. `python3 rfl/trades.py` (trades for 2043 picks; creates 2043 pick ownership; staff moves; syncs and updates `data/rfl_coaching.json` = project doc `claude/rfl_coaching.json`, which had been stale for 2042 hires).
4. `python3 rfl/draft.py` (2043 draft: order from 2042 results, pool `data/draft_pool_2043.json` from the college sim, 7 rounds, UDFAs, camp cuts to 53). Re-run with the QB premium on 24 Oct 2026 is canon.
History file now has `offseason_2043`, `draft_order_2043`, `draft_2043`. The 2042 season record is `data/rfl_2042_season.json` (repo only).
Next: republish the Archive (done with the draft), then the 2043 schedule build and season. Project docs are at the 2 MB cap: clear space before adding new docs.
