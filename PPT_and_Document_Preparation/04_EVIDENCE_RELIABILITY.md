# 04 EVIDENCE FOR RELIABILITY (Stage 6), good and bad

Source: `outputs/audit_stage6.md` (identical text to `outputs/reliability.md`), `audit_stage5.md`, `audit_stage6b.md`, `sensitivity.csv`, `top10_*.csv`, `website/data/robustness.json`. Penalties are fixed; thresholds halved for split-half and season-to-season (60 pressure balls, 7 matches).

## 1. Split-half reliability (Spearman-Brown corrected)

200 random splits of matches; each half rated with the same penalties; the file reports the SD of the raw split-half r across the 200 splits (`sd_over_splits`). **A percentile interval for the corrected value was NOT COMPUTED** (the per-split values were not saved), so the SD is the only spread available.

| role    | quantity        |   mean_split_half_r |   spearman_brown |   sd_over_splits |   mean_players |
|:--------|:----------------|--------------------:|-----------------:|-----------------:|---------------:|
| batters | baseline        |              0.3699 |           0.5311 |           0.1172 |        41.7950 |
| batters | pressure rating |              0.3743 |           0.5358 |           0.1175 |        41.7950 |
| batters | pressure shift  |              0.0823 |           0.1303 |           0.2057 |        41.7950 |
| bowlers | baseline        |              0.4995 |           0.6622 |           0.0745 |        45.2100 |
| bowlers | pressure rating |              0.4989 |           0.6617 |           0.0733 |        45.2100 |
| bowlers | pressure shift  |              0.0912 |           0.1495 |           0.1837 |        45.2100 |

**Decision rule fixed in the blueprint:**

| role    |   split_half_pressure_rating | decision             |
|:--------|-----------------------------:|:---------------------|
| batters |                       0.5358 | rank on it (>= 0.40) |
| bowlers |                       0.6617 | rank on it (>= 0.40) |

## 2. Season to season (fit on 2022-2024, score 2025-2026)

| role    |   players |   pressure_rating_r |   spearman |   ci_lo |   ci_hi |   baseline_r |   shift_r |
|:--------|----------:|--------------------:|-----------:|--------:|--------:|-------------:|----------:|
| batters |        34 |              0.0477 |     0.0032 | -0.2294 |  0.3174 |       0.0271 |    0.0787 |
| bowlers |        37 |              0.5110 |     0.5225 |  0.2517 |  0.7201 |       0.4871 |    0.0673 |

`ci_lo`/`ci_hi` = 95% interval, bootstrap over players. Bowlers persist; batters do not (r = 0.0477, interval -0.2294 to 0.3174, n = 34).

## 3. Does the pressure shift add anything?

| role    | term                      |   coefficient |   ci_lo |   ci_hi | excludes_zero   |   n |
|:--------|:--------------------------|--------------:|--------:|--------:|:----------------|----:|
| batters | earlier baseline (per SD) |        0.0091 | -0.0501 |  0.0579 | False           |  34 |
| batters | earlier shift (per SD)    |        0.0200 | -0.0156 |  0.0530 | False           |  34 |
| bowlers | earlier baseline (per SD) |        0.0851 |  0.0363 |  0.1327 | True            |  37 |
| bowlers | earlier shift (per SD)    |        0.0112 | -0.0373 |  0.0439 | False           |  37 |

The shift coefficient's interval includes zero for both roles (batters 0.0200, [-0.0156, 0.0530]; bowlers 0.0112, [-0.0373, 0.0439]). Only the bowler baseline predicts later pressure value (0.0851, [0.0363, 0.1327]).

## 4. Permutation test

| role    |   players |   real_spread |   shuffled_mean |   shuffled_p95 |   p_value | real_beyond_p95   |
|:--------|----------:|--------------:|----------------:|---------------:|----------:|:------------------|
| batters |       217 |        0.2697 |          0.2440 |         0.2704 |    0.0620 | False             |
| bowlers |       228 |        0.2523 |          0.2305 |         0.2519 |    0.0480 | True              |

500 shuffles. Observed spread vs the 95th percentile of shuffles: batters 0.2697 vs 0.2704 (not beyond, p = 0.062); bowlers 0.2523 vs 0.2519 (just beyond, p = 0.048).

## 5. Rank stability of every listed player

| role   |   rank | name                 |   p_top10 |   p_top20 |   rank_p10 |   rank_p90 |   variants_in_top10_of_14 | fragile   |
|:-------|-------:|:---------------------|----------:|----------:|-----------:|-----------:|--------------------------:|:----------|
| batter |      1 | Heinrich Klaasen     |     0.993 |     1.000 |      1.000 |      6.000 |                        13 | False     |
| batter |      2 | Suryakumar Yadav     |     0.990 |     1.000 |      1.000 |      6.000 |                        14 | False     |
| batter |      3 | Tim David            |     0.907 |     0.967 |      1.000 |     10.000 |                        13 | False     |
| batter |      4 | Abhishek Sharma      |     0.850 |     0.977 |      2.000 |     14.000 |                        13 | False     |
| batter |      5 | Phil Salt            |     0.763 |     0.957 |      2.000 |     16.100 |                        13 | False     |
| batter |      6 | Shreyas Iyer         |     0.743 |     0.940 |      3.000 |     17.100 |                        13 | False     |
| batter |      7 | Namboori Tilak Varma |     0.587 |     0.930 |      4.000 |     18.000 |                        14 | False     |
| batter |      8 | Sai Sudharsan        |     0.283 |     0.813 |      8.000 |     23.100 |                        12 | False     |
| batter |      9 | Nicholas Pooran      |     0.563 |     0.860 |      4.000 |     23.000 |                        11 | False     |
| batter |     10 | Shubman Gill         |     0.247 |     0.760 |      8.000 |     26.000 |                         7 | False     |
| bowler |      1 | Sunil Narine         |     0.983 |     1.000 |      1.000 |      7.000 |                        13 | False     |
| bowler |      2 | Kuldeep Yadav        |     0.847 |     0.993 |      1.900 |     12.000 |                        14 | False     |
| bowler |      3 | Rashid Khan          |     0.840 |     0.980 |      1.000 |     12.000 |                        14 | False     |
| bowler |      4 | Varun Chakravarthy   |     0.800 |     0.983 |      1.000 |     13.000 |                        14 | False     |
| bowler |      5 | Josh Hazlewood       |     0.780 |     0.970 |      1.000 |     15.000 |                        14 | False     |
| bowler |      6 | Wanindu Hasaranga    |     0.683 |     0.963 |      3.000 |     17.000 |                        14 | False     |
| bowler |      7 | Jasprit Bumrah       |     0.670 |     0.953 |      3.000 |     17.000 |                        13 | False     |
| bowler |      8 | Axar Patel           |     0.390 |     0.903 |      5.000 |     20.000 |                        10 | False     |
| bowler |      9 | Noor Ahmad           |     0.540 |     0.867 |      2.000 |     23.000 |                        12 | False     |
| bowler |     10 | Krunal Pandya        |     0.537 |     0.867 |      2.900 |     22.000 |                        10 | False     |

**Exceptions flagged** (rule 1: P(top 20) < 0.6 = none; rule 2, my addition: P(top 10) < 0.5; rule 3: fragile flag):

- P(top 20) below 0.6: **none** (lowest is Shubman Gill 0.76).
- Fragile flag: **none** (Gill is in the top 10 under 7 of 14 variants, exactly half; the rule flags fewer than half).
- P(top 10) below 0.5 (listed players that finish in the top 10 in fewer than half of resamples): Sai Sudharsan (0.283), Shubman Gill (0.247), Axar Patel (0.390).

## 6. Cross-check: regression ranking vs the simple shrunk ranking

| role    |   spearman_regression_vs_simple |   k_baseline |   k_shift |   n |
|:--------|--------------------------------:|-------------:|----------:|----:|
| batters |                          0.9696 |     234.9667 |  567.1337 |  53 |
| bowlers |                          0.9839 |     182.5514 |  429.8722 |  56 |

## 7. Which blueprint rule did the reliability number trigger, and what the report should lead with

- **Rule triggered:** split-half pressure rating >= 0.40 (batters 0.5358, bowlers 0.6617) -> **'rank on it'**. The 'widen to top 30%' branch and the 'below 0.25' branch were not triggered by the rating. The pressure shift on its own is 0.1303 / 0.1495 (below 0.25). Blueprint wording for that branch: `NOT AVAILABLE (blueprint not provided)`.

- **Plain-language finding to lead with** (the project's own report.md leads with it):

> The ratings measure proven quality in live, high-leverage situations. A separate clutch trait is not reliably measurable in this data (pressure-shift split-half reliability 0.13 for batters and 0.15 for bowlers).

- Supporting lines: the baseline alone is as reliable as the pressure rating (0.531 / 0.662 vs 0.536 / 0.662), so the repeatability is general quality; bowlers persist across 2022-24 vs 2025-26 (r = 0.511, 95% interval 0.252 to 0.720, n = 37), batters do not (r = 0.048, interval -0.229 to 0.317, n = 34; batter baseline r = 0.027).

## 8. Sensitivity

Copied: `sensitivity.csv` (this folder) = `outputs/sensitivity.csv`. Overlap is with the main top 10 under the same floor PROXY (rating minus 1.2816 x bootstrap SD), not the final list; Kendall tau is over the eligible pool.

| variant                  |   overlap_of_10_batters |   overlap_of_10_bowlers |   kendall_tau_batters |   kendall_tau_bowlers |
|:-------------------------|------------------------:|------------------------:|----------------------:|----------------------:|
| cutoff_top10%            |                   9.000 |                   9.000 |                 0.964 |                 0.937 |
| cutoff_top15%            |                   9.000 |                  10.000 |                 0.972 |                 0.961 |
| cutoff_top25%            |                   9.000 |                  10.000 |                 0.971 |                 0.977 |
| cutoff_top30%            |                   9.000 |                  10.000 |                 0.959 |                 0.966 |
| cutoff_within_innings    |                   9.000 |                   9.000 |                 0.938 |                 0.923 |
| no_cutoff_log_leverage   |                   9.000 |                   9.000 |                 0.914 |                 0.918 |
| benchmark_pressure_index |                  10.000 |                   9.000 |                 0.948 |                 0.938 |
| benchmark_rule_of_thumb  |                  10.000 |                   9.000 |                 0.929 |                 0.919 |
| lower_tier_included      |                  10.000 |                  10.000 |                 0.956 |                 0.952 |
| IPL_only                 |                   6.000 |                   8.000 |                 0.734 |                 0.638 |
| T20I_only                |                   6.000 |                   7.000 |                 0.538 |                 0.552 |
| recency_2yr_half_life    |                   8.000 |                   8.000 |                 0.803 |                 0.832 |
| position_band_in_context |                  10.000 |                  10.000 |                 0.983 |                 1.000 |
| winsorised_values_1_99   |                  10.000 |                  10.000 |                 0.978 |                 0.957 |

Median overlap: batters 9, bowlers 9 (target >= 7). Minimum overlap: 6 of 10 (IPL-only and T20I-only batters). Not run: win probability without recalibration.

### Which listed players drop out of which variants

| role   |   rank | name                 |   in_top10_of_14 |   drops_out_in | fragile   | variants_missed                                                                                                                                            |
|:-------|-------:|:---------------------|-----------------:|---------------:|:----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| batter |      1 | Heinrich Klaasen     |               13 |              1 | False     | T20I_only                                                                                                                                                  |
| batter |      2 | Suryakumar Yadav     |               14 |              0 | False     | none                                                                                                                                                       |
| batter |      3 | Tim David            |               13 |              1 | False     | IPL_only                                                                                                                                                   |
| batter |      4 | Abhishek Sharma      |               13 |              1 | False     | IPL_only                                                                                                                                                   |
| batter |      5 | Phil Salt            |               13 |              1 | False     | IPL_only                                                                                                                                                   |
| batter |      6 | Shreyas Iyer         |               13 |              1 | False     | T20I_only                                                                                                                                                  |
| batter |      7 | Namboori Tilak Varma |               14 |              0 | False     | none                                                                                                                                                       |
| batter |      8 | Sai Sudharsan        |               12 |              2 | False     | cutoff_within_innings, T20I_only                                                                                                                           |
| batter |      9 | Nicholas Pooran      |               11 |              3 | False     | cutoff_top15%, T20I_only, recency_2yr_half_life                                                                                                            |
| batter |     10 | Shubman Gill         |                7 |              7 | False     | benchmark_pressure_index, benchmark_rule_of_thumb, lower_tier_included, T20I_only, recency_2yr_half_life, position_band_in_context, winsorised_values_1_99 |
| bowler |      1 | Sunil Narine         |               13 |              1 | False     | T20I_only                                                                                                                                                  |
| bowler |      2 | Kuldeep Yadav        |               14 |              0 | False     | none                                                                                                                                                       |
| bowler |      3 | Rashid Khan          |               14 |              0 | False     | none                                                                                                                                                       |
| bowler |      4 | Varun Chakravarthy   |               14 |              0 | False     | none                                                                                                                                                       |
| bowler |      5 | Josh Hazlewood       |               14 |              0 | False     | none                                                                                                                                                       |
| bowler |      6 | Wanindu Hasaranga    |               14 |              0 | False     | none                                                                                                                                                       |
| bowler |      7 | Jasprit Bumrah       |               13 |              1 | False     | T20I_only                                                                                                                                                  |
| bowler |      8 | Axar Patel           |               10 |              4 | False     | cutoff_within_innings, benchmark_pressure_index, IPL_only, recency_2yr_half_life                                                                           |
| bowler |      9 | Noor Ahmad           |               12 |              2 | False     | no_cutoff_log_leverage, IPL_only                                                                                                                           |
| bowler |     10 | Krunal Pandya        |               10 |              4 | False     | cutoff_top10%, benchmark_rule_of_thumb, T20I_only, recency_2yr_half_life                                                                                   |

(Membership reproduced from `sensitivity_ratings_*.csv` with the stage-7 rule and matches `variants_in_top10` for all 20 players; asserted at build time.)

**Across the five cutoffs (the chosen top 20% plus 10/15/25/30%)**, on the website's proxy lists, between 9 and 10 of the final top-10 batters and between 9 and 10 of the final top-10 bowlers survive in the top 10 (`website/data/robustness.json` `cutoff_survivors_min/max`).

**Which listed players are fragile:** none by the pipeline's rule (fewer than half of 14 variants). **Closest to it:** Shubman Gill, in the top 10 under 7 of 14 variants (out under: benchmark_pressure_index, benchmark_rule_of_thumb, lower_tier_included, T20I_only, recency_2yr_half_life, position_band_in_context, winsorised_values_1_99); Axar Patel and Krunal Pandya 10 of 14 each; Nicholas Pooran 11 of 14.
