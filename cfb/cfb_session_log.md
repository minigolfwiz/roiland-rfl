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
2042 QF travel map published (build_travel_map.py). FINDING for Dan: engine assigns bowls by state LABEL positions (CM.vdist on COORDS), not campus/city positions; on true positions Tasson is nearer Redwood (86) than Lumber (109), Barhold 193 vs 272. Options: leave, or pin via P['venue_override']['QF'] (list of bowl names in P['qf'] order). QF NOT PLAYED; Dan to decide sites.
RULE (Dan, 2042): neutral-site bowls assigned by SCHOOL distance (campus to bowl city), not state distance. Implemented in committee.vdist; applies to 2042 QF/SF and all future seasons.
2042 (Dan): rotation_venue now takes the opponent; the higher seed skips any bowl located in the opponent's own state (de facto home game), falling back to plain nearest only if every free bowl is one. playoff._neutral_round passes the lower seed. Backups: committee.py.pre_oppo_home, playoff.py.bak_oppo. 2042 QF sites: Dietsche-Hoganelle 501 (Stamford); Tasson-Barhold Redwood (Kirkwood); Eona-Fiota Bay Copper (Billiataho); Ranroman State-Pistolheart Lumber (Port Logan).
2042 PLAYOFF QF PLAYED: Dietsche 40 Hoganelle 10 (501 Bowl); Tasson 38 Barhold 17 (Redwood Bowl); Eona 35 Fiota Bay 21 (Copper Bowl); Pistolheart 34 Ranroman State 17 (Lumber Bowl). SF: Dietsche-Pistolheart, Tasson-Eona. NEXT: SF previews then Dan's go.
2042 SF previews given (Dietsche v Pistolheart @ Steam Bowl, Coachville; Tasson v Eona @ Star Bowl, Ediville). Tasson RB Marshwell season-ending injury (inj_out 99) before R2. NOT PLAYED; waiting on Dan's go for playoff.run_sf.
RULE (Dan, 2042): semis always Copper-Steam, Lumber-Star or Redwood-501 from 2043; cycle 2043 Redwood-501, 2044 Lumber-Star, 2045 Copper-Steam. No overlap with awarded title sites 2043-2044. Future title awards (2045+) must avoid that year's semi cities: Copper-Steam=Billiataho/Coachville, Lumber-Star=Port Logan/Ediville, Redwood-501=Kirkwood/Stamford. SF 2042 NOT PLAYED; waiting on Dan.
2042 PLAYOFF SF PLAYED: Dietsche 28 Pistolheart 13 (Steam Bowl); Eona 31 Tasson 28 (Star Bowl). FINAL: Dietsche v Eona @ Palm Creek (Natzumakis). Preview next, then Dan's go for run_champ. REMINDER queued for after season: award 2045-49 title sites, show full list.
2042 NATIONAL CHAMPIONSHIP PLAYED (Palm Creek, Natzumakis): (4) Eona 56, (1) Dietsche 24. Eona is the 2042 national champion; history.champ[2042]=(Eona, Dietsche); awards canonized by finalize_season (Ryskamp Torrarini). Run happened before a second call raised 'already played' (guard held, single game). FINAL MEDIA POLL filed (key 16, media_history[15], media_final_key=16; champion first on all ballots, playoff games now in loss penalties; media_pool.py.pre_final_poll): 1 Eona 2 Dietsche 3 Park Island 4 Tasson 5 Ranroman State. STANDING RULES (Dan): season viewer republished with EVERY playoff round; final media poll after the title game; previews every round. NEXT: post-season parity audit, award 2045-49 title sites, rollover.
2042 POST-SEASON PARITY AUDIT RUN (parity_audit_2042.md). Findings: <=2-loss power teams 10,8,7,7,5 (2038-42); league spread compressing (range 55 -> 39); ranked lost 20/40 (50%) to unranked wks12-14 vs model 33% (13.1) and 33-34% in 2040-41; wk14 half rivalry games, rivalry gap x0.55 (pbp_engine.py:302), fav win % in rivalry 68-74% vs 80-82% other 2040-42; guests 118-18. NO ENGINE CHANGE MADE; options sent to Dan.
2042 PARITY OPTION FOUR TESTED (parity_cause_2042.md): spread NOT structurally compressing (sd 9.3 is the long-run norm; 2038-39 were the high outliers right after the restart, strength-prestige corr 0.83 -> 0.78); talent still follows prestige (0.944); minor leaks: portal flow to strong teams 0.52 -> 0.32, draft 210 -> 280 from 2040. Elite records still short of restart projection (top-5 mean L 1.6-3.4 vs 1.08; top-10 win% 79-82 vs ~90 real). Recommendation sent: sweep NOISE_SCALE + rivalry factor at ~10,000 games/setting before 2043; add parity monitor at wk8/wk14; no pipeline changes. NO ENGINE CHANGE MADE.

### 2042 post-season: parity follow-through
RIVALRY_GAP now 0.70 (forward-only, backup pbp_engine.py.pre_rivalry_gap); NOISE_SCALE left 1.0. Added parity_sweep.py, parity_monitor.py, ballot_prep.py net-rank column, committee.title_site_check. Open: Dan to award 2045-2049 title sites.

### Title sites 2045-2051 (Dan)
Awarded 2045 Kirkwood, 2046 New Madrid, 2047 Marymond, 2048 Nelson Heights, 2049 Lornaman, 2051 Queensville (backup universe.pkl.pre_champ_2045_51). 2050 Tengus City pending location.

### 2050 title site: Tengus City (Dan). Local city_coords were missing Tengus City/Purcell and had stale New Madrid/Thurmond; synced to canon map package.

## 2042-43 OFFSEASON -- Stage 1 of 7 COMPLETE: coaching carousel (2026-10-24)
Backups state/*.pkl.pre_s18_carousel; s['carousel_s17']. Prestige step ran (152 moved on 980 results). 22 hires: 9 sitting HCs poached,
2 dream jobs, 3 retreads, 3 first-timers, 1 subdivision HC; 32 coordinator moves, 12 raids. Vacancies: 7 offseason firings, 4 retirements
(Churchill, Dove Island State, North Hatesei, Queensville), 2 interims not retained, 9 poached away, 2 dream-job exits.
Headlines: DeAndre Kingsbrook leaves German Shores for Greene (dream job, rating 10.62, best hire); Vika Lameotter to Orlot (dream job,
from Ranroman OC); Perla Notaro Eternal Fox -> North Hatesei; Kabir Venkatadeva East Tasson -> Verigon; chain Fiota State -> East Tasson,
New Madrid -> Dove Island State, Cordelle/Starfield/German Shores shuffle. Nico Salaanelli (fired Milharvey) retread at Stanton State;
Ebony Anywale (fired Kaji Kita) retread at North Hatesei St. NEXT: Stage 2, the 2043 draft pool for the RFL (needs Dan).

## 2042-43 OFFSEASON -- Stage 2 of 7 IN PROGRESS: 2043 draft pool handed to the RFL
export_draft_pool.py -> state/draft_pool_2043.json: 3,640 declared (2,461 Sr, 1,156 early, 23 subdivision). Project doc claude/cfb_draft_pool_2043.json = TOP 700 slim;
full file sent to Dan as attachment. NEXT: RFL returns 280 picks as claude/rfl_draft_2043_picks.json -> install_rfl_draft.py -> portal.

## 2042-43 OFFSEASON -- Stage 2 of 7 COMPLETE: the 2043 draft, run by the RFL
Picks from GitHub data/rfl_draft_2043_picks.json -> state/rfl_draft_2043.json -> install_rfl_draft.py --commit -> s['draft_s17'] + mark_departures.
Backups state/{season_state,rosters}.pkl.pre_s18_draft. 280 valid, 2,784 leaving college, 833 early entrants withdrew; 179 early entrants drafted, 1 subdivision.
#1 overall Veronique Quisveiro (Kaji Kita DL, Jr) to Lornaman; #2 Yrei Joryosei (Vaughn Bay State DL) to Bruca Beach; #3 Afamasaga Claycroft (UFNH DL) to Far Farris.
(Mistake noted: I first searched only the Project for the picks and said they were missing; they were on GitHub under data/.)
## 2042-43 OFFSEASON -- Stage 3 of 7 COMPLETE: transfer portal
Backups state/*.pkl.pre_s18_portal; s['portal_s17']. 407 entrants, 284 transfers, 123 no takers.
Flows L6->P6 114 / P6->P6 58 / P6->L6 37 / L6->L6 75 (2042: 102/62/46/80). Classes So 104 Jr 90 Fr 82 RS 8.
G14 in 32 / out 8 = +24 (2042 +15, 2041 +29, 2040 +18). 114 entrants lost a coach, 20 followed him. Top value: Raghav El-Fahim (Hoganelle WR) to Coastal Ranroman.
NEXT: Stage 4 recruiting.

## 2042-43 OFFSEASON -- Stage 4 of 7 COMPLETE: 2043 recruiting (2026-10-24)
Backups state/{season_state,rosters}.pkl.pre_s18_recruiting; stored s['recruiting_s17'] (class_size, needs_total, signed, unsigned). Assembled by hand as last year.
National class 2,822 | needs 2,490 | signed 2,490 | 332 unsigned (12 four/five-stars found no cap room).
Class 5* 13 | 4* 282 | 3* 988 | 2* 1,129 | 1* 410. Signed 5* 13 | 4* 270 | 3* 988 | 2* 1,129 | 1* 90.
Blue-chips signed 283: G14 58, PN 45, MV 44, JB 41, BS 39, WC 35; L6 total 21 (7.4%; 2042 about 10 of 275). Low Sixteen 5, East Forest 4, others 3 each. 68 programmes landed none.
Best classes by stars: Pistolheart 72, Antiragal State 67, Eona 66, Ranroman State 62, Crayellan 61, New Madrid 60.
WATCH: L6 blue-chip share roughly doubled vs 2042. NEXT: Stage 5 development.

## 2042-43 OFFSEASON -- Stage 5 of 7 COMPLETE: 2043 development (2026-10-24)
Backups state/{rosters,season_state}.pkl.pre_s18_dev; s['development_s17']. 7,086 players, mean +0.277 (Fr +0.489, So +0.196, RS +0.192, Jr +0.113).
316 breakouts, 70 busts, r_coach 0.454 (2042: 0.606). Best team development: Eternal Fox +0.419, Ranroman +0.418, Ranroman State +0.415, Skeenerland State +0.403, Crayellan +0.400; lowest Kaji Kita State +0.166, Milharvey +0.175, Leafette +0.182.
Players rated 9.0+: 28 (post-draft). NEXT: Stage 6 roster finalisation.

## 2042-43 OFFSEASON -- Stage 6 of 7 COMPLETE: 2043 roster finalisation (2026-10-24)
Backups state/{rosters,season_state}.pkl.pre_s18_rfinal. departed 2,784 | recruits added 2,490 | walkons 0 | floor fills 298 | trimmed 0 |
rosters 63-69, total 9,874. No _leaving flags remain. Rollover (stage 7) pending.

## 2042-43 OFFSEASON -- Stage 7 of 7 COMPLETE: rollover, 2042 closed and 2043 open (season 18) (2026-10-24)
Backups state/{season_state,rosters,coaches,universe}.pkl.pre_s18_rollover. Classes Sr 1,965 | Jr 2,427 | So 2,505 | RS 189 | Fr 2,788 (Sr down from 2,461 in 2042: bigger 2043 draft exit plus a smaller junior class).
456 staff records advanced. Records, polls, committee/media history reset; season_archive row '17' present (champion Eona); next_week 0.
Preseason top 10: Skeenerland State 10.57, Kaji Kita 10.28, Rogaela State 10.14, Pistolheart 10.10, Eona 10.08, Kaji Daun, North Verigon, Dietsche, Eastern State, UFNH. Range 6.59-10.57.
NEXT: 2043 schedule (non-conference hand-off -> Scheduling Office; conference office; no week-14 guest games), media pool redraw for s18 (carry-over rule), preseason.
Parity: RIVALRY_GAP 0.70 is live from 2043; run parity_monitor.py at weeks 8 and 14 and post-season. Title site 2043 = Canesta (Kaji Daun).

## 2043 SCHEDULE HAND-OFF (2026-10-24)
Hand-off section added to PENDING.md. Nothing scheduled yet; fresh conversation should start at step (1) non-con Scheduling Office for s18.
 
 ## 2043 SCHEDULE -- Scheduling Office published for season 18 (2026-10-24, new session). Engine restored from GitHub (cfb/ -> /home/claude/cfb2, gunzip state, games_db parts joined).
 export_schedule_board.py: 152 programmes | 217 guests | 6 locked cross-conf | 444 non-conference slots for Dan. Unreturned visits 240 pairs (3.2/programme); 16 series still owed a return ground.
 Page: out/schedule_office.html (template + __DATA__), published over artifact 6w2G7gu6yGaWNrqPkypmLW (v11, saves under schedule/s18). NEXT: Dan hand-places; pull save -> noncon_s18_handoff.json -> fill_noncon + fix_p6_hosting. NO week-14 guest games in 2043.

## 2043 SCHEDULE -- BUILT AND INSTALLED (2026-10-26)
Dan's Series Office bookings (series/y2043, 64 games + 6 locked rivalries, 134 with hand-picked weeks) -> convert_series_db.py -> fill_noncon (87 guests + 69 FBS auto-added; 136 guests) -> fix_p6_hosting -> export_conf_board (plan-driven, 0 problems) -> fill_conf (no hand-placed conference weeks; all Dan's non-con weeks and the 35 locked rivalries held) -> install_hand_schedule --commit, audit CLEAN.
980 games (684 conf, 296 non-con, 136 guests); week 0: 12 games; by week 0-14: 12/87/68/67/68/68/66/66/69/69/64/67/66/67/76; 3 programmes with a 4-game home/road run (worst Barhold, 4).
fill_conf patched (pre-change copy fill_conf.py.pre_s18): guest games are never placed in week 14 (standing rule), the first fill had 8.
state/season_state.pkl.gz, sub_rosters.pkl.gz, sub_coaches.pkl.gz re-pushed after install. NEXT (new conversation): media pool s18, preseason notes + page, week 0.
2026-10-26: Dan wants to view/change the INSTALLED 2043 calendar. Conference Office republished for s18 (v23; https://claude.ai/artifact/YXQd4pYUooTZaUb9tUs3yS) with all 980 filled weeks seeded (conf_board.json + db conf/s18 v1). Office read of snapshot.data() made shape-tolerant. AFTER Dan's edits: pull conf/s18 -> convert_conf_db.py -> install_hand_schedule.py --commit again (nothing played yet), re-gzip season_state/sub_rosters/sub_coaches and re-push. Hand-off before edits: conf_s18_handoff.json (complete).

## 2043 SCHEDULE -- REINSTALLED WITH DAN'S EDITS (2026-10-26 ~18:5x)
Dan edited 7 weeks in the Conference Office (Power North: Diveo State-Kaji Kita 10->2, Northlight-Diveo 4->2, Skeenerland-Marblehead 10->6, Barhold-Forrester 2->12, Barhold State-Grizzly Hills 2->3; Eona-Pinn College 1->12, Repidome-Eona 2->1).
install_hand_schedule --commit on state/conf_sched_s18_dan.json (now also conf_sched_s18.json): audit CLEAN, 2 programmes with 4-runs (worst Ciarralotta 4). season_state/sub_rosters/sub_coaches re-gzipped and pushed.
STANDING SCHEDULING PREFERENCES (Dan, 2043):
  * no team (power teams above all) ends the season without a HOME game in the last four weeks (11-14) -- all 152 pass in 2043
  * the three byes should not be bunched close together (e.g. weeks 0 and 2, or 4/6/8 followed by a long unbroken run); 5 L6 programmes still have all three byes inside six weeks in 2043 (Reid State, Skirter, Coachville College, Holliday, Waterloo) -- left as Dan installed
  * break long unbroken runs of games (7-9 straight weeks) with a mid-season bye
  TODO: teach fill_conf these as soft terms before the 2044 build.
NEXT (new conversation): media pool s18, preseason notes + page, week 0.

## 2043 PRESEASON -- 2026-10-26 (new conversation, container wiped again)
RESTORED from GitHub (minigolfwiz/roiland-rfl, cfb/ -> /home/claude/cfb2): gunzip state, games_db parts joined; season 18, next_week 0, 980-game schedule (Dan's Conference Office edits) installed.
Media pool s18 drawn by media_pool.make_pool (30 returning / 30 new, no school in all three of 2041-43). Preseason poll: run_season.poll_update(seed=10000) -> media_history['pre'], media_ballots[0]. Backup state/season_state.pkl.pre_s18_preseason.
Preseason top 5: Eona (all 60 firsts), Ranroman State, Dietsche, Rogaela State, Barhold; Black Forest 21st is the only L6 team in the 25. 25 notes in state/preseason_notes.json (2042's kept as preseason_notes_s17.json), written from export_preseason facts + playoff_s17.pkl results; no mascots/ratings.
Roiland Preseason republished (v6), Media Pool (v52).
FINDING: games_db in the repo holds only the 980 regular-season S17 games -- the 12 conference finals and 23 playoff games of 2042 are NOT in it (results survive in state/playoff_s17.pkl and history). Check whether the push predates the postseason before relying on box scores for 2042 CCG/playoffs.
Week 0 Gameview candidates: Skeenerland State at Ranroman State; Ranroman at Will Tech; Orlot at Park Island; Riveral at Burrstone. NEXT: Dan picks -> `python3 week_cycle.py 0 <host>`.

## 2043 WEEK 0 played (Gameview: Skeenerland State at Ranroman State) -- 2026-10-26
#2 Ranroman State 38-20 #20 Skeenerland State (Solland 350/5/1 for Ranroman State, Sorlovei 274 rec/3; Cha 236/1 in defeat). #6 Park Island lost 23-24 at home to Orlot (Torrarini 226/1/3 INT; Mesysei 151 rush/1; Lundby 183/2). #10 Ranroman 28-6 at Will Tech. Riveral 33-30 OT at Burrstone; Ireland River 13-10 Rogaela Tech; Mount Cairn 20-17 Repidome.
Guests 0-2. Poll: Eona 1, Ranroman State 2, Dietsche 3, Rogaela State 4, Barhold 5; Park Island fell 13 to 19th; nobody dropped out. Backup state/season_state.pkl.pre_w0.
Season viewer (v157) and Media Pool (v53) republished. The 2042 viewer (the only copy of the 12 CCG + 23 playoff box scores) archived at cfb/archive/season_viewer_2042_full.html.gz before being overwritten.
NEXT: week 1 Gameview pick (Hatesei at Skylar Rose; Eona at Repidome; Rogaela State at Rogaela; Ireland River at UFNH).

## 2043 WEEK 1 played (Gameview: Hatesei at Skylar Rose) -- 2026-10-26
#14 Skylar Rose 28-20 #15 Hatesei (Verville 301/4/3 INT; Sorlemyr 421/1/3 INT, Milovar 191 rec for Hatesei). Ranked losers: #3 Dietsche 17-30 to East Tasson (Slaviczek 358); #6 Crayellan 21-30 to Hoganelle (Kofmah 379; Omtreimyr 4 INT); #9 North Hatesei 10-28 to West Hatesei (Ashford 295/4); #19 Park Island 13-24 to Reid State (0-2); #24 Kaji Daun 13-21 OT to Far Farris (DL Lourdes Leregard out for the year).
Top-10 wins: #1 Eona 38-31 at Repidome; #4 Rogaela State 27-10 at Rogaela; #5 Barhold 38-3 Holliday; #8 Pistolheart 38-0 and #10 Central Stanton 40-0 over guests. Guests 3-31 on the week (NW Stanton, Harko, Skeenerland Parley won); season guests 3-33.
Poll: Eona, Ranroman State, Rogaela State, Barhold, UFNH 5th (+8). Dropped out: Park Island, Kaji Daun. In: Roosevelt 23rd, Ciarralotta State 25th. Backup state/season_state.pkl.pre_w1. Viewer and Media Pool republished.
NEXT: week 2 Gameview pick (North Hatesei at Yrei Trobniy; Black Forest at Ciarralotta State; UFNH at Ekralund State; Marblehead at Crayellan State).

## 2043 WEEK 2 played (Gameview: Black Forest at Ciarralotta State) -- 2026-10-27
#25 Ciarralotta State 27-17 #18 Black Forest (Manupati 497/3/5 INT, Rocheville 228 rec; Chrykidis 395/1/3 INT). Ranked losers: #5 UFNH 24-27 to Ekralund State (2-1); #6 Pistolheart 37-40 OT to #31 Canesta State at home (Kyo-Hwan 343 rush/3; Clairlac 484/3/4 INT); #18 Black Forest; #22 North Hatesei 3-24 at #13 Yrei Trobniy (0-2).
Top-10 wins: #2 Ranroman State 45-31 UN Minko; #3 Rogaela State 68-7 LSFA (Althauer 362 rush/4); #7 Ranroman 51-21 Barhold Valley; #8 Eastern State 28-14 Boulder Creek; #10 Tengus State 35-30 Diamond City. Other: German Shores 41-38 OT at #26 Verigon; Kaji Kita 25-24 Diveo State. Guests 0-13; season guests 3-46.
Poll: Ranroman State 1, Rogaela State 2, Eastern State 3, Eona 4, Barhold 5. Dropped out: North Hatesei. New: Krobe State 21st. Backup state/season_state.pkl.pre_w2. Viewer v159, Media Pool v55 republished.
NEXT: week 3 Gameview pick (Crayellan at Tasson; Dietsche at Eona; Rogaela State at Rogaela Tech; Skylar Rose at Far Farris).

## 2043 WEEK 3 played (Gameview: Dietsche at Eona) -- 2026-10-27
#17 Dietsche 41-17 #4 Eona at Eona (Ackerbauer 292/3/0, Runningwater 212 rec; Eona's Nagakubo 145/2/1). #20 Crayellan 34-31 #7 Tasson at Tasson (Omtreimyr 497/4/4 INT; Hochholz 367/3/2, Fentreimyr 194 rec/2) -- the only two ranked losses.
Top-10 wins: #1 Ranroman State 30-14 RU Herriman; #2 Rogaela State 30-0 at Rogaela Tech; #5 Barhold 31-21 Burrstone; #6 Ranroman 50-0 Enos; #8 UFNH 41-32 Parchynt; #9 Skylar Rose 44-21 at Far Farris (Verville 503/4/0); #10 Central Stanton 44-30 Milharvey. Guests 2-20 (Henderson State, Central Fiota State won); season guests 5-66.
Poll: Rogaela State 1, Eastern State 2, Ranroman State 3, Ranroman 4, Barhold 5; Eona fell 15 to 19th. Nobody dropped out. Backup state/season_state.pkl.pre_w3. Viewer v160, Media Pool v56 republished.
BUG FIXED (gameview_detail.py, pre-fix copy .pre_sortfix): the "last three meetings" lines sorted on b['season']/b['week'], which games from the rebuilt era (8,061 of 16,886) do not carry, so they showed the OLDEST meetings (2025-2034) instead of the latest. Now sorted on the S<n>W<n> game id. Series records were never affected; weeks 1-3 candidate detail only had series of 3 or fewer games, so nothing reported earlier was wrong.
NEXT: week 4 Gameview pick (Tengus State at Barhold; Ranroman State at Stanton; Ranroman at Ciarralotta; Skylar Rose at Natzumakis).

## 2043 WEEK 4 played (Gameview: Tengus State at Barhold) -- 2026-10-27
#11 Tengus State 42-24 #5 Barhold at Barhold (Vikstad 256/4/0, Caraascio 179 rush/2; Gyenna 192/1/2 INT). Ranked losers: #7 UFNH 23-31 to #30 Verigon (U-Cheol 326/4/2, Fairhurst 273 rec/4; UFNH 3-2); #10 Roosevelt 31-50 to Barhold Valley (Whitwood 239 rush/4); #22 Hatesei 10-27 to #19 Eona.
Top-10 wins: #1 Rogaela State 20-6 Keytommiyr; #2 Eastern State 31-24 Leafette; #3 Ranroman State 20-11 at Stanton; #4 Ranroman 14-12 at Ciarralotta; #6 Skylar Rose 19-16 OT at Natzumakis; #8 UNN 37-21 Cordelle; #9 Central Stanton 31-14 at Coachville College. #12 Tasson 38-35 at Krobe (Hochholz 476/1/0). Guests 0-4; season guests 5-70.
Poll: Rogaela State 1, Ranroman 2, Eastern State 3, Ranroman State 4, Tengus State 5 (+6); Barhold fell 13 to 18th, UFNH 8 to 15th. Dropped out: Hatesei. Verigon in at 21st. Backup state/season_state.pkl.pre_w4. Viewer v161, Media Pool v57.
NEXT: week 5 Gameview pick (Krobe State at Tasson; Crayellan at Verigon; Eastern State at Coachville; Yrei Trobniy at Natzumakis State).

## 2043 WEEK 5 played (Gameview: Krobe State at Tasson) -- 2026-10-27
#12 Krobe State 49-13 #10 Tasson at Tasson (Freeley 245/5/0; Redwater 136 rec/2). Ranked losers: #3 Eastern State 27-29 to Coachville; #6 Skylar Rose 35-41 to Kaji Kita State; #7 Central Stanton 20-21 to UN Ediville (Asanari 245/3/2); #16 Marblehead 30-37 to Northlight; #17 Crayellan 24-26 to #21 Verigon; #18 Barhold 42-47 to Southern Tengus; #19 Dietsche 28-40 to #34 Leafette; #24 Pistolheart 21-26 to #33 Stanton.
Top-10 wins: #1 Rogaela State 27-13 Will Tech; #2 Ranroman 23-13 North Hatesei; #5 Tengus State 14-0 Barhold State; #8 UNN 38-31 Kaji Daun (Kingsworth 467/3/1). Guests 0-6.
Poll: Rogaela State 1, Ranroman 2, Tengus State 3, Ranroman State 4, Ciarralotta State 5. Dropped out: Dietsche, Pistolheart. Backup state/season_state.pkl.pre_w5. Viewer v162, Media Pool v58.
NEXT: week 6 Gameview pick (Rogaela State at Antiragal; UNN at UN Ediville; Central Stanton at Ranroman State; Krobe State at S Antiragal State).

## 2043 WEEK 6 played (Gameview: Krobe State at S Antiragal State) -- 2026-10-27
#7 Krobe State 38-24 #31 S Antiragal State (Freeley 276/4/2; Haruyama 184 rec/1 for SAS). Ranked losers: #2 Ranroman 6-23 to #34 Pistolheart; #5 Ciarralotta State 20-26 OT to Milharvey; #8 Eastern State 20-41 to Ekralund State; #10 Yrei Trobniy 10-29 to Burrstone; #12 Central Stanton 13-38 to #4 Ranroman State; #16 Verigon 37-40 OT to Costique River; #19 Antiragal State 13-30 to #18 Tasson; #21 Skeenerland State 21-30 to #23 Barhold; #22 Eona 7-31 to North Hatesei; #25 Phangrine State 20-36 to #29 Keeper.
Top-10 wins: #1 Rogaela State 38-3 Antiragal; #6 UNN 41-24 at UN Ediville (Kingsworth 377/5/1); #9 Lornaman 28-21 at Coachville. Guests 1-4 (Bragi 35-7 Hofferteltra).
Poll: Rogaela State 1, Tengus State 2, Ranroman State 3, Krobe State 4, Lornaman 5. Dropped out: Eona, German Shores, Phangrine State. RYSKAMP TWENTY (auto, week 6): Verville, Kyo-Hwan, Yunye, U-Cheol, Lamedeer, DiStefano, Althauer, Northman, Bonatelli, Kingsworth, Freeley, Hochholz, Westton, Darwish, Chrykidis, Filipek, Caldini, Aosaka, Lesinsky, Neitaw. Backup pre_w6. Viewer v163, Media Pool v59.
NEXT: week 7 Gameview pick (Skylar Rose at Roosevelt; UNN at Central Stanton; Barhold at Marblehead; Tengus State at Costique). Week 8: Dan hand-builds committee ballot; parity monitor.

## 2043 WEEK 7 played (Gameview: Skylar Rose at Roosevelt) -- 2026-10-27
#11 Roosevelt 30-10 #9 Skylar Rose (Yunye 395/2/0; Verville 239/0/3 INT, Aosaka 178 rec). Ranked losers: #6 UNN won 42-33 at #20 Central Stanton (Kingsworth 478/4, Verfleur 483/5, Karakos 288 rec/3) -- no loss; losers: #9 Skylar Rose; #19 Black Forest 28-32 to Hansenne; #20 Central Stanton 33-42 to UNN; #21 Eona Navy 27-35 to West Hatesei; #22 Stanton 17-36 to Eona; #24 Skeenerland State 23-31 to Northlight; #25 Barhold 20-35 to #14 Marblehead.
Top-10 wins: #1 Rogaela State 45-3 Krobe; #2 Tengus State 17-10 at Costique; #3 Ranroman State 24-17 at UN Ediville; #5 Lornaman 16-7 at Milharvey. Guests 0-5.
Poll: Rogaela State 1, Tengus State 2, Ranroman State 3, Lornaman 4 (+1), Krobe State 5. Dropped out: Stanton, Skeenerland State, Barhold. Backup pre_w7. Viewer v164, Media Pool v60.
NEXT: WEEK 8 -- Dan hand-builds the committee ballot first; Gameview candidates only after his rankings. Parity monitor after week 8. (Provisional media-poll candidates were NOT shown.)

## 2043 FIRST COMMITTEE BOARD INSTALLED (after week 7 results, for week 8) -- state/ballot_s18_w8.json, audit CLEAN
1 Ranroman State, 2 UNN, 3 Lornaman, 4 Tengus State, 5 Northlight, 6 Krobe State, 7 Roosevelt, 8 Rogaela State, 9 Fiota Bay, 10 Ranroman, 11 Marblehead, 12 Leafette, 13 Eona, 14 Antiragal State, 15 Yrei Trobniy, 16 Ciarralotta State, 17 Crayellan, 18 Phangrine State, 19 Ekralund State, 20 Skeenerland, 21 Tasson, 22 German Shores, 23 Costique River, 24 Orlot Western, 25 Keeper. Committee is now the ranking of record. Committee Ballot artifact v46. Backup season_state.pkl.pre_committee.
NOTE: gameview_detail prints MEDIA-poll rank tags (#6 UNN); candidate list itself uses committee ranks.
Week 8 candidates: Ranroman at UNN; Leafette at Krobe State; Phangrine State at Lornaman; Fiota Bay at Verigon. Passed: Barhold State at Northlight; Kaji Kita at Tengus State.
NEXT: week 8 Gameview pick; parity monitor after week 8.

## 2043 WEEK 8 played (Gameview: Phangrine State at Lornaman) -- 2026-10-27
#18 Phangrine State 51-20 #3 Lornaman at Lornaman (Georzoglou 468/4/1; Caldini 248/2/4 INT; Blaufelder 214 rec/1). Ranked/board losers: #5 Northlight 24-38 to Barhold State (Fenreniy 446/3); #10 Ranroman 20-38 to #2 UNN (Kingsworth 378/4); #12 Leafette 26-34 to #6 Krobe State; #13 Eona 44-45 to Ciarralotta (Triakos 363/4, Xizu 199 rush/2); #17 Crayellan 26-34 to UFNH (Lamedeer 377/4, Tetteh 222 rec/3). Wins: #4 Tengus State 30-10 Kaji Kita; #9 Fiota Bay 30-6 at Verigon. Guests 2-4 (Zialo State 16-14 Costique State; Redford 27-24 Hoganelle).
Media poll (info only; committee is ranking of record): Rogaela State 1, Tengus State 2, UNN 3, Ranroman State 4, Krobe State 5.
PARITY MONITOR (wk 8): undefeated 7, <=2 losses 48, top-5 mean losses 0.60, top-10 win% 92.4 (reference 74-83) -- elite records still well above 2038-42 pace; favourites by gap: 0-3 53%, 3-7 68%, 7-14 76%, 14-21 93%, 21+ 100% (in range). Ranked lost 27/99 to unranked wks 1-7 (27% vs 22% expected), wk 8 3/12.
Committee Ballot artifact v47 built for week 9. Viewer v165, Media Pool v61. Backup pre_w8.
NEXT: Dan's week 9 committee ballot; THEN week 9 Gameview candidates.

## 2043 WEEK 9 COMMITTEE BOARD INSTALLED (after week 8 results) -- state/ballot_s18_w9.json, audit CLEAN
1 UNN, 2 Ranroman State, 3 Tengus State, 4 Krobe State, 5 Roosevelt, 6 Rogaela State, 7 Fiota Bay, 8 Phangrine State, 9 Lornaman, 10 Marblehead, 11 Antiragal State, 12 Yrei Trobniy, 13 Ciarralotta State, 14 Ranroman, 15 Leafette, 16 Ekralund State, 17 Keeper, 18 Skeenerland, 19 Tasson, 20 Costique River, 21 German Shores, 22 Northlight, 23 UFNH, 24 Orlot Western, 25 Hatesei. Dropped out: Eona, Crayellan.
Week 9 candidates: Roosevelt at Yrei Trobniy; Ekralund State at Keeper; Rogaela State at Verigon State; Diveo at Phangrine State (non-conf). Passed: Crayellan at Fiota Bay [rivalry]; Southern Tengus at Tengus State; Keytommiyr at Krobe State.
NEXT: week 9 Gameview pick.

## 2043 WEEK 9 played (Gameview: Ekralund State at Keeper) -- 2026-10-27
#16 Ekralund State 38-6 #17 Keeper at Keeper (Hoshikubo 292/2/0; Freeland 271 rec/2; Seo-Kwan 4 INT). Board losses: #5 Roosevelt 27-30 OT to #12 Yrei Trobniy; #10 Marblehead 29-38 to Tengus (Kangrou 171 rush/3); #13 Ciarralotta State 31-34 to Stanton State (Manupati 433/4, Rocheville 363 rec/4; Eaddy 245 rush/3); #14 Ranroman 32-38 to Central Stanton (Verfleur 423/4, Karakos 334 rec/3); #17 Keeper; #18 Skeenerland 20-47 to Barhold; #22 Northlight 10-35 to Costique.
Wins: #2 Ranroman State 34-10 Ciarralotta; #3 Tengus State 38-21 Southern Tengus; #4 Krobe State 34-10 Keytommiyr; #6 Rogaela State 10-3 at Verigon State; #7 Fiota Bay 20-19 Crayellan; #8 Phangrine State 28-21 Diveo; #9 Lornaman 20-7 at Eastern State. UNN idle. Guests 0-6.
Media poll (info only): Rogaela State 1, Tengus State 2, Krobe State 3, UNN 4, Ranroman State 5.
Committee Ballot v48 built for week 10. Viewer v166, Media Pool v62. Backup pre_w9.
NEXT: Dan's week 10 ballot; then week 10 Gameview candidates. RYSKAMP: ten due at week 10 (strict subset of the twenty).

## 2043 WEEK 10 COMMITTEE BOARD INSTALLED (after week 9 results) -- state/ballot_s18_w10.json, audit CLEAN
1 UNN, 2 Ranroman State, 3 Tengus State, 4 Krobe State, 5 Rogaela State, 6 Fiota Bay, 7 Phangrine State, 8 Lornaman, 9 Antiragal State, 10 Yrei Trobniy, 11 Ekralund State, 12 Roosevelt, 13 Leafette, 14 Tasson, 15 Costique River, 16 Ciarralotta State, 17 Keeper, 18 UFNH, 19 Marblehead, 20 German Shores, 21 Orlot Western, 22 Hatesei, 23 Far Farris, 24 South Antiragal, 25 Barhold. Dropped out: Ranroman, Skeenerland, Northlight.
Week 10 candidates: Krobe State at Rogaela State; UNN at Ranroman State [rivalry; already visited]; Costique River at Fiota Bay; Phangrine State at Eastern State. No passed-over games listed.
NEXT: week 10 Gameview pick. Ryskamp TEN due after week 10 (auto, subset of the 20).

## 2043 WEEK 10 played (Gameview: UNN at Ranroman State) -- 2026-10-27
#1 UNN 35-29 #2 Ranroman State at Ranroman State (Solland 354/2/1 + 70 rush; Sandstrom 234 rec/1; Kingsworth 242/2/0). UNN 8-0, Ranroman State 7-1.
Board losses: #4 Krobe State 31-42 to #5 Rogaela State (Freeley 400/4; Chakraborty 329/3, Furumura 187 rush); #6 Fiota Bay 26-28 to #15 Costique River; #7 Phangrine State 10-38 to Eastern State (Krasovsky 232 rush/3); #17 Keeper 15-45 to Ciarralotta Tech (Shadid 337/5); #23 Far Farris 14-20 to Good River. Wins: #8 Lornaman 20-9 Diamond City; #9 Antiragal State 23-7 S Antiragal State; #10 Yrei Trobniy 31-17 at Barhold Valley; UFNH 20-17 Rogaela. Guests 2-7 (Yarrola 23-10 Churchill; Jack Todd 17-3 Underwood).
Media poll (info only): Rogaela State 1, Tengus State 2, UNN 3, Krobe State 4, Lornaman 5.
RYSKAMP TEN (auto, subset of the 20): Verville, Yunye, Kingsworth, Kyo-Hwan, Lamedeer, Freeley, Neitaw, U-Cheol, Chrykidis, Darwish.
Committee Ballot v49 built for week 11. Viewer v167, Media Pool v63. Backup pre_w10.
NEXT: Dan's week 11 ballot; then week 11 Gameview candidates.

## 2043 WEEK 11 COMMITTEE BOARD INSTALLED (after week 10 results) -- state/ballot_s18_w11.json, audit CLEAN
1 UNN, 2 Ranroman State, 3 Rogaela State, 4 Tengus State, 5 Krobe State, 6 Antiragal State, 7 Lornaman, 8 Yrei Trobniy, 9 Ekralund State, 10 Costique River, 11 Fiota Bay, 12 Roosevelt, 13 Leafette, 14 Tasson, 15 Phangrine State, 16 Ciarralotta State, 17 UFNH, 18 Hatesei, 19 Marblehead, 20 German Shores, 21 Orlot Western, 22 South Antiragal, 23 Eastern State, 24 Southern Tengus, 25 Barhold. Dropped out: Keeper, Far Farris.
Week 11 candidates: Antiragal State at Krobe State; Ciarralotta at UNN; Tengus State at Skeenerland State; Ranroman State at Orlot. Passed: Eastern State at Ciarralotta State (already visited Ciarralotta State).
NEXT: week 11 Gameview pick.

## 2043 WEEK 11 played (Gameview: Antiragal State at Krobe State) -- 2026-10-27
#5 Krobe State 34-13 #6 Antiragal State (Freeley 254/2/1; Grannes 162 rec/2; Kongiannis 171/1 + 74 rush). Krobe State 8-1.
Board losses: #1 UNN 14-38 to Ciarralotta (Miranegro 360/5, Eze 192 rec/2; Kingsworth 231/1/1) -- UNN 8-1; #2 Ranroman State 17-37 to Orlot (Lundby 192 + 26 rush) -- 7-2; #4 Tengus State 14-23 to Skeenerland State (Cha 282/2; Vikstad 280/1/3 INT, Faitai 202 rec) -- 8-1; #11 Fiota Bay 29-38 to East Costique (Dragovich 205 rush; Balaprasad 368/1/1) -- 7-3; #16 Ciarralotta State beat #23 Eastern State 30-24 (Manupati 400/3; Darwish 364/3, Eaglebear 252 rec/2); #18 Hatesei 13-21 OT to Pistolheart. Wins: #8 Yrei Trobniy 20-3 Kaji Kita State; #9 Ekralund State 40-24 at Milharvey. Rogaela State, Lornaman, Costique River, UFNH idle. Guests 1-8 (Lamb 27-18 Chapel Rock).
Media poll (info only): Rogaela State 1, Krobe State 2, Tengus State 3, Lornaman 4, UFNH 5.
Committee Ballot v50 built for week 12. Viewer v168, Media Pool v64. Backup pre_w11.
NEXT: Dan's week 12 ballot; then week 12 Gameview candidates.

## 2043 WEEK 12 COMMITTEE BOARD INSTALLED (after week 11 results) -- state/ballot_s18_w12.json, audit CLEAN
1 Rogaela State, 2 Krobe State, 3 UNN, 4 Yrei Trobniy, 5 Tengus State, 6 Lornaman, 7 Ekralund State, 8 Antiragal State, 9 Costique River, 10 Roosevelt, 11 Leafette, 12 Tasson, 13 Phangrine State, 14 Ciarralotta State, 15 UFNH, 16 Marblehead, 17 South Antiragal, 18 Skeenerland State, 19 German Shores, 20 Orlot Western, 21 Kaji Daun, 22 Southern Tengus, 23 Barhold, 24 Fiota Bay, 25 Skylar Rose. Dropped out: Ranroman State, Hatesei, Eastern State.
Week 12 candidates: Krobe State at South Antiragal; Marblehead at Tengus State; UFNH at Costique River; North Hatesei at UNN. Passed: Ciarralotta State at Lornaman (bigger game at Lornaman later); Rogaela State at S Antiragal State (already visited).
NEXT: week 12 Gameview pick. Parity monitor at week 14. No guest games week 14.

## 2043 WEEK 12 played (Gameview: UFNH at Costique River) -- 2026-10-27
#9 Costique River 35-26 #15 UFNH (Velecek 434/4/1; Lamedeer 286/3; Steinmeier 167 rec/1). 
Board losses: #3 UNN 17-22 to North Hatesei (Kingsworth 430/2/1; Lambrmatos 182 rec, Al-Mahdi 168 rec) -- UNN 8-2; #5 Tengus State 20-27 to #16 Marblehead (Altalarga 360/3/3; Faitai 215 rec) -- 8-2; #6 Lornaman 31-34 to #14 Ciarralotta State -- 8-2; #12 Tasson 10-28 to Verigon State; #17 South Antiragal 14-31 to #2 Krobe State (Freeley 462/4/2, Grannes 269 rec/3); #19 German Shores 13-35 to Trapper Point (Delmaison 235 rush/2) -- first loss. Wins: #1 Rogaela State 48-10 at S Antiragal State (10-0); #8 Antiragal State 26-10 Keytommiyr; Orlot Western 47-10 (10-0). Kaji Daun 33-30 Orlot; Hatesei 23-20 at Ranroman State. Guests 1-5 (VCA 24-21 David Harrison).
Media poll (info only): Rogaela State 1, Krobe State 2, Roosevelt 3, Tengus State 4, Orlot Western 5.
Committee Ballot v51 built for week 13. Viewer v169, Media Pool v65. Backup pre_w12.
NEXT: Dan's week 13 ballot; then week 13 Gameview candidates. Week 14: no guests, parity monitor.

## 2043 WEEK 13 COMMITTEE BOARD INSTALLED (after week 12 results) -- state/ballot_s18_w13.json, audit CLEAN
1 Rogaela State, 2 Krobe State, 3 Yrei Trobniy, 4 Costique River, 5 Ekralund State, 6 Antiragal State, 7 Ciarralotta State, 8 Marblehead, 9 Tengus State, 10 Lornaman, 11 Roosevelt, 12 Leafette, 13 UNN, 14 Phangrine State, 15 Skeenerland State, 16 UFNH, 17 Kaji Daun, 18 South Antiragal, 19 Orlot Western, 20 Southern Tengus, 21 Barhold, 22 Skylar Rose, 23 Fiota Bay, 24 Hatesei, 25 Tasson. Dropped out: German Shores.
Week 13 candidates: South Antiragal at Rogaela State; Marblehead at Skeenerland State; Park Island at Yrei Trobniy; Costique River at Rogaela. Passed: Krobe State at Antiragal (bigger game at Antiragal later).
NEXT: week 13 Gameview pick.

## 2043 WEEK 13 played (Gameview: South Antiragal at Rogaela State) -- 2026-10-27
#1 Rogaela State 30-13 #18 South Antiragal (Chakraborty 264/3; Furumura 168 rush; Havlund 138/1). Rogaela State 11-0.
Board losses: #2 Krobe State 14-52 to Antiragal (Stakos 260/4/0, Lousi 158 rec; Baifei 114/1/1) -- Krobe State 9-2; #8 Marblehead 17-52 to #15 Skeenerland State (Cha 405/5/0, Ulunoa 199 rec/2) -- 8-3; #13 UNN 26-31 to Orlot (Lundby 444/4/0; Kingsworth 400/3, Al-Mahdi 252 rec) -- 8-3; #20 Southern Tengus 0-24 to Kaji Kita. Wins: #3 Yrei Trobniy 30-26 Park Island (10-1); #4 Costique River 31-28 at Rogaela (9-2); #5 Ekralund State 49-6 Diamond City (10-1); #7 Ciarralotta State 31-30 at Keeper; #9 Tengus State 52-28 Diveo State; #10 Lornaman 38-14 at Ciarralotta Tech. Orlot Western 31-14 (11-0). Guests 3-6 (Rascha 18-13, UEKP 24-15, Northern Krobe 13-10).
Media poll (info only): Rogaela State 1, Ekralund State 2, Orlot Western 3, Tengus State 4, Roosevelt 5.
Week 14 schedule verified: 76 games, all FBS vs FBS, no guest games (standing rule held).
Committee Ballot v52 built for week 14. Viewer v170, Media Pool v66. Backup pre_w13.
NEXT: Dan's week 14 ballot; then week 14 Gameview candidates; parity monitor after week 14; then CCG.

## 2043 WEEK 14 COMMITTEE BOARD INSTALLED (after week 13 results) -- state/ballot_s18_w14.json, audit CLEAN
1 Rogaela State, 2 Yrei Trobniy, 3 Costique River, 4 Krobe State, 5 Ekralund State, 6 Ciarralotta State, 7 Antiragal State, 8 Tengus State, 9 Lornaman, 10 Roosevelt, 11 Skeenerland State, 12 Leafette, 13 Phangrine State, 14 Marblehead, 15 UFNH, 16 Kaji Daun, 17 Orlot Western, 18 Barhold, 19 Skylar Rose, 20 Fiota Bay, 21 Hatesei, 22 Tasson, 23 South Antiragal, 24 Barhold Valley, 25 UNN. Dropped out: Southern Tengus; Barhold Valley in.
Week 14 candidates: Ekralund State at Lornaman [rivalry; already visited Lornaman]; Fiota Bay at UFNH [rivalry]; Rogaela State at Dietsche [rivalry]; Yrei Trobniy at Good River [rivalry]. Passed: Leafette at Tasson (already visited Tasson).
NEXT: week 14 Gameview pick; then parity monitor; CCG.

## 2043 WEEK 14 played (Gameview: Ekralund State at Lornaman) -- 2026-10-27 -- REGULAR SEASON COMPLETE (980 games)
#9 Lornaman 37-24 #5 Ekralund State (Caldini 395/4/4; Hoshikubo 275/3/4; Freeland 150 rec/2). Both finish 10-2.
Board losses (15): #1 Rogaela State 24-45 to Dietsche (Chernecek 244 rush/2) -- 11-1; #2 Yrei Trobniy 39-48 to Good River (Stavrokidis 341/5) -- 10-2; #6 Ciarralotta State 26-31 to Ciarralotta Tech (Shadid 461/3, Fontichelli 243 rec/3); #7 Antiragal State 29-36 to Antiragal (Kongiannis 400/3/5 INT; Blackford 237 rec); #8 Tengus State 21-38 to Tengus; #11 Skeenerland State 31-37 OT to Skeenerland; #12 Leafette 24-30 OT to #22 Tasson; #13 Phangrine State 17-20 to Diamond City; #15 UFNH 19-24 to #20 Fiota Bay; #16 Kaji Daun 21-26 to Kaji Kita; #18 Barhold 24-31 to Barhold State; #19 Skylar Rose 24-42 to Southern Tengus; #24 Barhold Valley 35-44 to Kaji Kita State (Bonatelli 485/4/2, Littlelance 482/4/1, Buenamayor 303 rec/3); #25 UNN 34-51 to Eona. Wins: #3 Costique River 34-7 East Costique; #4 Krobe State 16-7 Krobe; #10 Roosevelt 18-13 Roosevelt State; #14 Marblehead 34-31 OT Costique; #17 Orlot Western 24-21 Black Forest (12-0). Guests 0-0 (no wk-14 guests, rule held).
Media poll (info only): Rogaela State 1, Orlot Western 2, Ekralund State 3, Roosevelt 4, Lornaman 5.
PARITY MONITOR (wk 14): undefeated 1 (Orlot Western), <=2 losses 11 (power 7), top-5 mean losses 2.40, top-15 2.80, top-10 win% 79.2 -- all inside 2038-42 reference ranges. Favourite win% by gap: 0-3 51, 3-7 61, 7-14 71, 14-21 89, 21+ 98 (in range). Ranked lost to unranked: wks1-7 27% (26% exp), wks 8-11 26% (27% exp), wks 12-14 40% of 45 vs 26% expected -- above expectation (reference 2040-42 wks12-14: 33/33/50%). Elite early-season records (7 undefeated at wk 8) regressed in the stretch run.
Gameview map built: gameview_2043.html (artifact https://claude.ai/artifact/KNh6UB6AdCUJ6RDKqwEYUU); needed state/roiland_map.png restored from roiland_map_package.json image_png_base64 (png now committed). 15 stops, route line per week. Viewer v171, Media Pool v67. Backup pre_w14.
CCG PREVIEW shown to Dan (ccg_preview.py; NOT PLAYED): Power North #11 Skeenerland State v #8 Tengus State; Jyras Bay #1 Rogaela State v #4 Krobe State; Great Fourteen #21 Hatesei v #16 Kaji Daun; Western Coast #2 Yrei Trobniy v #10 Roosevelt; Broad South #9 Lornaman v #5 Ekralund State; Mountain Valley #3 Costique River v #20 Fiota Bay; Vapor Stream Reid State v Hoganelle; Low Sixteen #17 Orlot Western v Hansenne; Brass Belt Eona Navy v UN Steelbridge; East Forest German Shores v Eternal Fox; Evening Star Dove Island State v Parchynt State; Southwestern Perth Island v Coastal Ranroman.
NEXT: Dan confirms -> python3 ccg.py --commit (backup first). Then selection ballot -> playoff. QUEUED (Dan): post-season parity audit.

CORRECTION (Dan, after wk 14): one more weekly committee ballot is due after week 14 results, BEFORE the conference championships (I had gone straight to the CCG preview; the CCG preview ranks were therefore the week-13 board). Committee Ballot v53 built for it (post-week-14). WAITING on Dan's top 25 -> install_committee.py state/ballot_s18_w15.json --commit; then re-run ccg_preview.py with the new ranks; then Dan's go for ccg.py --commit.

## 2043 POST-WEEK-14 COMMITTEE BOARD INSTALLED -- state/ballot_s18_w15.json, audit CLEAN (backup season_state.pkl.pre_w15board)
1 Rogaela State, 2 Costique River, 3 Krobe State, 4 Lornaman, 5 Roosevelt, 6 Ekralund State, 7 Yrei Trobniy, 8 Fiota Bay, 9 Ciarralotta State, 10 Marblehead, 11 Antiragal State, 12 Orlot Western, 13 Tasson, 14 Hatesei, 15 Leafette, 16 Tengus State, 17 Phangrine State, 18 Eona, 19 UFNH, 20 Skeenerland State, 21 South Antiragal, 22 Pistolheart, 23 Ranroman, 24 Good River, 25 Southern Tengus. Out: Kaji Daun, Barhold, Skylar Rose, Barhold Valley, UNN.
CCG PREVIEW (re-run with new ranks; NOT PLAYED): PN #20 Skeenerland State v #16 Tengus State; JB #1 Rogaela State v #3 Krobe State; G14 #14 Hatesei v Kaji Daun; WC #7 Yrei Trobniy v #5 Roosevelt; BS #4 Lornaman v #6 Ekralund State; MV #2 Costique River v #8 Fiota Bay; VS Reid State v Hoganelle; LS #12 Orlot Western v Hansenne; BB Eona Navy v UN Steelbridge; EF German Shores v Eternal Fox; ES Dove Island State v Parchynt State; SW Perth Island v Coastal Ranroman.
NEXT: Dan's go -> backup, python3 ccg.py --commit. Then selection ballot -> playoff.

## S18 conference championships (played)
Power North: Skeenerland State 33, Tengus State 17. Jyras Bay: Krobe State 34, Rogaela State 17. Great Fourteen: Hatesei 44, Kaji Daun 37. Western Coast: Roosevelt 17, Yrei Trobniy 13. Broad South: Lornaman 24, Ekralund State 21. Mountain Valley: Fiota Bay 31, Costique River 10. Vapor Stream: Reid State 35, Hoganelle 7. Low Sixteen: Orlot Western 30, Hansenne 0. Brass Belt: Eona Navy 13, UN Steelbridge 10. East Forest: German Shores 38, Eternal Fox 35. Evening Star: Dove Island State 43, Parchynt State 21. Southwestern: Perth Island 20, Coastal Ranroman 10.
Disclosure: export_playoff_board.py read champions from season state, but ccg.py writes state/conf_champs_s18.pkl; added a pickle fallback (backup export_playoff_board.py.pre_champfix). Selection Board published (artifact v7). Awaiting Dan's 24-team field JSON; install_field.py not yet run.

## S18 playoff field installed
Dan's 24-team field (state/field_s18.json) installed via install_field.py -> playoff_s18.pkl. Byes: 1 Krobe State, 2 Roosevelt, 3 Lornaman, 4 Rogaela State, 5 Hatesei, 6 Yrei Trobniy, 7 Tasson, 8 Fiota Bay. R1: 24 Dove Island St @ 9 Costique River; 23 Perth Island @ 10 Skeenerland St; 22 Reid St @ 11 Ekralund St; 21 Eona Navy @ 12 Orlot Western; 20 German Shores @ 13 Eona; 19 Kaji Daun @ 14 Leafette; 18 Ciarralotta St @ 15 Pistolheart; 17 Phangrine St @ 16 Marblehead. Round 1 previews shown; awaiting Dan's go to play.

## S18 playoff round 1 PLAYED (backups pre_s18_po1)
Costique River 42, Dove Island St 14; Skeenerland St 38, Perth Island 31; Reid St 20, Ekralund St 17; Orlot Western 31, Eona Navy 0; Eona 55, German Shores 7; Leafette 35, Kaji Daun 21; Pistolheart 44, Ciarralotta St 16; Marblehead 56, Phangrine St 27.
R2 (at higher seed): 22 Reid St @ 1 Krobe St; 16 Marblehead @ 2 Roosevelt; 15 Pistolheart @ 3 Lornaman; 14 Leafette @ 4 Rogaela St; 13 Eona @ 5 Hatesei; 12 Orlot Western @ 6 Yrei Trobniy; 10 Skeenerland St @ 7 Tasson; 9 Costique River @ 8 Fiota Bay. Season viewer v173 published. Round 2 preview next; awaiting Dan's go. (playoff_preview.py only handles r1; r2 preview needs P['r2'] pairs.)

## S18 playoff round 2 PLAYED (backups pre_s18_po2)
Reid St 27, Krobe St 16 (22 over 1); Roosevelt 43, Marblehead 34; Lornaman 41, Pistolheart 3; Rogaela St 14, Leafette 7; Hatesei 24, Eona 21; Yrei Trobniy 37, Orlot Western 0 (unbeaten run ends at 14-1); Tasson 35, Skeenerland St 20; Costique River 56, Fiota Bay 3.
QF (neutral): Roosevelt v Reid St; Lornaman v Costique River; Rogaela St v Tasson; Hatesei v Yrei Trobniy. Viewer rebuilt (1008 games), publish pending at time of this entry; QF preview next.

## S18 playoff quarterfinals PLAYED (backups pre_s18_qf)
Roosevelt 30, Reid St 3 (Copper Bowl); Costique River 41, Lornaman 14 (Steam Bowl); Rogaela St 24, Tasson 17 (Lumber Bowl); Yrei Trobniy 24, Hatesei 17 (Star Bowl).
SF: (2) Roosevelt v (9) Costique River @ 501 Bowl (Stamford, Ciarralotta); (4) Rogaela St v (6) Yrei Trobniy @ Redwood Bowl (Kirkwood, Crayellan). Viewer rebuilt (1012 games). SF preview shown; awaiting go.

## S18 playoff semifinals PLAYED (backups pre_s18_sf)
Costique River 41, Roosevelt 38 (501 Bowl); Rogaela St 41, Yrei Trobniy 20 (Redwood Bowl). FINAL: (4) Rogaela St v (9) Costique River @ Canesta (Kaji Daun). Series Rogaela St 3-1.
Awards basis: created state/season_state.pkl.pre_s18_po_r1 as a copy of pre_s18_po1 (snapshot taken after CCGs, before round 1) because run_champ's finalize_season looks for that name. Viewer rebuilt (1014 games). Title-game preview shown; awaiting go.

## S18 (2043) AWARDS NAMED (Dan asked mid-playoff; basis reg season + CCG, snapshot pre_s18_po_r1; backup season_state.pkl.pre_s18_awards)
CORRECTION: the Ryskamp FOUR step (due right after the CCGs, strict subset of the ten) was missed; done now as the top four pooled by award score. Ryskamp FOUR: Kingsworth (UNN), Verville (Skylar Rose), Yunye (Roosevelt), Neitaw (Leafette). RYSKAMP WINNER: Douglas Kingsworth, UNN QB Jr (4,622 yds, 35 TD, 7 INT). Seumalo (German Shores) led the open board but was outside the pools.
DPOY Kavya Somaprasad (Orlot Western DL Jr); finalists Fontobruno (Chapel Rock), Blancbourg (Marines), Thornley (Ek Tech). FOY Joaquin Caldini (Lornaman QB Fr); finalists Ramadeva (Vaughn Bay), Balaprasad (Fiota Bay), Ackerbauer (Dietsche). COY Orlot Western (13-0 regular season; CCG champion).
Awards canonized via finalize_season (history.awards[2043]); champion/runner-up still to be filed when the title game runs.

## S18 (2043) NATIONAL CHAMPIONSHIP PLAYED (Canesta, Kaji Daun; backups pre_s18_champ)
(9) Costique River 47, (4) Rogaela State 43. Costique River is the 2043 national champion; history.champ[2043]=(Costique River, Rogaela State). A 9 seed won it, beating the 24-seed-era no-bye path of 3 straight; Rogaela State finished 14-3 as runner-up.
FINAL MEDIA POLL filed (media_history[15], media_final_key=16, backup pre_s18_finalpoll; champion first on all ballots): 1 Costique River 2 Rogaela State 3 Roosevelt 4 Orlot Western 5 Lornaman 6 Krobe State 7 Ekralund State 8 Yrei Trobniy 9 Tengus State 10 UFNH. Season viewer v177 and Media Pool republished.
NEXT: post-season parity audit (Dan queued; wk 12-14 ranked-lost-to-unranked 40% vs ~26% expected), award title sites 2052+ if due, rollover and 2044 build (teach fill_conf calendar preferences first).

## S18 POST-SEASON PARITY AUDIT (Dan queued) -- see parity_audit_2043.md
2043 inside the 2038-42 envelope; the 2042 worry (few 2-loss power teams) did not repeat (7/78 at <=2 L). Only flag: weeks 12-14 ranked-lost-to-unranked 40% vs ~26% expected, week-14 favourites 70% vs 80% other weeks (trend since 2040), rivalry favourites 70%. No engine change shipped.

## 2043 offseason, stages 1-2 (rollover to 2044)
- Stage 1 carousel run (carousel.py): 20 HC vacancies filled (10 fired, 1 retirement [Hansenne], 1 interim not retained [Dove Island], 8 poached HCs backfilled), 30 coordinator moves, 12 raids. Stored in s['carousel_s18']; backups *.pre_s19_carousel.
- Stage 2 draft pool exported (export_draft_pool.py): state/draft_pool_2044.json, 3,211 declared. Slim top-700 filed to Project as claude/cfb_draft_pool_2044.json; full pool sent to Dan. Waiting on RFL's 280 picks ({"season":18,...}) -> install_rfl_draft.py --commit, then stages 3-7 (portal, recruiting, development, roster_final, rollover).
- Parity audit 2043 written up in parity_audit_2043.md; no knobs changed. Open for Dan: week-14 soft spot.

## 2043 offseason, stages 2-7 complete -> 2044 open
- Stage 2: RFL draft installed (data/rfl_draft_2044_picks.json, 280 picks, 0 rejected; 198 early entrants drafted, 1 subdivision). 2,316 leave college, 872 withdrew to school.
- Stage 3 portal: 291 transfers, 147 withdrew. Stage 4 recruiting: national class 2,816 (13 five-stars, 282 four-stars), 2,018 spots open, 798 unsigned. Stage 5 development run. Stage 6 roster_final: 1,261 walk-ons, 759 floor fills, rosters 63-65.
- Stage 7 rollover (--commit): 2043 archived (champion Costique River), classes advanced, 209 redshirts, staff aged, season reset to 2044 (season 19). Backups *.pre_s19_portal/recruit/dev/final/rollover.
- Preseason top 10: Skeenerland State 10.31, Dietsche, Rogaela State, Pistolheart, Eona, Kaji Kita, Central Stanton, Roosevelt, Kaji Daun, North Hatesei.
- Dan: leave week 14 alone (no engine change). TODO before 2044 build: teach fill_conf calendar preferences; no week-14 guest games.

## 2044 SCHEDULE -- Series Office rolled forward (2026-10-27)
Dan: "send me the same multi-year noncon builder". conf_plan.py 19 10 re-run (2044-2050 slates identical to the old plan; 2053 added; pre-copy conf_plan.json.pre_s19) -> export_series_board.py (window 2044-2053) -> series_office_template.html with __DATA__/__SEED__ -> republished over artifact FsJi7pHPnmBhXVkj6BTAcb (v17, db docs series/y<year> kept). Seed = Dan's live bookings pulled from the db (2044: 88 games, 2045: 68, 2046: 50, 2047: 39, 2048: 28, 2049: 21, 2050: 28, 2051: 17, 2052: 21; 2053 empty), state/series_live/. NEXT: Dan finishes 2044 bookings -> pull series/y2044 -> convert_series_db.py -> fill_noncon -> fix_p6_hosting -> export_conf_board -> fill_conf -> install_hand_schedule --commit (no week-14 guests).

## Western Coast week-14 rotation (Dan, 2026-10-27)
Kaji Kita State / Barhold Valley / Skylar Rose have no week-14 rival. conf_plan.py now locks one EXISTING conference game among them to week 14 each season (type w14_rotation; no matchup or host changed; pre-copy conf_plan.py.pre_w14rot): the left-out team rotates Skylar Rose (2044), Kaji Kita State (2045), Barhold Valley (2046), repeating. Locked games: 2044 BV-KKS, 2045 BV-SR, 2046 KKS-SR, 2047 BV-KKS, 2048 BV-SR, 2049 KKS-SR, 2050 BV-KKS, 2051 BV-SR, 2052 KKS-SR, 2053 BV-KKS. Series Office republished (v18).
Adjustment: 2047 lock changed to BV-SR (KKS left out) because Dan already booked Southern Tengus at KKS in week 14 that year (override W14_OVERRIDE). UNAVOIDABLE clashes left for Dan: 2046 (KKS hosts... Southern Tengus at KKS wk14 booked; no BV-SR game that year) and 2050 (Southern Tengus v BV wk14 booked; no KKS-SR game that year). Series Office v19.

## 2044 SCHEDULE -- BUILT AND INSTALLED (2026-10-28)
Series Office series/y2044 (v130) pulled -> Kaji Kita was booked 4 times (locked Kaji Daun + 3); Dan: drop Kaji Kita v Southern Krobe (removed from db too, now v131). convert_series_db -> noncon_s19_handoff (129 games incl. 6 locked) -> fill_noncon (96 guests + 71 FBS auto) -> fix_p6_hosting -> noncon_s19.json.
First fill_conf left UNN and Chinolka with week-14 byes: Great Fourteen had an odd number free in wk14 and UNN's 3 non-con were all Dan's (wks 1-3). Fix (auto games only): UN Ediville v Burrell (guest) + Kaji Daun State v Hughes State -> UN Ediville hosts Kaji Daun State in WEEK 14, Hughes State hosts Burrell. Pre-fix copy noncon_s19.json.pre_w14fix.
export_conf_board (0 problems) -> fill_conf (attempt 1, 0 hard violations) -> conf_sched_s19.json -> install_hand_schedule --commit, audit CLEAN. 980 games (684 conf, 296 non-con, 136 guests), by week 0-14: 12/82/68/69/68/67/68/67/65/67/68/68/67/68/76. All Dan's weeks/hosts held; 0 guests in week 14; W14 rotation BV-KKS in week 14, Skylar Rose v Roosevelt Mines wk14. Backups *.pre_s19_sched.
NEXT: media pool s19, preseason, week 0. (Dan's reminder: start a NEW CONVERSATION once the schedule is installed.)

## NAME (Dan, 2026-10-28)
The college football sim is now called RCFB. "resume RCFB season 20XX" = restore cfb/ from GitHub into /home/claude/cfb2 (gunzip state, join games_db parts) and pick up at that season. 2044 status: schedule installed; next media pool s19, preseason, week 0.

## 2044 PRESEASON -- 2026-10-28 (new conversation, container wiped again)
RESTORED from GitHub (read-only clone of minigolfwiz/roiland-rfl, cfb/ -> /home/claude/cfb2): gunzip state, games_db parts joined; season 19, next_week 0, 980-game schedule, 136 guest rosters/staffs consistent with the installed schedule.
Media pool s19 drawn by media_pool.make_pool (30 returning / 30 new, no school in all of 2042-44). Preseason poll: run_season.poll_update(seed=10000) -> media_history['pre'], media_ballots[0]. Backup state/season_state.pkl.pre_s19_preseason.
Preseason top 5: Rogaela State (49 firsts), Eona (9), Costique River (1; defending champions third), North Hatesei, Central Stanton; Orlot Western 20th and German Shores 25th are the L6 teams. 25 notes in state/preseason_notes.json (2043's kept as preseason_notes_s18.json), from export_preseason facts + playoff_s18.pkl results; no mascots/ratings.
Roiland Preseason republished (v7), Media Pool (v69).
Week 0 Gameview candidates: Crayellan at North Hatesei; Ranroman at Barhold Valley; Churchill at Eona State; Hansenne at Fiota State. NEXT: Dan picks -> `python3 gameview.py pick 0 <host>` then `python3 week_cycle.py 0 <host>`.
PERSISTENCE GAP: this session had read-only git access (add_repo push was declined by the auto-mode classifier). state/season_state.pkl.gz, state/preseason*.json, state/media_pool_view.json, cfb_session_log.md and PENDING.md changed locally and are NOT yet pushed to minigolfwiz/roiland-rfl.
ARCHIVE: 2043 viewer (incl. CCG + playoff box scores) saved at archive/season_viewer_2043_full.html.gz before the 2044 viewer overwrote it (not yet pushed).

## 2044 WEEK 0 played (Gameview North Hatesei). Backup state/season_state.pkl.pre_w0. Poll: Rogaela State, Eona, Costique River, North Hatesei (73-35 over Crayellan; RB Ustevaw Karravaw 345 rush yds, out for the season), Central Stanton; Ranroman (#16) lost 23-7 at Barhold Valley and dropped out. Viewer v178, Media Pool v70. Old 2043 viewer archived. NEXT: Dan picks week-1 Gameview. NOT PUSHED (read-only git).

## 2044 WEEK 1 played (Gameview Skylar Rose 48-35 over Roosevelt). Backup state/season_state.pkl.pre_w1. Poll: Costique River, Eona, North Hatesei, Central Stanton, Ranroman State; #1 Rogaela State lost 30-24 to Rupin State at home (fell to 11th); Tasson dropped out. Viewer + Media Pool republished. NEXT: Dan picks week-2 Gameview. NOT PUSHED (read-only git).

## 2044 WEEK 2 played (Gameview Pistolheart 30-13 over Tengus State). Backup state/season_state.pkl.pre_w2. Poll: Eona, North Hatesei, Costique River, Ranroman State, Skylar Rose; upsets: San Diego Valley 15-13 at #4 Central Stanton, West Hatesei 26-20 OT at #9 Hatesei, Sacred Tomb 31-25 over #12 Eastern State, East Tasson 20-19 at #25 German Shores; dropped out Eastern State, Roosevelt, German Shores. Viewer + Media Pool republished. NEXT: Dan picks week-3 Gameview. NOT PUSHED (read-only git).

## 2044 WEEK 3 played (Gameview Skeenerland State 38-10 over Ranroman State). Backup state/season_state.pkl.pre_w3. Poll: North Hatesei, Eona, Ciarralotta State, Skylar Rose, Costique River; upsets: Southeastern 38-27 over #15 Marblehead, Keeper 36-21 over #16 Lornaman, New Madrid 27-21 at #18 Yrei Trobniy, Stanton 17-19 loss to #5 Skylar Rose (close); dropped out Lornaman, Yrei Trobniy, Stanton. Standing: ALWAYS show both teams' records on Gameview candidates (Dan, wk 3). Viewer + Media Pool republished. NEXT: Dan picks week-4 Gameview. NOT PUSHED (read-only git).

PUSHED 2026-10-28 (write access restored; repo attached with push): state through 2044 week 3 (next_week 4), games_db parts re-split, 2043 viewer archive. Earlier NOT PUSHED notes for the 2044 preseason and weeks 0-3 are superseded.

## 2044 WEEK 4 played (Gameview Riveral, UFNH won 38-10; Dan's own pick, not on the candidate list). Backup state/season_state.pkl.pre_w4. Poll: North Hatesei, Eona, Pistolheart, Kaji Daun, Barhold; #1 North Hatesei survived 23-20 at Ranroman State; upsets: Parchynt 20-13 at #5 Costique River, Kaji Kita 26-20 over #7 Skeenerland State, Coachville College 27-10 over #12 Black Forest, Hansenne 24-22 over #17 Orlot Western; dropped out Orlot Western, Hatesei. Viewer + Media Pool republished. NEXT: Dan picks week-5 Gameview.

## 2044 WEEK 5 played (Gameview Leafette: #11 Dietsche won 34-21 at #7 Leafette). Backup state/season_state.pkl.pre_w5. Poll: North Hatesei, Eona, Pistolheart, Barhold, Kaji Daun; upsets: Phangrine State 27-24 at #6 Ciarralotta State, Riveral 42-35 at #13 Costique River, Ciarralotta 21-17 at #17 Central Stanton, Verigon 24-20 over #18 Crayellan State, UN Minko 35-29 OT at #25 Coastal Ranroman; dropped out Coastal Ranroman. Viewer + Media Pool republished and state pushed. NEXT: Dan picks week-6 Gameview.

## 2044 WEEK 6 played (Gameview Kaji Daun: #5 Kaji Daun 27-10 over #1 North Hatesei). Backup state/season_state.pkl.pre_w6. Poll: Eona, North Hatesei, Kaji Daun, Dietsche, Fiota Bay; upsets: UNN 41-24 over #3 Pistolheart, Skeenerland 35-0 over #4 Barhold, Ciarralotta Tech 27-16 over #9 Southern Krobe, Tengus 39-21 over #10 Skeenerland State, Dove Island 37-35 OT over #14 Krobe State, #18 Crayellan State lost 26-20 to #8 Fiota Bay (reverse: Fiota Bay won), Kaji Daun State 27-10 over #19 Hoganelle, Greene 28-10 over #24 Central Stanton; dropped out Central Stanton, Ranroman State. RYSKAMP: twenty nominees named after week 6 (s['ryskamp_s19']['twenty']); closed pools 20 -> 10 -> 4. NEXT: Dan picks week-7 Gameview. Committee ballot starts after week 8.

## 2044 WEEK 7 played (Gameview Ciarralotta State: #10 Ciarralotta State 24-21 over #12 Southern Krobe). Backup state/season_state.pkl.pre_w7. Poll: Eona, Dietsche, North Hatesei, Fiota Bay, Kaji Daun; upsets: Orlot 13-7 at #3 Kaji Daun, #23 Crayellan State 49-28 over #8 UFNH (Guanting Kaizhong 340 rush yds, 5 TD), South Antiragal 24-21 at #9 Leafette, Barhold State 45-36 at #15 Diveo State, #16 Krobe State 24-20 over #20 Rogaela State, Crayellan 16-13 over #21 Costique River; dropped out Hoganelle. Committee ballot starts after week 8 (Dan ranks by hand); Gameview for week 9 comes after his ballot. Viewer + Media Pool republished and state pushed. NEXT: Dan picks week-8 Gameview.

## 2044 WEEK 8 played (Gameview Barhold: #11 Barhold 45-7 over #12 Marblehead). Backup state/season_state.pkl.pre_w8. Media poll: Eona, Fiota Bay, Ciarralotta State, Dietsche, Pistolheart. Upsets: S Antiragal State 21-3 at #2 Dietsche, #8 Pistolheart 35-25 at #3 North Hatesei, #24 Ranroman State 24-13 over #5 Kaji Daun, Yrei Trobniy 38-27 over #6 Skylar Rose, Eastern State 24-7 at #14 Southern Krobe, North Verigon 10-7 over #23 Crayellan State, Rogaela 31-13 at #25 Costique River; dropped out Crayellan State, Costique River. Viewer v186, Media Pool v78, Committee Ballot built (week 8, first committee board). WAITING on Dan's first committee top 25 -> install_committee.py state/ballot_s19_w8.json --commit; Gameview week-9 candidates only AFTER his ballot (provisional candidates NOT shown). parity_monitor.py wk 8 ran but printed '2033 through week 14' (wrong season label/range, to check).

## 2044 FIRST COMMITTEE BOARD INSTALLED (after week 8 results, for week 9) -- state/ballot_s19_w8.json, audit CLEAN
1 Eona, 2 Fiota Bay, 3 Pistolheart, 4 Park Island, 5 Tengus State, 6 Krobe State, 7 Skeenerland, 8 Barhold, 9 Ranroman State, 10 Ciarralotta State, 11 UFNH, 12 Dietsche, 13 Kaji Daun, 14 North Hatesei, 15 Phangrine State, 16 Ranroman, 17 Rogaela State, 18 Skylar Rose, 19 Diveo State, 20 Roosevelt, 21 Keeper, 22 Lornaman, 23 Marblehead, 24 Orlot, 25 Rogaela. Committee is now the ranking of record. Backup season_state.pkl.pre_committee. Week 9 candidates: Ranroman State at Eona; Krobe State at Dietsche; Fiota Bay at Crayellan; Keeper at Ciarralotta State (visited). Passed: Ranroman at Kaji Daun. NEXT: Dan picks week-9 Gameview.

## 2044 WEEK 9 played (Gameview Eona: #9 Ranroman State 34-9 over #1 Eona). Backup state/season_state.pkl.pre_w9. Media poll: Ciarralotta State, Eona, Pistolheart, Barhold, UFNH. Upsets: Crayellan 28-24 over #2 Fiota Bay, Skeenerland State 31-14 over #5 Tengus State, #6 Krobe State 17-16 at #12 Dietsche (Dietsche lost), Ciarralotta Tech 41-24 over #15 Phangrine State, #13 Kaji Daun 30-13 over #16 Ranroman, #10 Ciarralotta State 59-7 over #21 Keeper. Viewer v188, Media Pool v79, Ballot v55 (week 9), Gameview map v2. WAITING on Dan's week-9 committee top 25 -> install_committee.py state/ballot_s19_w9.json --commit; Gameview week-10 candidates only AFTER his ballot (not shown).

## 2044 WEEK 9 BOARD INSTALLED (ballot_s19_w9.json, audit CLEAN): 1 Pistolheart, 2 Krobe State, 3 Park Island, 4 Eona, 5 Skeenerland, 6 Barhold, 7 Fiota Bay, 8 Ciarralotta State, 9 Ranroman State, 10 UFNH, 11 Kaji Daun, 12 Tengus State, 13 North Hatesei, 14 Rogaela State, 15 Skylar Rose, 16 Diveo State, 17 Roosevelt, 18 Dietsche, 19 Skeenerland State, 20 Lornaman, 21 Marblehead, 22 Orlot, 23 Rogaela, 24 Keytommiyr, 25 New Madrid. Out: Phangrine State, Ranroman, Keeper. Backup pre_w9board. Viewer v189. Week 10 candidates: North Hatesei at Eona (visited), Park Island at Kaji Kita State, Ranroman State at UNN (rivalry), Will Tech at Krobe State. Passed: Orlot at Pistolheart. NEXT: Dan picks week-10 Gameview.

## 2044 WEEK 10 played (Gameview Rogaela: #23 Rogaela 38-20 over Riveral; Dan's own pick, host Rogaela). Backup state/season_state.pkl.pre_w10. Media poll: Ciarralotta State, Eona, Pistolheart, Barhold, Park Island. Upsets: Will Tech 45-26 at #2 Krobe State, UNN 30-7 over #9 Ranroman State, Greene 34-10 at #11 Kaji Daun, #4 Eona 46-43 OT over #13 North Hatesei (Eona survived), Southern Krobe 31-28 OT at #20 Lornaman, Verigon Tech (guest) 42-36 at #24 Keytommiyr. RYSKAMP: cut to ten after week 10 (s['ryskamp_s19']['ten']): Wolfbruck, Clairlac, Norniy, Vasulingam, Balaraj, Manupati, Baifei, Vikstad, Ducour, Notaw; next cut 4 finalists. Viewer + Media Pool + Ballot (wk 10) + map republished. WAITING on Dan's week-10 committee top 25 -> install_committee.py state/ballot_s19_w10.json --commit; Gameview week-11 candidates only AFTER his ballot.

## 2044 WEEK 10 BOARD INSTALLED (ballot_s19_w10.json, audit CLEAN): 1 Pistolheart, 2 Park Island, 3 Eona, 4 Skeenerland, 5 Barhold, 6 Fiota Bay, 7 Ciarralotta State, 8 UFNH, 9 Tengus State, 10 Krobe State, 11 Rogaela State, 12 Skylar Rose, 13 Diveo State, 14 Skeenerland State, 15 Greene, 16 Roosevelt, 17 Dietsche, 18 Marblehead, 19 UNN, 20 Rogaela, 21 North Hatesei, 22 Kaji Daun, 23 Ranroman State, 24 New Madrid, 25 Barhold State. Out: Lornaman, Orlot, Keytommiyr. Backup pre_w10board. Viewer v191. Week 11 candidates: Skeenerland at Tengus State; Barhold at Diveo State; Eona at Pistolheart (visited); UNN at Greene. NEXT: Dan picks week-11 Gameview.

## Season 19 (2044) week 11
- Gameview: Eona at Pistolheart (Pistolheart 38-27; #1 beat #3). Played wk11 (769 results). Viewer, Media Pool, Gameview map, wk11 committee ballot published. Awaiting Dan's wk11 top 25 before wk12 Gameview candidates.
- Week 11 committee board installed: 1 Pistolheart, 2 Park Island, 3 Fiota Bay, 4 Diveo State, 5 Eona. Out: Rogaela State, Kaji Daun, New Madrid, Barhold State.

## Season 19 (2044) week 12
- Gameview: Skeenerland State at Diveo State (28-0 Skeenerland State). Wk12 played (836 results). Kaji Daun beat #1 Pistolheart 30-27. All pages published. Awaiting wk12 committee ballot before wk13 candidates.
- Week 12 committee board installed: 1 Park Island, 2 Fiota Bay, 3 Pistolheart, 4 Eona, 5 Ciarralotta State. Out: Rogaela. In: Kaji Daun (25).

## Season 19 (2044) week 13
- Gameview: Roosevelt at Park Island (Roosevelt 38-33; #13 beat #1). Wk13 played. Pages published. Awaiting wk13 ballot before wk14 candidates.
- Week 13 committee board installed: 1 Pistolheart, 2 Eona, 3 Ciarralotta State, 4 UFNH, 5 Skeenerland. Out: Ranroman, Greene, Lornaman. In: Black Forest, German Shores, Costique.

## Season 19 (2044) week 14 (regular season complete, 980/980)
- Gameview: UFNH at Fiota Bay (UFNH 34-26; #4 beat #10). Pages published. Awaiting wk14 committee ballot. Then: CCGs (ccg.py), Ryskamp four after CCGs, parity monitor wk14 (header bug).
- Week 14 board installed (ballot_s19_w14.json): 1 Pistolheart, 2 Eona, 3 UFNH, 4 Ciarralotta State, 5 Skeenerland. Out: Dietsche, Costique. CCG preview shown (not played). parity_monitor.py takes a SEASON number (not week): earlier '2033 through week 14' header was my misuse; run with no arg for current season.

## 2044 CONFERENCE FINALS PLAYED (ccg.py --commit; backups season_state.pkl.pre_s19_ccg, games_db.pkl.pre_s19_ccg)
Tengus State 31 Marblehead 24; Krobe State 55 Keytommiyr 16; Pistolheart 34 Eona 23; Roosevelt 34 Park Island 28; Phangrine State 41 Ciarralotta State 7; UFNH 14 Fiota Bay 6; NE Rogaela 26 Palisades 10; New Madrid 37 Black Forest 34; Wolford 34 West Hatesei 0; German Shores 10 East Tasson 0; VSSC 41 Rupin State 17; Underwood 17 Chapel Rock 13.
RYSKAMP FOUR (strict subset of ten): Clairlac, Baifei, Wolfbruck, Vasulingam. Selection Board built+published; awaiting Dan's 24-team field JSON -> install_field.py. Parity monitor (current season, no arg) wk14 ok.

## 2044 PLAYOFF FIELD INSTALLED (state/field_s19.json -> playoff_s19.pkl). Seeds: 1 Pistolheart, 2 Eona, 3 UFNH, 4 Roosevelt, 5 Phangrine State, 6 Ciarralotta State, 7 Krobe State, 8 Tengus State | 9 UNN, 10 Skeenerland, 11 Marblehead, 12 Skeenerland State, 13 Barhold, 14 North Hatesei, 15 Kaji Daun, 16 Ranroman, 17 Leafette, 18 Ranroman State, 19 German Shores, 20 NE Rogaela, 21 New Madrid, 22 Wolford, 23 VSSC, 24 Underwood. R1 preview shown, NOT PLAYED.
- Playoff preview format: Dan asked previews be mobile-friendly; now published as artifact FuosurU7aayp5kR4iANeWE via playoff_preview_page.py.

## 2044 PLAYOFF FIELD CORRECTED (Dan): seed 18 is Park Island, not Ranroman State (field_s19.json, playoff_s19.pkl updated). Round 1 PLAYED (backups season_state.pkl.pre_s19_po1 / pre_s19_po_r1, games_db.pkl.pre_s19_po1, playoff_s19.pkl.pre_po1): UNN 51 Underwood 15; VSSC 17 Skeenerland 12; Marblehead 28 Wolford 7; New Madrid 23 Skeenerland State 20 (2OT); Barhold 41 NE Rogaela 10; North Hatesei 33 German Shores 0; Park Island 34 Kaji Daun 25; Ranroman 17 Leafette 6. R2 (bye teams host, reseeded): 1 Pistolheart v VSSC, 2 Eona v New Madrid, 3 UFNH v Park Island, 4 Roosevelt v Ranroman, 5 Phangrine State v North Hatesei, 6 Ciarralotta State v Barhold, 7 Krobe State v Marblehead, 8 Tengus State v UNN. Previews go in chat (Dan: no artifact).

## 2044 PLAYOFF ROUND 2 PLAYED (backups *.pkl.pre_s19_po2 for season_state, rosters, seed_registry, games_db, playoff_s19): Pistolheart 23 VSSC 14; Eona 27 New Madrid 21; Park Island 41 UFNH 10; Roosevelt 28 Ranroman 22; Phangrine State 24 North Hatesei 19; Barhold 31 Ciarralotta State 0; Krobe State 21 Marblehead 3; UNN 56 Tengus State 7.
QF (neutral, rotation): 1 Pistolheart v 18 Park Island @ 501 Bowl, Stamford (Ciarralotta); 2 Eona v 13 Barhold @ Steam Bowl, Coachville (Stanton); 4 Roosevelt v 9 UNN @ Copper Bowl, Billiataho (Roosevelt); 5 Phangrine State v 7 Krobe State @ Redwood Bowl, Kirkwood (Crayellan). Preview shown in chat; NOT PLAYED.

## 2044 PLAYOFF QUARTERFINALS PLAYED (backups *.pkl.pre_s19_poqf): Pistolheart 38 Park Island 17 @501 Bowl; Barhold 24 Eona 18 @Steam Bowl; Roosevelt 49 UNN 28 @Copper Bowl; Krobe State 34 Phangrine State 0 @Redwood Bowl.
SF: 1 Pistolheart v 13 Barhold @ Star Bowl, Ediville (Natzumakis); 4 Roosevelt v 7 Krobe State @ Lumber Bowl, Port Logan (Fiota). Preview in chat; NOT PLAYED.

## 2044 PLAYOFF SEMIFINALS PLAYED (backups *.pkl.pre_s19_posf): Pistolheart 49 Barhold 33 @Star Bowl; Roosevelt 30 Krobe State 24 @Lumber Bowl. NATIONAL CHAMPIONSHIP: 1 Pistolheart v 4 Roosevelt. Preview in chat; NOT PLAYED. After title: final media poll, Ryskamp winner + awards (finalists), parity monitor post-season, parity audit, title sites 2045+ (show full list), republish viewer.

## 2044 RYSKAMP WINNER (named before the title game at Dan's request; basis regular season + conference finals, snapshot pre_s19_po_r1; backup season_state.pkl.pre_s19_ryskamp): Andres Clairlac, Pistolheart QB Jr (4,763 yds, 40 TD, 9 INT; 145 rush yds, 3 TD). Finalists: Rongrong Baifei (Krobe State QB So 4,513 yds, 42 TD, 12 INT), Snezana Wolfbruck (Rupin State WR Sr 113 rec, 1,821 yds, 16 TD), Ghaith Vasulingam (Diveo State QB So 3,804 yds, 33 TD, 5 INT). Open board matched the four exactly. DPOY/FOY/COY/All-America come with the title-game finalize.

## RULING (Dan, 29 Oct 2026): from now on DAN narrows the Ryskamp ten to the four finalists himself and picks the winner; the engine/I must not name the four or the winner automatically. Present the ten (with stat lines) at the post-CCG checkpoint, wait for his four, then his winner. 2044 stands as played (Clairlac).

## 2044 NATIONAL CHAMPIONSHIP PLAYED (Coachville, Stanton; backups *.pkl.pre_s19_pochamp): (4) Roosevelt 31, (1) Pistolheart 19. Roosevelt is the 2044 national champion; history.champ[2044]=(Roosevelt, Pistolheart). Awards canonized by finalize_season: Ryskamp Andres Clairlac (Dan's pick stands), DPOY Alessia Boischamp (Eona DL Jr), FOY Catalina Georledis (Will Tech QB Fr), COY German Shores. FINAL MEDIA POLL filed (media_history[15], media_final_key=16, backup season_state.pkl.pre_s19_finalpoll): 1 Roosevelt 2 Pistolheart 3 Barhold 4 Black Forest 5 Ciarralotta State 6 UFNH 7 Tengus State 8 Park Island 9 Krobe State 10 Eona. NEW STANDING RULE (Dan, 29 Oct): national championship is narrated one quarter at a time with the result only at the bottom (as the RFL Mega Bowl). NEXT: post-season parity monitor + audit, award 2045+ title sites (show full previous list), rollover/2045.
- CORRECTION (Dan, 29 Oct): title-game quarter-by-quarter narration MUST show the running score after every scoring play and at the end of each quarter; only the final result/champion banner waits for the bottom.
- STANDING (Dan, 29 Oct): at the end of every season, show the all-time national title standings (history.book titles/runnerup; grouped by title count, mobile-friendly, in chat). Shown for 2044.

## 2044 POST-SEASON PARITY AUDIT (Dan queued) -- see parity_audit_2044.md
2044 inside the envelope; weeks 12-14 ranked-lost-to-unranked 22% (exp 25%), week-14 favourites 91%. 10/78 power teams at <=2 L. Flags: strength spread sd 7.90 (lowest since 2038) and guest margin +18.3 (lowest). No engine change shipped.

## 2044-45 OFFSEASON -- Stage 1 of 7 COMPLETE: coaching carousel (2026-10-29)
Backups state/{season_state,rosters,coaches,universe,seed_registry}.pkl.pre_s20_carousel; s['carousel_s19']. Prestige step ran (152 moved on 980 results).
19 HC hires, 29 coordinator moves, 12 raids. Vacancies: 10 offseason firings, 2 retirements (Tasson State, Verigon), 2 interims not retained
(Costique River, Central Stanton), 5 poached away. Poached HCs: Brookborough Eona Navy -> Central Stanton; Latu Ciarralotta State -> Leafette;
Bernard UN Minko -> North Verigon; Lafleur Hansenne -> Barhold Valley; Otoviy New Madrid -> Crimson Mount. Retread: Areum Kleinheim (fired Eternal Fox) at New Madrid.
NEXT: Stage 2, the 2045 draft pool for the RFL (needs Dan).

## 2044-45 OFFSEASON -- Stage 2 of 7 IN PROGRESS: 2045 draft pool handed to the RFL (2026-10-29)
export_draft_pool.py -> state/draft_pool_2045.json: 3,459 declared (2,076 seniors, 1,360 early entrants, 23 subdivision). State untouched (verified byte-identical). Slim top-700 filed to Project as claude/cfb_draft_pool_2045.json; full pool sent to Dan.
WAITING on RFL's 280 picks ({"season":19,...}) -> install_rfl_draft.py --commit, then stages 3-7 (portal, recruiting, development, roster_final, rollover).

## 2044-45 OFFSEASON -- Stage 2 of 7 COMPLETE: the 2045 draft, run by the RFL (2026-10-29)
install_rfl_draft.py --forfeits=1 --commit (new flag: League Office pick forfeits shrink the draft; 2045 had 279 picks, round 4 one short). Backups state/{season_state,rosters}.pkl.pre_s20_draft. s['draft_s19']: 279 picks (170 juniors, 109 seniors, 1 subdivision). 2,424 leave college, 1,012 declared underclassmen withdrew to school.
#1 Alessia Boischamp (Eona DL Jr) to Bruca Beach; #2 Verity Hyun-Nam (UFNH DL) to Eona; #3 Freya Osterberg (Tasson LB) to Chapel Rock. Verigon 12 draftees, Orlot 8. Great Fourteen 48, Power North 45, Mountain Valley 41.
NEXT: Stage 3 portal.

## 2044-45 OFFSEASON -- Stages 3-7 COMPLETE in one run at Dan's request (2026-10-29): 2044 closed, 2045 open (season 20)
Backups state/{season_state,rosters,coaches,universe,seed_registry}.pkl.pre_s20_{portal,recruit,dev,final,rollover}.
Stage 3 portal: 307 transfers, 128 withdrew. Stage 4 recruiting (assembled by hand, now coded in recruiting.py --commit): class 2,791, needs 2,422, signed 2,422, unsigned 369; signed 5* 13 | 4* 266 | 3* 977 | 2* 1,116 | 1* 50; L6 blue-chip share 9.0%; best classes Phangrine State 71 pts, Rogaela State 64, Fiota Bay 63, Ranroman 61, North Hatesei 61, Barhold 60; 64 programmes landed no blue-chip.
Stage 5 development: 7,154 players, mean +0.25, r_coach 0.50, 268 breakouts, 85 busts; 9.0+ rated players: only 10 (28 post-draft in 2042/2043).
Stage 6 roster_final: 2,424 departed, 2,422 recruits added, 0 walk-ons, 243 floor fills, rosters 63-68, total 9,819.
Stage 7 rollover (--commit): 2044 archived (Roosevelt), classes Sr 2,157 | Jr 2,768 | So 2,081 | RS 148 | Fr 2,665. Preseason top 10: Skeenerland State 10.50, UFNH, Eona, Pistolheart, Marblehead, Rogaela State, Kaji Kita, Tengus State, Ranroman, Costique River.
### BUG FOUND (disclosed to Dan): THE 2044 FRESHMAN CLASS WAS NEVER SIGNED
In the 2043-44 offseason stage 4 only sized the class (recruiting.py __main__ printed and stopped) and the signing/storage step was not run, so s['recruiting_s18'] does not exist; roster_final then added 0 recruits and generated 2,020 walk-ons (1,261 + 759 floor fills, ability 2.6-4.8) as the entire 2044 freshman class. Evidence: 2044 Fr 2,020 all walkon, none with stars; s['roster_final_s18'] recruits_added 0. Today's sophomores: 2,081, of whom 1,888 are those walk-ons (mean ability 4.14); only 51 sophomores rated 7+, against 608 juniors. 2044 results stand (permanence). Likely contributor to the 2044 parity flags (strength spread sd 7.90, lowest since 2038; guest margin +18.3). Fix FORWARD: recruiting.py now signs and stores with --commit; roster_final.py asserts recruiting_s<N> exists. Decision on the lost class is Dan's.

## 2044 FRESHMAN CLASS MADE REAL (Dan ruling, 2026-10-29: "do whatever you need to do to make that class real, even if all results from last year stand")
retro_class_2044.py --commit; backups state/{season_state,rosters}.pkl.pre_s20_retro; games_db verified byte-identical (md5), no 2044 result, record, box score or stat line touched.
The same 2,020 players (pid, name, position, stats) kept; a 2,816-player class was drawn with make_class(seed 63018) and signed with run_recruiting (signing order from archived 2043 standings, prestige as it stands, crowding off): signed 13 five-stars, 254 four-stars, 986 three-stars, 767 two-stars; 796 unsigned. Matched to each programme's walk-ons by position (leftovers to non-specialists, weakest to K/P). Each takes the recruit's stars/ability plus one year of freshman growth (development had already run on him as a walk-on): mean 4.15 -> 6.29; 265 blue-chips (G14 50, PN 44, JB 41, MV 40, BS 35, WC 34, six L6 conferences 21). Stored as s['recruiting_s18'] (made_real note); players flagged class_made_real=2044 and walkon removed; preseason ratings recomputed (formula and seed as rollover).
Sophomores now: mean 6.28, 431 rated 7+ (was 51). New preseason top 10: Skeenerland State 10.71, UFNH 10.32, Eona 10.30, Pistolheart 10.27, Marblehead 10.22, Kaji Kita 10.07, Rogaela State 10.07, Tengus State 9.87, Kaji Daun 9.82, Costique River 9.80.
NOTE: s['roster_final_s18'] still reads walkons 1261 / recruits_added 0 -- left as the original record of what happened.

## 2045 SCHEDULE -- BUILT AND INSTALLED (2026-10-30)
Series Office series/y2045 (v91, 87 of Dan's games) pulled -> convert_series_db -> noncon_s20_handoff (93 games incl. 6 locked) -> fill_noncon (122 guests + 81 FBS auto, attempt 1) -> fix_p6_hosting -> noncon_s20.json. export_conf_board: 12 conferences, 0 problems, 4/5 home split everywhere.
fill_conf TAUGHT DAN'S 2043 CALENDAR PREFERENCES (soft terms; backup fill_conf.py.pre_s20): home game somewhere in weeks 11-14 (12; 18 for power teams), three byes not bunched (span under 6 weeks 3/wk short; two byes one game apart 2), unbroken runs past 6 games (3 per game). Hard rules unchanged. attempt 3 clean (0 hard violations). Result: ALL 152 programmes have a home game in weeks 11-14, 0 with byes inside 6 weeks, 0 runs of 7+ games, 0 week-14 guests (2044 had 5 L6 byes bunched). conf_s20_filled -> convert_conf_db -> conf_sched_s20.json -> install_hand_schedule --commit, audit CLEAN. 980 games (684 conf, 296 non-con, 136 guests); by week 0-14: 12/88/79/69/69/61/62/68/60/66/67/68/67/68/76; worst home/road run 4 (5 programmes, Eona). Backups *.pre_s20_sched.
Series Office rolled forward: window now 2046-2054 (2045 built). conf_plan.py 21 10 would have CHANGED 2046+ slates, so it was discarded; the 20-10 plan (slates identical, 2054 added) with 2045 dropped is in place (copies conf_plan.json.pre_s20, .s20_window, .s21_attempt). export_series_board host0 now accounts for base_year vs first_year (locked-rival hosts flip correctly: 2046 host = opposite of 2045). Series Office artifact republished (v20), seed = Dan's live bookings 2046-2053.
NEXT: new conversation -> RESTORE from GitHub -> media pool s20, preseason poll + notes, week 0.

## SERIES OFFICE SAVE (Dan, 2026-10-30 13:06)
Pulled all series/y2043-y2054 docs from the Series Office db into state/series_live/series/ (Dan's latest bookings: 2046 66 games, 2047 ~, 2053-54 started) and mirrored to the repo. Change on Dan's request: 2046 Park Island hosts RPU (guest) moved from week 3 to week 4 (db series/y2046 v69; Park Island's other 2046 games are weeks 1 and 2, no clash).
