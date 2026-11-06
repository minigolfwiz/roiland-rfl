# RCBA (Roiland college basketball), Division I

Canon recorded 2026-11-06 from the RCBA season 5 PDF, aligned by Dan in the Map Office artifact.

Files
- `teams_conferences.json`: all 374 Division I schools with RCBA conference, RCFB conference, state, map position, mascot, season 5 record. Also the 32 conferences and their members.
- `final_four_history.json` / `final_four_standings.json`: every Final Four 1916 to 2021 (champion, runner-up, two semifinalists) and standings by team and by current conference.
- `RCBA_DivI_teams_conferences.xlsx`: the same data as sheets, plus geography stats per conference.
- `map_changes_not_yet_in_cfb.json`: map changes made during the alignment that have not been applied to the CFB universe yet (read before touching `cfb/state/map_placements.json`).

Structure
- 374 schools: the 369 CFB schools plus 5 RCBA-only schools with no football (Crayellan Ag, Coachville Rev, Fiota Catskill, East Costique Int, Eternal Fox JC).
- 32 conferences: the 12 RCFB conferences (same names) and 20 RCBA-only conferences named by Dan. Sizes are uneven on purpose after Dan's moves.
- The PDF had no conference names. The first groupings were inferred from page layout and round-robin completeness. Dan then moved 51 schools between conferences in the Map Office.

Naming rules (Dan)
- A name ending in "St" becomes "State", except South Antiragal St, which keeps "St" (the old "South Antiragal State" and "S Antiragal State" spellings are now "South Antiragal St").
- No periods in team names (the mascot "St. Bernards" keeps its period).
- Kro Magloire has no "St". Ro is "Koli Ro". Eternal Fox JC and Crayellan Ag are correct as written.
- Marines is the only team with no mascot. Formal name: The Academy of Marines.
- Mascots come from the CFB school list wherever a school exists there. The PDF grid matched it for all 374.
- The directory pages inside the RCBA PDF are very old. Do not trust them.

Final Four notes
- Conference standings use today's alignment, not the alignment at the time.
- Dan's original list had 1982 twice. The top 1982 became 1983 and every later year moved up one, so the history ends in 2021 (Eternal Fox over Will Tech).
- KLC in Dan's list is Keeper.
- Hennington appears in the PDF schedule as a neutral-site opponent three times (Nov 23, 25, 27) but has no team column. Dan does not recognize it; treated as filler, not a team.

Map placement decisions
- Forrester moved from Diveo to northwestern Stanton (266.0, 457.0).
- Chorrisaw moved 1.05 units north from Orlot into Stanton so all 12 Stanton Valley schools are in Stanton.
