# Audit: Stage 4 (ball values, credit split, rating regression)

## Gates

| gate                                            | passed   | detail                       |
|:------------------------------------------------|:---------|:-----------------------------|
| batter baseline vs strike rate rank correlation | PASS     | rho = 0.708 (>= 0.5), n=53   |
| bowler baseline vs economy rank correlation     | PASS     | rho = -0.795 (<= -0.4), n=56 |

Chosen penalties by 5-fold CV (whole matches held out): lambda_B = 300, lambda_C = 3000 (held-out MSE 3.04371). Penalty at grid edge: baseline False, shift False.

Shift penalty / baseline penalty = 10.0x (blueprint expected the shift penalty to be much larger).

## CV grid

|     lambda_B |      300 |     1000 |     3000 |    10000 |    30000 |   100000 |
|-------------:|---------:|---------:|---------:|---------:|---------:|---------:|
|    30.000000 | 3.050405 | 3.049994 | 3.049955 | 3.049959 | 3.049963 | 3.049964 |
|   100.000000 | 3.046072 | 3.045664 | 3.045627 | 3.045632 | 3.045636 | 3.045638 |
|   300.000000 | 3.044153 | 3.043748 | 3.043715 | 3.043722 | 3.043727 | 3.043729 |
|  1000.000000 | 3.044296 | 3.043922 | 3.043913 | 3.043932 | 3.043941 | 3.043944 |
|  3000.000000 | 3.045710 | 3.045451 | 3.045511 | 3.045563 | 3.045582 | 3.045589 |
| 10000.000000 | 3.047057 | 3.046945 | 3.047092 | 3.047186 | 3.047218 | 3.047230 |

## Spread of ratings (shrinkage)

| role    |   sd_baseline |   sd_shift |   sd_baseline_eligible |   sd_shift_eligible |
|:--------|--------------:|-----------:|-----------------------:|--------------------:|
| batters |        0.0534 |     0.0037 |                 0.0628 |              0.0085 |
| bowlers |        0.0538 |     0.0042 |                 0.0667 |              0.0084 |

Ball values: batter rows 150,307, bowler rows 156,062; v quantiles {0.0: -14.86, 0.001: -10.145, 0.01: -7.764, 0.25: -0.478, 0.5: -0.072, 0.75: 0.428, 0.99: 3.771, 0.999: 4.496, 1.0: 5.709}

Eligible batters 53, bowlers 56. (Fallback used: batters False, bowlers False.)
