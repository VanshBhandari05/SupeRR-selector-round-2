# 03 EVIDENCE FOR THE PRESSURE DEFINITION (Stage 3)

Everything below is read from `outputs/audit_stage3.md`, `audit_stage2.md`, `audit_stage2c.md`, `website/data/league_split.json` and `outputs/balls_pressure.parquet`. Comparison is between LIVE pressure balls and LIVE ordinary balls, standardised within innings x phase x wickets band (cells need at least 30 balls on both sides), with 95% intervals from 300 whole-match bootstrap resamples.

## 1. Outcome shift by phase (stratified; pressure minus ordinary)

Differences are in rate units (e.g. 0.0208 = +2.08 percentage points); `runs` is runs per ball. `extras` = wides and no-balls per delivery (`m_extras = is_wide | is_noball` in `stage3_prove.py`). Wickets-band and innings standardisation is inside each phase (the audit reports the phase level only; the raw cell rates by innings, phase and wickets band are in Section 4).

| phase           | metric    |   diff_pressure_minus_ordinary |   ci_lo |   ci_hi | excludes_zero   |
|:----------------|:----------|-------------------------------:|--------:|--------:|:----------------|
| powerplay (1-6) | dismissal |                         0.0007 | -0.0041 |  0.0057 | False           |
| powerplay (1-6) | boundary  |                         0.0187 |  0.0083 |  0.0278 | True            |
| powerplay (1-6) | dot       |                        -0.0453 | -0.0564 | -0.0311 | True            |
| powerplay (1-6) | runs      |                         0.1166 |  0.0629 |  0.1590 | True            |
| powerplay (1-6) | extras    |                         0.0005 | -0.0043 |  0.0052 | False           |
| middle (7-15)   | dismissal |                         0.0090 |  0.0046 |  0.0144 | True            |
| middle (7-15)   | boundary  |                         0.0144 |  0.0061 |  0.0218 | True            |
| middle (7-15)   | dot       |                        -0.0345 | -0.0442 | -0.0233 | True            |
| middle (7-15)   | runs      |                         0.0862 |  0.0460 |  0.1201 | True            |
| middle (7-15)   | extras    |                         0.0051 |  0.0014 |  0.0098 | True            |
| death (16-20)   | dismissal |                         0.0208 |  0.0096 |  0.0315 | True            |
| death (16-20)   | boundary  |                         0.0170 | -0.0019 |  0.0371 | False           |
| death (16-20)   | dot       |                        -0.0217 | -0.0447 | -0.0020 | True            |
| death (16-20)   | runs      |                         0.1131 |  0.0293 |  0.2055 | True            |
| death (16-20)   | extras    |                         0.0146 |  0.0025 |  0.0262 | True            |

**Which phases pass the gate** (dismissal OR boundary interval excludes zero; need >= 2 of 3):

| phase           | dismissal_excludes_zero   | boundary_excludes_zero   | passes   |
|:----------------|:--------------------------|:-------------------------|:---------|
| powerplay (1-6) | False                     | True                     | True     |
| middle (7-15)   | True                      | True                     | True     |
| death (16-20)   | True                      | False                    | True     |

**Result: 3 of 3 phases pass; gate PASS.** Honest detail: in the powerplay the dismissal difference (+0.07 pts) and in the death overs the boundary difference (+1.7 pts, interval -0.2 to +3.7) do not exclude zero; the pass comes from boundaries in the powerplay and dismissals in the death overs. Outcome 'runs' differences exclude zero in all three phases.

## 2. Behaviour shift (strokes and delivery styles)

| phase           | metric           |   diff_pressure_minus_ordinary |   ci_lo |   ci_hi | excludes_zero   |
|:----------------|:-----------------|-------------------------------:|--------:|--------:|:----------------|
| powerplay (1-6) | attacking_stroke |                         0.0043 | -0.0006 |  0.0094 | False           |
| powerplay (1-6) | defensive_stroke |                        -0.0273 | -0.0368 | -0.0161 | True            |
| powerplay (1-6) | yorker           |                         0.0014 | -0.0020 |  0.0042 | False           |
| powerplay (1-6) | slower           |                         0.0118 |  0.0066 |  0.0178 | True            |
| middle (7-15)   | attacking_stroke |                         0.0107 |  0.0051 |  0.0165 | True            |
| middle (7-15)   | defensive_stroke |                        -0.0154 | -0.0237 | -0.0076 | True            |
| middle (7-15)   | yorker           |                         0.0068 |  0.0037 |  0.0102 | True            |
| middle (7-15)   | slower           |                         0.0136 |  0.0064 |  0.0188 | True            |
| death (16-20)   | attacking_stroke |                         0.0297 |  0.0163 |  0.0431 | True            |
| death (16-20)   | defensive_stroke |                        -0.0130 | -0.0265 | -0.0001 | True            |
| death (16-20)   | yorker           |                         0.0216 |  0.0069 |  0.0358 | True            |
| death (16-20)   | slower           |                         0.0050 | -0.0109 |  0.0177 | False           |

Groupings (config `stage3`, chosen by me, CHANGES #15): attacking = Slog, Slog Sweep, Paddle Scoop, Reverse Paddle Scoop; defensive = Frontfoot defensive, Backfoot defensive, Defense, Intentional Padding; yorker = Yorker, Wide Yorker; slower = Slow Ball, Slow Bouncer, Knuckle, Back of Hand.

## 3. League-wide pressure vs ordinary (RAW rates, not standardised)

Source: `website/data/league_split.json` `overall` (aggregation of the rated matches' live balls). These raw rates mix phases and innings: for example in the death overs the raw pressure strike rate (161.4) is slightly BELOW the ordinary one (164.0) even though the stratified runs-per-ball difference is positive. Use the stratified table in Section 1 for the 'proof' and these for headline context.

| metric                     |   normal (ordinary live balls) |   pressure |
|:---------------------------|-------------------------------:|-----------:|
| balls faced (non-wide)     |                      120111.00 |   29948.00 |
| deliveries bowled          |                      124799.00 |   31263.00 |
| strike rate                |                         139.50 |     146.60 |
| dismissal % of balls faced |                           5.09 |       5.86 |
| dot %                      |                          30.00 |      27.50 |
| boundary %                 |                          18.80 |      20.10 |
| economy (runs/over)        |                           8.67 |       9.13 |
| balls per wicket           |                          20.20 |      17.40 |
| wickets                    |                        5935.00 |    1712.00 |

By phase (same file, `by_phase`):

| phase     | metric        |   normal |   pressure |
|:----------|:--------------|---------:|-----------:|
| powerplay | sr            |   134.00 |     145.20 |
| powerplay | dismissal_pct |     4.36 |       4.80 |
| powerplay | dot_pct       |    40.60 |      36.70 |
| powerplay | boundary_pct  |    21.60 |      23.60 |
| powerplay | economy       |     8.32 |       9.00 |
| middle    | sr            |   133.40 |     139.10 |
| middle    | dismissal_pct |     4.46 |       5.20 |
| middle    | dot_pct       |    26.30 |      23.70 |
| middle    | boundary_pct  |    15.40 |      16.40 |
| middle    | economy       |     8.24 |       8.63 |
| death     | sr            |   164.00 |     161.40 |
| death     | dismissal_pct |     7.90 |       8.52 |
| death     | dot_pct       |    20.50 |      20.80 |
| death     | boundary_pct  |    22.00 |      21.60 |
| death     | economy       |    10.32 |      10.20 |

## 4. Raw cell rates by innings, phase and wickets band

(`audit_stage3.md`; only cells with enough balls on both sides appear. Innings 1 contributes a single cell: 98 pressure balls.)

|   innings | phase           | wickets_band   | metric    |   n_pressure |   n_ordinary |   rate_pressure |   rate_ordinary |
|----------:|:----------------|:---------------|:----------|-------------:|-------------:|----------------:|----------------:|
|         1 | death (16-20)   | 6+             | dismissal |           98 |         8628 |          0.0408 |          0.0976 |
|         1 | death (16-20)   | 6+             | boundary  |           98 |         8628 |          0.2245 |          0.1735 |
|         1 | death (16-20)   | 6+             | dot       |           98 |         8628 |          0.3673 |          0.2349 |
|         1 | death (16-20)   | 6+             | runs      |           98 |         8628 |          1.5816 |          1.4609 |
|         1 | death (16-20)   | 6+             | extras    |           98 |         8628 |          0.0408 |          0.0554 |
|         2 | powerplay (1-6) | 0-2            | dismissal |        11525 |        14814 |          0.0470 |          0.0458 |
|         2 | powerplay (1-6) | 0-2            | boundary  |        11525 |        14814 |          0.2252 |          0.2050 |
|         2 | powerplay (1-6) | 0-2            | dot       |        11525 |        14814 |          0.3538 |          0.4018 |
|         2 | powerplay (1-6) | 0-2            | runs      |        11525 |        14814 |          1.4672 |          1.3424 |
|         2 | powerplay (1-6) | 0-2            | extras    |        11525 |        14814 |          0.0407 |          0.0401 |
|         2 | powerplay (1-6) | 3-5            | dismissal |          381 |         1295 |          0.0184 |          0.0355 |
|         2 | powerplay (1-6) | 3-5            | boundary  |          381 |         1295 |          0.1470 |          0.1714 |
|         2 | powerplay (1-6) | 3-5            | dot       |          381 |         1295 |          0.4672 |          0.4324 |
|         2 | powerplay (1-6) | 3-5            | runs      |          381 |         1295 |          1.0525 |          1.1861 |
|         2 | powerplay (1-6) | 3-5            | extras    |          381 |         1295 |          0.0394 |          0.0409 |
|         2 | middle (7-15)   | 0-2            | dismissal |         5658 |        10062 |          0.0546 |          0.0396 |
|         2 | middle (7-15)   | 0-2            | boundary  |         5658 |        10062 |          0.1812 |          0.1528 |
|         2 | middle (7-15)   | 0-2            | dot       |         5658 |        10062 |          0.1964 |          0.2442 |
|         2 | middle (7-15)   | 0-2            | runs      |         5658 |        10062 |          1.5237 |          1.3661 |
|         2 | middle (7-15)   | 0-2            | extras    |         5658 |        10062 |          0.0373 |          0.0304 |
|         2 | middle (7-15)   | 3-5            | dismissal |         7975 |         8586 |          0.0522 |          0.0466 |
|         2 | middle (7-15)   | 3-5            | boundary  |         7975 |         8586 |          0.1377 |          0.1309 |
|         2 | middle (7-15)   | 3-5            | dot       |         7975 |         8586 |          0.2508 |          0.2796 |
|         2 | middle (7-15)   | 3-5            | runs      |         7975 |         8586 |          1.2979 |          1.2474 |
|         2 | middle (7-15)   | 3-5            | extras    |         7975 |         8586 |          0.0392 |          0.0358 |
|         2 | middle (7-15)   | 6+             | dismissal |          471 |          796 |          0.0488 |          0.0553 |
|         2 | middle (7-15)   | 6+             | boundary  |          471 |          796 |          0.1019 |          0.1256 |
|         2 | middle (7-15)   | 6+             | dot       |          471 |          796 |          0.3715 |          0.3417 |
|         2 | middle (7-15)   | 6+             | runs      |          471 |          796 |          1.0170 |          1.1834 |
|         2 | middle (7-15)   | 6+             | extras    |          471 |          796 |          0.0382 |          0.0264 |
|         2 | death (16-20)   | 0-2            | dismissal |          437 |          257 |          0.0732 |          0.0623 |
|         2 | death (16-20)   | 0-2            | boundary  |          437 |          257 |          0.2197 |          0.2257 |
|         2 | death (16-20)   | 0-2            | dot       |          437 |          257 |          0.1670 |          0.1595 |
|         2 | death (16-20)   | 0-2            | runs      |          437 |          257 |          1.7414 |          1.7743 |
|         2 | death (16-20)   | 0-2            | extras    |          437 |          257 |          0.0618 |          0.0467 |
|         2 | death (16-20)   | 3-5            | dismissal |         4558 |         1186 |          0.0799 |          0.0582 |
|         2 | death (16-20)   | 3-5            | boundary  |         4558 |         1186 |          0.2119 |          0.1838 |
|         2 | death (16-20)   | 3-5            | dot       |         4558 |         1186 |          0.1707 |          0.2040 |
|         2 | death (16-20)   | 3-5            | runs      |         4558 |         1186 |          1.6909 |          1.5177 |
|         2 | death (16-20)   | 3-5            | extras    |         4558 |         1186 |          0.0654 |          0.0464 |
|         2 | death (16-20)   | 6+             | dismissal |         3391 |          764 |          0.0964 |          0.0733 |
|         2 | death (16-20)   | 6+             | boundary  |         3391 |          764 |          0.1781 |          0.1741 |
|         2 | death (16-20)   | 6+             | dot       |         3391 |          764 |          0.2383 |          0.2526 |
|         2 | death (16-20)   | 6+             | runs      |         3391 |          764 |          1.4553 |          1.4045 |
|         2 | death (16-20)   | 6+             | extras    |         3391 |          764 |          0.0669 |          0.0576 |

## 5. Close games vs blowouts: leverage against final margin

| close   |   matches |   median_peak_LI |   mean_peak_LI |   median_mean_LI |   median_total_LI |
|:--------|----------:|-----------------:|---------------:|-----------------:|------------------:|
| False   |       671 |           1.6001 |         2.6273 |           0.8767 |          186.8341 |
| True    |       137 |          10.1484 |        12.2160 |           1.3083 |          324.0343 |

Mann-Whitney (close > other) peak LI p=6.27e-56; mean LI per live ball p=1.59e-44. Spearman peak LI vs runs margin (wins by runs, n=395): -0.853 (p=8.4e-113); mean LI vs margin: -0.775; peak LI vs wickets in hand (wins by wickets, n=404): -0.623.

Matches classed close: 137 of 808 clean matches (blueprint expected about 130 across all matches).

- 'Close' = tie, or won by <= 10 runs, or won with <= 3 wickets in hand. Margin is never an input to the pressure definition.

## 6. Benchmark agreement

Bhattacharjee-Lemmer PI = (CRRR/IRRR) x 0.5 x [exp(RU/100) + exp(sum w_i / 11)], wicket weights by batting position of the dismissed batter. RU (resources used) is DERIVED from our own scoring model (100 x (1 - expected runs to come / expected runs at the start)), because the Duckworth-Lewis table is not in the data. Spearman(PI, LI): live chase balls 0.328; all chase balls 0.110; by phase [np.float64(0.089), np.float64(0.266), np.float64(0.233)]. Share of the top-20% PI balls that are pressure balls: 0.679.

Rule-of-thumb overlap (live balls):

|   innings |   rule_balls |   pressure_balls |      both |   share_of_rule_that_is_pressure |   share_of_pressure_in_rule |   jaccard |
|----------:|-------------:|-----------------:|----------:|---------------------------------:|----------------------------:|----------:|
|    1.0000 |   16710.0000 |          98.0000 |   98.0000 |                           0.0059 |                      1.0000 |    0.0059 |
|    2.0000 |    6078.0000 |       34396.0000 | 5630.0000 |                           0.9263 |                      0.1637 |    0.1616 |

Figures: figures/stage3_separation.png, stage3_where_pressure_lives.png, stage3_close_games.png, stage3_case_studies.png

**Reading:** rank correlation between our LI and the published pressure index on live chase balls is 0.328 (all chase balls 0.110; by phase 0.089 / 0.266 / 0.233). The two agree on direction but are far from identical, and the index's resources-used term is substituted by one derived from our own scoring model (CHANGES #14). Overlap with the rule-of-thumb set: 92.6% of rule-of-thumb chase balls are pressure balls, but the rule covers only 16.4% of pressure chase balls (Jaccard 0.162). In innings 1 the rule marks 16,710 balls and 98 are pressure.

## 7. Calibration of the win probability (held-out seasons)

Leave-one-season-out. `gap` = predicted minus observed; `gap_lo`/`gap_hi` = 95% match-bootstrap interval on the gap (about +/-0.05, as wide as the 0.05 tolerance).

**Brier scores and log loss:**

|   innings |      balls |   brier_const |   brier_baseline |   brier_raw |   brier_star |   logloss_baseline |   logloss_raw |   logloss_star |
|----------:|-----------:|--------------:|-----------------:|------------:|-------------:|-------------------:|--------------:|---------------:|
|    1.0000 | 99471.0000 |        0.2500 |           0.2294 |      0.2190 |       0.2193 |             0.6512 |        0.6307 |         0.6285 |
|    2.0000 | 91335.0000 |        0.2497 |           0.1490 |      0.1264 |       0.1270 |             0.4548 |        0.3933 |         0.3922 |

The final model WP* beats the one-feature baseline in both innings (innings 1: 0.2193 vs 0.2294; innings 2: 0.1270 vs 0.1490). The raw (un-recalibrated) WP is slightly better on Brier (0.2190 / 0.1264) but fails the decile gate (raw max gap 0.0994 / 0.0601), which is why recalibration is used.

**Decile table, WP*, innings 1:**

|    bin |     balls |   pred |    obs |     gap |   gap_lo |   gap_hi |
|-------:|----------:|-------:|-------:|--------:|---------:|---------:|
| 0.0000 | 9948.0000 | 0.1703 | 0.1726 | -0.0023 |  -0.0609 |   0.0529 |
| 1.0000 | 9947.0000 | 0.3093 | 0.3068 |  0.0025 |  -0.0515 |   0.0531 |
| 2.0000 | 9947.0000 | 0.3880 | 0.3805 |  0.0075 |  -0.0419 |   0.0683 |
| 3.0000 | 9947.0000 | 0.4418 | 0.4412 |  0.0006 |  -0.0543 |   0.0581 |
| 4.0000 | 9947.0000 | 0.4840 | 0.4697 |  0.0144 |  -0.0328 |   0.0603 |
| 5.0000 | 9947.0000 | 0.5214 | 0.5399 | -0.0185 |  -0.0625 |   0.0244 |
| 6.0000 | 9947.0000 | 0.5614 | 0.5673 | -0.0059 |  -0.0464 |   0.0433 |
| 7.0000 | 9947.0000 | 0.6093 | 0.6285 | -0.0193 |  -0.0646 |   0.0245 |
| 8.0000 | 9947.0000 | 0.6765 | 0.7097 | -0.0332 |  -0.0798 |   0.0134 |
| 9.0000 | 9947.0000 | 0.8161 | 0.7743 |  0.0418 |  -0.0197 |   0.1025 |

**Decile table, WP*, innings 2:**

|    bin |     balls |   pred |    obs |     gap |   gap_lo |   gap_hi |
|-------:|----------:|-------:|-------:|--------:|---------:|---------:|
| 0.0000 | 9134.0000 | 0.0020 | 0.0020 | -0.0000 |  -0.0028 |   0.0018 |
| 1.0000 | 9133.0000 | 0.0380 | 0.0424 | -0.0044 |  -0.0294 |   0.0157 |
| 2.0000 | 9134.0000 | 0.1390 | 0.1370 |  0.0020 |  -0.0373 |   0.0414 |
| 3.0000 | 9133.0000 | 0.2738 | 0.2611 |  0.0127 |  -0.0356 |   0.0633 |
| 4.0000 | 9134.0000 | 0.4048 | 0.3836 |  0.0212 |  -0.0200 |   0.0789 |
| 5.0000 | 9133.0000 | 0.5389 | 0.5621 | -0.0233 |  -0.0784 |   0.0348 |
| 6.0000 | 9133.0000 | 0.6837 | 0.6918 | -0.0081 |  -0.0566 |   0.0527 |
| 7.0000 | 9134.0000 | 0.8202 | 0.8298 | -0.0096 |  -0.0508 |   0.0393 |
| 8.0000 | 9133.0000 | 0.9374 | 0.9236 |  0.0138 |  -0.0200 |   0.0555 |
| 9.0000 | 9134.0000 | 0.9935 | 0.9835 |  0.0100 |  -0.0061 |   0.0303 |

**Honest caveats on calibration (from the same audit):** innings-1 bins above 0.8 over-predict (e.g. bin (0.9, 0.95]: predicted 0.922, observed 0.839, 969 balls); start-of-chase over-predicts chasing associates by 8.7 points (52 matches) and A-teams by 5.4 points (30 matches); IPL -0.1, full-member T20I +2.3.

## 8. Three tight finishes and three one-sided chases

Selection rule (from `src/stage3_prove.py`, replicated and matched at build time): tight = the first tie, the closest win by runs (margin <= 2, ties broken by margin then match id), the first win by 1 wicket or fewer; one-sided = the two largest wins by runs and the largest win by wickets. Series are the CHASING innings (innings 2). Underlying series exported as `03_trace_series.csv` (derived columns only: match id, ball of the chase, over, LI, WP*, live, pressure flag); summaries in `03_trace_summary.csv`.

| kind      |   match_id | date       | teams                  | chasing_team   |   target | result                                |   chase_balls |   peak_LI |   peak_ball_of_chase |   peak_over |   live_balls |   pressure_balls |   pressure_share_of_chase |   final_wp_star |
|:----------|-----------:|:-----------|:-----------------------|:---------------|---------:|:--------------------------------------|--------------:|----------:|---------------------:|------------:|-------------:|-----------------:|--------------------------:|----------------:|
| tight     |      13613 | 2022-02-13 | Australia v Sri Lanka  | Sri Lanka      |      165 | Australia Won the one over Eliminator |           122 |    18.350 |                  122 |          20 |          122 |               77 |                     0.631 |           0.219 |
| tight     |      13512 | 2022-01-23 | West Indies v England  | West Indies    |      174 | England Won by 1 Run                  |           124 |     1.440 |                  124 |          20 |           66 |                6 |                     0.048 |           0.015 |
| tight     |      16662 | 2022-09-07 | Pakistan v Afghanistan | Pakistan       |      130 | Pakistan Won by 1 Wicket              |           117 |    11.310 |                  117 |          20 |          117 |               74 |                     0.632 |           0.635 |
| one_sided |      19717 | 2023-02-01 | India v New Zealand    | New Zealand    |      235 | India Won by 168 runs                 |            75 |     0.690 |                    5 |           1 |            7 |                0 |                     0.000 |           0.001 |
| one_sided |      40040 | 2025-02-02 | India v England        | England        |      248 | India Won by 150 runs                 |            65 |     0.930 |                   13 |           3 |           33 |                0 |                     0.000 |           0.001 |
| one_sided |      15458 | 2022-06-07 | Sri Lanka v Australia  | Australia      |      129 | Australia Won by 10 Wickets           |            87 |     0.950 |                    7 |           2 |           30 |                0 |                     0.000 |           0.999 |

**Short ball-by-ball LI readings:**

- **13613** (tight, 2022-02-13, Australia v Sri Lanka, chasing: Sri Lanka, target 165; result: Australia Won the one over Eliminator). Peak LI 18.35 on ball 122 (over 20); 77 of 122 chase balls are pressure balls (63.1%). Last six balls' LI: 3.87, 5.73, 6.49, 4.80, 12.45, 18.35.
- **13512** (tight, 2022-01-23, West Indies v England, chasing: West Indies, target 174; result: England Won by 1 Run). Peak LI 1.44 on ball 124 (over 20); 6 of 124 chase balls are pressure balls (4.8%). Last six balls' LI: 0.02, 0.03, 0.02, 0.08, 0.38, 1.44.
- **16662** (tight, 2022-09-07, Pakistan v Afghanistan, chasing: Pakistan, target 130; result: Pakistan Won by 1 Wicket). Peak LI 11.31 on ball 117 (over 20); 74 of 117 chase balls are pressure balls (63.2%). Last six balls' LI: 4.54, 4.70, 4.86, 7.24, 7.76, 11.31.
- **19717** (one_sided, 2023-02-01, India v New Zealand, chasing: New Zealand, target 235; result: India Won by 168 runs). Peak LI 0.69 on ball 5 (over 1); 0 of 75 chase balls are pressure balls (0.0%). Last six balls' LI: 0.00, 0.00, 0.00, 0.00, 0.00, 0.00.
- **40040** (one_sided, 2025-02-02, India v England, chasing: England, target 248; result: India Won by 150 runs). Peak LI 0.93 on ball 13 (over 3); 0 of 65 chase balls are pressure balls (0.0%). Last six balls' LI: 0.00, 0.00, 0.00, 0.00, 0.00, 0.00.
- **15458** (one_sided, 2022-06-07, Sri Lanka v Australia, chasing: Australia, target 129; result: Australia Won by 10 Wickets). Peak LI 0.95 on ball 7 (over 2); 0 of 87 chase balls are pressure balls (0.0%). Last six balls' LI: 0.00, 0.00, 0.00, 0.00, 0.00, 0.03.

### FLAG: one of the three 'tight finish' traces barely registers as pressure

Match **13512** (England won by 1 run, West Indies chasing 174 in the model) has peak LI **1.44**, only **6** pressure balls (4.8% of the chase), and 58 of its 124 chase balls are 'dead' (WP* outside 0.02 to 0.98) so they are excluded from pressure. The chase was effectively lost on the model's numbers until the last over, when three sixes (`balls_state` `runs` = 6 on each of the last three balls) closed the gap to the 1-run margin. Two issues: (1) the three 'tight' ids were picked mechanically by `stage3_prove.py`, not by looking at them, and this one does not illustrate a pressure spike; (2) the rebuilt state does not reconcile exactly with the stated margin: rebuilt R1 = 171, rebuilt R2 = 172 (`outputs/matches_clean_totals.csv`), anchor target = 174 (R2 + margin 1 + 1), so the model has the chasers needing 8 off the last ball and finishing 2 short, while the stated margin is 1 run (the backward anchor puts any rebuilt-total error into the target; the margin gate allows up to 6 at the 95th percentile, 8 at the maximum). **For slides, use match 16662 (Pakistan won by 1 wicket, peak LI 11.31, 63.2% pressure balls) or 13613 (peak LI 18.35, 63.1%) as the tight example, not 13512.** I did not change any figure or rule. See `07_LIMITATIONS_OBSERVED.md`.

Figures for this document are listed in `08_FIGURE_INDEX.md` (F01 heatmap, F02 calibration, F03 trace, F09 paired bars, plus the originals `stage3_*.png`, `stage2_calibration.png`).
