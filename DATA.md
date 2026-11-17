# About the dataset (not included)

The ball-by-ball data used by this solution is a **proprietary dataset supplied for the SupeRR Selector Season 2 competition**. It is large and not licensed for redistribution, so it is **not in this repository**. Only a few illustrative rows are shown below.

To reproduce the results, place the six CSVs in the repository root (same file names) and run `python run_all.py`.

| File | Rows | What it holds |
|---|---:|---|
| `ball_by_ball.csv` | 200,999 | One row per delivery: match, innings, over, striker, bowler, runs, wicket, shot and bowling details (~41 MB) |
| `matches.csv` | 883 | One row per match: competition, date, venue, teams, toss, result, revised targets |
| `playing_eleven.csv` | 28,381 | Players who featured in each match, batting order, captain / keeper / impact flags |
| `teams.csv` | 353 | Team ids and names per competition |
| `competitions.csv` | 141 | Competition ids, names, format, season |
| `competition_team_player_mapping.csv` | 6,413 | Player ids and names per team per competition |

`data_external/external_totals.csv` (small, public scorecard totals used only for validation) is included.

## Sample rows: `ball_by_ball.csv` (12 of the columns shown)

|   match_id |   innings |   overid |   over_ball_num | striker_name   | bowler_name      | batting_type   | bowling_type         |   runs | is_four   | is_six   | is_wicket   |
|-----------:|----------:|---------:|----------------:|:---------------|:-----------------|:---------------|:---------------------|-------:|:----------|:---------|:------------|
|      13511 |         1 |        1 |               1 | Jason Roy      | Sheldon Cottrell | RHB            | Left-arm fast-medium |      0 | False     | False    | False       |
|      13511 |         1 |        1 |               2 | Jason Roy      | Sheldon Cottrell | RHB            | Left-arm fast-medium |      0 | False     | False    | False       |
|      13511 |         1 |        1 |               3 | Jason Roy      | Sheldon Cottrell | RHB            | Left-arm fast-medium |      0 | False     | False    | False       |

## Sample rows: `matches.csv` (9 of the columns shown)

|   match_id |   comp_id | match_date   | stage   | home_team   | away_team   | toss_opted   |   win_team_id | result                       |
|-----------:|----------:|:-------------|:--------|:------------|:------------|:-------------|--------------:|:-----------------------------|
|      13511 |      1331 | 2022-01-22   | League  | West Indies | England     | Fielding     |            28 | West Indies Won by 9 Wickets |
|      13512 |      1331 | 2022-01-23   | League  | West Indies | England     | Fielding     |            22 | England Won by 1 Run         |
|      13513 |      1331 | 2022-01-26   | League  | West Indies | England     | Fielding     |            28 | West Indies Won by 20 runs   |
