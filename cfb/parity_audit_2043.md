# 2043 post-season parity audit (scripts: parity_monitor.py; parity_audit.py/parity_audit3.py with SEAS extended to 18)
Verdict: 2043 sits inside the 2038-42 envelope everywhere except weeks 12-14 (and week 14 generally). No engine knob changed.
- Losses: 2 teams <=1 L, 9 with 2 L (6 power) -- the 2042 worry (only 2 two-loss power teams) did NOT repeat: 7/78 power teams at <=2 L vs 5 in 2042. 1 unbeaten (Orlot Western, L6).
- Final board top 25 mean losses 2.88 (2042 2.96; 2040-41 2.56-2.76). Preseason top 25 4.12 (ref 3.96-4.24).
- Favourite win rate by gap: 51/61/71/89/98%; overall 68.5% (2038-42: 69-73%). Mid-gap 7-14 at 71% is just below the 73-80 range.
- Spread (sd 8.90, range 43.5) is in line with 2040-42. Guests: FBS 121-15, mean margin +21.9.
- Ranked lost to unranked: wks1-7 27% (exp 26), wks8-11 26% (exp 27), wks12-14 40% (exp 26) -- the only flag. 2040-43 weeks 12-14: 34/33/50/40%.
- Week 14 favourites (gap>=7): 23/33 = 70% vs 80% weeks 0-13. Trend 89,91,79,77,73,70 since 2038. Rivalry games at gap>=7: 14/20 = 70% vs 80% other (RIVALRY_GAP 0.70 shipped in 2043 did not visibly lift it; n=20). Week 14 is 34 rivalry games of ~76 each year, so the two effects overlap.
Open for Dan: week 14 is the persistent soft spot (since 2040). Options: leave; raise RIVALRY_GAP step-wise (0.85 gave 0.702 in 2042 sweep); or test a week-14-specific cause (rotation/fatigue/injury load) before touching anything.
