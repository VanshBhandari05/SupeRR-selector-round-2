# Audit: Stage 0 and 1

Raw file: 200,999 rows, 867 matches. Output table: 193,076 rows, 808 matches (728 in the rating sample).

## Gates

| gate                    | passed   | detail                                                                                                                |
|:------------------------|:---------|:----------------------------------------------------------------------------------------------------------------------|
| columns                 | PASS     | 33 columns                                                                                                            |
| unique key              | PASS     | 0 duplicate (match_id, innings, innings_ball_num)                                                                     |
| competition tags        | PASS     | {'T20I-full': 428, 'IPL': 371, 'T20I-assoc': 54, 'A-team': 30}; non-T20I in T20I groups: 0                            |
| result parser           | PASS     | {'wickets': 419, 'runs': 414, 'no_result': 40, 'tie': 10}                                                             |
| rain flag               | PASS     | 38 matches flagged                                                                                                    |
| truncation flag         | PASS     | flagged [14130, 14164, 15795, 18532, 31278, 48514, 50407]; expected [14130, 14164, 15795, 18532, 31278, 48514, 50407] |
| rating sample           | PASS     | 728 matches: {'T20I-full': 375, 'IPL': 353}, ties 7                                                                   |
| strike rule             | PASS     | 0.99977 agreement on 170,306 normal balls                                                                             |
| legal balls <= 120      | PASS     | max 120                                                                                                               |
| first innings 120 legal | PASS     | 686 not-bowled-out first innings; 0 not 120 {}                                                                        |
| wickets gate            | PASS     | 403 of 404 chases won by wickets match; failures [20190]                                                              |
| margin gate             | PASS     | n=395 median|err|=0.0 p95=4.0 max=8.0                                                                                 |
| margin outliers         | PASS     | 0 matches off by more than 8 runs                                                                                     |
| external totals         | PASS     | mean error -1.00 (allowed -3 to 1); 29 of 30 within 5 (need 27)                                                       |

## Rows removed (applied in this order)

| rule                             |   rows removed |   matches |
|:---------------------------------|---------------:|----------:|
| innings > 2 (super overs)        |             38 |         6 |
| no result                        |           1753 |        24 |
| rain                             |           4726 |        28 |
| truncated                        |           1406 |         7 |
| no ball data (abandoned, 0 rows) |              0 |        16 |

## Matches by group

| group      |   clean matches |
|:-----------|----------------:|
| T20I-full  |             375 |
| IPL        |             353 |
| T20I-assoc |              50 |
| A-team     |              30 |

Rating sample by group: {'T20I-full': 375, 'IPL': 353}; ties kept: 7

## Truncation flag: every flagged match

|   match_id | match_date   | group     | result                               |   legal1 |   wk1 |   legal2 |   wk2 |
|-----------:|:-------------|:----------|:-------------------------------------|---------:|------:|---------:|------:|
|      14130 | 2022-04-24   | IPL       | Lucknow Super Giants Won 36  Runs    |      119 |     6 |      119 |     8 |
|      14164 | 2022-05-22   | IPL       | Punjab Kings Won by 5 wickets        |      119 |     8 |       91 |     5 |
|      15795 | 2022-06-26   | T20I-full | India Won by 7 Wickets               |       72 |     4 |       56 |     3 |
|      18532 | 2022-11-22   | T20I-full | Match Tied                           |      118 |    10 |       54 |     4 |
|      31278 | 2024-05-11   | IPL       | Kolkata Knight Riders Won by 18 runs |       96 |     7 |       96 |     8 |
|      48514 | 2026-01-12   | T20I-full | Sri Lanka Won by 14 runs             |       72 |     6 |       72 |     8 |
|      50407 | 2026-10-14   | T20I-full | West Indies Won by 24 runs           |      120 |     3 |      117 |     9 |

## External totals check

Sample (seed 42): [14152, 14154, 14159, 17739, 31242, 31246, 35427, 40719, 40762, 41977, 43594, 45504, 45505, 48467, 50598]

|   match_id | match_date   |   R1 |   public_total_inn1 |   err1 |   R2 |   public_total_inn2 |   err2 | source                                                          |
|-----------:|:-------------|-----:|--------------------:|-------:|-----:|--------------------:|-------:|:----------------------------------------------------------------|
|      14152 | 2022-05-11   |  160 |                 160 |      0 |  161 |                 161 |      0 | espncricinfo.com/ci/engine/match/1304104.html                   |
|      14154 | 2022-05-13   |  209 |                 209 |      0 |  155 |                 155 |      0 | espncricinfo.com/ci/engine/match/1304106.html                   |
|      14159 | 2022-05-17   |  193 |                 193 |      0 |  190 |                 190 |      0 | espncricinfo.com/ci/engine/match/1304111.html                   |
|      17739 | 2022-10-09   |  137 |                 137 |      0 |  142 |                 142 |      0 | espncricinfo.com/ci/engine/match/1322336.html                   |
|      31242 | 2024-04-10   |  196 |                 196 |      0 |  199 |                 199 |      0 | espncricinfo.com/ci/engine/match/1426262.html                   |
|      31246 | 2024-04-14   |  161 |                 161 |      0 |  160 |                 162 |     -2 | espncricinfo.com/ci/engine/match/1426266.html                   |
|      35427 | 2024-08-26   |  132 |                 132 |      0 |  120 |                 124 |     -4 | espncricinfo.com/ci/engine/match/1446764.html                   |
|      40719 | 2025-04-12   |  180 |                 180 |      0 |  182 |                 186 |     -4 | espncricinfo.com/ci/engine/match/1473463.html                   |
|      40762 | 2025-05-25   |  230 |                 230 |      0 |  143 |                 147 |     -4 | espncricinfo.com/ci/engine/match/1473504.html                   |
|      41977 | 2025-11-02   |  186 |                 186 |      0 |  186 |                 188 |     -2 | sportsyaari/skysports/lokmattimes (AUS 186/6; IND 188/5)        |
|      43594 | 2025-07-13   |  179 |                 177 |      2 |   94 |                  94 |      0 | espncricinfo.com/ci/engine/match/1485509.html                   |
|      45504 | 2025-09-17   |  148 |                 146 |      2 |  101 |                 105 |     -4 | sportsyaari/cricketsky/pcb.com.pk (one live blog said 144)      |
|      45505 | 2025-09-18   |  169 |                 169 |      0 |  163 |                 171 |     -8 | espncricinfo.com/ci/engine/match/1496930.html                   |
|      48467 | 2026-01-31   |  170 |                 170 |      0 |  140 |                 140 |      0 | cricketireland.ie/wisden/cricketaddictor                        |
|      50598 | 2026-06-19   |  192 |                 196 |     -4 |  187 |                 189 |     -2 | mykhel (BAN total single source; consistent with won by 7 runs) |

## Chase difference (diagnostic, not a gate)

won chases n=404: mean 1.49, sd 3.14; below 0: 68, above 5: 32

## Overs without 6 legal balls (report only, not the final over)

|   match_id |   innings |   overid |   legal |   lastov |
|-----------:|----------:|---------:|--------:|---------:|
|      41509 |         1 |       12 |       7 |       20 |

## Wickets gate: 410 vs 406

By-wicket chases by exclusion: all 419; without DLS wording 410; in clean sample 404. Matches in the 410-style count but not in the clean sample:

|   match_id | match_date   | group     | result                        | drop_reason   |   first_inn_revised_overs |   second_inn_revised_overs |   revised_target |
|-----------:|:-------------|:----------|:------------------------------|:--------------|--------------------------:|---------------------------:|-----------------:|
|      14164 | 2022-05-22   | IPL       | Punjab Kings Won by 5 wickets | truncated     |                       nan |                        nan |              nan |
|      15795 | 2022-06-26   | T20I-full | India Won by 7 Wickets        | truncated     |                       nan |                        nan |              nan |
|      17395 | 2022-09-23   | T20I-full | India Won by 6 Wickets        | rain          |                        48 |                         48 |               91 |
|      19959 | 2023-03-25   | T20I-full | West Indies won by 3 wickets  | rain          |                        66 |                        nan |              nan |
|      40727 | 2025-04-18   | IPL       | Punjab Kings Won by 5 wickets | rain          |                        84 |                         84 |               96 |
|      39809 | 2025-03-18   | T20I-full | New Zealand Won by 5 wickets  | rain          |                        90 |                         90 |              136 |

## Does imputing 4 inflate totals?

Rebuilt totals against the forward target (first innings + 1) in won chases, for each non-rotating bye value:

|   nonrot_value |   margin_median |   margin_p95 |   chases_below_target |   chases_over_by_gt5 |
|---------------:|----------------:|-------------:|----------------------:|---------------------:|
|              1 |               1 |            7 |                   100 |                   49 |
|              2 |               0 |            6 |                    86 |                   38 |
|              4 |               0 |            4 |                    68 |                   32 |

Value used: 4. Margin cancels same-sign overcounts; the chase-vs-target counts do not.

## Margin outliers (> 8 runs)

none

## Wickets gate failures

|   match_id | result                                |   wk_end |   expected |
|-----------:|:--------------------------------------|---------:|-----------:|
|      20190 | Lucknow Super Giants Won by 6 wickets |        5 |          4 |

## Notes

- Result/winner inconsistencies (runs win not by first batter, or wickets win not by chaser): 3 [24822, 28334, 48610]
- Inferred dismissed_player_id for match 40709 innings 2 ball 117: candidates absent later = [np.int64(7897)]; set to 7897.0
- Bye/leg-bye rows where rotation was unknowable (final ball of innings or wicket ball), imputed 1 instead of 4: 59
- Legal balls per over, match 41509 innings 1: {1: 6, 2: 6, 3: 6, 4: 6, 5: 6, 6: 6, 7: 6, 8: 6, 9: 6, 10: 6, 11: 6, 12: 7, 13: 6, 14: 6, 15: 6, 16: 6, 17: 6, 18: 6, 19: 6, 20: 4}; sum = 119