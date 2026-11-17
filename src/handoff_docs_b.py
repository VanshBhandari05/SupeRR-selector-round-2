"""Handoff pack, documents 05 to 12 plus the deck-number list."""
import json
import re
import shutil
import subprocess
import urllib.request

import numpy as np
import pandas as pd

import handoff_data as H
import handoff_figs as F
from handoff_data import CFG, OUT, PACK, ROOT, WEB, md, rd, sec, table_from, ordinal
from handoff_docs_a import A1, A2, A2C, A3, A4, A5, A6, A6B, A7, TODAY, W, rank_table


# =====================================================================================================  05
def why_sentence(role, r, c, prev):
    nm = r["name"]
    p = f"{nm} ranks {ordinal(r['rank'])} on a floor of {r.floor_p10:.3f} (rating {r.pressure_rating:.3f} = baseline {r.baseline:.3f} {r['shift']:+.3f} shift) from {c['pressure_balls']} pressure balls in {c['matches_with_pressure_balls']} matches"
    if role == "batters":
        p += f"; his strike rate is {c['sr_pressure']} on pressure balls against {c['sr_ordinary']} on ordinary balls (runs index {c['runs_index']}, dismissal ratio {c['dismissal_ratio']})"
    else:
        p += f"; his economy is {c['econ_pressure']} on pressure balls against {c['econ_ordinary']} on ordinary balls (economy index {c['economy_index']}, wicket ratio {c['wicket_ratio']})"
    if prev is not None and r.pressure_rating > prev.pressure_rating:
        p += f"; his rating is higher than {prev['name']}'s ({r.pressure_rating:.3f} vs {prev.pressure_rating:.3f}) but his floor is lower ({r.floor_p10:.3f} vs {prev.floor_p10:.3f}), so he ranks below"
    if r.p_top10 < 0.5:
        p += f"; he finishes in the top 10 in only {100 * r.p_top10:.0f}% of resamples (P(top 20) {r.p_top20:.2f})"
    if c["t20i_pressure_balls"] == 0:
        p += "; all his pressure balls are in the IPL, so he is rated on one competition only"
    if role == "bowlers" and not r.sign_check_strict:
        p += "; his economy index is below 100 but his wicket ratio is above 1, which is why the bowler sign check was amended"
    if role == "bowlers" and c["wicket_ratio"] < 1:
        p += "; his wicket ratio is below 1 so his rating rests on economy"
    return p + "."


def surprises_omissions():
    sur, om = {}, {}
    for role in ("batters", "bowlers"):
        sur[role] = list(H.TOP[role].nsmallest(3, "p_top10").player_id)
        got = [d["id"] for d in H.OMIT["surprises"][role]]
        assert set(sur[role]) == set(got), (role, sur[role], got)
        e = H.UNF[role].copy()
        e["base"] = e["B"] if role == "batters" else e["W"]
        e = e[~e.player_id.isin(H.TOP[role].player_id)].sort_values("base", ascending=False).head(4)
        om[role] = list(e.player_id)
        site = [d["id"] for d in H.OMIT["omissions"][role]]
        assert set(om[role]) == set(site), (role, om[role], site)
    return sur, om


def doc_05():
    sur, om = surprises_omissions()
    s = ["# 05 PLAYER CARDS: one evidence card per listed player (20)\n",
         "Source: `outputs/evidence_cards.md` (parsed), `outputs/top10_*.csv`, `outputs/eligible_table_*.csv`. Cards follow the blueprint's evidence-card blocks: sample, rating, cricket numbers on pressure vs ordinary balls, consistency, single highest-value pressure match (date, opponent; value = win probability added over the player's pressure balls in that match, `dWP0` summed). "
         "The 'why' sentence is generated from the numbers only. `player_cards.csv` has the same fields in one row per player.\n",
         "**Surprise names** (marked SURPRISE): for each role, the three listed players with the lowest probability of finishing in the top 10 across the 300 resamples (the website's stated rule, `website/data/omissions.json`; replicated here and equal). **Notable omissions** (marked OMISSION in the table at the end): for each role, the four eligible players outside the top 10 with the highest baseline rating (this includes players removed for a reliably negative shift). Both are rules, not my taste.\n"]
    rows = []
    for role in ("batters", "bowlers"):
        t = H.TOP[role]
        s.append(f"## {role.capitalize()}\n")
        prev = None
        for _, r in t.iterrows():
            c = H.CARDS[int(r.player_id)]
            tag = " (SURPRISE)" if int(r.player_id) in sur[role] else ""
            w = why_sentence(role, r, c, prev)
            body = c["raw_text"]
            s.append(f"### {role[:-1].capitalize()} #{int(r['rank'])}: {r['name']} (id {int(r.player_id)}; {r.teams}){tag}\n")
            s.append(body + "\n")
            s.append(f"- Companion: {'sign check (strict economy-only rule) passes' if r.sign_check_strict else 'fails the strict economy-only sign rule; passes the amended rule'}; amended sign check passes: {bool(r.sign_check)}.\n- **Why he ranks here:** {w}\n")
            row = dict(role=role[:-1], rank=int(r["rank"]), player_id=int(r.player_id), name=r["name"], teams=r.teams, surprise=int(r.player_id) in sur[role],
                       pressure_balls=c["pressure_balls"], matches_with_pressure_balls=c["matches_with_pressure_balls"], ipl_pressure_balls=c["ipl_pressure_balls"], t20i_pressure_balls=c["t20i_pressure_balls"],
                       pressure_rating=r.pressure_rating, floor_p10=r.floor_p10, p90=r.p90, baseline=r.baseline, shift=r["shift"], p_top10=r.p_top10, p_top20=r.p_top20, rank_p10=r.rank_p10, rank_p90=r.rank_p90,
                       delivery_rate=r.delivery_rate, delivery_matches=c["delivery_matches"], variants_in_top10_of_14=int(r.variants_in_top10), fragile=bool(r.fragile),
                       best_match_date=c["best_match_date"], best_match_opponent=c["best_match_opponent"], best_match_wp_added=c["best_match_wp_added"], why=w)
            if role == "batters":
                row.update(strike_rate_pressure=c["sr_pressure"], strike_rate_ordinary=c["sr_ordinary"], runs_index=c["runs_index"], dismissal_ratio=c["dismissal_ratio"])
            else:
                row.update(economy_pressure=c["econ_pressure"], economy_ordinary=c["econ_ordinary"], economy_index=c["economy_index"], wicket_ratio=c["wicket_ratio"])
            rows.append(row)
            prev = r
    pd.DataFrame(rows).to_csv(PACK / "player_cards.csv", index=False, encoding="utf-8")
    s.append("## Notable omissions (rule: highest baseline among eligible players outside the top 10)\n")
    allr = {r: H.UNF[r].set_index("player_id") for r in ("batters", "bowlers")}
    pool = {r: H.POOL[r].set_index("player_id") for r in ("batters", "bowlers")}
    ors = []
    for role in ("batters", "bowlers"):
        tenth = H.TOP[role].floor_p10.iloc[-1]
        for pid in om[role]:
            e = allr[role].loc[pid]
            status = f"ranked {int(pool[role].loc[pid, 'rank'])} in the pool" if pid in pool[role].index else ("removed: reliably negative shift" if bool(e.active) else "not active in 2025-26")
            base = e["B"] if role == "batters" else e["W"]
            ors.append(dict(role=role[:-1], player_id=int(pid), name=e["name"], baseline=base, baseline_rank_among_eligible=int(allr[role]["B" if role == "batters" else "W"].rank(ascending=False).loc[pid]), status=status, floor_p10=e.floor_p10,
                            floor_of_10th_listed=tenth, p_top10=e.p_top10, shift=e.C if role == "batters" else e.K, shift_p90=e.shift_p90, **{"gap_floor_to_10th": e.floor_p10 - tenth}))
    s.append(md(pd.DataFrame(ors), ".4f"))
    s.append("\nReading: each omission is excluded because his FLOOR is below the 10th listed player's floor (or, if marked removed, because his bootstrap shift is reliably negative). Jos Buttler is the closest: 11th, floor 0.0937 vs Gill's 0.0941 (a gap of 0.0004).\n")
    W("05_PLAYER_CARDS.md", "\n".join(s))
    return sur, om


# =====================================================================================================  06
def doc_06(rs):
    s = ["# 06 FAIRNESS AND ADJUSTMENT\n"]
    s.append("## 1. Raw vs shrunk ratings of the 20 listed players\n")
    s.append("Three numbers per player, all in the same unit (value per ball, in units of expected swing in win probability):\n"
             "- **raw** = unshrunk mean ball value `v` on the player's pressure balls (NEW aggregation of `outputs/ball_values_bat.parquet` / `ball_values_bowl.parquet`; no opposition adjustment, no shrinkage; `n` is the number of pressure-ball rows);\n"
             "- **simple shrunk** = `simple_rating` in the pipeline (shrunk raw means, no regression, no opposition terms; Stage 5 cross-check);\n"
             "- **final ridge pressure rating** = baseline + shift from the regression (the ranking input).\n"
             "The final rating is NOT just 'raw pulled toward zero': it also removes opposition strength and context terms, so some players move up (e.g. Tim David raw 0.131 -> 0.226). Compare the first two columns to see pure shrinkage.\n")
    t = rs.copy()
    t["shrink_effect (simple - raw)"] = t.simple_shrunk_rating - t.raw_mean_value_on_pressure_balls
    t["adjustment_effect (ridge - simple)"] = t.final_ridge_pressure_rating - t.simple_shrunk_rating
    s.append(md(t.drop(columns=["baseline", "shift"]), ".4f"))
    corr = {}
    for role in ("batters", "bowlers"):
        e = H.UNF[role].merge(H.RAW[role][["raw_pressure_mean_v"]], left_on="player_id", right_index=True)
        corr[role] = (np.corrcoef(e.raw_pressure_mean_v, e.pressure_rating)[0, 1], np.corrcoef(e.simple_rating, e.pressure_rating)[0, 1], len(e))
    s.append(f"\nAcross all eligible players: Pearson r(raw, final) = {corr['batters'][0]:.3f} batters (n={corr['batters'][2]}), {corr['bowlers'][0]:.3f} bowlers (n={corr['bowlers'][2]}); r(simple shrunk, final) = {corr['batters'][1]:.3f} / {corr['bowlers'][1]:.3f}. (New aggregation; the pipeline's own rank cross-check is Spearman 0.9696 / 0.9839, `audit_stage5.md`.)\n")
    s.append("Figure: `08_FIGURES/F04_raw_vs_shrunk.png`.\n")
    s.append("## 2. Opposition adjustment: biggest rank movers\n")
    s.append("Compares the rank by **final ridge pressure rating** (which has opposing players' terms in the regression) with the rank by **simple shrunk rating** (no regression, no opposition terms) among all eligible players (53 batters, 56 bowlers). Caveat: the two versions also differ in how they shrink, so this is 'regression with opposition adjustment vs simple shrunk', not an isolated opposition effect. Positive `rank_gain` = the regression ranks him higher than the simple version. (NEW aggregation of existing `simple_rating` and `pressure_rating` columns; ranks computed among all eligible players, ties broken by order.)\n")
    for role in ("batters", "bowlers"):
        up, dn, allm = H.movers(role)
        s.append(f"**{role}: top 5 up**\n")
        s.append(md(up.rename(columns={"moved_up_by_regression": "rank_gain"})[["name", "player_id", "rank_simple", "rank_regression", "rank_gain"]], ".0f"))
        s.append(f"\n**{role}: top 5 down**\n")
        s.append(md(dn.rename(columns={"moved_up_by_regression": "rank_gain"})[["name", "player_id", "rank_simple", "rank_regression", "rank_gain"]], ".0f"))
        s.append("")
    s.append("## 3. Share of pressure-rating variance from baseline vs pressure shift\n")
    s.append("NEW computation (not in the pipeline) on the eligible players' ridge estimates: `var(B + C) = var(B) + var(C) + 2cov(B, C)`.\n")
    vs = pd.DataFrame([H.variance_share("batters"), H.variance_share("bowlers")])
    s.append(md(vs, ".5f"))
    s.append(f"\nReading: the baseline accounts for about {100 * vs.share_baseline.iloc[0]:.0f}% (batters) and {100 * vs.share_baseline.iloc[1]:.0f}% (bowlers) of the variance of the pressure rating among eligible players; the shift's own variance share is about {100 * vs.share_shift.iloc[0]:.1f}% and {100 * vs.share_shift.iloc[1]:.1f}%; the rest is covariance. This agrees with the pipeline: shift split-half reliability 0.13 / 0.15, and the shift penalty is 10x the baseline penalty.\n")
    s.append("## 4. Eligible-player counts\n")
    s.append("| role | eligible | eligible and active (2025-26) | removed for reliably negative shift | ranked pool |\n|---|---|---|---|---|\n"
             f"| batters | 53 | 53 | 6 | 47 |\n| bowlers | 56 | 55 | 7 | 48 |\n")
    s.append("Sources: `website/data/meta.json`, `outputs/audit_stage5.md`, `audit_stage7.md`. Players with any rows at all: 627 batters, 459 bowlers (`meta.json`, `players_with_any_rows_*`).\n")
    s.append("## 5. Player tables in this pack\n")
    s.append("- `player_ratings.csv`: all 109 eligible players (53 batters + 56 bowlers) with baseline, shift, pressure rating, floor, 90th percentile, bootstrap SD, P(top 10/20), rank interval, `simple_rating`, sample sizes (pressure balls and matches), companion cricket stats, active flag, whether he is in the ranked pool, his pool rank, whether removed for a negative shift, and whether he is listed.\n"
             "- `players_unfiltered.csv`: the pipeline's own unfiltered appendix lists (`outputs/unfiltered_eligible_batters.csv`, `unfiltered_eligible_bowlers.csv`) stacked, unchanged, with a `role` column. These contain every eligible player whether or not active.\n")
    W("06_FAIRNESS_AND_ADJUSTMENT.md", "\n".join(s))


def write_player_tables():
    frames = []
    for role in ("batters", "bowlers"):
        e = H.UNF[role].copy()
        e.insert(0, "role", role[:-1])
        e.to_csv(PACK / f"_tmp_unf_{role}.csv", index=False)
        frames.append(e)
        (PACK / f"_tmp_unf_{role}.csv").unlink()
    pd.concat(frames, ignore_index=True).to_csv(PACK / "players_unfiltered.csv", index=False, encoding="utf-8")
    out = []
    for role in ("batters", "bowlers"):
        e = H.UNF[role].copy()
        pool = H.POOL[role].set_index("player_id")
        e["in_ranked_pool"] = e.player_id.isin(pool.index)
        e["pool_rank"] = e.player_id.map(pool["rank"])
        e["removed_reliably_negative_shift"] = e.active & ~e.in_ranked_pool
        e["listed_top10"] = e.player_id.isin(H.TOP[role].player_id)
        e["role"] = role[:-1]
        e["baseline"] = e["B"] if role == "batters" else e["W"]
        e["shift"] = e["C"] if role == "batters" else e["K"]
        e["pressure_balls"] = e[H.PB[role]]
        e["matches_with_pressure_balls"] = e["matches_P"]
        keep = ["role", "player_id", "name", "baseline", "shift", "pressure_rating", "floor_p10", "p90", "boot_sd", "p_top10", "p_top20", "rank_p10", "rank_p90", "simple_rating", "pressure_balls", "matches_with_pressure_balls", "matches_all", "active",
                "in_ranked_pool", "pool_rank", "removed_reliably_negative_shift", "listed_top10", "delivery_rate", "delivery_matches", "wins_added_per100_pressure"]
        extra = [c for c in ("sr_P", "sr_O", "runs_index_P", "dismissal_ratio_P", "boundary_rate_P", "dot_rate_P", "economy_P", "economy_O", "economy_index_P", "wicket_ratio_P", "boundary_conceded_P", "extras_per_over_P", "balls_all", "legal_all") if c in e.columns]
        out.append(e[keep + extra])
    pr = pd.concat(out, ignore_index=True)
    pr.to_csv(PACK / "player_ratings.csv", index=False, encoding="utf-8")
    return pr


# =====================================================================================================  07
def doc_07(trace_sum):
    s = ["# 07 LIMITATIONS OBSERVED IN THE ACTUAL RESULTS\n",
         "**The blueprint's list of six limitations was not available to me** (blueprint file not in the project). Part A therefore goes through the 13 limitations the project's own `report.md` section 9 states (and `exhibit_map.md` page 9), which include the blueprint-derived ones (exhibit_map 9.5, 9.6, 9.7 cite 'blueprint limitations': fielding, who faces pressure, tournament pressure). For each: does the actual result show it mattering, with a number where one exists.\n"]
    LIM = [
        ("Pressure is mostly a live chase", "YES, large", "78 of 31,263 rated pressure balls (0.25%) are in innings 1; 75.4% of pressure balls fall before over 16; 37.2% of innings-2 balls are pressure vs 0.1% of innings-1 balls (audit_stage2c.md, meta.json)."),
        ("Venue is not in the rating regression's context", "NOT TESTED", "Venue enters only through the scoring model (`env_tier`). No sensitivity variant adds a venue term. No number."),
        ("Skipped sensitivity variant; floor proxy in the grid", "YES, once", "Proxy top 10 differs from the final list by one player: Jos Buttler 9th on proxy, 11th on true floor; Gill 11th on proxy, 10th on true floor (CHANGES #39). 'No recalibration' variant NOT RUN."),
        ("Bowler sign check was amended after seeing results", "YES", "2 of 10 listed bowlers (Hasaranga economy index 94.8, Noor Ahmad 91.5) fail the original economy-only check; strict list differs by 2 names (Mujeeb Ur Rahman, Bhuvneshwar Kumar for Hasaranga, Noor Ahmad)."),
        ("No separable clutch trait", "YES, central result", "Pressure-shift split-half 0.1303 batters / 0.1495 bowlers; batter season-to-season r 0.0477 (CI -0.2294 to 0.3174); permutation p 0.062 batters, 0.048 bowlers."),
        ("Team scores are rebuilt from partly missing extras", "YES, small", "External check: mean error -1.00 runs, 29 of 30 totals within 5, worst single error -8 (match 45505); chase totals about 2 low; margin error median 0, p95 4.0, max 8.0 (audit_stage1.md). 59 bye rows imputed 1 run."),
        ("Win probability is team-neutral", "YES for non-rated groups", "Start-of-chase over-prediction: associates +8.7 pts (52 matches), A-teams +5.4 pts (30), full-member T20I +2.3 (392), IPL -0.1 (366) (audit_stage2.md). Associate/A-team matches do not rate players, but they fit the scoring model."),
        ("Calibration tolerance is as wide as its sampling noise", "YES", "Max decile gap 0.0418 (innings 1) and 0.0233 (innings 2) vs limit 0.05; 95% bootstrap intervals on the gaps are about +/-0.05. Innings-1 bins above 0.8 over-predict by 6.5 to 8.8 points."),
        ("Fielding, partnerships, role are invisible; who faces pressure is not random", "PLAUSIBLY, not measurable here", "Spinners are 8 of 10 listed bowlers vs 20 of 55 in the pool, while spinners bowl 35.0% of pressure balls vs 37.2% of live balls (step3_reports.md (d)); that gap is a selection effect that role/captaincy could explain. No fielding data."),
        ("Tournament pressure untested", "YES", f"No World Cup in the data; knockout matches: {int(H.MFLAGS[H.MFLAGS.clean & (H.MFLAGS.knock_out == 1)].shape[0])} of the 808 clean matches ({int((H.MFLAGS.knock_out == 1).sum())} in the whole matches file, the figure exhibit_map.md cites)."),
        ("Small pools", "YES", "53 batters / 56 bowlers eligible; 47 / 48 after the active and negative-shift steps. Listed players are the top 10 of 47 and 48."),
        ("Heavy tails in ball values", "Small", "Batter ball values reach -14.9; capping at the 1st/99th percentile leaves both lists unchanged (overlap 10 of 10, Kendall 0.978 batters / 0.957 bowlers)."),
        ("Data quality: one chase fails the wickets reconciliation", "YES, one match", "Match 20190: result text 'won by 6 wickets', ball data 5 wickets (4 implied); named exception, ball data used."),
    ]
    s.append("## Part A. The limitations and whether the results show them\n")
    s.append(md(pd.DataFrame(LIM, columns=["limitation", "does it matter in the results?", "number / evidence (file)"])))
    s.append("\n## Part B. Extra limitations noticed during the build\n")
    s.append("1. **The list is ranked by floor, not by P(top 10).** Unlisted players with a HIGHER P(top 10) than the 10th listed player:\n")
    ex = []
    for role in ("batters", "bowlers"):
        ten = H.TOP[role].p_top10.min()
        e = H.POOL[role][~H.POOL[role].player_id.isin(H.TOP[role].player_id)]
        e = e[e.p_top10 > ten][["name", "rank", "p_top10", "floor_p10", "pressure_rating"]]
        for _, r in e.iterrows():
            ex.append(dict(role=role[:-1], name=r["name"], pool_rank=int(r["rank"]), p_top10=r.p_top10, floor_p10=r.floor_p10, rating=r.pressure_rating, lowest_listed_p_top10=ten))
    s.append(md(pd.DataFrame(ex), ".3f") if ex else "(none)")
    s.append("\n   Batters: Josh Inglis, Jos Buttler and Mitchell Marsh have a higher P(top 10) than Shubman Gill (0.247), and Josh Inglis (0.323) is also higher than Sai Sudharsan (0.283). This is the cost of ranking on the floor; it is the rule as run. Bowlers: none exceeds the lowest listed P(top 10) (Axar Patel 0.39).\n")
    s.append("2. **IPL-only listed players.** Sai Sudharsan, Sunil Narine and Krunal Pandya have 0 T20I pressure balls, so they are rated on one competition. Klaasen has 40 and Iyer 43 T20I pressure balls. Rating IPL-only keeps 6 of 10 batters and 8 of 10 bowlers; T20I-only keeps 6 and 7.\n")
    s.append("3. **Batters do not persist across seasons** (r = 0.048, n = 34): the list is a verdict on 2022-2026 pooled, and weighting recent seasons (2-year half-life) removes Nicholas Pooran and Shubman Gill and brings in Ishan Kishan and Virat Kohli (overlap 8 of 10).\n")
    s.append("4. **Era effects**: the impact-player rule (IPL from 2023) is in the scoring model only. No explicit era term in the rating regression.\n")
    s.append("5. **Pressure share is 20% by construction** (top 20% of live balls). Sizes and shares of 'pressure' therefore describe the chosen cutoff, not a natural quantity.\n")
    s.append("6. **The audit for the choice of C is empty.** `audit_stage2.md` has a 'Choice of C' table with no rows because C was fixed (`stage2_choices.json` `logloss` is `{}`); the evidence for the choice exists only as prose in CHANGES #5.\n")
    s.append("7. **Evidence cards print '(stable)' for every listed player**, including Gill (7 of 14 variants). The fragile rule is 'fewer than half', so 7 of 14 is not fragile, but the card label hides that he is the weakest.\n")
    s.append("## Part C. Listed players with a small pressure sample\n")
    rows = []
    for role in ("batters", "bowlers"):
        for _, r in H.TOP[role].iterrows():
            c = H.CARDS[int(r.player_id)]
            rows.append(dict(role=role[:-1], rank=int(r["rank"]), name=r["name"], pressure_balls=c["pressure_balls"], matches=c["matches_with_pressure_balls"], ipl=c["ipl_pressure_balls"], t20i=c["t20i_pressure_balls"], delivery_matches=c["delivery_matches"]))
    sm = pd.DataFrame(rows)
    s.append(f"Eligibility is 120 pressure balls over 15 matches; every listed player clears it. The smallest samples, relative to the rest of the lists, are (sorted by pressure balls):\n")
    s.append(md(sm.sort_values("pressure_balls").head(8), ".0f"))
    s.append("\nNone is below the threshold; Heinrich Klaasen (200 balls, 19 matches) is the smallest sample in the batters' list and sits at rank 1 with P(top 10) 0.99 because his baseline is very high; Noor Ahmad (207 balls, 16 matches; delivery rate 0.31 on 13 qualifying matches) is the smallest bowler sample and has the widest interval (floor 0.074 to p90 0.204).\n")
    s.append("## Part D. Results that flip when the cutoff moves\n")
    s.append("From the sensitivity grid (floor-proxy top 10 under each pressure-cutoff variant; the final list is the true-floor list, so a one-player difference exists even at the main cutoff):\n")
    rows = []
    for role in ("batters", "bowlers"):
        names = H.ALLR[role].set_index("player_id").name
        for v in ["cutoff_top10%", "cutoff_top15%", "cutoff_top25%", "cutoff_top30%", "cutoff_within_innings", "no_cutoff_log_leverage"]:
            top = set(H.VM[role].index[H.VM[role][v]])
            listed = set(H.TOP[role].player_id)
            rows.append(dict(role=role[:-1], variant=v, listed_players_out=", ".join(names[list(listed - top)]) or "none", players_in=", ".join(names[list(top - listed)]) or "none"))
    s.append(md(pd.DataFrame(rows)))
    s.append("\nSo the pressure cutoff moves at most one name at a time. The variants that move the lists most are IPL-only / T20I-only and the recency weighting, not the cutoff.\n")
    s.append("## Part E. Numbers that did not reconcile exactly\n")
    rec = []
    rec.append(("Final list vs sensitivity proxy", "Proxy 'main' top 10 puts Buttler 9th and Gill 11th; the final true-floor list has Gill 10th, Buttler 11th", "CHANGES #39; website robustness.json `proxy_note`", "disclosed, by design"))
    rec.append(("Match 13512 trace", "Stated 1-run margin vs rebuilt state: rebuilt R1 171, R2 172, anchor target 174, needing 8 off the last ball and scoring 6 (2 short, margin says 1)", "outputs/matches_clean_totals.csv; balls_state.parquet", "within the margin gate (max 8) but visible in a showcase trace"))
    rec.append(("Margin gate", "Rebuilt vs stated margin: median 0.0, p95 4.0, max 8.0 (n=395); gate allows p95 <= 6, outlier > 8", "audit_stage1.md", "passes"))
    rec.append(("Match 20190", "Wickets reconciliation 5 vs 4", "audit_stage1.md", "named exception"))
    rec.append(("Chase totals", "External check: chase totals run about 2 low; one -8 (match 45505)", "audit_stage1.md", "inside the gate"))
    rec.append(("Audit gap", "'Choice of C' table is empty", "audit_stage2.md", "documentation gap"))
    rec.append(("Raw vs recalibrated Brier", "Raw WP has slightly better Brier (0.2190 / 0.1264) than WP* (0.2193 / 0.1270) but fails the decile gate (0.0994 / 0.0601)", "audit_stage2.md", "known trade-off"))
    rec.append(("Results text vs ball data", "3 matches where result/winner are inconsistent (24822, 28334, 48610)", "audit_stage1.md Notes", "noted; ball data used"))
    s.append(md(pd.DataFrame(rec, columns=["item", "what does not reconcile", "file", "status"])))
    s.append("\nNothing here was changed or fixed. **The only item I think needs your decision** is the choice of the tight-finish example for slides (use 16662 or 13613, not 13512).\n")
    # extra diagnostic: how often does the anchored target differ from the forward target in by-runs chases
    bs = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "target", "in_rating_sample"])
    t = bs[bs.innings == 2].groupby("match_id").target.first()
    tot = pd.read_csv(OUT / "matches_clean_totals.csv").set_index("match_id")
    mf = H.MFLAGS.set_index("match_id")
    ids = [m for m in t.index if mf.loc[m, "rtype"] == "runs" and m in tot.index]
    diff = (t.loc[ids] - (tot.loc[ids, "R1"] + 1))
    s.append(f"\n**New diagnostic (computed here from `balls_state.parquet` and `matches_clean_totals.csv`):** in the {len(ids)} clean chases that were lost by runs, the anchored target differs from the forward target (rebuilt first-innings total + 1) by 0 in {int((diff == 0).sum())} matches, by 1 to 2 runs in {int(diff.abs().between(1, 2).sum())}, by 3 to 5 in {int(diff.abs().between(3, 5).sum())} and by more than 5 in {int((diff.abs() > 5).sum())} (max {int(diff.abs().max())}). This is the same quantity the margin gate measures.\n")
    W("07_LIMITATIONS_OBSERVED.md", "\n".join(s))


# =====================================================================================================  08 index
ORIG = [("stage2_calibration.png", "Win probabilities are calibrated out of sample and beat a one-feature baseline.", "Max decile gap 0.0418 (inn 1), 0.0233 (inn 2); Brier 0.2193 vs 0.2294 and 0.1270 vs 0.1490 (audit_stage2.md). Several panels (calibration, start-of-chase by target, two chase traces, distribution)."),
        ("stage3_case_studies.png", "The leverage index spikes where a cricket watcher expects it, in tight finishes, and stays flat in one-sided chases.", "Six matches: tight 13613, 13512, 16662; one-sided 19717, 40040, 15458. NOTE 13512 barely registers (peak LI 1.44) - see 03_EVIDENCE_DEFINITION.md flag."),
        ("stage3_separation.png", "Pressure balls differ from ordinary balls in the same phase: more boundaries, fewer dots, more dismissals late; fewer defensive strokes.", "Differences with 95% intervals by phase (audit_stage3.md): e.g. death dismissal +0.0208, powerplay dot -0.0453, middle runs +0.0862."),
        ("stage3_where_pressure_lives.png", "Pressure lives in the chase: innings 1 has 98 pressure balls; 75.4% of pressure balls fall before over 16.", "Left: mean LI by runs required and over (chase); centre: by wickets and over (innings 1); right: pressure share by over (audit_stage2c.md)."),
        ("stage8_ratings_scatter.png", "Pressure ratings sit almost on the baseline line, and the regression ranking is almost identical to the simple shrunk one.", "Top row: baseline vs pressure rating with 10th-90th percentile bars; bottom row: simple vs regression, Spearman 0.9696 batters, 0.9839 bowlers (audit_stage5.md)."),
        ("stage8_shift_distribution.png", "Pressure shifts are tiny and centred on zero.", "Histogram of bootstrap-mean shifts; shift SD about 0.0085 (batters), 0.0084 (bowlers) among eligible players (audit_stage4.md).")]


def doc_08(info):
    s = ["# 08 FIGURE INDEX\n",
         "All files are in `08_FIGURES/`. Colour grammar: **blue = normal, pink = pressure**. New figures (prefix `F`) are PNG at 1920 px wide plus SVG; text is sized for slides. Originals copied from `figures/` keep their names with the prefix `pipeline_` (PNG only; no SVG exists for them; `stage3_close_games.png` is replaced by F10 because it was under 1600 px).\n",
         "## Required figures and where to find them\n",
         "| required | file(s) |\n|---|---|\n"
         "| leverage heatmap (balls left x runs required) | `F01_leverage_heatmap_balls_left_x_runs_required` (new); `pipeline_stage3_where_pressure_lives.png` (original: runs required x over) |\n"
         "| calibration plot | `F02_calibration_deciles` (new, clean); `pipeline_stage2_calibration.png` (original, multi-panel) |\n"
         "| separation chart | `pipeline_stage3_separation.png` |\n"
         "| one match trace | `F03_match_trace_16662` (new); `pipeline_stage3_case_studies.png` (six matches) |\n"
         "| raw vs shrunk chart | `F04_raw_vs_shrunk` (new) |\n"
         "| batter and bowler baseline vs pressure scatter with intervals | `F05_baseline_vs_pressure_scatter` (new); `pipeline_stage8_ratings_scatter.png` (original, top row) |\n"
         "| stability chart | `F06_rank_stability` (new) |\n"
         "| sensitivity / fragile-flag table | `F07_sensitivity_fragile_table` (new) |\n"
         "| two top-10 lists, one image each | `F08_top10_batters`, `F08_top10_bowlers` (new) |\n"
         "| pressure vs ordinary paired-bar chart, league-wide | `F09_pressure_vs_ordinary_paired_bars` (new) |\n"]
    NEW = {
        "F01_leverage_heatmap_balls_left_x_runs_required": ("Pressure builds as balls and runs run out together: the pink zone is 'few runs, few balls' (and mid-chase when the ask is high).", f"Mean LI per cell, innings 2, live balls, {info['heat_balls']:,} balls in {info['heat_cells']} cells (>= 20 balls each); cutoff LI {H.THR['p80']:.3f} (pressure_thresholds.json)."),
        "F02_calibration_deciles": ("When the model says 70%, the team wins about 70% of the time, on seasons it never saw.", "Decile predicted vs observed win rate with 95% match-bootstrap intervals; largest gaps 0.0418 (innings 1), 0.0233 (innings 2) (audit_stage2.md)."),
        "F03_match_trace_16662": ("In a 1-wicket finish the leverage index stays near the cutoff for most of the chase and then climbs to 11.3 in the last over.", "Match 16662 (2022-09-07, Pakistan v Afghanistan, Pakistan won by 1 wicket): peak LI 11.31 on ball 117 (over 20); 74 of 117 chase balls are pressure balls (03_trace_summary.csv)."),
        "F04_raw_vs_shrunk": ("Raw pressure records are noisy and are pulled in by shrinkage and opposition adjustment.", "Raw mean value, simple shrunk rating and final ridge rating for the 20 listed players (06_FAIRNESS_AND_ADJUSTMENT.md)."),
        "F05_baseline_vs_pressure_scatter": ("A player's pressure rating is almost his baseline: pressure adds or removes very little.", "Pressure rating vs baseline for 53 batters and 56 bowlers with 10th-90th percentile bars (player_ratings.csv); listed players in pink."),
        "F06_rank_stability": ("The top of each list is secure; places 7 to 10 depend on the resample.", "Rank 10th to 90th percentile bars and P(top 10), P(top 20) for the 20 listed players (top10_*.csv)."),
        "F07_sensitivity_fragile_table": ("Most listed players survive almost every variant; Gill (7 of 14), Axar Patel and Krunal Pandya (10 of 14) are the least secure.", "Top-10 membership of each listed player under 14 sensitivity variants (floor proxy; sensitivity_ratings_*.csv, top10_*.csv `variants_in_top10`)."),
        "F08_top10_batters": ("The ten batters, baseline (blue) and pressure rating (pink) with 80% interval.", "top10_batters.csv: rating, baseline, floor_p10, p90 per player."),
        "F08_top10_bowlers": ("The ten bowlers, baseline (blue) and pressure rating (pink) with 80% interval.", "top10_bowlers.csv: rating, baseline, floor_p10, p90 per player."),
        "F10_close_games_vs_rest": ("Pressure concentrates in games that finished tight although margin is never an input.", "137 close matches: median peak LI 10.1 vs 1.6 (671 others); Spearman peak LI vs runs margin -0.853 (n=395) (audit_stage3.md; values re-derived and asserted equal at build time). Full-width re-render of the original stage3_close_games.png (which was 1560 px and is NOT copied)."),
        "F09_pressure_vs_ordinary_paired_bars": ("On pressure balls batters score faster (146.6 vs 139.5) but also get out more often (5.86% vs 5.09%), and bowlers concede more (economy 9.13 vs 8.67).", "website/data/league_split.json overall, raw rates for live balls of the 728 rated matches; NOT standardised by phase."),
    }
    s.append("\n## New figures\n")
    s.append("| file (PNG + SVG) | takeaway | numbers shown |\n|---|---|---|")
    for stem, _t in F.MADE:
        tk, nums = NEW[stem]
        s.append(f"| `{stem}` | {tk} | {nums} |")
    s.append("\n## Original pipeline figures (copied)\n")
    s.append("| file | takeaway | numbers shown |\n|---|---|---|")
    from PIL import Image
    for f, tk, nums in ORIG:
        w, h = Image.open(ROOT / "figures" / f).size
        note = " **(width below 1600 px)**" if w < 1600 else ""
        s.append(f"| `pipeline_{f}` ({w} x {h}){note} | {tk} | {nums} |")
    s.append("\nNote on width: all new figures are 1920 px wide. The original `stage3_close_games.png` is 1560 px wide (the only one under 1600). I did not re-render originals because that would mean re-running pipeline code; it is usable on a slide at half width or can be rebuilt from `src/stage3_prove.py`.\n")
    W("08_FIGURE_INDEX.md", "\n".join(s))


def copy_originals():
    for f, _t, _n in ORIG:
        shutil.copy2(ROOT / "figures" / f, PACK / "08_FIGURES" / f"pipeline_{f}")


# =====================================================================================================  09
def doc_09():
    idx = rd(WEB / "index.html")
    secs = re.findall(r'<section class="[^"]*" id="([\w-]+)"[^>]*>', idx)
    heads = re.findall(r'<h[12][^>]*>(.*?)</h[12]>', idx, re.S)
    heads = [re.sub(r"<[^>]+>", "", h).strip() for h in heads]
    try:
        url = subprocess.run(["git", "-C", str(WEB), "remote", "get-url", "origin"], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        url = ""
    live = "https://vanshbhandari05.github.io/pressure-room/"
    try:
        code = urllib.request.urlopen(urllib.request.Request(live, headers={"User-Agent": "handoff-pack-check"}), timeout=15).status
        status = f"HTTP {code} when checked on {TODAY} by this build"
    except Exception as e:
        status = f"NOT CHECKED ({type(e).__name__})"
    rb = H.ROBUST["roles"]
    s = ["# 09 WEBSITE (The Pressure Room)\n",
         f"- **Live URL:** {live} ({status}).\n- **Repository:** {url.replace('.git', '')} (git remote of `website/`; Pages served from branch main).\n- Not an official Rajasthan Royals or IPL page; no official logos or photos.\n"]
    s.append("## Sections as built (from `website/index.html`)\n")
    s.append("| # | section id | heading |\n|---|---|---|")
    hs = [h for h in heads]
    for i, sid in enumerate(secs):
        s.append(f"| {i + 1} | `{sid}` | {hs[i] if i < len(hs) else ''} |")
    s.append("\n**Sections dropped:** I cannot compare against the original site brief (not in the project). `website/CHANGES.md` records one dropped design idea (#23: the 'pink/blue split by role' avatars, dropped to keep the colour grammar), and `website/DATA_INVENTORY.md` section 7 lists 9 things the prompt asked for that the methodology cannot support as written (copied below). No whole section is recorded as dropped.\n")
    s.append("## Robustness headline (from `website/data/robustness.json`)\n")
    s.append(f"- Across the five pressure cutoffs (chosen top 20% plus 10/15/25/30%), **{rb['batters']['cutoff_survivors_min']} to {rb['batters']['cutoff_survivors_max']} of the final top-10 batters** and **{rb['bowlers']['cutoff_survivors_min']} to {rb['bowlers']['cutoff_survivors_max']} of the final top-10 bowlers** stay in the top 10 (on the floor-proxy lists).\n"
             f"- Variants each listed player stays in the top 10 for (of 14): batters {', '.join(f'{k}: {v}' for k, v in rb['batters']['variants_in_top10'].items())}; bowlers {', '.join(f'{k}: {v}' for k, v in rb['bowlers']['variants_in_top10'].items())} (keys are player ids).\n"
             f"- Proxy vs final: {rb['batters']['proxy_note']}\n")
    ok = []
    for role in ("batters", "bowlers"):
        j = json.load(open(WEB / "data" / f"top10_{role}.json", encoding="utf-8"))
        ids = [d["id"] for d in j["list"]]
        ok.append((role, ids == list(H.TOP[role].player_id)))
    s.append("## Confirmation: site top 10 = pipeline top 10\n")
    s.append(f"- `website/data/top10_batters.json` equals `outputs/top10_batters.csv` in order and `player_id`: **{ok[0][1]}**. `top10_bowlers.json` equals `top10_bowlers.csv`: **{ok[1][1]}**. (Rechecked by `check_handoff.py`; the site's own build asserts the same plus SHA-256 against FINAL_LOCK.md.)\n")
    s.append("## `website/data/CHECKS.md` (copied)\n")
    s.append(rd(WEB / "data" / "CHECKS.md"))
    s.append("\n## `website/DATA_INVENTORY.md` (copied)\n")
    s.append(rd(WEB / "DATA_INVENTORY.md"))
    W("09_WEBSITE.md", "\n".join(s))


# =====================================================================================================  10
NUMS = []


def N(label, file, pattern, unit, loc, safe=True, note="", group=1, nth=0, display=None, flags=0):
    t = rd(ROOT / file)
    ms = list(re.finditer(pattern, t, flags))
    assert ms, (label, pattern)
    m = ms[nth]
    raw = m.group(group)
    v = float(raw.replace(",", ""))
    v = int(v) if ("." not in raw) else v
    NUMS.append(dict(label=label, value=v, display=display if display is not None else raw, unit=unit, source_file=file, source_location=loc, source_text=m.group(0), safe_for_slide=safe, context_note=note))


def D(label, value, unit, file, loc, recompute, safe, note):
    NUMS.append(dict(label=label, value=value, display=str(value), unit=unit, source_file=file, source_location=loc, source_text="", derived=True, recompute=recompute, safe_for_slide=safe, context_note=note))


def deck_numbers():
    NUMS.clear()
    N("Raw rows in the supplied ball-by-ball file", "outputs/audit_stage1.md", r"Raw file: ([\d,]+) rows", "rows", "first line", True, "Organiser data; count only.")
    N("Matches in the supplied file", "outputs/audit_stage1.md", r"Raw file: [\d,]+ rows, ([\d,]+) matches", "matches", "first line")
    N("Balls analysed (clean)", "outputs/audit_stage1.md", r"Output table: ([\d,]+) rows", "balls", "first line; also website/data/meta.json balls_analysed", True, "After removing super overs, no-result, rain-affected and truncated matches.")
    N("Clean matches", "outputs/audit_stage1.md", r"Output table: [\d,]+ rows, ([\d,]+) matches", "matches", "first line")
    N("Matches in the rating sample", "outputs/audit_stage1.md", r"\(([\d,]+) in the rating sample\)", "matches", "first line", True, "IPL + full-member T20I, no rain or truncation; 7 ties kept.")
    N("Rating-sample matches: IPL", "website/data/meta.json", r'"matches_rated_ipl": (\d+)', "matches", "matches_rated_ipl")
    N("Rating-sample matches: T20I (full-member)", "website/data/meta.json", r'"matches_rated_t20i": (\d+)', "matches", "matches_rated_t20i")
    N("Rating-sample ties kept", "config.yaml", r"expected_rating_sample: \{IPL: \d+, T20I: \d+, ties: (\d+)\}", "matches", "gates.expected_rating_sample", True, "Gate value; the audit confirms 'ties kept: 7'.")
    N("First season covered", "website/data/meta.json", r'"seasons": \[\s*(\d{4})', "year", "meta.json seasons[0]", True, "Matches 2022 onwards.")
    N("Last season covered", "website/data/meta.json", r'(\d{4})\s*\],\s*"competitions"', "year", "meta.json seasons[-1]", True, "2026 season data included.")
    N("Players eligible, batters", "website/data/meta.json", r'"eligible_batters": (\d+)', "players", "meta.json eligible_batters", True, "120 pressure balls and 15 matches.")
    N("Players eligible, bowlers", "website/data/meta.json", r'"eligible_bowlers": (\d+)', "players", "meta.json eligible_bowlers")
    N("Eligible and active, batters", "outputs/audit_stage5.md", r"\| batters \|\s+53 \|\s+(\d+) \|", "players", "Eligibility table", True, "Active = any appearance in 2025 or 2026.")
    N("Eligible and active, bowlers", "outputs/audit_stage5.md", r"\| bowlers \|\s+56 \|\s+(\d+) \|", "players", "Eligibility table")
    N("Minimum pressure balls to be eligible", "config.yaml", r"min_pressure_balls: (\d+)", "balls", "rating.eligibility")
    N("Minimum matches to be eligible", "config.yaml", r"min_matches: (\d+)", "matches", "rating.eligibility")
    N("Live balls in rated matches", "website/data/meta.json", r'"live_balls_rated": (\d+)', "balls", "meta.json live_balls_rated", display="156,062")
    N("Pressure balls in rated matches", "website/data/meta.json", r'"pressure_balls_rated": (\d+)', "balls", "meta.json pressure_balls_rated", display="31,263")
    N("Pressure share of live balls", "outputs/audit_stage2c.md", r"([\d.]+)% of live balls", "%", "first paragraph", True, "By construction: the top 20% of live balls.")
    N("Pressure cutoff (leverage index)", "outputs/pressure_thresholds.json", r'"p80": ([\d.]+)', "LI (average live ball = 1)", "pressure_thresholds.json p80", True, "Round to 1.21 on a slide.", display="1.207")
    N("Pressure cutoff percentile", "config.yaml", r"pressure_quantile: ([\d.]+)", "quantile", "pressure.pressure_quantile", True, "0.80 = the 80th percentile of live balls.")
    N("Live-ball lower bound (WP*)", "config.yaml", r"live_low: ([\d.]+)", "probability", "pressure.live_low")
    N("Live-ball upper bound (WP*)", "config.yaml", r"live_high: ([\d.]+)", "probability", "pressure.live_high")
    N("Pressure balls in innings 1 (rated matches)", "website/data/meta.json", r'"pressure_balls_innings1_rated": (\d+)', "balls", "meta.json", False, "Needs context: shows pressure is almost entirely a live chase.")
    N("Pressure balls in innings 2 (rated matches)", "website/data/meta.json", r'"pressure_balls_innings2_rated": (\d+)', "balls", "meta.json", False, "Needs context.", display="31,185")
    N("Share of pressure balls before over 16", "outputs/audit_stage2c.md", r"Pressure balls outside overs 16-20: ([\d.]+)%", "%", "first paragraph", False, "Needs context: pressure is not just death overs.")
    N("Calibration slope, innings 1", "outputs/audit_stage2.md", r"\|\s+1\.0000 \|\s+-0\.0468 \|\s+([\d.]+) \|", "slope", "Recalibration table", False, "Technical; below 1 = raw model over-confident.")
    N("Calibration slope, innings 2", "outputs/audit_stage2.md", r"\|\s+2\.0000 \|\s+0\.1526 \|\s+([\d.]+) \|", "slope", "Recalibration table", False, "Technical.")
    N("Brier score, final model, innings 1", "outputs/audit_stage2.md", r"inn1: WP\* ([\d.]+) vs baseline [\d.]+", "Brier", "Stage 2 gate row", True, "Lower is better; baseline 0.2294.")
    N("Brier score, one-feature baseline, innings 1", "outputs/audit_stage2.md", r"inn1: WP\* [\d.]+ vs baseline ([\d.]+)", "Brier", "Stage 2 gate row")
    N("Brier score, final model, innings 2", "outputs/audit_stage2.md", r"inn2: WP\* ([\d.]+) vs baseline [\d.]+", "Brier", "Stage 2 gate row", True, "Baseline 0.1490.")
    N("Brier score, one-feature baseline, innings 2", "outputs/audit_stage2.md", r"inn2: WP\* [\d.]+ vs baseline ([\d.]+)", "Brier", "Stage 2 gate row")
    N("Largest decile calibration gap, innings 1", "outputs/audit_stage2.md", r"innings 1 \(WP\*, LOSO\)\s*\| PASS\s*\| max \|pred - obs\| = ([\d.]+)", "probability", "Stage 2 gates", False, "Needs context: 95% intervals on the gaps are about +/-0.05.")
    N("Largest decile calibration gap, innings 2", "outputs/audit_stage2.md", r"innings 2 \(WP\*, LOSO\)\s*\| PASS\s*\| max \|pred - obs\| = ([\d.]+)", "probability", "Stage 2 gates", False, "Needs context.")
    N("Close matches (tie, <=10 runs, <=3 wickets)", "outputs/audit_stage3.md", r"Matches classed close: (\d+) of \d+", "matches", "Close games section", True, "Out of 808 clean matches.")
    N("Median peak leverage, close matches", "outputs/audit_stage3.md", r"\| True\s+\|\s+137 \|\s+([\d.]+) \|", "LI", "Close games table", True, "Median over the 137 close matches.", display="10.1")
    N("Median peak leverage, all other matches", "outputs/audit_stage3.md", r"\| False\s+\|\s+671 \|\s+([\d.]+) \|", "LI", "Close games table", True, "Median over the 671 other matches.", display="1.6")
    N("Rank correlation, peak leverage vs winning margin", "outputs/audit_stage3.md", r"n=395\): (-[\d.]+)", "Spearman", "Close games section", True, "Wins by runs, n = 395.")
    N("Rank correlation with the published pressure index (live chase balls)", "outputs/audit_stage3.md", r"live chase balls ([\d.]+)", "Spearman", "Benchmark agreement", False, "Needs context: moderate agreement; the index's resources term is substituted (CHANGES #14).")
    N("Dismissal-rate difference at the death, pressure minus ordinary", "outputs/audit_stage3.md", r"\| death \(16-20\)\s+\| dismissal\s+\|\s+([\d.]+) \|", "rate (0.0208 = 2.1 points)", "Outcome shift table", True, "Interval 0.0096 to 0.0315.")
    N("Dot-ball difference in the powerplay, pressure minus ordinary", "outputs/audit_stage3.md", r"\| powerplay \(1-6\)\s+\| dot\s+\|\s+(-[\d.]+) \|", "rate (-0.0453 = -4.5 points)", "Outcome shift table", True, "Interval -0.0564 to -0.0311.")
    N("Strike rate on pressure balls, league-wide", "website/data/league_split.json", r'"pressure":\s*\{\s*"balls":\s*\d+,\s*"deliveries":\s*\d+,\s*"sr":\s*([\d.]+)', "runs per 100 balls", "league_split.json overall.pressure.sr", False, "Raw, not standardised by phase.")
    N("Strike rate on ordinary live balls, league-wide", "website/data/league_split.json", r'"normal":\s*\{\s*"balls":\s*\d+,\s*"deliveries":\s*\d+,\s*"sr":\s*([\d.]+)', "runs per 100 balls", "league_split.json overall.normal.sr", False, "Raw, not standardised.")
    N("Economy on pressure balls, league-wide", "website/data/league_split.json", r'"pressure":\s*\{\s*"balls":\s*\d+,\s*"deliveries":\s*\d+,\s*"sr":\s*[\d.]+,\s*"dismissal_pct":\s*[\d.]+,\s*"dot_pct":\s*[\d.]+,\s*"boundary_pct":\s*[\d.]+,\s*"economy":\s*([\d.]+)', "runs per over", "league_split.json overall.pressure.economy", False, "Raw.")
    N("Economy on ordinary live balls, league-wide", "website/data/league_split.json", r'"normal":\s*\{\s*"balls":\s*\d+,\s*"deliveries":\s*\d+,\s*"sr":\s*[\d.]+,\s*"dismissal_pct":\s*[\d.]+,\s*"dot_pct":\s*[\d.]+,\s*"boundary_pct":\s*[\d.]+,\s*"economy":\s*([\d.]+)', "runs per over", "league_split.json overall.normal.economy", False, "Raw.")
    N("Penalty on baselines (lambda_B)", "outputs/stage4_choices.json", r'"lambda_B": (\d+)', "penalty", "stage4_choices.json", False, "Technical.")
    N("Penalty on pressure shifts (lambda_C)", "outputs/stage4_choices.json", r'"lambda_C": (\d+)', "penalty", "stage4_choices.json", False, "Technical: 10x the baseline penalty.")
    N("Bootstrap resamples", "website/data/meta.json", r'"bootstrap_n": (\d+)', "resamples", "meta.json params.bootstrap_n", True, "Whole-match resamples.")
    N("Rank correlation, baseline vs strike rate (batters)", "outputs/audit_stage4.md", r"rho = ([\d.]+) \(>= 0\.5\)", "Spearman", "Stage 4 gates", True, "n = 53.")
    N("Rank correlation, baseline vs economy (bowlers)", "outputs/audit_stage4.md", r"rho = (-[\d.]+) \(<= -0\.4\)", "Spearman", "Stage 4 gates", True, "n = 56; negative is good for economy.")
    N("Regression vs simple shrunk ranking, batters", "outputs/audit_stage5.md", r"\| batters \|\s+(0\.9696) \|", "Spearman", "Cross-check table", True, "Opposition adjustment barely changes the ranking.")
    N("Regression vs simple shrunk ranking, bowlers", "outputs/audit_stage5.md", r"\| bowlers \|\s+(0\.9839) \|", "Spearman", "Cross-check table")
    N("HEADLINE reliability: split-half of pressure rating, batters", "outputs/audit_stage6.md", r"\| batters \| pressure rating \|\s+[\d.]+ \|\s+([\d.]+) \|", "Spearman-Brown r", "Split-half table", True, "Show as 0.54. Must be shown WITH the next two rows.")
    N("Split-half of pressure rating, bowlers", "outputs/audit_stage6.md", r"\| bowlers \| pressure rating \|\s+[\d.]+ \|\s+([\d.]+) \|", "Spearman-Brown r", "Split-half table", True, "Show as 0.66.")
    N("Split-half of baseline alone, batters", "outputs/audit_stage6.md", r"\| batters \| baseline\s+\|\s+[\d.]+ \|\s+([\d.]+) \|", "Spearman-Brown r", "Split-half table", False, "Needs context: baseline alone is as reliable, so the rating's repeatability is general quality.")
    N("Split-half of baseline alone, bowlers", "outputs/audit_stage6.md", r"\| bowlers \| baseline\s+\|\s+[\d.]+ \|\s+([\d.]+) \|", "Spearman-Brown r", "Split-half table", False, "Needs context.")
    N("Split-half of pressure SHIFT alone, batters", "outputs/audit_stage6.md", r"\| batters \| pressure shift\s+\|\s+[\d.]+ \|\s+([\d.]+) \|", "Spearman-Brown r", "Split-half table", True, "Show as 0.13: the 'no separable clutch trait' number.")
    N("Split-half of pressure SHIFT alone, bowlers", "outputs/audit_stage6.md", r"\| bowlers \| pressure shift\s+\|\s+[\d.]+ \|\s+([\d.]+) \|", "Spearman-Brown r", "Split-half table", True, "Show as 0.15.")
    N("Season-to-season correlation, batters", "outputs/audit_stage6.md", r"\| batters \|\s+34 \|\s+([\d.]+) \|", "Pearson r", "Season to season table", False, "Needs context: 34 players, interval -0.2294 to 0.3174.")
    N("Season-to-season correlation, bowlers", "outputs/audit_stage6.md", r"\| bowlers \|\s+37 \|\s+([\d.]+) \|", "Pearson r", "Season to season table", False, "Needs context: 37 players, interval 0.2517 to 0.7201.")
    N("Permutation test p-value, batters", "outputs/audit_stage6.md", r"\| batters \|\s+217 \|\s+[\d.]+ \|\s+[\d.]+ \|\s+[\d.]+ \|\s+([\d.]+) \|", "p", "Permutation table", False, "Needs context: not beyond the 95th percentile.")
    N("Permutation test p-value, bowlers", "outputs/audit_stage6.md", r"\| bowlers \|\s+228 \|\s+[\d.]+ \|\s+[\d.]+ \|\s+[\d.]+ \|\s+([\d.]+) \|", "p", "Permutation table", False, "Needs context: borderline.")
    N("Median top-10 overlap across sensitivity variants, batters", "outputs/audit_stage6b.md", r"\| batters \|\s+([\d.]+) \|\n\| bowlers", "players of 10", "Median overlap table", True, "14 variants; target was >= 7.", display="9")
    N("Median top-10 overlap across sensitivity variants, bowlers", "outputs/audit_stage6b.md", r"\| bowlers \|\s+([\d.]+) \|\n\nNot run", "players of 10", "Median overlap table", True, "14 variants.", display="9")
    N("Lowest top-10 overlap (IPL-only batters)", "outputs/audit_stage6b.md", r"\| batters \| IPL_only\s+\|\s+(\d+) \|", "players of 10", "Sensitivity table", False, "Needs context: rating on a different slice of the data.")
    N("Top-10 batters surviving the pressure-cutoff variants (minimum)", "website/data/robustness.json", r'"cutoff_survivors_min":(\d+)', "players of 10", "robustness.json roles.batters.cutoff_survivors_min", True, "Floor-proxy lists across 10/15/25/30% cutoffs.", nth=0)
    N("Top-10 bowlers surviving the pressure-cutoff variants (minimum)", "website/data/robustness.json", r'"cutoff_survivors_min":(\d+)', "players of 10", "robustness.json roles.bowlers.cutoff_survivors_min", True, "Floor-proxy lists across 10/15/25/30% cutoffs.", nth=1)
    D("Listed batters in the top 10 under ALL 14 sensitivity variants", int((H.TOP["batters"].variants_in_top10 == 14).sum()), "players of 10", "outputs/top10_batters.csv", "column variants_in_top10 == 14", {"csv": "outputs/top10_batters.csv", "col": "variants_in_top10", "op": "count_eq", "arg": 14}, True, "Suryakumar Yadav and Tilak Varma.")
    D("Listed bowlers in the top 10 under ALL 14 sensitivity variants", int((H.TOP["bowlers"].variants_in_top10 == 14).sum()), "players of 10", "outputs/top10_bowlers.csv", "column variants_in_top10 == 14", {"csv": "outputs/top10_bowlers.csv", "col": "variants_in_top10", "op": "count_eq", "arg": 14}, True, "Kuldeep, Rashid, Varun, Hazlewood, Hasaranga.")
    D("Listed batters in the top 10 under at least 12 of 14 variants", int((H.TOP["batters"].variants_in_top10 >= 12).sum()), "players of 10", "outputs/top10_batters.csv", "column variants_in_top10 >= 12", {"csv": "outputs/top10_batters.csv", "col": "variants_in_top10", "op": "count_ge", "arg": 12}, True, "Pooran (11) and Gill (7) are the exceptions.")
    D("Listed bowlers in the top 10 under at least 12 of 14 variants", int((H.TOP["bowlers"].variants_in_top10 >= 12).sum()), "players of 10", "outputs/top10_bowlers.csv", "column variants_in_top10 >= 12", {"csv": "outputs/top10_bowlers.csv", "col": "variants_in_top10", "op": "count_ge", "arg": 12}, True, "Axar Patel and Krunal Pandya (10 each) are the exceptions.")
    N("Players removed for a reliably negative pressure shift, batters", "outputs/audit_stage7.md", r"Removed for a reliably negative shift: (\d+)\.", "players", "Stage 7 audit", True, "Shift 90th percentile below zero.", nth=0)
    N("Players removed for a reliably negative pressure shift, bowlers", "outputs/audit_stage7.md", r"Removed for a reliably negative shift: (\d+)\.", "players", "Stage 7 audit", True, "", nth=1)
    N("Spinners among the 10 listed bowlers", "outputs/step3_summary.json", r'"spinners_listed": (\d+)', "players of 10", "step3_summary.json", True, "WOW (bowlers): 8 of 10 are spinners vs 20 of 55 in the eligible, active pool; spinners bowl 35.0% of pressure balls vs 37.2% of live balls.")
    N("Spinners in the eligible, active bowler pool", "outputs/step3_summary.json", r'"spinners_pool": (\d+)', "players of 55", "step3_summary.json", True, "")
    N("Shreyas Iyer strike rate on pressure balls", "outputs/evidence_cards.md", r"Shreyas Iyer \(id 3647[^\n]*\n(?:[^\n]*\n){3}- Cricket numbers: strike rate ([\d.]+) pressure", "runs per 100 balls", "evidence card, Batter #6", False, "WOW (batters): largest pressure uplift among the 10 listed batters. Small sample: 298 pressure balls, 20 matches. Pair with the next row.")
    N("Shreyas Iyer strike rate on ordinary balls", "outputs/evidence_cards.md", r"Shreyas Iyer \(id 3647[^\n]*\n(?:[^\n]*\n){3}- Cricket numbers: strike rate [\d.]+ pressure vs ([\d.]+) ordinary", "runs per 100 balls", "evidence card, Batter #6", False, "Pair with the previous row.")
    N("Krunal Pandya economy on pressure balls", "outputs/evidence_cards.md", r"Krunal Pandya \(id 4219[^\n]*\n(?:[^\n]*\n){3}- Cricket numbers: economy ([\d.]+) pressure", "runs per over", "evidence card, Bowler #10", False, "Best improvement under pressure among listed bowlers. 247 balls, 18 matches. Pair with the next row.")
    N("Krunal Pandya economy on ordinary balls", "outputs/evidence_cards.md", r"Krunal Pandya \(id 4219[^\n]*\n(?:[^\n]*\n){3}- Cricket numbers: economy [\d.]+ pressure vs ([\d.]+) ordinary", "runs per over", "evidence card, Bowler #10", False, "Pair with the previous row.")
    N("Klaasen pressure rating (batter #1 by floor)", "outputs/top10_batters.csv", r"^1,4260,Heinrich Klaasen,[^,]*,([\d.]+)", "rating per ball", "top10_batters.csv row 1 pressure_rating", False, "Show as 0.245. Ranking is by floor (0.197), not rating; Suryakumar Yadav's rating is slightly higher (0.248).", display="0.245", flags=re.M)
    N("Narine pressure rating (bowler #1 by floor)", "outputs/top10_bowlers.csv", r"^1,781,Sunil Narine,[^,]*,([\d.]+)", "rating per ball", "top10_bowlers.csv row 1 pressure_rating", False, "Show as 0.198.", display="0.198", flags=re.M)
    N("Public-scorecard check: totals within 5 runs", "outputs/audit_stage1.md", r"(29) of 30 within 5", "totals of 30", "external totals check", True, "Mean error -1.00 runs.")
    return NUMS


def doc_10():
    nums = deck_numbers()
    nums = [n for n in nums if n]
    json.dump(nums, open(PACK / "10_NUMBERS_FOR_DECK.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    s = ["# 10 NUMBERS FOR THE DECK\n",
         "Machine-readable twin: `10_NUMBERS_FOR_DECK.json` (fields: label, value, unit, source_file, source_location, plus `display` (how to show it), `source_text` (the exact text in the source file the value was read from), `safe_for_slide`, `context_note`). `check_handoff.py` re-opens every source file and verifies that `source_text` is still in it and contains the value (rows marked derived are recomputed from the named CSV).\n",
         "**Safe** = can stand alone on a slide. **Needs context** = true but misleading without the stated caveat; keep the caveat on the slide or in the notes.\n"]
    for flag, title in ((True, "Safe to show on a slide"), (False, "Needs context before it goes on a slide")):
        rows = [dict(label=n["label"], value=n["display"], unit=n["unit"], source=f"{n['source_file']} ({n['source_location']})", note=n["context_note"]) for n in nums if n["safe_for_slide"] == flag]
        s.append(f"## {title}\n")
        s.append(md(pd.DataFrame(rows)))
        s.append("")
    s.append("## The two 'wow' insights (taken straight from the results)\n")
    s.append("- **Bowlers:** 8 of the 10 listed bowlers are spinners (20 of the 55 in the eligible, active pool are), source `outputs/step3_summary.json`. Honest context: spinners bowl 35.0% of pressure balls vs 37.2% of live balls, so this is not because spinners face more pressure; role/captaincy selection is not controlled.\n"
             "- **Batters:** Shreyas Iyer's strike rate rises from 148.2 on ordinary balls to 172.8 on pressure balls (`outputs/evidence_cards.md`), the largest uplift among the 10 listed batters. Honest context: 298 pressure balls in 20 matches; the reliability work says a separable clutch trait is not measurable (shift split-half 0.13), so present it as 'he scored fast when it mattered', not 'he is clutch'.\n")
    W("10_NUMBERS_FOR_DECK.md", "\n".join(s))
    return nums


# =====================================================================================================  11
def doc_11(trace_sum, sur):
    t10, b10 = H.TOP["batters"], H.TOP["bowlers"]
    buttler = H.POOL["batters"].set_index("player_id").loc[813]
    gill_floor = t10.floor_p10.iloc[-1]
    s = ["# 11 STORY BEATS: seven findings that make the strongest presentation, from the results only\n",
         "Each beat: one-sentence finding, the supporting number (with source), the figure or table that shows it, and a one-line honest caveat. Order is a suggested running order.\n"]
    beats = [
        ("1. How pressure was defined, and why",
         "Pressure is how far the next ball can swing the match: we measure the expected change in win probability on the next ball, and call the top 20% of live balls 'pressure balls'.",
         f"31,263 pressure balls out of 156,062 live balls in 728 matches (20.0%); cutoff LI {H.THR['p80']:.3f} where an average live ball = 1 (website/data/meta.json; outputs/pressure_thresholds.json).",
         "F01 leverage heatmap; F03 match trace (16662).",
         "Under the pooled cutoff, pressure is almost entirely a live chase: 78 pressure balls in innings 1, and 75.4% of pressure balls come before over 16."),
        ("2. The proof it separates real situations",
         "Balls we call pressure behave differently from ordinary balls in the same phase, and the index spikes in games that finished tight although the margin is never an input.",
         "Death-over dismissal rate +2.1 points (interval +1.0 to +3.1); powerplay dot balls -4.5 points; close matches median peak LI 10.1 vs 1.6; Spearman -0.853 between peak LI and winning margin (audit_stage3.md).",
         "pipeline_stage3_separation.png; pipeline_stage3_close_games.png; 03_EVIDENCE_DEFINITION.md tables.",
         "Agreement with the published pressure index is only moderate (Spearman 0.328), and one of the three auto-picked 'tight' trace matches (13512) barely registers; use 16662 or 13613."),
        ("3. Batters: the main surprise",
         f"The batters' list is ranked by a conservative floor, so the last places are a coin-toss: Shubman Gill takes 10th by {gill_floor - buttler.floor_p10:.4f} of floor over Jos Buttler, and Sai Sudharsan and Gill finish in the top 10 in only 28% and 25% of resamples.",
         f"Gill floor {gill_floor:.4f} vs Buttler {buttler.floor_p10:.4f}; P(top 10): Sudharsan {t10[t10.player_id == 23450].p_top10.iloc[0]:.3f}, Gill {t10[t10.player_id == 6288].p_top10.iloc[0]:.3f} (top10_batters.csv; eligible_table_batters.csv).",
         "F06 rank stability; F07 sensitivity table.",
         "Gill is in the top 10 under only 7 of 14 sensitivity variants; Inglis, Buttler and Marsh have a higher P(top 10) than he does but a lower floor."),
        ("4. Bowlers: the main surprise",
         "Eight of the ten best pressure bowlers are spinners, and Sunil Narine tops the list.",
         "8 of 10 listed are spinners vs 20 of 55 in the pool; spinners bowl 35.0% of pressure balls vs 37.2% of live balls (step3_summary.json; step3_reports.md (d)). Narine: rating 0.198, floor 0.153, P(top 10) 0.983 (top10_bowlers.csv).",
         "F08 top-10 bowlers image; 05_PLAYER_CARDS.md.",
         "Jasprit Bumrah is listed on economy (index 117) but his wicket ratio is 0.59 and his net value is about +5 runs (interval -68 to +86; step2_bowler_net.md); Noor Ahmad's delivery rate is only 0.31."),
        ("5. The reliability finding (lead with this honestly)",
         "The ratings measure proven quality in live, high-leverage situations; a separate clutch trait is not reliably measurable in this data.",
         "Split-half: pressure rating 0.536 batters / 0.662 bowlers, but baseline alone 0.531 / 0.662 and pressure shift alone 0.130 / 0.150; season-to-season r 0.048 batters (CI -0.229 to 0.317, n 34) vs 0.511 bowlers (CI 0.252 to 0.720, n 37) (audit_stage6.md).",
         "04_EVIDENCE_RELIABILITY.md section 1 to 3; pipeline_stage8_shift_distribution.png; F05 scatter.",
         "Batter ratings did not persist across 2022-24 vs 2025-26 (r = 0.05), so the batters' list is a verdict on the pooled record, not a forecast."),
        ("6. Robustness: the lists barely move",
         "Across 14 reasonable alternative ways of doing the analysis, a median 9 of the top 10 stay in for both lists.",
         "Median overlap 9 (batters) and 9 (bowlers); 5 of 10 bowlers and 2 of 10 batters survive all 14 variants; the pressure cutoff alone moves at most one name (sensitivity.csv; audit_stage6b.md).",
         "F07 sensitivity table; 04_EVIDENCE_RELIABILITY.md section 8.",
         "The lowest overlaps (6 of 10) come from rating on IPL-only or T20I-only data, and the 'no recalibration' variant was not run."),
        ("7. The single most important limitation",
         "'Pressure' here is essentially a live run chase, so the ratings are ratings of performance under chase pressure.",
         "78 of 31,263 pressure balls are in innings 1 (0.25%); 37.2% of innings-2 balls vs 0.1% of innings-1 balls are pressure balls (audit_stage2c.md; meta.json).",
         "pipeline_stage3_where_pressure_lives.png; F01.",
         "Defending-side pressure in the first innings is almost invisible by construction; a within-innings cutoff (a tested variant) keeps 9 of 10 on both lists."),
        ("8. (Optional) What we changed after seeing results, stated upfront",
         "We amended one rule after seeing results, and we show both versions.",
         "Original bowler sign check (economy index > 100 only) fails Wanindu Hasaranga (94.8) and Noor Ahmad (91.5); amended to 'economy index > 100 OR wicket ratio > 1'; strict list swaps in Mujeeb Ur Rahman and Bhuvneshwar Kumar (strict_rule_bowlers.csv).",
         "00_DEVIATIONS.md Part A; report appendix A.",
         "It is post hoc by definition; the ranking itself was not changed."),
    ]
    for ttl, finding, num, fig, cav in beats:
        s.append(f"## {ttl}\n")
        s.append(f"- **Finding:** {finding}\n- **Supporting number:** {num}\n- **Figure / table:** {fig}\n- **Honest caveat:** {cav}\n")
    W("11_STORY_BEATS.md", "\n".join(s))


# =====================================================================================================  12
def doc_12():
    sub = pd.read_csv(ROOT / "submission_sheet.csv")
    s = ["# 12 UNSTOP ENTRIES: exactly what to type into the dropdowns\n",
         "Source: `outputs/top10_*.csv` (ranking), `submission_sheet.csv` (project root, written by `src/finalize.py`) and `competition_team_player_mapping.csv` (display name as the mapping file spells it; the mapping file itself is NOT in this pack). Match by `player_id` and team, not name alone.\n",
         "**Status of the Unstop typing: NOT CONFIRMED.** I cannot see Unstop, so I cannot say what was typed or what the dropdown shows. Tick the 'typed' column yourself.\n"]
    for role in ("batters", "bowlers"):
        t = H.TOP[role]
        rows = []
        for _, r in t.iterrows():
            pid = int(r.player_id)
            srow = sub[(sub.list == role[:-1]) & (sub["rank"] == r["rank"])].iloc[0]
            assert int(srow.player_id) == pid
            disp = H.MAP_NAME.get(pid, "")
            warn = ""
            if bool(r.duplicate_name):
                warn = f"DUPLICATE NAME: another player_id {srow.other_id_with_same_name} has the same name. Pick the {r.teams} one (id {pid})."
            rows.append(dict(rank=int(r["rank"]), player_id=pid, display_name_in_mapping_file=disp, name_in_pipeline=r["name"], team=r.teams, duplicate_name_warning=warn, typed_into_unstop="(you)"))
        s.append(f"## Top 10 {role}\n")
        s.append(md(pd.DataFrame(rows)))
        s.append("")
    s.append("Display-name equality: for all 20 players the mapping-file name equals the pipeline name (checked at build time).\n")
    for role in ("batters", "bowlers"):
        for _, r in H.TOP[role].iterrows():
            assert H.MAP_NAME.get(int(r.player_id)) == r["name"], r["name"]
    W("12_UNSTOP_ENTRIES.md", "\n".join(s))


# =====================================================================================================  copies
def copy_files():
    shutil.copy2(OUT / "top10_batters.csv", PACK / "top10_batters.csv")
    shutil.copy2(OUT / "top10_bowlers.csv", PACK / "top10_bowlers.csv")
    shutil.copy2(ROOT / "config.yaml", PACK / "config.yaml")
    shutil.copy2(OUT / "sensitivity.csv", PACK / "sensitivity.csv")
