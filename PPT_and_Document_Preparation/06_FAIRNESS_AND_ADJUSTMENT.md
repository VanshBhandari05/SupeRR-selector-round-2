# 06 FAIRNESS AND ADJUSTMENT

## 1. Raw vs shrunk ratings of the 20 listed players

Three numbers per player, all in the same unit (value per ball, in units of expected swing in win probability):
- **raw** = unshrunk mean ball value `v` on the player's pressure balls (NEW aggregation of `outputs/ball_values_bat.parquet` / `ball_values_bowl.parquet`; no opposition adjustment, no shrinkage; `n` is the number of pressure-ball rows);
- **simple shrunk** = `simple_rating` in the pipeline (shrunk raw means, no regression, no opposition terms; Stage 5 cross-check);
- **final ridge pressure rating** = baseline + shift from the regression (the ranking input).
The final rating is NOT just 'raw pulled toward zero': it also removes opposition strength and context terms, so some players move up (e.g. Tim David raw 0.131 -> 0.226). Compare the first two columns to see pure shrinkage.

| role    |   rank |   player_id | name                 |   pressure_balls |   raw_mean_value_on_pressure_balls |   simple_shrunk_rating |   final_ridge_pressure_rating |   shrink_effect (simple - raw) |   adjustment_effect (ridge - simple) |
|:--------|-------:|------------:|:---------------------|-----------------:|-----------------------------------:|-----------------------:|------------------------------:|-------------------------------:|-------------------------------------:|
| batters |      1 |        4260 | Heinrich Klaasen     |              200 |                             0.3602 |                 0.2048 |                        0.2449 |                        -0.1553 |                               0.0401 |
| batters |      2 |        1699 | Suryakumar Yadav     |              433 |                             0.2616 |                 0.2147 |                        0.2477 |                        -0.0469 |                               0.0330 |
| batters |      3 |        6396 | Tim David            |              270 |                             0.1310 |                 0.1857 |                        0.2260 |                         0.0547 |                               0.0403 |
| batters |      4 |        6281 | Abhishek Sharma      |              385 |                             0.1445 |                 0.1523 |                        0.2094 |                         0.0077 |                               0.0571 |
| batters |      5 |        5553 | Phil Salt            |              231 |                             0.3039 |                 0.1757 |                        0.1937 |                        -0.1282 |                               0.0180 |
| batters |      6 |        3647 | Shreyas Iyer         |              298 |                             0.3494 |                 0.1732 |                        0.1877 |                        -0.1761 |                               0.0144 |
| batters |      7 |        7897 | Namboori Tilak Varma |              498 |                             0.1454 |                 0.1226 |                        0.1636 |                        -0.0228 |                               0.0410 |
| batters |      8 |       23450 | Sai Sudharsan        |              312 |                             0.0587 |                 0.0816 |                        0.1424 |                         0.0229 |                               0.0609 |
| batters |      9 |        3125 | Nicholas Pooran      |              368 |                             0.1697 |                 0.1166 |                        0.1590 |                        -0.0530 |                               0.0423 |
| batters |     10 |        6288 | Shubman Gill         |              470 |                             0.0982 |                 0.0832 |                        0.1357 |                        -0.0151 |                               0.0526 |
| bowlers |      1 |         781 | Sunil Narine         |              300 |                             0.2079 |                 0.1777 |                        0.1980 |                        -0.0302 |                               0.0203 |
| bowlers |      2 |        3644 | Kuldeep Yadav        |              299 |                             0.1799 |                 0.1473 |                        0.1650 |                        -0.0326 |                               0.0178 |
| bowlers |      3 |        4722 | Rashid Khan          |              439 |                             0.1966 |                 0.1672 |                        0.1699 |                        -0.0294 |                               0.0027 |
| bowlers |      4 |        6256 | Varun Chakravarthy   |              373 |                             0.0844 |                 0.1248 |                        0.1705 |                         0.0404 |                               0.0457 |
| bowlers |      5 |         830 | Josh Hazlewood       |              352 |                             0.1907 |                 0.1596 |                        0.1687 |                        -0.0311 |                               0.0091 |
| bowlers |      6 |        4900 | Wanindu Hasaranga    |              364 |                             0.0290 |                 0.1024 |                        0.1431 |                         0.0734 |                               0.0408 |
| bowlers |      7 |        2933 | Jasprit Bumrah       |              318 |                             0.0391 |                 0.1071 |                        0.1487 |                         0.0680 |                               0.0416 |
| bowlers |      8 |        2876 | Axar Patel           |              386 |                             0.1720 |                 0.1173 |                        0.1226 |                        -0.0547 |                               0.0053 |
| bowlers |      9 |        7967 | Noor Ahmad           |              207 |                             0.0098 |                 0.0986 |                        0.1442 |                         0.0888 |                               0.0456 |
| bowlers |     10 |        4219 | Krunal Pandya        |              247 |                             0.3023 |                 0.1459 |                        0.1367 |                        -0.1564 |                              -0.0091 |

Across all eligible players: Pearson r(raw, final) = 0.724 batters (n=53), 0.732 bowlers (n=56); r(simple shrunk, final) = 0.979 / 0.978. (New aggregation; the pipeline's own rank cross-check is Spearman 0.9696 / 0.9839, `audit_stage5.md`.)

Figure: `08_FIGURES/F04_raw_vs_shrunk.png`.

## 2. Opposition adjustment: biggest rank movers

Compares the rank by **final ridge pressure rating** (which has opposing players' terms in the regression) with the rank by **simple shrunk rating** (no regression, no opposition terms) among all eligible players (53 batters, 56 bowlers). Caveat: the two versions also differ in how they shrink, so this is 'regression with opposition adjustment vs simple shrunk', not an isolated opposition effect. Positive `rank_gain` = the regression ranks him higher than the simple version. (NEW aggregation of existing `simple_rating` and `pressure_rating` columns; ranks computed among all eligible players, ties broken by order.)

**batters: top 5 up**

| name           |   player_id |   rank_simple |   rank_regression |   rank_gain |
|:---------------|------------:|--------------:|------------------:|------------:|
| Mitchell Marsh |         818 |            18 |                11 |           7 |
| Sanju Samson   |        2258 |            32 |                25 |           7 |
| Lokesh Rahul   |         953 |            21 |                15 |           6 |
| Riyan Parag    |        6423 |            29 |                23 |           6 |
| Travis Head    |        2367 |            25 |                20 |           5 |

**batters: top 5 down**

| name            |   player_id |   rank_simple |   rank_regression |   rank_gain |
|:----------------|------------:|--------------:|------------------:|------------:|
| Pathum Nissanka |        6931 |            16 |                27 |         -11 |
| Rovman Powell   |        4986 |            14 |                21 |          -7 |
| Sikandar Raza   |        2984 |            22 |                29 |          -7 |
| Rinku Singh     |        4708 |            20 |                26 |          -6 |
| Tanzid Hasan    |        7900 |            38 |                44 |          -6 |

**bowlers: top 5 up**

| name               |   player_id |   rank_simple |   rank_regression |   rank_gain |
|:-------------------|------------:|--------------:|------------------:|------------:|
| Varun Chakravarthy |        6256 |             7 |                 2 |           5 |
| Mustafizur Rahman  |        4373 |            27 |                22 |           5 |
| Kagiso Rabada      |        3628 |            24 |                19 |           5 |
| Noor Ahmad         |        7967 |            12 |                 7 |           5 |
| Hardik Pandya      |        3330 |            54 |                49 |           5 |

**bowlers: top 5 down**

| name             |   player_id |   rank_simple |   rank_regression |   rank_gain |
|:-----------------|------------:|--------------:|------------------:|------------:|
| Patrick Cummins  |        1758 |            20 |                26 |          -6 |
| Mujeeb Ur Rahman |        6450 |             6 |                11 |          -5 |
| Mohammad Nabi    |        1107 |            50 |                55 |          -5 |
| Mohammad Nawaz   |        2490 |             8 |                12 |          -4 |
| FazalHaq Farooqi |        7240 |            38 |                42 |          -4 |

## 3. Share of pressure-rating variance from baseline vs pressure shift

NEW computation (not in the pipeline) on the eligible players' ridge estimates: `var(B + C) = var(B) + var(C) + 2cov(B, C)`.

| role    |   n |   var_baseline |   var_shift |   cov_2x |   var_rating |   share_baseline |   share_shift |   share_covariance |   corr_baseline_shift |
|:--------|----:|---------------:|------------:|---------:|-------------:|-----------------:|--------------:|-------------------:|----------------------:|
| batters |  53 |        0.00395 |     0.00007 |  0.00029 |      0.00431 |          0.91502 |       0.01677 |            0.06821 |               0.27530 |
| bowlers |  56 |        0.00444 |     0.00007 |  0.00018 |      0.00469 |          0.94664 |       0.01508 |            0.03828 |               0.16019 |

Reading: the baseline accounts for about 92% (batters) and 95% (bowlers) of the variance of the pressure rating among eligible players; the shift's own variance share is about 1.7% and 1.5%; the rest is covariance. This agrees with the pipeline: shift split-half reliability 0.13 / 0.15, and the shift penalty is 10x the baseline penalty.

## 4. Eligible-player counts

| role | eligible | eligible and active (2025-26) | removed for reliably negative shift | ranked pool |
|---|---|---|---|---|
| batters | 53 | 53 | 6 | 47 |
| bowlers | 56 | 55 | 7 | 48 |

Sources: `website/data/meta.json`, `outputs/audit_stage5.md`, `audit_stage7.md`. Players with any rows at all: 627 batters, 459 bowlers (`meta.json`, `players_with_any_rows_*`).

## 5. Player tables in this pack

- `player_ratings.csv`: all 109 eligible players (53 batters + 56 bowlers) with baseline, shift, pressure rating, floor, 90th percentile, bootstrap SD, P(top 10/20), rank interval, `simple_rating`, sample sizes (pressure balls and matches), companion cricket stats, active flag, whether he is in the ranked pool, his pool rank, whether removed for a negative shift, and whether he is listed.
- `players_unfiltered.csv`: the pipeline's own unfiltered appendix lists (`outputs/unfiltered_eligible_batters.csv`, `unfiltered_eligible_bowlers.csv`) stacked, unchanged, with a `role` column. These contain every eligible player whether or not active.
