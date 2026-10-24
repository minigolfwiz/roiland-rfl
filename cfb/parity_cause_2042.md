# Option four: why did the spread compress? (2042 audit; script parity_cause.py)

=== 1. SPREAD AND PERSISTENCE OF TEAM STRENGTH, ALL SEASONS WITH FBS GAMES ===
season | sd | range | corr with previous season | corr with prestige
2026 | 12.50 | 55.9 | - | 0.71
2027 | 9.10 | 49.0 | 0.74 | 0.71
2028 | 10.13 | 45.8 | 0.66 | 0.63
2029 | 9.39 | 48.8 | 0.60 | 0.55
2030 | 8.51 | 37.0 | 0.56 | 0.52
2031 | 8.88 | 46.7 | 0.60 | 0.60
2032 | 8.55 | 45.0 | 0.61 | 0.63
2033 | 8.75 | 39.9 | 0.65 | 0.66
2034 | 9.23 | 49.1 | 0.70 | 0.66
2035 | 9.63 | 43.5 | 0.63 | 0.68
2036 | 8.90 | 51.4 | 0.64 | 0.73
2037 | 6.45 | 37.0 | 0.61 | 0.72
2038 | 10.96 | 55.4 | 0.65 | 0.83
2039 | 10.53 | 53.1 | 0.75 | 0.83
2040 | 8.87 | 48.7 | 0.68 | 0.82
2041 | 9.45 | 45.2 | 0.59 | 0.75
2042 | 9.27 | 39.3 | 0.69 | 0.78

=== 2. LONG-RUN: <=2-loss teams, top-10 strength and favourite win % ===
season | teams<=2 L (all) | power <=2 L | top10 mean | fav win% overall
2026 | 7 | 6 | 19.7 | 75%
2027 | 6 | 4 | 18.7 | 75%
2028 | 7 | 5 | 18.7 | 74%
2029 | 7 | 6 | 18.3 | 73%
2030 | 3 | 2 | 16.8 | 71%
2031 | 9 | 5 | 19.2 | 75%
2032 | 8 | 6 | 19.0 | 77%
2033 | 9 | 7 | 18.7 | 75%
2034 | 11 | 10 | 21.4 | 77%
2035 | 9 | 7 | 19.6 | 75%
2036 | 9 | 5 | 19.1 | 72%
2037 | 8 | 6 | 13.7 | 73%
2038 | 16 | 10 | 21.4 | 78%
2039 | 10 | 8 | 20.2 | 75%
2040 | 12 | 7 | 17.8 | 76%
2041 | 10 | 7 | 17.4 | 78%
2042 | 7 | 5 | 17.8 | 74%

=== 3. OFFSEASON MECHANISMS (classes after seasons 10-16) ===
--- recruiting: class strength vs prestige, and where the stars go ---
class | corr(class avg ability, prestige) | corr(class avg ability, last season's strength) | share of 5-star signees to top-25 prestige | share of 4-5 star | avg class size top25p vs rest
2036 | 0.68 | 0.76 | 10/13 (77%) | 39% | 17.2 vs 18.7
2037 | 0.40 | 0.42 | 12/13 (92%) | 43% | 10.6 vs 11.9
2038 | 0.46 | 0.35 | 12/13 (92%) | 42% | 16.2 vs 17.4
2039 | 0.81 | 0.77 | 12/13 (92%) | 43% | 14.4 vs 17.4
2040 | 0.74 | 0.62 | 12/13 (92%) | 45% | 12.6 vs 13.1
2041 | 0.72 | 0.75 | 12/13 (92%) | 44% | 15.1 vs 13.8
2042 | 0.74 | 0.67 | 12/13 (92%) | 46% | 15.1 vs 14.5
--- draft: picks taken from each team ---
draft after | picks | share from top-25 by last-season strength | corr(picks, last-season strength)
2035 | 210 | 37% | 0.54
2036 | 210 | 39% | 0.55
2037 | 210 | 31% | 0.48
2038 | 210 | 32% | 0.56
2039 | 210 | 38% | 0.59
2040 | 280 | 40% | 0.58
2041 | 280 | 34% | 0.60
--- development: average yearly progress by team vs strength ---
2035 | mean 0.224 | corr(team progress, strength that season) 0.37 | corr(team progress, prestige) 0.48 | sd of team means 0.050
2036 | mean 0.228 | corr(team progress, strength that season) 0.31 | corr(team progress, prestige) 0.40 | sd of team means 0.039
2037 | mean 0.199 | corr(team progress, strength that season) -0.05 | corr(team progress, prestige) 0.08 | sd of team means 0.044
2038 | mean 0.287 | corr(team progress, strength that season) 0.52 | corr(team progress, prestige) 0.57 | sd of team means 0.058
2039 | mean 0.279 | corr(team progress, strength that season) 0.27 | corr(team progress, prestige) 0.26 | sd of team means 0.052
2040 | mean 0.252 | corr(team progress, strength that season) 0.31 | corr(team progress, prestige) 0.45 | sd of team means 0.051
2041 | mean 0.265 | corr(team progress, strength that season) 0.33 | corr(team progress, prestige) 0.48 | sd of team means 0.059
--- portal: net flow of value toward strong teams ---
2035 | transfers 329 | corr(net value, strength) 0.56 | corr(net value, prestige) 0.65
2036 | transfers 319 | corr(net value, strength) 0.44 | corr(net value, prestige) 0.57
2037 | transfers 265 | corr(net value, strength) 0.43 | corr(net value, prestige) 0.60
2038 | transfers 302 | corr(net value, strength) 0.52 | corr(net value, prestige) 0.62
2039 | transfers 325 | corr(net value, strength) 0.43 | corr(net value, prestige) 0.51
2040 | transfers 271 | corr(net value, strength) 0.47 | corr(net value, prestige) 0.59
2041 | transfers 290 | corr(net value, strength) 0.32 | corr(net value, prestige) 0.47

=== 4. ELITE RECORDS vs the 2038 restart's projection (top-5 mean losses 1.08, top-15 1.88, top-10 roster wins 70.8%, undefeated 0.83/season) ===
season | undefeated FBS | top-5 by strength: mean L | top-15 mean L | top-10 win% vs FBS
2038 | 0 | 2.80 | 3.07 | 74.2%
2039 | 1 | 3.40 | 3.27 | 75.8%
2040 | 1 | 1.80 | 2.40 | 82.5%
2041 | 0 | 1.60 | 2.53 | 79.2%
2042 | 0 | 2.20 | 2.80 | 79.2%

=== 5. DOES TALENT STILL FOLLOW PRESTIGE? (rosters now, after the 2042 season) ===
corr(roster talent, prestige) now: 0.944  (2038 restart regenerated at 0.951)
roster talent sd 0.470 range 1.87
corr(2042 season strength, roster talent now) 0.80 ; (2042 strength, prestige) 0.78
