# 01 RANKINGS: the two final top-10 lists, exactly as run

Source: `outputs/top10_batters.csv`, `outputs/top10_bowlers.csv` (copied into this pack unchanged), `outputs/eligible_table_*.csv` (pressure balls, matches), `outputs/evidence_cards.md` (IPL vs T20I split). Pressure balls and matches with pressure balls from the cards equal the eligible tables (asserted at build time). Columns: **80% interval** is the 10th to 90th percentile of the pressure rating over 300 whole-match bootstrap resamples; **floor** is its 10th percentile (the ranking statistic). `p_top10`/`p_top20` = share of resamples in which the player finishes in the top 10 / 20 of the eligible, active pool (53 batters, 55 bowlers). `delivery_rate` = share of matches with 6+ pressure balls in which the player's total value was positive. `fragile` = in the top 10 under fewer than half of the 14 sensitivity variants.

## Top 10 batters

|   rank |   player_id | name                 | teams                                 |   pressure_rating | 80% interval (p10 to p90)   |   floor_p10 |   baseline |   shift |   pressure_balls |   matches_with_pressure_balls | IPL / T20I pressure balls   |   p_top10 |   p_top20 |   delivery_rate | fragile   |
|-------:|------------:|:---------------------|:--------------------------------------|------------------:|:----------------------------|------------:|-----------:|--------:|-----------------:|------------------------------:|:----------------------------|----------:|----------:|----------------:|:----------|
|      1 |        4260 | Heinrich Klaasen     | Sunrisers Hyderabad / South Africa    |            0.2449 | [0.197, 0.292]              |      0.1969 |     0.2324 |  0.0125 |              200 |                            19 | 160 / 40                    |    0.9933 |    1.0000 |          0.8889 | False     |
|      2 |        1699 | Suryakumar Yadav     | Mumbai Indians / India                |            0.2477 | [0.194, 0.302]              |      0.1939 |     0.2373 |  0.0104 |              433 |                            33 | 265 / 168                   |    0.9900 |    1.0000 |          0.7391 | False     |
|      3 |        6396 | Tim David            | Mumbai Indians / Australia            |            0.2260 | [0.165, 0.303]              |      0.1651 |     0.2294 | -0.0034 |              270 |                            29 | 147 / 123                   |    0.9067 |    0.9667 |          0.5789 | False     |
|      4 |        6281 | Abhishek Sharma      | Sunrisers Hyderabad / India           |            0.2094 | [0.143, 0.271]              |      0.1428 |     0.2085 |  0.0008 |              385 |                            33 | 288 / 97                    |    0.8500 |    0.9767 |          0.6818 | False     |
|      5 |        5553 | Phil Salt            | Royal Challengers Bengaluru / England |            0.1937 | [0.129, 0.254]              |      0.1289 |     0.1823 |  0.0114 |              231 |                            19 | 74 / 157                    |    0.7633 |    0.9567 |          0.7333 | False     |
|      6 |        3647 | Shreyas Iyer         | Punjab Kings / India                  |            0.1877 | [0.126, 0.245]              |      0.1265 |     0.1655 |  0.0222 |              298 |                            20 | 255 / 43                    |    0.7433 |    0.9400 |          0.7500 | False     |
|      7 |        7897 | Namboori Tilak Varma | Mumbai Indians / India                |            0.1636 | [0.121, 0.211]              |      0.1214 |     0.1575 |  0.0060 |              497 |                            33 | 252 / 246                   |    0.5867 |    0.9300 |          0.6154 | False     |
|      8 |       23450 | Sai Sudharsan        | Gujarat Titans                        |            0.1424 | [0.102, 0.175]              |      0.1017 |     0.1435 | -0.0011 |              312 |                            24 | 312 / 0                     |    0.2833 |    0.8133 |          0.5625 | False     |
|      9 |        3125 | Nicholas Pooran      | Lucknow Super Giants / West Indies    |            0.1590 | [0.099, 0.225]              |      0.0992 |     0.1500 |  0.0090 |              368 |                            33 | 204 / 164                   |    0.5633 |    0.8600 |          0.6250 | False     |
|     10 |        6288 | Shubman Gill         | Gujarat Titans / India                |            0.1357 | [0.094, 0.172]              |      0.0941 |     0.1316 |  0.0041 |              469 |                            36 | 387 / 83                    |    0.2467 |    0.7600 |          0.5652 | False     |

## Top 10 bowlers

|   rank |   player_id | name               | teams                                   |   pressure_rating | 80% interval (p10 to p90)   |   floor_p10 |   baseline |   shift |   pressure_balls |   matches_with_pressure_balls | IPL / T20I pressure balls   |   p_top10 |   p_top20 |   delivery_rate | fragile   |
|-------:|------------:|:-------------------|:----------------------------------------|------------------:|:----------------------------|------------:|-----------:|--------:|-----------------:|------------------------------:|:----------------------------|----------:|----------:|----------------:|:----------|
|      1 |         781 | Sunil Narine       | Kolkata Knight Riders                   |            0.1980 | [0.153, 0.245]              |      0.1532 |     0.1927 |  0.0053 |              300 |                            23 | 300 / 0                     |    0.9833 |    1.0000 |          0.5909 | False     |
|      2 |        3644 | Kuldeep Yadav      | Delhi Capitals / India                  |            0.1650 | [0.123, 0.211]              |      0.1231 |     0.1588 |  0.0062 |              299 |                            20 | 233 / 66                    |    0.8467 |    0.9933 |          0.7368 | False     |
|      3 |        4722 | Rashid Khan        | Gujarat Titans / Afghanistan            |            0.1699 | [0.119, 0.217]              |      0.1188 |     0.1632 |  0.0067 |              439 |                            33 | 235 / 204                   |    0.8400 |    0.9800 |          0.7333 | False     |
|      4 |        6256 | Varun Chakravarthy | Kolkata Knight Riders / India           |            0.1705 | [0.116, 0.220]              |      0.1163 |     0.1754 | -0.0048 |              373 |                            31 | 249 / 124                   |    0.8000 |    0.9833 |          0.5769 | False     |
|      5 |         830 | Josh Hazlewood     | Royal Challengers Bengaluru / Australia |            0.1687 | [0.106, 0.226]              |      0.1059 |     0.1621 |  0.0066 |              352 |                            25 | 236 / 116                   |    0.7800 |    0.9700 |          0.5909 | False     |
|      6 |        4900 | Wanindu Hasaranga  | Royal Challengers Bengaluru / Sri Lanka |            0.1431 | [0.099, 0.197]              |      0.0994 |     0.1547 | -0.0116 |              364 |                            26 | 208 / 156                   |    0.6833 |    0.9633 |          0.5000 | False     |
|      7 |        2933 | Jasprit Bumrah     | Mumbai Indians / India                  |            0.1487 | [0.095, 0.195]              |      0.0953 |     0.1569 | -0.0082 |              318 |                            27 | 239 / 79                    |    0.6700 |    0.9533 |          0.4091 | False     |
|      8 |        2876 | Axar Patel         | Delhi Capitals / India                  |            0.1226 | [0.082, 0.169]              |      0.0815 |     0.1111 |  0.0115 |              386 |                            35 | 173 / 213                   |    0.3900 |    0.9033 |          0.6071 | False     |
|      9 |        7967 | Noor Ahmad         | Chennai Super Kings / Afghanistan       |            0.1442 | [0.074, 0.204]              |      0.0744 |     0.1503 | -0.0060 |              207 |                            16 | 139 / 68                    |    0.5400 |    0.8667 |          0.3077 | False     |
|     10 |        4219 | Krunal Pandya      | Lucknow Super Giants                    |            0.1367 | [0.072, 0.196]              |      0.0725 |     0.1207 |  0.0160 |              247 |                            18 | 247 / 0                     |    0.5367 |    0.8667 |          0.7647 | False     |

## The ranking rule exactly as run

From the stage-7 code docstring (`src/stage7_rank.py`) and `config.yaml`:

> Eligible + active players; drop anyone whose pressure shift is reliably negative (90th percentile of the bootstrap shift below zero); sort by the floor (10th percentile of the bootstrap pressure rating); ties by delivery rate, then pressure balls.

- **Eligible:** at least 120 pressure balls over at least 15 matches (fixed before any leaderboard was viewed). Fallback (90 balls / 12 matches if fewer than 40 qualify) was NOT used.
- **Active:** any appearance in 2025 or 2026 (CHANGES #25).
- **Removal step:** a player is removed if the 90th percentile of his bootstrap pressure shift is below zero (`shift_p90 < 0`).
- **Sort:** descending `floor_p10` (the 10th percentile of the bootstrap pressure rating, 300 resamples); ties broken by `delivery_rate` (descending) then pressure balls (descending). Take the first 10.
- **Consequence worth knowing:** a list ranked by floor is not a list ranked by rating or by P(top 10). Sai Sudharsan (rating 0.142) is listed 8th, above Nicholas Pooran (rating 0.159), because Sudharsan's floor is higher (0.102 vs 0.099). Several unlisted players have a higher P(top 10) than the 10th listed batter (see `07_LIMITATIONS_OBSERVED.md`).

### Players removed by the 'reliably negative shift' step

Source: `outputs/step3_removed_batters.csv`, `step3_removed_bowlers.csv` (also in `outputs/step3_reports.md` (b)). Reason for every row: bootstrap `shift_p90 < 0`. Best `floor_rank_if_kept` among the removed: batters 17, bowlers 36 (so none would have reached the top 10).

**batters: 6 removed** (of 53 eligible and active)

| name             |   player_id |   baseline_rank |   floor_rank_if_kept |   baseline |   shift |   shift_p90 |   pressure_rating |   floor_p10 |
|:-----------------|------------:|----------------:|---------------------:|-----------:|--------:|------------:|------------------:|------------:|
| Shivam Dube      |        4755 |              17 |                   17 |     0.1090 | -0.0075 |     -0.0007 |            0.1014 |      0.0568 |
| Marcus Stoinis   |        2639 |              31 |                   33 |     0.0748 | -0.0103 |     -0.0017 |            0.0645 |      0.0037 |
| Babar Azam       |        2485 |              37 |                   35 |     0.0540 | -0.0085 |     -0.0007 |            0.0455 |     -0.0060 |
| Tanzid Hasan     |        7900 |              42 |                   48 |     0.0341 | -0.0119 |     -0.0054 |            0.0222 |     -0.0514 |
| Ayush Badoni     |        6460 |              46 |                   46 |     0.0206 | -0.0099 |     -0.0030 |            0.0107 |     -0.0462 |
| Charith Asalanka |        4895 |              50 |                   52 |     0.0070 | -0.0126 |     -0.0046 |           -0.0056 |     -0.0793 |

**bowlers: 7 removed** (of 55 eligible and active)

| name               |   player_id |   baseline_rank |   floor_rank_if_kept |   baseline |   shift |   shift_p90 |   pressure_rating |   floor_p10 |
|:-------------------|------------:|----------------:|---------------------:|-----------:|--------:|------------:|------------------:|------------:|
| Rahul Chahar       |        6161 |              30 |                   38 |     0.0457 | -0.0078 |     -0.0001 |            0.0378 |     -0.0360 |
| Mohammed Siraj     |        5944 |              38 |                   36 |     0.0216 | -0.0111 |     -0.0003 |            0.0105 |     -0.0319 |
| Andre Russell      |        1318 |              41 |                   46 |     0.0004 | -0.0110 |     -0.0013 |           -0.0106 |     -0.0735 |
| Tushar Deshpande   |        6806 |              45 |                   45 |    -0.0043 | -0.0139 |     -0.0061 |           -0.0183 |     -0.0660 |
| Azmatullah Omarzai |        6676 |              47 |                   48 |    -0.0083 | -0.0148 |     -0.0046 |           -0.0232 |     -0.0742 |
| Hardik Pandya      |        3330 |              48 |                   47 |    -0.0173 | -0.0117 |     -0.0016 |           -0.0290 |     -0.0741 |
| Vaibhav Arora      |        8746 |              49 |                   50 |    -0.0226 | -0.0086 |     -0.0004 |           -0.0312 |     -0.0837 |

Pool sizes: batters eligible 53 -> eligible and active 53 -> ranked pool 47 after removal; bowlers eligible 56 -> active 55 -> ranked pool 48 (`website/data/meta.json`, `outputs/audit_stage5.md`, `audit_stage7.md`).

## Identity check

- Names that map to more than one `player_id` in `competition_team_player_mapping.csv`: **7**: Abdul Samad, Bashir Ahmad, Basil Hameed, Haider Ali, Mohammad Ali, Muhammad Farooq, Rashid Khan. (Computed from the mapping file; the mapping file itself is not in this pack.)
- Of those, only **Rashid Khan** is among the 109 eligible players or the 20 listed. The list uses **player_id 4722** (Gujarat Titans, Afghanistan). The other id is **20172** (Nepal).
- No other listed or eligible name is duplicated (`outputs/audit_stage7.md`: duplicate_names 0 for batters, 1 for bowlers; `id_ok` = 1 for both).
- **Unstop dropdown match: NOT VERIFIED BY ME.** I cannot open Unstop. The dropdown check is the submitter's manual step (CHANGES #34). See `12_UNSTOP_ENTRIES.md` for the exact ids and names to match.

## Copies of the pipeline files

`top10_batters.csv` and `top10_bowlers.csv` in this folder are byte copies of `outputs/top10_*.csv`; their SHA-256 matches `FINAL_LOCK.md` (checked by `check_handoff.py`).

## Automated check result (`check_handoff.py`, run 2026-11-15)

```
PASS  (a) all required files exist | 25 required items present
PASS  (a) 08_FIGURES has PNG and SVG files | 17 png, 11 svg
PASS  (a) PNG width >= 1600 px (informational; originals may be narrower) | all PNG >= 1600 px
PASS  (b) top-10 batters: identical in order and player_id across 6 sources | reference outputs/top10_batters.csv = [4260, 1699, 6396, 6281, 5553, 3647, 7897, 23450, 3125, 6288]
PASS  (b) top-10 bowlers: identical in order and player_id across 6 sources | reference outputs/top10_bowlers.csv = [781, 3644, 4722, 6256, 830, 4900, 2933, 2876, 7967, 4219]
PASS  (b) pack copy of config.yaml has the FINAL_LOCK.md SHA-256 | 27709eea817d...
PASS  (b) pack copy of top10_batters.csv has the FINAL_LOCK.md SHA-256 | c3182235b809...
PASS  (b) pack copy of top10_bowlers.csv has the FINAL_LOCK.md SHA-256 | 31c82073156f...
PASS  (c) every number in 10_NUMBERS_FOR_DECK.json traces to its source file | 82 numbers checked
PASS  (c) every deck number has label, value, unit, source_file, source_location
PASS  (d) no raw organiser file in the pack (by name, by hash, by ball-level header) | forbidden=[] identical-to-organiser=[] ball-level-header=[]
PASS  (d) only plain files (.md .csv .json .png .svg, plus config.yaml and this script) | ok
PASS  (e) total size under 15 MB | 4.00 MB across 52 files

RESULT: 13 of 13 checks passed
```
