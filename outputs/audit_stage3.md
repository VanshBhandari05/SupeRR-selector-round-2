# Audit: Stage 3 (proving the pressure definition)

## Gate

| gate                                                                                | passed   | detail                                                       |
|:------------------------------------------------------------------------------------|:---------|:-------------------------------------------------------------|
| pressure separates dismissal or boundary rate in >= 2 of 3 phases (match bootstrap) | PASS     | powerplay (1-6): yes; middle (7-15): yes; death (16-20): yes |

Comparison is between live pressure balls and live ordinary balls, standardised within innings x phase x wickets band (cells need >= 30 balls on both sides), 95% match bootstrap (300 resamples).

## Outcome and behaviour shift (phase-level, stratified)

| phase           | metric           |   diff_pressure_minus_ordinary |   ci_lo |   ci_hi | excludes_zero   |
|:----------------|:-----------------|-------------------------------:|--------:|--------:|:----------------|
| powerplay (1-6) | dismissal        |                         0.0007 | -0.0041 |  0.0057 | False           |
| powerplay (1-6) | boundary         |                         0.0187 |  0.0083 |  0.0278 | True            |
| powerplay (1-6) | dot              |                        -0.0453 | -0.0564 | -0.0311 | True            |
| powerplay (1-6) | runs             |                         0.1166 |  0.0629 |  0.1590 | True            |
| powerplay (1-6) | extras           |                         0.0005 | -0.0043 |  0.0052 | False           |
| powerplay (1-6) | attacking_stroke |                         0.0043 | -0.0006 |  0.0094 | False           |
| powerplay (1-6) | defensive_stroke |                        -0.0273 | -0.0368 | -0.0161 | True            |
| powerplay (1-6) | yorker           |                         0.0014 | -0.0020 |  0.0042 | False           |
| powerplay (1-6) | slower           |                         0.0118 |  0.0066 |  0.0178 | True            |
| middle (7-15)   | dismissal        |                         0.0090 |  0.0046 |  0.0144 | True            |
| middle (7-15)   | boundary         |                         0.0144 |  0.0061 |  0.0218 | True            |
| middle (7-15)   | dot              |                        -0.0345 | -0.0442 | -0.0233 | True            |
| middle (7-15)   | runs             |                         0.0862 |  0.0460 |  0.1201 | True            |
| middle (7-15)   | extras           |                         0.0051 |  0.0014 |  0.0098 | True            |
| middle (7-15)   | attacking_stroke |                         0.0107 |  0.0051 |  0.0165 | True            |
| middle (7-15)   | defensive_stroke |                        -0.0154 | -0.0237 | -0.0076 | True            |
| middle (7-15)   | yorker           |                         0.0068 |  0.0037 |  0.0102 | True            |
| middle (7-15)   | slower           |                         0.0136 |  0.0064 |  0.0188 | True            |
| death (16-20)   | dismissal        |                         0.0208 |  0.0096 |  0.0315 | True            |
| death (16-20)   | boundary         |                         0.0170 | -0.0019 |  0.0371 | False           |
| death (16-20)   | dot              |                        -0.0217 | -0.0447 | -0.0020 | True            |
| death (16-20)   | runs             |                         0.1131 |  0.0293 |  0.2055 | True            |
| death (16-20)   | extras           |                         0.0146 |  0.0025 |  0.0262 | True            |
| death (16-20)   | attacking_stroke |                         0.0297 |  0.0163 |  0.0431 | True            |
| death (16-20)   | defensive_stroke |                        -0.0130 | -0.0265 | -0.0001 | True            |
| death (16-20)   | yorker           |                         0.0216 |  0.0069 |  0.0358 | True            |
| death (16-20)   | slower           |                         0.0050 | -0.0109 |  0.0177 | False           |

## Raw cell rates

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

## Where pressure lives

Share of pressure balls before over 16: 75.4%. Pressure balls by innings: {1: 98, 2: 34396}.

|    over |   innings 1 |   innings 2 |
|--------:|------------:|------------:|
|  1.0000 |      0.0000 |      0.1313 |
|  2.0000 |      0.0000 |      0.4009 |
|  3.0000 |      0.0000 |      0.3754 |
|  4.0000 |      0.0000 |      0.4931 |
|  5.0000 |      0.0000 |      0.4865 |
|  6.0000 |      0.0000 |      0.4723 |
|  7.0000 |      0.0000 |      0.1249 |
|  8.0000 |      0.0000 |      0.1714 |
|  9.0000 |      0.0000 |      0.2083 |
| 10.0000 |      0.0000 |      0.3560 |
| 11.0000 |      0.0000 |      0.3708 |
| 12.0000 |      0.0000 |      0.3857 |
| 13.0000 |      0.0000 |      0.4378 |
| 14.0000 |      0.0000 |      0.4269 |
| 15.0000 |      0.0000 |      0.4297 |
| 16.0000 |      0.0000 |      0.4376 |
| 17.0000 |      0.0000 |      0.4494 |
| 18.0000 |      0.0000 |      0.4699 |
| 19.0000 |      0.0057 |      0.4856 |
| 20.0000 |      0.0141 |      0.4540 |

## Close games against blowouts

| close   |   matches |   median_peak_LI |   mean_peak_LI |   median_mean_LI |   median_total_LI |
|:--------|----------:|-----------------:|---------------:|-----------------:|------------------:|
| False   |       671 |           1.6001 |         2.6273 |           0.8767 |          186.8341 |
| True    |       137 |          10.1484 |        12.2160 |           1.3083 |          324.0343 |

Mann-Whitney (close > other) peak LI p=6.27e-56; mean LI per live ball p=1.59e-44. Spearman peak LI vs runs margin (wins by runs, n=395): -0.853 (p=8.4e-113); mean LI vs margin: -0.775; peak LI vs wickets in hand (wins by wickets, n=404): -0.623.

Matches classed close: 137 of 808 clean matches (blueprint expected about 130 across all matches).

## Benchmark agreement (innings 2)

Bhattacharjee-Lemmer PI = (CRRR/IRRR) x 0.5 x [exp(RU/100) + exp(sum w_i / 11)], wicket weights by batting position of the dismissed batter. RU (resources used) is DERIVED from our own scoring model (100 x (1 - expected runs to come / expected runs at the start)), because the Duckworth-Lewis table is not in the data. Spearman(PI, LI): live chase balls 0.328; all chase balls 0.110; by phase [np.float64(0.089), np.float64(0.266), np.float64(0.233)]. Share of the top-20% PI balls that are pressure balls: 0.679.

Rule-of-thumb overlap (live balls):

|   innings |   rule_balls |   pressure_balls |      both |   share_of_rule_that_is_pressure |   share_of_pressure_in_rule |   jaccard |
|----------:|-------------:|-----------------:|----------:|---------------------------------:|----------------------------:|----------:|
|    1.0000 |   16710.0000 |          98.0000 |   98.0000 |                           0.0059 |                      1.0000 |    0.0059 |
|    2.0000 |    6078.0000 |       34396.0000 | 5630.0000 |                           0.9263 |                      0.1637 |    0.1616 |

Figures: figures/stage3_separation.png, stage3_where_pressure_lives.png, stage3_close_games.png, stage3_case_studies.png