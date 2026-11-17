"""Stage 0 (ingest, decode, audit) and Stage 1 (match state before every ball).

Run:  python -I src/stage0_1.py
Writes outputs/balls_state.parquet, outputs/matches_flags.csv, outputs/audit_stage1.md.
Every threshold comes from config.yaml. Gates are reported, never loosened.
"""
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml"))
DATA = ROOT / CFG["paths"]["data_dir"]
OUT = ROOT / CFG["paths"]["out_dir"]
OUT.mkdir(exist_ok=True)
G = CFG["gates"]
gates = []          # (name, passed, detail)
notes = []          # free-text findings for the audit file


def gate(name, ok, detail):
    gates.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + " | " + detail)


def md(df, **kw):
    return df.to_markdown(index=kw.get("index", False))


# ------------------------------------------------------------------ Stage 0
b = pd.read_csv(DATA / "ball_by_ball.csv", low_memory=False)
m = pd.read_csv(DATA / "matches.csv")
comp = pd.read_csv(DATA / "competitions.csv")

gate("columns", len(b.columns) == CFG["expected_ball_columns"], f"{len(b.columns)} columns")
dups = b.duplicated(["match_id", "innings", "innings_ball_num"]).sum()
gate("unique key", dups == 0, f"{dups} duplicate (match_id, innings, innings_ball_num)")
n_rows_raw, n_matches_raw = len(b), b.match_id.nunique()

for c in ("is_four", "is_six", "is_wicket"):
    b[c] = b[c].astype(str).str.lower().eq("true")
b["extra_kind"] = b.extras1_runs.map(CFG["extras_codes"])
assert b.extra_kind.notna().all(), "unknown extras1_runs code"
b["is_legal"] = b.extras1_runs.isin(CFG["legal_codes"])
b["is_wide"] = b.extras1_runs == CFG["wide_code"]
b["is_noball"] = b.extras1_runs.isin(CFG["noball_codes"])
b["is_penalty"] = b.extras1_runs == CFG["penalty_code"]
b = b.sort_values(["match_id", "innings", "innings_ball_num"]).reset_index(drop=True)

# match table: competition group by id, result parse, rain flag
m = m.merge(comp[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")
fm = set(CFG["competition"]["full_member_team_ids"])
C = CFG["competition"]
m["group"] = np.where(m.comp_id.isin(C["ipl_comp_ids"]), "IPL",
              np.where(m.comp_id.isin(C["ateam_comp_ids"]), "A-team",
              np.where(m.home_team_id.isin(fm) & m.away_team_id.isin(fm), "T20I-full", "T20I-assoc")))
m["year"] = pd.to_datetime(m.match_date).dt.year
bad_tag = m[(m.group.isin(["T20I-full", "T20I-assoc"])) & (m.match_format != "T20I")]
gate("competition tags", len(bad_tag) == 0, str(m.group.value_counts().to_dict()) + f"; non-T20I in T20I groups: {len(bad_tag)}")
m["impact_rule"] = (m.group == "IPL") & (m.year >= C["impact_rule_first_season"])


def parse_result(s):
    t = str(s if isinstance(s, str) else "").lower()
    if re.search(CFG["noresult_regex"], t): return "no_result", np.nan
    if re.search(CFG["tie_regex"], t): return "tie", np.nan
    x = re.search(r"(\d+)\s*runs?", t)
    if x: return "runs", float(x.group(1))
    x = re.search(r"(\d+)\s*(?:wickets?|wkts?)", t)
    if x: return "wickets", float(x.group(1))
    return "unparsed", np.nan


pr = m.result.apply(parse_result)
m["rtype"] = [p[0] for p in pr]
m["margin"] = [p[1] for p in pr]
rt = m.rtype.value_counts().to_dict()
gate("result parser",
     rt.get("runs") == G["expected_wins_by_runs"] and rt.get("wickets") == G["expected_wins_by_wickets"]
     and rt.get("tie") == G["expected_ties"] and rt.get("no_result") == G["expected_no_results"] and rt.get("unparsed", 0) == 0,
     str(rt))
m["rain"] = (m.first_inn_revised_overs.notna() | m.second_inn_revised_overs.notna() | m.revised_target.notna()
             | m.result.fillna("").str.lower().str.contains(CFG["rain_regex"]))
gate("rain flag", m.rain.sum() == G["expected_rain_matches"], f"{int(m.rain.sum())} matches flagged")
m["rain_text_only"] = m.result.fillna("").str.lower().str.contains(CFG["rain_regex"]) & ~(
    m.first_inn_revised_overs.notna() | m.second_inn_revised_overs.notna() | m.revised_target.notna())
m["rain_fields_only"] = m.rain & ~m.result.fillna("").str.lower().str.contains(CFG["rain_regex"])

# ------------------------------------------------------------------ innings summary and drops
log = []                                    # rows removed by each rule
so = b.innings > 2
log.append(("innings > 2 (super overs)", int(so.sum()), int(b[so].match_id.nunique())))
b = b[~so].copy()
mid_has_balls = set(b.match_id)
m["has_balls"] = m.match_id.isin(mid_has_balls)

inn = b.groupby(["match_id", "innings"]).agg(legal=("is_legal", "sum"), wk=("is_wicket", "sum"), rows=("is_legal", "size"),
                                              bat=("batting_team_id", "first"), lastw=("is_wicket", "last")).unstack("innings")
inn.columns = [f"{a}{i}" for a, i in inn.columns]
m = m.merge(inn, left_on="match_id", right_index=True, how="left")
m["chaser_won"] = m.win_team_id == m.bat2
m["first_won"] = m.win_team_id == m.bat1
# all out = 10 wickets, or the final ball is the ninth wicket (a batter absent)
m["allout1"] = (m.wk1 >= 10) | ((m.wk1 == 9) & m.lastw1.fillna(False).astype(bool))
m["allout2"] = (m.wk2 >= 10) | ((m.wk2 == 9) & m.lastw2.fillna(False).astype(bool))
trunc1 = (m.legal1 < CFG["innings_balls"]) & ~m.allout1
trunc2 = (m.legal2 < CFG["innings_balls"]) & ~m.allout2 & ~m.chaser_won
m["no_innings2"] = m.has_balls & m.legal2.isna()
m["truncated"] = m.has_balls & ~m.rain & (m.rtype != "no_result") & (trunc1.fillna(False) | trunc2.fillna(False) | m.no_innings2)
inconsistent = m[((m.rtype == "runs") & ~m.first_won) | ((m.rtype == "wickets") & ~m.chaser_won)]
notes.append(f"Result/winner inconsistencies (runs win not by first batter, or wickets win not by chaser): {len(inconsistent)} "
             f"{inconsistent.match_id.tolist()[:10]}")

rows_per_match = b.groupby("match_id").size()
m["rows"] = m.match_id.map(rows_per_match).fillna(0).astype(int)
m["drop_reason"] = np.where(~m.has_balls, "no ball data",
                    np.where(m.rtype == "no_result", "no result",
                    np.where(m.rain, "rain",
                    np.where(m.truncated, "truncated", ""))))
for reason in ["no result", "rain", "truncated"]:
    sel = m[(m.drop_reason == reason)]
    log.append((reason, int(sel.rows.sum()), len(sel)))
log.append(("no ball data (abandoned, 0 rows)", 0, int((m.drop_reason == "no ball data").sum())))
trunc_list = m[m.truncated][["match_id", "match_date", "group", "result", "legal1", "wk1", "legal2", "wk2"]]
flagged = sorted(m[m.truncated].match_id.tolist())
gate("truncation flag", flagged == sorted(G["expected_truncated_matches"]),
     f"flagged {flagged}; expected {sorted(G['expected_truncated_matches'])}")

clean_ids = set(m[m.drop_reason == ""].match_id)
b = b[b.match_id.isin(clean_ids)].copy()
m["clean"] = m.match_id.isin(clean_ids)
m["in_rating_sample"] = m.clean & m.group.isin(["IPL", "T20I-full"])
rs_ = m[m.in_rating_sample]
exp_rs = G["expected_rating_sample"]
gate("rating sample", (rs_.group == "IPL").sum() == exp_rs["IPL"] and (rs_.group == "T20I-full").sum() == exp_rs["T20I"]
     and (rs_.rtype == "tie").sum() == exp_rs["ties"],
     f"{len(rs_)} matches: {rs_.group.value_counts().to_dict()}, ties {int((rs_.rtype == 'tie').sum())}")

# ------------------------------------------------------------------ Stage 1: state before every ball
b = b.merge(m[["match_id", "group", "year", "match_date", "venue_id", "impact_rule", "bat1", "bat2"]], on="match_id", how="left")
g = b.groupby(["match_id", "innings"], sort=False)

# missing dismissed_player_id: batter (striker/non-striker) who stops appearing in the innings
b["dismissed_inferred"] = False
miss = b.index[b.is_wicket & b.dismissed_player_id.isna()]
for i in miss:
    r = b.loc[i]
    later = b[(b.match_id == r.match_id) & (b.innings == r.innings) & (b.innings_ball_num > r.innings_ball_num)]
    seen = set(later.striker_id) | set(later.non_striker_id)
    cand = [p for p in (r.striker_id, r.non_striker_id) if p not in seen]
    b.loc[i, "dismissed_player_id"] = cand[0] if len(cand) == 1 else r.striker_id
    b.loc[i, "dismissed_inferred"] = True
    notes.append(f"Inferred dismissed_player_id for match {r.match_id} innings {r.innings} ball {r.innings_ball_num}: "
                 f"candidates absent later = {cand}; set to {b.loc[i, 'dismissed_player_id']}")

b["legal_before"] = g.is_legal.cumsum() - b.is_legal.astype(int)
assert b.overid.between(1, 20).all(), "overid outside 1..20"
# balls_left = 120 minus legal balls bowled (exact; overid is mislabelled in match 41509)
b["balls_left"] = CFG["innings_balls"] - b.legal_before
assert b.balls_left.min() >= 1
b["wickets_lost"] = g.is_wicket.cumsum() - b.is_wicket.astype(int)

nxt_striker = g.striker_id.shift(-1)
nxt_over = g.overid.shift(-1)
has_next = nxt_striker.notna()
rot = np.where(nxt_over == b.overid, nxt_striker == b.non_striker_id, nxt_striker == b.striker_id)
b["rot_known"] = has_next & ~b.is_wicket
b["strike_rotated"] = pd.Series(rot, index=b.index) & b.rot_known

# strike-rule gate
mask = (b.extras1_runs == 6) & ~b.is_wicket & has_next
agree = ((b.runs % 2 == 1) == pd.Series(rot, index=b.index))[mask].mean()
gate("strike rule", agree >= G["strike_rule_min_agreement"], f"{agree:.5f} agreement on {int(mask.sum()):,} normal balls")

# team runs rebuild
tr = b.runs.astype(float).copy()
tr += (b.is_noball | b.is_wide).astype(int)
tr += b.extras_2_runs.fillna(0)
isbye = b.extras1_runs.isin(CFG["bye_codes"]) & (b.runs == 0)
imp = np.where(~b.rot_known, CFG["bye_unknown_rotation_runs"],
               np.where(b.strike_rotated, 1, CFG["bye_nonrotating_runs"]))
tr += np.where(isbye, imp, 0)
tr += (b.is_wide & b.strike_rotated).astype(int)
tr += np.where(b.is_penalty, CFG["penalty_runs"], 0)
b["team_runs"] = tr.astype(int)
b["bye_unknown_rot_rows"] = isbye & ~b.rot_known
notes.append(f"Bye/leg-bye rows where rotation was unknowable (final ball of innings or wicket ball), "
             f"imputed {CFG['bye_unknown_rotation_runs']} instead of {CFG['bye_nonrotating_runs']}: {int(b.bye_unknown_rot_rows.sum())}")
g = b.groupby(["match_id", "innings"], sort=False)
b["score_before"] = g.team_runs.cumsum() - b.team_runs

# match-level totals, backward anchor, target
tot = b.groupby(["match_id", "innings"]).team_runs.sum().unstack()
tot.columns = ["R1", "R2"]
last2 = b[b.innings == 2].groupby("match_id").team_runs.last().rename("last_runs")
mm = m[m.clean].merge(tot, left_on="match_id", right_index=True).merge(last2, left_on="match_id", right_index=True)
fwd = mm.R1 + 1
t_won = mm.R2 + (fwd - mm.R2).clip(lower=-(mm.last_runs.clip(lower=1) - 1), upper=0)
t_lost = mm.R2 + mm.margin + 1      # backward anchor only: runs required before ball 1 of the chase
t_tie = mm.R2 + 1
mm["target"] = np.where(mm.rtype == "wickets", t_won, np.where(mm.rtype == "runs", t_lost, t_tie)).astype(int)
b = b.merge(mm[["match_id", "target", "R1", "R2"]], on="match_id", how="left")
b["runs_required"] = np.where(b.innings == 2, b.target - b.score_before, np.nan)
b.loc[b.innings == 1, "target"] = np.nan
b["required_rate"] = b.runs_required * 6 / b.balls_left
b["batting_position"] = b.batting_order.clip(upper=CFG["batting_position_clip"])
bp = CFG["position_bands"]
b["position_band"] = np.select([b.batting_position <= bp["low"][1], b.batting_position <= bp["mid"][1]], ["1-3", "4-7"], "8+")

# env_tier: leave-one-out venue scoring rate shrunk to group-season rate, terciles within group
mt_rate = b.groupby("match_id").agg(runs=("team_runs", "sum"), balls=("is_legal", "sum"))
mm = mm.merge(mt_rate, left_on="match_id", right_index=True)
vsum = mm.groupby("venue_id")[["runs", "balls"]].transform("sum")
gs = mm.groupby(["group", "year"])[["runs", "balls"]].transform("sum")
prior = gs.runs / gs.balls
K = CFG["env_tier"]["pseudo_balls"]
mm["venue_rate"] = ((vsum.runs - mm.runs) + K * prior) / ((vsum.balls - mm.balls) + K)
mm["env_tier"] = mm.groupby("group").venue_rate.transform(
    lambda s: pd.qcut(s.rank(method="first"), CFG["env_tier"]["n_tiers"], labels=False)).astype(int)
b = b.merge(mm[["match_id", "env_tier", "venue_rate"]], on="match_id", how="left")

# ------------------------------------------------------------------ gates on clean data
legal_inn = b.groupby(["match_id", "innings"]).is_legal.sum()
gate("legal balls <= 120", legal_inn.max() <= CFG["innings_balls"], f"max {int(legal_inn.max())}")
mi = m[m.clean].set_index("match_id")
first = legal_inn.xs(1, level="innings")
first_notout = first[~mi.loc[first.index, "allout1"].astype(bool)]
bad_first = first_notout[first_notout != CFG["innings_balls"]]
gate("first innings 120 legal", len(bad_first) == 0, f"{len(first_notout)} not-bowled-out first innings; {len(bad_first)} not 120 {bad_first.to_dict()}")

ov = b[b.is_legal].groupby(["match_id", "innings", "overid"]).size().rename("legal").reset_index()
lastov = b.groupby(["match_id", "innings"]).overid.max().rename("lastov").reset_index()
ov = ov.merge(lastov, on=["match_id", "innings"])
ov_bad = ov[(ov.legal != 6) & (ov.overid != ov.lastov)]          # report only, not a gate
print(f"INFO overs without 6 legal balls (not final over): {len(ov_bad)} -> {ov_bad.values.tolist()}")
x41509 = ov[(ov.match_id == 41509) & (ov.innings == 1)][["overid", "legal"]]
notes.append("Legal balls per over, match 41509 innings 1: " + str(dict(zip(x41509.overid, x41509.legal))) +
             f"; sum = {int(x41509.legal.sum())}")

# wickets gate (chases won by wickets)
cw = mm[mm.rtype == "wickets"].copy()
cw["wk_end"] = cw.wk2
cw["expected"] = 10 - cw.margin
wk_bad = cw[cw.wk_end != cw.expected]
exc = set(G["wickets_gate_named_exceptions"])
gate("wickets gate", set(wk_bad.match_id) == exc,
     f"{len(cw) - len(wk_bad)} of {len(cw)} chases won by wickets match; failures {wk_bad.match_id.tolist()}")

# margin gate
rm = mm[mm.rtype == "runs"].copy()
rm["err"] = (rm.R1 - rm.R2) - rm.margin
med, p95 = rm.err.abs().median(), rm.err.abs().quantile(0.95)
gate("margin gate", med <= G["margin_median_abs_max"] and p95 <= G["margin_p95_abs_max"],
     f"n={len(rm)} median|err|={med} p95={p95} max={rm.err.abs().max()}")
outl = rm[rm.err.abs() > G["margin_outlier_runs"]][["match_id", "group", "result", "R1", "R2", "err"]]
gate("margin outliers", len(outl) == 0, f"{len(outl)} matches off by more than {G['margin_outlier_runs']} runs")

# chase difference: diagnostic only (one innings minus the other; blind to a common over-count)
cw["over_fwd"] = cw.R2 - (cw.R1 + 1)
n_below = int((cw.over_fwd < 0).sum()); n_over = int((cw.over_fwd > G["overshoot_diag_runs"]).sum())
chase_diag = (f"won chases n={len(cw)}: mean {cw.over_fwd.mean():.2f}, sd {cw.over_fwd.std():.2f}; below 0: {n_below}, "
              f"above {G['overshoot_diag_runs']}: {n_over}")
print("INFO chase difference:", chase_diag)

# external totals check against public scorecards (validation only)
X = CFG["external_check"]
ids = np.sort(mm.match_id.values)
pick = np.sort(np.random.default_rng(X["seed"]).choice(ids, size=X["n_matches"], replace=False))
samp = mm[mm.match_id.isin(pick)][["match_id", "match_date", "group", "home_team", "away_team", "bat1", "bat2", "R1", "R2", "result"]]
samp.to_csv(OUT / "external_check_sample.csv", index=False)
ext_path = ROOT / X["totals_file"]
ext_detail = None
if ext_path.exists():
    ext = pd.read_csv(ext_path)
    e = samp.merge(ext, on="match_id", how="left")
    if e.public_total_inn1.notna().all() and e.public_total_inn2.notna().all():
        err = pd.concat([e.R1 - e.public_total_inn1, e.R2 - e.public_total_inn2])
        within = int((err.abs() <= X["within_runs"]).sum()); mean_err = err.mean()
        ok = (X["mean_error_min"] <= mean_err <= X["mean_error_max"]) and within >= X["min_within"]
        gate("external totals", ok, f"mean error {mean_err:+.2f} (allowed {X['mean_error_min']} to {X['mean_error_max']}); "
             f"{within} of {len(err)} within {X['within_runs']} (need {X['min_within']})")
        ext_detail = e.assign(err1=e.R1 - e.public_total_inn1, err2=e.R2 - e.public_total_inn2)
    else:
        gate("external totals", False, "PENDING: totals file incomplete for the sampled matches")
else:
    gate("external totals", False, f"PENDING: {X['totals_file']} not found; sample written to outputs/external_check_sample.csv")

# ------------------------------------------------------------------ the four "still to confirm" items
# 1 truncation list  (above)
# 3 wickets gate denominator: 410 vs 406
w_all = m[(m.rtype == "wickets") & m.chaser_won & m.has_balls]
w_notext = w_all[~w_all.result.str.lower().str.contains(CFG["rain_regex"])]
extra4 = w_notext[~w_notext.match_id.isin(cw.match_id)][["match_id", "match_date", "group", "result", "drop_reason", "first_inn_revised_overs", "second_inn_revised_overs", "revised_target"]]
# 4 does 4 inflate totals?
cw_alt = cw[["match_id", "R1", "R2", "over_fwd"]]
# sensitivity of the nonrotating constant on the overshoot / below-target counts (recompute totals)
sens = []
for const in (1, 2, 4):
    d = const - CFG["bye_nonrotating_runs"]
    adj = b[b.extras1_runs.isin(CFG["bye_codes"]) & (b.runs == 0) & b.rot_known & ~b.strike_rotated].groupby(["match_id", "innings"]).size().unstack(fill_value=0)
    adj.columns = ["n1", "n2"]
    t = mm.merge(adj, left_on="match_id", right_index=True, how="left").fillna({"n1": 0, "n2": 0})
    t["R1c"] = t.R1 + d * t.n1; t["R2c"] = t.R2 + d * t.n2
    r = t[t.rtype == "runs"]; e = ((r.R1c - r.R2c) - r.margin)
    c_ = t[t.rtype == "wickets"]; of = c_.R2c - (c_.R1c + 1)
    sens.append(dict(nonrot_value=const, margin_median=e.abs().median(), margin_p95=e.abs().quantile(.95),
                     chases_below_target=int((of < 0).sum()), chases_over_by_gt5=int((of > G["overshoot_diag_runs"]).sum())))
sens = pd.DataFrame(sens)

# ------------------------------------------------------------------ write outputs
keep = ["match_id", "innings", "innings_ball_num", "overid", "over_ball_num", "group", "year", "match_date", "venue_id",
        "batting_team_id", "bowling_team_id", "striker_id", "non_striker_id", "bowler_id", "batting_order", "batting_position",
        "position_band", "runs", "is_four", "is_six", "extras1_runs", "extra_kind", "extras_2_runs", "is_legal", "is_wide", "is_noball",
        "is_penalty", "is_wicket", "dismissal_type", "dismissed_player_id", "dismissed_inferred", "stroke", "delivery_style",
        "pace_or_spin", "balls_left", "wickets_lost", "strike_rotated", "rot_known", "team_runs", "score_before", "runs_required",
        "target", "required_rate", "env_tier", "venue_rate", "impact_rule"]
b = b.merge(m[["match_id", "in_rating_sample"]], on="match_id", how="left")
b[keep + ["in_rating_sample"]].to_parquet(OUT / "balls_state.parquet", index=False)
m.drop(columns=[c for c in m.columns if c in ()]).to_csv(OUT / "matches_flags.csv", index=False)
mm[["match_id", "R1", "R2", "target", "env_tier", "venue_rate"]].to_csv(OUT / "matches_clean_totals.csv", index=False)

# ------------------------------------------------------------------ audit markdown
L = ["# Audit: Stage 0 and 1", "",
     f"Raw file: {n_rows_raw:,} rows, {n_matches_raw} matches. Output table: {len(b):,} rows, {b.match_id.nunique()} matches "
     f"({int(m.in_rating_sample.sum())} in the rating sample).", "",
     "## Gates", "", md(pd.DataFrame(gates, columns=["gate", "passed", "detail"]).assign(passed=lambda d: d.passed.map({True: "PASS", False: "FAIL"}))), "",
     "## Rows removed (applied in this order)", "", md(pd.DataFrame(log, columns=["rule", "rows removed", "matches"])), "",
     "## Matches by group", "", md(m[m.clean].group.value_counts().rename_axis("group").reset_index(name="clean matches")), "",
     "Rating sample by group: " + str(m[m.in_rating_sample].group.value_counts().to_dict()) +
     f"; ties kept: {int(((m.in_rating_sample) & (m.rtype == 'tie')).sum())}", "",
     "## Truncation flag: every flagged match", "", md(trunc_list), "",
     "## External totals check", "", ("Sample (seed %d): " % X["seed"]) + str(pick.tolist()), "",
     md(ext_detail[["match_id", "match_date", "R1", "public_total_inn1", "err1", "R2", "public_total_inn2", "err2", "source"]]) if ext_detail is not None else "PENDING", "",
     "## Chase difference (diagnostic, not a gate)", "", chase_diag, "",
     "## Overs without 6 legal balls (report only, not the final over)", "", md(ov_bad) if len(ov_bad) else "none", "",
     "## Wickets gate: 410 vs 406", "",
     f"By-wicket chases by exclusion: all {len(w_all)}; without DLS wording {len(w_notext)}; in clean sample {len(cw)}. "
     "Matches in the 410-style count but not in the clean sample:", "", md(extra4) if len(extra4) else "none", "",
     "## Does imputing 4 inflate totals?", "",
     "Rebuilt totals against the forward target (first innings + 1) in won chases, for each non-rotating bye value:", "", md(sens), "",
     f"Value used: {CFG['bye_nonrotating_runs']}. Margin cancels same-sign overcounts; the chase-vs-target counts do not.", "",
     "## Margin outliers (> %d runs)" % G["margin_outlier_runs"], "", md(outl) if len(outl) else "none", "",
     "## Wickets gate failures", "", md(wk_bad[["match_id", "result", "wk_end", "expected"]]) if len(wk_bad) else "none", "",
     "## Notes", ""] + [f"- {n}" for n in notes]
(OUT / "audit_stage1.md").write_text("\n".join(L), encoding="utf-8")
print("\nwrote", OUT / "audit_stage1.md")
sys.exit(0 if all(g_[1] for g_ in gates) else 1)

