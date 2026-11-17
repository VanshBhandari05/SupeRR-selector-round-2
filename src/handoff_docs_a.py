"""Handoff pack, documents 00 to 04 (deviations, rankings, method as run, evidence for the definition, evidence for reliability)."""
import datetime
import json
import re

import numpy as np
import pandas as pd

import handoff_data as H
from handoff_data import CFG, OUT, PACK, ROOT, WEB, md, rd, sec, table_from, ordinal

TODAY = datetime.date.today().isoformat()
A1, A2, A2C, A3, A4, A5, A6, A6B, A7 = (rd(OUT / f"audit_stage{s}.md") for s in ("1", "2", "2c", "3", "4", "5", "6", "6b", "7"))
CHANGES = rd(ROOT / "CHANGES_FOR_REVIEW.md")
REPORT = rd(ROOT / "report.md")


def W(name, text):
    (PACK / name).write_text(text.rstrip() + "\n", encoding="utf-8")


def pct(x, d=1):
    return f"{100 * x:.{d}f}%"


# =====================================================================================================  00
def doc_00():
    ch_rows = [l for l in CHANGES.splitlines() if re.match(r"\| \d+[a]? \|", l)]
    s = []
    s.append("# 00 DEVIATIONS: where the final pipeline differs from the blueprint, every gate, every decision\n")
    s.append(f"Built {TODAY} from files in the project folder. Nothing here changes a result.\n")
    s.append("## READ THIS FIRST: the blueprint file was not available to me\n")
    s.append("`SupeRR_Selector_Round_1_Solution_Blueprint.md` is **not in the project folder** (searched the whole folder tree for `*blueprint*`; no match). "
             "So I could not diff the pipeline against the blueprint myself. What I did instead:\n")
    s.append("- Treated **`CHANGES_FOR_REVIEW.md`** as the authoritative deviation log. It was written during the build and states, row by row, 'every place where the pipeline departs from the blueprint, or where I made a choice the blueprint left open'. It is copied in full in Part D below.\n"
             "- Took every threshold from `config.yaml` and from the gate tables in `outputs/audit_stage*.md`, where blueprint rules are quoted as 'pre-declared' or 'fixed in the blueprint'.\n"
             "- Wherever I cannot tell from project files what the blueprint originally said, I write **`NOT AVAILABLE (blueprint not provided)`** instead of guessing.\n"
             "- **Action for you:** if you upload the blueprint to the chat tool as well, ask it to check Part A and Part C against the blueprint's own 'Decisions that are yours' table and Stage 0 to 7 gates. Part C could not be mapped to the blueprint's row numbers.\n")

    s.append("## Part A. Departures from the blueprint (curated from CHANGES_FOR_REVIEW.md and the audits)\n")
    A = [
        ("0/1", "Truncation rule drops a 7th match (50407). Expected counts changed to 7 truncated matches and 728 rating-sample matches (375 T20I).", "Chase ends at 117 legal balls, 9 down, all 11 batters used, last ball a wide: a data gap like 14130 and 14164.", "CHANGES #1; config.yaml `gates.expected_truncated_matches`, `expected_rating_sample`; audit_stage1.md. Blueprint's original expected counts: NOT AVAILABLE (blueprint not provided)."),
        ("0/1", "Wickets gate passes only with a named exception: match 20190 (result text 'won by 6 wickets', ball data show 5).", "Result string disagrees with the ball data and with public scorecards.", "config.yaml `wickets_gate_named_exceptions: [20190]`; audit_stage1.md 'Wickets gate failures' (403 of 404 chases reconcile)."),
        ("0/1", "'Overshoot' diagnostic (5 runs) demoted: diagnostic only, not a gate (withdrawn).", "It was a bad rule; margins cancel same-sign overcounts.", "config.yaml `gates.overshoot_diag_runs` comment; audit_stage1.md 'Does imputing 4 inflate totals?'."),
        ("1", "59 bye/leg-bye rows whose strike rotation is unknowable are imputed 1 run, not 4.", "Blueprint decision for final-ball and wicket-ball byes.", "CHANGES #2; config `bye_unknown_rotation_runs: 1`."),
        ("1", "`env_tier` (venue scoring tercile) is cut within each competition group.", "Blueprint accepted, conditional on Stage 2 showing it helps.", "CHANGES #3."),
        ("2", "`env_tier` KEPT in the scoring model although held-out Brier is slightly better without it.", "Without it the innings-1 decile gate fails at every C tried (max gap 0.0533 to 0.0626 vs the 0.05 limit). A gate failure is a stop, so it was kept.", "CHANGES #4; config `use_env_tier: true`."),
        ("2", "Regularisation C fixed at 0.1 for both innings (rule declared before looking: lowest leave-one-season-out log loss among candidates that pass all four gates).", "C = 0.03 failed the cell gate (worst gap 0.0144 vs 0.01).", "CHANGES #5; config `C_fixed: 0.1`; outputs/stage2_choices.json."),
        ("2", "Chase win-probability surface projected to be monotone (used only because held-out Brier did not worsen: loss 0.00000 vs 0.0005 allowed).", "Raw surface rose up to 0.077 as wickets fell in sparse cells.", "CHANGES #6, #12; audit_stage2.md."),
        ("2", "All out with scores level counts as a tie (0.5).", "The literal ordering would give 0, contradicting the tie definition.", "CHANGES #7."),
        ("2", "Wickets on wides/no-balls folded into the wicket class; 5 runs on a legal ball folded into the 4 class; illegal 3+ valued at 5. Tie matches excluded from calibration. Innings-1 Brier baseline = one-feature logistic on runs above par. Calibration pooled over all four competition groups.", "Keeps 10 outcome classes; blueprint defines the baseline only for chases; larger sample.", "CHANGES #8 to #11."),
        ("3", "Pressure benchmark = published Bhattacharjee-Lemmer index with the 'resources used' term DERIVED from our own scoring model.", "Duckworth-Lewis table is not in the data. This is my assumption, not the paper's.", "CHANGES #14; audit_stage3.md."),
        ("3", "Stroke / delivery groupings (attacking, defensive, yorker, slower) were chosen by me.", "Blueprint names categories loosely.", "CHANGES #15; config `stage3`."),
        ("3", "FINDING: with the pooled 80th-percentile cutoff, innings 1 has 98 pressure balls (0.1%) (78 in the rated matches). Pressure is essentially a live chase. Pooled cutoff kept; within-innings cutoff is a sensitivity variant.", "Blueprint default kept; decision FINAL.", "CHANGES #17; audit_stage3.md; audit_stage2c.md."),
        ("4", "Credit-split implementation choices beyond the blueprint table (no-ball batter credit, non-striker dismissals as their own row, retire-outs valued as if no wicket, byes as dot balls, penalty rows excluded).", "Blueprint table leaves these numerically open.", "CHANGES #19."),
        ("4", "CV penalty grid widened (first grid hit the edge at lambda_B 300): final grid lambda_B 30 to 10000, lambda_C 300 to 100000; optimum unchanged and now interior (300 / 3000).", "Edge hit.", "CHANGES #21; audit_stage4.md. The CV surface is very flat in lambda_C (3.0437 to 3.0500)."),
        ("4", "Shift penalty is 10 times the baseline penalty (blueprint expected 'much larger').", "Chosen by cross-validation, not set by hand.", "audit_stage4.md ('Shift penalty / baseline penalty = 10.0x')."),
        ("4/5", "Ratings use LIVE balls of the rating sample only; one (lambda_B, lambda_C) pair for both fits.", "Blueprint: dead balls removed from the baseline.", "CHANGES #20, #21."),
        ("5", "Active-player filter = any appearance (striker, non-striker or bowler) in a clean match in 2025 or 2026, applied at player level (either role).", "Blueprint: 'at least one match in 2025 or 2026'.", "CHANGES #25."),
        ("5", "P(top 10), P(top 20) and rank intervals computed among eligible AND active players (53 batters, 55 bowlers), not among all eligible.", "", "CHANGES #26; stage5_bootstrap.py."),
        ("5", "No fallback eligibility was used (120 pressure balls, 15 matches met by 53 batters and 56 bowlers; fallback would have triggered below 40).", "", "audit_stage4.md ('Fallback used: batters False, bowlers False')."),
        ("6", "Sensitivity grid runs 14 variants (13 plus the later winsorised variant). NOT RUN: win probability without recalibration (would need Stage 2c rerun). Variants are ranked on a floor PROXY (rating minus 1.2816 x main bootstrap SD), not a per-variant bootstrap.", "Disclosed limitation; decision FINAL.", "CHANGES #28, #38, #39; audit_stage6b.md."),
        ("6", "Split-half and season-to-season use halved eligibility (60 pressure balls, 7 matches); season split = fit on 2022-2024, score 2025-2026.", "Blueprint.", "CHANGES #29; config `stage6`."),
        ("7", "POST-HOC amendment: bowler sign check is 'economy index above 100 OR wicket ratio above 1' (mirrors the batter check). The original economy-only rule fails for Wanindu Hasaranga (index 94.8) and Noor Ahmad (91.5).", "Decided after seeing the results, so it is disclosed as post hoc. The strict-rule list (Mujeeb Ur Rahman and Bhuvneshwar Kumar in, those two out) is kept as an appendix.", "CHANGES #33, #33a; outputs/top10_bowlers.csv (`sign_check`, `sign_check_strict`); outputs/strict_rule_bowlers.csv."),
        ("7", "Ranking uses the TRUE bootstrap floor. The sensitivity grid's proxy would have put Jos Buttler 9th and Shubman Gill 11th; the true floor gives Gill 10th, Buttler 11th.", "", "CHANGES #39; outputs/step3_reports.md (e)."),
        ("7", "Rashid Khan has two ids (4722 Gujarat Titans / Afghanistan; 20172 Nepal). The list uses 4722.", "Identity check; dropdown check is a manual submitter action.", "CHANGES #34; submission_sheet.csv; FINAL_LOCK.md."),
    ]
    s.append(md(pd.DataFrame(A, columns=["stage", "what ran instead of / beyond the blueprint", "reason", "file that shows it"]), ".3f"))
    s.append("\nAlso true but NOT a departure: the lists were locked (SHA-256 in FINAL_LOCK.md) and a full `run_all.py` rerun from an empty `outputs/` folder reproduced both top-10 files byte for byte (CHANGES #35, #42).\n")

    s.append("## Part B. Gate ledger, Stages 0 to 7\n")
    s.append("Measured values are read from the audit files named in the last column. 'Threshold changed?' answers: was the numeric threshold or expected count ever altered from what config/audit declare as pre-set. Where the original value is unknown to me it says NOT AVAILABLE.\n")
    G = CFG["gates"]
    ledger = [
        ("0/1", "33 columns", "33", "33", "PASS", "no", "audit_stage1.md"),
        ("0/1", "unique key (match, innings, ball)", "0 duplicates", "0", "PASS", "no", "audit_stage1.md"),
        ("0/1", "competition tags by id", "0 non-T20I in T20I groups", "0", "PASS", "no", "audit_stage1.md"),
        ("0/1", "result parser", f"{G['expected_wins_by_wickets']} wickets / {G['expected_wins_by_runs']} runs / {G['expected_no_results']} no result / {G['expected_ties']} tie", "419 / 414 / 40 / 10", "PASS", "no", "audit_stage1.md; config gates"),
        ("0/1", "rain flag", f"{G['expected_rain_matches']} matches", "38", "PASS", "no", "audit_stage1.md"),
        ("0/1", "truncation flag", f"flag {G['expected_truncated_matches']} and must flag {G['must_flag_truncated_match']}", "flagged exactly those 7", "PASS", "YES: 50407 added as 7th (CHANGES #1); original list NOT AVAILABLE", "audit_stage1.md"),
        ("0/1", "rating sample", f"IPL {G['expected_rating_sample']['IPL']}, T20I {G['expected_rating_sample']['T20I']}, ties {G['expected_rating_sample']['ties']}", "IPL 353, T20I 375, ties 7 (728 total)", "PASS", "YES with #1 (original NOT AVAILABLE)", "audit_stage1.md"),
        ("0/1", "strike rule agreement", f">= {G['strike_rule_min_agreement']}", "0.99977 on 170,306 normal balls", "PASS", "no", "audit_stage1.md"),
        ("0/1", "legal balls per innings <= 120", "<= 120", "max 120", "PASS", "no", "audit_stage1.md"),
        ("0/1", "first innings has 120 legal balls unless all out", "0 exceptions", "0 of 686", "PASS", "no", "audit_stage1.md"),
        ("0/1", "wickets gate (chase wickets lost reconcile with result text)", "all reconcile", "403 of 404; failure 20190", "PASS only via NAMED EXCEPTION (20190)", "exception added (config)", "audit_stage1.md"),
        ("0/1", "margin gate", f"median |err| <= {G['margin_median_abs_max']}, p95 <= {G['margin_p95_abs_max']}", "median 0.0, p95 4.0 (n=395, max 8.0)", "PASS", "no", "audit_stage1.md"),
        ("0/1", "margin outliers", f"none above {G['margin_outlier_runs']} runs", "none", "PASS", "no", "audit_stage1.md"),
        ("0/1", "external totals check (15 matches, seed 42)", f"mean error {CFG['external_check']['mean_error_min']} to {CFG['external_check']['mean_error_max']}; >= {CFG['external_check']['min_within']} of 30 within {CFG['external_check']['within_runs']} runs", "mean error -1.00; 29 of 30 within 5", "PASS", "no (set before any result)", "audit_stage1.md; data_external/external_totals.csv"),
        ("2", "WP* Brier beats one-feature baseline, both innings", "WP* < baseline", "inn1 0.2193 vs 0.2294; inn2 0.1270 vs 0.1490", "PASS", "no", "audit_stage2.md"),
        ("2", "decile gap innings 1 (leave-one-season-out)", f"<= {CFG['calibration']['decile_tolerance']}", "0.0418", "PASS (tight; 95% interval on gaps is about +/-0.05)", "no", "audit_stage2.md"),
        ("2", "decile gap innings 2", f"<= {CFG['calibration']['decile_tolerance']}", "0.0233", "PASS", "no", "audit_stage2.md"),
        ("2", "scoring model reproduces outcome frequencies (cells >= 500 balls)", f"<= {CFG['calibration']['cell_tolerance']}", "inn1 worst 0.0066 (46 cells); inn2 worst 0.0042 (42 cells)", "PASS", "no", "audit_stage2.md"),
        ("3", "pressure separates dismissal or boundary rate in >= 2 of 3 phases", ">= 2 of 3", "3 of 3 (powerplay, middle, death)", "PASS", "no", "audit_stage3.md"),
        ("3", "close-match count (informational)", "blueprint expected about 130", "137 of 808 clean matches", "informational", "no", "audit_stage3.md"),
        ("4", "batter baseline vs strike rate rank correlation", f">= {CFG['rating']['gate_batter_rho_min']}", "0.708 (n=53)", "PASS", "no", "audit_stage4.md"),
        ("4", "bowler baseline vs economy rank correlation", f"<= {CFG['rating']['gate_bowler_rho_max']}", "-0.795 (n=56)", "PASS", "no", "audit_stage4.md"),
        ("5", "cross-check: simple shrunk version vs regression", ">= 0.8 Spearman", "batters 0.9696; bowlers 0.9839", "PASS", "no", "audit_stage5.md"),
        ("6", "decision rule on split-half pressure rating", "rank on it if >= 0.40", "batters 0.5358; bowlers 0.6617", "PASS (rank on it)", "no", "audit_stage6.md / reliability.md"),
        ("6", "pressure SHIFT split-half (not a pass/fail gate in the files)", "report whatever it is; blueprint line 'below 0.25': see note", "batters 0.1303; bowlers 0.1495", "BELOW 0.25 (flagged, reported prominently)", "no", "audit_stage6.md"),
        ("6", "sensitivity grid median top-10 overlap", ">= 7 of 10", "batters 9; bowlers 9", "PASS", "no", "audit_stage6b.md"),
        ("7", "every listed player has P(top 20) >= 0.6", ">= 0.6", "0 of 20 below (lowest: Shubman Gill 0.76)", "PASS", "no", "audit_stage7.md"),
        ("7", "sign check (amended)", "batters: runs index > 100 OR dismissal ratio < 1; bowlers (amended): economy index > 100 OR wicket ratio > 1", "0 of 20 fail", "PASS after post-hoc amendment", "YES, post hoc (CHANGES #33a)", "audit_stage7.md; top10_*.csv"),
        ("7", "sign check (ORIGINAL strict bowler rule: economy index > 100 only)", "economy index > 100", "2 of 10 bowlers fail (Hasaranga 94.8, Noor Ahmad 91.5)", "FAIL under the original rule", "rule amended, list unchanged", "audit_stage7.md (strict_sign_check_fails = 2); step2_bowler_net.md"),
        ("7", "no listed player fragile (in the top 10 under fewer than half of the 14 variants)", "0", "0 of 20 fragile (lowest: Gill 7 of 14, exactly half, so not 'fewer than half')", "PASS", "no", "audit_stage7.md; top10_batters.csv"),
        ("7", "identity: every listed id resolves to one name; duplicate names flagged", "all resolve", "id_ok = 1 both roles; 1 duplicate name (Rashid Khan)", "PASS (manual Unstop dropdown check still yours)", "no", "audit_stage7.md"),
    ]
    s.append(md(pd.DataFrame(ledger, columns=["stage", "gate", "threshold", "measured", "result", "threshold changed?", "source"])))
    s.append("\n**Blueprint rule for the shift reliability:** the files only quote the 0.40 rule for the rating ('rank on it', 'widen to top 30%', 'below 0.25 plan' are the three outcomes you named). The pipeline ran the 'rank on it' branch. Whether the blueprint's 'below 0.25' plan applies to the shift alone or to the rating, I cannot tell without the blueprint. The rating's split-half is 0.5358 and 0.6617, so by the rating-based rule, 'rank on it' applies. `NOT AVAILABLE (blueprint not provided)`.\n")
    s.append("### Earlier gate failures that were resolved during the build (from CHANGES_FOR_REVIEW.md)\n")
    s.append("1. Stage 0/1: truncation list (expected 6) missed match 50407; fixed by changing the expected list (CHANGES #1). Original blueprint value NOT AVAILABLE.\n"
             "2. Stage 2: innings-1 decile gate FAILED without `env_tier` (max gap 0.0533 to 0.0626 vs 0.05); `env_tier` kept so the gate passes (CHANGES #4).\n"
             "3. Stage 2: scoring-model cell gate FAILED at C = 0.03 (0.0144 vs 0.01); C = 0.1 passes (0.0066) (CHANGES #5).\n"
             "4. Stage 4: first CV grid hit the edge; grid widened (CHANGES #21).\n"
             "5. Stage 7: bowler sign check failed for 2 listed bowlers; rule amended post hoc (CHANGES #33a).\n"
             "The final run has no failing gate except the original strict bowler sign rule shown above.\n")

    s.append("## Part C. 'Decisions that are yours': which option was actually used\n")
    s.append("I could not read the blueprint's 'Decisions that are yours' table, so these are the decisions the project files show were made (by you, per CHANGES_FOR_REVIEW.md 'approved as implemented' and the project memory). Map them to the blueprint's rows yourself.\n")
    D = [
        ("Pressure cutoff: pooled across both innings vs within each innings", "POOLED (top 20% of live balls, LI >= 1.2073). Within-innings is a sensitivity variant only.", "CHANGES #17; pressure_thresholds.json"),
        ("Cutoff percentile", "80th percentile of live balls (top 20%); alternatives 10/15/25/30% run as variants", "config `pressure_quantile: 0.80`; `sensitivity.cutoffs`"),
        ("Venue/era feature (`env_tier`) in the scoring model", "KEPT", "CHANGES #4"),
        ("Regularisation strength C", "Fixed at 0.1 for both innings", "CHANGES #5"),
        ("Monotone projection of the chase surface", "USED", "CHANGES #6, #12"),
        ("Eligibility", "120 pressure balls and 15 matches; no fallback needed", "config `rating.eligibility`; audit_stage4.md"),
        ("Active-player rule", "Any appearance in 2025 or 2026 (either role)", "CHANGES #25"),
        ("Ranking statistic", "Bootstrap floor (10th percentile of pressure rating), after removing reliably negative shifts (90th percentile of shift < 0); ties by delivery rate then pressure balls", "config `rating`; stage7_rank.py"),
        ("Bowler sign check", "Amended post hoc to economy index > 100 OR wicket ratio > 1; strict list kept as appendix", "CHANGES #33a"),
        ("Skipped sensitivity variant (no recalibration)", "SKIPPED, disclosed as a limitation", "CHANGES #28"),
        ("Sensitivity ranking statistic", "Floor proxy (rating minus 1.2816 x bootstrap SD), disclosed as a limitation", "CHANGES #28, #39"),
        ("Rashid Khan identity", "id 4722 (Gujarat Titans / Afghanistan); 20172 is a different player (Nepal)", "CHANGES #34; submission_sheet.csv"),
        ("Benchmark pressure index", "Published index with a model-derived 'resources used' term", "CHANGES #14"),
        ("Rating regression context", "innings x phase x pressure (12 terms) + competition group; no venue term; batting-position band only as a variant", "CHANGES #22; report.md section 9"),
    ]
    s.append(md(pd.DataFrame(D, columns=["decision", "option actually used", "file"])))
    s.append("\n## Part D. The pipeline's own change log, copied in full (CHANGES_FOR_REVIEW.md)\n")
    s.append("| # | Stage | Change / choice | Why | Evidence | Where | Status |\n|---|---|---|---|---|---|---|")
    s.extend(ch_rows)
    s.append("\n## Part E. Verbatim gate tables from the audits\n")
    s.append("### Stage 0/1 gates (audit_stage1.md)\n\n" + sec(A1, "Gates"))
    s.append("\n### Stage 2 gates (audit_stage2.md)\n\n" + sec(A2, "Gates"))
    s.append("\n### Stage 3 gate (audit_stage3.md)\n\n" + sec(A3, "Gate"))
    s.append("\n### Stage 4 gates (audit_stage4.md)\n\n" + sec(A4, "Gates"))
    W("00_DEVIATIONS.md", "\n".join(s))


# =====================================================================================================  01
def rank_table(role):
    t = H.TOP[role].copy()
    rows = []
    for _, r in t.iterrows():
        c = H.CARDS[int(r.player_id)]
        pb = int(H.POOL[role].set_index("player_id").loc[r.player_id, H.PB[role]])
        assert pb == c["pressure_balls"], (r["name"], pb, c["pressure_balls"])
        mp_ = int(H.POOL[role].set_index("player_id").loc[r.player_id, "matches_P"])
        assert mp_ == c["matches_with_pressure_balls"]
        rows.append({"rank": int(r["rank"]), "player_id": int(r.player_id), "name": r["name"], "teams": r.teams, "pressure_rating": r.pressure_rating,
                     "80% interval (p10 to p90)": f"[{r.floor_p10:.3f}, {r.p90:.3f}]", "floor_p10": r.floor_p10, "baseline": r.baseline, "shift": r["shift"],
                     "pressure_balls": pb, "matches_with_pressure_balls": mp_, "IPL / T20I pressure balls": f"{c['ipl_pressure_balls']} / {c['t20i_pressure_balls']}",
                     "p_top10": r.p_top10, "p_top20": r.p_top20, "delivery_rate": r.delivery_rate, "fragile": bool(r.fragile)})
    return pd.DataFrame(rows)


def doc_01():
    s = ["# 01 RANKINGS: the two final top-10 lists, exactly as run\n",
         "Source: `outputs/top10_batters.csv`, `outputs/top10_bowlers.csv` (copied into this pack unchanged), `outputs/eligible_table_*.csv` (pressure balls, matches), `outputs/evidence_cards.md` (IPL vs T20I split). "
         "Pressure balls and matches with pressure balls from the cards equal the eligible tables (asserted at build time). Columns: **80% interval** is the 10th to 90th percentile of the pressure rating over 300 whole-match bootstrap resamples; **floor** is its 10th percentile (the ranking statistic). "
         "`p_top10`/`p_top20` = share of resamples in which the player finishes in the top 10 / 20 of the eligible, active pool (53 batters, 55 bowlers). `delivery_rate` = share of matches with 6+ pressure balls in which the player's total value was positive. `fragile` = in the top 10 under fewer than half of the 14 sensitivity variants.\n"]
    for role in ("batters", "bowlers"):
        s.append(f"## Top 10 {role}\n")
        s.append(md(rank_table(role), ".4f"))
        s.append("")
    s.append("## The ranking rule exactly as run\n")
    s.append("From the stage-7 code docstring (`src/stage7_rank.py`) and `config.yaml`:\n")
    s.append("> Eligible + active players; drop anyone whose pressure shift is reliably negative (90th percentile of the bootstrap shift below zero); sort by the floor (10th percentile of the bootstrap pressure rating); ties by delivery rate, then pressure balls.\n")
    R = CFG["rating"]
    s.append(f"- **Eligible:** at least {R['eligibility']['min_pressure_balls']} pressure balls over at least {R['eligibility']['min_matches']} matches (fixed before any leaderboard was viewed). Fallback ({R['eligibility']['fallback_pressure_balls']} balls / {R['eligibility']['fallback_matches']} matches if fewer than {R['eligibility']['fallback_min_players']} qualify) was NOT used.\n"
             f"- **Active:** any appearance in {R['active_years'][0]} or {R['active_years'][1]} (CHANGES #25).\n"
             f"- **Removal step:** a player is removed if the {int(R['negative_shift_quantile'] * 100)}th percentile of his bootstrap pressure shift is below zero (`shift_p90 < 0`).\n"
             f"- **Sort:** descending `floor_p10` (the {int(R['floor_quantile'] * 100)}th percentile of the bootstrap pressure rating, {R['bootstrap_n']} resamples); ties broken by `delivery_rate` (descending) then pressure balls (descending). Take the first {R['top_n']}.\n"
             "- **Consequence worth knowing:** a list ranked by floor is not a list ranked by rating or by P(top 10). Sai Sudharsan (rating 0.142) is listed 8th, above Nicholas Pooran (rating 0.159), because Sudharsan's floor is higher (0.102 vs 0.099). Several unlisted players have a higher P(top 10) than the 10th listed batter (see `07_LIMITATIONS_OBSERVED.md`).\n")
    s.append("### Players removed by the 'reliably negative shift' step\n")
    s.append("Source: `outputs/step3_removed_batters.csv`, `step3_removed_bowlers.csv` (also in `outputs/step3_reports.md` (b)). Reason for every row: bootstrap `shift_p90 < 0`. Best `floor_rank_if_kept` among the removed: batters %d, bowlers %d (so none would have reached the top 10).\n" % (int(H.REMOVED["batters"].floor_rank_if_kept.min()), int(H.REMOVED["bowlers"].floor_rank_if_kept.min())))
    for role in ("batters", "bowlers"):
        d = H.REMOVED[role]
        t = d[["name", "player_id", "baseline_rank", "floor_rank_if_kept", "B" if role == "batters" else "W", "C" if role == "batters" else "K", "shift_p90", "pressure_rating", "floor_p10"]].rename(columns={"B": "baseline", "W": "baseline", "C": "shift", "K": "shift"})
        s.append(f"**{role}: {len(d)} removed** (of {len(H.UNF[role][H.UNF[role].active])} eligible and active)\n")
        s.append(md(t, ".4f"))
        s.append("")
    s.append(f"Pool sizes: batters eligible {META_('eligible_batters')} -> eligible and active 53 -> ranked pool {META_('ranked_pool_batters')} after removal; bowlers eligible {META_('eligible_bowlers')} -> active 55 -> ranked pool {META_('ranked_pool_bowlers')} (`website/data/meta.json`, `outputs/audit_stage5.md`, `audit_stage7.md`).\n")
    s.append("## Identity check\n")
    dn = H.MAP.groupby("player_name").player_id.nunique()
    dn = sorted(dn[dn > 1].index)
    s.append(f"- Names that map to more than one `player_id` in `competition_team_player_mapping.csv`: **{len(dn)}**: {', '.join(dn)}. (Computed from the mapping file; the mapping file itself is not in this pack.)\n"
             "- Of those, only **Rashid Khan** is among the 109 eligible players or the 20 listed. The list uses **player_id 4722** (Gujarat Titans, Afghanistan). The other id is **20172** (Nepal).\n"
             "- No other listed or eligible name is duplicated (`outputs/audit_stage7.md`: duplicate_names 0 for batters, 1 for bowlers; `id_ok` = 1 for both).\n"
             "- **Unstop dropdown match: NOT VERIFIED BY ME.** I cannot open Unstop. The dropdown check is the submitter's manual step (CHANGES #34). See `12_UNSTOP_ENTRIES.md` for the exact ids and names to match.\n")
    s.append("## Copies of the pipeline files\n\n`top10_batters.csv` and `top10_bowlers.csv` in this folder are byte copies of `outputs/top10_*.csv`; their SHA-256 matches `FINAL_LOCK.md` (checked by `check_handoff.py`).\n")
    W("01_RANKINGS.md", "\n".join(s))


def META_(k):
    return H.META[k]


# =====================================================================================================  02
def doc_02():
    SM, PR, R, S6, S3 = CFG["scoring_model"], CFG["pressure"], CFG["rating"], CFG["stage6"], CFG["stage3"]
    thr = H.THR
    s = ["# 02 METHOD AS RUN: what the final pipeline actually did, stage by stage\n",
         "Parameters come from `config.yaml` (copied into this pack as `config.yaml`; SHA-256 in `FINAL_LOCK.md`) and the audit files named under each heading. This describes what RAN, not what the blueprint planned; departures are in `00_DEVIATIONS.md`.\n"]
    # --- stage 0/1
    s.append("## Stage 0 and 1: ingest, clean, rebuild the match state\n")
    s.append("Source: `outputs/audit_stage1.md`.\n")
    s.append(f"- Raw file: 200,999 rows, 867 matches. Output table: 193,076 rows, 808 matches, of which **728 matches form the rating sample** (IPL 353, T20I full-member 375) and **7 are ties** that are kept. Competition groups are tagged by id, not name (config `competition`): IPL ids {CFG['competition']['ipl_comp_ids']}, A-team ids {CFG['competition']['ateam_comp_ids']}, full-member team ids list in config. Competition tags over the 883 matches listed in `matches.csv` (16 have no ball data): T20I-full 428, IPL 371, T20I-assoc 54, A-team 30. Clean matches by group: T20I-full 375, IPL 353, T20I-assoc 50, A-team 30. **Associate and A-team matches fit the scoring model only; they never rate players.**\n")
    s.append("**Exclusions by rule (applied in this order):**\n")
    s.append(sec(A1, "Rows removed (applied in this order)"))
    s.append(f"\nRules as configured: super overs = innings > 2; no result = regex `{CFG['noresult_regex']}`; rain = regex `{CFG['rain_regex']}` (38 matches flagged; 28 matches are removed at the rain step after the earlier rules); truncation = 7 matches flagged ({CFG['gates']['expected_truncated_matches']}); tie regex `{CFG['tie_regex']}`. Result parser: 419 wins by wickets, 414 by runs, 40 no results, 10 ties.\n")
    s.append("**Rebuilt state (the data omit bye, leg-bye and wide-extra runs, so team runs are rebuilt):**\n")
    s.append(f"- Team runs per ball = bat runs + 1 for a wide or no-ball + `extras_2_runs` + imputed bye/leg-bye runs + wide-run rotation + {CFG['penalty_runs']} for a penalty. A bye/leg-bye that did not rotate strike is imputed **{CFG['bye_nonrotating_runs']}** runs; where rotation is unknowable (final ball of an innings or a wicket ball: **59 rows**) it is imputed **{CFG['bye_unknown_rotation_runs']}**. `extras1_runs` is a type code, never runs (config `extras_codes`).\n"
             "- Strike rotation is inferred from the next ball's striker; it agrees with bat-run parity on 0.99977 of 170,306 normal balls.\n"
             "- **Backward anchor** (`src/stage0_1.py` lines 198 to 210): runs required before ball 1 of the chase is anchored on the stated result: for a chase won by wickets, `target` = the forward target (rebuilt first-innings total + 1) clipped to lie between the rebuilt chase total minus (runs on the last ball - 1) and the rebuilt chase total; for a chase that LOST by runs, `target = rebuilt chase total + margin + 1`; for ties, rebuilt chase total + 1. So the target absorbs any error in the rebuilt chase total.\n"
             "- Other imputations: one dismissed player id inferred (match 40709 innings 2 ball 117 set to player 7897); `balls_left` = 120 minus legal balls bowled (match 41509 has a mislabelled over, handled by this rule); batting position clipped at 11.\n"
             "- Validation against public scorecards (15 matches, seed 42): mean error -1.00 runs, 29 of 30 totals within 5 runs; rebuilt margins differ from stated margins by a median 0.0 runs (95th percentile 4.0, max 8.0).\n"
             "- `env_tier`: leave-one-out venue scoring rate shrunk toward the group-season rate with 1200 pseudo-balls, cut into 3 terciles within each competition group.\n")
    # --- stage 2
    s.append("## Stage 2: scoring model, win probability, leverage and the pressure flag\n")
    s.append("Source: `outputs/audit_stage2.md`, `audit_stage2c.md`, `pressure_thresholds.json`, `stage2_choices.json`, `step3_reports.md` (c).\n")
    s.append(f"- **Scoring (next-ball) model inputs:** over band ({len(SM['over_band_starts'])} bands starting at overs {SM['over_band_starts']}), wickets lost (0 to 6, then 7+), required-rate band in innings 2 (edges {SM['rr_band_edges']}), venue scoring tier (`env_tier`, kept), competition group, impact-player rule. One multinomial logistic regression per innings, inverse regularisation C = {SM['C_fixed']} (fixed, CHANGES #5), fitted on all 808 clean matches.\n"
             "- **Outcome classes (10):** legal ball: wicket, 0, 1, 2, 3, 4, 6; illegal ball: 1, 2, 3+ runs. Wickets on wides/no-balls fold into the wicket class; 5 runs on a legal ball folds into the 4 class (CHANGES #8).\n"
             "- **Win probability:** exact backward induction over match states using the next-ball model (innings-1 states: score, balls left, wickets; chase states: runs required, balls left, wickets), then **recalibrated** on out-of-fold (leave-one-season-out) predictions: `logit(WP*) = a + c x logit(WP)`. Chase surface projected to be monotone (used; Brier loss 0.00000).\n")
    s.append("**Recalibration parameters** (`audit_stage2.md`):\n")
    s.append(sec(A2, "Recalibration"))
    s.append(f"\n- **Leverage:** `swing(s) = sum_o p(o|s) |WP*(after o) - WP*(s)|` and `LI(s) = swing(s) / mean swing over live balls` (mean swing on live balls = {thr['mean_swing_live']:.6f}, `pressure_thresholds.json`).\n"
             f"- **Live-ball bounds:** a ball is live when {PR['live_low']} < WP* < {PR['live_high']}. Live share: 99.7% of innings-1 balls, 78.0% of innings-2 balls.\n"
             f"- **Pressure cutoff:** LI >= **{thr['p80']:.4f}** = the {int(PR['pressure_quantile'] * 100)}th percentile of live-ball LI, pooled across both innings (so the top 20% of live balls). Median live LI {thr['median']:.4f}; 95th percentile {thr['p95']:.4f}; maximum LI 30.19.\n"
             "- **Number and share of pressure balls:** 34,494 of 193,076 clean balls (17.9%; 20.0% of live balls). In the 728 rated matches: **31,263** pressure balls of 156,062 live (20.0%). **Pressure balls outside overs 16 to 20: 75.4%.**\n")
    s.append("By innings (all clean balls):\n")
    s.append(sec(A2C, "By innings"))
    s.append("\nBy over (all clean balls; share of balls in that over that are pressure balls):\n")
    s.append(sec(A2C, "By over"))
    ri = {1: int(H.META["pressure_balls_innings1_rated"]), 2: int(H.META["pressure_balls_innings2_rated"])}
    s.append(f"\nIn the rated matches only: innings 1 has **{ri[1]}** pressure balls and innings 2 has **{ri[2]}** (`website/data/meta.json`). Pressure is essentially a live chase under the pooled cutoff (CHANGES #17); the 'within-innings' cutoff is a sensitivity variant.\n")
    # --- stage 3 pointer
    s.append("## Stage 3: proving the pressure definition\n")
    s.append(f"Run as described in `03_EVIDENCE_DEFINITION.md`. Settings: phases {S3['phase_bounds']} (powerplay 1-6, middle 7-15, death 16-20), wickets bands {S3['wicket_bands']} (0-2, 3-5, 6+), min {S3['min_cell_balls']} balls per cell on each side, {S3['bootstrap_n']} match bootstrap resamples; close = tie, or won by <= {S3['close_runs']} runs, or <= {S3['close_wickets']} wickets.\n")
    # --- stage 4
    s.append("## Stage 4: ball value, credit split, rating regression\n")
    s.append("Source: `src/rating_model.py`, `outputs/audit_stage4.md`, CHANGES #19 to #24, `report.md` section 4.\n")
    s.append("- **Ball value:** `dWP` is the change in the batting side's win probability (WP*). Subtract the mean `dWP` of balls in the same state bin (innings x over band x wickets band x leverage band; computed separately for batter and bowler rows), then divide by the ball's `swing`: `v = (dWP - mean dWP in bin) / swing`.\n")
    cred = re.search(r"\*\*Who gets the credit\.\*\*(.+?)\n\n", REPORT, re.S).group(1).strip()
    s.append(f"- **Credit table (who is credited or charged for each event):** {cred}\n")
    s.append("  - Implementation choices beyond the blueprint table (CHANGES #19): no-ball batter credit = WP*(after) minus WP*(after a lone penalty run); non-striker dismissals get their own row valued at the wicket's incremental effect; retire-out balls valued as if no wicket; bye/leg-bye valued as a dot ball for both sides; penalty rows excluded.\n")
    s.append("- **Regression form:** two ridge regressions, one on balls faced (150,307 batter rows) and one on balls bowled (156,062 bowler rows), live balls of the 728 rated matches:\n\n"
             "  `batting:  v = context + B_i + P x C_i - (W_j + P x K_j)`   `bowling:  v = context + W_j + P x K_j - (B_i + P x C_i)`\n\n"
             "  `i` batter, `j` bowler, `P` = 1 on pressure balls. `B`/`W` baselines, `C`/`K` pressure shifts. **Pressure rating = baseline + shift.** Context fixed effects = innings x phase x P (12 terms) + competition group (IPL vs T20I); context penalty "
             f"{R['context_lambda']}. Opposing players' terms in the same regression adjust for opposition quality.\n")
    ch = json.load(open(OUT / "stage4_choices.json"))
    s.append(f"- **Chosen penalties:** lambda_B = {ch['lambda_B']} (baselines), lambda_C = {ch['lambda_C']} (shifts); held-out MSE {ch['cv_mse']:.5f}. **How chosen:** {R['cv_folds']}-fold cross-validation with whole matches held out, loss = summed held-out squared error of both fits; grid lambda_B {R['lambda_B_grid']}, lambda_C {R['lambda_C_grid']}; neither optimum is on the grid edge. Shift penalty / baseline penalty = 10.0x. CV grid:\n")
    s.append(sec(A4, "CV grid"))
    s.append("\nSpread of ratings after shrinkage:\n")
    s.append(sec(A4, "Spread of ratings (shrinkage)"))
    # --- stage 5
    s.append("\n## Stage 5: fair comparison\n")
    s.append("Source: `outputs/audit_stage5.md`, `audit_stage4.md`, CHANGES #25 to #27.\n")
    s.append(f"- **Eligibility thresholds:** {R['eligibility']['min_pressure_balls']} pressure balls and {R['eligibility']['min_matches']} matches. **Fallback used: none** (batters False, bowlers False).\n"
             "- **Eligible players per role:** batters 53, bowlers 56 (before the active filter); **eligible and active** (any appearance in 2025 or 2026): batters 53, bowlers 55; **ranked pool** after removing reliably negative shifts: batters 47, bowlers 48.\n")
    s.append(sec(A5, "Eligibility"))
    s.append("\n- **Shrinkage:** the two ridge penalties (above) shrink a thin pressure record toward the player's baseline and a thin baseline toward average. Eligible-player SD of baselines 0.063 (batters) / 0.067 (bowlers); of shifts 0.0085 / 0.0084.\n"
             "- **Opposition:** opposing players' baseline and shift terms sit in the same regression. A simple version without the regression (shrunk raw means) ranks almost identically: Spearman 0.9696 batters, 0.9839 bowlers (shrinkage constants k via method of moments: baseline 235.0 / 182.6, shift 567.1 / 429.9).\n"
             "- **IPL vs T20I:** one model, one scale, competition-group term in the context. IPL-only and T20I-only ratings are sensitivity variants (top-10 overlap with the main list: IPL-only 6 batters / 8 bowlers; T20I-only 6 / 7).\n"
             "- **Venue and era:** enter the SCORING model (venue scoring tier, impact-player rule), hence win probability and leverage. They are NOT in the rating regression's context (only innings, phase, pressure, competition group); batting-position band was tested as a variant only (overlap 10 of 10 batters).\n"
             f"- **Bootstrap:** {R['bootstrap_n']} whole-match resamples of both fits with penalties fixed, seed {CFG['seed']}. Outputs: `floor_p10` (10th percentile), `p90`, `boot_sd`, `p_top10`, `p_top20`, rank 10th/90th percentile. P(top 10), P(top 20) are computed among eligible AND active players.\n")
    # --- stage 6 pointer
    s.append("## Stage 6: reliability and sensitivity\n")
    s.append(f"Details in `04_EVIDENCE_RELIABILITY.md`. Settings: split-half {S6['split_half_n']} random match splits with halved eligibility ({S6['half_min_pressure_balls']} pressure balls, {S6['half_min_matches']} matches); season split fit on <= {S6['season_split_year']}, score {R['active_years'][0]}-{R['active_years'][1]}; {S6['permutations']} permutations; sensitivity cutoffs {CFG['sensitivity']['cutoffs']}, recency half-life {CFG['sensitivity']['recency_half_life_years']} years, winsor quantiles {CFG['sensitivity']['winsor_quantiles']}.\n")
    # --- stage 7
    s.append("## Stage 7: ranking and sanity checks\n")
    s.append("- **Ranking rule:** see `01_RANKINGS.md` (eligible + active, drop reliably negative shift, sort by bootstrap floor, ties by delivery rate then pressure balls).\n"
             "- **Face validity (ranks 11 to 20, from `audit_stage7.md`):** batters 11 Jos Buttler, 12 Virat Kohli, 13 Lokesh Rahul, 14 Mitchell Marsh, 15 Ishan Kishan, 16 Yashasvi Jaiswal, 17 Cameron Green, 18 Riyan Parag, 19 Rovman Powell, 20 Josh Inglis; bowlers 11 Mujeeb Ur Rahman, 12 Bhuvneshwar Kumar, 13 Mitchell Santner, 14 Ravindra Jadeja, 15 Mohammad Nawaz, 16 Trent Boult, 17 Kagiso Rabada, 18 Arshdeep Singh, 19 Haris Rauf, 20 Mustafizur Rahman.\n"
             "- **Sign check:** every listed batter has runs index > 100 or dismissal ratio < 1. For bowlers, under the amended rule 0 of 10 fail; under the original economy-only rule 2 fail (Hasaranga 94.8, Noor Ahmad 91.5; their wicket ratios are 1.34 and 1.39). See `00_DEVIATIONS.md`.\n"
             "- **Surprises explained:** see `05_PLAYER_CARDS.md` (surprise names chosen by the website's stated rule) and `07_LIMITATIONS_OBSERVED.md`.\n"
             "- **Spinner share:** 8 of the 10 listed bowlers are spinners vs 20 of 55 in the eligible, active pool; spinners bowl 35.0% of pressure balls vs 37.2% of all live balls (ratio 0.939) (`outputs/step3_reports.md` (d), `step3_summary.json`).\n")
    W("02_METHOD_AS_RUN.md", "\n".join(s))


# =====================================================================================================  03
def doc_03(trace_sum, rs_info):
    S3 = CFG["stage3"]
    s = ["# 03 EVIDENCE FOR THE PRESSURE DEFINITION (Stage 3)\n",
         "Everything below is read from `outputs/audit_stage3.md`, `audit_stage2.md`, `audit_stage2c.md`, `website/data/league_split.json` and `outputs/balls_pressure.parquet`. Comparison is between LIVE pressure balls and LIVE ordinary balls, standardised within innings x phase x wickets band (cells need at least 30 balls on both sides), with 95% intervals from 300 whole-match bootstrap resamples.\n"]
    sh = table_from(sec(A3, "Outcome and behaviour shift (phase-level, stratified)"))
    s.append("## 1. Outcome shift by phase (stratified; pressure minus ordinary)\n")
    s.append("Differences are in rate units (e.g. 0.0208 = +2.08 percentage points); `runs` is runs per ball. `extras` = wides and no-balls per delivery (`m_extras = is_wide | is_noball` in `stage3_prove.py`). Wickets-band and innings standardisation is inside each phase (the audit reports the phase level only; the raw cell rates by innings, phase and wickets band are in Section 4).\n")
    out = sh[sh.metric.isin(["dismissal", "dot", "boundary", "runs", "extras"])].copy()
    s.append(md(out, ".4f"))
    s.append("\n**Which phases pass the gate** (dismissal OR boundary interval excludes zero; need >= 2 of 3):\n")
    g = []
    for ph in out.phase.unique():
        q = out[out.phase == ph].set_index("metric")
        g.append(dict(phase=ph, dismissal_excludes_zero=bool(q.loc["dismissal", "excludes_zero"] in (True, "True")), boundary_excludes_zero=bool(q.loc["boundary", "excludes_zero"] in (True, "True"))))
    g = pd.DataFrame(g)
    g["passes"] = g.dismissal_excludes_zero | g.boundary_excludes_zero
    s.append(md(g))
    s.append(f"\n**Result: {int(g.passes.sum())} of 3 phases pass; gate PASS.** Honest detail: in the powerplay the dismissal difference (+0.07 pts) and in the death overs the boundary difference (+1.7 pts, interval -0.2 to +3.7) do not exclude zero; the pass comes from boundaries in the powerplay and dismissals in the death overs. Outcome 'runs' differences exclude zero in all three phases.\n")
    s.append("## 2. Behaviour shift (strokes and delivery styles)\n")
    beh = sh[sh.metric.isin(["attacking_stroke", "defensive_stroke", "yorker", "slower"])]
    s.append(md(beh, ".4f"))
    s.append("\nGroupings (config `stage3`, chosen by me, CHANGES #15): attacking = Slog, Slog Sweep, Paddle Scoop, Reverse Paddle Scoop; defensive = Frontfoot defensive, Backfoot defensive, Defense, Intentional Padding; yorker = Yorker, Wide Yorker; slower = Slow Ball, Slow Bouncer, Knuckle, Back of Hand.\n")
    s.append("## 3. League-wide pressure vs ordinary (RAW rates, not standardised)\n")
    s.append("Source: `website/data/league_split.json` `overall` (aggregation of the rated matches' live balls). These raw rates mix phases and innings: for example in the death overs the raw pressure strike rate (161.4) is slightly BELOW the ordinary one (164.0) even though the stratified runs-per-ball difference is positive. Use the stratified table in Section 1 for the 'proof' and these for headline context.\n")
    o = H.LEAGUE["overall"]
    lg = pd.DataFrame({"metric": ["balls faced (non-wide)", "deliveries bowled", "strike rate", "dismissal % of balls faced", "dot %", "boundary %", "economy (runs/over)", "balls per wicket", "wickets"],
                       "normal (ordinary live balls)": [o["normal"][k] for k in ("balls", "deliveries", "sr", "dismissal_pct", "dot_pct", "boundary_pct", "economy", "balls_per_wicket", "wickets")],
                       "pressure": [o["pressure"][k] for k in ("balls", "deliveries", "sr", "dismissal_pct", "dot_pct", "boundary_pct", "economy", "balls_per_wicket", "wickets")]})
    s.append(md(lg, ".2f"))
    s.append("\nBy phase (same file, `by_phase`):\n")
    rows = []
    for ph, d in H.LEAGUE["by_phase"].items():
        for k in ("sr", "dismissal_pct", "dot_pct", "boundary_pct", "economy"):
            rows.append(dict(phase=ph, metric=k, normal=d["normal"][k], pressure=d["pressure"][k]))
    s.append(md(pd.DataFrame(rows), ".2f"))
    s.append("\n## 4. Raw cell rates by innings, phase and wickets band\n")
    s.append("(`audit_stage3.md`; only cells with enough balls on both sides appear. Innings 1 contributes a single cell: 98 pressure balls.)\n")
    s.append(sec(A3, "Raw cell rates"))
    s.append("\n## 5. Close games vs blowouts: leverage against final margin\n")
    s.append(sec(A3, "Close games against blowouts"))
    s.append("\n- 'Close' = tie, or won by <= 10 runs, or won with <= 3 wickets in hand. Margin is never an input to the pressure definition.\n")
    s.append("## 6. Benchmark agreement\n")
    s.append(sec(A3, "Benchmark agreement (innings 2)"))
    s.append("\n**Reading:** rank correlation between our LI and the published pressure index on live chase balls is 0.328 (all chase balls 0.110; by phase 0.089 / 0.266 / 0.233). The two agree on direction but are far from identical, and the index's resources-used term is substituted by one derived from our own scoring model (CHANGES #14). "
             "Overlap with the rule-of-thumb set: 92.6% of rule-of-thumb chase balls are pressure balls, but the rule covers only 16.4% of pressure chase balls (Jaccard 0.162). In innings 1 the rule marks 16,710 balls and 98 are pressure.\n")
    s.append("## 7. Calibration of the win probability (held-out seasons)\n")
    s.append("Leave-one-season-out. `gap` = predicted minus observed; `gap_lo`/`gap_hi` = 95% match-bootstrap interval on the gap (about +/-0.05, as wide as the 0.05 tolerance).\n")
    s.append("**Brier scores and log loss:**\n")
    s.append(sec(A2, "Brier and log loss (leave-one-season-out)"))
    s.append("\nThe final model WP* beats the one-feature baseline in both innings (innings 1: 0.2193 vs 0.2294; innings 2: 0.1270 vs 0.1490). The raw (un-recalibrated) WP is slightly better on Brier (0.2190 / 0.1264) but fails the decile gate (raw max gap 0.0994 / 0.0601), which is why recalibration is used.\n")
    s.append("**Decile table, WP*, innings 1:**\n")
    s.append(sec(A2, "Deciles, WP* (innings 1)"))
    s.append("\n**Decile table, WP*, innings 2:**\n")
    s.append(sec(A2, "Deciles, WP* (innings 2)"))
    s.append("\n**Honest caveats on calibration (from the same audit):** innings-1 bins above 0.8 over-predict (e.g. bin (0.9, 0.95]: predicted 0.922, observed 0.839, 969 balls); start-of-chase over-predicts chasing associates by 8.7 points (52 matches) and A-teams by 5.4 points (30 matches); IPL -0.1, full-member T20I +2.3.\n")
    s.append("## 8. Three tight finishes and three one-sided chases\n")
    s.append("Selection rule (from `src/stage3_prove.py`, replicated and matched at build time): tight = the first tie, the closest win by runs (margin <= 2, ties broken by margin then match id), the first win by 1 wicket or fewer; one-sided = the two largest wins by runs and the largest win by wickets. Series are the CHASING innings (innings 2). Underlying series exported as `03_trace_series.csv` (derived columns only: match id, ball of the chase, over, LI, WP*, live, pressure flag); summaries in `03_trace_summary.csv`.\n")
    ts = trace_sum.copy()
    s.append(md(ts, ".3f"))
    s.append("\n**Short ball-by-ball LI readings:**\n")
    tf = H.trace_frame()
    for _, r in ts.iterrows():
        d = tf[tf.match_id == r.match_id]
        last = d.tail(6)
        s.append(f"- **{r.match_id}** ({r.kind}, {r.date}, {r.teams}, chasing: {r.chasing_team}, target {r.target}; result: {r.result}). Peak LI {r.peak_LI} on ball {r.peak_ball_of_chase} (over {r.peak_over}); {r.pressure_balls} of {r.chase_balls} chase balls are pressure balls ({100 * r.pressure_share_of_chase:.1f}%). Last six balls' LI: {', '.join(f'{v:.2f}' for v in last.LI)}.")
    r13 = ts[ts.match_id == 13512].iloc[0]
    s.append("\n### FLAG: one of the three 'tight finish' traces barely registers as pressure\n")
    s.append("Match **13512** (England won by 1 run, West Indies chasing 174 in the model) has peak LI **%s**, only **%d** pressure balls (%.1f%% of the chase), and %d of its %d chase balls are 'dead' (WP* outside 0.02 to 0.98) so they are excluded from pressure. The chase was effectively lost on the model's numbers until the last over, when three sixes (`balls_state` `runs` = 6 on each of the last three balls) closed the gap to the 1-run margin. " % (r13["peak_LI"], r13["pressure_balls"], 100 * r13["pressure_share_of_chase"], r13["chase_balls"] - r13["live_balls"], r13["chase_balls"]) +
             "Two issues: (1) the three 'tight' ids were picked mechanically by `stage3_prove.py`, not by looking at them, and this one does not illustrate a pressure spike; (2) the rebuilt state does not reconcile exactly with the stated margin: rebuilt R1 = 171, rebuilt R2 = 172 (`outputs/matches_clean_totals.csv`), anchor target = 174 (R2 + margin 1 + 1), so the model has the chasers needing 8 off the last ball and finishing 2 short, while the stated margin is 1 run (the backward anchor puts any rebuilt-total error into the target; the margin gate allows up to 6 at the 95th percentile, 8 at the maximum). "
             "**For slides, use match 16662 (Pakistan won by 1 wicket, peak LI 11.31, 63.2% pressure balls) or 13613 (peak LI 18.35, 63.1%) as the tight example, not 13512.** I did not change any figure or rule. See `07_LIMITATIONS_OBSERVED.md`.\n")
    s.append("Figures for this document are listed in `08_FIGURE_INDEX.md` (F01 heatmap, F02 calibration, F03 trace, F09 paired bars, plus the originals `stage3_*.png`, `stage2_calibration.png`).\n")
    W("03_EVIDENCE_DEFINITION.md", "\n".join(s))


# =====================================================================================================  04
def doc_04():
    s = ["# 04 EVIDENCE FOR RELIABILITY (Stage 6), good and bad\n",
         "Source: `outputs/audit_stage6.md` (identical text to `outputs/reliability.md`), `audit_stage5.md`, `audit_stage6b.md`, `sensitivity.csv`, `top10_*.csv`, `website/data/robustness.json`. Penalties are fixed; thresholds halved for split-half and season-to-season (60 pressure balls, 7 matches).\n"]
    s.append("## 1. Split-half reliability (Spearman-Brown corrected)\n")
    s.append(f"{CFG['stage6']['split_half_n']} random splits of matches; each half rated with the same penalties; the file reports the SD of the raw split-half r across the 200 splits (`sd_over_splits`). **A percentile interval for the corrected value was NOT COMPUTED** (the per-split values were not saved), so the SD is the only spread available.\n")
    s.append(sec(A6, "Split-half reliability (200 random match splits, Spearman-Brown corrected)"))
    s.append("\n**Decision rule fixed in the blueprint:**\n")
    s.append(sec(A6, "Decision rule fixed in the blueprint"))
    s.append("\n## 2. Season to season (fit on 2022-2024, score 2025-2026)\n")
    s.append(sec(A6, "Season to season (fit on <= 2024, score later; bootstrap over players)"))
    s.append("\n`ci_lo`/`ci_hi` = 95% interval, bootstrap over players. Bowlers persist; batters do not (r = 0.0477, interval -0.2294 to 0.3174, n = 34).\n")
    s.append("## 3. Does the pressure shift add anything?\n")
    s.append(sec(A6, "Does the shift add anything? (later mean value on pressure balls ~ earlier baseline + earlier shift, WLS)"))
    s.append("\nThe shift coefficient's interval includes zero for both roles (batters 0.0200, [-0.0156, 0.0530]; bowlers 0.0112, [-0.0373, 0.0439]). Only the bowler baseline predicts later pressure value (0.0851, [0.0363, 0.1327]).\n")
    s.append("## 4. Permutation test\n")
    s.append(sec(A6, "Permutation test on raw pressure shifts (shuffle the pressure flag within each player)"))
    s.append(f"\n500 shuffles. Observed spread vs the 95th percentile of shuffles: batters 0.2697 vs 0.2704 (not beyond, p = 0.062); bowlers 0.2523 vs 0.2519 (just beyond, p = 0.048).\n")
    s.append("## 5. Rank stability of every listed player\n")
    rows = []
    for role in ("batters", "bowlers"):
        for _, r in H.TOP[role].iterrows():
            rows.append(dict(role=role[:-1], rank=int(r["rank"]), name=r["name"], p_top10=r.p_top10, p_top20=r.p_top20, rank_p10=r.rank_p10, rank_p90=r.rank_p90, variants_in_top10_of_14=int(r.variants_in_top10), fragile=bool(r.fragile)))
    st = pd.DataFrame(rows)
    s.append(md(st, ".3f"))
    exc = st[(st.p_top20 < 0.6) | (st.p_top10 < 0.5) | (st.fragile)]
    exc_txt = ", ".join("%s (%.3f)" % (r["name"], r.p_top10) for _, r in exc.iterrows()) or "none"
    s.append("\n**Exceptions flagged** (rule 1: P(top 20) < 0.6 = none; rule 2, my addition: P(top 10) < 0.5; rule 3: fragile flag):\n")
    s.append("- P(top 20) below 0.6: **none** (lowest is Shubman Gill 0.76).\n- Fragile flag: **none** (Gill is in the top 10 under 7 of 14 variants, exactly half; the rule flags fewer than half).\n"
             f"- P(top 10) below 0.5 (listed players that finish in the top 10 in fewer than half of resamples): {exc_txt}.\n")
    s.append("## 6. Cross-check: regression ranking vs the simple shrunk ranking\n")
    s.append(sec(A5, "Cross-check: simple shrunk version vs regression (blueprint wants Spearman >= 0.8)"))
    s.append("\n## 7. Which blueprint rule did the reliability number trigger, and what the report should lead with\n")
    s.append("- **Rule triggered:** split-half pressure rating >= 0.40 (batters 0.5358, bowlers 0.6617) -> **'rank on it'**. The 'widen to top 30%' branch and the 'below 0.25' branch were not triggered by the rating. The pressure shift on its own is 0.1303 / 0.1495 (below 0.25). Blueprint wording for that branch: `NOT AVAILABLE (blueprint not provided)`.\n")
    s.append("- **Plain-language finding to lead with** (the project's own report.md leads with it):\n\n> The ratings measure proven quality in live, high-leverage situations. A separate clutch trait is not reliably measurable in this data (pressure-shift split-half reliability 0.13 for batters and 0.15 for bowlers).\n\n"
             "- Supporting lines: the baseline alone is as reliable as the pressure rating (0.531 / 0.662 vs 0.536 / 0.662), so the repeatability is general quality; bowlers persist across 2022-24 vs 2025-26 (r = 0.511, 95% interval 0.252 to 0.720, n = 37), batters do not (r = 0.048, interval -0.229 to 0.317, n = 34; batter baseline r = 0.027).\n")
    s.append("## 8. Sensitivity\n")
    s.append("Copied: `sensitivity.csv` (this folder) = `outputs/sensitivity.csv`. Overlap is with the main top 10 under the same floor PROXY (rating minus 1.2816 x bootstrap SD), not the final list; Kendall tau is over the eligible pool.\n")
    sn = H.SENS_SUM.copy()
    piv = sn.pivot(index="variant", columns="role", values=["top10_overlap_with_main", "kendall_tau"])
    piv.columns = [f"{a.replace('top10_overlap_with_main', 'overlap_of_10')}_{b}" for a, b in piv.columns]
    piv = piv.reset_index()
    piv["variant"] = pd.Categorical(piv.variant, categories=H.VARIANTS, ordered=True)
    s.append(md(piv.sort_values("variant"), ".3f"))
    s.append("\nMedian overlap: batters 9, bowlers 9 (target >= 7). Minimum overlap: 6 of 10 (IPL-only and T20I-only batters). Not run: win probability without recalibration.\n")
    s.append("### Which listed players drop out of which variants\n")
    rows = []
    for role in ("batters", "bowlers"):
        for _, r in H.TOP[role].iterrows():
            miss = [v for v in H.VARIANTS if not H.VM[role].loc[r.player_id, v]]
            rows.append(dict(role=role[:-1], rank=int(r["rank"]), name=r["name"], in_top10_of_14=14 - len(miss), drops_out_in=len(miss), fragile=bool(r.fragile), variants_missed=", ".join(miss) or "none"))
    s.append(md(pd.DataFrame(rows)))
    s.append("\n(Membership reproduced from `sensitivity_ratings_*.csv` with the stage-7 rule and matches `variants_in_top10` for all 20 players; asserted at build time.)\n")
    rb = H.ROBUST["roles"]
    s.append(f"**Across the five cutoffs (the chosen top 20% plus 10/15/25/30%)**, on the website's proxy lists, between {rb['batters']['cutoff_survivors_min']} and {rb['batters']['cutoff_survivors_max']} of the final top-10 batters and between {rb['bowlers']['cutoff_survivors_min']} and {rb['bowlers']['cutoff_survivors_max']} of the final top-10 bowlers survive in the top 10 (`website/data/robustness.json` `cutoff_survivors_min/max`).\n")
    gill = H.VM["batters"].loc[6288]
    gmiss = ", ".join(v for v in H.VARIANTS if not gill[v])
    s.append("**Which listed players are fragile:** none by the pipeline's rule (fewer than half of 14 variants). **Closest to it:** Shubman Gill, in the top 10 under 7 of 14 variants (out under: %s); Axar Patel and Krunal Pandya 10 of 14 each; Nicholas Pooran 11 of 14.\n" % gmiss)
    W("04_EVIDENCE_RELIABILITY.md", "\n".join(s))
