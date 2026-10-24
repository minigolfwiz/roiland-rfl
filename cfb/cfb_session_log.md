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
