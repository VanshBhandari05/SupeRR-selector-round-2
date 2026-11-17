# 12 UNSTOP ENTRIES: exactly what to type into the dropdowns

Source: `outputs/top10_*.csv` (ranking), `submission_sheet.csv` (project root, written by `src/finalize.py`) and `competition_team_player_mapping.csv` (display name as the mapping file spells it; the mapping file itself is NOT in this pack). Match by `player_id` and team, not name alone.

**Status of the Unstop typing: NOT CONFIRMED.** I cannot see Unstop, so I cannot say what was typed or what the dropdown shows. Tick the 'typed' column yourself.

## Top 10 batters

|   rank |   player_id | display_name_in_mapping_file   | name_in_pipeline     | team                                  | duplicate_name_warning   | typed_into_unstop   |
|-------:|------------:|:-------------------------------|:---------------------|:--------------------------------------|:-------------------------|:--------------------|
|      1 |        4260 | Heinrich Klaasen               | Heinrich Klaasen     | Sunrisers Hyderabad / South Africa    |                          | (you)               |
|      2 |        1699 | Suryakumar Yadav               | Suryakumar Yadav     | Mumbai Indians / India                |                          | (you)               |
|      3 |        6396 | Tim David                      | Tim David            | Mumbai Indians / Australia            |                          | (you)               |
|      4 |        6281 | Abhishek Sharma                | Abhishek Sharma      | Sunrisers Hyderabad / India           |                          | (you)               |
|      5 |        5553 | Phil Salt                      | Phil Salt            | Royal Challengers Bengaluru / England |                          | (you)               |
|      6 |        3647 | Shreyas Iyer                   | Shreyas Iyer         | Punjab Kings / India                  |                          | (you)               |
|      7 |        7897 | Namboori Tilak Varma           | Namboori Tilak Varma | Mumbai Indians / India                |                          | (you)               |
|      8 |       23450 | Sai Sudharsan                  | Sai Sudharsan        | Gujarat Titans                        |                          | (you)               |
|      9 |        3125 | Nicholas Pooran                | Nicholas Pooran      | Lucknow Super Giants / West Indies    |                          | (you)               |
|     10 |        6288 | Shubman Gill                   | Shubman Gill         | Gujarat Titans / India                |                          | (you)               |

## Top 10 bowlers

|   rank |   player_id | display_name_in_mapping_file   | name_in_pipeline   | team                                    | duplicate_name_warning                                                                                                  | typed_into_unstop   |
|-------:|------------:|:-------------------------------|:-------------------|:----------------------------------------|:------------------------------------------------------------------------------------------------------------------------|:--------------------|
|      1 |         781 | Sunil Narine                   | Sunil Narine       | Kolkata Knight Riders                   |                                                                                                                         | (you)               |
|      2 |        3644 | Kuldeep Yadav                  | Kuldeep Yadav      | Delhi Capitals / India                  |                                                                                                                         | (you)               |
|      3 |        4722 | Rashid Khan                    | Rashid Khan        | Gujarat Titans / Afghanistan            | DUPLICATE NAME: another player_id 20172 (Nepal) has the same name. Pick the Gujarat Titans / Afghanistan one (id 4722). | (you)               |
|      4 |        6256 | Varun Chakravarthy             | Varun Chakravarthy | Kolkata Knight Riders / India           |                                                                                                                         | (you)               |
|      5 |         830 | Josh Hazlewood                 | Josh Hazlewood     | Royal Challengers Bengaluru / Australia |                                                                                                                         | (you)               |
|      6 |        4900 | Wanindu Hasaranga              | Wanindu Hasaranga  | Royal Challengers Bengaluru / Sri Lanka |                                                                                                                         | (you)               |
|      7 |        2933 | Jasprit Bumrah                 | Jasprit Bumrah     | Mumbai Indians / India                  |                                                                                                                         | (you)               |
|      8 |        2876 | Axar Patel                     | Axar Patel         | Delhi Capitals / India                  |                                                                                                                         | (you)               |
|      9 |        7967 | Noor Ahmad                     | Noor Ahmad         | Chennai Super Kings / Afghanistan       |                                                                                                                         | (you)               |
|     10 |        4219 | Krunal Pandya                  | Krunal Pandya      | Lucknow Super Giants                    |                                                                                                                         | (you)               |

Display-name equality: for all 20 players the mapping-file name equals the pipeline name (checked at build time).

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
