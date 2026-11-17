# Step 2: bowler net value on pressure balls and the strict-rule list

net runs = (actual - expected bowler-credited wickets) x (mean run value of a wicket on the bowler's pressure balls) - (actual - expected runs conceded). Expected wickets = sum of the model's wicket probability x the share of wickets credited to bowlers; expected runs = model's expected bat runs + expected wide/no-ball runs. Run value of a wicket per ball = (WP* after a dot - WP* after a wicket) / (p-weighted WP* gain per run across the 0,1,2,3,4,6 outcomes). Mean over all pressure balls: 8.09 runs; quantiles {0.1: 2.44, 0.5: 7.59, 0.9: 14.25}. net_p10 / net_p90 = 10th/90th percentile of a match bootstrap (1000).

## Listed bowlers (current top 10)

|   rank | name               |   player_id |   pressure_balls |    wk |   exp_wk |   wicket_ratio |   runs |   exp_runs |   economy_index |   rv_mean |   wicket_effect_runs |   runs_effect_runs |   net_runs |   net_runs_per100 |   net_p10 |   net_p90 |   net_runs_pw |
|-------:|:-------------------|------------:|-----------------:|------:|---------:|---------------:|-------:|-----------:|----------------:|----------:|---------------------:|-------------------:|-----------:|------------------:|----------:|----------:|--------------:|
|      1 | Sunil Narine       |         781 |           300.00 | 18.00 |    14.61 |           1.23 | 359.00 |     434.58 |          121.05 |      8.20 |                27.83 |              75.58 |     103.42 |             34.47 |     36.87 |    163.68 |        101.44 |
|      2 | Kuldeep Yadav      |        3644 |           299.00 | 17.00 |    15.05 |           1.13 | 389.00 |     454.14 |          116.75 |      6.86 |                13.34 |              65.14 |      78.48 |             26.25 |     36.11 |    122.09 |         77.74 |
|      3 | Rashid Khan        |        4722 |           439.00 | 24.00 |    21.88 |           1.10 | 481.00 |     617.41 |          128.36 |      7.17 |                15.22 |             136.41 |     151.62 |             34.54 |     86.97 |    215.29 |        150.53 |
|      4 | Varun Chakravarthy |        6256 |           373.00 | 26.00 |    19.36 |           1.34 | 541.00 |     541.17 |          100.03 |      7.71 |                51.21 |               0.17 |      51.37 |             13.77 |    -23.68 |    117.67 |         46.19 |
|      5 | Josh Hazlewood     |         830 |           352.00 | 30.00 |    19.31 |           1.55 | 474.00 |     528.36 |          111.47 |      9.07 |                96.98 |              54.36 |     151.34 |             43.00 |     56.30 |    242.18 |        136.95 |
|      6 | Wanindu Hasaranga  |        4900 |           364.00 | 26.00 |    19.40 |           1.34 | 532.00 |     504.10 |           94.76 |      6.85 |                45.17 |             -27.90 |      17.27 |              4.75 |    -30.81 |     68.73 |         13.12 |
|      7 | Jasprit Bumrah     |        2933 |           318.00 | 10.00 |    16.93 |           0.59 | 405.00 |     472.04 |          116.55 |      8.89 |               -61.61 |              67.04 |       5.42 |              1.71 |    -68.31 |     85.65 |         12.33 |
|      8 | Axar Patel         |        2876 |           386.00 | 24.00 |    20.16 |           1.19 | 532.00 |     570.64 |          107.26 |      8.04 |                30.91 |              38.64 |      69.54 |             18.02 |     -6.88 |    154.64 |         66.51 |
|      9 | Noor Ahmad         |        7967 |           207.00 | 14.00 |    10.06 |           1.39 | 309.00 |     282.77 |           91.51 |      6.69 |                26.33 |             -26.23 |       0.10 |              0.05 |    -47.98 |     49.19 |         -2.01 |
|     10 | Krunal Pandya      |        4219 |           247.00 | 17.00 |    11.21 |           1.52 | 266.00 |     348.31 |          130.94 |      8.18 |                47.36 |              82.31 |     129.67 |             52.50 |     72.87 |    188.24 |        126.74 |

## Strict-rule list (economy index above 100 on pressure balls required)

|   rank | name               |   player_id |   pressure_rating |   floor_p10 |   economy_index |   wicket_ratio |   net_runs |   net_runs_per100 | new_vs_main   |
|-------:|:-------------------|------------:|------------------:|------------:|----------------:|---------------:|-----------:|------------------:|:--------------|
|      1 | Sunil Narine       |         781 |             0.198 |       0.153 |         121.054 |          1.232 |    103.418 |            34.473 | False         |
|      2 | Kuldeep Yadav      |        3644 |             0.165 |       0.123 |         116.747 |          1.129 |     78.485 |            26.249 | False         |
|      3 | Rashid Khan        |        4722 |             0.170 |       0.119 |         128.360 |          1.097 |    151.625 |            34.539 | False         |
|      4 | Varun Chakravarthy |        6256 |             0.171 |       0.116 |         100.031 |          1.343 |     51.372 |            13.773 | False         |
|      5 | Josh Hazlewood     |         830 |             0.169 |       0.106 |         111.469 |          1.553 |    151.343 |            42.995 | False         |
|      7 | Jasprit Bumrah     |        2933 |             0.149 |       0.095 |         116.553 |          0.591 |      5.425 |             1.706 | False         |
|      8 | Axar Patel         |        2876 |             0.123 |       0.082 |         107.263 |          1.191 |     69.544 |            18.017 | False         |
|     10 | Krunal Pandya      |        4219 |             0.137 |       0.072 |         130.943 |          1.516 |    129.666 |            52.496 | False         |
|     11 | Mujeeb Ur Rahman   |        6450 |             0.120 |       0.056 |         108.210 |          1.336 |     53.116 |            26.426 | True          |
|     12 | Bhuvneshwar Kumar  |         360 |             0.110 |       0.054 |         107.147 |          0.916 |     25.639 |             6.300 | True          |

Dropped from the current list under the strict rule:

|   rank | name              |   player_id |
|-------:|:------------------|------------:|
|      6 | Wanindu Hasaranga |        4900 |
|      9 | Noor Ahmad        |        7967 |

Ranks 11 to 14 of the pool, for reference:

|   rank | name              |   economy_index |
|-------:|:------------------|----------------:|
|     11 | Mujeeb Ur Rahman  |          108.21 |
|     12 | Bhuvneshwar Kumar |          107.15 |
|     13 | Mitchell Santner  |          115.70 |
|     14 | Ravindra Jadeja   |          110.20 |
