# Roiland CFB - Season 1 Offseason Implementation List

## 1. QB rushing (user-approved, implement in S1->S2 offseason)
Current state: QBs take ZERO rushing attempts. The designed-run path in run_play()
gates on attrs["mob"] > 6, but players carry no attrs dict (fallback mob=3), so the
branch is dead code. Sacks are tracked separately and two-point runs use RBs only.

Implementation plan:
- Add a real "mob" (mobility) rating to QBs at generation/recruiting, keyed to archetype:
  Dual-Threat high (7-9.5), Gunslinger/Game Manager mid (3-6), Pocket Passer low (1.5-4.5)
- Designed QB runs + scrambles: frequency and yardage scale with mob
  (dual threats ~8-14 carries/gm, pocket passers ~1-3 kneel/scramble)
- Sack-avoidance and scramble YAC switch from abil-fallback to true mob
- Backfill mob for all existing QBs from archetype + rng (seeded), so returning QBs
  gain believable mobility profiles
- Recalibrate with validation seasons: QB rush leaders target ~800-1,400 yds
  (dual-threat stars), overall rushing leaders still RB-dominated, scoring ~50-52,
  passing calibration unaffected

## Notes
- L6/P6 talent gap: user decided to LEAVE AS-IS for now (revisit later if desired)
- Names: gen_surname stem==suffix guard already live

## S2 END-OF-SEASON REVIEW (user-requested reminder)
- QB mobility engine is LIVE and accepted. Dual-threats now rush ~800-1,100 yds
  (leaders), RBs still lead overall rushing (1,300-1,600). BUT designed runs/scrambles
  replaced pass attempts: top passer fell ~4,300 -> ~3,800, scoring ~50 -> ~46.5.
  User accepted the run-heavier meta for now. **REMIND USER at end of Season 2** to
  review whether to nudge run/pass balance back toward the old passing baseline.

## SCHEDULER: FUTURE-SEASON RULE (user directive)
Season 2 schedule (seed 770005) kept despite two SOFT misses: worst H/A run = 6
(2 teams >=5) and 1 back-to-back bye. This was a one-time acceptance because the
strict 4/5 conf-home rule conflicted with run-length under time constraints.
FROM SEASON 3 ONWARD: all scheduling rules must hold together again — worst H/A
run <= 2, zero back-to-back byes, AND conf-home exactly 4/5. Likely needs a
conf-home-NEUTRAL run reducer (paired venue swaps) done correctly, or a CP/ILP solve.

## FEATURE REQUEST (user, mid-S2): implement PENALTIES
The engine currently models no penalties (no flags, no yardage/replay-down effects).
[DONE mid-review] Penalty system built: false starts, holding,
pass interference, personal fouls, offsides, etc., with realistic rates and
appropriate down/distance/spot effects, and box-score penalty totals.

## RIVALRY LOCK ADDED (user, S2): Hatesei vs North Hatesei
Added to fixed_pairs as a Week 14 (Rivalry Week) CONFERENCE game (both in Great Fourteen).
One of the sport's biggest rivalries. Now 41 total locked pairs. Applies to Season 3+
schedules (S2 already played without it). The scheduler freezes all locked pairs in place.

## S3 TITLE SITE (user): National Championship will be in Fiota Bay, Fiota.
Set championship=("Fiota Bay","Fiota") when building the Season 3 playoff bracket.

## STANDING SCHEDULE RULE (Dan, 2042 week 7): NO GUEST (subdivision) GAMES IN WEEK 14. Enforced in install_hand_schedule.audit from 2043 on. The 2042 schedule (already built, 12 week-14 guest games) was NOT changed.

## AFTER 2042 SEASON: PARITY AUDIT (Dan, wk 14) -- see cfb_session_log.md

## QUEUED (Dan, 2042 week 14): AUDIT PARITY AGAIN AFTER THE 2042 SEASON
Dan's concerns: (1) far more losses by good teams again (upset rate among top teams too high); (2) only ONE 2-loss power team all season looks suspect (loss-count distribution too flat / too few teams near the top of the win column).
Scope when run: final records by tier/"power" conferences; distribution of losses for the committee top 25 and for the preseason media top 25; upset rate by rating gap (favourite win % at each gap) vs earlier seasons; count of teams at <=2 losses by tier vs 2038-2041; guest-game results for sanity (2042 guests finished 18-118). Existing tools: parity_test.py, parity_ab.py, calib_*.py. Compare against prior-year audits before touching any engine knob; changes apply forward only.
- Neutral-site rule: bowls by SCHOOL distance (campus to bowl city), not state distance (committee.vdist, 2042).
- Neutral-site rule: higher seed skips bowls in the opponent's own state (committee._opp_home, 2042).
- Awarding 2045+ title sites: avoid that year's semifinal cities (committee.semi_title_overlap).
- REMIND DAN after the 2042 season: award title sites for 2045-2049 (five-year block). Show him the FULL LIST of previous title sites (2026-2044) when asking. Avoid that year's semifinal cities (committee.semi_title_overlap).
