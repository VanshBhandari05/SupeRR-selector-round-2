# 08 FIGURE INDEX

All files are in `08_FIGURES/`. Colour grammar: **blue = normal, pink = pressure**. New figures (prefix `F`) are PNG at 1920 px wide plus SVG; text is sized for slides. Originals copied from `figures/` keep their names with the prefix `pipeline_` (PNG only; no SVG exists for them; `stage3_close_games.png` is replaced by F10 because it was under 1600 px).

## Required figures and where to find them

| required | file(s) |
|---|---|
| leverage heatmap (balls left x runs required) | `F01_leverage_heatmap_balls_left_x_runs_required` (new); `pipeline_stage3_where_pressure_lives.png` (original: runs required x over) |
| calibration plot | `F02_calibration_deciles` (new, clean); `pipeline_stage2_calibration.png` (original, multi-panel) |
| separation chart | `pipeline_stage3_separation.png` |
| one match trace | `F03_match_trace_16662` (new); `pipeline_stage3_case_studies.png` (six matches) |
| raw vs shrunk chart | `F04_raw_vs_shrunk` (new) |
| batter and bowler baseline vs pressure scatter with intervals | `F05_baseline_vs_pressure_scatter` (new); `pipeline_stage8_ratings_scatter.png` (original, top row) |
| stability chart | `F06_rank_stability` (new) |
| sensitivity / fragile-flag table | `F07_sensitivity_fragile_table` (new) |
| two top-10 lists, one image each | `F08_top10_batters`, `F08_top10_bowlers` (new) |
| pressure vs ordinary paired-bar chart, league-wide | `F09_pressure_vs_ordinary_paired_bars` (new) |


## New figures

| file (PNG + SVG) | takeaway | numbers shown |
|---|---|---|
| `F01_leverage_heatmap_balls_left_x_runs_required` | Pressure builds as balls and runs run out together: the pink zone is 'few runs, few balls' (and mid-chase when the ask is high). | Mean LI per cell, innings 2, live balls, 68,932 balls in 192 cells (>= 20 balls each); cutoff LI 1.207 (pressure_thresholds.json). |
| `F02_calibration_deciles` | When the model says 70%, the team wins about 70% of the time, on seasons it never saw. | Decile predicted vs observed win rate with 95% match-bootstrap intervals; largest gaps 0.0418 (innings 1), 0.0233 (innings 2) (audit_stage2.md). |
| `F03_match_trace_16662` | In a 1-wicket finish the leverage index stays near the cutoff for most of the chase and then climbs to 11.3 in the last over. | Match 16662 (2022-09-07, Pakistan v Afghanistan, Pakistan won by 1 wicket): peak LI 11.31 on ball 117 (over 20); 74 of 117 chase balls are pressure balls (03_trace_summary.csv). |
| `F04_raw_vs_shrunk` | Raw pressure records are noisy and are pulled in by shrinkage and opposition adjustment. | Raw mean value, simple shrunk rating and final ridge rating for the 20 listed players (06_FAIRNESS_AND_ADJUSTMENT.md). |
| `F05_baseline_vs_pressure_scatter` | A player's pressure rating is almost his baseline: pressure adds or removes very little. | Pressure rating vs baseline for 53 batters and 56 bowlers with 10th-90th percentile bars (player_ratings.csv); listed players in pink. |
| `F06_rank_stability` | The top of each list is secure; places 7 to 10 depend on the resample. | Rank 10th to 90th percentile bars and P(top 10), P(top 20) for the 20 listed players (top10_*.csv). |
| `F07_sensitivity_fragile_table` | Most listed players survive almost every variant; Gill (7 of 14), Axar Patel and Krunal Pandya (10 of 14) are the least secure. | Top-10 membership of each listed player under 14 sensitivity variants (floor proxy; sensitivity_ratings_*.csv, top10_*.csv `variants_in_top10`). |
| `F08_top10_batters` | The ten batters, baseline (blue) and pressure rating (pink) with 80% interval. | top10_batters.csv: rating, baseline, floor_p10, p90 per player. |
| `F08_top10_bowlers` | The ten bowlers, baseline (blue) and pressure rating (pink) with 80% interval. | top10_bowlers.csv: rating, baseline, floor_p10, p90 per player. |
| `F09_pressure_vs_ordinary_paired_bars` | On pressure balls batters score faster (146.6 vs 139.5) but also get out more often (5.86% vs 5.09%), and bowlers concede more (economy 9.13 vs 8.67). | website/data/league_split.json overall, raw rates for live balls of the 728 rated matches; NOT standardised by phase. |
| `F10_close_games_vs_rest` | Pressure concentrates in games that finished tight although margin is never an input. | 137 close matches: median peak LI 10.1 vs 1.6 (671 others); Spearman peak LI vs runs margin -0.853 (n=395) (audit_stage3.md; values re-derived and asserted equal at build time). Full-width re-render of the original stage3_close_games.png (which was 1560 px and is NOT copied). |

## Original pipeline figures (copied)

| file | takeaway | numbers shown |
|---|---|---|
| `pipeline_stage2_calibration.png` (2015 x 1170) | Win probabilities are calibrated out of sample and beat a one-feature baseline. | Max decile gap 0.0418 (inn 1), 0.0233 (inn 2); Brier 0.2193 vs 0.2294 and 0.1270 vs 0.1490 (audit_stage2.md). Several panels (calibration, start-of-chase by target, two chase traces, distribution). |
| `pipeline_stage3_case_studies.png` (1920 x 900) | The leverage index spikes where a cricket watcher expects it, in tight finishes, and stays flat in one-sided chases. | Six matches: tight 13613, 13512, 16662; one-sided 19717, 40040, 15458. NOTE 13512 barely registers (peak LI 1.44) - see 03_EVIDENCE_DEFINITION.md flag. |
| `pipeline_stage3_separation.png` (1820 x 650) | Pressure balls differ from ordinary balls in the same phase: more boundaries, fewer dots, more dismissals late; fewer defensive strokes. | Differences with 95% intervals by phase (audit_stage3.md): e.g. death dismissal +0.0208, powerplay dot -0.0453, middle runs +0.0862. |
| `pipeline_stage3_where_pressure_lives.png` (2210 x 676) | Pressure lives in the chase: innings 1 has 98 pressure balls; 75.4% of pressure balls fall before over 16. | Left: mean LI by runs required and over (chase); centre: by wickets and over (innings 1); right: pressure share by over (audit_stage2c.md). |
| `pipeline_stage8_ratings_scatter.png` (1950 x 1430) | Pressure ratings sit almost on the baseline line, and the regression ranking is almost identical to the simple shrunk one. | Top row: baseline vs pressure rating with 10th-90th percentile bars; bottom row: simple vs regression, Spearman 0.9696 batters, 0.9839 bowlers (audit_stage5.md). |
| `pipeline_stage8_shift_distribution.png` (1820 x 650) | Pressure shifts are tiny and centred on zero. | Histogram of bootstrap-mean shifts; shift SD about 0.0085 (batters), 0.0084 (bowlers) among eligible players (audit_stage4.md). |

Note on width: all new figures are 1920 px wide. The original `stage3_close_games.png` is 1560 px wide (the only one under 1600). I did not re-render originals because that would mean re-running pipeline code; it is usable on a slide at half width or can be rebuilt from `src/stage3_prove.py`.
