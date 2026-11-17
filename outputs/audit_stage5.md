# Audit: Stage 5 (fair comparison)

Penalties fixed at lambda_B=300, lambda_C=3000. 300 whole-match bootstrap resamples of both fits. Rules came from config.yaml (locked before any leaderboard was viewed).

## Eligibility

| role    |   eligible |   eligible_and_active |
|:--------|-----------:|----------------------:|
| batters |         53 |                    53 |
| bowlers |         56 |                    55 |

## Uncertainty

| role    |   median_boot_sd_eligible |   sd_of_ratings_eligible |   share_eligible_shift_interval_excludes_zero |
|:--------|--------------------------:|-------------------------:|----------------------------------------------:|
| batters |                    0.0473 |                   0.0657 |                                        0.3019 |
| bowlers |                    0.0413 |                   0.0685 |                                        0.1964 |

## Cross-check: simple shrunk version vs regression (blueprint wants Spearman >= 0.8)

| role    |   spearman_regression_vs_simple |   k_baseline |   k_shift |   n |
|:--------|--------------------------------:|-------------:|----------:|----:|
| batters |                          0.9696 |     234.9667 |  567.1337 |  53 |
| bowlers |                          0.9839 |     182.5514 |  429.8722 |  56 |
