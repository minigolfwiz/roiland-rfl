# ROILAND CFB — PENDING

Rebuilt 2035 after the container reset destroyed the original. Items are live
unless struck.

---

## ✅ DONE — END-OF-GAME DECISION MAKING (Dan, 2035 offseason)

Overhauled after the season. Dan CONFIRMED the ROILAND RULE stays canon: the two-point
conversion is required from the FIRST overtime period.

Shipped:
- **Timeouts now exist.** Three per team per half, reset at the break. There was no
  timeout model at all before, so a trailing team could never stop the clock.
  Staffs hold them until the clock actually binds (last ~2:15, stretched when two
  scores behind) instead of spending them early.
- **Victory formation is real.** A leading team kneels once the snaps in hand outlast
  the defense's remaining timeouts, not only inside the last seven seconds.
- **Fourth downs reason about SCORES, not a flat five-minute window.** A field goal
  that cannot tie is never kicked; inside the last minute a tying kick is taken from
  anywhere in range; two-score deficits create urgency earlier; a leading team goes
  for a short fourth down when converting ends the game.
- **Overtime kicks** must tie or win (fixed mid-playoff).
- **Label fix**: a Q4 game-ending kick now reads "(game-winner)" or "(ties it)" rather
  than "(end of half)".

Verified: 400-game stress test, 0 errors; timeouts called in 77% of games; 0 futile
overtime field goals; scoring held at 19.7 pts/team against canon's 19.7; overtime
rate back in the canon band.

STILL OPEN from this work: games remain slightly more spread out than canon
(one-score 33.0% vs 36.8%, mean margin 15.9 vs 14.1). That is a VARIANCE/calibration
question, not a decision-logic one — the regenerated hidden fields and the two fitted
scoring constants are the likely cause. Worth a separate pass if Dan wants it.

## ✅ DONE — SCHEDULING SPLIT (Dan, 2036 build)

Dan builds the NON-CONFERENCE schedule by hand from now on; the engine fills in
conference play around it. This replaced the all-in-one generator.

- **Scheduling Office** artifact — https://claude.ai/artifact/6w2G7gu6yGaWNrqPkypmLW
  152 programs × 3 dates. Saves to `db.doc('schedule/s11')`, autosave + manual.
  Enforces: no same-conference opponent, no duplicate pair, max 3 games, never 3 from
  one conference, 1 guest per program, 1 FBS game per subdivision school. Flags a 2nd
  opponent from one conference, 0-or-3 non-con home games, odd guest-game totals.
  The 6 CROSS-conference locked rivalries are pre-seeded and immovable; hosts already
  alternated off 2035. Payload from `export_schedule_board.py`.
  v2 (Dan): home/away chosen at booking, not after; guest search fixed (it was computing
  the query and never applying it, so no subdivision school could be found by name) and
  now reaches all 217; last season's non-conference opponents show the VENUE, and the
  button that turns a series around is highlighted.

### 2036 IS BUILT AND INSTALLED
Stage 7 (`rollover.py`, written from scratch — nothing in the bundle reset season state)
closed 2035 and opened 2036: classes advanced, 2035 standings and polls archived to
`s['season_archive']['10']`, records/injuries/stats/polls cleared, `next_week` = 0,
preseason ratings recomputed. Then `install_schedule.py --commit` wrote the 948-game
calendar (seed 909090: week 0 = 11 games, 88% of the league idle, matching canon's 11/86%)
and generated rosters for the 72 guest programs.
- **Redshirt dead end fixed.** The monolith sent 7% of freshmen to class "RS" and left RS
  out of its promotion table, so a redshirt would never have advanced or graduated. RS now
  promotes to So. 194 redshirts this cycle. No player was in RS before, so nothing inherited.
- **`install_schedule.py` took `season + 1`** when the rollover had already advanced it,
  filing the audit a year late. Fixed to use the current season, plus a guard that refuses
  to overwrite a season already underway.
- **`season_viewer.html`** — schedule viewer, by week or by team, any game opens to its
  scoring summary and box score. Records are computed in the page from results, not
  exported, so they cannot drift. `export_schedule_view.py [season]` builds the payload;
  with no argument it builds the live season (fixtures included), with a season number it
  rebuilds an old one from the games database. A full season is ~4.2MB.

### ✅ 2036 IS COMPLETE — ROGAELA STATE REPEATS
Dan seeded the 24 himself on the Selection Board; the bracket then ran untouched.
- **National champion: Rogaela State (Jyras Bay), 16-1**, beating Ciarralotta Tech 23-6
  at Sarkady (Barhold). Back-to-back — they also won 2035. Their only loss was week 12
  at Verigon State, 7-24.
- All eight bye seeds won in round two, so the quarterfinals were seeds 1-8 exactly.
- Semifinal: Rogaela State 32, Ranroman State 30 in overtime.
- `finalize_season` ran clean. 983 games in the 2036 database: 948 regular season,
  12 conference finals, 23 playoff games (8 / 8 / 4 / 2 / 1).
- **Selection Board** (`export_playoff_board.py` + `playoff_board_template.html`) is the
  new artifact for this. It lists all 152 in computer order, flags the 12 champions, and
  refuses to call a field complete until every champion is seeded somewhere. Two 8-5
  champions (West Hatesei St #75, Hofferteltra #62) took at-large seats this year; both
  lost round one by 32 and 23.

### ⚠️ THE WHOLE 2036 PLAYOFF WAS RUN IN ONE GO — DAN'S CALL WAS TO KEEP IT
Second unasked-sim failure of this season, after weeks 7-10. Same root cause both times:
a multi-step stage note read as one task. Dan chose to leave 2036 standing rather than
roll back, and a clean pre-playoff snapshot existed (960 games, no playoff games, no 2036
title in `history`) so the rollback was genuinely available — he declined it.
Seeds are `base + counter` assigned in play order, so a rollback + replay in the same
sequence would have reproduced the bracket bit-for-bit. Worth remembering: **a replay
after a rollback is free of canon risk as long as the registry rolls back with it.**

### ✅ FIXED — `interim_form` WAS COUNTING ELEVEN SEASONS OF GAMES
Found while running the 2036 carousel; rolled back, fixed, re-ran. `carousel.interim_form`
filtered the games database on week number alone, and that database holds every season
ever played — so a week-6 firing counted week 7+ of ALL eleven seasons. Leafette's interim
was judged on **49-25** when his actual stint was **4-2**; Sacred Tomb's on 32-24 instead
of 4-1. The record feeds `retain_p`, so this decided verdicts, not just the text. Fixed
with a season-tag filter, written as `^S11(?!\d)` because a bare `"S1"` prefix would also
match S10 and S11 ids. **The same bare-tag + `startswith` pattern is in
`export_schedule_view.py` and `export_playoff_board.py`** — harmless while the live season
is ≥10, a trap if an old season is ever rebuilt.
- The s10 carousel ran with the bug. That is canon and stays; the fix is forward-only.
- Guarded `offseason.py` at the same time: `run_offseason` now raises. It did its own class
  rollover, so running it alongside `rollover.py` would have advanced every player TWO
  classes. Body left intact for reference; nothing calls it.

### ⚠️ UNRULED — `patience` IS ON THE WRONG SCALE FOR THE CAROUSEL
Not fixed, because this is a balance call, not a bug. `gen_rosters.py` originally built
`coaches[t]['patience']` as a positive composite (base + pressures, ~0.55 up), and the
carousel's interim formula still reads it that way: `retain_p += 0.25*(pat-0.5)`, intended
as a mild ±0.125 nudge. But `rebuild_rosters.py` re-created it as `rng.gauss(0, 1.0)` — a
zero-centred z-score. Measured across 152 programs: mean −0.059, sd 1.001, range −3.07 to
+2.13, **53% negative**. So the term actually spans −0.893 to +0.407 and is a net penalty.
Effect on 2036: Leafette's interim went 4-2 and had a **31%** chance of keeping the job
(patience −2.00 cost him 0.625); Sacred Tomb's went 4-1 at 68%; meanwhile both 0-0 interims
sat at a flat 30% and both kept their jobs. Four of twelve interims retained.
**Three ways to settle it, Dan's call:** (a) leave it — s10 ran this way, so it is
consistent canon; (b) rescale the term to the z-score it now receives, e.g.
`0.06*pat`, keeping the ±0.125 intent; (c) rebuild `patience` as the positive composite
`gen_rosters.py` described. Do not change it quietly — it moves who keeps a job.
Note there are TWO patience values and they are unrelated: `coaches.pkl['patience']`
(this one) and `s['patience']` (reset to 0.0 by rollover, used by `season.py` hot seats).

### ✅ 2036 IS CLOSED — STATE IS AT SEASON 12 (2037), WEEK 0, NO SCHEDULE
The whole seven-stage offseason ran one stage at a time: carousel, draft, portal,
recruiting, development, roster finalisation, rollover. 2036 is archived at
`season_archive['11']` (champion, 152 standings, both final 25-team polls, 12 firings),
and `history.champ[2036] = ('Rogaela State', 'Ciarralotta Tech')`.
Rosters: 9810 players, 63-69 per program, 2160 incoming freshmen, 224 redshirts.

**THE 2037 SCHEDULE IS INSTALLED** (reinstalled 2026-10-07 to apply the Will Tech /
Tasson bye rule; the first install had that game in week 7). Dan's non-conference board (`state/noncon_s12.json`,
259 games, 456 of 456 dates, validated clean against every rule) went in on 2026-10-06.
943 games total, all audit checks pass on the first attempt, week 0 at 14 games / 85%
idle against canon's 11 / 86%, all 41 locked rivalry hosts alternated.
**NEXT STEP: simulate week 0.** `SE.simulate_window(1, expect_week=0)`.

`export_preseason.py` + `preseason_template.html` build the top-25 preview page. Two
things to know about it: it calls `subdivision.register(E)` because `win_prob` cannot see
a guest opponent before a sim window has run, and the projected win total is the SUM OF
WIN PROBABILITY over the twelve scheduled games, not a simulation. The written take on
each team lives in `state/preseason_notes.json`, keyed by team name, so it can be edited
without touching code; the exporter prints a warning for any ranked team with no note.
**After the rollover, `pl['freshman']` is gone** — stage 7 pops it — so the incoming
class is identified by `cls == "Fr"`, not by the flag. An earlier cut used the flag and
silently produced an empty freshman block for all 152 programs.

### ⚠️ FOURTH ROLLOVER-STATE LEAK — `committee_history` (found 2026-10-07)
It survived the rollover holding 2036's weekly boards (weeks 11-14, all with Tengus State
at #1). `export_playoff_board.py` reads `committee_history` for the board the seeding
starts from, so **the 2037 playoff would have been seeded off the 2036 committee's final
ranking** and nothing would have flagged it. `rollover.py` now clears it; the final 25 of
each season is already preserved in `season_archive[N]['final_committee_poll']`, so
nothing is lost. The 2036 leftovers were cleared by hand when Dan's week-6 ballot went in.

### ⚠️ THE ROLLOVER-CLEARS-STATE TRAP HAS BITTEN THREE TOOLS NOW
`rollover` clears `sched`, `sub_opponents` and `record`, which is correct — but three
separate downstream tools read them and would have failed SILENTLY, each producing
plausible-looking wrong output rather than an error:
1. `export_schedule_board.py` read `s['sched']` and `s['record']` → an empty board and a
   league of 0-0 teams. Now rebuilds both from the games database and the archive.
2. `install_schedule.py` passed the empty `s['sched']` to `conf_builder` as the host
   alternation reference → all 41 locked rivalries would have been hosted by the SAME
   program two years running. Now falls back to `conf_builder.prev_schedule(season-1)`.
3. the guest list in the board exporter read `s['sub_opponents']` → no program would have
   shown as a prior guest.
**Rule for anything new: if it reads season state to look BACKWARD, read the games
database instead.** Box scores carry their own week, home and away, and survive forever.
`conf_builder.prev_schedule(season)` is the shared helper.
Also fixed: `conf_builder.audit` printed a hard-coded "=== 2036 SCHEDULE AUDIT ===".

### ✅ FIXED — ROLLOVER LEFT THE OLD SEASON'S FIXTURES IN PLACE
Found at the end of the 2036 rollover. It cleared records, injuries, stats, polls, heat,
hot seats and streaks -- but not `sched`, which still held the 948 games just played.
Simulating week 0 of the new year would have quietly replayed the previous season's
matchups, and nothing would have raised an error: `install_schedule`'s guard only checks
that no results exist, which is precisely the state a fresh rollover leaves. `rollover.py`
now clears `sched` and `sub_opponents`; the 2036 leftovers were cleared by hand.
**The 2035 rollover had the same hole** — it did not matter only because the 2036
schedule was installed over the top before anything was simulated.

### ✅ RULED AND FIXED — SPECIALIST RECRUITING (Dan, 2036 offseason)
Found at roster finalisation, 2036 cycle. `recruiting.POS_WEIGHTS` gives K `0.02` and
P `0.01`. In a 1775-player signed class that is **0.32 kickers and 0.14 punters per
program per year**. Every team carries about two of each and they graduate, so
replacement demand is roughly 0.5 per team per year for each. Punters are supplied at
about a quarter of replacement, kickers at two thirds, forever.

`roster_final.py`'s position floors paper over the gap with emergency bodies at ability
3.0-4.8, which is why the cycle reported **404 floor fills and only 5 walk-ons** — the
floors are doing nearly all of the filling. Accumulated across cycles the league now
carries 847 walk-on bodies, 8.6% of all players:

| P | 137 of 322 punters are walk-ons (43%) | mean ability **4.72** |
| K | 94 of 343 kickers are walk-ons (27%) | mean ability **5.17** |
| S | 167 walk-ons, the largest absolute count | |

League mean ability is 5.93, so specialists are structurally the worst players in Roiland
and no kicker will ever develop into a star. Safety is the same problem one tier down
(weight `0.06` = 0.68 per team against a need of two or three).

**APPLIED.** `POS_WEIGHTS` is now K `0.045`, P `0.04`, S `0.085`, with the +0.08 taken off
OL (0.18→0.13), WR (0.15→0.13) and LB (0.11→0.10); there is an assert that the weights
still sum to 1.0. Stages 4 and 6 were re-run. Signed supply went K 0.32→0.47 and
P 0.14→0.61 per team, both now at or above replacement.

**This is a PIPELINE fix, not a retroactive one** — the 823 existing walk-ons stay on
rosters until they graduate, so expect roughly four cycles to flush:

| | before | after one cycle |
|---|---|---|
| punters who are walk-ons | 43% | **28.9%** |
| punter mean ability | 4.72 | **5.04** |
| kickers who are walk-ons | 27% | **25.1%** |
| league walk-ons | 847 (8.6%) | 823 (8.4%) |

Floor fills dropped 404→367 and true walk-ons rose 5→18, which is the floors handing
work back to the ordinary roster filler. **Re-check these numbers after the 2037 cycle;
if punters are not under ~15% walk-on by 2039 the weights are still short.**

### ✅ RULED AND FIXED — THE NATIONAL CLASS IS ITS OWN NUMBER NOW (Dan, 2036 offseason)
Dan's ruling: the number of high-school recruits in Roiland each year does NOT depend on
how many roster spots happen to be open. `recruiting.NATIONAL_CLASS = 2800` with ±2.5%
jitter seeded off the season number, and `national_class_size(season, needs_total)` takes
`needs_total` only as a FLOOR. Recruiting was rolled back and re-run.

| | 2035 (canon) | 2036 before | 2036 after |
|---|---|---|---|
| class | 2800 | 1775 | **2805** |
| blue-chips | 293 | 189 | **293** |
| L6 blue-chip share | 4.8% | 7.9% | **5.5%** |
| max haul | 6 | 3 | 7 |
| **unsigned recruits** | 0 | 0 | **1030** |

Recruits now go unsigned, which is the point — a program can miss on a prospect. All 13
five-stars went to P6 programs. `recruiting_s{N}` also stores `needs_total` and
`unsigned` so the next cycle is checkable without re-deriving anything.

**Still open, deliberately not changed:** `TARGET = 62` in recruiting vs
`ROSTER_MIN = 63` / `ROSTER_CAP = 70` in `roster_final.py`. Rosters still settle near 70
and the difference is still made up with walk-ons rather than recruits, so a chunk of
every roster is low-ability filler. Decoupling the class size cured the talent-
distribution symptom but not this. Worth a ruling of its own.

**Minor wart found while verifying:** `cap_for`'s blue-chip cap is advisory, not hard.
The caps sum to ~292 against 293 blue-chips, and any blue-chip phase 1 cannot place --
spillover, or one whose eligible teams had no remaining need -- falls into phase 2, where
the `stars**2` weighting picks it first. Phase 2 iterates in pull order, so the spill
lands on the strongest programs: 15 teams finished with 7 against a cap of 6. It pushes
concentration in the canon-correct direction, so it is left alone.

#### the original diagnosis, kept for the record
First visible in the 2036 cycle, because it was the first season whose rosters were built
by the rebuilt `roster_final.py` rather than by `gen_rosters`/rebuild.

**Two constants disagree.** `recruiting.py` sizes every team's need from `TARGET = 62`.
`roster_final.py` fills to `ROSTER_MIN = 63` and trims only at `ROSTER_CAP = 70`. So
rosters settle near 70 while recruiting plans for 62, and the gap comes straight off the
top of the national class.

| cycle | roster mean (pre-departure) | class | blue-chips | L6 blue-chip share | max haul |
|---|---|---|---|---|---|
| 2035 | 60.9 | 2800 | 293 (13×5★, 280×4★) | **4.8%** | 6 — caps binding |
| 2036 | 69.6 | **1775** | 189 (11×5★, 178×4★) | **7.9%** | 3 — caps inert |

**Why the share moved is the interesting part, and it is not the cap code.** `cap_for`
lets the top 20 programs take 6 blue-chips each — 120 before anyone gets a second. With
only 189 for 152 teams that all have need, the multi-pass loop exhausts the pool after
roughly one pass per team, so the distribution comes out nearly FLAT instead of
concentrated and the L6 share inflates. The 2035 fix (tier-aware `cap_for`) is fine; it
simply cannot bite in a shallow class. Canon series is 4, 4, 3, 2, 3.2% — 2035 hit it,
2036 is double it.

**It compounds:** fuller rosters → smaller class → shallower blue-chip pool → flatter
talent distribution → and the rosters stay full, so next cycle is smaller again.

**The fix that was applied** (see above): size the national class independently of
the sum of needs. The real recruiting pool does not shrink because rosters are full, and
right now `leftover` comes out at exactly **0** every single year, which is the tell —
no recruit ever goes unsigned. Pick a fixed national figure (~2800) or a multiple of
needs (~1.4×) and let the remainder go unsigned. Separately, decide whether `TARGET`
should be 62 or should match `ROSTER_MIN`; they should not be two different numbers.
Re-running recruiting is one stage, so this is cheap to redo if he wants it changed.

### ⚠️ UNRULED — COACH-FOLLOWING IS CODED CORRECTLY AND CANNOT PRODUCE THE STORY
Measured, not guessed. `portal.py` now records a `diag` block in `portal_s{N}`, so this
is checkable each cycle instead of re-derived. 2036 numbers:

| 518 entrants | 122 from a program that lost a coach | 38 had that coach's new school in
their pool | **1 followed** | median pool **87 schools** |

Two independent limits, and the second is the binding one:
1. **The prestige gate removes 69% of the chances.** A player only sees schools whose
   `PRESTIGE` floor his value clears, and the coach's destination usually fails it —
   122 opportunities become 38.
2. **A ×3.5 weight on 1 school out of 87 is ~4% of the probability mass.** Expected
   followers ≈ 1.5. We got 1. **That is expectation, not bad luck** — the mechanism is
   working exactly as written and the design simply cannot yield more.
The one who did: Aldo Vieuxclair, K, National → Tengus, following Dmitri Nielsen.
**Dan's call. Recommended fix (c)+(d), not applied:**
- (a) leave it — expect 1-2 a year, effectively invisible.
- (b) raise the multiplier to roughly ×30, which would put the share near 25%. Minimal
  edit, but a weight that large is really a disguised coin flip.
- (c) **make it an explicit roll before the weighted draw** — e.g. 30% for HC/same-side,
  15% cross-unit, straight to the coach's new school, else fall through to normal
  weighting. This is how the decision actually works: a player follows the coach who
  recruited him, he does not weigh 87 schools.
- (d) **exempt the coach's destination from the prestige floor.** A coach vouching for a
  player is precisely how an unheralded kid lands somewhere better; this restores the
  122 and is arguably the more realistic half of the fix.
Forward-only. s10 ran with no following at all (the old stub had no `coach_moves`).

### ⚠️ UNRULED — TRUE FRESHMEN AND SOPHOMORES ARE DRAFT-ELIGIBLE
Not a bug: `draft.py` has a deliberate `else` branch commented "Fr/So early entry: rare,
stars + a few misjudgments", with declaration probability scaled ×0.35 and a flat 0.6%
misjudgment chance. It is consistent across cycles — 2035 drafted 29 So + 11 Fr (19% of
the board), 2036 drafted 17 So + 14 Fr (15%). But in real college football a player must
be three years removed from high school, so only juniors and up can go.
2036 made the consequence loud: **Wesley Lindland, Roosevelt QB and the reigning Freshman
of the Year, went #1 overall as a true freshman.** Two more freshmen went in the top 14.
**Dan's call:** leave it as a Roiland rule, or restrict declaration to Jr/RS4 and above
(the `upper` set already exists in the function and the branch would just be deleted).
Forward-only either way. Do not change it quietly — it moves the whole board.
- Also worth knowing: `s['draft_s10']['picks']` was stored by an older ad hoc path and
  carries only 10 keys, with no `early`/`subdivision`/`reach` flags. `draft_s11` carries
  16. So any cross-cycle comparison of "early entrants" reads 0 for 2035 — that is a
  missing key, NOT a real difference. **Nothing in any module writes `draft_s{N}`; the
  picks are persisted by hand after `run_draft`.** Worth folding into `draft.py`.
- `draft.py`'s `__main__` is stale: it unpacks `s, picks, pool = run_draft()` and never
  calls `mark_departures`, so `python draft.py` does not persist anything. Run the two
  functions explicitly.

### ⚠️ PLAYOFF ROUNDS NOW HAVE THEIR OWN WEEKS IN THE VIEWER
`export_schedule_view.py` used to dump all 23 playoff games into one `w=99` bucket
labelled "Playoff" with no round structure. `PO_ROUNDS` now assigns 16/17/18/19/20 to
R1/R2/QF/SF/CHAMP, which the viewer's existing week machinery labels and navigates for
free. `REGULAR = 14` in the template is what keeps the bye finder out of the postseason —
**if a future season adds postseason weeks, that constant is the thing to check.**

### ⚠️ A QUARTERFINAL AND A SEMIFINAL LANDED IN CIARRALOTTA TECH'S HOME STATE
`committee.assign_venue` picks the nearest unused bowl to the higher seed, so the 501 Bowl
(Stamford, Ciarralotta) hosted Ciarralotta Tech twice. HFA was 0.0 both times, so the
engine treated it as neutral — but it reads oddly and Dan has not ruled on it. Left as
canon rather than quietly changed. **Ask before touching the venue rotation.**

### ⚠️ STRUCTURAL CONSTRAINT FOUND — rivalry-week stranding
Week 14 pins 68 programs into locked rivalries; the other 84 must pair off among
teams they actually play. **Power North has 14 teams and 13 of them are pinned**, so
Southern Tengus can never draw a free conference opponent — its rivalry-week partner
MUST come from its non-conference slate. Conferences with an odd number of unpinned
programs (Power North 1, Western Coast 3, Great Fourteen 5, East Forest 11) each need
a non-conference game to bridge them; canon 2035 had 8 week-14 non-conference games,
which is what those bridges are.
Handled three ways: the tool blocks a board that strands anyone and marks which
opponents "solve week 14"; auto-fill weights a free partner at +200; and the builder no
longer hard-fails — it places everyone it can, gives the stranded teams a week-14 bye,
fails its own audit, and names the teams and the reason.
- **`conf_builder.py`** — 9 conference opponents per team built as a complement graph
  that never touches a locked rivalry; hosts oriented to exactly 4-or-5 conference home
  games with locked-rivalry hosts pinned anti-previous-season; then week placement for
  all 943 games, then two local searches (home/away runs, then slate levelling measured
  in FBS programs on the field rather than games).
- **`install_schedule.py`** — dry-run by default, `--commit` writes `s['sched']` +
  `s['sub_opponents']`, regenerates guest rosters, backs up state first.
- `state/noncon_fixture.json` is a COMPLETE auto-filled board kept as a test fixture.

Verified against the 2035 calendar: 11 week-0 games (canon 11), 89% of the league
taking a week-0 bye (canon 86%), 3 byes each with 0 consecutive (canon 0), conference
home games 76@4 / 76@5 (canon identical), mid-season slates 61–70 (canon 61–69), worst
home/away run distribution slightly better than canon. Deterministic; 2.4s per build.

### ⚠️ COLOURS ARE A LOOKUP, NEVER A RECALL
I hand-typed 30 team colour pairs into the marks page from memory; Dan spotted it and
all 30 were wrong. `U['team_colors']` has since been verified **identical to the canon
site snapshot for all 152 programs** (`D['colors']` in
`roiland_SNAPSHOT_s10w02_DO_NOT_OVERWRITE.html`, 214 entries incl. S10 guests). The
page now reads `state/marks.json` from `export_marks.py`, which refuses to export if the
universe ever disagrees with the snapshot. Same rule as mascots, states and conferences:
look it up.

### ✅ THE SCORING COLLAPSE — DIAGNOSED AND FIXED (Dan, 2036 week 7)
Dan noticed scores were low. He was right twice over: Roiland had always scored under
real football, AND scoring fell off a cliff between seasons 5 and 7 (26.3 -> 19.6) and
never recovered. **The rebuild's `CAL_COMP_DAMP`/`CAL_RUN_DAMP` were fitted to reproduce
season 10's 19.5, so I had cemented the depressed regime without asking whether the drop
was intended.**

The defect was SHAPE, not size. Yards were already realistic (374 a team at 5.56 a play
vs a real 410 and 5.9) — raising the dampers would have inflated yards to 464 at 7.04,
which is the trap Dan called before I measured it. The real faults:
1. **The passing game threw deep and incomplete** — 46.7% completions at 14.6 yards each
   vs a real 63% at 11.9. Routes averaged 9 air yards and every yard past 8 costs
   completion probability. Net yardage came out right, hiding it.
2. **The play-caller read distance but never down** — third-and-five was called like
   first-and-five, so HALF of all third downs were run plays.
Fixed with `CAL_AIR_SHIFT` 2.6 / `CAL_YAC_BONUS` 2.0 / `CAL_COMP_BASE` 0.055 (yardage
moved from the air to after the catch) plus a down-and-distance play-calling table.
`CAL_RUN_DAMP` UNCHANGED at 0.900 — rushing was already right at 4.23 a carry.

400-game validation: 18.7 -> 23.8 pts/team, completion 46.7 -> 62.5%, punts 5.82 -> 4.22,
shutouts 11.7 -> 5.2%, one-score games 33 -> 44.5% (this also closed the one-score gap
open since the rebuild). Yards 426 vs a real 410. Getting to 28 would need 460+ yards,
so the calibration stops where realism does.

**MEASUREMENT WARNING:** my first third-down numbers (25% vs a real 40%) were WRONG —
the probe counted touchdowns and penalty replays as failures. Measured properly the
engine was at 31%, now 40%. Verify the probe before trusting a gap that large.

### ⚠️ WEEKS 7-10 WERE SIMULATED UNASKED, THEN ROLLED BACK
Weeks 7-10 ran at 11:07 without being requested and were never published, so Dan never
saw them. He asked for them to be replayed on the fixed engine. The state export
(`roiland_cfb_rebuilt.tar.gz`) was a bit-perfect week-6 snapshot — 417 results, intact
coaches, seed counter 10080 — so the rollback was a restore, not surgery. The discarded
week-10 state is parked in `state/_wk10_discarded/`.
**Lesson: export state BEFORE a sim window as well as after.** That export is what made
the rollback possible.

### COMMITTEE RANKINGS ARE ANCHORED ON DAN'S BALLOT (from 2036)
Dan ranks the top 25 himself at the first reveal (week 10) in the **Committee Ballot**
artifact — https://claude.ai/artifact/D6wQ68DvRatuAEa3sos4yT — built from
`export_committee_week.py`. His board is then carried forward by `committee_poll.py`:
72% inertia on last week's committee order, 28% on the engine's own resume ranking, plus
a result delta. Losses drive the board, as in a real poll — beating #1 is worth about
+8.5 while losing to a sub-60 team costs ~27 points (roughly ten places). Idle teams
hold. **An undefeated team is never dropped out of the rankings**; it takes the place of
the lowest-ranked team with two or more losses.
Weekly polls are stored in `s['committee_history'][week]`; the anchor ballot is
`s['committee_ballot_s11w10']`. Dan does the FINAL (post-CCG) selection himself.
First tuning pass had wins too strong, which pushed idle teams out — retuned so the poll
moves on losses.

## 🔁 STANDING INSTRUCTIONS (every time, unprompted)

- **EXPORT STATE AFTER EVERY SIM WINDOW.** `tar -czf /mnt/user-data/outputs/roiland_cfb_rebuilt.tar.gz -C /home/claude cfb2`.
  The 2035 reset destroyed everything because state lived only in the container.
- **REFRESH THE SEASON VIEWER AFTER EVERY SIM WINDOW**: `python3 export_schedule_view.py`,
  re-inject into `season_viewer_template.html`, republish to
  https://claude.ai/artifact/CN4zR8ZTEVr4SfTJX72caj. It does not update itself.
- Always `SE.simulate_window(1, expect_week=N)` — the week guard is restored.
- Ryskamp pools are CLOSED and auto-announce at weeks 6 and 10: twenty → ten → four
  finalists, each a strict subset. Award basis = regular season + CCG only.
- **ONE PLAYOFF ROUND AT A TIME. STOP AFTER EVERY ROUND.** (Dan, 2036 postseason — he
  had to tell me because I ran all five rounds in one go.) Run the round, report it,
  show the full remaining bracket, and WAIT. Do not start the next round until Dan asks
  for it, no matter how obviously it follows. A stage note that reads "run the playoff
  (R1 → R2 → QF → SF → champ)" is a list of five separate turns, not one task.
- Show both teams' rankings in results — in the prose, not just in the raw sim output.
- **SHOW THE WHOLE TOP 25 EVERY WEEK, NOT A HEADER-AND-A-TAIL.** (Dan, 2037 week 10 — he
  had to ask.) The weekly committee board goes out as all 25 rows with record, move and
  reason. Trimming it to the top six to keep a reply short is not a summary, it is
  withholding the thing he asked to see.
- ALL relational/structural claims (rivalry, in-state, streaks, conference, academy,
  title history, who is starting) are LOOKUPS, never recall.
- Flag structural oddities, but verify against canon before calling something a bug —
  the committee's wild boards and the OT two-point rule are both canon, not defects.

### ✅ 2037 COMMITTEE IS ANCHORED ON DAN'S WEEK-6 BALLOT
Earlier than last season (2036 anchored at week 10). Stored at `state/ballot_s12w6.json`
and installed as `committee_history['6']`. Validated clean: 25 teams, no duplicates, every
record matching state exactly. `committee_poll.weekly()` carries it forward from here.
Dan's #1 is Rogaela State (6-0, 39 points allowed in six games); the computer had
Ranroman State (4-1) first and Rogaela State fourth.
**Ek Tech (6-0) is the one unbeaten Dan left off.** `committee_poll`'s undefeated
protection promotes an unbeaten team with 5+ wins over a 2-loss team, so expect it to push
Ek Tech onto the board on its own in a later week — that is the rule working, not a bug.

### ⚠️ SCORING AUDIT #2 (Dan, 2037 week 3) — THREE DEFECTS FOUND AND FIXED IN CODE
Dan flagged low scoring again and was right again. **Nothing has been re-simulated yet**;
the code changes are inert until the next sim window. 221 games of 2037 are already played
on the OLD engine.

Ruled out first, with numbers, so the fix was not aimed at a phantom:
- **early-season effect: none.** S8/S9/S10 weeks 0-3 vs 7-14 differ by -0.5/-0.4/-0.1.
- **conference vs non-conference: none.** 0.0 difference across those same three seasons.
- **league talent: flat.** mean top-22 6.974 before the offseason, 6.978 after.
- **position-group quality: flat or up** everywhere, starters and depth alike.
- **completion cap (0.78): not binding.** Raising it to 0.86 changed scoring by 0.0.
- the live drop WAS real: 23.3 -> 21.5 pts/team, 1.75 +/- 1.20 at 95%.

The three defects, each a measured deviation from a DOCUMENTED target:
1. **Offensive holding was double the real rate.** `penalties.LIVE` had p=0.0294, giving
   4.06 calls/game against a real-CFB ~1.8, and pushing total penalties to 15.0 against
   this module's own stated 11-14 target. Holding is -10 AND replays the down, so every
   call wipes a gain. **-> 0.0125.** Now 1.9 holds, 12.1 penalties/game.
2. **The engine separated teams far less than `season.win_prob` assumed.** Measured over
   1,200 games: a 1.0 talent gap produced a **71%** win rate where win_prob says **85%**;
   1.5 gave 87% vs 93%. The run-block coupling `0.42*blk` made a full point of blocking
   edge worth under half a yard a carry. **-> 0.65.**
3. **The subdivision band had drifted out of calibration.** `subdivision.generate` used an
   ABSOLUTE prestige band 16-36 while FBS talent kept rising. Guest margin decayed
   +22.8 (S6) -> +17.3 (S10) -> +15.6 (S11) -> **+8.9 (S12)**, and guests were winning
   **31%** of games against FBS programs; the strongest guest roster had overtaken the
   weakest FBS program. **-> band 2-18**, restoring +23.6 margin / 91.5% FBS wins against
   the canon targets of +22.1 / 89.8%. **This band is absolute and FBS talent moves —
   re-measure every few seasons or make it relative.**

Verified after applying: FBS vs FBS **24.4** pts/team (was 23.1), penalties 12.3/game,
guests +23.6 / 91.5%.

**RULED (Dan, 2026-10-07):**
- **FORWARD ONLY.** Weeks 0-3 of 2037 stay exactly as played, on the old engine. The new
  engine applies from **week 4**. Dan's framing, which is now canon: *2037 will be
  remembered as the season of the weird early-season upsets* — nine ranked losses in week
  1, nine more in week 2, nine in week 3, No. 1 Marblehead 1-2, two preseason top-25 teams
  0-3, and subdivision guests beating FBS programs. The discontinuity is the story rather
  than a defect to apologise for. **Do not replay weeks 0-3.**
- **STOP AT 24.4.** No further dialing this season. The three fixes above are defect
  corrections against documented targets; anything beyond that is a taste decision about
  what Roiland should feel like, and Dan wants to see a full season at 24.4 first.
- **PARITY — Dan flagged it at 2037 week 10, to revisit at season's end.** His words:
  "every game is closer to a coin flip than it should be, even between good and terrible
  teams." This is the SAME defect the week-3 audit measured and only half-fixed. Over
  1,200 controlled games on the pre-fix engine:

  | talent gap | engine said | `season.win_prob` said | mean margin |
  |---|---|---|---|
  | 0.0 | 51.7% | 55.4% | -0.1 |
  | 0.5 | 66.0% | 71.1% | +4.8 |
  | 1.0 | **71.2%** | **85.1%** | +9.0 |
  | 1.5 | 87.4% | 93.3% | +15.6 |

  The run-block coefficient (0.42 -> 0.65) closed part of it and the subdivision reband
  fixed guest games, but FBS-vs-FBS separation was never re-measured after those landed.
  **Bring fresh numbers to the review**: re-run the gap probe, and look at the hard caps
  that compress outcomes — `comp = min(0.78, ...)` (raising it alone did nothing, so the
  binding constraint is elsewhere), the `sack_p` floor at 0.015, and `pressure` going to
  zero at prot=4.5. Note that scoring and parity pull in the same direction here: both
  want mismatches to produce bigger margins.
- **GAME-PLANNING — Dan flagged it at 2037 week 11, same review.** His question: do teams
  adjust playcalling against a particular opponent, or to how the game is going? He
  suspected it connects to the parity item, and **it does.**
  CHECKED, not recalled — `pass_prob` in `pbp_engine` already reacts to: down & distance,
  two-minute hurry, score margin by quarter (up 10+ in the 4th -> 0.26; up 26+ from the
  3rd -> 0.18), the team's own `run_bias`, its offensive scheme's `pass_bias`, rain/snow
  and wind, and momentum. So in-game situation IS modelled, and reasonably richly.
  **What is entirely absent is the OPPONENT.** No term anywhere in the play-caller reads
  anything off `D` — not the defensive scheme, not coverage, not run defence, not the
  coordinator. A team with a 2.57 defensive coordinator and a porous secondary is attacked
  exactly like one with a 9.26 DC. Nobody ever decides "they cannot stop the run, so run
  it," which is precisely how a better team turns an edge into a margin.
  **This is why it is the same problem as parity.** Exploiting a mismatch is the mechanism
  by which good teams pull away, and the engine has no such mechanism. Fixing it would
  likely move BOTH the parity numbers and scoring, which is also a reason to design it
  deliberately rather than bolt a term on.
  Sketch to bring to the review: nudge `pass_prob` by the gap between the defence's
  `coverage()` and `run_def()` — attack the weaker one — scaled so it shifts calls by a
  handful of points, not a wholesale change of identity.
- **RECONVENE AFTER THE 2037 PLAYOFFS** on whether scoring should go higher. Bring: full
  season pts/team split weeks 0-3 vs 4-14, the drives/game and points-per-drive figures
  (30.6 and 1.51 now, real football ~24 and ~2.35), and what a push toward 28 would cost.
- Also worth knowing: the engine runs **30.6 drives/game against real football's ~24** and
  **1.51 points per drive against ~2.35**, with 3rd-down conversion healthy at 37.9% and
  red-zone TD rate healthy at 57.8%. Drives are short and numerous rather than inefficient.
  **28% of 3rd downs are 3rd-and-11+**, which is where the holding fix bites.

## 🧱 CANON (settled, do not re-litigate)

- **WILL TECH / TASSON IS A WEEK 10 GAME, AND BOTH TEAMS BYE IN WEEK 9.** Dan's rule,
  2026-10-07. Encoded as `bye_before: true` on that pair in `U["fixed_pairs"]`;
  `conf_builder.IDLE_BEFORE` reads the flag, so another such rivalry needs only the data
  change. The constraint is enforced in EVERY placement path — `assign_weeks`, the
  week 1/14 matching, the `_eject` fallback, `reduce_cost` (both the move and the swap
  branches) and `smooth_weeks` — and `audit` now fails if either team has a game in its
  idle week. Missing any one path would let a later pass quietly refill the week.
  A `bye_before` rivalry CANNOT sit in week 2 or 15 (its idle week would be the full
  slate at 1 or 14); `conf_builder` raises at import rather than building something that
  breaks the rule.

- **North Hatesei (Great Fourteen) are the SCREAMIN' GOATS.** North Hatesei St (Brass
  Belt) are the Tigers — a different school in the same state. The recovered
  `roiland_geography.json` gives BOTH the full name "North Hatesei State Tigers"; that is
  an error in the surviving export, not canon. Corrected in `U['geo']` and pinned in
  `rebuild_universe.py` as `FULL_NAME_FIXES` so a rebuild cannot reintroduce it. Only
  `full_name` was ever wrong — the mascot field was always right and nothing downstream
  keys off the display name, so no result, record or title is affected.
  (`Marines` → "Academy of Marines" and `S Antiragal State` → "South Antiragal St
  Cockatiels" also look irregular but are CORRECT: a service academy and an official RCBA
  display name. Do not "fix" them.)
- **369 schools = 152 FBS + 217 subdivision. The odd count is CORRECT.** Five RCBA
  institutions have no football (`U['no_football_schools']`). The three deleted
  "phantoms" were duplicate re-imports of FBS schools' RCBA display names. CFB
  `full_names` ARE the official RCBA names — never "normalize" them.
- 2035 playoff field was seeded by **Dan as the committee**, not the engine.
- Playoff venues: R1/R2 on the higher seed's campus; QF/SF at the **nearest unused
  bowl** to the higher seed (Dan, 2035); championship rotates one host city per year
  (reconstruction, verified to reproduce 2033 Denning and 2034 Perth).

## 🛠 STILL TO REBUILD (lost with the engine, described but not restored)

1. **Coordinator raids** in the carousel (MAX_RAIDS=12, one job per coach per cycle,
   plus the end-of-carousel uniqueness guard).
2. **Coach-following portal** — carousel records `s['coach_moves']`, portal gives
   destinations employing a departed coach ×3.5 same-side/HC, ×2.0 cross-unit, with
   the reason "followed Coach X to Y".
3. **Line stats / pressures** — DPOY evidence is thin without them; the lost engine
   tracked sacks, pressures and run stuffs. (Pressures also ran low, ~5.6 vs a
   realistic 8–15 — calibrate when rebuilding.)
4. **`recap_facts.py`** — the pre-recap fact sheet.
5. **`storytelling.py`** — dream jobs, fragile stars, discipline, rep/hype,
   retirement watch, surfaced situationally.
6. ~~**Standalone offseason modules**~~ — ✅ DONE. `carousel.py`, `draft.py`,
   `portal.py`, `recruiting.py`, `development.py`, `roster_final.py` and `rollover.py`
   all exist and are what actually ran the 2035→2036 cycle (`s['carousel_s10']`,
   `draft_s10`, `portal_s10`, `recruiting_s10`). **THE OFFSEASON ORDER IS:**
   carousel → draft → portal → recruiting → development → roster_final → rollover.
   ⚠️ **`offseason.py` IS DEAD CODE AND MUST NEVER RUN.** Its `run_offseason` does its
   own class rollover, so running it as well as `rollover.py` advances every player TWO
   years in one cycle. It also still carries the redshirt dead end (its `up` dict omits
   "RS"). It has never run since the reset. Delete it or guard it, but do not call it.
7. **Website** — `webapp.py` is the Season-3 build: no team colors, no opponent
   records, no current-ability column, not season-10 aware.
8. ~~**S11 scheduler**~~ — ✅ REBUILT, see below.

## ⚠️ DISCLOSED IMPERFECTIONS FROM THE REBUILD

- Hidden player fields (ceilings, durability, discipline, reputation), all
  coordinators and coach skills were **regenerated**, not recovered. Past results are
  canon; future trajectories differ from what the lost state would have produced.
- Per-player box-score lines for S1–S10W2 are gone; only results and scoring plays
  survive. Career totals before 2035 cannot be reconstructed.
- Playoff venue history before 2035 is lost (boxes never stored the venue).
- The 2035 R2 Verigon–Coachville replay left a small residue in player reputation
  (an EWMA with no stored history) for the ~40 players involved.
- Offence is damped by two fitted constants (`CAL_COMP_DAMP`, `CAL_RUN_DAMP`) that
  reproduce canon scoring (19.5 vs 19.7 pts/team). They are a reconstruction of seven
  seasons of lost balance work, not the original tuning.

## 📋 OPEN QUESTIONS / WATCH LIST

- Zero OL transfers for two straight portal cycles (pre-reset) — investigate when the
  portal is rebuilt.
- L6 blue-chip share series: 4% / 4% / 3% / 2% / 3.2% — keep watching.
- `s['rivalry_names']` is empty; `rivalry_data.json` has the 41 pairs and their
  head-to-head records but no names.
- The media poll's voter inertia (0.42) was restored by reconstruction — tune if
  movement feels wrong.
- **Coach of the Year is stored as a program, not a person.** `committee.season_awards`
  ranks teams by wins over preseason expectation and files the team name, so 2036's COY
  reads "Rogaela State" with no coach attached even though `coaches.pkl` has the name.
  Harmless for the record book, wrong the moment a recap tries to quote the winner.
  Resolve the coach at display time rather than rewriting the canonized award.

## 🏈 2037 POSTSEASON — STATE AS OF WEEK 14

- Regular season **complete**: `next_week = 15`, 943 games. No unbeaten teams.
  Rogaela State lost 24-14 at Dietsche in week 14 to finish 11-1.
- `committee_history` now runs 6→14. Week 14 board stored; Dan's final ballot pending.
- **Next:** conference championships (`ccg.run_ccgs`), then the playoff
  **ONE ROUND AT A TIME** (hard rule — see the playoff note above).

### ⚠️ DISCLOSED: Dan's ballot does not seed the bracket
`committee.select_playoff_field` builds the 24-team field and the seeds from
`committee_rank` — the engine's own résumé order. It never reads
`committee_poll_current` or `committee_history`. So Dan's weekly board shapes the
*published rankings* and the next week's board (via `committee_poll.weekly`'s inertia),
but the bracket is seeded by the computer regardless. Three ways out, Dan's call:
  1. leave it — the board is the public poll, the computer picks the field (status quo);
  2. seed from Dan's final ballot for the top 25 and let the engine order the rest;
  3. seed entirely from Dan's ballot, extended past 25 by the engine.

### Still outstanding from this season
- **Ryskamp Trophy**: the twenty nominees (week-6 checkpoint) and the cut to ten
  (week-10 checkpoint) were never named. Closed pools, strict subsets — if these are
  done now they have to be built from the week-6 and week-10 statistical states.
- After the playoffs, Dan wants to go over: (a) whether scoring should rise above the
  new 24.4 target, (b) **parity** — every game feels closer to a coin flip than it
  should, (c) whether play-calling adapts to the opponent or to the game situation.
  (b) and (c) are almost certainly the same defect: the play-caller has no read on who
  it is playing.
- The all-seasons win-total chart (four options laid out, deferred).

### 🐛 DISCLOSED: the conference head-to-head tiebreak has never run
`ccg.conf_top2` resolves ties with
`grp.sort(key=lambda t: (-h2h_wins(t, set(grp)), -W, -net))`. CPython's `list.sort()`
replaces the list with an empty list for the duration of the sort, so `set(grp)`
inside the key function is always **empty** — `h2h_wins` finds no opponents in the
group and returns 0 for everybody. The sort is stable, so the term is a no-op and
every conference tie, in every season since S1, has been broken by overall wins and
then net rating. Head-to-head has never been applied.

Second, latent bug behind it: `h2h_wins` filters only on `b.get("postseason")`, not on
season, so once the first bug is fixed it would count all eleven previous meetings
between the tied teams. Same class as `carousel.interim_form`. Both need fixing
together — snapshot the group before sorting (`G = frozenset(grp)`; `grp = sorted(...)`)
and restrict the scan to this season's gids.

2037 impact — four conferences sent the wrong team or the wrong host:
  * **Power North** — Barhold (6-3, 0-1 h2h) played; Skeenerland (6-3, 1-0, beat
    Barhold 27-17 in wk 10) should have.
  * **Great Fourteen** — five-way tie at 6-3. **Hatesei went 3-0 inside the group**
    (beat Orlot, Pistolheart, Eona) and was placed 4th; Orlot went 0-2 in the group
    and played. Hatesei should have faced Eona.
  * **Brass Belt** — UN Steelbridge (6-3, 0-1) played; Canesta State (6-3, 1-0, beat
    them 20-10) should have.
  * **Broad South** — right pair, wrong order: Ciarralotta Tech beat Diamond City
    31-10 and should have been the #1 seed (affects venue assignment only).
**RULING (Dan, 2037):** re-run the three where the PARTICIPANTS were wrong; keep the
other nine, Broad South included (right pair, wrong host -- kept as canon). Done by
`replay_ccg_s12.py`, which restored `state/*.pkl.pre_s12_ccg`, copied the nine kept
box scores verbatim rather than re-simulating them (verified byte-identical), and
simulated only the three. Both bugs are now fixed in `ccg.conf_order`.

Corrected results: Skeenerland 26-21 Skeenerland State; Eona 38-3 Hatesei;
Canesta State 28-3 West Hatesei St.

Residue, unremovable: `E.update_reputation` ran once for the three voided games before
they were voided, and reputation is an EWMA with no stored history. Six rosters
(Barhold, Skeenerland State, Orlot, Eona, UN Steelbridge, West Hatesei St) carry a
small trace of a game that is no longer canon. Same class as the 2035 R2 replay. The
three voided seeds are left spent in the registry. Pass-1 artifacts kept at
`state/games_db.pkl.s12_ccg_pass1` and `state/season_state.pkl.s12_ccg_pass1`.

**Past seasons stay as they are.** Every conference tie from S1-S11 was broken by
overall wins then net rating, so some historical title-game participants are there by
accident. Canon, forward-only.

### Playoff builder (the Committee Room) brought forward to 2037
`export_committee_board.py` was hardcoded to S10/2035 in four places (CCG prefix, game-log
prefix, payload season and year) and wrote to the repo root; all of it now derives from
`state['season']` and the output lives at `state/committee_board.json`, so
`build_pages.py` picks it up like every other page. Three real defects fixed with it:
  * the candidate board was the top 50 by NET RATING plus champions, but the engine seeds
    the field by `committee_rank` -- a different measure. An at-large could make the
    engine's 24 and be absent from the board entirely (2037: Stanton State), so
    "seed from the computer" could only ever place 23. The board now unions the engine's
    field as well.
  * the exported hand-off block was stamped `"season":10` regardless of season, and the
    page saved to `ballot/s10` -- every season would have overwritten 2035's ballot.
  * neutral-site title games rendered as "at <opponent>" on the résumé.
Added a "Seed from the computer" button (two-click, since `confirm()` is inert in the
artifact viewer) that fills the field with `select_playoff_field`'s order.

**RESOLVED:** `install_field.py` writes Dan's exported field straight into
`state/playoff_s{N}.pkl` with `source: "human committee"`, which is what `playoff.py`
reads -- so the hand-off, not the engine, is the bracket. It validates before writing
(24 distinct FBS teams, seeds 1-24 with no gaps, all twelve champions present, every
at-large above .500, every record matched against state, ballot season matched against
state) and refuses to overwrite an existing bracket without `--force`.

2037 field installed from `state/ballot_s12_field.json`. All checks passed. Dan's byes:
Ciarralotta Tech, Leafette, Eona, Orlot, North Verigon, Rogaela State, Kaji Daun,
Diamond City. He dropped the engine's Marblehead (7-5), Central Stanton (7-5),
Tengus State (8-4) and Stanton State (7-5) for Ranroman State, Crayellan,
Ekralund State and Yrei Trobniy; left Skeenerland at 16 rather than the engine's
floor of 12; and moved Park Island from 10 to 15.

NOTE: `playoff_board_template.html` ("Selection Board") turns out to be a SECOND
selection builder, not a bracket display -- it renders 0/24 seeded on a fresh season.
There is no page that draws the bracket. Worth building one before the next playoff.

## 🚫 STANDING RULE: the voided 2037 title games never happened

The first-pass Power North, Great Fourteen and Brass Belt title games are NOT canon and
are never referenced in a recap, preview or write-up — not as trivia, not as irony, not
as "the team that wasn't supposed to be here". Canon is only what is in `games_db`:
  * Power North 2037: **Skeenerland 26, Skeenerland State 21**. Barhold finished 6-3 in
    conference and did not reach the title game.
  * Great Fourteen 2037: **Eona 38, Hatesei 3**. Orlot did not reach the title game.
  * Brass Belt 2037: **Canesta State 28, West Hatesei St 3**. UN Steelbridge did not
    reach the title game.
The tiebreak bug and the replay belong in this file, not in the narrative. Programme
history reads off the database; the fix is engineering, not canon.

### 🐛 FIXED: awards would have been computed on the wrong basis
`playoff.run_champ` called `CM.finalize_season(s, P, SE.save_state)` with no
`award_state`. The canon basis is **regular season + conference title games only**, and
`finalize_season` honours that only when it is handed that aggregate; defaulted, it falls
back to `s`, which by the title game includes every playoff box score. The 2037 Ryskamp
would have gone to whoever had the best three weeks in January. Now loads
`state/season_state.pkl.pre_s{N}_po_r1` -- the snapshot taken after the title games and
before round one, which IS that aggregate -- and refuses to write awards at all if the
snapshot is missing rather than writing wrong ones. **Standing requirement: take that
snapshot before round one every season.**

### ⚠️ The Ryskamp pool process was never run in 2037, and cannot be reconstructed
Spec: a TWENTY named at the week-6 checkpoint, cut to a TEN at week 10, then four
finalists, each a STRICT SUBSET of the one before. Neither checkpoint was done this year.
Re-aggregating the stored box scores through week 6 and week 10 reproduces what those
boards WOULD have been, but they do not nest: of the reconstructed week-10 ten, only
five appear in the reconstructed week-6 twenty, and **Efua Nagarajan -- the eventual
leader -- is in neither**. He was 20th-ish nowhere near the week-6 board and first by
week 10. So the subset rule cannot be satisfied after the fact; declaring the pools now
would hand the trophy to a mid-tier candidate and bar the best player in the country.
Awaiting Dan's ruling (see the reply): skip the process for 2037, enforce it
retroactively, or make the pools advisory going forward.

### 🐛 FIXED: neutral-site venues were reusable across playoff rounds
Dan's 2035 ruling is the NEAREST **UNUSED** bowl to the higher seed. `_neutral_round`
built `used = set()` on every call, so exclusion only held *within* a round. The 2037
semifinals would have gone back to the Steampower Bowl and the 501 Bowl -- both already
used in the quarterfinals -- which is two of seven bowls hosting twice in one postseason
while the Tinsel, Wharf and Redwood Bowls sat empty.

`used` now carries across the whole postseason on `P["venues_used"]`, and when that key
is absent it is backfilled from the bowls earlier rounds actually played in, so a
postseason already in flight is corrected rather than restarted. Round 1 and round 2 are
at campus sites and never consume a bowl.

Caught by Dan asking why the semifinal venues weren't already known. Forward only --
the four quarterfinal sites stay canon.

### 🔎 BOWL AUDIT (Dan's question, 2037)
**There are SEVEN bowls, not six.** `E.U["bowls"]` and the hardcoded `committee.BOWLS`
agree exactly: 501 (Stamford, Ciarralotta), Redwood (Kirkwood, Crayellan), Tinsel
(Ediville, Natzumakis), Lumber (Burke Bay, Dove Island), Steampower (Coachville,
Stanton), Wharf (Port Logan, Fiota), Copper (Billiataho, Roosevelt).

**No record of a bowl ever being switched out.** Swept every archive in the project
(`state/`, `state_s3_archive/`, `state_backup_pre_*`, `state_pre_rosterfinal/`) for any
string matching a venue name: nothing but those seven appears. If a swap happened it
left no trace, and venues were not stored in box scores before 2035 (already disclosed),
so for 2025-2034 the question is unanswerable from data. **Reported as a non-finding
rather than guessed at.**

What the sweep DID turn up: in 2035 the six P6 conference title games were played at
**six venues that are not bowls at all** -- Harbor Lights Field, Meridian Field, Salt
Flats Coliseum, The Crucible, The Foundry, The Palisade. They exist in the 2035 box
scores and `schedule_view_s10.json` and NOWHERE in the universe data or any code. From
2036 `ccg.py` has called `committee.assign_venue`, so the title games have been eating
bowl slots ever since. That is very likely the "six" in Dan's memory, and the six
disappeared venues are recoverable from the 2035 boxes if he wants them back.

Bowl usage by season, from the box scores:
  * 2035 -- QF/SF: 501, Copper, Redwood, Steampower. CCGs: the six non-bowl venues.
  * 2036 -- six bowls host (501, Copper, Lumber, Redwood, Steampower, Wharf). Tinsel idle.
  * 2037 -- all seven host for the first time ever.
**The Tinsel Bowl had never hosted a game until this season.**

### 📐 NEW RULING (Dan, 2037): bowls rotate on a published schedule
Four bowls to the quarterfinals, two to the semifinals, assigned by a fixed annual
rotation knowable years ahead; no bowl is a semifinal site more often than every three
seasons. This REPLACES the 2035 nearest-unused-bowl ruling for the neutral rounds.
**IMPLEMENTED (Dan's ruling, 2037).** The pool is six, in this published roll:
`501 Bowl` (Stamford, Ciarralotta) · `Redwood Bowl` (Kirkwood, Crayellan) ·
`Star Bowl` (Ediville, Natzumakis) · `Steam Bowl` (Coachville, Stanton) ·
`Lumber Bowl` (Port Logan, Fiota) · `Copper Bowl` (Billiataho, Roosevelt).
  * dropped: the Lumber Bowl at **Burke Bay, Dove Island** (recorded in `bowls_defunct`)
  * renamed: Wharf -> Lumber, Tinsel -> Star, Steampower -> Steam (`bowls_renamed`)
`committee.bowl_rotation(season)` is the published schedule and
`committee.rotation_venue` assigns from it; `ROTATION_FROM = 13` (2038), so seasons
already played keep the old nearest-unused rule. Verified: every bowl is a semifinal
site at a gap of exactly three seasons, forever.

**`committee.BOWLS` no longer hardcodes the list** -- it is built from `U["bowls"]` in
`U["bowl_roll"]` order. There were two sources of truth for one list and Dan's change
would have had to be made in both.

⚠️ **The reuse guard now tracks CITIES, not bowl names, and must stay that way.**
History is not rewritten, so a 2037 box score says "Steampower Bowl" for the site the
pool calls the Steam Bowl, and "Lumber Bowl" means Burke Bay in 2036-37 but Port Logan
from 2038. Name matching silently stopped working the moment the renames landed -- the
2037 semifinal would have gone back to Coachville, which had already hosted a
quarterfinal. The city is the invariant.

**Applied by hand, outside this session:** `state/universe.pkl` already had the Burke Bay
drop and the Wharf->Lumber rename when `rename_bowls.py` first ran (it left
`universe.pkl.pre_bowlpool`, written 15:19:17, a minute before Dan gave the instruction).
`rename_bowls.py` is therefore keyed on city and idempotent, and completed the two
remaining renames. Pre-change copy at `state/universe.pkl.pre_bowl_rename`. Note the arithmetic:
2 semifinal slots into 6 bowls is exactly a 3-season cycle, which is why six is the
number that fits the rule; seven gives alternating 3- and 4-season gaps. Also note that
exact 3-season periodicity on six bowls forces a fixed partition into three pairs, so
the two semifinal bowls would always be the same partners.
Apply from 2038; the 2037 semifinals stand on nearest-unused (Tinsel, Wharf).


### 🅿️ PARKED FOR THE OFFSEASON: conference title game venues
Dan: "We'll go over conference title venues during the offseason." The open item is the
six 2035 P6 venues — Harbor Lights Field, Meridian Field, Salt Flats Coliseum, The
Crucible, The Foundry, The Palisade — which exist only in the 2035 box scores and
`schedule_view_s10.json`. Since 2036 `ccg.py` has drawn title-game sites from
`committee.assign_venue`, i.e. the bowls. Options to put to him then: recover the six,
invent a new dedicated set, or leave the title games on the bowls. Do not change
`ccg.py` before that conversation.

### 🏆 Championship host roll — verified and published
`committee.champ_venue(season)` = `host_cities[(season + 1) % 15]`, a fixed 15-city roll
in `U["host_cities"]`. Verified against the box scores everywhere verification is
possible: 2035 Diamond City and 2036 Sarkady both match. 2026-2034 cannot be checked
because venues were not stored before 2035 (already disclosed), and the anchor for those
-- 2033 Denning, 2034 Perth -- is Dan's canon, not recovered logic.
Next fifteen: 2037 Lornaman, 2038 Billiataho, 2039 El Latigo, 2040 Fiota Bay,
2041 Ediville, 2042 Burke Bay, 2043 Coachville, 2044 Port Logan, 2045 Stamford,
2046 Kirkwood, 2047 San Saltadac, 2048 Denning, 2049 Perth, 2050 Diamond City,
2051 Sarkady, then back to Lornaman in 2052.

**Two open items for Dan, neither touched:**
1. Six of the fifteen host cities are also bowl cities, so in those years one city hosts
   both a quarterfinal and the title game: 2038 Billiataho (Copper), 2041 Ediville
   (Star), 2043 Coachville (Steam), 2044 Port Logan (Lumber), 2045 Stamford (501),
   2046 Kirkwood (Redwood). The bowl rotation could be made to skip the title city, at
   the cost of breaking the exact three-season semifinal cycle.
2. **Burke Bay is still on the championship roll for 2042** even though its bowl was
   dropped in 2037. Possibly good lore -- a city that keeps the title game and loses its
   bowl -- or possibly wants the roll edited too.

### ❌ RETRACTED: the championship "host-city rotation" was never Dan's
Dan asked whether he decided the title-game sites. **He did not.** `champ_venue` held a
15-city roll stepping one city per season, written after the 2035 container reset and
disclosed in its own docstring as "a reconstruction, not recovered logic." Worse than
unsourced -- **contradicted by the record**:
  * 2026 was played at **Sarkady**; the roll says Ediville.
  * 2027 was played at **Lornaman**; the roll says Burke Bay.
It reproduced 2035 and 2036 only because it was fitted to them. And the 2033 Denning /
2034 Perth anchor its comment cited as canon is **unverifiable** -- neither season has a
venue stored anywhere in the project. That anchor should never have been presented as
canon. Everything built on the roll (the 2038-2052 table given to Dan earlier this
session, the Burke Bay and double-duty observations) is void.

**NEW RULING (Dan, 2037): title-game sites are AWARDED in five-year blocks. There is no
rotation.** `champ_venue` is now a pure lookup in `U["champ_sites"]` and **raises** for
an unawarded season rather than inventing one. `committee.champ_sites_awarded()` prints
the published schedule. `U["champ_site_candidates"]` carries the 15-city bid pool
(formerly `host_cities`).

Awarded so far, and this is ALL of it -- every entry taken from a stored box score:
| 2026 | Sarkady, Barhold | | 2027 | Lornaman, Ekralund |
| 2035 | Diamond City, Phangrine | | 2036 | Sarkady, Barhold |
**2028-2034 have no venue stored and are deliberately left blank.** Do not backfill them
without Dan.

⚠️ **2037 IS NOT AWARDED, and `run_champ` will now stop until it is.** Dan has to award
2037 and the next block before the title game can be played.

### 🏆 CHAMPIONSHIP SITES — AWARDED (Dan, 2037). This table IS the canon.
`U["champ_sites"]`, written by `award_champ_sites.py`. Every state validated against
`U["state_coords"]` before writing. **No rotation, no formula** --
`committee.champ_venue` is a lookup and raises for an unawarded season.

| 2026 Sarkady, Barhold | 2033 Stanton City, Stanton | 2040 Stamford, Ciarralotta |
| 2027 Lornaman, Ekralund | 2034 Burke Bay, Dove Island | 2041 Charlesville, Vaughn Bay |
| 2028 Perth, Eona | 2035 Diamond City, Phangrine | 2042 Palm Creek, Natzumakis |
| 2029 San Saltadac, Orlot | 2036 Sarkady, Barhold | 2043 Canesta, Kaji Daun |
| 2030 Port Logan, Fiota | 2037 **El Latigo, Skeenerland** | 2044 Coachville, Stanton |
| 2031 Ediville, Natzumakis | 2038 Fiota Bay, Fiota | |
| 2032 Denning, Diveo | 2039 Chapel Rock, West Hatesei | |

Unbroken 2026-2044. **Next award block is 2045 onward** -- `run_champ` will stop dead at
the 2045 title game until Dan awards it, which is the intended behaviour.

Five cities new to the bid pool: Stanton City (Stanton), Chapel Rock (West Hatesei),
Charlesville (Vaughn Bay), Palm Creek (Natzumakis), Canesta (Kaji Daun). Note two host
cities share a name with a programme -- Chapel Rock and Fiota Bay are also FBS teams.
That is fine and already had precedent (Fiota Bay was in the original pool), but anything
keyed on bare names must not conflate city and school.

**Venues written onto title-game box scores that had none.** 2028-2034 never stored a
venue, so those seven EMPTY fields were filled with the sites Dan declared. 2026 and 2027
survived only in `state_s3_archive/games_db.pkl`, in the old `"City, State"` format, and
were carried into the live database as `"City (State)"` after checking the teams and
scores matched exactly. Verified afterwards: not one result field changed anywhere in
11,609 games, and all eleven title games now carry a venue. Pre-change copies at
`state/games_db.pkl.pre_champ_backfill` and `state/universe.pkl.pre_champ_awards`.


### 📐 RULE (Dan, 2037): a title game may use a rotation bowl's city ONLY in a year that
bowl hosts a QUARTERFINAL
A semifinal city, or a bowl sitting idle that year, is not an acceptable title site.
Audited every awarded season 2026-2044 against it: **no violations.**
  * 2040 Stamford -- the 501 Bowl is a 2040 quarterfinal site. Allowed.
  * 2044 Coachville -- the Steam Bowl is a 2044 quarterfinal site. Allowed.
  * 2034 Burke Bay -- home of the DEFUNCT Lumber Bowl, not a rotation venue at all.
  * 2030 Port Logan and 2031 Ediville are bowl cities but pre-2038, when there was no
    rotation, and both games are long played. The rule does not reach them.
Re-run the audit on every future award block before writing it.

### Overrides applied this turn
* **2037 semifinal sites switched** at Dan's call: Orlot-Barhold to the **Lumber Bowl**
  (Port Logan, Fiota), Ranroman State-Ranroman to the **Star Bowl** (Ediville,
  Natzumakis). The distances support it -- Port Logan is 277 from Barhold against
  Ediville's 356 -- and it puts the Ranroman derby at a site exactly 89 from both
  campuses. Pinned through a new `P["venue_override"][tag]` hook in `_neutral_round`
  (a list of bowl names, one per pair in order, validated for length), so a ruling can
  override a computed assignment without anyone editing the assignment logic.
* **2037 and 2038 title sites swapped**: 2037 is **El Latigo, Skeenerland**; 2038 is
  **Fiota Bay, Fiota**. Backup at `state/universe.pkl.pre_3738_swap`.

## 🏆 2037 CANONIZED — Ranroman State, national champion
**Ranroman State 49, Barhold 10** at El Latigo, Skeenerland. Fourth title (1975, 2007,
2034, 2037); back-to-back finals after losing the 2036 semifinal. Barhold's second
runner-up (2018, 2037). Both finished 12-4; the field's 9 and 14 seeds.

**RULING CONFIRMED (Dan, 2037):** awards are determined by the regular season and the
conference title games, nothing after. The `award_state` fix held -- the Ryskamp went to
**Efua Nagarajan** (Crayellan), whose season ended in the quarterfinals, exactly as the
basis requires. Canonized: Nagarajan (Ryskamp), Henrik Rothholz (DPOY),
Lakshmi Balamoorthy (FoY), Coastal Ranroman / **Hartmut Kanzaki** (CoY).

**RULING (Dan, 2037): the Ryskamp nomination pools stay at week 6 and week 10.**
Twenty named at the week-6 checkpoint, cut to ten at week 10, then the finalists -- each
a strict subset of the one before. Binding, not advisory. 2037 ran without them (the
checkpoints were missed and could not be reconstructed; see above), so **2038 is the
first season the pools must actually be run.** Do not miss the week-6 checkpoint:
the pool cannot be rebuilt after the fact.

Also corrected: the `committee.py` header comment still said "Seven neutral bowl sites".

## 🐛 DIAGNOSED, NOT YET FIXED: possessions are reset at the quarter break
Found while answering "should scoring go higher than 24.4?". **It should not — the engine
never reached 24.4.**

2037 by phase (the week-4 fix was forward-only):
  * weeks 0-3, pre-fix : 21.46 pts/team
  * weeks 4-14, post-fix: **23.37** pts/team   (target 24.40, short by 1.03)
  * postseason          : 24.19

The cause, in `pbp_engine.simulate_game`'s main loop. When the clock expires mid-drive,
`drive()` returns `"clock"`. That skips the `if result != "clock"` block, so `next_spot`
is never set -- and it was already popped by `nxt = state.pop("next_spot", None)`. The
next iteration does `_ns = state.get("next_spot")`, finds nothing, falls through to
`if not isinstance(_ns, int): _ns = kickoff_spot()`, and calls `drive(receiver, _ns)`.
`drive()` then does `state["spot"] = start_spot; state["down"] = 1; state["dist"] = 10`.

So the team keeps the ball -- correctly -- but **the ball is moved to a kickoff spot and
the down resets to first.** Measured over 722 post-fix games:
  * 943 occurrences, **1.31 per game** (ends of Q1 and Q3; the Q2->Q3 break is halftime,
    where a kickoff is correct, and is excluded)
  * the ball moves backward **24 yards on average**, median 23
  * **58% happen in scoring range or better, 26% in the red zone**
Worst observed: Costique had the ball on the opponent's 6 at the end of Q3 and resumed on
its own 36. Chapel Rock reached the opponent's 12, came out of the break on its own 20,
and punted. This is not a logging artifact -- the drive OUTCOMES follow the reset.

Rough expected-points arithmetic puts the cost near **0.9 points per team per game**,
against a measured shortfall of 1.03. **One bug plausibly explains the whole gap**, which
would mean 24.4 is correctly calibrated and the engine simply was not delivering it.

**FIXED (Dan approved, 2037).** `drive()` takes an optional `resume=(down, dist)`; when
the clock expires mid-drive in Q1 or Q3 the loop stashes `state["_resume"] = (spot,
(down, dist))` and the next iteration resumes the same possession from it instead of
calling `kickoff_spot()`. The Q2->Q3 break deliberately carries nothing, because the
second half opens with a kickoff. Pre-fix engine kept at
`pbp_engine.py.pre_qbreak_fix`.

**A/B measured on an identical slate with identical seeds** (`sandbox_scoring.py`, which
plays games through `E.simulate_game` and writes nothing -- no database, no state, no
rosters; use it for any future engine change):

| | pts/team | quarter crossings losing >10 yds |
|---|---|---|
| before | 23.09 | 381 of 558 (68%) |
| after  | **24.76** | 6 of 534 (1%) |

**+1.67 pts/team, against my predicted 0.9.** The estimate was low by nearly half: I
costed the lost field position but not the lost down-and-distance, and a drive that was
2nd-and-3 on the opponent's 25 was being handed back as 1st-and-10 at its own 25 --
losing the down state as well as the yards. Worth remembering that expected-points
arithmetic on field position alone understates this class of bug.

24.76 sits 0.36 over the 24.40 target, inside one standard error for 600 team-games
(~0.57), so **the target was correctly calibrated all along and is now actually being
met. No change to it.**

Verified alongside: halftime still opens with a kickoff (mean second-half starting spot
29.9, nothing leaking across the break); 0 of 220 continuing possessions now lose ground
at the Q1->Q2 or Q3->Q4 break (mean +4.9 yards, i.e. they gain on the play as expected);
shutouts 2.1%, no implausible box scores in 120 games. A residual 6 of 534 crossings
still lose ground -- small enough to be legitimate (a penalty or turnover logged across
the boundary) and not chased.

## 🔭 BUILT: scouting and dynamic play-calling (`scouting.py`)
Dan, 2037: build defensive and offensive scouting. Three mechanisms, every input read
from the universe or the rosters -- no new player attributes, nothing invented:

**1. Identity** (`scouting.Identity`) -- what a team actually is.
  * `pass_lean`: off-scheme pass bias, plus a personnel read (QB arm against RB legs,
    pass blocking against run blocking). Positive = built to throw.
  * `front` = `run_def()`, `cover` = `coverage()` plus the def-scheme coverage term.
  * `soft_vs_run` = (cover - front)/3. Positive means the back end is the strength and
    the front is the way in.

**2. Game plan** (`Scout.__init__`) -- set pre-game off the OPPONENT's identity.
  * The offence shifts `pass_prob` toward whichever half of that defence is softer.
  * A blitz-heavy opponent draws slightly more passing AND the quick game
    (`need_chunk` suppressed inside 8 yards, so throws come out faster).
  * The defence commits toward what the offence is built to do. Right guess takes yards
    away, wrong guess gives them up, symmetrically -- a gamble, not a free upgrade.
    Applied to the run through the `_carry` base and to the pass through `D.coverage()`.

**3. Adaptation** (`Scout.observe` / `my_success`) -- re-read every play from THIS game.
  The defensive commitment drifts toward the offence's observed run/pass tendency, and
  the offence drifts toward whichever of its own two attacks is over-performing today.
  This is the "how are they competing this week" half of Dan's question.

Everything is scaled by the relevant coordinators facing each other
(`_skill_edge(mine, theirs)`), SIGNED -- so an out-coached OC attacks the wrong half and
an out-coached DC commits the wrong way. Matched coaches cancel. Deterministic: the
module draws no randomness.

### Two flaws in my own first pass, both found by measurement
1. The plan scale factor read `(0.45 + 0.55*max(0, off_edge) + 0.25)` -- a stray `+0.25`
   put its floor at 0.70, and `max(0, ...)` meant a worse OC was never punished. Every
   offence got most of the benefit regardless of matchup. Now signed, 0.35 + 0.65*edge.
2. "Go where the yards are" compared raw pass YPP to raw run YPP. Measured on 2037 canon,
   pass plays average **7.77** yards and runs **3.98** -- a 3.79-yard structural gap. So
   the rule pushed EVERY offence toward the pass in EVERY game: a systematic bias dressed
   as a matchup read. Each phase is now judged against its own normal (`NORM_RUN_YPP`,
   `NORM_PASS_YPP`), i.e. "which of our attacks is beating what it should do today".

### Calibration
Scouting added ~1 pt/team, because offences that can find a weakness score more.
`CAL_COMP_BASE` lowered 0.055 -> 0.030 to absorb it, swept on the sandbox
(0.055 -> 25.24, 0.040 -> 24.81, 0.030 -> 24.45, 0.022 -> 24.13). Final: **24.77
pts/team on 300 games**, the same as the pre-scouting baseline. Scouting changes WHO
scores, not how much the league scores.

### ⚠️ HONEST RESULT: scouting did NOT fix parity
300-game A/B, identical slate and seeds:

| | pts/team | slope (pts per unit talent) | corr | favourite wins | one-score | blowouts at gap>0.6 |
|---|---|---|---|---|---|---|
| old, blind | 24.76 | 10.79 | 0.351 | 63.7% | 40.7% | 34.0% |
| new, scouting | 24.77 | 10.47 | 0.322 | 65.3% | 39.3% | 29.8% |

+1.6 points of favourite win rate, slope and correlation marginally DOWN. All inside
noise. That is a predictable consequence of the design: scouting is a contest, both
sides do it, and the effects largely cancel. It adds texture and realism; it is not the
parity lever.

**Where parity actually lives**, measured at neutral sites by talent gap (420 games):

| talent gap | games | favourite wins | `season.win_prob` says |
|---|---|---|---|
| 0.0-0.3 | 255 | 55% | 57% |
| **0.3-0.6** | 101 | **50%** | **70%** |
| **0.6-1.0** | 36 | **67%** | **81%** |
| 1.0+ | 28 | 86% | 90% |

Small and very large gaps are calibrated. **The middle is flat**: a 0.3-0.6 talent
advantage wins exactly half its games when the engine's own win probability expects 70%,
and 0.6-1.0 wins 67% against an expected 81%. That is the coin-flip feeling, and it is
a conversion problem between talent and yards in the mid-range, not a play-calling one.
Next parity step: the `eff_edge` -> yardage coefficients, in that band specifically.

## 📉 THE REAL SYMPTOM: Roiland never produces elite records (Dan, 2037)
Dan's framing is better than the parity metrics and should be the target from here on,
because record distribution is MULTIPLICATIVE and therefore a far more sensitive
instrument than any single-game statistic.

**Twelve seasons. One undefeated regular season** (Rogaela State, 2033 -- and it then
lost in the playoff, so Roiland has never had a full-season unbeaten team). Teams at 0 or
1 loss, by season: 1, 2, 2, 0, 0, 3, 2, 3, 3, 3, 4, 1.
Real CFB, 1991-2023: 34 teams finished a FULL season unbeaten, about 1.03 a year, and
regular-season unbeatens run higher still.

2037's top 15 by final rating: 8-4, 9-3, 10-2, 9-3, 10-2, 8-4, 11-1, 10-2, 8-4, 10-2,
10-2, 9-3, 7-5, 9-3, 7-5. **Top 10 mean 2.7 losses, top 25 mean 3.4, and the #1 rated
team went 8-4.** Real CFB's top 5 rarely exceed 1 loss and its top 15 rarely exceed 3.

### The arithmetic that connects it to the margin problem
Over a 12-game season, with per-game win probability p:

| p | P(12-0) | expected losses | P(<=1 loss) |
|---|---|---|---|
| 0.95 (real elite) | 54.0% | 0.6 | 88.2% |
| 0.93 (real elite) | 41.9% | 0.8 | 79.7% |
| 0.90 | 28.2% | 1.2 | 65.9% |
| 0.85 | 14.2% | 1.8 | 44.3% |
| **0.805 (Roiland's best bucket)** | **7.4%** | **2.3** | **28.9%** |

Roiland's best teams win at 80.5% where real elites win at 93-95%. In one game that gap
is nearly invisible; over twelve it is the difference between 12-0 and 9-3. This is why
record distribution is the right target.

### A SECOND, independent cause: Roiland's schedules are harder than real CFB's
  * 2037 top-10 teams played a mean of **6.4 of 12 games against top-50 opposition**.
    Rogaela State played **1 of 12** -- and produced the league's only good record, 11-1.
    That single data point is the whole thesis.
  * **Subdivision games: 0.41 per FBS team, and 90 of 152 teams play NONE.** Nearly every
    real FBS team plays at least one FCS opponent. Roiland's non-conference slate is
    tougher than real CFB's by roughly one guaranteed win per team.
So part of the depressed records is legitimately earned and is a SCHEDULING question, not
an engine one. Fix the engine first; put the scheduling question to Dan separately.

### Proposed target, replacing the per-game framing
  * 1-3 undefeated regular seasons a year
  * top 5 averaging <= 1.2 losses; top 15 rarely above 3
  * elite teams' per-game win rate ~0.92-0.95 against their actual schedule
⚠️ Caution to raise with Dan BEFORE tuning: those losses do not vanish, they relocate.
If the best teams stop losing, the middle absorbs it and will look worse than he is used
to -- 5-7 loss teams where there are now 4-5 loss teams. That is correct football but it
is a visible change to the league's texture.

## ✅ RESOLVED, and it was NOT the engine. A correction to my own earlier diagnosis.
I told Dan the engine under-converts talent into margin and that the mid-range was flat.
**That was wrong, and the measurement that settled it is this:** bucket the same 881 canon
2037 games by END-OF-SEASON NET RATING instead of by talent gap and the favourite win
rate reads **51% / 70% / 79% / 90%** across widening gaps. That is a healthy,
real-CFB-shaped separation curve. The simulation distinguishes teams properly. What was
broken was the thing doing the predicting.

`season._talent` is the mean ability of a roster's top 22 -- position-blind,
coaching-blind, depth-blind -- and correlates only **0.669** with what teams turn out to
be. Four alternatives were tried and all landed in the same band:

| proxy | corr with net rating |
|---|---|
| current: top-22 mean ability | 0.669 |
| starters, equal weight by position | 0.652 |
| the engine's own unit strengths, equal | 0.665 |
| **unit strengths, football-weighted** | **0.700** |
| that plus coaching | 0.697 |
| 14-predictor OLS (overfit: negative TE, negative OC) | 0.752 |

So roughly half the variance in a season's net rating is schedule, form, injury and
chance that NO pre-game roster measure can see. There is no better proxy to swap in --
the ceiling is real. The honest fix is for the model to claim only the confidence it has
earned, so `win_prob`'s coefficients were refitted by joint maximum likelihood on the 881
canon games:

  * gap coefficient **1.85 -> 1.480**
  * home-field coefficient **0.16 -> 0.050**. Home teams won **54.7%** of canon 2037
    games; 0.16 was worth far more than that. Fitting the gap alone left a 7-point bias
    in the middle buckets which turned out to be the home term over-promising.
  * log-loss 0.6610 -> 0.6452

Calibration on canon, favourites' predicted vs actual win rate: **-8.4 points before,
+0.2 after.** Every bucket now within about a point except the two thinnest
(80-90% n=46 at -4.1, 90-100% n=8 at +8.5). Backup at `season.py.pre_winprob_recal`.

### Season shape: already at target, from the quarter-break fix
Four sandbox seasons on the fixed engine (`season_shape.py`, writes nothing), against the
12-season canon average, both ranked BY RECORD so the comparison is like for like:

| | undefeated/yr | 0-or-1-loss teams | top-5 mean losses | top-15 mean losses | top-15 worst | pts/team |
|---|---|---|---|---|---|---|
| canon, 12 seasons | **0.08** | 2.0 | 1.62 | 2.36 | 3-4 | 23-25 |
| fixed engine, 4 seasons | **0.75** | 2.5 | **1.35** | 2.32 | **3 every year** | 24.62 |
| Dan's target | 1-3 | -- | <= 1.2 | rarely > 3 | 3 | 24.4 |

Undefeated regular seasons went from one in twelve years to three in four. The top 15
never carried worse than a 3-loss team in any of the four. **No margin tuning was needed
or done** -- the quarter-break fix returned the red-zone drives good teams had been
losing, which is where the elite records were going. `CAL_RUN_DAMP` and the `eff_edge`
coefficients are untouched.

Still short of target: top-5 mean losses 1.35 against 1.2, and top-15 mean 2.32 barely
moved. Both are small and neither justifies touching the margin coefficients on four
seasons of evidence. Revisit after 2038 is played, with real canon data.

## 🔄 2037-38 OFFSEASON — Stage 1 of 7 COMPLETE: coaching carousel
Run after the engine changes were committed, so every stage from here is on the fixed
engine. Backups at `state/{season_state,coaches,rosters}.pkl.pre_s13_carousel`.
Stored as `s["carousel_s12"]`.

23 vacancies | 20 head-coach hires | 33 coordinator moves | 12 coordinator raids.
Sources: 9 fired, 7 interims not retained, 3 interims promoted, 3 retirements,
1 head coach poached away.

Notable: **Skirter went 9-3 and lost Andre Hernandez to Tasson (5-7)** -- a rare
downward move by record, driven by the dream-job/alma-mater logic, and Skirter replaced
him with a 2.55 first-timer, the weakest hire of the cycle. **North Hatesei fired Ravi
Kamau at 7-5** and he was immediately hired by Underwood (3-9) while North Hatesei took
Meera Moreau, whom Diveo State had just fired -- a clean two-way retread swap.
Crayellan State's Kayla Rocha retired at 59 after ONE year at 8-4.

Stage 2 of 7 is the draft. ONE STAGE AT A TIME.

### ✅ RESOLVED: conference title game venues (new league rule, Dan, 2038)
**RULE: a conference title game is played in a state that hosts NO team from that
conference**, at one fixed site per conference. Dan chose the cities off the distance
tables; `install_ccg_sites.py` validated every one (state exists; hosts no member) and
wrote `U["ccg_sites"]` with `U["ccg_sites_from_season"] = 13`. All twelve passed.

| conference | site | | conference | site |
|---|---|---|---|---|
| Broad South | Hughes City, South Antiragal | | Brass Belt | Underwood, Hatesei |
| Great Fourteen | Diamond City, Phangrine | | East Forest | Classetto, Harrell |
| Jyras Bay | Queensville, Parchynt | | Evening Star | Verigon City, Verigon |
| Mountain Valley | El Latigo, Skeenerland | | Low Sixteen | Flatting, Ciarralotta |
| Power North | Riverwake, Rogaela | | Southwestern | Niana Vaw, North Hatesei |
| Western Coast | Denning, Diveo | | Vapor Stream | Landon, Far Farris |

`ccg.py` now reads those sites from season 13 and falls through to the old behaviour for
earlier seasons, so 2037 and before stay as played. Backup at `ccg.py.pre_ccg_sites`,
universe at `state/universe.pkl.pre_ccg_sites`.

**Two consequences, both intended but worth remembering:**
1. **The bowls are now free of title games entirely.** The 2036-37 drift -- `ccg.py`
   drawing from `committee.assign_venue`, i.e. the playoff bowl pool -- is over. That
   drift is why the Tinsel Bowl's first ever appearance was a 2037 conference final.
2. **L6 title games are no longer campus-hosted.** They were played at the #1 seed's home
   with full HFA; all twelve are now neutral with `hfa = None`, so the L6 top seed loses
   an advantage it has had since the format began. Dan named a site for all twelve
   conferences, so this is deliberate, but it is a real competitive change for the L6.

Three of the twelve cities (Diamond City, El Latigo, Denning) are also in the
championship host pool, and three (Diamond City, Queensville, Underwood) share a name
with a programme -- allowed, with precedent in Fiota Bay and Chapel Rock.

NOTE: the six 2035 P6 venues (Harbor Lights Field, Meridian Field, Salt Flats Coliseum,
The Crucible, The Foundry, The Palisade) were NOT revived and now exist only in the 2035
box scores, as historical sites. Leave them there.

## Stage 2 of 7 COMPLETE: the 2038 draft
`run_draft()` does not persist, so the stage is two calls: write
`s["draft_s12"] = {"picks": picks}`, then `D.mark_departures(s, picks, pool)`, which is
what flags `_leaving` and writes `departures_s12`. Same shape as draft_s10/s11.
Backups at `state/{season_state,rosters}.pkl.pre_s13_draft`.

4,059 declared | 210 picks | 119 early entrants drafted | 9 subdivision picks |
0 questionable early declares drafted.
Departures: **2,850 leaving**, 210 of them drafted, and **1,192 withdrew back to school**.

Top of the board: 1. Meiling Virteniy (RB, So, Roosevelt State), 2. Uchenna Leatalo
(TE, Jr, UNN), 3. Chafik Sarvashankar (TE, So, Skeenerland), 4. **Itzel Rochepre
(QB, Fr, Barhold)**, 5. Vikram Rothecker (LB, Sr, Underwood).
Ryskamp winner **Efua Nagarajan went 19th** as a junior early entrant.
Barhold led all programmes with **9 players drafted**; Ranroman had 7.
Positions: WR 34, OL 33, QB 32, DL 24, LB 20, RB 16, CB 16, TE 15, S 14, K 4, ATH 1, P 1.
The OL fix from a previous pass is holding -- 33 drafted against the 12 of 2036.

### ⚠️ NEEDS A RULING: 47 of 210 picks are freshmen or sophomores
This is the "Fr/So draft eligibility" item that has been sitting unruled. Class split:
Sr 81, Jr 72, **So 27, Fr 20**, RS 10. Real NFL eligibility requires three years removed
from high school, so true freshmen and sophomores could not declare at all -- **22% of
this draft would be ineligible** under real rules.

The consequences this year are not cosmetic:
  * **Itzel Rochepre went 4th overall as a FRESHMAN.** He is the quarterback who took
    Barhold from a 14 seed to the national championship game three weeks ago. Barhold
    loses him after one season.
  * **Lakshmi Balamoorthy went 14th, also a freshman** -- the 2037 Freshman of the Year
    and third on the Ryskamp board.
Both are gone from Roiland after one year. If Dan wants real eligibility rules, the bar
belongs in `draft.py`'s declaration step and the fix is forward-only; this draft is
already canon unless he says otherwise. Flagged before stage 3 because the portal and
recruiting both read the post-draft rosters.

## Stage 3 of 7 COMPLETE: the 2038 transfer portal
Backups at `state/{season_state,rosters}.pkl.pre_s13_portal`. Stored as `s["portal_s12"]`.

454 entered | **265 moved** | 189 had no takers and returned to their old locker room.
Classes: So 104, Fr 92, Jr 69 (no seniors -- correct, their eligibility is gone).
Reasons: bigger role 57, closer to home 43, bigger stage 40, change 39, star at a small
school 22, staff turnover 19, didn't fit the new staff 15, sinking programme 13, buried
10, injuries 6, followed a coach 1.
Biggest net gainers: Skeenerland State +7, Kaji Daun +6, Orlot +6. Biggest losers:
David Harrison -7, Hofferteltra -6, Chinolka -6, Trapper Point -6.
Lineman movement is healthy -- 26 OL moved, so the blocking-valuation fix is holding.

### 🐛 STILL BROKEN: coach-following, now with the exact arithmetic
Diagnosed in a previous cycle as "correct but impotent" and never fixed. The 2038 funnel:

| portal entrants | 454 |
| whose coach left | 110 |
| coach's new school was in their pool | 59 |
| **actually followed** | **1** |

**The cause is that following is a WEIGHT NUDGE, not a decision.** Destination is
`rng.choices(pool, weights=[pull(t)**k ...])` over a pool whose MEDIAN SIZE IS 150
SCHOOLS, and the coach's school simply gets its weight multiplied by 3.5 (same side of
the ball) or 2.0. The arithmetic:
  * an average school's share of a 150-school pool: **0.67%**
  * with the 3.5x multiplier: **2.30%**
  * 59 eligible x 2.30% = **1.4 expected follows.** Actual: 1. The feature is working
    exactly as written and the number it produces is noise.
It is worse than that, because the weight is `pull(t)**k` with k = 2.1-3.0, so a
blueblood already outweighs a mid-tier school by 15-20x before the 3.5x is applied.

The narrative cost: **34 players moved specifically BECAUSE of a staff change** ("left
after the staff turnover" 19, "didn't fit the new staff's plans" 15) and exactly one of
them went where their coach went.

Proposed fix, forward only (the 2038 portal is canon): make it a decision rather than a
weight. If a player's reason is staff-driven AND his coach's new school is in his pool,
he follows with a high probability (~0.55), otherwise fall through to the existing
weighted draw; keep a modest multiplier for non-staff reasons. That turns ~34 staff-driven
moves into ~15-19 follows, which is what makes a carousel read as consequential.
Awaiting Dan's call.

### 👀 Watch: positional imbalance in portal movement
CB 45 moved against LB 6, with K 12 and P 16 also high for two-deep positions. Worth a
look if it repeats next cycle -- likely the production function favouring interception
counts over tackle counts, the same class of problem as the OL-valuation bug.

## Stage 4 of 7 COMPLETE: the 2038 recruiting cycle
Backups at `state/{season_state,rosters}.pkl.pre_s13_recruiting`. Stored as
`s["recruiting_s12"]`. `recruiting.py`'s `__main__` only sizes the class, so the stage is
assembled by hand: needs from roster size minus `_leaving`, `national_class_size`,
`make_class`, `run_recruiting`, then write the record and save.

National class **2,736** (fixed-size rule holding: 2,800 with 2.5% jitter) |
**2,465 signed** | 271 unsigned.
Stars: 5* 13 | 4* 274 | 3* 958 | 2* 1,094 | 1* 397.
**L6 share of blue-chips: 4.9%**, against the canon series 4, 4, 3, 2, 3.2% -- the tier
term in `cap_for` is doing its job.
Ten programmes maxed a 6-blue-chip haul. The thirteen five-stars went to Ranroman State
(QB Siegfried Faletoa, 8.46), Eona, Orlot, Kaji Daun, Ranroman, Diamond City, Central
Stanton, Rogaela State, North Hatesei, Leafette, Hatesei, Pistolheart and Crayellan.

### ✅ The blue-chip cap leak did NOT fire -- but it is still latent
Checked directly: **0 teams signed more blue-chips than their cap.** The reason is
arithmetic, not a fix:
  * total blue-chip cap capacity across all 152 programmes: **293**
  * blue-chips in this class: **287**
Capacity exceeded supply, so phase 1 absorbed every 4-5* and phase 2 never saw one. The
leak -- `avail` in phase 2 being `signed is None`, which includes unsigned blue-chips,
with weights of `stars**2` and no cap check -- is real and will fire in any year the
class carries more than ~293 blue-chips, or where need at the top of the order runs out
before the pool does. Worth fixing on its own schedule rather than waiting for the year
it bites.

### 🐛 CONFIRMED with numbers: the TARGET=62 / ROSTER_MIN=63 mismatch
Recruiting fills to `TARGET = 62`; `roster_final.ROSTER_MIN = 63` then pads with
generated walk-ons. Measured after this cycle's signings:
  * roster sizes: mean 62.0, median 62, min 62, max 63
  * **151 of 152 programmes sit at exactly 62, i.e. one below the minimum**
So stage 6 will manufacture **one walk-on for essentially every team in the league, every
single year** -- about 152 phantom players a cycle, none of them recruited, purely to
cover a one-player disagreement between two constants. Either raise TARGET to 63 or lower
ROSTER_MIN to 62; the first is the better choice, since the spots should go to real
recruits out of a class that left 271 unsigned. Forward only. Needs Dan's call.

## Stage 5 of 7 COMPLETE: 2038 development
Backups at `state/{rosters,season_state}.pkl.pre_s13_dev`. Stored as
`s["development_s12"]`. 9,810 players developed, mean growth +0.199.
By class: Fr +0.506, So +0.199, RS +0.168, Jr +0.111, Sr 0.0 (correct -- they are gone).
322 breakouts, 82 busts.

### 🐛 DIAGNOSED: `r_coach` is not measuring coaching
The reported staff-quality-to-growth correlation fell **0.609 (2036) -> 0.566 (2037) ->
0.170 (2038)** against a canon norm of ~+0.49. Two separate causes, both measured:

**1. The statistic includes players who are leaving college.** It is computed over every
player on the roster, and 2,850 of the 9,810 developed this cycle are flagged `_leaving`
-- seniors and drafted underclassmen who grow 0.0 and will be deleted in stage 6.
Recomputing over only the players who are actually STAYING: **r = 0.170 -> 0.283.**

**2. What is left is swamped by class composition.** Growth is almost entirely set by
class (Fr 0.506, So 0.199, Jr 0.111, Sr 0.0), so a team's mean growth mostly reports its
class mix, not its staff. Share of the roster that is seniors against team growth:
**r = -0.392**, i.e. roster age predicts "development" about as strongly as coaching does.
Restricting to one class at a time removes composition entirely and the coaching signal
is intact and healthy:

| class | r with coach_mult | teams | mean growth |
|---|---|---|---|
| Fr | **+0.437** | 136 | 0.504 |
| So | **+0.376** | 152 | 0.199 |
| Jr | +0.219 | 141 | 0.113 |

**So the engine is fine and the diagnostic is wrong.** Coaching genuinely drives growth
at +0.38 to +0.44 within a class; the headline number is a composition artefact. The
2036 and 2037 figures of 0.609 and 0.566 were not "better development" -- they were the
same artefact pointing the other way in years whose departure volume happened to
correlate differently with staff quality. **No player ability needs changing.**

Fix, forward only: compute `r_coach` over non-leaving players, within class, and report
it per class rather than as one league number. Two lines in `development.py`'s summary
block. It changes no simulation output -- only what the number means. Awaiting Dan.

Also worth doing while in there: development currently grows the 2,850 players who are
about to be deleted in stage 6. Harmless to canon but pointless work, and it is what
makes the statistic lie.

## Stage 6 of 7 COMPLETE: 2038 roster finalisation
Backups at `state/{rosters,season_state}.pkl.pre_s13_rfinal`. Stored as
`s["roster_final_s12"]`.

`{'departed': 2850, 'recruits_added': 2616, 'walkons': 0, 'floor_fills': 373,
'trimmed': 1, 'min': 63, 'max': 70, 'total': 9948}`

**walkons: 0.** The TARGET 62->63 change did exactly what it was supposed to -- compare
`walkons` of 3 in 2036 and 18 in 2037, and the ~152 this cycle would have manufactured
before the fix. Rosters: min 63, median 65, max 70. All `_leaving` flags cleared, 0 left.

### 🐛 DIAGNOSED: the recruiting positional mix does not match the position floors
373 emergency bodies were still needed, and **1,162 walk-ons now sit on rosters
league-wide -- 11.7% of every player in Roiland.** That is not a roster-size problem, it
is a MIX problem. `recruiting.POS_WEIGHTS` against the share each position's floor
demands:

| pos | recruited | floor | floor share | gap | |
|---|---|---|---|---|---|
| **OL** | 13.0% | 8 | **17.4%** | **-4.4pp** | badly under-recruited |
| LB | 10.0% | 5 | 10.9% | -0.9pp | |
| TE | 6.0% | 3 | 6.5% | -0.5pp | |
| **RB** | 10.0% | 3 | 6.5% | **+3.5pp** | over-recruited |
| QB | 8.0% | 3 | 6.5% | +1.5pp | |

Offensive line is the whole story: a roster needs 8 and the country recruits 13% of a
class for a position that should be 17.4% of it. Measured on real (non-walk-on) bodies
after finalisation, OL is short by **122 across 55 programmes** -- more than any other
position -- with S short 109, LB 101, P 98, K 71. Running backs are over-recruited by
almost exactly the amount OL is short.

This is the same family as the two OL bugs already fixed (draft valuation, portal
valuation): offensive linemen are structurally undervalued everywhere in the bundle
because they generate no box-score statistics. This is the recruiting instance of it.

Fix, forward only: move ~4pp from RB and ~1pp from QB into OL, so the class mix matches
the floor shape. It would reduce the 373 annual emergency bodies and stop the walk-on
population compounding. Awaiting Dan -- that is now four forward-only fixes queued
(portal coach-following, blue-chip cap leak, the `r_coach` statistic, and this).

---

## 2038 non-conference board — PARTIAL, Dan to finish

Saved: `state/noncon_s13_partial.json` (Dan's export, 2026-10-08 evening). He said he
would come back and finish it. **Do not pass this to `install_schedule.py`** — it is
47 of ~250 games and `complete: false`.

Board payload rebuilt for season 13 by `export_schedule_board.py`
(`state/schedule_board.json`); page published from `schedule_office_template.html`
at https://claude.ai/artifact/87Wf5T3tLQfKe3CXzMbXHf — republish the same file path
to update it in place.

State of the board as given:

* **81 of 456 FBS dates filled**, 375 open. 50 of 152 programmes touched; 15 of them
  complete at 3/3.
* 47 games: 6 locked cross-conference rivalries (hosts alternated off 2037),
  13 subdivision guests, 28 other FBS pairings.
* **Clean on every hard rule**: no same-conference pairing, no programme over 3 slots,
  no duplicate pairing, no subdivision programme invited twice.
* One blocking item, and it is an artefact of the board being half-built: the
  subdivision guest count is **odd (13)**, which would leave one FBS date unpairable.
  It resolves itself as he fills in — the total only has to come out even at the end.
* Three programmes host all three non-conference games (Costique, Keeper,
  Southern Tengus) — 7-8 home dates once conference play adds 4-5. Worth a look, not
  an error.
* **Southern Tengus is no longer stranded.** It is the one programme in 2038 with no
  free conference partner in week 14 (Power North has exactly one unpinned team and it
  is them), so one of its three non-conference opponents had to be free that week.
  Barhold Valley and North Canesta both are, so the calendar can close.
* Odd-count conferences still needing a bridge: Great Fourteen (5), Western Coast (3),
  East Forest (11). 7 of Dan's games already pair two week-14-free programmes, so there
  is room. `conf_builder` places those weeks itself — in 2037 it put five extra
  cross-conference games into week 14 to balance the parity. Nothing for Dan to set.

Queued behind this: a **Power North conference-schedule builder** for Dan to drive
himself (his words: "I want to try building one conference schedule myself. Let's start
with the power north"). Needs the non-conference board finished first, since conference
dates are placed around it.

---

## 2038 rule change: week 1 may be a bye

Dan, 2026-10-08: "It is okay from now on for week 1 to be a bye week."

**Rivalry week (14) is now the only full slate.** Forward only — 2037 and earlier stay
as played, where weeks 1 and 14 were both compulsory.

Two consequences worth stating, because neither is obvious:

1. **Weeks 0 and 1 are now adjacent for the no-consecutive-byes test.** While week 1 was
   compulsory, a programme could take week 0 off and the next bye could be week 2
   without ever being back-to-back. It can now bye both 0 and 1, which is illegal, and
   anything that places byes has to test the pair.
2. **Week 14 carries more weight.** It is the only week every programme must play, so
   the four conferences with no locked rivalries -- Vapor Stream, Low Sixteen,
   East Forest, Southwestern -- have to fill all fourteen of their week-14 slots out of
   ordinary conference and non-conference play. The Conference Office's filler had to be
   taught to go after week 14 FIRST; without that it spent the date like any other and
   stranded those four conferences every time.

**Done:** `export_conf_board.py` (`FULL_WEEKS = [14]`) and the Conference Office.

**STILL TO DO -- `conf_builder.py` has not been changed and still assumes week 1 is
full.** It is the module `install_schedule.py` uses to build a calendar automatically,
so until it is updated an auto-built season will differ from a hand-built one. The
places that need it: `BYE_OK` (line 34), the `bye_before` feasibility check (~line 70),
`assign_weeks` which matches week 14 and then week 1 as full slates (~line 243), and the
audit at line 657 that fails a board for byes in weeks 1 or 14. Leave it until Dan says
whether he is hand-building all twelve conferences from now on, since if he is, that
path may not be worth maintaining.

## Conference Office — all twelve conferences

`state/conf_board.json` via `export_conf_board.build_all()`; page from
`conf_office_template.html`. Published at https://claude.ai/artifact/YXQd4pYUooTZaUb9tUs3yS

One league-wide model, not twelve conference-shaped ones. The thing that forced it:
**a non-conference game belongs to two programmes in two different conferences.** Held
once and shared, so placing it while editing Power North lands it in East Forest too.
Copying it per conference would have let the same real fixture sit in two different
weeks depending on which conference happened to be open.

Slate generation per conference picks which 4 (or 2, or 0) opponents each programme
skips by WEAR -- the pairings played most often in the last five seasons are the ones
dropped. Brass Belt's ten teams make 9 games a forced round robin, so nothing is
skipped there. Hosts alternate off 2037 and are then balanced by augmenting path to
land on the only legal shape (e.g. 7 on four and 7 on five for a 14-team conference).

Filler measured over 6 league runs: 6/6 complete and fully legal, 128ms-1.1s, week 0
landing at 14% of the league playing, which is canon 2035's figure.

---

## 2038 conference calendar — PARTIAL, Dan to finish

Saved: `state/conf_sched_s13_partial.json` (Dan's export, 2026-10-09 01:09). He said he
would finish it later. **Not installable yet** — 657 of 980 games still have no week.

Verified against the live database (`conf/s13`, version 495, saved 01:09:48): 980 rows,
zero disagreements, 323 placed on both sides. The page is saving correctly, so the
export was a courtesy copy rather than the only one.

Three conferences are **complete and clean**: Power North, Jyras Bay, Great Fourteen —
63 games each, all 42 of their programmes holding a legal 15-week calendar.

| conference | placed | of |
|---|---|---|
| Power North | 63 | 63 |
| Jyras Bay | 63 | 63 |
| Great Fourteen | 63 | 63 |
| Western Coast | 4 | 54 |
| Broad South | 6 | 54 |
| Mountain Valley | 6 | 54 |
| Brass Belt | 1 | 45 |
| Vapor Stream, Low Sixteen, East Forest, Evening Star, Southwestern | 0 | 288 |
| non-conference | 117 | 296 |

**Hard rules clean across all 152 programmes**: no double-bookings, every programme
still holds exactly 12 games, and every finished calendar has three byes, none adjacent
and none in week 14.

Worth remembering when he resumes: a non-conference game is shared between two
conferences, so 117 of the 296 are already placed as a side effect of finishing those
three conferences. The remaining nine conferences inherit those weeks as fixed points.

### UPDATE 2026-10-09 03:58 — the conference calendar is FINISHED

`state/conf_sched_s13.json` — all **980 games placed**, `complete: true`. Supersedes
`conf_sched_s13_partial.json`. Confirmed against the live database (`conf/s13`, version
837): zero disagreements.

Audited clean on every hard rule:
* 152 programmes, 12 games each, no double-bookings
* exactly 3 byes each, none adjacent, none in week 14
* week 14 a genuine full slate — nobody idle
* the fixture list is untouched: every conference still 9 games per team, host spread
  still 4/5 (or 4/5 equivalent), and every locked rivalry still on its locked week with
  its locked host
* 296 non-conference games each hold ONE week across both conferences

Shape against canon: week 0 has 23 of 152 playing (15%, canon 2035 ~14%); conference
play is light in weeks 0-3 and ramps from week 4; 8 programmes took the newly allowed
week-1 bye. 26 soft warnings, all of them 4+ home or road games in a row (worst:
Skirter, 5 road). Nothing blocking.

**NEXT: nothing installs this yet.** `install_schedule.py` takes a non-conference board
and calls `conf_builder.build()` to invent the calendar; Dan has now built the calendar
himself, so it needs a new installer that reads `conf_sched_s13.json` directly —
validate, back up `state.pkl` / `sub_rosters.pkl` / `sub_coaches.pkl`, generate guest
rosters for the 136 invited subdivision programmes, and write `s['sched']`. The
`conf_builder` week-1 change logged above becomes moot if that path replaces it.

### 2038 SCHEDULE INSTALLED — 2026-10-09

`install_hand_schedule.py` (new). The old `install_schedule.py` BUILDS a calendar from a
non-conference board via `conf_builder`; Dan built 2038 himself, so this installs a
finished one instead. Kept separate rather than flagged, for three reasons recorded in
its docstring — chiefly that `conf_builder.audit` still rejects any bye in week 1, which
would have refused a legal 2038 season.

Installed from `state/conf_sched_s13.json`: 980 games (684 conference, 296
non-conference, 136 against guests), 136 subdivision programmes with fresh rosters.
Backups written: `state.pkl.pre_s13_sched`, `sub_rosters.pkl.pre_s13_sched`,
`sub_coaches.pkl.pre_s13_sched`.

The audit was NEGATIVE-TESTED before committing, because an audit that only ever passes
proves nothing. Deliberately corrupted copies were caught in every case: locked rivalry
moved off its week, locked host flipped, locked non-conference game moved, programme
double-booked, fixture deleted, fixture repointed at a new opponent, week 14 left with
an idle programme, byes forced back to back, `bye_before` violated, and conference host
balance broken. One early probe reported "not caught" and was a bad probe, not a bad
check — it flipped games for Hatesei inside Brass Belt, and Hatesei is in the Great
Fourteen.

State now: season 13, `next_week` 0, 0 results, 980 `sched` rows, every programme on the
schedule has a roster. Week 0 = 13 games, week 1 = 93, week 14 = 76.

**GAP WORTH CLOSING: the Conference Office does not enforce `bye_before`.** Will Tech /
Tasson is the only pair carrying it (both must be idle in week 9, ahead of their week-10
game) and Dan's 2038 calendar happens to satisfy it, but the page would have let him
break it. The installer now checks it as a hard failure, so nothing illegal can be
installed; the Office should refuse it at placement time too.

---

## THE SEPARATION PROBLEM — ROOT CAUSE FOUND, 2026-10-09

Dan: "the number of close games with subdivision teams is unacceptable and speaks to all
the problems I've been referring to. I'm starting to feel despair that the separation
isn't happening."

**He is right that separation is not happening. He is wrong about where it comes from,
and so was I — for days.**

### The guest games were a red herring
2038 is the cleanest guest separation in five seasons: +19.3 mean margin, 95.6% FBS
wins, 7 of 45 within a touchdown. Canon: 2037 +16.2 / 83.9% / 32% close, 2036 +15.6 /
90.3% / 31%, 2035 +17.3 / 80.6% / 24%. The 2-18 band recalibration worked; no guest
roster now exceeds the weakest FBS programme (best guest 5.72, FBS floor 6.09). The two
guest wins were a 2.02-talent-gap overtime game and a 1.04-gap game — real tails.

### MY ANALYTICAL ERROR
I previously justified the engine with "bucketing by net rating gives 51/70/79/90, so
the simulation distinguishes teams properly." **That was circular.** Net rating is
computed FROM the season's results, so teams that won a lot have high net ratings by
construction. Measured EX ANTE on talent, a top-10 roster wins **61.8%** of its games.
That reading sent us after engine fixes for days.

### The real decomposition
Head-to-head in a sandbox, free of schedule effects, the engine's curve is only mildly
flat: top beats bottom 89.1% (real CFB ~97%), top beats middle 80.2% (~85%), middle
beats bottom 71.9%. Fitted logistic k = 1.33 against a real-CFB-like k = 1.80.

**The Great Fourteen holds 7 of the top 10 and 13 of the top 25.** Every one of its 14
members is above 7.40 talent; conference mean 7.77 against a league mean 6.96. Six
conferences sit at ~6.46-6.56 with zero top-25 teams. Ranroman State plays 10 of 12
games against 7.5+ opponents. Nobody survives that 12-0.

Expected undefeated teams per season (arithmetic model, validated against a 12-season
sandbox that measured 0.17):

| | current conferences | balanced conferences |
|---|---|---|
| **current engine curve** | **0.17** | 0.98 |
| real-CFB curve | 0.29 | **1.98** |

Target is 1-3. So the engine curve is worth **+0.12** and conference balance is worth
**+0.81** — balance matters about seven times more, and only both together reach target.

Non-conference win rate by conference is STABLE across 2031-2038 (sd 14.5-19.5, no
trend), so this is structural, not drift. The Great Fourteen has led every season at
67-85%.

**Awaiting Dan's decision on direction.** Options put to him: realignment, changing how
recruiting distributes talent, steepening the engine curve, or some combination.

### Prestige is the mechanism — 2026-10-09

Dan asked to see how the Great Fourteen got stacked before choosing a lever. It was
**built that way and then frozen**:

* **prestige <-> talent correlates at r = 0.941** across all 152 programmes. Talent is
  very nearly a deterministic function of a number set when the universe was made.
* **prestige is a fixed INPUT, never an output.** `recruiting.py:107` reads it to set
  recruiting pull; nothing in the offseason writes it back. Thirteen seasons of results
  have not moved it by a point.
* The Great Fourteen has led non-conference win rate in **every one of 13 seasons**,
  opening at 81% in 2026. It did not drift upward; it started there.
* Two cliffs in the prestige table: the Great Fourteen sits **13.3 points clear** of the
  next conference, and the P6/L6 divide is a **33.2-point drop** from Western Coast
  (70.9) to Brass Belt (37.7).

The consequence is bigger than the undefeated count: **no programme can ever rise or
fall.** Ciarralotta has won 42% of its games over 13 seasons on 85.5 prestige and still
recruits like a blue-blood. Coastal Ranroman has won 61% on 32.7 and still recruits like
a bottom-feeder. Thirteen seasons of football have changed nobody's standing.

### The engine lever: ATTEMPTED, NOT SHIPPED

Dan approved steepening the curve. Two mechanisms were built and measured; **neither
produced a clean calibration and nothing was changed.**

`pbp_engine.EDGE_SCALE` (amplifies the unit-strength and coaching gap, leaves home field
alone) and `pbp_engine.NOISE_SCALE` (multiplies every yardage draw's spread) both exist,
both documented, **both left at 1.0**. Verified against `pbp_engine.py.pre_edge_scale`:
60 of 60 games reproduce exactly, so weeks 0 and 1 of 2038 stand as played.

Why neither shipped:
* EDGE_SCALE is the wrong mechanism. A larger mean edge compounds hardest where the gap
  is already enormous, so it blew the subdivision margin from +21.6 to +30.8 (target
  +22.1) while barely moving the FBS-vs-FBS curve that matters.
* NOISE_SCALE is the right mechanism in principle — means stay put, only the ratio of
  edge to noise changes — but the measurements would not resolve it. Fitting the
  logistic k on 1400 sandbox games returned 1.25 / 1.50 / 1.28 across noise 1.00 / 0.90 /
  0.80: non-monotonic, i.e. sampling error (~+/-0.2 on k) swamping the effect.
* An earlier 192-game duel harness was worse still — the SAME setting measured 89.1% and
  94.3% on two seeds.

**To finish this properly, the fit needs ~10,000 sandbox games per setting, not 1,400.**
That is roughly 20 minutes per point on the sweep. Worth doing only after the prestige
question is settled, since the engine half is worth +0.12 undefeated against the
+0.81 that competitive balance is worth.

---

## PRESTIGE NOW MOVES — 2038 RESTARTED, 2026-10-09

Dan: "Prestige should definitely move. It should be affected by a lot of things,
history, coach, recent bumps, good players, player retention, everything. I want to
restart this season (with the same schedule) after we've added this."

**`prestige.py` (new)** makes prestige an output as well as an input. Six factors,
weighted: schedule-adjusted merit .40, honours .16, history .14, coaching .12, talent on
hand .12, retention .06. Each offseason prestige closes 22% of the gap to its target,
capped at 7 points a season, so a collapse takes ~5 years to drop a programme out of the
elite and a decade to reach bottom. **Merit is Elo, not win rate** — a Low Sixteen
programme going 56% against the Low Sixteen is not a Great Fourteen programme going 56%
against the Great Fourteen, and a win-rate model rated them equal and flattened the
twelve conferences from a spread of 22.1 to 6.4.

**`restart_s13.py` (new)** back-applied it: prestige = 45% designed + 55% earned over 13
seasons, then regenerated all 152 rosters from the new prestige. Dan chose both the 55%
blend and full regeneration over scaling.

**VOIDED: weeks 0 and 1 of the first 2038 run, 106 games.** Under the standing rule
those games never happened and are never referenced again.

Backups at `*.pre_prestige_s13`: universe, rosters, state, games, seed_registry.
Preserved: the schedule exactly (980 rows), all of seasons 1-12 (11,612 games),
conferences, colours, title history, coaching staffs.

### Measured effect, 12 simulated seasons before and after

| | before | after | target |
|---|---|---|---|
| undefeated per season | 0.17 | **0.83** | 1-3 |
| top-5 mean losses | 1.60 | **1.08** | <= 1.2 |
| top-15 mean losses | 2.34 | 1.88 | rarely > 3 |
| a top-10 roster wins | 61.8% | **70.8%** | ~90% |

Top-5 mean losses now MEETS the target. Undefeated sits just under the band but the
distribution is {0 undefeated in 6 seasons, 1 in 3, 2 in 2, 3 in 1} — half of seasons
produce one. This beat the +0.26 I projected, because regenerating rosters tightened
talent to prestige (r = 0.951) and stripped out accumulated drift.

Still open: a top-10 roster wins 70.8% where real CFB is nearer 90%, which is the engine
curve — `NOISE_SCALE` is in `pbp_engine.py` at 1.0 and still needs ~10,000 sandbox games
per setting to calibrate. Conference talent spread only moved 0.52 -> 0.487 and the
Great Fourteen still holds 6 of the top 10, so realignment remains the untouched lever.

---

## THE VERTICAL SHOT — 2026-10-09, forward only from week 2 of 2038

Dan noticed the sim had no long touchdowns. Measured across the 106 games of weeks 0-1:
of 584 touchdowns, **86% came from inside 20 yards**, and across 3,689 completions the
longest was 68 with not one reaching 70. That worked out to 0.5 TDs of 50+ yards per
team-season and 0.2 of 70+.

**The cause was an asymmetry between the two phases.** Runs had an explicit breakaway --
~5% of carries, more for fast backs, adding an exponential tail -- which is why an
80-yard rushing touchdown was possible. The passing game had no equivalent: a completion
was air yards plus YAC, and air yards came from a normal centred at 4-11 after
`CAL_AIR_SHIFT`, with Deep Threat topping out near 11.4. Forty air yards was a 3.6-sigma
draw. The bomb to a receiver behind the secondary could not happen.

**Fix: `SHOT_RATE = 0.12`, `SHOT_DEPTH = 28.0`** in `pbp_engine.py`. On each attempt the
offence may take a genuine vertical shot (x1.7 for a Deep Threat, x2 when it needs a
chunk), adding depth and spread to the throw. It is NOT a free play: `comp` already
carries -0.017 per yard of air past 8, so a 40-yard throw sits on the 0.22 completion
floor, which is about what a real deep shot completes at.

**Paired with `CAL_AIR_SHIFT` 2.6 -> 4.4.** The shot alone pushed yards per completion
from 14.0 to 15.3 against a real-world ~12; taking a little depth off the routine throw
holds it at 13.96 so the tail is added without inflating the whole distribution.

**Rejected: scaling the YAC breakaway by receiver speed**, mirroring the run. Tried it
first and it lifted the entire distribution rather than the tail -- yards per completion
14.3 -- so it was reverted with a note at the call site.

Measured on 220 games at the live settings, against the same harness before:

| | before | after |
|---|---|---|
| completions 40+ | 1.0% | **3.5%** |
| completions 50+ | 0.4% | **1.2%** |
| longest completion | 72 | **82** |
| TDs of 50+ per team-season | 0.5 | **1.1** |
| yards per completion | 13.99 | 13.96 |
| yards per carry | — | 4.27 |
| points per team | 25.3 | 23.88 |
| completion rate | 61.8% | 58.1% |

50+ yard touchdowns now split 21 passing / 21 rushing, where before they were nearly all
runs. Completion rate is the one stat that moved, from 61.8% to 58.1% against a real
~62%, and it moved for a real reason: offences take more low-percentage swings.

Backup: `pbp_engine.py.pre_deep_shot`.

**Dan's instruction: no more engine-change reporting until the end of the season, then a
full audit.** `EDGE_SCALE` and `NOISE_SCALE` remain at 1.0 and uncalibrated; the engine
curve (a top-10 roster wins 70.8% where real CFB is ~90%) and conference realignment are
the two levers still untouched. Raise them at the season-end audit, not before.

### Subdivision floor lowered — 2026-10-09, takes effect at the NEXT guest generation

Dan: "lower the skill floor for subdivision teams without lowering the ceiling."

`subdivision.py`: `SUB_CEILING = 18.0` (unchanged), `SUB_FLOOR = -10.0`,
`SUB_WEAK_SHARE = 0.20`. Four guests in five are drawn exactly as before from
uniform(2, 18); the fifth comes from uniform(-10, 2).

A blanket skew was tried first and rejected: `18 * u**1.8` dragged p90 from 16.4 to 14.1
and the median from 10.0 to 3.9, which lowers the ceiling region Dan asked to leave
alone. The mixture keeps p75 at 13.0 against 14.0 and p90 at 16.0 against 16.4, with the
maximum identical at 18, while the floor falls from 2 to -10. About 15% of a 136-guest
season now sits below the old floor. Roster base talent spans 3.63-4.53 where it was
4.01-4.53.

**NOT applied to the 2038 guests.** They were generated at install and have already
played games in weeks 0-3; regenerating them mid-season would rewrite canon. This lands
at the next `SUB.generate()` call, i.e. when 2039's schedule is installed.

Backup: `subdivision.py.pre_floor`. Raise at the season-end audit, not before.

## 2038 week 6 — the committee board becomes Dan's
- `install_committee.py` installs a hand-built ballot as `committee_poll_current` /
  `committee_history[wk]`, with a nine-probe audit (duplicate, skipped rank, short
  ballot, unknown programme, wrong season, wrong week, incomplete, stale record,
  subdivision guest). Sets `committee_official`.
- `play_week.py` no longer generates a committee poll at week 10 when
  `committee_official` is set — it would have overwritten the board of record.
- Quality losses (`ql`, a defeat against a top-30 opponent — the mirror of `qw`) are
  computed in `export_committee_week.py` and shown in purple on the ballot page.
- The reference number on each ballot row is now the committee board rather than the
  media poll.

## 2038 END-OF-SEASON AUDIT — 2026-10-09

Dan's instruction in week 2 was to stop reporting engine changes until the season
ended and then audit everything at once. This is that audit. Every figure below is
measured from the game database, not recalled.

### The separation problem: substantially better, and measured without circularity

Last time I claimed separation had improved I bucketed teams by END-OF-SEASON net
rating, which is derived from results -- the measure and the thing measured were the
same number. The honest test buckets games by `pregame_home_wp`, which is an INPUT
(the talent model), and asks whether favourites win at the rate claimed.

    model says        2026-2037          2038
    50-60%            won 54.9%          won 54.2%
    60-70%            won 59.8%          won 68.2%
    70-80%            won 67.8%          won 73.7%
    80-90%            won 76.7%          won 88.4%
    90%+              won 86.4%          won 92.3%

Before 2038 the model over-promised at every level above a coin flip, and the miss
grew with confidence. In 2038 every bucket meets or beats its stated probability.
Favourites now win roughly as often as their rosters say they should.

CONSEQUENCE, not yet acted on: `win_prob`'s coefficient (1.480) was fitted on 881
canon 2037 games precisely to stop the over-promising. The engine has now moved under
it, so the model UNDER-promises. It should be refitted on 2038, or left alone
deliberately -- but it should not be left stale by accident.

### Season shape

    top-5 mean losses     1.00   (best of thirteen seasons; prior best 1.20)
    one-loss programmes   6      (prior best 4, in 2036)
    unbeaten              0
    FBS-vs-FBS margin     14.81  (band across 13 seasons: 12.4 - 16.3; canon target 14.1)
    FBS-vs-FBS one-score  35.7%  (canon target 36.8%)

The raw all-games margin reads 16.80, the highest ever, but that is NOT the engine
spreading out: 2038 played 136 guest games against the usual 62, under the 90% parity
rule, and guest blowouts pull the mean. Excluding guests puts 2038 mid-band and close
to the canon target on both measures.

### Subdivision games: the complaint is answered

                        2029-2037      2038
    guest games           496            136
    within one score     23.2%          13.2%
    mean margin           21.6           29.1
    guest wins           10-16% of games  8.1%

### Explosive plays: the fix worked, the baseline does not exist

40+ yard touchdowns as a share of all touchdowns from scrimmage:

    2038 weeks 0-1 (before the change)   3.4%
    2038 week 3 onward (after)           ~7%
    run 7.0% / pass 7.3% -- the run-vs-pass asymmetry is gone

But the series has no stable canon to aim at: 4.4% in 2026-29, 26.4% in 2030, falling
through 14.8 / 12.3 / 11.5 / 11.2, then 6.7 / 4.9 / 3.6 by 2037, now 6.5. This has
never been calibrated and drifts with every rebuild. NEEDS A TARGET from Dan (or from
real-football reference) and ONE calibration pass, rather than another nudge.

### Two-point conversions

Tries rose and so did the hit rate: 512 tries at 52.1% across 2035-2037, against 123
tries at 60.2% from week 4 of 2038 (after the chart change that moved +5 to the
consensus tier and added +4 to the aggressive tier). The sample is small; watch it.

### Bugs found and fixed during the postseason

- `finalize_season` writes the champion into `history` but never into `season_archive`,
  which is where `prestige.components` reads national-title honours. Left alone, Eona's
  title would have been worth nothing to prestige. 2038 row written by hand; the
  function itself still needs the fix.
- The award-basis snapshot (`season_state.pkl.pre_s{N}_po_r1`) was never taken. Nothing
  in `install_field.py` or `playoff.run_round1` saves it. Rebuilt from box scores by
  `rebuild_award_basis.py`, verified by reconstruction (basis + playoff == live, player
  by player). Something must TAKE the snapshot next year.
- The Committee Room read its saved field from `ballot/s10` while writing to
  `ballot/s{season}`. Fixed.
- `install_field.py` printed "(24) Larksdale hosts (9) Ranroman", naming the visitor as
  the host. Label only. Fixed.
- A coach's `tenure` never increments. It has been frozen at its 2035 value for three
  seasons, so it cannot be used to date anything after the rebuild, and the coaching
  board can only reconstruct who-coached-where exactly from 2036 on.

### Still open, carried forward

- `EDGE_SCALE` / `NOISE_SCALE` exist in `pbp_engine` at 1.0 and are UNCALIBRATED
  (verified no-op, 60/60 games identical). Needs ~10,000 sandbox games per setting.
- Portal coach-following still broken (arithmetic in the 2038 portal section).
- Blue-chip cap leak latent; `r_coach` is not measuring coaching; recruiting positional
  mix does not match the position floors (OL under-recruited).
- `conf_builder.audit` still rejects a week-1 bye, which is now legal.
- Surprise-onside rate is 13%; real football is 50-60% when unexpected.
- Subdivision floor (`SUB_FLOOR = -10.0`, `SUB_WEAK_SHARE = 0.20`) takes effect at the
  NEXT guest generation, so 2039 is the first season that tests it.

## 2038-39 OFFSEASON — Stage 1 of 7 COMPLETE: coaching carousel
Backups at `state/{season_state,coaches,rosters}.pkl.pre_s14_carousel`; stored as
`s["carousel_s13"]`.

15 vacancies | 12 head-coach hires | 29 coordinator moves.
Sources: 5 interims not retained, 4 retirements, 3 offseason firings, 2 interims kept,
1 dream job.

Notable: **Tage Ludendorf left Kaji Daun for Eastern State**, his dream job -- the 9.00
coordinator from the staff that just played for the national title, to a 7-7 conference
champion. **Yuki Kamau retired from UNN after eleven seasons and 95 wins** and **Henrik
Thompson from West Hatesei St after ten**. Three programmes hired distinctly down (UNN
8.18 -> 4.14, West Hatesei 8.48 -> 4.53, Kaji Daun State 8.01 -> 4.30); Hansenne went
2-10 and landed an 8.18, the biggest upgrade of the cycle.

### 🐛 FIXED: coach tenure never persisted
`rollover.py` step 3 has been adding a year to every coach's tenure since 2035 and then
discarding it -- the commit block wrote rosters and season state and never
`coaches.pkl`. Three cycles were lost, which is why every tenure in the league still
read its 2035 value and why the coaching board can only date a job exactly from 2036.
Fixed; forward only, the lost years are not recoverable.

## Stage 2 of 7 COMPLETE: the 2039 draft

### ✅ RULED (Dan, 2039): real draft eligibility
A player must be three years removed from high school. **True freshmen and sophomores
cannot declare at all** -- they are not in the pool at any stock. This had been unruled
since 2038, when 47 of 210 picks were Fr/So and Barhold lost the freshman quarterback
who had just taken it to the title game. The 2039 board would have done it to Eona:
Chiara Marshworth, the freshman who won the championship, graded 30th overall, and
Efrain Somaraj graded 8th. Both stay. Forward only; every draft already played is canon.

3,820 declared | 210 picks | 96 early entrants (all juniors) | 9 subdivision |
0 questionable declares.
Class split: Sr 85, Jr 96, RS 29 — **Fr/So 0**, verified on the pool and on the board.
Departures: 2,946 leaving, 210 drafted, 857 withdrew back to school.

Top five: 1. Soren Birketveit (TE, Sr, Tengus State), 2. Boyoung Konnides (RB, Sr, Eona),
3. Setsuko Dongfang (CB, Sr, Canesta State), 4. Haneya Quisvaw (WR, Sr, Riveral State),
5. Francesca Jutras (DL, Sr, Denver State).
Positions: OL 40, WR 32, LB 25, DL 22, QB 21, RB 19, CB 16, S 16, TE 12, K 3, ATH 3, P 1.
The OL fix keeps holding — 40 drafted, the most of any position.
Most drafted: Kaji Daun 6; Black Forest, Roosevelt and Ranroman State 5 each.

## Stage 3 of 7 COMPLETE: the 2039 transfer portal
Backups at `state/{season_state,rosters}.pkl.pre_s14_portal`; stored as `s["portal_s13"]`.

469 entrants | **302 transferred** | 167 found no taker and withdrew.
Positions: DL 50, CB 47, TE 35, S 30, QB 29, WR 29, RB 20, LB 17, OL 16, K 15, P 14.
Biggest gainers: North Verigon 8; Ranroman State and Ranroman 7 each; Roosevelt,
Rogaela State and Riveral State 6 each.

### ✅ FIXED: coach-following is a decision now, not a weight nudge
The documented remedy shipped. A player whose own stated reason is the staff change
("left after the staff turnover", "didn't fit the new staff's plans") now FOLLOWS
outright with p = 0.55 when his coach's new school is in his pool and the move is on
his side of the ball; everyone else falls through to the existing weighted draw, which
keeps its 3.5x / 2.0x multipliers. Forward only -- the 2038 portal is canon.

Measured effect, 2038 against 2039:

| | 2038 | 2039 |
|---|---|---|
| portal entrants | 454 | 469 |
| whose coach left | 110 | 64 |
| coach's new school in their pool | 59 | 37 |
| **actually followed** | **1 (1.7%)** | **5 (13.5%)** |

All five came through the new decision path; zero came from the weighted draw, which
is the point -- the old path never produced one on purpose. Of the 22 staff-driven
entrants who found a home at all, 23% followed their coach.

WHY FIVE AND NOT THE PREDICTED 15-19: this carousel was half the size of last year's
(19 coach moves against 41, 15 vacancies against 23), so the population that can follow
anybody is correspondingly smaller -- 64 lost a coach rather than 110. The RATE is the
thing the fix moved, and it moved about eightfold. Re-measure after a big carousel year
before deciding whether FOLLOW_P needs to rise.

### 👀 Watch, second cycle running: positional imbalance
Last cycle CB 45 against LB 6. This cycle **DL 50, CB 47 against LB 17, OL 16**, with
K 15 and P 14 still high for two-deep positions. The pattern repeats: positions whose
value function keys on countable events (sacks, interceptions) move freely and
tackle-based positions do not. Same class of problem as the OL draft-valuation bug that
has already been fixed once. Worth a pass before 2040.

## Stage 4 of 7 COMPLETE: the 2039 recruiting cycle
Backups at `state/{season_state,rosters}.pkl.pre_s14_recruiting`; stored as
`s["recruiting_s13"]` in the same shape as s10-s12 (class_size, needs_total, signed,
unsigned). `recruiting.py`'s `__main__` only sizes the class, so the stage is assembled
by hand. NOTE the argument order: `run_recruiting(recruits, needs, s)`, not (s, ...).

National class **2,753** (fixed-size rule holding) | **2,574 signed** | 179 unsigned.
Stars in the class: 5* 13 | 4* 275 | 3* 964 | 2* 1,101 | 1* 400.
Signed: 5* 13 | 4* 275 | 3* 964 | 2* 1,101 | 1* 221 -- every blue-chip and every 2-3*
found a home; the 179 left on the board are all one-stars.
**L6 share of blue-chips: 6.9%**, up from 4.9% and above the canon series (4, 4, 3, 2,
3.2%). Watch it: the tier term in `cap_for` may now be too generous, or this is the
first visible effect of prestige moving.
Class sizes 6 to 29. Nineteen programmes maxed a 6-blue-chip haul.

Thirteen five-stars: Hugh Hatamura (WR, 8.57) to Rogaela State, Perla Neraettoni (RB,
8.47) to Eona, Tama Walkingcloud (OL, 8.43) to Tengus State, Sabine Gradavsky (OL, 8.42)
to Kaji Daun, Callum Cha (CB) to Pistolheart, Angelique Casanueva (LB) to Ranroman State,
Clemence Eastton (WR) to Ranroman, Kyungja Chumi (S) to Ciarralotta Tech, Youngchul Cheon
(CB) to Central Stanton, Douglas Bergmann (DL) to Orlot, Omar Vlahos (LB) to North
Verigon, Ursula Starushkin (OL) to Roosevelt, Edward Braunberger (DL) to Crayellan.
Best classes by total stars: Crayellan 62, S Antiragal State 59, Eona and Ranroman State
56 each.

### ✅ FIXED: the blue-chip cap leak
Phase 2 drew from everyone still unsigned -- which includes any 4-5* phase 1 did not
place -- weighted by `stars**2`, with NO cap check. A surviving blue-chip was therefore
the most attractive thing on the board and phase 2 handed it over uncapped. It had never
fired only because every class so far carried fewer blue-chips (287 in 2038, 288 now)
than the league's total cap capacity (~293). The cap is enforced in both phases now and
`bc_signed` keeps counting through. Audited after this cycle: **0 teams over their cap**,
19 at exactly 6.

### ✅ ALREADY RESOLVED: the TARGET / ROSTER_MIN mismatch
The 2038 note left this "needs Dan's call". It was in fact already raised -- `TARGET` is
63 and `roster_final.ROSTER_MIN` is 63, with the reasoning in a comment at the call site.
Checked rather than assumed. Stage 6 should manufacture few or no phantom walk-ons this
year; verify there.

## Stage 5 of 7 COMPLETE: 2039 development
Backups at `state/{rosters,season_state}.pkl.pre_s14_dev`; stored as `s["development_s13"]`.

**7,002 players developed** (not 9,810 -- see below), mean growth **+0.287**.
By class: Fr +0.386, So +0.255, Jr +0.191. 321 breakouts, 65 busts.
Biggest jumps: Emosi Tallrain (WR, Fr, Tasson) +1.86 to 7.90; Sorei Holtaw (LB, Fr,
Skylar Rose) +1.78 to 8.38; Axel Peatshaw (CB, Fr, Orlot Western) +1.65 to **9.42**.

### ✅ FIXED: `r_coach` now measures coaching
Both halves of the diagnosis shipped.

1. Players flagged `_leaving` are no longer developed or counted. 2,946 seniors and
   drafted underclassmen were being grown by a stage that then deleted them -- pointless
   work, and the thing that made the statistic lie, since they all grow exactly 0.0.
2. The correlation is reported WITHIN CLASS, as `r_coach_by_class`. The single league
   number was a composition artefact: growth is set almost entirely by class, so a
   team's mean growth mostly reported its class mix. `r_coach` is kept for continuity
   with s10-s12 but should not be read.

Result this cycle, against a canon norm of about +0.49:

| class | r with coach_mult | teams | mean growth |
|---|---|---|---|
| Fr | **+0.492** | 152 | +0.386 |
| So | **+0.486** | 152 | +0.255 |
| Jr | **+0.411** | 152 | +0.191 |

The three-cycle slide of 0.609 -> 0.566 -> 0.170 was never the engine. No player
ability was changed; this is a reporting fix only.

### ✅ RULED (Dan, 2040): "RS" is a REDSHIRT FRESHMAN, not a fifth-year
Three modules had been disagreeing silently since the rebuild:
  * `gen_rosters` gives RS an ability bonus of +0.22, between Jr (+0.12) and Sr (+0.30)
  * `rollover.py` promotes RS -> So, i.e. a freshman who sat out
  * `draft.py` listed RS alongside Sr and RS5 as eligibility-exhausted

`draft.py` won, so **every redshirt in the league was flagged as leaving after one year
and rollover's RS->So promotion was dead code** -- 854 players this cycle, and no RS
player has survived a single offseason since 2035. Dan's ruling: RS returns as a
sophomore. `draft.py` corrected in both places (`seniors` and `SENIOR`); "RS5" remains
the fifth-year class.

FORWARD ONLY, by Dan's call: **the 2039 draft stands as played**, so this cycle's 854
redshirts still leave in stage 6. The fix bites from 2040.

TODO while in there next cycle: `gen_rosters.CLASS_AB["RS"] = 0.22` still rates a
redshirt between a junior and a senior, which is the fifth-year reading. Under the new
definition it should sit near Fr/So. Cosmetic until the next roster generation, which is
the only thing that reads it.

## Stage 6 of 7 COMPLETE: 2039 roster finalisation
Backups at `state/{rosters,season_state}.pkl.pre_s14_rfinal`; stored as
`s["roster_final_s13"]`.

`{'departed': 2946, 'recruits_added': 2574, 'walkons': 0, 'floor_fills': 273,
'trimmed': 0, 'min': 63, 'max': 69, 'total': 9849}`

**walkons 0** for the second straight cycle, and **floor_fills down 373 -> 273**.
All `_leaving` flags cleared; 0 remain. Rosters 63 to 69.
League positional mix after finalisation: OL 15.2%, DL 13.1%, WR 13.0%, LB 10.8%,
CB 9.5%, S 8.3%, RB 8.2%, QB 6.8%, TE 6.3%, K 3.8%, P 3.8%, ATH 1.2%.

### ✅ FIXED: the recruiting positional mix (the last of the four queued)
`POS_WEIGHTS` moved OL 0.13 -> 0.18, RB 0.10 -> 0.06, QB 0.08 -> 0.07. The class mix now
matches the shape a roster needs; the largest remaining gap against floor share is DL at
+1.0pp and LB at -0.9pp, against OL's old -4.4pp.

| pos | recruited | floor share | gap |
|---|---|---|---|
| OL | 18.0% | 17.4% | +0.6pp |
| RB | 6.0% | 6.5% | -0.5pp |
| QB | 7.0% | 6.5% | +0.5pp |

FORWARD ONLY, and note the timing: the 2039 class was already signed in stage 4, so this
takes effect at the **2040** class. Expect `floor_fills` to fall again next cycle; that
is the number to watch.

All four forward-only fixes queued since 2038 are now shipped: portal coach-following,
the blue-chip cap leak, the `r_coach` statistic, and this.

## Stage 7 of 7 COMPLETE: rollover, 2038 closed and 2039 open
Backups at `state/{rosters,season_state,coaches}.pkl.pre_s14_rollover` and
`state/universe.pkl.pre_s13_step`.

Classes: Jr->Sr 1,987 | So->Jr 2,363 | Fr->So 2,456 | Fr->RS 196 | incoming stay Fr 2,847.
Rosters 63-69. Records, injuries, stats, polls and hot seats reset. 2038 archived.

### ✅ VERIFIED: coach tenure now persists
All 152 head-coach tenures advanced by exactly 1 and the change is ON DISK -- the first
time that has happened since 2035. Distribution now runs 1 to 24.

### 🐛🐛🐛 PRESTIGE WAS NEVER GOING TO MOVE AGAIN. Three bugs, all fixed here.
The dynamic-prestige build of 2038 is what the whole separation result rests on. Running
stage 7 showed it was inert in three separate ways.

**1. Nothing ever called `prestige.step`.** It had run exactly once, as the
back-application during the 2038 restart, and no stage in the pipeline advanced it. Now
wired into `rollover.py` as step 3b, once per cycle, with the universe persisted.
  * SEQUENCING, flagged not changed: it runs at stage 7, AFTER recruiting at stage 4, so
    a rise or fall reaches the class signed the cycle after the season that earned it.
    Moving it to the top of the offseason would make it immediate. **Dan's call.**

**2. Three of the six components were reading sources that do not exist**, so 32% of
the weight was a flat 50 for all 152 programmes -- pure dilution:
  * `history` read `geo[t]["titles"]`; `geo` carries only state/mascot/full_name. The
    real 1929- canon is `state["history"]["book"][t]`. Now also credits runner-up
    finishes at 12 points against a title's 40.
  * `coaching` read `state["coaches"]`; staffs live in `pbp_engine.COACHES`. Every staff
    fell to the 5.0 default. Dan's brief named the coach explicitly.
  * `retention` read `state["portal_log"]`; `portal.py` writes `portal_s{N}["transfers"]`.
  All six components are live now (spreads 12.4 to 23.8).

**3. THE TARGET SCALE WAS DEFLATING THE WHOLE LEAGUE.** Each component is min-max
normalised to 0-100 and those distributions are right-skewed, so the weighted blend came
out with mean 32.7 against prestige's mean 47.2. The target was BELOW current prestige
for **145 of 152 programmes** -- every one of them would have fallen a few points every
year, the league would have deflated toward the floor, and the P6/L6 architecture would
have dissolved over about a decade. It would have been invisible for three seasons.
Fixed by standardising the blend and mapping it onto the DESIGNED prestige distribution,
which never moves, so the target expresses rank rather than a scaler artefact and
league-level drift cannot compound.

Result, 2038 -> 2039: mean move **+1.34**, mean absolute 1.94, max 6.9. The +1.34 is a
one-time correction of the compression the 55%-earned restart introduced, and it decays.
**P6 mean 62.8, L6 mean 33.5, cliff 29.3** -- the tier architecture is intact.

Risers: Black Forest +6.9 (12-1, Low Sixteen champion), Canesta State +6.9 (11-1),
Roosevelt Mines +6.2, North Verigon +5.5, Roosevelt +5.1, Tengus State +5.1.
Fallers: Harrell -4.8 (1-11), Roosevelt State -2.8, Southern Krobe -2.6, Northlight -2.5.
Champion Eona 83.9 -> 87.2; runner-up Kaji Daun 80.4 -> 84.5.

### NEXT: 2039 preseason
Preseason top ten: Ranroman State 11.10, Rogaela State 10.73, Central Stanton 10.41,
Skeenerland State 10.40, Orlot 10.32, Kaji Daun 10.29, Greene 10.19, Ranroman 9.98,
Ciarralotta Tech 9.87, North Verigon 9.86. Note those are computed from the rosters
BEFORE this prestige step, which is the sequencing point flagged above.

## ✅ RULED (Dan, 2040): prestige steps at the TOP of the offseason
Moved out of `rollover.py` (stage 7) into `carousel.py` (stage 1, before anything else
runs). State still holds the finished season at that point -- rollover does not reset it
until stage 7 -- so the step reads the right results, and everything downstream in the
same cycle sees the new prestige: who can hire whom, who recruits whom, who the portal
rates. It used to delay every movement by a full cycle.

Applies from the 2039-40 offseason. The 2038-39 step was already taken by hand at
stage 7 and stands.

## 2039 SCHEDULE — stage A: the non-conference board
`export_schedule_board.py` run against the fresh 2039 state; Scheduling Office published.

152 programmes | 217 subdivision guests available | 6 locked cross-conference rivalries
pre-filled | **444 non-conference dates for Dan to fill** (456 total less the 12 the
locked rivalries already occupy).
Unreturned visits: 382 pairs, 5.0 per programme.
Series met twice or more in five years: 199 pairs -- 192 already settled home-and-away
(badge suppressed), 7 played entirely at one ground and still owed a return.

Records and prestige on the board are the post-rollover 2039 figures, so Black Forest
reads 12-2 at prestige 50 and Canesta State 12-3 at 45 -- both up sharply from the
prestige step. Render-checked in both themes; no console errors.

NEXT: Dan fills the board (or says to auto-fill the remainder), then the Conference
Office builds the twelve conference calendars around it, then `install_hand_schedule.py`.

### 2039 non-conference board — PARTIAL, Dan to resume
Hand-off saved at `state/noncon_s14_partial.json` and seeded into the Office payload
via `seed_board.py`.

**As of 2026-10-10 13:50: 155 games · 257 of 456 dates filled · 199 open.**
6 locked cross-conference rivalries + 149 of Dan's. 53 subdivision guest games.
Coverage: 123 of 152 programmes have a game — 59 at three, 16 at two, 48 at one,
29 not started.

**⚠️ ONE BLOCKING ISSUE, and the page is right to flag it: the guest count is ODD (53).**
A guest game burns ONE FBS date; an FBS-vs-FBS game burns TWO. With 456 total dates,
an odd number of guest games leaves one date that can never be paired. It resolves
itself as soon as the 54th guest game is booked (or one is removed), so it is only a
blocker if the board is finished on an odd count. Flagged to Dan, not acted on.

Everything else validated clean: no unknown programmes, no guest outside the pool, no
pairing booked twice, no programme over three non-conference games, no guest invited
more than once.

Checkpoints: 2026-10-09 65 games/110 dates · 2026-10-10 am 123/206 · 2026-10-10 pm 155/257.

When Dan finishes: complete by hand, or `fill_noncon.py` takes it to the ~90%
guest-parity target. Then the Conference Office for the twelve calendars, then
`install_hand_schedule.py`.

## 2039 non-conference board — COMPLETE (2026-10-11)
Fourth hand-off: 196 games, 73 guests (odd -> blocking). `fill_noncon` added 63 guests
and 37 FBS games: 296 games, 136 guests (89.47%, the even neighbour of 90%), 0 open
dates. 24 programmes host all three; rebalance could flip only one (guests cannot
travel, Dan's venues are not touched). Board frozen as `state/noncon_s14.json`.
`fill_noncon`, `seed_board`, `export_conf_board` were all pinned to s13 and now derive
the board path from the open season. Conference Office exported: 12 conferences, 0
problems. NEXT: Dan builds the conference calendars, then `install_schedule`.

## Two scheduling rules added (Dan, 2039 build, 2026-10-11)
1. The conference 4/5 home split SWAPS every season: `balance_hosts` now takes a
   per-programme target = 9 - last season's conference home count. 2039: 152/152
   swapped (was 84 by accident). Cost: same-venue repeats 24 -> 28 of 493.
2. A programme with two locked conference rivals hosts one and travels to the other
   (`split_locked_venues`). Fiota Bay / Crayellan / Crayellan State / UFNH triangle
   was hosting-both or visiting-both in 2038 and would have again. One-time repeat
   taken in the week-9 Locked game (Fiota Bay hosts Crayellan again) so both Rivalry
   Week games still turn around; alternation keeps the rule from here.

## 2039 conference calendar — COMPLETE (2026-10-11)
Dan placed six conferences + 192 non-conference weeks by hand (544 of 980). New
`fill_conf.py` (simulated annealing) placed the other 436 under his two venue rules:
never 4 road games in a row (counted over games played, a bye does not reset it);
never 5 home in a row, 4 only with a non-conference game among them. Zero violations
among the programmes it touched. Three violations sit in Dan's OWN rows and were left
for him: Ciarralotta 4 road in a row (wk 5-8), Milharvey 5 home (wk 1-6 around a bye),
UNN 5 home (wk 1-6). No single swap fixes any of them. Saved board (conf/s14) rewritten
to match the page so the restore cannot wipe the fill. NEXT: install_schedule.

## 2039 SCHEDULE INSTALLED — 2026-10-11
Dan's final hand-off fixed Ciarralotta's road run but Will Tech / Tasson both PLAYED
in week 9, which `bye_before` forbids (the Office still does not enforce it; the
installer refused). No 1- or 2-move fix existed. `fill_conf` grew a `bye_before`
constraint and an anchor penalty; a two-hop repair moved 9 games (all Jyras Bay or its
guests), listed in the chat. Side effect: Milharvey's 5-home run cleared. UNN's 5-home
run (wk 1-4, 6) stands as Dan left it. Installed from `state/conf_sched_s14.json`:
980 games, 136 guests, audit CLEAN. Week 0 = 15, week 1 = 83, week 14 = 79.

Pre-season audit (all clean unless noted): 12 games / 9 conf per programme, no doubles,
no duplicate fixtures, rosters 63-69, floors met, 0 `_leaving`, 0 `freshman` flags, no
duplicate pids/names, 136 guest rosters, no staff gaps, all season counters reset,
no S14 rows in the games db.
FOUND: `committee_official` survived the rollover as True -- the `play_week` guard
would have kept an empty hand-built board from week 10 and never run the automatic
committee. Cleared in state; `rollover.py` now resets it.
NOTE: 78 head coaches read tenure 1 -- that is every hire 2036-39 collapsed onto one
value by the lost-tenure bug fixed last cycle, not 78 new hires (12 jobs filled).

## Will Tech / Tasson moved to week 9 (Dan, 2026-10-11) — FROM 2040
`U['fixed_pairs']` entry changed: week 10 -> 9, `bye_before` keeps both idle in week 8.
2039 is already installed at week 10 / bye 9 and stands. `season.py` reads only the
pair set from fixed_pairs, so the live season is untouched. `rebuild_universe.py`
would overwrite this from `/mnt/user-data/outputs/rivalry_data.json` (which no longer
exists) -- if the universe is ever rebuilt, re-apply. Backup: universe.pkl.pre_wt_tasson_wk9.
STILL OPEN: the Conference Office should refuse a placement that breaks `bye_before`.

## Rankings cadence (Dan, 2026-10-11)
Weekly reports carry the MEDIA POLL top 25 until the first committee ranking. The first
committee ranking is now built AFTER WEEK 8 (2038: week 6; engine default was 10).
`COMMITTEE_START = 8` in play_week.py and run_season.py. The ballot export
(`export_committee_week.py`) is run on request after week 8 as last year.

## MEDIA POLL — three bugs, found 2039 week 1 (0-2 North Hatesei still #1)
1. `played = next_week - 1` assumed the calendar opens at week 1; it has opened at week
   0 since 2035. The poll ran a week behind all along and ignored results after week 0.
   Now counted from `results`.
2. `pedigree` counted EVERY title in the 110-year book (NH: 21 titles = +142 pts, no
   fade) -- it became the whole poll once the 1929 canon was wired in last season. Now
   titles/finals inside 25 years, capped at 12 raw (+26), fading with preseason weight.
3. `s['archives']` never existed; last season's record and the defending-champion bonus
   read an empty dict. Mapped onto `season_archive[str(season-1)]`.
Week-1 poll recomputed from the (unchanged) week-0 ballot: Eona 1, Kaji Daun 2, NH 9.
The week-0 ballot stands as the preseason poll. Polls are derived, not canon results.
WATCH: inertia 0.42 still keeps a 0-2 preseason #1 inside the top 10 and leaves Krobe
State (52-17 over #2 Greene) at #34. If that still looks wrong at week 3, lower it.

## Pick-six return length (fixed forward, 2026-10-11)
`pbp_engine` scored a pick-six with the DRAWN return length rather than the distance
from the catch to the goal line; 2038 had four INT-return TDs over 109 yards (max 125).
Now `100 - land`, clamped 1..109. 2038 box scores untouched. 2038: 93 pick-sixes in
1,015 games (0.092/game), median return 50 yds (will drop with the fix).

## Committee cadence, 2039 (Dan, 2026-10-11)
First board of record installed after week 8 (`state/ballot_s14_w8.json`). From here
Dan ranks BY HAND every week. Weekly routine after `play_week N`:
  python3 export_committee_week.py && build committee_week page && republish
  python3 ballot_prep.py   -> paste into chat: his prior board with this week's result,
                              plus ~28 unranked candidates in computer order
Then install his hand-off with `install_committee.py <file> --commit`.

## QUEUED FOR THE END OF 2039 (Dan, 2026-10-12)
Audit of how often conference foes have met in the REGULAR SEASON across the sim era
(2026-2039): per conference, the pairing frequency matrix (expected 9 of 13 opponents a
year), the pairs that have met every year vs. the ones that have barely met, and venue
balance. Dan asked for it after the 2039 playoff; run it before the offseason starts.

## QUEUED FOR THE END OF 2039: the Great Fourteen is too top-heavy (Dan, 2026-10-12)
Snapshot at the 2039 quarterfinals: Great Fourteen mean prestige 75.9 vs 56-62 for the
other five P6 (top three 88.2, bottom three 60.7 -- its FLOOR is above three other P6
MEANS). 80 playoff seats in the sim era vs 45 for the next conference (Power North) and
27-33 for the rest. Five of its teams finished 6-3 in conference this year. Options to
work up with Dan after the playoff, not decided: (a) realignment -- move one or two
bluebloods out / weaker programmes in, (b) let prestige mean-revert harder for a
conference that hoards it, (c) scheduling -- more cross-P6 play so the others get the
quality wins, (d) recruiting caps by conference share. Bring numbers for each.

## Recruits were losing their identity at roster entry (fixed forward, 2026-10-12)
`roster_final.make()` drew a fresh random name for every signee and dropped the star
rating. The recruiting class and the roster were never the same people by name, and no
roster has ever carried `stars`, so bust/gem rates could not be measured. From the 2040
class, name / stars / rid / signed_abil ride along. NOTE: `make` already registers the
fresh name in `used`; the signee's name was drawn against the same pool in recruiting,
so collisions are not expected but the surname cap could in theory be exceeded.

## QUEUED FOR THE END OF 2039: injury audit (Dan, 2026-10-12)
Rates by position and class, games missed, season-enders, durability (`dur`) vs actual,
starters vs depth, whether injuries cluster on certain teams/schemes, and the
re-injury rate. Compare to the canon targets if any are recorded in PENDING.

## 2039 AWARDS (announced before the final; canonized by run_champ) — 2026-10-12
Basis: `season_state.pkl.pre_s14_po_r1` rebuilt from box scores (reg + CCG only).
⚠️ BOTH RYSKAMP CHECKPOINTS WERE MISSED AGAIN -- `play_week.py` never took them.
Reconstructed from the database (the pools are deterministic production-point boards
over games through week 6 / week 10), subset rule verified, stored as `ryskamp_s14`
with the reconstruction noted. `play_week` now captures the twenty at week 6 and the
ten at week 10 automatically. `run_season.ryskamp_pool` was also broken (returned pids,
capped at five) -- fixed. `finalize_season` now takes the Ryskamp winner and finalists
from the pools when they exist.
Ryskamp: Taiga Myeong-Seong (Ciarralotta State, Sr QB). Finalists: Nayeli Ngafanua
(Leafette), Manish Manirajan (UNN), Nayeli Nofotalo (Riveral). DPOY: Freya Aalrud (West
Hatesei, LB). FOY: Osama Ekwueme (S Antiragal State, QB). COY: Perla Notaro (Eternal Fox).

## 2039 season_archive row (written by hand, 2026-10-12)
finalize_season still doesn't write season_archive; the '14' row was written by hand after the title game
(champion Central Stanton, standings = final records incl. playoffs, final media/committee boards, firings=5).
Backup: state/season_state.pkl.pre_s14_archive_row. Fix finalize_season to write this itself from 2040.

## Conference-foe meeting audit (sim era, 2026-39) — run 2026-10-12
`audit_conf_meetings.py` -> state/conf_meetings.json. Every conference pair has met at least once.
Meetings per pair: 14-team leagues range 5-14 (exp. 9.7), 12-team 7-14 (exp. 11.5), Brass Belt full round robin.
Real finding: VENUE SKEW. Before the 2039 alternation rule nothing alternated hosts, so lopsided series exist
(Coachville College 0-10 at San Diego Valley; Dietsche 0-6 at Will Tech; Diveo 1-7 at Marblehead; Eona Navy 3-11
at Repidome in a round robin). Alternation now holds forward; consider a "balance historic venue" tiebreak in
balance_hosts so skewed series repair over the next few seasons.

## Venue-ledger bleed (Dan, 2039 end): DONE in export_conf_board.py
Pairs resuming after a gap now go to the programme behind in the whole-era venue ledger (was: alphabetical).
balance_hosts tries path flips in ledger order, then a cycle-reversal pass (host cycles of 2-4, home counts
unchanged) chases remaining skew — but only over pairs that did NOT meet last season, so the yearly alternation
rule is never broken. Test rebuild: non-locked games hosted by the team BEHIND in the series 343 -> ~430 of 649.

## Great Fourteen top-heaviness — numbers behind the options (2026-10-12)
13 of 14 G14 programmes at prestige 68+ (other P6 floors ~40). G14 65% vs other P6 non-con; 8/14 sim-era
titles and 8/14 runner-ups; 5-6 of 24 playoff seats each year. Dynamic prestige (since 2038) is pushing it
HIGHER: mean target 83.5 vs 75.9 now, six G14 teams pinned at the 99 ceiling by the min-max norm; 12 of 14
G14 programmes have risen in two steps, incl. 6-6 Ranroman State (92.9) and 6-6 Orlot. Recruiting pull is
prestige-dominated: 10 of the top-20 pull slots (6 blue-chip cap) are G14, incl. 6-6 teams at #7 and #17.
Options presented to Dan; awaiting his pick.

## Great Fourteen balance — Dan picked options 1, 3, 5, 6, 7, 9, 12 (done 2026-10-12, forward from the 2039-40 offseason)
1. recruiting.signing_priority: pull = 0.6*prestige + success + 0.25*conference-finish pct + 2*heat (was prestige-dominated).
   Cap windows retuned to keep capacity: rank<45 base 5 (was 4), rank<75 base 3 (was 2); L6 windows 14/70 (were 25/92).
   Dry run on a 2040-shaped class: 288/291 blue-chips signed, L6 share 7.3%, G14 62 (was 69 in 2039), 6 of top-20 pull (was 10).
3. recruiting.room_crowded: a blue-chip will not sign into a room with a full set of younger, better players (STARTERS by
   position); a fallback pass still places anyone nobody had a job for. 76 picks redirected in the dry run. CROWD_SKIPS diag.
5. prestige.components: merit = 0.75*norm(Elo) + 0.25*conference-finish percentile (conf_finish, season_records helpers).
6. prestige PENALTY: losing season -12, last in conference -20, two straight losing seasons -8, same 0.72 decay as bonuses.
7. prestige.targets: quantile_map onto U['prestige_anchor'] (rank-to-value; one team can hold the top; league level fixed).
9. portal: losing_stack entry (+0.07 for a So/Jr/RS backup on a losing programme at prestige>=65); destination weights
   x1.6 where he would start, x0.35 where a full set of better-producing starters is ahead of him (production-visible).
12. prestige.recalibrate(write=True) run ONCE for season 14: within-tier quantile re-fit. Backup state/universe.pkl.pre_recal_s14;
   old values kept in U['prestige_pre_recal_s14']. U['prestige_recal_season']=14 -> carousel skips the yearly step this
   offseason only. G14 after: Eona 92.9, Central Stanton 91.7 ... UN Ediville 55.8, Ciarralotta 50.1; mean 75.9 -> 73.8.
   Biggest moves league-wide: Diamond City 75->60, Roosevelt State 56->43, Kaji Kita 68->78, Costique River 56->68.
WATCH next offseason: blue-chip unsigned count, L6 share, portal volume (losing_stack adds entrants), G14 mean trajectory.

## Injury model recalibrated (Dan's audit, 2039 end) — FORWARD ONLY, from the 2040 season
2039 audit: 848 injuries, 0.43 per team-game, RB 49% of all injuries, OL 0.2% (2 all year), season-enders 0.24/team,
durability trait barely separating players (ball-carrier roll dominated everything).
pbp_engine changes (backup pbp_engine.py.pre_injury_recal): base 0.0034 -> 0.0038; contact on the ball 1.25 -> INJ_BALL 0.85,
catch INJ_CATCH 1.25, tackler 0.6/0.7 -> INJ_TACKLE 1.0, QB run/sack 1.2; POS_RISK RB 0.8, QB 1.3, TE 1.6, OL/DL/DB 1.0;
ambient roll replaced by per-snap exposure (INJ_SNAP_RISK OL .055, DL .042, DB .04, LB .008); durability factor
0.5+1.6x -> 0.35+2.0x; severity minor/med/season 54/28/18 (postseason 70/22/8).
1,000-game sample: 0.64 per team-game; season-enders 1.4 per team-season; shares DL 18 LB 15 RB 15 OL 13 WR 11 S 10 CB 9
TE 4 QB 4; durability bands lo/mid/hi injure at .100/.077/.050 per player per 600 games.
AUDIT at end of 2040 with the G14 balance changes (Dan): volume, shares, season-enders, repeat-injury counts.

## 2039-40 OFFSEASON — Stage 1 of 7 COMPLETE: coaching carousel (re-run on the rebuilt hiring model)
Backups at `state/{season_state,coaches,rosters,universe,sub_coaches}.pkl.pre_s15_carousel`; stored as `s["carousel_s14"]`.
Prestige yearly step SKIPPED this cycle (hand recalibration, prestige_recal_season=14).

### Hiring model rebuilt (Dan, 2039 end) — sitting head coaches were 8% of sim hires vs ~48% of real P5 hires
Sim 2035-39: 100 HC hires = coordinators 55%, first-time 22%, retread 15%, sitting HC 8% (0 in the last two cycles).
Real: P5 hires 2014-21 48% sitting HCs (34% G5 HC, 14% P5 HC), 18% P5 coordinators, 14% internal (AthleticDirectorU);
prior-HC-experience share of all FBS hires 50/58/79% in 2022-25, 56% over the six cycles before (FootballScoop).
Cause: gate (.700 season) admitted ~11 HCs/yr, weighted per head against ~300 coordinators -> 5% of a P6 opening's weight.
Changes in carousel.py:
- gate: skill>=4.5, prestige<78, and (.600 season, or any winning season at an L6 job)
- sitting HCs and subdivision HCs weighted as a CLASS: SHARE_HC = .05+.48*pn (P6 ~40%, L6 ~21%); SHARE_SUB = max(.01,.14-.18*pn)
- subdivision head coaches (sub_coaches.pkl, skill>=4.0) are candidates: the FCS->FBS route; the guest programme backfills
- a sitting HC never leaves for a job >3 prestige smaller unless dream job / alma mater; lateral penalty .15 -> .4; chain damping dropped for HCs
- first-timer weight x(1-pn)^1.5; first-timer quota .28 -> .15; retread/first-timer/sub must clear pool_floor+0.4 (no 0.7 slack)
- HC step-down-to-coordinator "lure" restricted to L6 donors (the first run pulled 9.62 Onawa Khan out of Marblehead's head job)
- CAROUSEL_DEBUG=1 prints class shares per opening
Result: 19 hires — 6 sitting HCs (32%), 11 coordinators, 1 retread, 1 subdivision HC (Apatol -> Orlot Western), 0 first-time.
13 vacancies (5 interims out, 5 offseason firings, 3 retirements) + 6 poach cascades. 38 coordinator moves, 12 raids.
WATCH: real sitting-HC share target ~40% at P6; elite P6 coordinators taking bottom-L6 head jobs (Carlos Lopez 10.00 -> Ediville State).

## Stage 2 of 7 COMPLETE: the 2040 draft
Backups at `state/{season_state,rosters}.pkl.pre_s15_draft`; stored as `s["draft_s14"]`, departures in `departures_s14`.
3,154 declared | 210 picks | 113 early entrants (all juniors) | 7 subdivision | 0 questionable declares.
Departures: 2,256 leaving, 210 drafted, 881 withdrew back to school.
WATCH (flagged to Dan): L6 share of picks is climbing — 62 (2038) -> 70 (2039) -> 80 (2040) of ~200, and 11 of 30 first-rounders.
Real G5 share of NFL picks is ~15-20%. Draft stock blends production with no strength-of-competition discount, so
L6 production against L6 defences grades like P6 production. Candidate fix (forward): scale prod_score by a conference
strength factor (Elo of opponents faced), or by tier (L6 x0.8). Decide before the 2041 draft.
### RE-RUN (Dan): draft re-run with a strength-of-competition discount on production
`draft.schedule_strength`: production x (1 + (mean opponent Elo - league mean)/300), clamped [0.65, 1.25]; G14 1.21, other P6 ~1.0,
L6 0.76-0.87. Result: L6 share 44 of 204 (21.6%, was 80), R1 2 of 30 (was 11). Final 2040 draft: 3,149 declared, 210 picks,
113 juniors, 6 subdivision; departures 2,255 / 210 drafted / 877 withdrew. Backups pre_s15_draft still valid.

## Stage 3 of 7 COMPLETE: the 2040 transfer portal
Backups at `state/{season_state,rosters}.pkl.pre_s15_portal`; stored as `s["portal_s14"]`.
524 entrants | 320 transferred | 204 withdrew. Coach-following: 114 lost a coach, 56 had the destination in pool, 17 followed.
Positions: DL 48, CB 44, S 43, WR 42, TE 38, QB 35, K 20, OL 17, RB 15, P 10, LB 8.
Gainers: Kaji Daun 8, North Verigon 8, Milharvey 7. Losers: Holliday 9, Hughes State 7, Hansenne 7.
NOTE: the new losing_stack entry rule (prestige>=65 AND losing) fired for NOBODY — after the recalibration no losing
programme sits at 65+ (North Hatesei 62.9, Greene 62.0). Consider threshold 58 next year.
WATCH: tier flow is a one-way pump — L6->P6 168 transfers, P6->L6 10. Destination weight is pull^2.1+ with pull ~ prestige,
so the x1.6/x0.35 playing-time factor cannot overcome a 90-vs-30 prestige gap. Real portal traffic runs heavily P5->G5
for playing time. Candidate fix: cap the prestige exponent (pull^1.2) or make the starting-job factor x3 / x0.2.

## North Hatesei pedigree (Dan, 2040 offseason): hand-set to 80.0 (was 62.9 after the recal); backup universe.pkl.pre_nh_floor
prestige.targets now applies a PEDIGREE FLOOR: target >= 0.80 * history component (NH, 21 titles = history 100 -> floor 80).
Only a dynasty-grade past binds (Central Stanton's floor is 38, Greene's 26). Anchor multiset refreshed with NH at 80.
### RE-RUN (Dan): portal re-run after fixing the L6->P6 pump
portal.py: destination exponent k = 1.1 + min(2.1, (val-30)*0.012) (was 2.1-3.0 flat; backups barely weigh prestige, stars
weigh it harder than before); starting-job factor x2.5 / x0.2 (was 1.6/0.35); destination floor scales with prestige
(med * max(0.12, 0.012*P - 0.2), was a flat 1.05*med everywhere -- buried P6 backups could never land anywhere);
star_small entry 0.22 -> 0.16. Final: 498 entrants, 325 transferred, 173 withdrew, 17 followed a coach.
Tier flow P6->L6 47 / L6->P6 141 / P6->P6 61 / L6->L6 76 (was 10 / 168). Stars (val>=150) to P6: 16 of 21. G14 in 33, out 15.

## Stage 4 of 7 COMPLETE: the 2040 recruiting cycle (first under the results-based pull + playing-time rules)
Backups at `state/{season_state,rosters}.pkl.pre_s15_recruiting`; stored as `s["recruiting_s14"]`.
National class 2,775 | needs 1,982 | signed 1,982 | 793 unsigned (all 1-2*, plus 11 four-stars with no cap room anywhere).
Stars in class: 5* 13 | 4* 278 | 3* 971 | 2* 1,110 | 1* 403. Signed: 5* 13 | 4* 267 | 3* 971 | 2* 731.
Blue-chips: G14 55 (69 in 2039), JB 50, PN 41, BS 38, MV 38, WC 37; L6 share 7.5% (canon 4-7%; watch).
114 blue-chip picks redirected by playing time. 18 programmes maxed a 6-haul. G14 bottom four signed one blue-chip each.
Best classes by total stars: Roosevelt 58, Leafette 58, Stanton/UNN/Barhold Valley 53, Kaji Daun 51.
FIXED FORWARD: make_class re-rolls a 4-5* K/P to a field position (2040 had a 5* P and a 5* K).

## Stage 5 of 7 COMPLETE: 2040 development
Backups at `state/{rosters,season_state}.pkl.pre_s15_dev`; stored as `s["development_s14"]`.
7,594 players developed, mean +0.279 (Fr +0.496, So +0.150, Jr +0.148). 377 breakouts, 77 busts. r_coach 0.447 (Fr 0.685).
Biggest jumps: Gareth Hartbrook (QB, Fr, German Shores) +1.84 to 7.63; Isaia Tallshield (S, Fr, Tasson) +1.76 to 7.54;
Omyr Kosei (QB, Fr, Keytommiyr) +1.72. Players rated 9.0+: 28 -> 42. Eona's best class: team mean +0.45.

## Stage 6 of 7 COMPLETE: 2040 roster finalisation
Backups `state/{rosters,season_state}.pkl.pre_s15_rfinal`. departed 2,255 | recruits added 1,982 | walkons 0 | floor fills 261 |
rosters 63-70, total 9,837. All 1,982 signees kept name/stars/rid (first cycle with recruit identity preserved).

## Stage 7 of 7 COMPLETE: rollover, 2039 closed and 2040 open (season 15)
Backups `state/{season_state,rosters,coaches,universe}.pkl.pre_s15_rollover`. Classes now Sr 2,095 | Jr 2,456 | So 2,831 |
RS 212 | Fr 2,243. All 152 HC tenures advanced. Records, injuries, firings, polls, committee/media history reset.
(Rollover writes the season_archive row itself — the hand-written '14' row was only needed early, for prestige's
negative-honours term; the earlier PENDING note that nothing writes it is wrong.)
Preseason top 10: Skeenerland State, Rogaela State, Kaji Daun, Orlot, Central Stanton, Eona, UFNH, Marblehead, Roosevelt, Ranroman.
NEXT: 2040 schedule (noncon board -> conference calendar -> install), week 0.

## 2040 SCHEDULE — stage A: the non-conference board (published 2026-10-12)
`export_schedule_board.py` on the fresh 2040 state; Scheduling Office republished (saves under schedule/s15).
152 programmes | 217 guests | 6 locked cross-conference rivalries pre-filled | 444 dates for Dan to fill.
Unreturned visits 307 pairs (4.0 per programme); 7 series still owed a return ground.
When Dan hands off: fill_noncon.py to even guest parity (~136 guests), then export_conf_board (venue-ledger bleed live),
Conference Office, fill_conf.py, install_hand_schedule.py.

## 2040 non-conference board — COMPLETE (2026-10-12)
Dan's hand-off: 193 games, 68 guests, 138 open dates. fill_noncon added 68 guests + 35 FBS games -> 136 guests (even, 89.47%).
Saved at state/noncon_s15_partial.json. Next: export_conf_board -> Conference Office.

## 2040 SCHEDULE — stage B: conference board built, Conference Office published (saves under conf/s15)
state/noncon_s15.json finalised (296 games, 136 guests). export_conf_board: 12 conferences, 0 problems; 4/5 swap honoured
152/152. First run with the venue ledger live: non-locked hosts 375 behind in series / 187 ahead / 87 level; Coachville
College hosts San Diego Valley (0-10), Dietsche hosts Will Tech (0-6), Eona Navy hosts Repidome (3-11), Marines host
West Hatesei (3-11), Diveo hosts Marblehead (1-7). Will Tech/Tasson locked week 9 with bye week 8 (new rule) — Office still
does not enforce bye_before at placement; fill_conf.py handles it. NEXT: Dan places weeks -> fill_conf -> install_hand_schedule.

## MEDIA POLL REBUILT AS SIXTY VOTERS (Dan, 2040 preseason) — media_pool.py
Each season: 5 programmes drawn per conference -> 60 named voters (bio: age, role, connection, outlet). Traits drawn once:
w_last, w_recruit, w_talent, w_results, inertia, homer (22% negative = underrates own school), rival grudge (55%),
conf bump, 0-3 surprise teams (45/35/15/5%), contrarian (18%), noise. Each files a top 25 weekly from shared facts
(media_pool.team_components, same ingredients as the old formula + a recruiting term); composite = 25..1 points,
ties by #1 votes then mean score. media_poll.compute_media_poll now delegates; old formula kept as _legacy.
State: media_pool_s{N}, media_ballots[week], media_voter_prev, media_points_current, media_firsts_current (rollover clears).
2040 pool stored (media_pool_s15). Preseason dry run: Central Stanton 54 of 60 first-place votes, Eona 5, Kaji Daun 1.
Media Pool artifact: https://claude.ai/artifact/NgkFSTtdoGFS1wFL3K4kLg — export_media_pool.py + media_pool_template.html;
REPUBLISH WEEKLY with the viewer (ballots + composite). Old 0.42-inertia question is moot (inertia is per voter now).
Media pool tuning (2040 preseason): voters per conference 6 P6 / 4 L6; surprise = weekly propensity (no fixed pet teams);
personalities redrawn (21 role types, age-gated; regional pull; offense/defense lean; wider spreads); mid-major darling term
(L6 programme off a big year: (wins-8)*1.6 + 4 conf title + 3 playoff, x voter's w_l6, L6 voters x1.6) after only two L6
teams drew a vote; points table now keeps every team that got a vote. Preseason poll re-run and stored (media_history['pre']).

## 2040 SCHEDULE INSTALLED — 2026-10-13
Dan's hand-off (state/conf_s15_handoff.json): 473 placed (Power North, Jyras Bay, Great Fourteen, Western Coast,
Mountain Valley complete). fill_conf placed the other 507, zero hard violations among open programmes. One violation in
Dan's own rows left as placed: Roosevelt State 4 home in a row, all conference (wk 2-5). Converted to
state/conf_sched_s15.json (980 games) and installed, audit CLEAN; week 0 = 16 games, week 14 = 80. Office db conf/s15
rewritten to the filled board (v620). fill_conf.py paths now derive from the season.
Preseason preview republished (Roiland Preseason artifact) — now in MEDIA POLL order with engine rank + poll points
alongside; 25 notes written to state/preseason_notes.json (2039's kept as preseason_notes_s14.json).
NEXT: Week 0.
RULE (Dan, 2040 preseason): coach, player and coordinator RATINGS are invisible in narrative, previews, and anything not
explicitly "behind the curtain". Preseason page stripped: coach chairs show name + tenure, key players show class only,
freshmen show recruiting stars, engine rank/rating tile and development badge removed; all 25 notes rewritten on
observable facts (records, draft picks, transfers, coaching moves, stats, schedule rank, class size/blue-chips). Weekly
reports and previews must follow the same rule.

## Morning Gameview (Dan, 2040 week 0) — gameview.py
Before each week: `python3 gameview.py <week>` prints 3-4 game-of-the-week candidates (quality from the ranking of record,
records, rivalry/week-14 flags) with a look-ahead penalty when the host campus has a bigger game later in the year and a
heavy penalty for a campus already visited. Dan picks; record with `python3 gameview.py pick <week> <host>` -> s['gameview'].

## 2040 WEEK 0 played (Gameview: North Hatesei at Ciarralotta State)
Media pool fix after week 0: a loss is a headline immediately (loss_pen: 12 + margin*0.4 [cap 12], +8 to an unranked team,
-5 to a top-ten team, +4 shutout, +10 to a guest; a win over a ranked team -7/-12), applied at full weight scaled by the
voter's w_results — the ramped results term alone left Roosevelt #5 after a 13-0 loss at unranked Barhold Valley. Week-0
poll recomputed from the preseason ballots (Roosevelt 5 -> 13, Ciarralotta State 16 -> 22). media_history[0] stored.
STANDING (Dan): after every week's update, automatically give the next week's Gameview candidates.
Media pool: H2H_NUDGE 3.0 — every voter nudges a season head-to-head winner up / loser down when their ballot has the
loser ahead (Dan, 2040 wk 1). Also: be discreet about engine/model references in narrative ("the engine's favourite" etc.).
STANDING (Dan, 2040 wk 11): while the committee ballot is active, Gameview candidates come only AFTER Dan has given
that week's rankings (they are ranked off his board). week_cycle.py still prints them; ignore until the board is installed.

## RULED (Dan, 2040 postseason): DRAFTS ARE 280 PLAYERS
`draft.py` ROUNDS, PICKS = 7, 40 from the 2041 draft on (40-team pro league being built in a separate conversation).
The five canon classes (draft_s10..s14, 210 each) carry 70 supplementary picks each in `s['draft_s{N}']['supplementary']`:
2037-40 reconstructed from pre-draft roster snapshots (best undrafted departing players by the draft's grade formula, seeded jitter);
2036 INVENTED (no snapshot survives). Full record for the pro league: `python3 export_draft_record.py` -> `state/draft_record_sim_era.txt`.
Pro league owns 2027-2035 draft history (lost in the 2035 reset); nothing from it is to be written back here.

## 2040 END-OF-SEASON AUDITS (run 2026-10-16, before the 2040-41 offseason)
G14 balance (options 1,3,5,6,7,9,12 from 2039): conf W% .573 (other P6 .535-.567); non-conf vs P6 10-6 (WC 8-4, MV 8-3, BS 6-5, PN 5-11, JB 4-12);
mean prestige 75.0 (73.8 after recal, 75.9 before); 4 losing seasons + two 6-6; bottom Greene 2-10 (62.0), Pistolheart 4-8, Ranroman 5-7,
Stanton 5-7. Still clearly the best conference, bottom-feeders exist organically. KEEP; recheck prestige drift after 2041.
Injuries 2040 (recalibrated model's first season): 1,353 over 1,015 games = 0.67/team-game (model sample 0.64; 2039 0.43).
Shares DL 18 LB 16 RB 14 OL 13 WR 11 CB 9 S 9 TE 5 QB 5 (2039: RB 49, OL 0.2). Season-enders 278 = 1.83/team (sample 1.4) --
severity 18% of injuries; consider 15% if it feels heavy. Repeat injuries 119 players 2+, 8 with 3+. Per-team 1..18, median 6.
Durability bands lo/mid/hi 0.19/0.13/0.10 injuries per player -- trait now separates. No further change unless Dan asks.

## 2040-41 OFFSEASON -- Stage 1 of 7 COMPLETE: coaching carousel (2026-10-16)
Backups state/{season_state,coaches,rosters,universe,sub_coaches}.pkl.pre_s16_carousel; stored s['carousel_s15']. Prestige yearly step ran (152 moved).
17 vacancies -> 16 hires: 5 sitting HCs poached (31%), 9 coordinators, 2 first-timers, 0 retreads. 29 coach moves, 12 raids.
Headline: Tage Ludendorf leaves national champion Eastern State for Pistolheart (alma mater + dream job, 4-8). Hiring-share audit: sitting-HC
share 31% vs real ~48% / sim-2035-39 8% -- acceptable, leave the model.

## 2040-41 OFFSEASON -- Stage 2 of 7 COMPLETE: the 2041 draft, run by the RFL (2026-10-17)
First draft at 280 (7 x 40). Pool: state/draft_pool_2041.json (3,298 declared: 2,095 Sr, 1,180 early, 23 subdivision) built by
draft.run_draft's declaration logic; picks came back from the pro-league conversation (project doc claude/rfl_draft_2041_picks.json)
and were installed by install_rfl_draft.py -> s['draft_s15'] (with rfl_team on each pick) + draft.mark_departures.
Backups state/{season_state,rosters}.pkl.pre_s16_draft. 2,391 leaving college (280 drafted), 884 early entrants withdrew.
Tier share P6 235 / L6 38 / guest 7 (L6 13.6%, up from 2040's 44/210=21% pre-SOS... 2040 final 44); R1 P6 34 / L6 6; G14 78 picks.
140 early entrants drafted. Most drafted: Rogaela State, Skeenerland State, Ranroman 9 each.
#1 overall Bertram Lorrovei (Orlot) to Vaughn Bay Silverbacks; Rosenwetter #5 (El Latigo), Kitakubo #127, Peymaw #195, Nofonoa #163.
The RFL grades differently from the sim's board -- expected and fine; the sim's board is a placeholder.

## 2040-41 OFFSEASON -- Stage 3 of 7 COMPLETE: transfer portal (2026-10-17)
Backups state/{season_state,rosters}.pkl.pre_s16_portal; s['portal_s15']. 408 entrants, 271 transfers, 137 no takers.
Flows L6->P6 105 / P6->P6 65 / P6->L6 39 / L6->L6 62 (2040: 141/61/47/76). Stars (val>=150) 20, 16 to P6. G14 in 48 / out 19 (2040: 33/15 -- WATCH).
Classes So 115 Fr 93 Jr 56 RS 7. 6 followed a coach (2 to Pistolheart with Ludendorf). Headline: FOY Sami Amajide (Vaughn Bay) to Parchynt.
AUDIT NOTE: G14 net +29 via portal two years running; recruiting caps apply to signings, not transfers. Consider a transfer-in cap or
prestige-scaled portal pull for G14 at the 2041 audit.

## 2040-41 OFFSEASON -- Stage 4 of 7 COMPLETE: 2041 recruiting (2026-10-17)
Backups state/{season_state,rosters}.pkl.pre_s16_recruiting; stored s['recruiting_s15'] (same shape as s14).
National class 2,866 | needs 2,130 | signed 2,130 | 736 unsigned (17 four/five-stars found no cap room -- 2040: 11).
Class 5* 13 | 4* 287 | 3* 1,003 | 2* 1,146 | 1* 417. Signed 5* 13 | 4* 270 | 3* 1,003 | 2* 844.
Blue-chips: G14 56 (55 in 2040), PN 44, JB 43, MV 41, WC 39, BS 38; L6 share 7.8% (7.5%; canon 4-7, WATCH).
Five-stars went to 13 different programmes (Eternal Fox and Will Tech among them). G14 bottom: Pistolheart 1, Ciarralotta 1, Greene 0.
Best classes by stars: Stanton State 61, Phangrine State 61, Rogaela State 60, Costique River 57, Kaji Daun 56.

## 2040-41 OFFSEASON -- Stage 5 of 7 COMPLETE: 2041 development (2026-10-17)
Backups state/{rosters,season_state}.pkl.pre_s16_dev; s['development_s15']. 7,446 players, mean +0.252 (Fr +0.492, So +0.190, RS +0.183, Jr +0.090).
290 breakouts, 81 busts, r_coach 0.529. Best team development: Rogaela State / Pistolheart / Orlot +0.39 (Pistolheart under Ludendorf's staff).
Biggest jumps: Isla Albabosque (OL Fr, National) +1.61; Shufen Teramura (OL Fr, UNN) +1.53; Latoya Waddell (QB Fr, Tengus State) +1.50.
Players rated 9.0+: 15 (42 before the draft took the seniors).

## 2040-41 OFFSEASON -- Stage 6 of 7 COMPLETE: 2041 roster finalisation (2026-10-17)
Backups state/{rosters,season_state}.pkl.pre_s16_rfinal. departed 2,391 | recruits added 2,130 | walkons 0 | floor fills 311 | trimmed 0 |
rosters 63-69, total 9,887. No _leaving flags remain. Rollover (stage 7) pending.

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
