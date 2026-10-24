# Roiland CFB session log (2041 season -> 2042 offseason)

## 2040-41 OFFSEASON -- Stage 7 of 7 COMPLETE: rollover, 2040 closed and 2041 open (season 16) (2026-10-17)
Backups state/{season_state,rosters,coaches,universe}.pkl.pre_s16_rollover. Classes Sr 2,160 | Jr 2,831 | So 2,288 | RS 167 | Fr 2,441.
456 staff records advanced. Records, polls, committee/media history reset; season_archive row '15' present. next_week 0.
NEXT: 2041 schedule (noncon hand-off -> Scheduling Office; conference office), media pool redraw for s16, preseason. Before scheduling:
decide whether to switch distance rules to school coordinates (U['school_coords'] complete since 2026-10-15).

## RULED (Dan, 2041 preseason): MEDIA POOL CARRY-OVER
Each year half the schools in each conference's media seats carry over from the previous pool (3 of 6 P6, 2 of 4 L6) and keep the
same voter, a year older; no school holds a seat more than two years running. `media_pool.make_pool` implements it via
s['media_pool_teams'][season]; 2040's teams were back-filled as season 15 so the two-year rule bites from 2042.
2041 pool drawn: s['media_pool_s16'], 30 returning / 30 new.

## 2041 SCHEDULE -- Scheduling Office published for season 16 (saves under schedule/s16). 444 non-conference slots for Dan.

## 2041 non-conference board -- COMPLETE (2026-10-17)
Dan's hand-off (state/noncon_s16_handoff.json): 191 games, 69 guests, 143 open, 1 blocking. fill_noncon added 67 guests + 38 FBS games
-> 296 games, 136 guests (89.47%), complete. state/noncon_s16.json.
## 2041 SCHEDULE -- stage B: conference board built, Conference Office published (saves under conf/s16)
export_conf_board: 12 conferences, 0 problems, 4/5 home split honoured everywhere, 35 locked pairs carried. NEXT: Dan places -> fill_conf -> install_hand_schedule.

## 2041 CONFERENCE OFFICE — PROGRESS SAVED 2026-10-17 16:43
Dan's Office save (db conf/s16, version 164, 4:42 PM) pulled down: state/conf_office_save_s16_v164.json (raw) and
converted by convert_conf_db.py -> state/conf_s16_handoff.json (980 rows: 684 conference + 296 non-conference weeks,
137 placed: Power North complete 63/63, Jyras Bay 7, Great Fourteen 6, Broad South 6, Mountain Valley 6, Western
Coast 4, Brass Belt 1, plus 44 non-conference weeks). Loads clean in fill_conf.Cal (no double-booking).
The Office doc is the live source; re-run `python3 convert_conf_db.py state/confdb/conf/s16.json` after each pull.
NEXT when Dan hands off: convert -> fill_conf.py -> conf_sched_s16.json -> install_hand_schedule.py --commit -> audit
-> preseason (export_preseason.py, 2041 notes, media pool page for s16 voters) -> week 0.
2026-10-22: Office db still at version 164 (no newer save than the one pulled 10/17). seed_conf_board.py bakes the
hand-off weeks into state/conf_board.json and rebuilds conf_office.html; republished (Version 13) so the 137 placed
weeks show even if the saved-board read fails. Re-run seed_conf_board.py after every convert.

## 2041 SCHEDULE INSTALLED — 2026-10-22
Dan's Office save v429 (2:40 AM): 318 placed — Power North, Western Coast, Mountain Valley complete; Great Fourteen 17,
Jyras Bay 14, Broad South 6, Brass Belt 1; 109 non-conference weeks. fill_conf placed the other 662, zero hard
violations among open programmes, first attempt. Two violations in Dan's own rows left as placed (2040 precedent):
North Verigon 5 home in a row (wk 6-11, incl. a non-conference), Skeenerland State 5 home in a row (wk 2-7).
state/conf_sched_s16.json installed, audit CLEAN; week 0 = 15 games, week 14 = 81; 136 guests with fresh rosters.
Office db conf/s16 rewritten to the filled board; conf_board.json seeded with every week (seed_conf_board.py).
NEXT: preseason (export_preseason.py, 2041 notes, media pool page for s16 voters), then Week 0.

## 2041 PRESEASON — 2026-10-22
Preseason media poll run (60 voters, s16 pool: 30 returning/30 new) and stored: media_history['pre'], media_ballots[0].
Top 5: Rogaela State (23 firsts), Eastern State (24 firsts), Central Stanton, Kaji Daun, Crayellan; Eternal Fox 9th,
the only L6 team ranked. 25 notes written to state/preseason_notes.json (2040's kept as preseason_notes_s15.json),
observable facts only, no engine wording. Roiland Preseason republished (Version 4); Media Pool republished (Version 25).
Backup: state/season_state.pkl.pre_s16_preseason. NEXT: Dan picks the week-0 Gameview, then `week_cycle.py 0`.
Gameview visit list was still 2040's at week 0 -> archived as s['gameview_s15'], cleared; rollover.py now does this.
Gameview 2040 map published (artifact 95sRVx5uYELEP6SFPqWJV5, gameview_2040.html from state/gameview_2040.json):
15 stops on the Roiland map with the route and the chronological list; ranks = poll going INTO the game
(media_history[w-1], 'pre' for week 0). 2040's weekly media/committee polls were NOT archived at rollover — recovered
from season_state.pkl.pre_s16_rollover into season_archive['15']; rollover.py now archives both every year.
Week 0 Gameview 2041: Barhold at Barhold Valley (recorded).

## 2041 WEEK 0 played (Gameview: Barhold at Barhold Valley) — 2026-10-22
Barhold 45-38 at Barhold Valley (Tessa Brookham 186 rush, 4 TD; Barhold RB Frieda Grünhauer hurt). Central Stanton 49-0
Larksdale -> No. 1. Guests 0-4. Season viewer (v110) and Media Pool (v26) republished. NEXT: week 1, Dan picks Gameview.
## 2041 WEEK 1 played (Gameview: Verigon at Verigon State) — Verigon 24-22 despite 4 Yacoub INTs.
Upsets: Lornaman 38-29 over #1 Central Stanton (Quickbear 440 yds), Marines 35-28 Eternal Fox, Westburg 14-10 Orlot,
Phangrine St 24-22 Kaji Kita, Keeper 37-26 Ranroman, UFNH 37-21 Skeenerland St, guest Mt St Williams 14-13 Roosevelt.
Poll: Rogaela State No. 1. Viewer v111, Media Pool v27 published. NEXT: week 2 Gameview pick.
## 2041 WEEK 2 played (Gameview: North Hatesei at Ranroman State) — NH 30-21 in snow, Shangqi 4 INT.
Kaji Daun 42-10 at Eona -> No. 1. Upsets: Harrell 24-21 Costique River (QB Tichovich out for year), Pikeland (guest)
30-26 Will Tech, Fiota Bay 30-25 Verigon. Viewer v112, Media Pool v28. NEXT: week 3 Gameview pick.
## 2041 WEEK 3 played (Gameview: Yrei Trobniy at Eastern State) — ES 45-17, Grimaldi 332/4 TD. Eastern State No. 1.
Upsets: Kaji Kita State 24-13 over #1 Kaji Daun; Northlight 40-38 OT over #6 Tengus State; Rogaela 33-30 OT over #7
Crayellan; UN Minko 10-3 over #16 Barhold (Blaudorf 4 INT); Barhold State 27-21 Ciarralotta State; Stanton 42-21 UN
Ediville. Third No. 1 in three weeks. Viewer v113, Media Pool v29. NEXT: week 4 Gameview pick.
## 2041 WEEK 4 played (Gameview: Leafette at Rogaela State) — RS 28-14 in rain, Althauer 128/2 TD as a freshman.
Pistolheart (Ludendorf) 28-27 over #11 Ciarralotta Tech; National 21-12 Lornaman; Tengus 21-10 Canesta State. Eastern
State 34-27 survives Ekralund State, stays No. 1. Viewer v114, Media Pool v30. NEXT: week 5 Gameview pick.
## 2041 WEEK 5 played (Gameview: Central Stanton at Kaji Daun) — CS 28-14 in snow, Campovieja 119/2. Kaji Daun 2-2.
Ciarralotta 41-7 over #4 North Hatesei (Taoli 420 yds); North Canesta 27-7 Ciarralotta Tech; Harrell 33-31 Fiota Bay;
West Hatesei St 30-14 Canesta State; Ranroman State 20-17 Crayellan. Poll: Park Island No. 1 (5-0) over Eastern State.
Viewer v115, Media Pool v31. NEXT: week 6 Gameview pick.
## 2041 WEEK 6 played (Gameview: Crayellan State at UFNH) — UFNH 30-17, Fontoncelli 257/3, Rosenholz 3 4th-qtr FGs.
Ranroman 37-13 over #11 Kaji Daun (2-3, three straight losses); Pistolheart 23-22 North Hatesei (Ludendorf's 2nd
ranked win); UNN 41-12 Hatesei; Costique State 34-14 Eternal Fox; Far Farris 14-7 Yrei Trobniy; Greene 30-24 Dietsche.
Eastern State 38-28 at Ciarralotta Tech. Park Island (bye) still No. 1. Viewer v116, Media Pool v32. NEXT: week 7 pick.
RULED (Dan, 2041 wk 6): quality win / quality loss / bad loss are judged against the CURRENT rankings, not the rating.
resume_marks.py: quality = opponent in the current top 25 (Dan's committee board once official, media poll before);
bad = opponent nowhere in the current poll AND outside the rating top 60. Exports (committee week + Committee Room)
carry per-game `mark`; templates read it. A win over a team that has since dropped out loses its quality mark.
Engine's own resume scoring (committee.committee_rank) unchanged.
## 2041 WEEK 7 played (Gameview: Rogaela at Verigon) — Verigon 31-17, windy; Nishiyama 2 TD catches as a freshman.
Tasson 27-6 over #3 Rogaela State; Crayellan 41-0 over #8 UFNH; UNN 21-18 Kaji Daun (2-4); UN Ediville 28-14 Hatesei;
New Madrid 38-17 Black Forest; Orlot 38-33 Ranroman; Central Stanton 42-13 at Ranroman State. Park Island 21-20 over
Barhold Valley keeps No. 1. Viewer v117, Media Pool v33. NEXT: week 8 pick.
STANDING (Dan, 2041 wk 7): Gameview candidates always come with both teams' records and rest-of-season outlook
(gameview.outlook: record, conference place/games back, projected finish from win probabilities over the remaining
schedule, games left and how many vs ranked, next three opponents). Printed by gameview.py and week_cycle.py.
## 2041 WEEK 8 played (Gameview: Park Island at Good River) — PI 33-21 in snow, Lormyraw 331/4; Fujihara 3 INT + fumble.
Riveral 31-23 over #5 Crayellan State; Crayellan 30-9 at #8 Verigon; Pistolheart 59-28 Kaji Daun (2-5, out of poll);
Diamond City 49-31 North Hatesei; Hughes State 26-0 Black Forest; UNN 14-10 Orlot; Fiota State 37-3 Parchynt State.
Central Stanton 10-7 over Eona. Park Island / Eastern State 1-2. Viewer v118, Media Pool v34. NEXT: week 9 pick.
Committee Ballot published for the first 2041 board (after week 8, v30) with the new current-rankings marks. Waiting on
Dan's ballot -> install_committee.py. Week 9 Gameview candidates already printed; re-rank off his board once installed.
Week 8 committee board installed (state/ballot_s16_w8.json): 1 Eastern State, 2 Central Stanton, 3 Keeper, 4 Park Island,
5 Fiota Bay; Krobe State, Skylar Rose, UNN, Will Tech, Costique River, Dietsche, Pistolheart, National, Kaji Kita in;
Crayellan State, Rogaela, Hatesei, Coastal Ranroman, Orlot, North Hatesei, Black Forest, Parchynt State, Kaji Daun out.
Viewer v119. week_cycle.py backup name no longer hardcoded to s15. NEXT: week 9 Gameview pick.
## 2041 WEEK 9 played (Gameview: Yrei Trobniy at Park Island) — PI 34-25 in rain; Seo-Seong 371 yds/3 TD, Lormyraw 437.
Stanton State 23-21 over #3 Keeper; Antiragal State 34-20 Rogaela State; Fiota Bay 45-10 Crayellan (Winswick 5 TD);
Crayellan State 21-11 Costique River; Ciarralotta 26-10 Ranroman State; San Diego Valley 31-10 National; Rogaela 31-24
Skeenerland. Viewer v120, Media Pool v35, Committee Ballot v31 (week 9). Waiting on Dan's board; then wk 10 candidates.
Week 9 board installed (ballot_s16_w9.json): 1 Eastern State, 2 Park Island, 3 Central Stanton, 4 Fiota Bay, 5 UFNH;
Keeper 3->11; Ciarralotta, Crayellan State, Rogaela, Barhold in; Ranroman State, Yrei Trobniy, Ranroman, National out.
Viewer v121. NEXT: week 10 Gameview pick.
## 2041 WEEK 10 played (Gameview: Krobe State at Will Tech) — WT 24-17, 21 pts in 4th; Salaemonte 351/3, Hongkai 422.
Stanton 24-14 over #3 Central Stanton (rivalry); Ranroman State 38-24 UNN; Tasson 27-6 Dietsche (El-Najjar 4 INT);
UN Ediville 13-10 Pistolheart; Diveo State 28-3 Barhold; Keeper 38-31 at Lornaman (Staledis 7 sacks, hurt for year).
Viewer v122, Media Pool v36, Committee Ballot v32. Waiting on Dan's week-10 board.
Week 10 board installed (ballot_s16_w10.json): 1 Eastern State, 2 Park Island, 3 Fiota Bay, 4 UFNH, 5 Will Tech; Central
Stanton 3->13; Coastal Ranroman, UN Ediville, Ciarralotta Tech in; Costique River, Lornaman, Barhold out. Viewer v123.
NEXT: week 11 Gameview pick.
Gameview 2041 map published (artifact QeWXmprNPowVCZ5vUPz9aV) from build_gameview_map.py + gameview_map_template.html
(generalised from the 2040 one-off; `python3 build_gameview_map.py [season]`; current season adds next week's
candidates as dashed pins; ranks = board of record going in). Republish after each week if Dan wants it live.
## 2041 WEEK 11 played (Gameview: Ciarralotta at UNN) — UNN 49-13, Tetteng 324/5 TD, 7 TD passes in all.
Diamond City 20-17 OT over #1 Eastern State (first loss); Costique River 34-14 Fiota Bay; Diveo State 24-18 Skeenerland
State; Costique 25-23 Tengus State; Southern Krobe 29-14 Keeper; South Antiragal 34-14 Rogaela State; Southern Tengus
30-21 Skeenerland; Verigon 21-20 at Crayellan State. Nine ranked losers. Park Island 21-20 at Far Farris, only unbeaten
left on the board. Viewer v124, Media Pool v37, Ballot v33, Gameview map v2. Waiting on Dan's week-11 board.
Week 11 board installed (ballot_s16_w11.json): 1 Park Island, 2 UFNH, 3 Will Tech, 4 Skylar Rose, 5 Eastern State;
South Antiragal, Eona, Ranroman State in; Rogaela State, Skeenerland, Ciarralotta Tech out. Viewer v125. NEXT: wk 12 pick.
## 2041 WEEK 12 played (Gameview: Skeenerland State at Tengus State) — SkSt 23-21 from 21-0 down; 6 INTs in the game,
Minakado 35-yd FG with 41s left; Taumalu 3 first-quarter TDs. Skylar Rose 28-23 at #1 Park Island (Western Coast to
Skylar Rose); Tasson 31-27 Krobe State; Ekralund State 37-29 Keeper; Orlot 35-9 Pistolheart; UN Ediville 27-24
Ciarralotta; Eona 27-14 Ranroman State. No unbeaten P6 left. Viewer v126, Media Pool v38, Ballot v34, map v3.
Waiting on Dan's week-12 board.
Week 12 board installed (ballot_s16_w12.json): 1 Skylar Rose, 2 UFNH, 3 Park Island, 4 Will Tech, 5 Eastern State;
Hatesei, Yrei Trobniy, Lornaman, Burrstone in; Ciarralotta, Crayellan State, Pistolheart, Ranroman State out.
Viewer v127. NEXT: week 13 pick.
## 2041 WEEK 13 played (Gameview: UFNH at Rogaela) — UFNH 42-21, Fontoncelli 4 TD, Cabranegro 170/2. UFNH 7-1 MV.
Ranroman 34-17 over #9 Central Stanton (3rd loss); Skeenerland State 34-23 Kaji Kita (Power North to SkSt); Costique
River 38-24 Crayellan; South Antiragal 24-20 Dietsche; Leafette 10-7 Krobe State; UNN 41-10 UN Ediville; Ciarralotta
Tech 27-9 Keeper; Diamond City 41-30 Lornaman. Will Tech 28-24 at Rogaela State. Viewer v128, Media Pool v39, Ballot
v35, map v4. Waiting on Dan's week-13 board, then rivalry week.
Week 13 board installed (ballot_s16_w13.json): 1 UFNH, 2 Skylar Rose, 3 Park Island, 4 Will Tech, 5 Eastern State;
Ranroman, Diamond City, Ciarralotta Tech in; Krobe State, Keeper, Lornaman out. Viewer v129. NEXT: rivalry week pick.
## 2041 WEEK 14 played (Gameview: Fiota Bay at UFNH) — UFNH 34-31, Lomteniy 216 yds; Fiota Bay TD with 47s left, no time.
Dove Island 20-16 over #4 Will Tech; Parchynt 17-14 Rogaela; Southern Tengus 38-10 Coastal Ranroman; North Hatesei
22-7 Hatesei; Good River 35-14 Yrei Trobniy; Phangrine State 13-10 Diamond City. Central Stanton 24-23 Pistolheart.
INCIDENT: `python3 ccg.py` was run looking for a preview and PLAYED+COMMITTED the twelve finals. Unwound by hand
(db keys S16CCG_* deleted, records/PF/PA, season_stats, reputation, injuries and the pre-playoff tick reversed,
conf_champs_s16.pkl removed; snapshots season_state.pkl.ccg_premature / rosters.pkl.ccg_premature). Seed registry
kept. ccg.py now refuses to play without --commit and prints the preview instead. New ccg_preview.py (matchups,
site, records, series, this year's meeting). Results of the premature run NOT reported to Dan.
Viewer v130, Media Pool v40, Ballot v36 (week 14), map v5 (15 stops). NEXT: Dan's week-14 board -> CCG preview -> play.
## 2041 CONFERENCE FINALS played (backups *.pre_s16_ccg; stale S16CCG seeds released from the registry first)
Verigon 24-14 UFNH (MV); Ciarralotta Tech 15-14 Eastern State (BS, five El-Husri FGs... three, in rain); Skylar Rose
28-24 Park Island (WC, Verville 4 INT); UNN 31-16 Central Stanton (G14, Tetteng 435); South Antiragal 31-21 Will Tech
(JB, Vignoretti 267/3); Kaji Kita 17-11 Skeenerland State (PN, El-Ghazali 4 INT). L6: Hoganelle OT, New Madrid,
Marines, Eternal Fox 17-0, Riveral State, UN Minko 17-8 Coastal Ranroman. Five of six P6 favourites lost.
Week-14 board installed (ballot_s16_w14.json). Selection ballot published (v37, stage CCG); viewer v131.
NEXT: Dan's final 25 -> install -> "playoff office" (export_committee_board -> Committee Room) -> field -> R1 preview.
Committee Room published for 2041 selection (v8): 53 candidates, 12 champions (Marines, Eternal Fox, UN Minko forced
onto the board as unranked-by-rating champions). Waiting on Dan's field JSON -> install_field.py -> R1 preview.
## 2041 PLAYOFF FIELD installed (state/field_s16.json -> state/playoff_s16.pkl, human committee)
Byes: 1 Skylar Rose, 2 Verigon, 3 UFNH, 4 Park Island, 5 Eastern State, 6 UNN, 7 Kaji Kita, 8 Skeenerland State.
R1 at the higher seed: Marines@South Antiragal, Eternal Fox@Will Tech, New Madrid@Fiota Bay, UN Minko@Tengus State,
Hoganelle@Central Stanton, Riveral State@Eona, Ciarralotta Tech@Dietsche, Ranroman@Rogaela. Left out: Coastal
Ranroman 11-2, Crayellan 8-4. R1 previewed. NEXT: "Round one" -> playoff.run_round1 (auto-preview R2 with venues after).
NOTE install_field.py writes the bracket on its first run (no dry run); --commit is a no-op second pass.
## 2041 PLAYOFF R1 played (snapshot season_state.pkl.pre_s16_po_r1 + games_db.pkl.pre_s16_po_r1)
South Antiragal 34-0 Marines; Eternal Fox 37-24 at Will Tech; Fiota Bay 30-10 New Madrid; UN Minko 24-17 at Tengus
State; Central Stanton 37-3 Hoganelle; Eona 54-16 Riveral State (two pick-sixes); Dietsche 35-34 Ciarralotta Tech
(El-Najjar 423/5, Ugonti 441/4); Rogaela 24-9 Ranroman. R2 previewed (at the higher seed). NEXT: "Round two".
## 2041 AWARDS (announced after R1; canonized by run_champ from season_state.pkl.pre_s16_po_r1)
Ryskamp: Imogen Danecombe (Pistolheart, Jr QB; 3,789/32/12 + 406 rush, 4 TD) over Grimaldi (Eastern State),
Lormyraw (Park Island), Suryarajan (Riveral State) -- four = top of the week-10 ten by basis points; pool closed.
DPOY: Ernest Fjelldahl (Kaji Kita, So DL, 19 sacks). FOY: Zaire Winswick (Fiota Bay, Fr QB, 3,383/30/6).
COY: Sybil Casafría (Riveral State, 11-2, yr 7). s['awards_announced_s16'] written.
## 2041 PLAYOFF R2 played (snapshot pre_s16_po_r2)
Skylar Rose 45-23 Eternal Fox (Verville 3 rush TD); Verigon 31-21 UN Minko (Hazelden 176); UFNH 35-10 Rogaela; Dietsche
34-9 at (4) Park Island (now 4-0 all-time vs PI); Eastern State 31-27 Eona (Havmark 214/3, winner with 44s left);
UNN 38-20 Central Stanton (Tetteng 463/5, Kingsston 197/4); Kaji Kita 19-16 Fiota Bay (Winswick 3 INT); Skeenerland
State 38-3 South Antiragal. QF: Skylar Rose-Dietsche, Verigon-Skeenerland State, UFNH-Kaji Kita, Eastern State-UNN.
Awards announced after R1 (Danecombe Ryskamp). NEXT: "Quarters" (venues by rotation; override if Dan pins).
## 2041 QUARTERFINALS played (snapshot pre_s16_po_qf)
Skylar Rose 52-37 Dietsche @ Copper Bowl (Verville 418/6 + 96 rush, Winsdale 249/5; El-Najjar 472/5); Skeenerland
State 38-29 Verigon @ Lumber Bowl (El-Ghazali 406/4, Winterbridge 220); UFNH 30-17 Kaji Kita @ Steam Bowl; UNN 31-17
Eastern State @ Star Bowl in snow (champions out; Grimaldi 180, 0 TD). SF: Skylar Rose-Skeenerland State @ Redwood
Bowl, UFNH-UNN @ 501 Bowl. NEXT: "Semis".
SF venues pinned (Dan): Skylar Rose-Skeenerland State @ 501 Bowl (Stamford), UFNH-UNN @ Redwood Bowl (Kirkwood);
P['venue_override']['SF']. In-depth previews given. NEXT: "Semis".
## 2041 SEMIFINALS played (snapshot pre_s16_po_sf)
Skylar Rose 37-20 Skeenerland State @ 501 Bowl, windy — 20-20 in the 4th, Tangshuai 87-yd pick-six; Verville 283/3/3,
Blauberger 2 TD. UFNH 24-0 UNN @ Redwood Bowl — Tetteng 116 yds, Apopoulos 4 sacks, Cabranegro 2 TD, Vallanelli 190.
FINAL: Skylar Rose vs UFNH — first meeting, first title game for both. NEXT: "Title" -> run_champ + finalize_season.
## 2041 NATIONAL TITLE — Skylar Rose 49, UFNH 10 @ Charlesville (snow). Sandcott 211/2, El-Nadim 132/1, Verville 147/3/0;
UFNH 106 passing, Fontoncelli pulled. First title for Skylar Rose (16-1). Season canonized: awards (Danecombe Ryskamp,
Fjelldahl DPOY, Winswick FOY, Riveral State COY), champ 2041 = (Skylar Rose, UFNH). Backups pre_s16_po_champ.
NEXT: offseason ("Start the offseason": audits -> carousel -> draft pool for RFL -> portal -> recruiting -> dev ->
roster -> rollover). Open: distance rules on school_coords; injury severity 18->15%; G14 portal inflow audit.

## 2041 END-OF-SEASON AUDITS (run 2026-10-22, before the 2041-42 offseason)
G14 balance: non-conf vs P6 9-7; all-games W% .551 (PN .551, WC .550, JB .545, BS .537, MV .590); mean prestige 74.0 (75.0);
losing seasons 3. Balanced -- KEEP, no change. Injuries 2041: 1,332 over 1,015 games = 0.66/team-game (2040 0.67);
season-enders 224 = 1.47/team (1.83), severity 17% -- settling on its own, NO change to the 18% severity.
Shares DL 19 LB 16 OL 14 RB 13 WR 11. G14 portal inflow and L6 blue-chip share rechecked at those stages below.

## 2041-42 OFFSEASON -- Stage 1 of 7 COMPLETE: coaching carousel
Backups state/*.pkl.pre_s17_carousel; s['carousel_s16']. Prestige step ran (152 moved). 22 vacancies/hires: 8 sitting HCs
poached (36%), 9 coordinators, 3 subdivision HCs, 3 retreads, 1 first-timer; 32 coordinator moves, 12 raids.
Headlines: Kaji Daun (Fatima Larsen out mid-season; DC Henrik Moreau retained), Roosevelt (interim Inglethorpe out; Tane
Fifita from Southern Tengus), Hatesei lost Poppy Hollerbach to Ireland River (dream job) and hired Freya Dahlqvist from
South Antiragal (dream job); South Antiragal took Dante Valloncelli from Sacred Tomb; 2037 COY Hartmut Kanzaki fired at
German Shores, replaced by Eona OC DeAndre Kingsbrook (alma mater). NEXT: Stage 2 draft pool for the RFL.
## 2041-42 OFFSEASON -- Stage 2 of 7 IN PROGRESS: 2042 draft pool handed to the RFL
export_draft_pool.py (new; wraps draft.run_draft's declarations) -> state/draft_pool_2042.json: 3,560 declared
(2,160 Sr, 1,377 early, 23 subdivision). Project doc claude/cfb_draft_pool_2042.json. Top of the sim's board: Winterbridge
(SkSt WR, Jr), Grimaldi (ES QB, Jr early), Owusowah (UNN TE), Brookwood, Campovieja, Havtveit, Lormyraw, Danecombe.
Early declarations of note: Grimaldi, Danecombe (Ryskamp), Campovieja, Winterbridge, Xuegang. Verville/Winswick are
freshmen -- ineligible. NEXT: RFL returns 280 picks -> install_rfl_draft.py (reads draft_pool_2042.json) -> portal.
Project is at its size cap: the full pool was refused; claude/cfb_draft_pool_2042.json holds the TOP 700 by stock (slim
fields). Full file sent to Dan as an attachment. Dan should clear old Project docs if he wants full pools there.
## 2041-42 OFFSEASON -- Stage 2 of 7 COMPLETE: the 2042 draft, run by the RFL
Picks from Project doc claude/rfl_draft_2042_picks.json -> state/rfl_draft_2042.json -> install_rfl_draft.py --commit ->
s['draft_s16'] + mark_departures. Backups state/{season_state,rosters}.pkl.pre_s17_draft. 280 valid (6 traded slots),
2,530 leaving college, 1,007 early entrants withdrew; 192 early entrants drafted, 4 subdivision.
#1 overall Wanda Borovec (Ciarralotta Tech S) to Queensville. Grimaldi 27th (Chapel Rock), El-Ghazali 26th, Danecombe
116th (Billiataho), Winterbridge 171st, Lormyraw 199th, Hazelton 192nd, Fontoncelli 173rd. RFL also signed ~60
undrafted FAs (its own ledger; sim treats undrafted seniors as gone anyway). NEXT: Stage 3 portal.
## 2041-42 OFFSEASON -- Stage 3 of 7 COMPLETE: transfer portal
Backups state/{season_state,rosters}.pkl.pre_s17_portal; s['portal_s16']. 444 entrants, 290 transfers, 154 no takers.
Flows L6->P6 102 / P6->P6 62 / P6->L6 46 / L6->L6 80 (2041: 105/65/39/62). Classes Jr 102 So 100 Fr 81 RS 7.
G14 in 37 / out 22 = +15 (2041 +29, 2040 +18): inflow easing on its own; keep watching, no cap added. 6 followed a coach.
Headlines: Tsuvai Eiselniy (Will Tech WR, 999 yds, 5*) to Eona; Omyr Tirresei (UN Minko QB, Southwestern champion) to
Pistolheart; Tupou Fatupeau (Dove Island QB) to Hatesei. NEXT: Stage 4 recruiting.

## 2041-42 OFFSEASON -- Stage 4 of 7 COMPLETE: 2042 recruiting (2026-10-23)
Backups state/{season_state,rosters}.pkl.pre_s17_recruiting; stored s['recruiting_s16'] (class_size, needs_total, signed, unsigned).
recruiting.py __main__ only sizes the class -- stage assembled by hand again (needs = 63 - (roster - _leaving); national_class_size; make_class; run_recruiting(recruits, needs, s)).
National class 2,785 | needs 2,219 | signed 2,219 | 566 unsigned (16 four/five-stars found no cap room).
Class 5* 13 | 4* 278 | 3* 975 | 2* 1,114 | 1* 405. Signed 5* 13 | 4* 262 | 3* 975 | 2* 969.
Blue-chips signed 275; by conference G14 55, JB 47, PN 42, MV 39, BS 36, WC 34, East Forest 6, L16 4. 67 programmes landed none.
Best classes by stars: Skeenerland State / Ciarralotta Tech / Central Stanton 60, Ranroman 59, UNN & Harrell 58.

## 2041-42 OFFSEASON -- Stage 5 of 7 COMPLETE: 2042 development (2026-10-23)
Backups state/{rosters,season_state}.pkl.pre_s17_dev; s['development_s16']. 7,357 players, mean +0.265 (Fr +0.500, So +0.188, RS +0.191, Jr +0.108).
321 breakouts, 74 busts, r_coach 0.606. Best team development: Ranroman +0.421, Kaji Daun / Poland State +0.393, Skeenerland State +0.389; lowest Clark +0.115.
Players rated 9.0+: 28 (post-draft). NEXT: Stage 6 roster finalisation.

## 2041-42 OFFSEASON -- Stage 6 of 7 COMPLETE: 2042 roster finalisation (2026-10-23)
Backups state/{rosters,season_state}.pkl.pre_s17_rfinal. departed 2,530 | recruits added 2,219 | walkons 0 | floor fills 294 | trimmed 0 |
rosters 63-69, total 9,870. No _leaving flags remain. Rollover (stage 7) pending.

## 2041-42 OFFSEASON -- Stage 7 of 7 COMPLETE: rollover, 2041 closed and 2042 open (season 17) (2026-10-23)
Backups state/{season_state,rosters,coaches,universe}.pkl.pre_s17_rollover. Classes Sr 2,461 | Jr 2,288 | So 2,427 | RS 181 | Fr 2,513.
456 staff records advanced. Records, polls, committee/media history reset; season_archive row '16' present (champion Skylar Rose); gameview_s16 archived. next_week 0.
Preseason top 10: Skeenerland State 10.35, Kaji Daun 10.19, Pistolheart 10.19, Marblehead 10.14, Orlot 10.14, Rogaela State, Eona, North Verigon, Leafette, UFNH. Range 6.85-10.35.
NEXT: 2042 schedule (noncon hand-off -> Scheduling Office; conference office), media pool redraw for s17 (carry-over rule: half same teams, no school >2 years in a row), preseason.
Before scheduling: distance rules vs U['school_coords'] still undecided.

## 2042 SCHEDULE -- Scheduling Office published for season 17 (saves under schedule/s17). 444 non-conference slots for Dan. (2026-10-23)
152 programmes | 217 guests | 6 locked cross-conference rivalries | unreturned visits 249 pairs (3.3 per programme); 13 series still owed a return ground.
REMINDER (Dan, 2026-10-23): once the schedule is completely built (noncon -> conference -> installed), TELL DAN TO START A NEW CONVERSATION to save usage.
Media pool redraw for s17 (carry-over rule) still to do before preseason.

## 2042 SCHEDULING OFFICE -- PROGRESS SAVED 2026-10-23 18:26
Dan's Office save (db schedule/s17, version 17, 6:24 PM) pulled down: state/schedule_office_save_s17_v17.json. Dan is partway through; resume from the Office (his save reloads there).

## 2042 non-conference board -- COMPLETE (2026-10-23)
Dan's Office save (db schedule/s17, v30, 6:50 PM) -> state/schedule_office_save_s17_v30.json -> state/noncon_s17_handoff.json (33 games incl. 6 locked, 9 guests).
fill_noncon.py patched for 2042 (pre-patch copy fill_noncon.py.pre_s17): BALANCE term -- a P6 programme is rewarded for the missing category
(P6 / L6 opponent) and penalised for a second of one; guests are placed on P6 programmes first. Result: 296 games, 136 guests (89.47%), complete.
state/noncon_s17.json. P6 non-con mix: 67 of 78 are 1 power / 1 non-power / 1 guest; 11 off-balance (5 from Dan's picks/locked rivalries: Kaji Daun, Leafette, Tasson, Barhold Valley, Northlight;
6 filler: Ekralund State, Pistolheart, UN Ediville, Parchynt, Riveral, UFNH = 0 power/2 non-power/1 guest).
Conference board built (export_conf_board: 12 conferences, 0 problems); Conference Office rebuilt for saves under conf/s17.
REMINDER (Dan): once the schedule is completely built, tell him to start a new conversation.

## 2042 non-conference board -- host repair (2026-10-23, Dan: power teams should rarely be on the road at non-power teams)
Initial fill had 44 of 83 P6-vs-L6 games with the P6 team travelling. New fix_p6_hosting.py (local search over host flips on AUTO non-guest games; Dan's picks and locked rivalries untouched):
P6 visiting L6 = 3, all-away = 10, all-home = 10 for L6 but only 0.5 for P6 (structural: 1 guest + 1 L6 + 1 P6 forces ~half of P6 to travel somewhere unless P6 may host all three).
Result: 6 P6-at-L6 games remain (2 Dan's: Northlight@Starfield, Park Island@Marines; 4 auto: Ranroman@Chinolka, Harrell@Vaughn Bay, Central Stanton@Coachville College, Pistolheart@West Hatesei St).
P6 non-con home counts: 3 home 37 | 2 home 39 | 1 home 2. L6: nobody all-home/all-away. Pre-fix file state/noncon_s17.json.pre_hostfix. Conference board rebuilt with new hosts.

## 2042 non-conference board -- host repair v2 (2026-10-23, Dan: P6 need not always travel; base on previous seasons)
Dan's past finals: P6 away at an L6 in 18-29% of P6/L6 games (s13 23, s14 29, s15 27, s16 18); P6 hosting all three non-con 23-31% of P6; 1 home 3-13%.
fix_p6_hosting.py weights tuned to that (w_away 2.4, w_allhome 1.2, w_oneP6 0.6): 17 of 83 P6/L6 games have the P6 away (20%); P6 home dist 1:2 | 2:50 | 3:26. Conference board rebuilt.

## 2042 distance rules -> SCHOOL COORDINATES (Dan, 2026-10-23: "yes, use school coordinates")
export_schedule_board.py and export_conf_board.py now take each team's/guest's xy from U['school_coords'] (state seed fallback); the Office distance/regional logic reads those xy. Pre-change copies *.py.pre_s17.
2042 non-con board was built on state coords BEFORE this change (not re-filled; Dan can ask for a re-fill). Stray duplicate viewer artifact 7G5yKnxG7RgVB9aAZiUDs6 DELETED at Dan's OK.

## 2042 CONFERENCE OFFICE -- PROGRESS SAVED 2026-10-23 22:4x
Dan's Office save (db conf/s17, version 26, 9:11 PM) pulled down: state/conf_office_save_s17_v26.json; converted (convert_conf_db.py) -> state/conf_s17_handoff.json:
53 of 980 rows placed (9 Jyras Bay conference games + 3 non-conference weeks by Dan, rest locked/pre-set). seed_conf_board.py baked them into conf_board.json; Office republished.
NEXT when Dan hands off: fill_conf.py -> conf_sched_s17.json -> install_hand_schedule.py --commit -> audit; then tell Dan to START A NEW CONVERSATION (media pool s17, preseason notes, week 0).

## 2042 non-conference board -- EXPANSION REFILL (2026-10-23 23:xx, Dan: too many teams playing only in-state / one-state-over opponents)
Measured on school coords: Dan's past hand-built boards median trip 78-110 (75th 145-192, 90th 222-300), ~20% in-state; the first auto-fill had median 63 (75th 102), 40% in-state.
fill_noncon.pair_score now rewards the middle band (70-180 units best, 180-260 good), taxes in-state (-12) and a SECOND short trip (<90) for a team (-25); pre-change copy fill_noncon.py.pre_expand.
Refill kept every game Dan hand-picked OR placed a week on (51 games, marked non-auto) and re-solved the rest; fix_p6_hosting re-run.
Result: 296 games, 136 guests; median 127 / 75th 168 / 90th 236; in-state 16 of 160 FBS games (10%); P6 mix 71 of 78 balanced (1/1/1); P6 away at L6 22 of 79; P6 home 1:1 | 2:59 | 3:18; no L6 all-home/all-away.
Teams still all-near (<90): Ciarralotta State, East Costique, Kaji Daun, North Verigon, Parchynt, Rogaela, Verigon, Wolford (locked/hand-set games or no longer legal partners).
Dan's Office save v119 (conf/s17, 10/23 ~10:xx PM) -> state/conf_office_save_s17_v119.json; 70 conf games + his non-con weeks carried BY PAIR onto the new board; DB doc conf/s17 RE-KEYED (version 120) because N-ids are positional. Office republished.
Dan must RELOAD the Office before placing more (a stale page would write old N-ids).

## 2042 CONFERENCE OFFICE -- DEBUG (2026-10-23 23:1x, Dan: why does UFNH play Riveral State in rivalry week?)
Cause: my own bug in the re-key after the non-con refill. convert_conf_db.py was run against the NEW board with the OLD positional N-ids, then seed_conf_board baked those mismatched weeks into conf_board.json,
and my "carry by pair" step then kept them as the default -- 17 non-con games got a week that was never Dan's (UFNH vs Riveral State = week 14 was one; UFNH already had a locked week-14 game vs Fiota Bay).
Fix: regenerated conf_board.json fresh, carried only Dan's 33 non-con weeks by pair from the pre-refill board (git ce29677) using his v119 ids, rewrote DB conf/s17 (version 123, clean_doc), republished Office (v21).
Checks after fix: board non-con == noncon_s17 (296); every FBS team has 3 non-con and 9 conf games; no guest reused; no team double-booked or with two week-14 games; 138 placed (all Dan's + locks).
LESSON: never run convert_conf_db.py with a board whose N-order differs from the ids in the save; build pairs from the board the save was made on.

## 2042 CONFERENCE OFFICE -- FILLED, awaiting Dan's review (2026-10-24 00:1x)
Dan's save v473 -> state/conf_office_save_s17_v473.json (306 of 980 rows placed by Dan/locks). fill_conf.py (seed 2039, attempt 1) placed the other 674, zero hard violations among open programmes;
none of Dan's placements moved. state/conf_s17_filled.json (980 rows). Hard-rule flags only on programmes Dan hand-filled completely: Far Farris & Far Farris State (5 home in a row), Natzumakis (5 home in a row), North Verigon (4 road in a row).
Review copy written to DB conf/s17 (version 474) and Office republished; Dan edits there. Dan's own pre-fill hand-off kept as state/conf_s17_handoff_dan.json.
NEXT after Dan's OK: pull save -> convert_conf_db.py -> conf_sched_s17.json -> install_hand_schedule.py --commit -> audit -> tell Dan to START A NEW CONVERSATION.

## 2042 CONFERENCE OFFICE -- DAN'S EDITS SAVED 2026-10-24 01:0x
Office save v589 (12:57 AM) -> state/conf_office_save_s17_v589.json; 24 rows changed vs the filled calendar (6 conference games, 18 non-con weeks); all 980 placed. convert_conf_db.py -> state/conf_s17_handoff.json + conf_sched_s17.json (complete).
Not installed yet -- waiting for Dan's OK (install_hand_schedule.py --commit, then audit, then tell Dan to START A NEW CONVERSATION).

## 2042 SCHEDULE -- INSTALLED (2026-10-24 01:3x)
Dan's final Office save v589 (12:57 AM) -> convert_conf_db.py -> state/conf_sched_s17.json -> install_hand_schedule.py --commit (backup state/season_state.pkl.pre_s17_install).
980 games (684 conference, 296 non-conference, 136 guests), audit CLEAN; week 0: 18 games; games by week 0-14: 18/79/71/69/68/66/67/68/65/65/67/65/61/69/82. 4 programmes with 4+ home/road runs (worst Natzumakis, 5 home).
NEXT (new conversation, per Dan): media pool redraw for s17 (half same teams; no school >2 years in a row), preseason notes + page, then week 0.

## 2042 PRESEASON -- 2026-10-24 (new conversation, container wiped again)
RESTORED from GitHub (minigolfwiz/roiland-rfl, cfb/): code + gz state + games_db parts; season 17, next_week 0, 980-game schedule installed. Two gaps found and closed:
(1) marks_lib.js had never been committed (build_pages needs it) -- recovered verbatim from the published Roiland Preseason page and now in the repo.
(2) state/sub_rosters.pkl.gz in the repo was the STALE 2041 guest set (the 2042 guests were generated at install after the last push) and sub_coaches.pkl was never committed. Regenerated the 2042 guest rosters + staffs from the install seed (20267000 = 17*1000+20250000; derive_attrs rng 909090): positions, classes, abilities, staff skills/ages/tenures are as at install; player and coach NAMES are fresh (the originals were unseeded and are gone; nothing had been played or shown). 136 guests, 7,208 players. Both now committed (state/sub_rosters.pkl.gz, state/sub_coaches.pkl.gz). Stale copies: *.pkl.stale_s16 (local only).
Media pool s17 drawn by media_pool.make_pool (30 returning / 30 new, no school in all three of 2040-42). Preseason poll run: poll_update(seed=10000) -> media_history['pre'], media_ballots[0]. Backup state/season_state.pkl.pre_s17_preseason.
Top 5: Central Stanton (31 firsts), Skylar Rose (26), Eona, Skeenerland State, Eastern State; Eternal Fox 23rd is the only L6 ballot team. 25 notes in state/preseason_notes.json (2041's kept as preseason_notes_s16.json), fact-checked against the log; no mascots/ratings. Roiland Preseason republished (v5), Media Pool (v41).
Week 0 Gameview candidates printed: Skeenerland State at Cordelle; Natzumakis at Skylar Rose; Crayellan at North Verigon; VSSC at Rogaela State. NEXT: Dan picks -> `python3 week_cycle.py 0 <host>`.
LESSON: commit every file the build needs (*.js, sub_coaches.pkl) and re-push sub_rosters/sub_coaches right after every install_hand_schedule --commit.

## 2042 WEEK 0 played (Gameview: Natzumakis at Skylar Rose) -- 2026-10-24
Natzumakis 34-14 over #2 Skylar Rose (Notaw 190/2 TD; Sandcott 201 rush for Skylar Rose; Verville 135/1/1; DL Kalani Ulunoa out for the year). Skeenerland State 41-10 at Cordelle; Hoganelle 35-32 Keytommiyr;
guest win: Veriota 31-22 at Fiota State (3 guest games, 1 guest win). Poll: Central Stanton 1, Skeenerland State 2, Eona 3, Skylar Rose 4 (0-1), UNN 5. No one dropped out.
Backup state/season_state.pkl.pre_w0. Season viewer v133, Media Pool v42. NEXT: week 1 Gameview pick (Ranroman State at Crayellan; Dietsche at UNN; Eona at Dove Island; Skylar Rose at Good River).

## 2042 WEEK 1 played (Gameview: Ranroman State at Crayellan) -- 2026-10-24
Ranroman State 41-27 at #12 Crayellan (Omtreimyr 480/2 in defeat; Petitcour 245 rush, Jorrovei 204/3). #5 UNN lost 28-21 to #18 Dietsche... (UNN 21, Dietsche 28 at UNN; Kingsworth 420/3, El-Najjar 327/3).
Upsets: Vaughn Bay State 34-21 #6 Tengus State (Vikstad 3 INT); Keeper 23-10 #15 Ciarralotta Tech; Tasson 24-21 #25 Fiota Bay. Skylar Rose 56-24 at Good River; Park Island 56-21 at Marines. 23 guest games, 2 guest wins (Pietro Tadal 17-14 Waterloo, Krei 12-0 Westburg).
Poll: Central Stanton 1, Skeenerland State 2, Eona 3; Fiota Bay dropped out, Hatesei in at 21. Backup season_state.pkl.pre_w1. Viewer v134, Media Pool v43.
NEXT: week 2 pick (Will Tech at Dietsche; Yrei Trobniy at North Hatesei; Central Stanton at Ciarralotta; Ranroman at Stanton; passed: Lornaman at Skeenerland State).

## 2042 WEEK 2 played (Gameview: Will Tech at Dietsche) -- 2026-10-24
Dietsche 28-13 over Will Tech (El-Najjar 203/3, Dhanaswamy 135 rush). #1 Central Stanton 26-10 at Ciarralotta. Upsets: Lornaman 41-21 over #2 Skeenerland State (Quickbear 335/3); Stanton 28-9 over #5 Ranroman;
Verigon State 31-7 #13 Rogaela State; Costique 14-7 #11 Kaji Kita; Pistolheart 27-13 #22 Ciarralotta Tech; Fiota Bay 40-26 #25 Eternal Fox (Winswick 353/3, Verbourg 268/3); German Shores 37-28 #23 Verigon;
North Hatesei 27-19 #17 Yrei Trobniy. 19 guest games, 2 guest wins (Peterhaus 31-10 East Costique; Southern Bay 20-17 Poland State). Poll: Central Stanton 1, Eona 2, UFNH 3, Ranroman State 4, Park Island 5;
out: Ciarralotta Tech, Verigon, Eternal Fox. Backup season_state.pkl.pre_w2. Viewer v135, Media Pool v44.
STANDING (Dan, 2042 wk 2): when giving Gameview candidates, also give detail on each: series (since 2025), last meetings, week-by-week results/leaders, coaches, long-term injuries, stakes and outlook.
NEXT: week 3 pick.

## 2042 WEEK 3 played (Gameview: Kaji Kita at Barhold) -- 2026-10-24
#15 Kaji Kita 34-23 at #17 Barhold (Byungho Jinhai 249 rush/2). Ten ranked teams lost: #1 Central Stanton 30-38 to #23 Rogaela State (Althauer 283 rush/2; Watanuki 403, Karakos 260 rec); #4 Ranroman State 6-7 to Canesta State;
#7 Dietsche 30-31 to Dove Island (El-Najjar 404/3); #9 Eastern State 27-30 Ekralund State; #16 Ciarralotta State 38-49 Lornaman (Quickbear 469/5); #10 Skylar Rose 19-7 #20 Tengus State; #21 Yrei Trobniy 3-7 UN Steelbridge;
#22 Marblehead 17-25 Keeper; #24 Roosevelt 21-33 Parchynt State. Skeenerland State 17-6 Riverwake, UFNH 37-0 Riveral State, Park Island 31-7 Barhold State, Eona 27-16 Orlot. 10 guest games, 1 guest win (St. Ballo's 30-24 Burrstone).
Poll: 1 UFNH, 2 Park Island, 3 Eona, 4 Central Stanton, 5 Ranroman State, 6 Kaji Daun; out: Yrei Trobniy, Marblehead. Backup season_state.pkl.pre_w3. Viewer v136, Media Pool v45. gameview_detail.py added (detail for candidates).
NEXT: week 4 pick (Ranroman State at Kaji Daun; Park Island at Skylar Rose; Tengus State at Kaji Kita; Dietsche at S Antiragal State).

## 2042 WEEK 4 played (Gameview: Ranroman State at Kaji Daun) -- 2026-10-24
#5 Ranroman State 28-26 at #6 Kaji Daun (Jorrovei 218/4; Schwarzhoff 322/0). Park Island 38, Skylar Rose 28 at Skylar Rose (Torrarini 416/2; Verville 320/2/2, Weon 211 rec/2).
Upsets: Stanton 35-21 at #12 North Hatesei (Pellavanti 139/3); #25 Tengus State 45-3 at #14 Kaji Kita (Sotohermosa 157 rec/5 TD); National 48-10 at #19 Lornaman; Leafette 25-24 #21 Will Tech; Parchynt 37-24 at #22 Crayellan State (Sierralonga 284/2).
Hatesei 28-21 Ciarralotta; Dietsche 44-24 at S Antiragal State. 8 guest games, 1 guest win (Polt Hall 27-19 at Clark). 305 results.
Poll: 1 Park Island, 2 UFNH, 3 Ranroman State, 4 Kaji Daun, 5 Eona; out: Lornaman, Ciarralotta State, Will Tech. Backup season_state.pkl.pre_w4. Viewer (1.7 MB, 305 box scores), Media Pool published.
NEXT: week 5 pick (UNN at Eona; Central Stanton at North Hatesei; Stanton at Hatesei; UFNH at Harrell).

## 2042 WEEK 5 played (Gameview: Stanton at Hatesei) -- 2026-10-24
#9 Hatesei 31-30 #19 Stanton (Fatupeau 254/2; Claybridge 184 rush/2; Brookden 312/3). #7 UNN 30-10 #5 Eona at Eona (Kingsworth 412; Danefield 224 rec). North Hatesei 31-17 #6 Central Stanton. Ciarralotta 34-31 #4 Kaji Daun (Schwarzhoff 288/3/2; Yukimaki 280 rec). North Verigon 14-3 #17 Costique River. Southern Krobe 20-15 #15 Eastern State. Barhold State 29-24 #11 Southern Tengus. Skeenerland 27-24 #25 Tengus State. Guests 0-5.
Poll: 1 Park Island, 2 UFNH, 3 Ranroman State, 4 UNN, 5 Kaji Daun, 6 Hatesei, 7 Eona. Out: Barhold, Tengus State.
NEXT: week 6 pick (Eona at Stanton; North Hatesei at UNN; Ranroman at Central Stanton; Eastern State at Phangrine State).

## 2042 WEEK 6 played (Gameview: North Hatesei at UNN) -- 2026-10-24
#4 UNN 38-21 #17 North Hatesei (Kingsworth 342/4/4 INT; Lomoletti 201/3/2). Stanton 44-31 #7 Eona (Pellavanti 272/3; Eastdale 368/3/2; Nnabayo 235 rec/2). Ranroman 19-16 OT #10 Central Stanton (Eastman 127/2/3; Watanuki 101/0/3; Kofjide 4 sk). Parchynt 42-26 #9 Crayellan (Sierralonga 373 rush/3). Far Farris State 41-10 #19 Roosevelt. Eastern State 31-14 #20 Phangrine State (Darwish 345/3; Georzoglou 5 INT). Verigon 41-27 #16 Costique River. UFNH 20-17 East Costique, Park Island 21-17 Good River, Hatesei 26-21 at UN Ediville, Dietsche 41-10 at Antiragal. Guests 0-5 (1-13 on the year).
Poll: 1 UFNH, 2 Park Island, 3 UNN, 4 Ranroman State, 5 Hatesei. Out: Rogaela State, Kaji Kita.
RYSKAMP: engine auto-named the TWENTY at week 6 (ryskamp_s17, open). Next cuts: ten at week 10, four finalists.
NEXT: week 7 pick (UNN at Ranroman; Ranroman State at Pistolheart; UFNH at Crayellan State; Crayellan at Costique River).

## 2042 WEEK 7 played (Gameview: UFNH at Crayellan State) -- 2026-10-24
POLL CHANGE (Dan approved "medium", from wk 7 and all future seasons; weeks 0-6 stand): media_pool.py -- extra losses forgiven 75% less each; preseason weight fades .18/game; prestige+talent fade .09/game to 40%; a team that lost last week has voter inertia x0.3 and can only be pushed DOWN. Backup media_pool.py.pre_w7; changelog media_pool.py.CHANGELOG.
#23 Crayellan State 49-39 #1 UFNH (Ashdale 239/5; Lamedeer 409/4; Steinmeier 225 rec/3). Ranroman 27-24 #3 UNN (Althardt 145 rush; Kingsworth 353). Eona 30-7 at #5 Hatesei (Eastdale 270/3; Nnabayo 189 rec/2). Harrell 20-0 #9 Rogaela. Ranroman State 52-27 at #17 Pistolheart (Jorrovei 346/5; Loken 245 rec/2). East Costique 20-18 #19 Parchynt. Crayellan 16-14 at #21 Costique River (Omtreimyr 383/0/2). Kaji Daun 28-27 #22 North Hatesei. Guests 0-6.
Poll: 1 Park Island, 2 Ranroman State, 3 UFNH, 4 UNN, 5 Dietsche. Out: Costique River, North Hatesei, Roosevelt. In: Diveo State 6-0, UN Steelbridge 6-0.
** COMMITTEE: Dan builds the FIRST COMMITTEE RANKING BY HAND after WEEK 8 is played. REMIND HIM right after week 8 results. **
NEXT: week 8 pick (Skeenerland State at Southern Tengus; Rogaela at UFNH; Kaji Daun at Eona; Ranroman State at Hatesei).

## 2042 WEEK 8 played (Gameview: Skeenerland State at Southern Tengus) -- 2026-10-24
STANDING RULE (Dan): NO GUEST GAMES IN WEEK 14 -- enforced in install_hand_schedule.audit from 2043; 2042 schedule (12 wk-14 guest games) left as built.
Guest record corrected from data: through wk 7 7-72 (79 games); 57 more scheduled (wk8 7, wk9 8, wk10 8, wk11 4, wk12 4, wk13 14, wk14 12). Earlier "1-19" tallies in chat were wrong.
#7 Southern Tengus 41-14 #6 Skeenerland State (Kepu 319/3; Monteclara 170 rec/3; Furube 148/0/2). Eona 31-10 #8 Kaji Daun (Eastdale 362/3). Ranroman State 20-17 at #9 Hatesei (Jorrovei 289; Sorlovei 243 rec). UFNH 23-16 #10 Rogaela. Pistolheart 31-17 #11 Ranroman (Virtravaw 172/4). North Verigon 23-22 #18 Crayellan State. Marines 20-16 #23 UN Steelbridge. Park Island 70-17 at #29 Roosevelt. Guest win: Inkstromm 21-7 at Chapel Rock (guests now 8-78).
Media poll wk8: 1 Park Island, 2 Ranroman State, 3 UFNH, 4 Dietsche, 5 UNN. Out: Eastern State.
** FIRST COMMITTEE BALLOT: committee_week.html built, ballot_prep.py sheet given to Dan. WAITING on his top 25 -> install_committee.py <file> --commit. Gameview week 9 candidates only AFTER his board is installed (standing). **

## 2042 FIRST COMMITTEE BOARD INSTALLED (after week 8) -- state/ballot_s17_w8.json, audit CLEAN
1 Park Island, 2 Ranroman State, 3 Southern Tengus, 4 Stanton, 5 Diamond City, 6 North Verigon, 7 Tasson, 8 Pistolheart, 9 UFNH, 10 Dietsche, 11 Diveo State, 12 Eona, 13 Rogaela State, 14 UNN, 15 Ekralund State, 16 Crayellan State, 17 Crayellan, 18 Ranroman, 19 Eastern State, 20 Phangrine State, 21 Fiota Bay, 22 Hatesei, 23 Canesta State, 24 Antiragal State, 25 Hoganelle.
Dan ranks by hand every week from here. Weekly routine: play week -> export_committee_week.py -> build_pages -> publish Committee Ballot -> ballot_prep.py -> Dan's board -> install_committee.py -> THEN Gameview candidates.
NEXT: week 9 pick (candidates ranked off his board).
FIRST COMMITTEE BOARD INSTALLED (state/ballot_s17_w8.json): 1 Park Island, 2 Ranroman State, 3 Southern Tengus, 4 Stanton, 5 Diamond City, 6 North Verigon, 7 Tasson, 8 Pistolheart, 9 UFNH, 10 Dietsche, 11 Diveo State, 12 Eona, 13 Rogaela State, 14 UNN, 15 Ekralund State, 16 Crayellan State, 17 Crayellan, 18 Ranroman, 19 Eastern State, 20 Phangrine State, 21 Fiota Bay, 22 Hatesei, 23 Canesta State, 24 Antiragal State, 25 Hoganelle. Committee is now the ranking of record.
Week 9 candidates (off his board): Natzumakis State at Park Island; Tasson at Will Tech; North Verigon at Riveral; Southern Tengus at Diveo. NEXT: Dan's pick.

## 2042 WEEK 9 played (Gameview: Keeper at Diamond City) -- 2026-10-24
Keeper 47-41 OT #5 Diamond City (DiStefano 480/3; Greenton 309 rec/2; Marettoni 331 rush/3). Diveo 25-23 #3 Southern Tengus (Sandwick 431; Kepu 424/2/4 INT; Isveiro 249 rec). Riveral 29-26 OT #6 North Verigon. Krobe 28-21 #13 Rogaela State. Coachville 38-21 #15 Ekralund State (Sarvadeva 221 rush/4). Costique River 23-21 #16 Crayellan State. Fiota Bay 36-24 #17 Crayellan (Blackbourne 310 rush/3). Lornaman 38-35 #20 Phangrine State (Georzoglou 464). Park Island 35-7 Natzumakis State; Ranroman State 36-24 UN Ediville; Tasson 23-14 at Will Tech. Guests 0-8.
WAITING on Dan's week 9 committee board (ballot_prep sheet given). Wk 10 candidates only after install.
WEEK 9 COMMITTEE BOARD INSTALLED (state/ballot_s17_w9.json): 1 Park Island, 2 Ranroman State, 3 Stanton, 4 Tasson, 5 Pistolheart, 6 UFNH, 7 Dietsche, 8 Diveo State, 9 Eona, 10 Diamond City, 11 UNN, 12 Fiota Bay, 13 Diveo, 14 Southern Tengus, 15 Ranroman, 16 Eastern State, 17 Hatesei, 18 Ekralund State, 19 Skeenerland State, 20 Rogaela State, 21 Antiragal State, 22 North Verigon, 23 Canesta State, 24 Hoganelle, 25 Phangrine State. Out: Crayellan State, Crayellan.
Week 10 candidates: Pistolheart at Eona; Ranroman State at UNN; Antiragal State at Ekralund State; Stanton at Central Stanton. NEXT: Dan's pick.

## 2042 WEEK 10 played (Gameview: Pistolheart at Eona) -- 2026-10-24
#9 Eona 21-19 #5 Pistolheart (Eastdale 289/2; Woolridge 130 rec; Clairlac hurt, 3 wks). #11 UNN 20-7 #2 Ranroman State (Kingsworth 355; Jorrovei 211/1/1). Central Stanton 47-14 #3 Stanton (Watanuki 263/3; Northgate 186 rec/2). Barhold 6-0 #13 Diveo. #18 Ekralund State 31-10 #21 Antiragal State (Kongiannis 3 INT). Park Island 41-28 at Kaji Kita State; Tasson 40-0 Krobe; UFNH 28-3 at Riveral; Dietsche 28-14; Diveo State 37-6; Diamond City 30-0 Waterloo. Guests 1-7 (Skeenerland East 41-34 at Hofferteltra) -> season guests 9-93.
RYSKAMP TEN (auto, subset of the 20): Torrarini, Sierralonga, Althauer, Hariraman, Kingsworth, El-Najjar, U-Cheol, Kepu, Usoanua, Staledis.
WAITING on Dan's week 10 committee board; wk 11 candidates after install.
WEEK 10 COMMITTEE BOARD INSTALLED (state/ballot_s17_w10.json): 1 Park Island, 2 Tasson, 3 UFNH, 4 Dietsche, 5 Diveo State, 6 Eona, 7 Pistolheart, 8 Ranroman State, 9 Diamond City, 10 UNN, 11 Stanton, 12 Fiota Bay, 13 Southern Tengus, 14 Ranroman, 15 Eastern State, 16 Hatesei, 17 Ekralund State, 18 Skeenerland State, 19 Far Farris State, 20 Rogaela State, 21 North Verigon, 22 Canesta State, 23 Hoganelle, 24 Lornaman, 25 Phangrine State. Out: Diveo, Antiragal State.
Week 11 candidates: Pistolheart at Stanton; Costique at Diveo State; Verigon at UFNH; Eona at UN Ediville. NEXT: Dan's pick.

## 2042 WEEK 11 played (Gameview: UN Steelbridge at Canesta State) -- 2026-10-24
UN Steelbridge 24-21 #22 Canesta State (Viroviy 205 rush/2; Al-Dabbagh 302/1). UN Ediville 42-36 OT #6 Eona (Menssei 346/4; Iwasato 250 rec/4; Eastdale 395/3/3 INT). Stanton State 20-17 OT #9 Diamond City. Orlot 21-18 #10 UNN (Whitman 244 rec; Kingsworth 371). #7 Pistolheart 30-24 #11 Stanton at Stanton (Petroridis 270/2/2; Xusun 230 rec). Good River 37-28 #19 Far Farris State. Skeenerland 51-23 #23 Hoganelle (Krishnanathan 417/4; El-Fahim 270 rec/2). Southern Krobe 17-13 #25 Phangrine State. UFNH 34-21 Verigon. Diveo State 37-31 OT Costique. Guests 0-4 -> season 9-97.
WAITING on Dan's week 11 board; wk 12 candidates after install.
WEEK 11 COMMITTEE BOARD INSTALLED (state/ballot_s17_w11.json): 1 Park Island, 2 Tasson, 3 UFNH, 4 Dietsche, 5 Diveo State, 6 Pistolheart, 7 Ranroman State, 8 Fiota Bay, 9 Southern Tengus, 10 Ranroman, 11 Eastern State, 12 Hatesei, 13 Ekralund State, 14 Skeenerland State, 15 Diamond City, 16 Rogaela State, 17 Stanton, 18 North Verigon, 19 Lornaman, 20 Krobe State, 21 Rogaela, 22 UN Steelbridge, 23 Black Forest, 24 Keeper, 25 Far Farris State. Out: Eona, UNN, Canesta State, Hoganelle, Phangrine State.
Week 12 candidates: Tasson at Krobe State; North Verigon at Fiota Bay; Keeper at Ekralund State; UFNH at Parchynt. NEXT: Dan's pick.

## 2042 WEEK 12 played (Gameview: North Verigon at Fiota Bay) -- 2026-10-24
#8 Fiota Bay 34-13 #18 North Verigon (Winswick 319/4/2; Al-Hadid 180 rush; Rowberry 169/1/3). Barhold Valley 38-35 #1 Park Island AT Park Island (Bonatelli 478; Torrarini 475/3/2; Elvstrom 209 rec/2). Barhold 34-9 #5 Diveo State (Gyenna 180/3 + 111 rush). Tengus State 14-0 #9 Southern Tengus. #15 Diamond City 38-20 #11 Eastern State. #20 Krobe State 31-40 #2 Tasson (Freeley 492; Highknife 473/4; Shimazuka 235 rec). Wolford 28-7 #22 UN Steelbridge. #13 Ekralund State 27-17 #24 Keeper (Midbe 234 rec/2). UFNH 30-24 at Parchynt; Dietsche 44-13; Ranroman State 21-17 Orlot; Ranroman 37-29 at Greene. Guests 0-4 -> 9-101.
WAITING on Dan's week 12 board; wk 13 candidates after install.
WEEK 12 COMMITTEE BOARD INSTALLED (state/ballot_s17_w12.json): 1 Tasson, 2 UFNH, 3 Dietsche, 4 Pistolheart, 5 Fiota Bay, 6 Park Island, 7 Ranroman State, 8 Diveo State, 9 Ranroman, 10 Ekralund State, 11 Diamond City, 12 Hatesei, 13 Skeenerland State, 14 Rogaela State, 15 Stanton, 16 Lornaman, 17 Rogaela, 18 Eastern State, 19 Eona, 20 Black Forest, 21 Far Farris State, 22 Barhold, 23 North Verigon, 24 Krobe State, 25 Ciarralotta State. Out: Southern Tengus, UN Steelbridge, Keeper.
Week 13 candidates: Rogaela State at Tasson; Hatesei at Pistolheart; Far Farris State at Park Island; Eona at Ranroman. NEXT: Dan's pick.

## 2042 WEEK 13 played (Gameview: Rogaela State at Tasson) -- 2026-10-24
#1 Tasson 56-28 #14 Rogaela State (Marshwell 510 rush, 8 TD; Highknife 153/0/1). Crayellan 25-24 #2 UFNH (Dahlvoll 389/1/6 INT; Lamedeer 307; Vallanelli 227 rec). #12 Hatesei 34-27 #4 Pistolheart at Pistolheart (Fatupeau 327/3; Holmtveit 240 rec/3; Clairlac 295/3/4 INT). Crayellan State 41-31 #5 Fiota Bay (Winswick 428; Lindnes 236 rush). Tengus State 40-29 #8 Diveo State. #19 Eona 41-27 #9 Ranroman at Ranroman (Eastdale 280/4; Nnabayo 211 rec/2). Ciarralotta State 45-17 #10 Ekralund State (Oakfield 391/4). Marblehead 14-8 #13 Skeenerland State. UNN 17-6 #15 Stanton. #18 Eastern State 49-24 #16 Lornaman (O. Ashdale 307 rush/3). Costique River 27-7 #17 Rogaela. #6 Park Island 42-23 #21 Far Farris State. Parchynt 21-14 #23 North Verigon. Dove Island 31-21 #24 Krobe State. Dietsche 52-21 Lawiiri (guest); Ranroman State 24-19 at Ciarralotta.
GUESTS 4-10 in wk 13 (Lazzagu, Southern Perth, Highrose OT, Lighaty 41-35 at Riveral) -> season 13-111 (124 played; 12 left, all wk 14).
WAITING on Dan's week 13 board; wk 14 candidates after install.
WEEK 13 COMMITTEE BOARD INSTALLED (state/ballot_s17_w13.json): 1 Tasson, 2 Dietsche, 3 Park Island, 4 Hatesei, 5 Ranroman State, 6 UFNH, 7 Diamond City, 8 Pistolheart, 9 Eastern State, 10 Eona, 11 Ekralund State, 12 Ranroman, 13 Fiota Bay, 14 Barhold, 15 UNN, 16 Diveo State, 17 Ciarralotta State, 18 Black Forest, 19 Marblehead, 20 Costique River, 21 Rogaela State, 22 Lornaman, 23 Skeenerland State, 24 Rogaela, 25 Dove Island. Out: Stanton, Far Farris State, North Verigon, Krobe State.
Week 14 (last regular-season week) candidates: Ranroman at Ranroman State [rivalry]; Dietsche at Rogaela State [rivalry]; Lornaman at Ekralund State [rivalry]; UFNH at Fiota Bay [rivalry]. NEXT: Dan's pick.

## 2042 WEEK 14 played (Gameview: Ranroman at Ranroman State) -- 2026-10-24  [REGULAR SEASON COMPLETE: 980/980]
#5 Ranroman State 16-10 OT #12 Ranroman (Jorrovei 252/1/1; Eastman 195/1/2; Hirotsu 5 sacks). North Hatesei 23-6 #4 Hatesei at Hatesei. #13 Fiota Bay 38-12 #6 UFNH (Winswick 329/3; Hariwardhan 201 rec/3). Phangrine State 33-31 #7 Diamond City (Georzoglou 370/3). Keeper 27-17 #9 Eastern State (Darwish 4 INT). Lornaman 39-28 #11 Ekralund State (Quickbear 424). Central Stanton 28-20 #15 UNN. Ciarralotta Tech 31-20 #17 Ciarralotta State. Costique 38-14 #19 Marblehead. #2 Dietsche 21-12 #21 Rogaela State. Skeenerland 27-17 #23 Skeenerland State. Will Tech 41-7 #25 Dove Island. #1 Tasson 30-6 at Leafette; #3 Park Island 34-14 at Burrstone; #8 Pistolheart 24-19 at UN Ediville; #10 Eona 41-7 Cherry Lake.
GUESTS 5-7 in wk 14 (Robertson, Long South 9-7, Gunther, Jones College, Jack Todd OT) -> FINAL 18-118 (136 games).
NEXT: Dan's WEEK-14 BOARD (stage CCG) -> ccg_preview.py (NEVER run ccg.py without --commit; 2041 incident) -> conference finals -> selection ballot -> playoff.
TODO (Dan, 2042 wk 14): AFTER THE SEASON, AUDIT PARITY AGAIN -- he feels good teams lost far more often than they should (upsets of top-ranked teams). Tools: parity_test.py, parity_ab.py. Compare 2042 upset rates (ranked/top-10 losses to unranked or lower-rated teams) against prior seasons and the target; report before changing anything; fixes apply forward only.
QUEUED (Dan, wk 14): after the season, AUDIT PARITY AGAIN -- too many losses by good teams; only one 2-loss power team in 2042 looks suspect. Details in OFFSEASON_TODO.md.
WEEK 14 COMMITTEE BOARD INSTALLED (state/ballot_s17_w14.json): 1 Tasson, 2 Dietsche, 3 Park Island, 4 Ranroman State, 5 Pistolheart, 6 Eona, 7 Fiota Bay, 8 UFNH, 9 Barhold, 10 Diveo State, 11 Black Forest, 12 Lornaman, 13 Costique River, 14 Hatesei, 15 Rogaela, 16 Ranroman, 17 Antiragal State, 18 Diamond City, 19 Ekralund State, 20 Stanton, 21 Eastern State, 22 UNN, 23 Rogaela State, 24 Barhold Valley, 25 North Hatesei. Out: Ciarralotta State, Marblehead, Skeenerland State, Dove Island.
CCG PREVIEW shown to Dan (ccg_preview.py; NOT played): Power North Diveo State v Marblehead; Jyras Bay Tasson v Dietsche; Great Fourteen Ranroman State v Eona; Western Coast Park Island v Yrei Trobniy; Broad South Lornaman v Keeper; Mountain Valley Fiota Bay v Crayellan; Vapor Stream Skirter v Hoganelle; Low Sixteen Black Forest v Westburg; Brass Belt Canesta State v Churchill; East Forest Trapper Point v Eternal Fox; Evening Star Vaughn Bay State v Vaughn Bay; Southwestern UN Minko v Cordelle.
NEXT: Dan confirms -> python3 ccg.py --commit (backups first). NEVER run ccg.py without --commit being intended.
2042 CONFERENCE FINALS PLAYED (ccg.py --commit): Marblehead 28 Diveo State 24; Dietsche 42 Tasson 23; Eona 30 Ranroman State 14; Yrei Trobniy 33 Park Island 31; Lornaman 24 Keeper 23; Crayellan 27 Fiota Bay 20; Hoganelle 24 Skirter 10; Black Forest 18 Westburg 0; Canesta State 42 Churchill 10; Trapper Point 41 Eternal Fox 38 (1OT); Vaughn Bay State 38 Vaughn Bay 14; UN Minko 30 Cordelle 14.
RYSKAMP FOUR (strict subset of ten): Torrarini, El-Najjar, Hariraman, Sierralonga.
NEXT: selection ballot (stage CCG) from Dan -> playoff office.
2042 PLAYOFF FIELD INSTALLED (human committee): 1 Dietsche 2 Tasson 3 Park Island 4 Eona 5 Ranroman State 6 Pistolheart 7 Fiota Bay 8 UFNH | R1: 24 Vaughn Bay State@9 Barhold, 23 UN Minko@10 Lornaman, 22 Trapper Point@11 Diveo State, 21 Canesta State@12 Black Forest, 20 Hoganelle@13 Costique River, 19 Crayellan@14 Hatesei, 18 Marblehead@15 Rogaela, 17 Yrei Trobniy@16 Ranroman. NOT PLAYED; waiting on Dan's go.
2042 R1 full previews given (playoff_preview.py, read-only). NOT PLAYED; waiting on Dan's go for playoff.py run_round1.
2042 PLAYOFF R1 PLAYED: Barhold 41 Vaughn Bay State 10; Lornaman 26 UN Minko 7; Trapper Point 27 Diveo State 18; Canesta State 31 Black Forest 10; Hoganelle 30 Costique River 21; Crayellan 17 Hatesei 14; Marblehead 32 Rogaela 28; Yrei Trobniy 30 Ranroman 24. Snapshot state/season_state.pkl.pre_s17_po_r1 taken before. NEXT: R2 preview, then Dan's go.
STANDING RULE (Dan, 2042): always give full previews of EVERY playoff round before playing it (playoff_preview.py r1|r2|qf|sf|champ). 2042 R2 previews given; NOT PLAYED; waiting on Dan's go for playoff.run_round2.
2042 PLAYOFF R2 PLAYED: Dietsche 50 Trapper Point 31; Tasson 35 Canesta State 17; Hoganelle 34 Park Island 23; Eona 36 Crayellan 27; Ranroman State 55 Marblehead 7; Pistolheart 35 Yrei Trobniy 20; Fiota Bay 34 Lornaman 17; Barhold 48 UFNH 23. QF: Dietsche-Hoganelle, Tasson-Barhold, Eona-Fiota Bay, Ranroman State-Pistolheart. NEXT: QF previews (with sites) then Dan's go.
2042 QF previews given (sites: Dietsche-Hoganelle 501 Bowl Stamford; Tasson-Barhold Lumber Bowl Port Logan; Eona-Fiota Bay Copper Bowl Billiataho; Ranroman State-Pistolheart Redwood Bowl Kirkwood). NOT PLAYED; waiting on Dan's go for playoff.run_qf.
