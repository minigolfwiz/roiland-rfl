# ROILAND CFB — PROJECT HANDOFF DOCUMENT
*Paste this into a new conversation to resume exactly where we are. Last updated: end of the Season 2→3 offseason, with Season 3 fully set up and ready to simulate Week 1.*

---

## 0. HOW TO USE THIS DOCUMENT (read first)

This is a **fictional college football simulation** called **Roiland CFB**. You (Claude) are helping the user run it. The project's real state lives in two places:

1. **Code + data on disk** at `/home/claude/cfb2/` — the sim engines and all binary state (rosters, game database, history). **This document cannot regenerate that binary state** (10,207 players, full play-by-play engine, game DB). Those files persist on disk between sessions in this project. If they are ever missing, this document lets you understand the design and canon, but the rosters/games would have to be rebuilt.
2. **This document** — captures the narrative, canon rules, engine designs, calibrations, file map, and standing preferences so a fresh instance can continue seamlessly.

**On first resuming:** run a quick state check (`season.load_state()`, confirm `season==3`, `next_week==1`) and read the relevant `.py` files before making changes. Don't trust memory over the live files.

---

## 1. CURRENT STATE (the checkpoint)

- **We are at: Season 3 (year 2028), Week 1, ready to simulate.** All records 0-0, stats empty, rosters finalized, schedule built. Pristine checkpoint.
- **Seasons 1 (2026) and 2 (2027) are complete and canonized.**
- The entire Season 2→3 offseason pipeline is done (draft, carousel, recruiting, portal, development, roster finalization, rollover, schedule).
- The engine just received a large feature batch (special teams, weather, schemes, momentum, 4th-down analytics, kicker quality, onside kicks) plus penalties and coach ages — all live for Season 3, all debugged (17/17 checks pass, 1000-game stress test clean).

**Immediate next action available:** simulate Season 3 Week 1 (e.g. `run_window.run(1)` or `season.simulate_window(n)`).

---

## 2. THE PERMANENCE RULE (most important canon rule)

**All simulated results are immutable canon. Engine fixes apply FORWARD only.** If a bug is found after games were simulated, those games stand as-is; the fix affects future games. The user audits raw output carefully and expects **honest, proactive bug disclosure**. When something looks off, explain it rather than hiding it. Never silently rewrite past results.

---

## 3. UNIVERSE STRUCTURE

- **152 teams**, **12 conferences** (6 "Power" tier = P6, 6 "Lower" tier = L6). The P6/L6 talent gap is **intentionally wide** and should NOT be narrowed.
- **10,207 players**, **~456 coaches** (HC/OC/DC per team).
- **Shared geography with RCBA** (the user's basketball sim): same fictional states (Dove Island, Fiota, Krobe, Ciarralotta, Barhold, Antiragal, Hatesei, Ranroman, etc.).

### Conference tiers (U["tiers"]):
- **P6:** Power North, Jyras Bay, Great Fourteen, Western Coast, Broad South, Mountain Valley
- **L6:** Vapor Stream, Low Sixteen, Brass Belt, East Forest, Evening Star, Southwestern

### Season/year mapping:
- **Year = 2025 + season.** S1 = 2026, S2 = 2027, S3 = 2028. (This formula is used consistently for champions AND awards — do not use 2026+season.)

---

## 4. CANON / HISTORY

### Champions:
- **2026 (S1):** Tengus State (def. Barhold Valley 34-28). S1 POY (then called Heisman): Moussa Gyasi (Barhold Valley).
- **2027 (S2):** Diamond City (def. Ranroman 56-10; Wei Hanwen 4 rush TD). Diamond City's FIRST-EVER title. Ranroman now 3× runner-up (1980/2002/2027), a 44-year drought.
- Full **1936–2025 history** is canonized (four eras: bowls 1936-78, title-game 79-2015, 8-team playoff 2016-25, 24-team playoff 2026-). **North Hatesei = greatest dynasty (9 titles).**

### The Ryskamp Trophy (award rename):
- From **2027 onward**, the Player-of-the-Year award is called **"The Ryskamp Trophy"** (was "Heisman"). Internal data key stays `heisman`; `committee.py` has an `AWARD_NAMES` dict. The 2026 award is recorded as "Heisman" in the ledger with a note.
- **2027 winners (canon):** Ryskamp = Bozena Krupka (Kaji Daun QB); DPOY = Alphonse Braunbrunner (Ranroman DL); Freshman of Year = Dobromir Georkoulis (Greene QB); Coach of Year = Diamond City.

### Naming canon (user-confirmed, precise):
- **"St" always means "State."**
- **"S Antiragal State"** is the canonical short form (of South Antiragal State).
- **Barhold, Barhold State, and Barhold Valley are three DISTINCT programs.** Same for other families.
- **"Koli Ro Shuriken"** is the correct full name (not "Ro Shuriken").
- A school whose name contains a state name must be located in that state.

### Rivalries:
- **41 locked rivalry pairs** in `U["fixed_pairs"]`, each pinned to a specific week. Includes the **Hatesei vs North Hatesei** game (Week 14, a Great Fourteen conference game, added in the S2→S3 cycle).

### Auto-canonization:
- `committee.finalize_season(state, playoff, save_fn)` records champion, runner-up, semifinalists, all playoff participants, AND the awards slate into `history` automatically at season end. **Idempotent** (safe to call repeatedly). Wire this into future title-game runs so the user never has to manually "lock in" a season.

---

## 5. THE SIM ENGINE (files at /home/claude/cfb2/)

### Core files:
- **`pbp_engine.py`** — the play-by-play simulation engine. `simulate_game(home, away, seed, ...)` returns `(box, pbp)`. Deterministic per seed. Contains the `TeamGame` class (unit accessors: `ols`, `dls`, `lbs`, `cbs`, `ss`, `wrs`, `tes`, `rbs`, `qbs`, `k`, `p`), the `drive()` loop, all scoring/turnover/special-teams logic.
- **`season.py`** — state management. `load_state()`, `save_state()`, `simulate_window(n_weeks)`, `merge_stats()`, records/heat/HFA/hot-seats/firings/NET rankings/win probability. State file: `state/season_state.pkl`.
- **`penalties.py`** — full real-CFB penalty set (see §6).
- **`special_teams.py`** — punts w/ returns, kickoff returns, onside kicks, blocks, muffs, fakes, 4th-down analytics, FG blocks (see §6).
- **`committee.py`** — playoff selection committee (12 personas, chair Marguerite Okonkwo-Hale), awards computation, `finalize_season()`.
- **`ccg.py`** — conference championship games (season-aware).
- **`playoff.py`** — 24-team playoff bracket (season-aware).
- **`scheduler_s2.py`** — the S3 scheduler (annealing-based `_run_reduce_neutral`, `build_schedule()`). `scheduler.py` is older.
- **`draft.py`** — NFL-style draft (`run_draft(seed)`). Uses `state/subdivision_schools.json` for small-school draftees.
- **`carousel.py`** — coaching carousel (`run_carousel(seed)`): firings, retirements (age-based), HC poaching, coordinator cascades.
- **`recruiting.py`** — recruiting class generation + signing (`make_class`, `run_recruiting`).
- **`offseason.py`** — OLD monolithic pipeline (draft→transfers→recruiting→dev→rollover). **NOT used this cycle** — we run stages standalone now. Portal logic lives inside it (extracted manually).
- **`media_poll.py`** — AP-style media poll.
- **`webapp.py`** → builds `roiland.html` (~7MB, season-aware) to `/mnt/user-data/outputs/`. `build_site()`.
- **`run_window.py`** — `run(n_weeks)`: simulate a window + rebuild the website.
- **`games_db.py`** — game database (`load_db`, `save_db`). Games keyed like `S3W01_...`.
- **`names_v2.py`** — name generator (`pick_name_v2`).
- **`universe.py`** — builds the universe (teams, conferences, prestige, geo).

### State files (state/*.pkl, *.json):
`season_state.pkl` (main state), `universe.pkl` (teams/conferences/prestige/geo/tiers/scheme-tables/fixed_pairs), `coaches.pkl`, `rosters.pkl`, `games_db.pkl`, `playoff_s1.pkl`, `playoff_s2.pkl`, `conf_champs_s1/s2.pkl`, `committee_panel.pkl`, `subdivision_schools.json` (220 RCBA-sourced small-school names), `schedule_s1/s2.pkl`, `schedule_s3_cache.pkl`, `seed_registry.pkl`, `gen_seed.pkl`.

### Determinism & seeds:
- Every game is deterministic given its seed. `E.game_seed(n)` / `assign_seed` produce stable seeds. Weather is derived per-seed (`seed ^ 0x5EED`) so it's reproducible.

### Data quirks to know:
- **Player pids are MIXED str and int.** S2 freshmen have `S2F_...` string pids, S3 freshmen `S3F_...`, walk-ons `S3W_...`, older players int pids. When computing `max(pid)`, filter to ints only.
- Rosters are `E.ROSTERS` (dict team→list of player dicts). Player dict keys: `pid, name, team, pos, cls, arch, abil, dur, rep, inj_hist, mob, attrs, discipline` (+ `freshman`/`walkon`/`_transferred_from` flags).

---

## 6. ENGINE FEATURES & CALIBRATIONS (what each system does)

### Penalties (`penalties.py`)
- Full real-CFB set: false start, offside, encroachment, delay of game, illegal formation/shift/substitution (pre-snap); offensive/defensive holding, offensive/defensive PI, roughing the passer, personal foul, face mask, block in the back, illegal block, targeting w/ ejection (live).
- **Rate: ~13.5/game (~6.7/team), ~53 penalty yards/team.** Realistic distribution (holding + false starts most common).
- **Per-player `discipline` trait** (0.45–1.9, position-weighted: OL/DL/DBs higher, K/QB lower) and **per-team `team_discipline`** (0.8–1.25, derived from coach skill). Correlation team-discipline↔penalties ≈ +0.55–0.82.
- **Excessive penalties reduce workload:** a player with 2+ penalties in a game gets benched more (strict coaches yank faster via `bench_tendency`; star/generational players get a longer leash). Box carries `penalties` (per-team n/yds) and `penalty_log`.

### Special teams (`special_teams.py`)
- **Punts:** real net (leg-driven), weather-dampened, live returns, fair catches. Rates: punt-return TD ~0.03/game, blocked punt ~0.05/g, muffed punt ~0.07/g.
- **Kickoff returns:** touchbacks + returns, kickoff-return TD ~0.03/g.
- **Onside kicks:** auto when trailing late after scoring; ~22% desperation recovery, ~13% surprise.
- **Fake punts/FGs:** ~0.02/g, coach-aggression driven.
- **Blocked FGs:** rises with distance.
- **Kicker/punter quality:** all 528 specialists have distinct `leg` + `accy` attrs (variety: big-leg-inaccurate vs accurate-short-leg). Affects punt distance, FG range, touchbacks.
- **4th-down analytics (`fourth_down_decision`):** situational go/punt/FG by field zone, distance, score, time, coach aggression. Distribution ~54% punt / 29% FG / 16% go. Replaced old hardcoded logic.

### Weather
- Per-seed: 60% clear / 19% windy / 13% rain / 9% cold-snow. Domes always clear.
- Bad weather → run-heavier play-calling (~9-point pass-rate drop in rain/snow) + dampened kicking. Box carries `weather` label.

### Coaching schemes
- **Offensive (`U["OFF_SCHEMES"]`):** Air Raid (~70% pass), Spread, Pro-Style, Pistol, Ground-and-Pound (~36% pass), Option. Stored per-team on `COACHES[t]["off_scheme"]`.
- **Defensive (`U["DEF_SCHEMES"]`):** 4-3 Base, 3-4 Multiple, Aggressive Blitz, Bend-Don't-Break, Cover-Heavy. On `COACHES[t]["def_scheme"]`.
- Dramatic realistic effect on pass/run balance. Box carries both teams' schemes.

### Momentum
- Light effect: nudges play-calling slightly toward a team's identity when they're rolling (user chose "shift win probability a little, mostly narrative"). `add_momentum()` fires from big plays (return TDs, blocks, missed FGs). Box carries `final_momentum`.

### Other engine mechanics (pre-existing, all live):
- **Safeties** (~0.03/g, sacks primary cause), **OT walk-off** (2nd OT team scoring go-ahead TD ends game, no conversion), **pick-6s** (~6% of INTs, via "house call" mechanic), **defensive attention** / usage-efficiency tradeoff (soft cap ~32-33% share), **generational talent exception** (P99+), **per-player form rolls**, **fatigue**, **garbage-time subs**, **reputation-driven role feedback**, **dynamic injury system**, **clutch logging** (final 5:00 + OT for close games), **dynamic HFA** (heat-based).

### Coach ages & retirement (`carousel.py`)
- Every coach has an `age` and personal `retire_age` (target ~58-73, most 65-68). Retirement probability ramps as they approach/pass target (6+ yrs out: 0.5%; at target: 45%; past: climbs steeply). Coaches age +1 each offseason. New hires get age-appropriate ages (first-timers late-30s/40s, retreads 50s, poached HCs keep their age).

### HC poaching (`carousel.py`)
- Successful HCs (win_pct ≥ .70, skill ≥ 4.5, prestige < 78) are poachable by bigger jobs (step-up in prestige required). Creates **cascade openings** (their old job opens, gets refilled — can chain). Generation prob 0.85. This was ADDED because the user noticed successful HCs were never poached.

---

## 7. THE S2→S3 OFFSEASON (what was done, for reference)

Run as standalone stages (NOT the monolithic `offseason.py`), each audited:
1. **Draft** — 210 picks/7 rounds. #1: Baltazar Ethier (Orlot RB). Ryskamp winner Krupka went #7 (early entry). Subdivision draftees use real RCBA school names. 1,352 departures (203 drafted + 1,149 grad seniors).
2. **Carousel** — 14-17 HC changes incl. HC poaching (e.g. Greene poached Marines' 11-3 coach) + age-based retirements + cascades.
3. **Recruiting** — 2,802 freshmen; pyramid 25 5★/280 4★/981 3★/1121 2★/395 1★; blue-chips concentrated at top programs.
4. **Portal** — 557 entered, 339 transferred. Production-based (position-normalized) valuations; studs flow to high prestige. Top transfer: Sota Han-Cheol (TE, Rupin St→Krobe St).
5. **Development** — 7,356 developed, mean +0.387, 612 breakouts/143 busts. Gem cap 8.6 for Fr/So. Production-earned growth boost.
6. **Roster finalization** — removed departures, advanced classes, added freshmen (S3F_ pids) + 225 walk-ons (S3W_), trimmed to cap ~70. Pyramid Fr2780/So2999/Jr2303/Sr2125 = 10,207. Avg roster 67.2. (So>Fr slightly = a big prior class bulge, not a bug.)
7. **Rollover** — season=3, all records/stats reset, S2 archived, prestige rolled (Diamond City 80→85; risers Vaughn Bay St/Larksdale/Black Forest; fallers UN Ediville/Greene 93→85). Preseason recomputed (top: Central Stanton, Eona, Kaji Daun; Diamond City #12). Coach tenures +1. Auto-canonized via finalize_season.
8. **S3 Schedule** — 912 games. **Run-of-3 accepted as the new standard** (was run-of-6 last year). Conf-home exactly 4/5 (76/76), 0 back-to-back byes, all 41 rivalries locked, title site Fiota Bay, Fiota. 74% of teams at run≤2, 26% at run-3. Build ~137s.

---

## 8. STANDING USER PREFERENCES

- **Rich weekly narratives** with quarter+clock scoring in summaries.
- **Honest, proactive bug disclosure** (permanence rule). User catches bugs by auditing output and asking pointed questions (e.g. once challenged a #2 seed, a 2-pt decision, an all-QB portal — all explained/fixed).
- **Offer options, don't make silent decisions.** User prefers to be given choices and tradeoffs (accepted slightly run-heavier meta, run-of-3 schedule when informed).
- **Always show next-round matchups** after each playoff round.
- Keep **clutch breakdowns** in storylines.
- **Auto-canonize at season end.**
- Run offseason stages **one at a time with audit reports.**
- Values **cross-project portability** (RCBA ↔ CFB share geography, school names, design philosophy).

---

## 9. KNOWN GAPS vs REAL CFB (not yet built, for future reference)

Built this session: penalties, safeties, OT walk-off, special teams phase, onside kicks, weather, coaching schemes, kicker/punter quality, 4th-down analytics, momentum (light), HC poaching, coach ages/retirement.

**Skipped per user:** redshirting (declined).

**Still unbuilt (not requested):** bowl games for non-playoff teams, named rivalry trophies, mid-year transfer portal, academic suspensions, time-of-possession as a tracked stat, deeper depth-chart/position-battle modeling, in-season coaching promotions.

---

## 10. WORKING CONVENTIONS

- **Working dir:** `/home/claude/cfb2/`. **Outputs:** `/mnt/user-data/outputs/`. **Transcript journal:** `/mnt/transcripts/journal.txt` (+ catalog of prior transcripts).
- **To simulate:** `run_window.run(n)` or `season.simulate_window(n)`; website auto-rebuilds.
- **Before editing:** read the relevant `.py`. Watch the mixed str/int pid issue. Filter ints for max-pid.
- **When rolling over a season:** reset `record` WITH `PF`/`PA` fields, `weekly_perf` as a **list** (not dict), clear season_stats/firings/injuries/heat/pressure/streak. (These were bugs caught in debug — don't repeat them.)
- **Debug before handoff / after big changes:** run a 1000-game stress test (0 errors expected), check state integrity, rebuild website.

---

*End of handoff. To resume: confirm the on-disk state (season==3, next_week==1), skim the engine files you'll touch, and continue — the natural next step is simulating Season 3 Week 1.*
