# Exhibit map: every claim the report will make, and what supports it

No report prose here. Paths are relative to the project folder. "Key number" is the figure the claim rests on, as produced by the pipeline (a full `python run_all.py` from an empty `outputs/` reproduced the top-10 files byte for byte).
Status: **supported** = exhibit exists and backs the claim; **caveat** = supported but the report states the caveat. No item is open: all decisions were made (see CHANGES_FOR_REVIEW.md #33a and #41).

## Page 1: The answer

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 1.1 | Top-10 batters, in rank order | outputs/top10_batters.csv | Klaasen, Suryakumar Yadav, Tim David, Abhishek Sharma, Salt, Shreyas Iyer, Tilak Varma, Sai Sudharsan, Pooran, Gill | supported |
| 1.2 | Top-10 bowlers, in rank order | outputs/top10_bowlers.csv | Narine, Kuldeep Yadav, Rashid Khan, Varun Chakravarthy, Hazlewood, Hasaranga, Bumrah, Axar Patel, Noor Ahmad, Krunal Pandya | supported (sign check amended, see 6.5) |
| 1.3 | Lists come from one generated file that also feeds the report tables | outputs/top10_*.csv, outputs/report_tables.md | | supported |
| 1.4 | Sample size | outputs/audit_stage1.md (rating sample), outputs/audit_stage2c.md, outputs/audit_stage4.md | 728 matches (353 IPL, 375 T20I); 156,062 live balls; 31,263 pressure balls | supported |
| 1.5 | Headline reliability numbers | outputs/reliability.md | split-half pressure rating 0.54 batters, 0.66 bowlers; pressure shift 0.13, 0.15 | caveat |
| 1.6 | Method in five lines | blueprint stages 2 to 7; config.yaml | | supported |
| 1.7 | Every listed player has P(top 20) of at least 0.6 and none is fragile | outputs/audit_stage7.md, top10_*.csv columns p_top20, fragile | 0 listed players below 0.6; 0 fragile of 20 | supported |

## Page 2: Pressure definition

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 2.1 | Pressure = expected absolute swing in win probability on the next ball, scaled so an average live ball is 1 | src/stage2c_leverage.py; outputs/pressure_thresholds.json | mean swing on live balls 0.0144 | supported |
| 2.2 | A ball is "live" when WP* is between 0.02 and 0.98 | config.yaml `pressure`; outputs/audit_stage2c.md | live share 99.7% innings 1, 78.0% innings 2 | supported |
| 2.3 | Pressure ball = leverage in the top 20% of live balls, pooled across both innings | outputs/pressure_thresholds.json | cutoff LI 1.207 (median 0.834, 95th pct 1.995) | supported (pooled cutoff kept; within-innings is a sensitivity variant) |
| 2.4 | The definition uses no hand-picked weights and no final margin | src/wp_engine.py (exact backward induction), src/stage2c_leverage.py | | supported |
| 2.5 | Leverage heatmap by runs required and over (innings 2), and by over and wickets (innings 1) | figures/stage3_where_pressure_lives.png | | supported |
| 2.6 | Pressure is almost entirely a live chase under the pooled cutoff | outputs/audit_stage2c.md "By innings" | innings 1: 98 pressure balls (0.1%); innings 2: 37.2% of all balls, 47.7% of live | caveat |
| 2.7 | 75% of pressure balls fall before over 16 | outputs/audit_stage2c.md; figures/stage3_where_pressure_lives.png (right panel) | 75.4% | caveat |
| 2.8 | The definition agrees only moderately with the published pressure index | outputs/audit_stage3.md "Benchmark agreement" | Spearman 0.328 on live chase balls | caveat |
| 2.9 | The simple rule-of-thumb set is much narrower than the pressure set | outputs/audit_stage3.md | 92.6% of rule-of-thumb chase balls are pressure; only 16.4% of pressure chase balls are in the rule | supported |
| 2.10 | The published index's resources-used term is replaced by one derived from our scoring model | CHANGES_FOR_REVIEW.md #14 | | caveat |

## Page 3: Proof that it captures pressure

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 3.1 | Pressure balls differ from ordinary balls within phase and wickets band | outputs/audit_stage3.md (shift table); figures/stage3_separation.png | gate passes in 3 of 3 phases | supported |
| 3.2 | Powerplay: more boundaries, fewer dots, more runs | outputs/audit_stage3.md | boundary +1.9 pts, dot -4.5 pts, runs +0.117 per ball (intervals exclude 0) | supported |
| 3.3 | Middle overs: more dismissals and boundaries | outputs/audit_stage3.md | dismissal +0.9 pts, boundary +1.4 pts | supported |
| 3.4 | Death overs: more dismissals and more runs | outputs/audit_stage3.md | dismissal +2.1 pts, runs +0.113 per ball; boundary difference not significant | supported |
| 3.5 | Batters play fewer defensive and more attacking strokes under pressure | outputs/audit_stage3.md (behaviour rows) | defensive -2.7 pts powerplay, -1.5 middle, -1.3 death; attacking +3.0 pts death | supported |
| 3.6 | Bowlers use more yorkers and slower balls under pressure | outputs/audit_stage3.md | yorker +2.2 pts death, +0.7 middle; slower +1.2 powerplay, +1.4 middle | supported |
| 3.7 | Pressure concentrates in games that finished tight although margin is never an input | figures/stage3_close_games.png; outputs/audit_stage3.md | 137 close matches: median peak LI 10.1 vs 1.6; Spearman -0.85 between peak LI and runs margin | supported |
| 3.8 | The index spikes where a cricket watcher expects | figures/stage3_case_studies.png | 3 tight finishes, 3 one-sided chases | supported |
| 3.9 | Win probabilities are calibrated out of sample | figures/stage2_calibration.png; outputs/audit_stage2.md | max decile gap 4.2 pts (innings 1), 2.3 pts (innings 2); 95% match-bootstrap intervals about plus or minus 5 pts | caveat |
| 3.10 | The win-probability model beats a one-feature baseline | outputs/audit_stage2.md | Brier 0.2193 vs 0.2294 (innings 1); 0.1270 vs 0.1490 (innings 2) | supported |
| 3.11 | The exact model is over-confident and is recalibrated | outputs/step3_reports.md (c) | slope c = 0.733 (innings 1), 0.804 (innings 2) | supported |
| 3.12 | The scoring model reproduces outcome frequencies | outputs/audit_stage2.md | worst cell gap 0.66 pts (innings 1), 0.42 pts (innings 2) | supported |
| 3.13 | Late-chase surface noise is removed by a monotone projection at no Brier cost | outputs/audit_stage2.md; CHANGES_FOR_REVIEW.md #6, #12 | largest violation 0.077 before, 0 after | supported |
| 3.14 | Start-of-chase calibration by target, and where it is weaker | outputs/audit_stage2.md, figures/stage2_calibration.png | over-predicts chasing sides for associates by 8.7 pts (52 matches) and A-teams by 5.4 pts (30 matches); IPL -0.1 pts, full-member T20I +2.3 pts | caveat |

## Page 4: Performance measurement

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 4.1 | Each ball is valued by its win-probability change against the average in the same state, scaled by leverage | src/rating_model.py `event_rows`; CHANGES_FOR_REVIEW.md #19, #20 | | supported |
| 4.2 | Credit table: who is credited or charged for each event | src/rating_model.py; CHANGES_FOR_REVIEW.md #19 | | caveat (implementation choices) |
| 4.3 | One ridge model for batters and bowlers with baseline, pressure shift and opposition terms | src/rating_model.py; outputs/audit_stage4.md | 150,307 batter rows; 156,062 bowler rows | supported |
| 4.4 | Penalties chosen by 5-fold cross-validation with whole matches held out | outputs/audit_stage4.md (CV grid) | lambda_B = 300, lambda_C = 3000 | supported |
| 4.5 | The pressure-shift penalty is ten times the baseline penalty | outputs/audit_stage4.md | 10x | supported |
| 4.6 | Ratings track conventional statistics | outputs/audit_stage4.md (gates) | batter baseline vs strike rate rho 0.708 (n=53); bowler baseline vs economy rho -0.795 (n=56) | supported |
| 4.7 | Baseline versus pressure rating | figures/stage8_ratings_scatter.png (top row) | pressure ratings sit almost on the baseline line | supported |
| 4.8 | Companion statistics on pressure and ordinary balls | outputs/player_ratings_batters.csv, player_ratings_bowlers.csv | strike rate, runs index, dismissal ratio, economy, economy index, wicket ratio | supported |
| 4.9 | Net value of a bowler on pressure balls in runs | outputs/bowler_net_value.csv; outputs/step2_bowler_net.md | wicket worth 8.1 runs on average; e.g. Rashid Khan +152, Narine +103, Bumrah +5 | caveat |

## Page 5: Fair comparisons

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 5.1 | Rating sample is IPL and full-member T20Is with no rain or truncation flag | outputs/audit_stage1.md (rows removed, matches by group) | 728 matches | supported |
| 5.2 | Rows removed by each cleaning rule | outputs/audit_stage1.md | 38 super-over rows; no-result, rain and truncated matches logged | supported |
| 5.3 | Eligibility rule (120 pressure balls, 15 matches), fixed in config before any leaderboard | config.yaml `rating.eligibility` | 53 batters and 56 bowlers eligible; 53 and 55 also active | supported |
| 5.4 | Active-player filter: at least one match in 2025 or 2026 | config.yaml; outputs/audit_stage5.md; outputs/unfiltered_eligible_*.csv (appendix list) | | supported |
| 5.5 | Small samples are shrunk by the ridge penalties | outputs/audit_stage4.md (spread table); outputs/audit_stage5.md | baseline SD about 0.06, shift SD 0.004 to 0.008 | supported |
| 5.6 | Opposition quality is adjusted for; the adjustment barely changes the ranking | outputs/audit_stage5.md (cross-check); figures/stage8_ratings_scatter.png (bottom row) | Spearman vs simple unadjusted version 0.970 batters, 0.984 bowlers | supported |
| 5.7 | IPL and T20I are rated on one scale with a competition-group term | src/rating_model.py `Design`; outputs/audit_stage6b.md (IPL-only, T20I-only) | top-10 overlap with main: IPL-only 6 batters / 8 bowlers; T20I-only 6 / 7 | caveat |
| 5.8 | Venue and era are controlled in the scoring model | config.yaml `scoring_model.use_env_tier`; CHANGES_FOR_REVIEW.md #4 | env_tier kept | supported |
| 5.9 | Batting position does not change the ranking | outputs/sensitivity.csv | batters overlap 10 of 10, Kendall 0.983 | supported |
| 5.10 | Lower-tier (associate, A-team) matches do not change the ranking | outputs/sensitivity.csv | overlap 10 of 10 both roles | supported |
| 5.11 | Players are keyed by player_id; duplicated names are checked | outputs/audit_stage7.md; outputs/top10_bowlers.csv column duplicate_name | Rashid Khan has two ids; list uses 4722 | supported (flagged in submission_sheet.csv; manual dropdown check by the submitter) |

## Pages 6 and 7: Evidence for the top 10

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 6.1 | Ranking rule: eligible and active; drop reliably negative shifts; sort by bootstrap floor; ties by delivery rate, then pressure balls | outputs/audit_stage7.md | | supported |
| 6.2 | Each listed player has a card with sample, rating and interval, cricket numbers, consistency and best pressure match | outputs/evidence_cards.md | 20 cards | supported |
| 6.3 | Players removed for a reliably negative shift, with their baseline ranks | outputs/step3_reports.md (b) | 6 batters (baseline ranks 17 to 50), 7 bowlers (30 to 49) | supported |
| 6.4 | Floor ranking on baseline alone nearly matches the main ranking | outputs/step3_reports.md (a) | batters 9 of 10 (Buttler for Gill); bowlers 10 of 10 | caveat |
| 6.5 | Bowler sign check is economy index above 100 OR wicket ratio above 1 (post-hoc amendment 33a); the original rule fails for two bowlers | outputs/audit_stage7.md; outputs/step2_bowler_net.md; CHANGES_FOR_REVIEW.md #33, #33a | Hasaranga economy index 94.8, Noor Ahmad 91.5; wicket ratios 1.34 and 1.39; 0 of 20 fail the amended check | caveat (post hoc) |
| 6.6 | Strict-rule bowler list (the two exceptions dropped, ranks 11 and 12 promoted) | outputs/strict_rule_bowlers.csv; outputs/step2_bowler_net.md | adds Mujeeb Ur Rahman and Bhuvneshwar Kumar | supported (appendix table) |
| 6.7 | Net value shows some listed bowlers add little on pressure balls | outputs/bowler_net_value.csv | Bumrah +5 runs (interval -68 to +86), Noor Ahmad +0.1, Hasaranga +17 | caveat |
| 6.8 | Spinners are over-represented among listed bowlers | outputs/step3_reports.md (d) | 8 of 10 listed vs 20 of 55 in the pool; spinners bowl 35.0% of pressure balls vs 37.2% of live balls | supported |

## Page 8: Reliability

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 8.1 | Pressure rating is reliable across random match halves | outputs/reliability.md | 0.536 batters, 0.662 bowlers (Spearman-Brown, 200 splits) | supported |
| 8.2 | The pressure shift on its own is not reliable | outputs/reliability.md | 0.130 batters, 0.150 bowlers (below the 0.25 line) | supported |
| 8.3 | Baseline reliability is as high as pressure-rating reliability, so the rating is mostly general quality | outputs/reliability.md | baseline 0.531 / 0.662 vs pressure rating 0.536 / 0.662 | supported |
| 8.4 | Season to season: bowlers persist, batters do not | outputs/reliability.md | bowlers r = 0.511 (95% CI 0.25 to 0.72, n=37); batters r = 0.048 (CI -0.23 to 0.32, n=34) | caveat |
| 8.5 | An earlier pressure shift does not predict later pressure value | outputs/reliability.md | interval includes zero for both roles | supported |
| 8.6 | Permutation test gives weak evidence that players differ under pressure | outputs/reliability.md | p = 0.062 batters (not beyond 95th pct), 0.048 bowlers (just beyond) | caveat |
| 8.7 | Rank stability: P(top 10), P(top 20) and 80% rank intervals | outputs/top10_*.csv; outputs/evidence_cards.md | all listed have P(top 20) of at least 0.6 | supported |
| 8.8 | Sensitivity grid: 14 variants, median top-10 overlap 9 of 10 | outputs/sensitivity.csv; outputs/audit_stage6b.md | min overlap 6 (IPL-only or T20I-only batters) | supported |
| 8.9 | Winsorised ball values do not change the ranking | outputs/sensitivity.csv | overlap 10 of 10 both roles; Kendall 0.978 batters, 0.957 bowlers | supported |
| 8.10 | Recency weighting moves two batters | outputs/step3_reports.md (e) | overlap 8 of 10: Pooran and Gill out, Kishan and Kohli in | supported |
| 8.11 | Fragile flags | outputs/top10_*.csv column fragile, variants_in_top10 | 0 fragile; lowest is Gill at 7 of 14 variants | supported |
| 8.12 | Win probability without recalibration was not run as a variant | outputs/audit_stage6b.md | | caveat |

## Page 9: Limitations

| # | Claim | Exhibit | Key number | Status |
|---|-------|---------|------------|--------|
| 9.1 | Team scores are rebuilt from partly missing extras; checked against public scorecards | outputs/audit_stage1.md (external totals table); data_external/external_totals.csv | mean error -1.00 runs; 29 of 30 totals within 5; chase totals run about 2 low | supported |
| 9.2 | Margin and wicket reconciliation of the rebuild | outputs/audit_stage1.md (gates) | margin median error 0, 95th pct 4; wickets match in 403 of 404 chases | supported |
| 9.3 | One result string is wrong (match 20190) | outputs/audit_stage1.md notes; CHANGES_FOR_REVIEW.md | public scorecards: 5-wicket win, text says 6 | supported |
| 9.4 | Win probability is team-neutral | outputs/audit_stage2.md (start of chase by group) | associates and A-teams over-predicted | supported |
| 9.5 | Fielding is invisible; non-strikers and partnerships get no credit | blueprint limitations | | supported |
| 9.6 | Who faces pressure is not random | blueprint limitations | | supported |
| 9.7 | No World Cup and only 31 knockout matches, so tournament pressure is untested | outputs/matches_flags.csv; blueprint data section | 31 knockout matches | supported |
| 9.8 | Few players qualify, so pools are small | outputs/audit_stage5.md | 53 batters, 56 bowlers eligible | supported |
| 9.9 | Pressure ratings reflect general quality in live situations, not a separable clutch trait | exhibits 8.1 to 8.6 | | supported |
| 9.10 | Ball values have heavy tails (wicket balls reach plus or minus 15); results are unchanged when capped | outputs/audit_stage4.md; exhibit 8.9 | | supported |
| 9.11 | Win-probability calibration tolerance (5 pts) is about as wide as its sampling noise | outputs/audit_stage2.md (bootstrap intervals) | | caveat |

## Appendix: Reproducibility

| # | Claim | Exhibit |
|---|-------|---------|
| A.1 | One command regenerates every table, chart and list; fixed seed | run_all.py; config.yaml `seed`; top-10 files identical after a rerun from an empty outputs folder |
| A.2 | All thresholds live in one config file | config.yaml |
| A.3 | Extras decoding, backward anchor, result parsing and rain/truncation rules | src/stage0_1.py; outputs/audit_stage1.md |
| A.4 | Every departure from the blueprint and every judgement call | CHANGES_FOR_REVIEW.md |
| A.5 | Full eligible table and the unfiltered (not active-filtered) list | outputs/eligible_table_*.csv, outputs/unfiltered_eligible_*.csv |
| A.6 | Per-stage audits with gate results | outputs/audit_stage1.md, 2, 2c, 3, 4, 5, 6 (reliability.md), 6b, 7 |

## Deliverables built from this map

| File | What it is |
|---|---|
| report.md, report.pdf | Draft report; every number is read from a generated file by src/build_report.py |
| submission_sheet.csv | Rank, name, player_id and team for all 20 players; flags names with two ids |
| FINAL_LOCK.md | SHA-256 of config.yaml and both top-10 files |
