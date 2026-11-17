# Audit: Stage 6, sensitivity grid

Main ranking proxy: rating minus 1.2816 x main bootstrap SD (the floor), among eligible and active players. Penalties fixed. Overlap is with the main top 10 by the same proxy.

| role    | variant                  |   top10_overlap_with_main |   kendall_tau |   players_missing |
|:--------|:-------------------------|--------------------------:|--------------:|------------------:|
| batters | cutoff_top10%            |                         9 |        0.9637 |                 0 |
| batters | cutoff_top15%            |                         9 |        0.9724 |                 0 |
| batters | cutoff_top25%            |                         9 |        0.9710 |                 0 |
| batters | cutoff_top30%            |                         9 |        0.9594 |                 0 |
| batters | cutoff_within_innings    |                         9 |        0.9376 |                 0 |
| batters | no_cutoff_log_leverage   |                         9 |        0.9144 |                 0 |
| batters | benchmark_pressure_index |                        10 |        0.9478 |                 0 |
| batters | benchmark_rule_of_thumb  |                        10 |        0.9289 |                 0 |
| batters | lower_tier_included      |                        10 |        0.9565 |                 0 |
| batters | IPL_only                 |                         6 |        0.7344 |                 0 |
| batters | T20I_only                |                         6 |        0.5385 |                 0 |
| batters | recency_2yr_half_life    |                         8 |        0.8026 |                 0 |
| batters | position_band_in_context |                        10 |        0.9826 |                 0 |
| batters | winsorised_values_1_99   |                        10 |        0.9782 |                 0 |
| bowlers | cutoff_top10%            |                         9 |        0.9367 |                 0 |
| bowlers | cutoff_top15%            |                        10 |        0.9609 |                 0 |
| bowlers | cutoff_top25%            |                        10 |        0.9771 |                 0 |
| bowlers | cutoff_top30%            |                        10 |        0.9663 |                 0 |
| bowlers | cutoff_within_innings    |                         9 |        0.9232 |                 0 |
| bowlers | no_cutoff_log_leverage   |                         9 |        0.9178 |                 0 |
| bowlers | benchmark_pressure_index |                         9 |        0.9380 |                 0 |
| bowlers | benchmark_rule_of_thumb  |                         9 |        0.9192 |                 0 |
| bowlers | lower_tier_included      |                        10 |        0.9515 |                 0 |
| bowlers | IPL_only                 |                         8 |        0.6377 |                 0 |
| bowlers | T20I_only                |                         7 |        0.5515 |                 0 |
| bowlers | recency_2yr_half_life    |                         8 |        0.8316 |                 0 |
| bowlers | position_band_in_context |                        10 |        1.0000 |                 0 |
| bowlers | winsorised_values_1_99   |                        10 |        0.9569 |                 0 |

## Median overlap (blueprint wants >= 7 of 10)

| role    |   median_overlap_of_10 |
|:--------|-----------------------:|
| batters |                 9.0000 |
| bowlers |                 9.0000 |

Not run: win probability without recalibration (would require rerunning Stage 2c leverage with the recalibration switched off).