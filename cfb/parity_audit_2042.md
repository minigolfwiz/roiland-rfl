# 2042 post-season parity audit (scripts: parity_audit.py, parity_audit2.py, parity_audit3.py)

=== 1. TEAMS BY REGULAR-SEASON LOSSES (FBS, weeks 0-14) ===
season | teams | <=1 L | 2 L | <=2 L (power) | <=2 L (non-power) | 0 L | unbeaten power
2038 | 152 | 6 | 10 | 10/78 | 6/74 | 0 | 0
2039 | 152 | 2 | 8 | 8/78 | 2/74 | 1 | 0
2040 | 152 | 5 | 7 | 7/78 | 5/74 | 1 | 0
2041 | 152 | 5 | 5 | 7/78 | 3/74 | 0 | 0
2042 | 152 | 4 | 3 | 5/78 | 2/74 | 0 | 0

  exactly-2-loss POWER teams by season: {2038: 7, 2039: 7, 2040: 4, 2041: 3, 2042: 2}

=== 2. LOSSES OF THE TOP 25 ===
(a) preseason media top 25: regular-season losses  | (b) final regular-season board (after wk14), losses
2038 pre: ({}, None) | final board: ({}, None)
2039 pre: ({}, None) | final board: ({}, None)
2040 pre: ({0: 1, 1: 3, 2: 1, 3: 5, 4: 3, 5: 4, 6: 4, 7: 3, 9: 1}, 4.24) | final board: ({0: 1, 1: 4, 2: 4, 3: 12, 4: 4}, 2.56)
2041 pre: ({1: 2, 2: 3, 3: 6, 4: 6, 5: 2, 6: 4, 7: 1, 8: 1}, 3.96) | final board: ({1: 5, 2: 4, 3: 8, 4: 8}, 2.76)
2042 pre: ({1: 2, 2: 1, 3: 4, 4: 9, 5: 6, 6: 1, 7: 2}, 4.08) | final board: ({1: 4, 2: 2, 3: 11, 4: 7, 5: 1}, 2.96)

=== 3. RANKED TEAMS LOSING TO UNRANKED FBS TEAMS, BY WEEK BLOCK ===
season | wks1-7: ranked losses to unranked / ranked games vs unranked | wks8-11 | wks12-14
2038 | 0/0 (0.0%) | 0/0 (0.0%) | 0/0 (0.0%)
2039 | 0/0 (0.0%) | 0/0 (0.0%) | 0/0 (0.0%)
2040 | 27/91 (29.7%) | 16/51 (31.4%) | 16/47 (34.0%)
2041 | 30/93 (32.3%) | 24/58 (41.4%) | 14/43 (32.6%)
2042 | 31/88 (35.2%) | 17/52 (32.7%) | 20/40 (50.0%)

=== 4. FAVOURITE WIN RATE BY RATING GAP (FBS v FBS, season-end power ratings, HFA removed) ===
season | gap 0-3 | gap 3-7 | gap 7-14 | gap 14-21 | gap 21-+ | overall fav win%
2038 | 55% (n=185) | 64% (n=222) | 78% (n=237) | 93% (n=133) | 96% (n=67) | 72.9%
2039 | 51% (n=179) | 57% (n=226) | 80% (n=257) | 90% (n=124) | 93% (n=58) | 70.0%
2040 | 54% (n=190) | 68% (n=204) | 73% (n=282) | 89% (n=124) | 98% (n=44) | 70.9%
2041 | 51% (n=179) | 69% (n=204) | 76% (n=271) | 87% (n=139) | 98% (n=51) | 72.2%
2042 | 52% (n=194) | 62% (n=218) | 74% (n=256) | 87% (n=127) | 92% (n=49) | 69.1%

=== 5. SPREAD OF TEAM STRENGTH (std dev of season-end power rating) ===
2038 sd 10.96 | top10 mean 21.4 | bottom10 mean -18.8 | range 55.4
2039 sd 10.53 | top10 mean 20.2 | bottom10 mean -20.9 | range 53.1
2040 sd 8.87 | top10 mean 17.8 | bottom10 mean -15.9 | range 48.7
2041 sd 9.45 | top10 mean 17.4 | bottom10 mean -18.2 | range 45.2
2042 sd 9.27 | top10 mean 17.8 | bottom10 mean -15.1 | range 39.3

=== 6. GUEST (SUBDIVISION) GAMES: FBS RECORD vs GUESTS ===
2038 FBS 125-11 vs guests | mean margin +28.2
2039 FBS 130-6 vs guests | mean margin +24.9
2040 FBS 120-16 vs guests | mean margin +20.0
2041 FBS 126-10 vs guests | mean margin +21.1
2042 FBS 118-18 vs guests | mean margin +20.1

2042 ranked lost 20 of 40 (50%) | model expected 13.1 (33%) | road games 22, lost 11 | mean rating gap in favour of ranked side +8.1 | avg true rating-rank of the wk12 board 21

=== B. 2042 weeks 12-14: every ranked loss to an unranked team ===
wk12 #5 Diveo State (rating rank 13) lost 9-34 at Barhold (rating rank 18)
wk12 #1 Park Island (rating rank 1) lost 35-38 to Barhold Valley (rating rank 39)
wk12 #9 Southern Tengus (rating rank 5) lost 0-14 at Tengus State (rating rank 33)
wk12 #22 UN Steelbridge (rating rank 60) lost 7-28 to Wolford (rating rank 106)
wk13 #17 Rogaela (rating rank 47) lost 7-27 at Costique River (rating rank 44)
wk13 #5 Fiota Bay (rating rank 14) lost 31-41 at Crayellan State (rating rank 32)
wk13 #8 Diveo State (rating rank 13) lost 29-40 to Tengus State (rating rank 33)
wk13 #24 Krobe State (rating rank 9) lost 21-31 to Dove Island (rating rank 51)
wk13 #13 Skeenerland State (rating rank 22) lost 8-14 at Marblehead (rating rank 40)
wk13 #23 North Verigon (rating rank 43) lost 14-21 at Parchynt (rating rank 29)
wk13 #2 UFNH (rating rank 23) lost 24-25 to Crayellan (rating rank 34)
wk13 #15 Stanton (rating rank 6) lost 6-17 at UNN (rating rank 3)
wk14 #15 UNN (rating rank 3) lost 20-28 at Central Stanton (rating rank 12)
wk14 #17 Ciarralotta State (rating rank 21) lost 20-31 at Ciarralotta Tech (rating rank 75) [rivalry]
wk14 #19 Marblehead (rating rank 40) lost 14-38 at Costique (rating rank 46) [rivalry]
wk14 #25 Dove Island (rating rank 51) lost 7-41 to Will Tech (rating rank 36) [rivalry]
wk14 #9 Eastern State (rating rank 15) lost 17-27 to Keeper (rating rank 37) [rivalry]
wk14 #4 Hatesei (rating rank 17) lost 6-23 to North Hatesei (rating rank 30) [rivalry]
wk14 #7 Diamond City (rating rank 20) lost 31-33 at Phangrine State (rating rank 35) [rivalry]
wk14 #23 Skeenerland State (rating rank 22) lost 17-27 to Skeenerland (rating rank 49) [rivalry]

=== C. 2-loss power teams 2042 and the <=1 loss teams ===
Dietsche 11-1 power P6
Park Island 11-1 power P6
Black Forest 11-1 non-power L6
Tasson 11-1 power P6
Hoganelle 10-2 non-power L6
Ranroman State 10-2 power P6
Diveo State 10-2 power P6

=== D. LARGEST UPSETS BY RATING GAP (gap 21+, favourite lost), 2042 ===
wk2 favourite Barhold Valley (rk 39) lost 17-20 to Hofferteltra (rk 135), gap 21
wk4 favourite Marblehead (rk 40) lost 16-24 to Tengus (rk 133), gap 21
wk5 favourite Southern Tengus (rk 5) lost 24-29 to Barhold State (rk 98), gap 24
wk9 favourite Central Stanton (rk 12) lost 3-17 to Larksdale (rk 131), gap 21

=== E. RIVALRY vs NON-RIVALRY: favourite win % (season-end ratings, FBS v FBS) ===
2038 gap>=7: rivalry fav wins 14/16 (88%) | other 358/421 (85%)
2039 gap>=7: rivalry fav wins 15/18 (83%) | other 356/421 (85%)
2040 gap>=7: rivalry fav wins 15/22 (68%) | other 343/428 (80%)
2041 gap>=7: rivalry fav wins 17/24 (71%) | other 359/437 (82%)
2042 gap>=7: rivalry fav wins 17/23 (74%) | other 329/409 (80%)

=== F. WEEK 14 vs OTHER WEEKS: favourite win % at gap>=7 ===
2038 wk14 32/36 (89%) | wk0-13 340/401 (85%)
2039 wk14 31/34 (91%) | wk0-13 340/405 (84%)
2040 wk14 33/42 (79%) | wk0-13 325/408 (80%)
2041 wk14 33/43 (77%) | wk0-13 343/418 (82%)
2042 wk14 24/33 (73%) | wk0-13 322/399 (81%)

=== G. WEEK 14: how many games were rivalry games, by season ===
2038 wk14 FBS games 76 rivalry 34
2039 wk14 FBS games 73 rivalry 34
2040 wk14 FBS games 72 rivalry 34
2041 wk14 FBS games 71 rivalry 34
2042 wk14 FBS games 70 rivalry 34

=== H. 2042 weeks 12-14 ranked-vs-unranked upsets: share that were rivalry games ===
2040 ranked-v-unranked games 47 (rivalry 14); ranked losses 16 (rivalry 6) | loss% rivalry 43% vs other 30%
2041 ranked-v-unranked games 43 (rivalry 14); ranked losses 14 (rivalry 5) | loss% rivalry 36% vs other 31%
2042 ranked-v-unranked games 40 (rivalry 12); ranked losses 20 (rivalry 7) | loss% rivalry 58% vs other 46%
