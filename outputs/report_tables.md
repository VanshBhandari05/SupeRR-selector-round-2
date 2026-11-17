# Report tables (generated)

## Final lists

### Top 10 batters

|   rank | name                 |   player_id |   pressure_rating |   floor_p10 |   p_top10 |   p_top20 |   delivery_rate | fragile   |
|-------:|:---------------------|------------:|------------------:|------------:|----------:|----------:|----------------:|:----------|
|      1 | Heinrich Klaasen     |        4260 |             0.245 |       0.197 |     0.993 |     1.000 |           0.889 | False     |
|      2 | Suryakumar Yadav     |        1699 |             0.248 |       0.194 |     0.990 |     1.000 |           0.739 | False     |
|      3 | Tim David            |        6396 |             0.226 |       0.165 |     0.907 |     0.967 |           0.579 | False     |
|      4 | Abhishek Sharma      |        6281 |             0.209 |       0.143 |     0.850 |     0.977 |           0.682 | False     |
|      5 | Phil Salt            |        5553 |             0.194 |       0.129 |     0.763 |     0.957 |           0.733 | False     |
|      6 | Shreyas Iyer         |        3647 |             0.188 |       0.126 |     0.743 |     0.940 |           0.750 | False     |
|      7 | Namboori Tilak Varma |        7897 |             0.164 |       0.121 |     0.587 |     0.930 |           0.615 | False     |
|      8 | Sai Sudharsan        |       23450 |             0.142 |       0.102 |     0.283 |     0.813 |           0.562 | False     |
|      9 | Nicholas Pooran      |        3125 |             0.159 |       0.099 |     0.563 |     0.860 |           0.625 | False     |
|     10 | Shubman Gill         |        6288 |             0.136 |       0.094 |     0.247 |     0.760 |           0.565 | False     |

### Top 10 bowlers

|   rank | name               |   player_id |   pressure_rating |   floor_p10 |   p_top10 |   p_top20 |   delivery_rate | fragile   |
|-------:|:-------------------|------------:|------------------:|------------:|----------:|----------:|----------------:|:----------|
|      1 | Sunil Narine       |         781 |             0.198 |       0.153 |     0.983 |     1.000 |           0.591 | False     |
|      2 | Kuldeep Yadav      |        3644 |             0.165 |       0.123 |     0.847 |     0.993 |           0.737 | False     |
|      3 | Rashid Khan        |        4722 |             0.170 |       0.119 |     0.840 |     0.980 |           0.733 | False     |
|      4 | Varun Chakravarthy |        6256 |             0.171 |       0.116 |     0.800 |     0.983 |           0.577 | False     |
|      5 | Josh Hazlewood     |         830 |             0.169 |       0.106 |     0.780 |     0.970 |           0.591 | False     |
|      6 | Wanindu Hasaranga  |        4900 |             0.143 |       0.099 |     0.683 |     0.963 |           0.500 | False     |
|      7 | Jasprit Bumrah     |        2933 |             0.149 |       0.095 |     0.670 |     0.953 |           0.409 | False     |
|      8 | Axar Patel         |        2876 |             0.123 |       0.082 |     0.390 |     0.903 |           0.607 | False     |
|      9 | Noor Ahmad         |        7967 |             0.144 |       0.074 |     0.540 |     0.867 |           0.308 | False     |
|     10 | Krunal Pandya      |        4219 |             0.137 |       0.072 |     0.537 |     0.867 |           0.765 | False     |

## Sensitivity grid

| role    | variant                  |   top10_overlap_with_main |   kendall_tau |   players_missing |
|:--------|:-------------------------|--------------------------:|--------------:|------------------:|
| batters | cutoff_top10%            |                         9 |         0.964 |                 0 |
| batters | cutoff_top15%            |                         9 |         0.972 |                 0 |
| batters | cutoff_top25%            |                         9 |         0.971 |                 0 |
| batters | cutoff_top30%            |                         9 |         0.959 |                 0 |
| batters | cutoff_within_innings    |                         9 |         0.938 |                 0 |
| batters | no_cutoff_log_leverage   |                         9 |         0.914 |                 0 |
| batters | benchmark_pressure_index |                        10 |         0.948 |                 0 |
| batters | benchmark_rule_of_thumb  |                        10 |         0.929 |                 0 |
| batters | lower_tier_included      |                        10 |         0.956 |                 0 |
| batters | IPL_only                 |                         6 |         0.734 |                 0 |
| batters | T20I_only                |                         6 |         0.538 |                 0 |
| batters | recency_2yr_half_life    |                         8 |         0.803 |                 0 |
| batters | position_band_in_context |                        10 |         0.983 |                 0 |
| batters | winsorised_values_1_99   |                        10 |         0.978 |                 0 |
| bowlers | cutoff_top10%            |                         9 |         0.937 |                 0 |
| bowlers | cutoff_top15%            |                        10 |         0.961 |                 0 |
| bowlers | cutoff_top25%            |                        10 |         0.977 |                 0 |
| bowlers | cutoff_top30%            |                        10 |         0.966 |                 0 |
| bowlers | cutoff_within_innings    |                         9 |         0.923 |                 0 |
| bowlers | no_cutoff_log_leverage   |                         9 |         0.918 |                 0 |
| bowlers | benchmark_pressure_index |                         9 |         0.938 |                 0 |
| bowlers | benchmark_rule_of_thumb  |                         9 |         0.919 |                 0 |
| bowlers | lower_tier_included      |                        10 |         0.952 |                 0 |
| bowlers | IPL_only                 |                         8 |         0.638 |                 0 |
| bowlers | T20I_only                |                         7 |         0.552 |                 0 |
| bowlers | recency_2yr_half_life    |                         8 |         0.832 |                 0 |
| bowlers | position_band_in_context |                        10 |         1.000 |                 0 |
| bowlers | winsorised_values_1_99   |                        10 |         0.957 |                 0 |

## Reliability

# Audit: Stage 6 (reliability)

Penalties fixed; thresholds halved for split-half and season-to-season (60 pressure balls, 7 matches). The numbers below are reported whatever they are.

## Split-half reliability (200 random match splits, Spearman-Brown corrected)

| role    | quantity        |   mean_split_half_r |   spearman_brown |   sd_over_splits |   mean_players |
|:--------|:----------------|--------------------:|-----------------:|-----------------:|---------------:|
| batters | baseline        |              0.3699 |           0.5311 |           0.1172 |        41.7950 |
| batters | pressure rating |              0.3743 |           0.5358 |           0.1175 |        41.7950 |
| batters | pressure shift  |              0.0823 |           0.1303 |           0.2057 |        41.7950 |
| bowlers | baseline        |              0.4995 |           0.6622 |           0.0745 |        45.2100 |
| bowlers | pressure rating |              0.4989 |           0.6617 |           0.0733 |        45.2100 |
| bowlers | pressure shift  |              0.0912 |           0.1495 |           0.1837 |        45.2100 |

## Decision rule fixed in the blueprint

| role    |   split_half_pressure_rating | decision             |
|:--------|-----------------------------:|:---------------------|
| batters |                       0.5358 | rank on it (>= 0.40) |
| bowlers |                       0.6617 | rank on it (>= 0.40) |

## Season to season (fit on <= 2024, score later; bootstrap over players)

| role    |   players |   pressure_rating_r |   spearman |   ci_lo |   ci_hi |   baseline_r |   shift_r |
|:--------|----------:|--------------------:|-----------:|--------:|--------:|-------------:|----------:|
| batters |        34 |              0.0477 |     0.0032 | -0.2294 |  0.3174 |       0.0271 |    0.0787 |
| bowlers |        37 |              0.5110 |     0.5225 |  0.2517 |  0.7201 |       0.4871 |    0.0673 |

## Does the shift add anything? (later mean value on pressure balls ~ earlier baseline + earlier shift, WLS)

| role    | term                      |   coefficient |   ci_lo |   ci_hi | excludes_zero   |   n |
|:--------|:--------------------------|--------------:|--------:|--------:|:----------------|----:|
| batters | earlier baseline (per SD) |        0.0091 | -0.0501 |  0.0579 | False           |  34 |
| batters | earlier shift (per SD)    |        0.0200 | -0.0156 |  0.0530 | False           |  34 |
| bowlers | earlier baseline (per SD) |        0.0851 |  0.0363 |  0.1327 | True            |  37 |
| bowlers | earlier shift (per SD)    |        0.0112 | -0.0373 |  0.0439 | False           |  37 |

## Permutation test on raw pressure shifts (shuffle the pressure flag within each player)

| role    |   players |   real_spread |   shuffled_mean |   shuffled_p95 |   p_value | real_beyond_p95   |
|:--------|----------:|--------------:|----------------:|---------------:|----------:|:------------------|
| batters |       217 |        0.2697 |          0.2440 |         0.2704 |    0.0620 | False             |
| bowlers |       228 |        0.2523 |          0.2305 |         0.2519 |    0.0480 | True              |
