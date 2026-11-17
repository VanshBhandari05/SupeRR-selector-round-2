# 07 LIMITATIONS OBSERVED IN THE ACTUAL RESULTS

**The blueprint's list of six limitations was not available to me** (blueprint file not in the project). Part A therefore goes through the 13 limitations the project's own `report.md` section 9 states (and `exhibit_map.md` page 9), which include the blueprint-derived ones (exhibit_map 9.5, 9.6, 9.7 cite 'blueprint limitations': fielding, who faces pressure, tournament pressure). For each: does the actual result show it mattering, with a number where one exists.

## Part A. The limitations and whether the results show them

| limitation                                                                   | does it matter in the results?   | number / evidence (file)                                                                                                                                                                                                                    |
|:-----------------------------------------------------------------------------|:---------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Pressure is mostly a live chase                                              | YES, large                       | 78 of 31,263 rated pressure balls (0.25%) are in innings 1; 75.4% of pressure balls fall before over 16; 37.2% of innings-2 balls are pressure vs 0.1% of innings-1 balls (audit_stage2c.md, meta.json).                                    |
| Venue is not in the rating regression's context                              | NOT TESTED                       | Venue enters only through the scoring model (`env_tier`). No sensitivity variant adds a venue term. No number.                                                                                                                              |
| Skipped sensitivity variant; floor proxy in the grid                         | YES, once                        | Proxy top 10 differs from the final list by one player: Jos Buttler 9th on proxy, 11th on true floor; Gill 11th on proxy, 10th on true floor (CHANGES #39). 'No recalibration' variant NOT RUN.                                             |
| Bowler sign check was amended after seeing results                           | YES                              | 2 of 10 listed bowlers (Hasaranga economy index 94.8, Noor Ahmad 91.5) fail the original economy-only check; strict list differs by 2 names (Mujeeb Ur Rahman, Bhuvneshwar Kumar for Hasaranga, Noor Ahmad).                                |
| No separable clutch trait                                                    | YES, central result              | Pressure-shift split-half 0.1303 batters / 0.1495 bowlers; batter season-to-season r 0.0477 (CI -0.2294 to 0.3174); permutation p 0.062 batters, 0.048 bowlers.                                                                             |
| Team scores are rebuilt from partly missing extras                           | YES, small                       | External check: mean error -1.00 runs, 29 of 30 totals within 5, worst single error -8 (match 45505); chase totals about 2 low; margin error median 0, p95 4.0, max 8.0 (audit_stage1.md). 59 bye rows imputed 1 run.                       |
| Win probability is team-neutral                                              | YES for non-rated groups         | Start-of-chase over-prediction: associates +8.7 pts (52 matches), A-teams +5.4 pts (30), full-member T20I +2.3 (392), IPL -0.1 (366) (audit_stage2.md). Associate/A-team matches do not rate players, but they fit the scoring model.       |
| Calibration tolerance is as wide as its sampling noise                       | YES                              | Max decile gap 0.0418 (innings 1) and 0.0233 (innings 2) vs limit 0.05; 95% bootstrap intervals on the gaps are about +/-0.05. Innings-1 bins above 0.8 over-predict by 6.5 to 8.8 points.                                                  |
| Fielding, partnerships, role are invisible; who faces pressure is not random | PLAUSIBLY, not measurable here   | Spinners are 8 of 10 listed bowlers vs 20 of 55 in the pool, while spinners bowl 35.0% of pressure balls vs 37.2% of live balls (step3_reports.md (d)); that gap is a selection effect that role/captaincy could explain. No fielding data. |
| Tournament pressure untested                                                 | YES                              | No World Cup in the data; knockout matches: 30 of the 808 clean matches (31 in the whole matches file, the figure exhibit_map.md cites).                                                                                                    |
| Small pools                                                                  | YES                              | 53 batters / 56 bowlers eligible; 47 / 48 after the active and negative-shift steps. Listed players are the top 10 of 47 and 48.                                                                                                            |
| Heavy tails in ball values                                                   | Small                            | Batter ball values reach -14.9; capping at the 1st/99th percentile leaves both lists unchanged (overlap 10 of 10, Kendall 0.978 batters / 0.957 bowlers).                                                                                   |
| Data quality: one chase fails the wickets reconciliation                     | YES, one match                   | Match 20190: result text 'won by 6 wickets', ball data 5 wickets (4 implied); named exception, ball data used.                                                                                                                              |

## Part B. Extra limitations noticed during the build

1. **The list is ranked by floor, not by P(top 10).** Unlisted players with a HIGHER P(top 10) than the 10th listed player:

| role   | name           |   pool_rank |   p_top10 |   floor_p10 |   rating |   lowest_listed_p_top10 |
|:-------|:---------------|------------:|----------:|------------:|---------:|------------------------:|
| batter | Jos Buttler    |          11 |     0.270 |       0.094 |    0.142 |                   0.247 |
| batter | Mitchell Marsh |          14 |     0.257 |       0.067 |    0.137 |                   0.247 |
| batter | Josh Inglis    |          20 |     0.323 |       0.046 |    0.134 |                   0.247 |

   Batters: Josh Inglis, Jos Buttler and Mitchell Marsh have a higher P(top 10) than Shubman Gill (0.247), and Josh Inglis (0.323) is also higher than Sai Sudharsan (0.283). This is the cost of ranking on the floor; it is the rule as run. Bowlers: none exceeds the lowest listed P(top 10) (Axar Patel 0.39).

2. **IPL-only listed players.** Sai Sudharsan, Sunil Narine and Krunal Pandya have 0 T20I pressure balls, so they are rated on one competition. Klaasen has 40 and Iyer 43 T20I pressure balls. Rating IPL-only keeps 6 of 10 batters and 8 of 10 bowlers; T20I-only keeps 6 and 7.

3. **Batters do not persist across seasons** (r = 0.048, n = 34): the list is a verdict on 2022-2026 pooled, and weighting recent seasons (2-year half-life) removes Nicholas Pooran and Shubman Gill and brings in Ishan Kishan and Virat Kohli (overlap 8 of 10).

4. **Era effects**: the impact-player rule (IPL from 2023) is in the scoring model only. No explicit era term in the rating regression.

5. **Pressure share is 20% by construction** (top 20% of live balls). Sizes and shares of 'pressure' therefore describe the chosen cutoff, not a natural quantity.

6. **The audit for the choice of C is empty.** `audit_stage2.md` has a 'Choice of C' table with no rows because C was fixed (`stage2_choices.json` `logloss` is `{}`); the evidence for the choice exists only as prose in CHANGES #5.

7. **Evidence cards print '(stable)' for every listed player**, including Gill (7 of 14 variants). The fragile rule is 'fewer than half', so 7 of 14 is not fragile, but the card label hides that he is the weakest.

## Part C. Listed players with a small pressure sample

Eligibility is 120 pressure balls over 15 matches; every listed player clears it. The smallest samples, relative to the rest of the lists, are (sorted by pressure balls):

| role   |   rank | name             |   pressure_balls |   matches |   ipl |   t20i |   delivery_matches |
|:-------|-------:|:-----------------|-----------------:|----------:|------:|-------:|-------------------:|
| batter |      1 | Heinrich Klaasen |              200 |        19 |   160 |     40 |                  9 |
| bowler |      9 | Noor Ahmad       |              207 |        16 |   139 |     68 |                 13 |
| batter |      5 | Phil Salt        |              231 |        19 |    74 |    157 |                 15 |
| bowler |     10 | Krunal Pandya    |              247 |        18 |   247 |      0 |                 17 |
| batter |      3 | Tim David        |              270 |        29 |   147 |    123 |                 19 |
| batter |      6 | Shreyas Iyer     |              298 |        20 |   255 |     43 |                 16 |
| bowler |      2 | Kuldeep Yadav    |              299 |        20 |   233 |     66 |                 19 |
| bowler |      1 | Sunil Narine     |              300 |        23 |   300 |      0 |                 22 |

None is below the threshold; Heinrich Klaasen (200 balls, 19 matches) is the smallest sample in the batters' list and sits at rank 1 with P(top 10) 0.99 because his baseline is very high; Noor Ahmad (207 balls, 16 matches; delivery rate 0.31 on 13 qualifying matches) is the smallest bowler sample and has the widest interval (floor 0.074 to p90 0.204).

## Part D. Results that flip when the cutoff moves

From the sensitivity grid (floor-proxy top 10 under each pressure-cutoff variant; the final list is the true-floor list, so a one-player difference exists even at the main cutoff):

| role   | variant                | listed_players_out   | players_in       |
|:-------|:-----------------------|:---------------------|:-----------------|
| batter | cutoff_top10%          | none                 | none             |
| batter | cutoff_top15%          | Nicholas Pooran      | Jos Buttler      |
| batter | cutoff_top25%          | none                 | none             |
| batter | cutoff_top30%          | none                 | none             |
| batter | cutoff_within_innings  | Sai Sudharsan        | Jos Buttler      |
| batter | no_cutoff_log_leverage | none                 | none             |
| bowler | cutoff_top10%          | Krunal Pandya        | Mujeeb Ur Rahman |
| bowler | cutoff_top15%          | none                 | none             |
| bowler | cutoff_top25%          | none                 | none             |
| bowler | cutoff_top30%          | none                 | none             |
| bowler | cutoff_within_innings  | Axar Patel           | Mujeeb Ur Rahman |
| bowler | no_cutoff_log_leverage | Noor Ahmad           | Mujeeb Ur Rahman |

So the pressure cutoff moves at most one name at a time. The variants that move the lists most are IPL-only / T20I-only and the recency weighting, not the cutoff.

## Part E. Numbers that did not reconcile exactly

| item                            | what does not reconcile                                                                                                                             | file                                                  | status                                                         |
|:--------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|:---------------------------------------------------------------|
| Final list vs sensitivity proxy | Proxy 'main' top 10 puts Buttler 9th and Gill 11th; the final true-floor list has Gill 10th, Buttler 11th                                           | CHANGES #39; website robustness.json `proxy_note`     | disclosed, by design                                           |
| Match 13512 trace               | Stated 1-run margin vs rebuilt state: rebuilt R1 171, R2 172, anchor target 174, needing 8 off the last ball and scoring 6 (2 short, margin says 1) | outputs/matches_clean_totals.csv; balls_state.parquet | within the margin gate (max 8) but visible in a showcase trace |
| Margin gate                     | Rebuilt vs stated margin: median 0.0, p95 4.0, max 8.0 (n=395); gate allows p95 <= 6, outlier > 8                                                   | audit_stage1.md                                       | passes                                                         |
| Match 20190                     | Wickets reconciliation 5 vs 4                                                                                                                       | audit_stage1.md                                       | named exception                                                |
| Chase totals                    | External check: chase totals run about 2 low; one -8 (match 45505)                                                                                  | audit_stage1.md                                       | inside the gate                                                |
| Audit gap                       | 'Choice of C' table is empty                                                                                                                        | audit_stage2.md                                       | documentation gap                                              |
| Raw vs recalibrated Brier       | Raw WP has slightly better Brier (0.2190 / 0.1264) than WP* (0.2193 / 0.1270) but fails the decile gate (0.0994 / 0.0601)                           | audit_stage2.md                                       | known trade-off                                                |
| Results text vs ball data       | 3 matches where result/winner are inconsistent (24822, 28334, 48610)                                                                                | audit_stage1.md Notes                                 | noted; ball data used                                          |

Nothing here was changed or fixed. **The only item I think needs your decision** is the choice of the tight-finish example for slides (use 16662 or 13613, not 13512).


**New diagnostic (computed here from `balls_state.parquet` and `matches_clean_totals.csv`):** in the 395 clean chases that were lost by runs, the anchored target differs from the forward target (rebuilt first-innings total + 1) by 0 in 247 matches, by 1 to 2 runs in 59, by 3 to 5 in 78 and by more than 5 in 11 (max 8). This is the same quantity the margin gate measures.
