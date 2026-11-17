# 11 STORY BEATS: seven findings that make the strongest presentation, from the results only

Each beat: one-sentence finding, the supporting number (with source), the figure or table that shows it, and a one-line honest caveat. Order is a suggested running order.

## 1. How pressure was defined, and why

- **Finding:** Pressure is how far the next ball can swing the match: we measure the expected change in win probability on the next ball, and call the top 20% of live balls 'pressure balls'.
- **Supporting number:** 31,263 pressure balls out of 156,062 live balls in 728 matches (20.0%); cutoff LI 1.207 where an average live ball = 1 (website/data/meta.json; outputs/pressure_thresholds.json).
- **Figure / table:** F01 leverage heatmap; F03 match trace (16662).
- **Honest caveat:** Under the pooled cutoff, pressure is almost entirely a live chase: 78 pressure balls in innings 1, and 75.4% of pressure balls come before over 16.

## 2. The proof it separates real situations

- **Finding:** Balls we call pressure behave differently from ordinary balls in the same phase, and the index spikes in games that finished tight although the margin is never an input.
- **Supporting number:** Death-over dismissal rate +2.1 points (interval +1.0 to +3.1); powerplay dot balls -4.5 points; close matches median peak LI 10.1 vs 1.6; Spearman -0.853 between peak LI and winning margin (audit_stage3.md).
- **Figure / table:** pipeline_stage3_separation.png; pipeline_stage3_close_games.png; 03_EVIDENCE_DEFINITION.md tables.
- **Honest caveat:** Agreement with the published pressure index is only moderate (Spearman 0.328), and one of the three auto-picked 'tight' trace matches (13512) barely registers; use 16662 or 13613.

## 3. Batters: the main surprise

- **Finding:** The batters' list is ranked by a conservative floor, so the last places are a coin-toss: Shubman Gill takes 10th by 0.0004 of floor over Jos Buttler, and Sai Sudharsan and Gill finish in the top 10 in only 28% and 25% of resamples.
- **Supporting number:** Gill floor 0.0941 vs Buttler 0.0937; P(top 10): Sudharsan 0.283, Gill 0.247 (top10_batters.csv; eligible_table_batters.csv).
- **Figure / table:** F06 rank stability; F07 sensitivity table.
- **Honest caveat:** Gill is in the top 10 under only 7 of 14 sensitivity variants; Inglis, Buttler and Marsh have a higher P(top 10) than he does but a lower floor.

## 4. Bowlers: the main surprise

- **Finding:** Eight of the ten best pressure bowlers are spinners, and Sunil Narine tops the list.
- **Supporting number:** 8 of 10 listed are spinners vs 20 of 55 in the pool; spinners bowl 35.0% of pressure balls vs 37.2% of live balls (step3_summary.json; step3_reports.md (d)). Narine: rating 0.198, floor 0.153, P(top 10) 0.983 (top10_bowlers.csv).
- **Figure / table:** F08 top-10 bowlers image; 05_PLAYER_CARDS.md.
- **Honest caveat:** Jasprit Bumrah is listed on economy (index 117) but his wicket ratio is 0.59 and his net value is about +5 runs (interval -68 to +86; step2_bowler_net.md); Noor Ahmad's delivery rate is only 0.31.

## 5. The reliability finding (lead with this honestly)

- **Finding:** The ratings measure proven quality in live, high-leverage situations; a separate clutch trait is not reliably measurable in this data.
- **Supporting number:** Split-half: pressure rating 0.536 batters / 0.662 bowlers, but baseline alone 0.531 / 0.662 and pressure shift alone 0.130 / 0.150; season-to-season r 0.048 batters (CI -0.229 to 0.317, n 34) vs 0.511 bowlers (CI 0.252 to 0.720, n 37) (audit_stage6.md).
- **Figure / table:** 04_EVIDENCE_RELIABILITY.md section 1 to 3; pipeline_stage8_shift_distribution.png; F05 scatter.
- **Honest caveat:** Batter ratings did not persist across 2022-24 vs 2025-26 (r = 0.05), so the batters' list is a verdict on the pooled record, not a forecast.

## 6. Robustness: the lists barely move

- **Finding:** Across 14 reasonable alternative ways of doing the analysis, a median 9 of the top 10 stay in for both lists.
- **Supporting number:** Median overlap 9 (batters) and 9 (bowlers); 5 of 10 bowlers and 2 of 10 batters survive all 14 variants; the pressure cutoff alone moves at most one name (sensitivity.csv; audit_stage6b.md).
- **Figure / table:** F07 sensitivity table; 04_EVIDENCE_RELIABILITY.md section 8.
- **Honest caveat:** The lowest overlaps (6 of 10) come from rating on IPL-only or T20I-only data, and the 'no recalibration' variant was not run.

## 7. The single most important limitation

- **Finding:** 'Pressure' here is essentially a live run chase, so the ratings are ratings of performance under chase pressure.
- **Supporting number:** 78 of 31,263 pressure balls are in innings 1 (0.25%); 37.2% of innings-2 balls vs 0.1% of innings-1 balls are pressure balls (audit_stage2c.md; meta.json).
- **Figure / table:** pipeline_stage3_where_pressure_lives.png; F01.
- **Honest caveat:** Defending-side pressure in the first innings is almost invisible by construction; a within-innings cutoff (a tested variant) keeps 9 of 10 on both lists.

## 8. (Optional) What we changed after seeing results, stated upfront

- **Finding:** We amended one rule after seeing results, and we show both versions.
- **Supporting number:** Original bowler sign check (economy index > 100 only) fails Wanindu Hasaranga (94.8) and Noor Ahmad (91.5); amended to 'economy index > 100 OR wicket ratio > 1'; strict list swaps in Mujeeb Ur Rahman and Bhuvneshwar Kumar (strict_rule_bowlers.csv).
- **Figure / table:** 00_DEVIATIONS.md Part A; report appendix A.
- **Honest caveat:** It is post hoc by definition; the ranking itself was not changed.
