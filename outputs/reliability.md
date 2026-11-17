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
