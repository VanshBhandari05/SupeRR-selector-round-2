# 02 METHOD AS RUN: what the final pipeline actually did, stage by stage

Parameters come from `config.yaml` (copied into this pack as `config.yaml`; SHA-256 in `FINAL_LOCK.md`) and the audit files named under each heading. This describes what RAN, not what the blueprint planned; departures are in `00_DEVIATIONS.md`.

## Stage 0 and 1: ingest, clean, rebuild the match state

Source: `outputs/audit_stage1.md`.

- Raw file: 200,999 rows, 867 matches. Output table: 193,076 rows, 808 matches, of which **728 matches form the rating sample** (IPL 353, T20I full-member 375) and **7 are ties** that are kept. Competition groups are tagged by id, not name (config `competition`): IPL ids [1358, 1715, 2193, 2725, 3298], A-team ids [2670, 3289], full-member team ids list in config. Competition tags over the 883 matches listed in `matches.csv` (16 have no ball data): T20I-full 428, IPL 371, T20I-assoc 54, A-team 30. Clean matches by group: T20I-full 375, IPL 353, T20I-assoc 50, A-team 30. **Associate and A-team matches fit the scoring model only; they never rate players.**

**Exclusions by rule (applied in this order):**

| rule                             |   rows removed |   matches |
|:---------------------------------|---------------:|----------:|
| innings > 2 (super overs)        |             38 |         6 |
| no result                        |           1753 |        24 |
| rain                             |           4726 |        28 |
| truncated                        |           1406 |         7 |
| no ball data (abandoned, 0 rows) |              0 |        16 |

Rules as configured: super overs = innings > 2; no result = regex `no result|abandon`; rain = regex `d/l|dls` (38 matches flagged; 28 matches are removed at the rain step after the earlier rules); truncation = 7 matches flagged ([14130, 14164, 15795, 18532, 31278, 48514, 50407]); tie regex `super over|tied|eliminator`. Result parser: 419 wins by wickets, 414 by runs, 40 no results, 10 ties.

**Rebuilt state (the data omit bye, leg-bye and wide-extra runs, so team runs are rebuilt):**

- Team runs per ball = bat runs + 1 for a wide or no-ball + `extras_2_runs` + imputed bye/leg-bye runs + wide-run rotation + 5 for a penalty. A bye/leg-bye that did not rotate strike is imputed **4** runs; where rotation is unknowable (final ball of an innings or a wicket ball: **59 rows**) it is imputed **1**. `extras1_runs` is a type code, never runs (config `extras_codes`).
- Strike rotation is inferred from the next ball's striker; it agrees with bat-run parity on 0.99977 of 170,306 normal balls.
- **Backward anchor** (`src/stage0_1.py` lines 198 to 210): runs required before ball 1 of the chase is anchored on the stated result: for a chase won by wickets, `target` = the forward target (rebuilt first-innings total + 1) clipped to lie between the rebuilt chase total minus (runs on the last ball - 1) and the rebuilt chase total; for a chase that LOST by runs, `target = rebuilt chase total + margin + 1`; for ties, rebuilt chase total + 1. So the target absorbs any error in the rebuilt chase total.
- Other imputations: one dismissed player id inferred (match 40709 innings 2 ball 117 set to player 7897); `balls_left` = 120 minus legal balls bowled (match 41509 has a mislabelled over, handled by this rule); batting position clipped at 11.
- Validation against public scorecards (15 matches, seed 42): mean error -1.00 runs, 29 of 30 totals within 5 runs; rebuilt margins differ from stated margins by a median 0.0 runs (95th percentile 4.0, max 8.0).
- `env_tier`: leave-one-out venue scoring rate shrunk toward the group-season rate with 1200 pseudo-balls, cut into 3 terciles within each competition group.

## Stage 2: scoring model, win probability, leverage and the pressure flag

Source: `outputs/audit_stage2.md`, `audit_stage2c.md`, `pressure_thresholds.json`, `stage2_choices.json`, `step3_reports.md` (c).

- **Scoring (next-ball) model inputs:** over band (10 bands starting at overs [1, 2, 4, 7, 10, 13, 16, 18, 19, 20]), wickets lost (0 to 6, then 7+), required-rate band in innings 2 (edges [6, 8, 10, 12, 15]), venue scoring tier (`env_tier`, kept), competition group, impact-player rule. One multinomial logistic regression per innings, inverse regularisation C = 0.1 (fixed, CHANGES #5), fitted on all 808 clean matches.
- **Outcome classes (10):** legal ball: wicket, 0, 1, 2, 3, 4, 6; illegal ball: 1, 2, 3+ runs. Wickets on wides/no-balls fold into the wicket class; 5 runs on a legal ball folds into the 4 class (CHANGES #8).
- **Win probability:** exact backward induction over match states using the next-ball model (innings-1 states: score, balls left, wickets; chase states: runs required, balls left, wickets), then **recalibrated** on out-of-fold (leave-one-season-out) predictions: `logit(WP*) = a + c x logit(WP)`. Chase surface projected to be monotone (used; Brier loss 0.00000).

**Recalibration parameters** (`audit_stage2.md`):

|   innings |       a |      c |
|----------:|--------:|-------:|
|    1.0000 | -0.0468 | 0.7332 |
|    2.0000 |  0.1526 | 0.8042 |

- **Leverage:** `swing(s) = sum_o p(o|s) |WP*(after o) - WP*(s)|` and `LI(s) = swing(s) / mean swing over live balls` (mean swing on live balls = 0.014414, `pressure_thresholds.json`).
- **Live-ball bounds:** a ball is live when 0.02 < WP* < 0.98. Live share: 99.7% of innings-1 balls, 78.0% of innings-2 balls.
- **Pressure cutoff:** LI >= **1.2073** = the 80th percentile of live-ball LI, pooled across both innings (so the top 20% of live balls). Median live LI 0.8336; 95th percentile 1.9954; maximum LI 30.19.
- **Number and share of pressure balls:** 34,494 of 193,076 clean balls (17.9%; 20.0% of live balls). In the 728 rated matches: **31,263** pressure balls of 156,062 live (20.0%). **Pressure balls outside overs 16 to 20: 75.4%.**

By innings (all clean balls):

|   innings |       balls |   live_share |   pressure_share_all |   pressure_share_of_live |   mean_LI_live |
|----------:|------------:|-------------:|---------------------:|-------------------------:|---------------:|
|    1.0000 | 100615.0000 |       0.9970 |               0.0010 |                   0.0010 |         0.7422 |
|    2.0000 |  92461.0000 |       0.7804 |               0.3720 |                   0.4767 |         1.3584 |

By over (all clean balls; share of balls in that over that are pressure balls):

|   innings |   over_b |     balls |   pressure_share |   mean_LI |
|----------:|---------:|----------:|-----------------:|----------:|
|    1.0000 |   1.0000 | 5113.0000 |           0.0000 |    0.7157 |
|    1.0000 |   2.0000 | 5087.0000 |           0.0000 |    0.8869 |
|    1.0000 |   3.0000 | 5024.0000 |           0.0000 |    0.8570 |
|    1.0000 |   4.0000 | 5027.0000 |           0.0000 |    0.8856 |
|    1.0000 |   5.0000 | 5015.0000 |           0.0000 |    0.8582 |
|    1.0000 |   6.0000 | 5011.0000 |           0.0000 |    0.8302 |
|    1.0000 |   7.0000 | 4970.0000 |           0.0000 |    0.6462 |
|    1.0000 |   8.0000 | 5003.0000 |           0.0000 |    0.6293 |
|    1.0000 |   9.0000 | 4998.0000 |           0.0000 |    0.6121 |
|    1.0000 |  10.0000 | 5015.0000 |           0.0000 |    0.6697 |
|    1.0000 |  11.0000 | 5032.0000 |           0.0000 |    0.6518 |
|    1.0000 |  12.0000 | 5033.0000 |           0.0000 |    0.6307 |
|    1.0000 |  13.0000 | 5050.0000 |           0.0000 |    0.7073 |
|    1.0000 |  14.0000 | 5029.0000 |           0.0000 |    0.6778 |
|    1.0000 |  15.0000 | 4995.0000 |           0.0000 |    0.6511 |
|    1.0000 |  16.0000 | 5060.0000 |           0.0000 |    0.7369 |
|    1.0000 |  17.0000 | 5097.0000 |           0.0000 |    0.7127 |
|    1.0000 |  18.0000 | 5074.0000 |           0.0000 |    0.7631 |
|    1.0000 |  19.0000 | 5084.0000 |           0.0057 |    0.8156 |
|    1.0000 |  20.0000 | 4898.0000 |           0.0141 |    0.8649 |
|    2.0000 |   1.0000 | 5063.0000 |           0.1313 |    0.9336 |
|    2.0000 |   2.0000 | 5101.0000 |           0.4009 |    1.0319 |
|    2.0000 |   3.0000 | 5032.0000 |           0.3754 |    0.9940 |
|    2.0000 |   4.0000 | 5044.0000 |           0.4931 |    1.0583 |
|    2.0000 |   5.0000 | 5042.0000 |           0.4865 |    1.0335 |
|    2.0000 |   6.0000 | 5012.0000 |           0.4723 |    1.0160 |
|    2.0000 |   7.0000 | 4962.0000 |           0.1249 |    0.7786 |
|    2.0000 |   8.0000 | 4988.0000 |           0.1714 |    0.7671 |
|    2.0000 |   9.0000 | 4968.0000 |           0.2083 |    0.7716 |
|    2.0000 |  10.0000 | 4947.0000 |           0.3560 |    0.8491 |
|    2.0000 |  11.0000 | 4892.0000 |           0.3708 |    0.8574 |
|    2.0000 |  12.0000 | 4869.0000 |           0.3857 |    0.8579 |
|    2.0000 |  13.0000 | 4822.0000 |           0.4378 |    0.9823 |
|    2.0000 |  14.0000 | 4765.0000 |           0.4269 |    0.9930 |
|    2.0000 |  15.0000 | 4645.0000 |           0.4297 |    1.0456 |
|    2.0000 |  16.0000 | 4518.0000 |           0.4376 |    1.1772 |
|    2.0000 |  17.0000 | 4255.0000 |           0.4494 |    1.2615 |
|    2.0000 |  18.0000 | 3905.0000 |           0.4699 |    1.5388 |
|    2.0000 |  19.0000 | 3338.0000 |           0.4856 |    1.9119 |
|    2.0000 |  20.0000 | 2293.0000 |           0.4540 |    3.3509 |

In the rated matches only: innings 1 has **78** pressure balls and innings 2 has **31185** (`website/data/meta.json`). Pressure is essentially a live chase under the pooled cutoff (CHANGES #17); the 'within-innings' cutoff is a sensitivity variant.

## Stage 3: proving the pressure definition

Run as described in `03_EVIDENCE_DEFINITION.md`. Settings: phases [6, 15] (powerplay 1-6, middle 7-15, death 16-20), wickets bands [2, 5] (0-2, 3-5, 6+), min 30 balls per cell on each side, 300 match bootstrap resamples; close = tie, or won by <= 10 runs, or <= 3 wickets.

## Stage 4: ball value, credit split, rating regression

Source: `src/rating_model.py`, `outputs/audit_stage4.md`, CHANGES #19 to #24, `report.md` section 4.

- **Ball value:** `dWP` is the change in the batting side's win probability (WP*). Subtract the mean `dWP` of balls in the same state bin (innings x over band x wickets band x leverage band; computed separately for batter and bowler rows), then divide by the ball's `swing`: `v = (dWP - mean dWP in bin) / swing`.

- **Credit table (who is credited or charged for each event):** Runs off the bat go to the striker and are charged to the bowler; wides are charged to the bowler only; no-balls charge the bowler the bat runs and the penalty run; byes and leg-byes count as dot balls for both; wickets are charged to the dismissed batter (including non-strikers run out, who get their own row) and credited to the bowler for bowled, caught, lbw, hit wicket and stumpings; run-outs and obstructing the field are not credited to the bowler; retire-outs are charged to nobody.

  - Implementation choices beyond the blueprint table (CHANGES #19): no-ball batter credit = WP*(after) minus WP*(after a lone penalty run); non-striker dismissals get their own row valued at the wicket's incremental effect; retire-out balls valued as if no wicket; bye/leg-bye valued as a dot ball for both sides; penalty rows excluded.

- **Regression form:** two ridge regressions, one on balls faced (150,307 batter rows) and one on balls bowled (156,062 bowler rows), live balls of the 728 rated matches:

  `batting:  v = context + B_i + P x C_i - (W_j + P x K_j)`   `bowling:  v = context + W_j + P x K_j - (B_i + P x C_i)`

  `i` batter, `j` bowler, `P` = 1 on pressure balls. `B`/`W` baselines, `C`/`K` pressure shifts. **Pressure rating = baseline + shift.** Context fixed effects = innings x phase x P (12 terms) + competition group (IPL vs T20I); context penalty 0.001. Opposing players' terms in the same regression adjust for opposition quality.

- **Chosen penalties:** lambda_B = 300 (baselines), lambda_C = 3000 (shifts); held-out MSE 3.04371. **How chosen:** 5-fold cross-validation with whole matches held out, loss = summed held-out squared error of both fits; grid lambda_B [30, 100, 300, 1000, 3000, 10000], lambda_C [300, 1000, 3000, 10000, 30000, 100000]; neither optimum is on the grid edge. Shift penalty / baseline penalty = 10.0x. CV grid:

|     lambda_B |      300 |     1000 |     3000 |    10000 |    30000 |   100000 |
|-------------:|---------:|---------:|---------:|---------:|---------:|---------:|
|    30.000000 | 3.050405 | 3.049994 | 3.049955 | 3.049959 | 3.049963 | 3.049964 |
|   100.000000 | 3.046072 | 3.045664 | 3.045627 | 3.045632 | 3.045636 | 3.045638 |
|   300.000000 | 3.044153 | 3.043748 | 3.043715 | 3.043722 | 3.043727 | 3.043729 |
|  1000.000000 | 3.044296 | 3.043922 | 3.043913 | 3.043932 | 3.043941 | 3.043944 |
|  3000.000000 | 3.045710 | 3.045451 | 3.045511 | 3.045563 | 3.045582 | 3.045589 |
| 10000.000000 | 3.047057 | 3.046945 | 3.047092 | 3.047186 | 3.047218 | 3.047230 |

Spread of ratings after shrinkage:

| role    |   sd_baseline |   sd_shift |   sd_baseline_eligible |   sd_shift_eligible |
|:--------|--------------:|-----------:|-----------------------:|--------------------:|
| batters |        0.0534 |     0.0037 |                 0.0628 |              0.0085 |
| bowlers |        0.0538 |     0.0042 |                 0.0667 |              0.0084 |

Ball values: batter rows 150,307, bowler rows 156,062; v quantiles {0.0: -14.86, 0.001: -10.145, 0.01: -7.764, 0.25: -0.478, 0.5: -0.072, 0.75: 0.428, 0.99: 3.771, 0.999: 4.496, 1.0: 5.709}

Eligible batters 53, bowlers 56. (Fallback used: batters False, bowlers False.)

## Stage 5: fair comparison

Source: `outputs/audit_stage5.md`, `audit_stage4.md`, CHANGES #25 to #27.

- **Eligibility thresholds:** 120 pressure balls and 15 matches. **Fallback used: none** (batters False, bowlers False).
- **Eligible players per role:** batters 53, bowlers 56 (before the active filter); **eligible and active** (any appearance in 2025 or 2026): batters 53, bowlers 55; **ranked pool** after removing reliably negative shifts: batters 47, bowlers 48.

| role    |   eligible |   eligible_and_active |
|:--------|-----------:|----------------------:|
| batters |         53 |                    53 |
| bowlers |         56 |                    55 |

- **Shrinkage:** the two ridge penalties (above) shrink a thin pressure record toward the player's baseline and a thin baseline toward average. Eligible-player SD of baselines 0.063 (batters) / 0.067 (bowlers); of shifts 0.0085 / 0.0084.
- **Opposition:** opposing players' baseline and shift terms sit in the same regression. A simple version without the regression (shrunk raw means) ranks almost identically: Spearman 0.9696 batters, 0.9839 bowlers (shrinkage constants k via method of moments: baseline 235.0 / 182.6, shift 567.1 / 429.9).
- **IPL vs T20I:** one model, one scale, competition-group term in the context. IPL-only and T20I-only ratings are sensitivity variants (top-10 overlap with the main list: IPL-only 6 batters / 8 bowlers; T20I-only 6 / 7).
- **Venue and era:** enter the SCORING model (venue scoring tier, impact-player rule), hence win probability and leverage. They are NOT in the rating regression's context (only innings, phase, pressure, competition group); batting-position band was tested as a variant only (overlap 10 of 10 batters).
- **Bootstrap:** 300 whole-match resamples of both fits with penalties fixed, seed 42. Outputs: `floor_p10` (10th percentile), `p90`, `boot_sd`, `p_top10`, `p_top20`, rank 10th/90th percentile. P(top 10), P(top 20) are computed among eligible AND active players.

## Stage 6: reliability and sensitivity

Details in `04_EVIDENCE_RELIABILITY.md`. Settings: split-half 200 random match splits with halved eligibility (60 pressure balls, 7 matches); season split fit on <= 2024, score 2025-2026; 500 permutations; sensitivity cutoffs [0.1, 0.15, 0.25, 0.3], recency half-life 2 years, winsor quantiles [0.01, 0.99].

## Stage 7: ranking and sanity checks

- **Ranking rule:** see `01_RANKINGS.md` (eligible + active, drop reliably negative shift, sort by bootstrap floor, ties by delivery rate then pressure balls).
- **Face validity (ranks 11 to 20, from `audit_stage7.md`):** batters 11 Jos Buttler, 12 Virat Kohli, 13 Lokesh Rahul, 14 Mitchell Marsh, 15 Ishan Kishan, 16 Yashasvi Jaiswal, 17 Cameron Green, 18 Riyan Parag, 19 Rovman Powell, 20 Josh Inglis; bowlers 11 Mujeeb Ur Rahman, 12 Bhuvneshwar Kumar, 13 Mitchell Santner, 14 Ravindra Jadeja, 15 Mohammad Nawaz, 16 Trent Boult, 17 Kagiso Rabada, 18 Arshdeep Singh, 19 Haris Rauf, 20 Mustafizur Rahman.
- **Sign check:** every listed batter has runs index > 100 or dismissal ratio < 1. For bowlers, under the amended rule 0 of 10 fail; under the original economy-only rule 2 fail (Hasaranga 94.8, Noor Ahmad 91.5; their wicket ratios are 1.34 and 1.39). See `00_DEVIATIONS.md`.
- **Surprises explained:** see `05_PLAYER_CARDS.md` (surprise names chosen by the website's stated rule) and `07_LIMITATIONS_OBSERVED.md`.
- **Spinner share:** 8 of the 10 listed bowlers are spinners vs 20 of 55 in the eligible, active pool; spinners bowl 35.0% of pressure balls vs 37.2% of all live balls (ratio 0.939) (`outputs/step3_reports.md` (d), `step3_summary.json`).
