"""Stage 4: ball values, credit split, rating regression, companion statistics, correlation gate.

Run:  python -I src/stage4_ratings.py
Writes outputs/ball_values_bat.parquet, ball_values_bowl.parquet, player_ratings.csv, stage4_choices.json, audit_stage4.md
"""
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rating_model as RM
import wp_engine as E

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
R, S3 = CFG["rating"], CFG["stage3"]
OUT = ROOT / CFG["paths"]["out_dir"]
T0 = time.time()
gates = []


def log(*a): print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)
def gate(name, ok, detail): gates.append((name, bool(ok), detail)); log(("PASS " if ok else "FAIL ") + name + " | " + detail)
def md(df, fl=".4f"): return df.to_markdown(index=False, floatfmt=fl)


def load_balls():
    b = pd.read_parquet(OUT / "balls_state.parquet")
    p = pd.read_parquet(OUT / "balls_pressure.parquet")
    b = b.merge(p, on=["match_id", "innings", "innings_ball_num"], suffixes=("", "_p"))
    mf = pd.read_csv(OUT / "matches_flags.csv")
    b = b.merge(mf[["match_id", "in_rating_sample"]], on="match_id", suffixes=("", "_m"))
    b["over"] = E.over_from_balls_left(b.balls_left)
    b["phase"] = np.select([b.over <= S3["phase_bounds"][0], b.over <= S3["phase_bounds"][1]], [0, 1], 2)
    return b


def build_values(b, sample="rating"):
    d = b[b.live]                                   # dead balls never enter values or baselines
    if sample == "rating": d = d[d.in_rating_sample]
    bands = E.Bands(CFG["scoring_model"])
    return RM.event_rows(d.reset_index(drop=True), bands.over_band)


if __name__ == "__main__":
    b = load_balls()
    bat, bowl = build_values(b)
    log(f"rating-sample live balls: {int((b.live & b.in_rating_sample).sum()):,}; batter rows {len(bat):,}; bowler rows {len(bowl):,}")
    q = bat.v.quantile([0, .001, .01, .25, .5, .75, .99, .999, 1]).round(3).to_dict()
    log("batter value v quantiles:", q)
    log("bowler value v quantiles:", bowl.v.quantile([0, .001, .01, .5, .99, .999, 1]).round(3).to_dict())

    all_bat = np.sort(np.unique(np.concatenate([bat.player.values, bowl.opp.values]))); all_bowl = np.sort(np.unique(np.concatenate([bat.opp.values, bowl.player.values])))
    Db = RM.Design(bat, all_bat, all_bowl); Dw = RM.Design(bowl, all_bowl, all_bat)
    log(f"design: batting fit {Db.X.shape}, bowling fit {Dw.X.shape}")
    res = RM.cv_select([Db, Dw], R["lambda_B_grid"], R["lambda_C_grid"], R["context_lambda"], R["cv_folds"], CFG["seed"])
    (lb, lc), best = min(res.items(), key=lambda kv: kv[1])
    log(f"CV chose lambda_B={lb}, lambda_C={lc}; held-out MSE {best:.5f}")
    cv_tbl = pd.DataFrame([{"lambda_B": k[0], "lambda_C": k[1], "cv_mse": v} for k, v in res.items()])
    lam_b_edge = lb in (R["lambda_B_grid"][0], R["lambda_B_grid"][-1]); lam_c_edge = lc in (R["lambda_C_grid"][0], R["lambda_C_grid"][-1])
    betab = Db.fit(Db.lam(lb, lc, R["context_lambda"])); betaw = Dw.fit(Dw.lam(lb, lc, R["context_lambda"]))
    Bb, Cb = Db.own(betab); Ww, Kw = Dw.own(betaw)
    bat_r = pd.DataFrame({"player_id": all_bat, "B": Bb, "C": Cb}); bowl_r = pd.DataFrame({"player_id": all_bowl, "W": Ww, "K": Kw})

    # ------------------------------------------------------------ companion statistics (live rating-sample balls, pressure vs ordinary)
    d = b[b.live & b.in_rating_sample].copy()
    d["Pn"] = np.where(d.pressure, "P", "O")
    st_out = d.is_wicket & (d.dismissed_player_id == d.striker_id) & ~d.dismissal_type.isin(list(RM.NOT_CHARGED))
    share_bat = st_out.sum() / max(d.is_wicket.sum(), 1)
    cred = d.is_wicket & d.dismissal_type.isin(list(RM.BOWLER_CREDITED)); share_bowl = cred.sum() / max(d.is_wicket.sum(), 1)
    f = d[~d.is_wide].assign(runs_=lambda x: x.runs, dism=st_out[~d.is_wide], bnd=lambda x: (x.is_four | x.is_six), dot=lambda x: (x.oc == 1), expw=lambda x: x.p_wicket * share_bat)
    g = f.groupby(["striker_id", "Pn"]).agg(balls=("runs_", "size"), runs=("runs_", "sum"), exp_runs=("exp_bat_runs", "sum"), dism=("dism", "sum"), exp_dism=("expw", "sum"), bnd=("bnd", "sum"), dot=("dot", "sum"),
                                              matches=("match_id", "nunique")).unstack("Pn")
    g.columns = [f"{a}_{c}" for a, c in g.columns]
    for s in ("P", "O"):
        g[f"sr_{s}"] = 100 * g[f"runs_{s}"] / g[f"balls_{s}"]; g[f"runs_index_{s}"] = 100 * g[f"runs_{s}"] / g[f"exp_runs_{s}"]; g[f"dismissal_ratio_{s}"] = g[f"dism_{s}"] / g[f"exp_dism_{s}"]
        g[f"boundary_rate_{s}"] = g[f"bnd_{s}"] / g[f"balls_{s}"]; g[f"dot_rate_{s}"] = g[f"dot_{s}"] / g[f"balls_{s}"]
    allb = f.groupby("striker_id").agg(balls_all=("runs_", "size"), runs_all=("runs_", "sum"), matches_all=("match_id", "nunique")); allb["sr_all"] = 100 * allb.runs_all / allb.balls_all
    bs = g.join(allb).reset_index().rename(columns={"striker_id": "player_id"})
    bat_r = bat_r.merge(bs, on="player_id", how="left")
    d["conceded"] = d.runs + (d.is_wide | d.is_noball).astype(int); d["exp_conc"] = d.exp_bat_runs + d.p_extra
    d["bw_wk"] = cred; d["exp_bw_wk"] = d.p_wicket * share_bowl; d["extra"] = (d.is_wide | d.is_noball); d["bnd"] = (d.is_four | d.is_six); d["dot"] = (d.oc == 1)
    gb = d.groupby(["bowler_id", "Pn"]).agg(deliveries=("conceded", "size"), legal=("is_legal", "sum"), conceded=("conceded", "sum"), exp_conc=("exp_conc", "sum"), wk=("bw_wk", "sum"), exp_wk=("exp_bw_wk", "sum"),
                                              dots=("dot", "sum"), bnd=("bnd", "sum"), extras=("extra", "sum"), matches=("match_id", "nunique")).unstack("Pn")
    gb.columns = [f"{a}_{c}" for a, c in gb.columns]
    for s in ("P", "O"):
        gb[f"economy_{s}"] = 6 * gb[f"conceded_{s}"] / gb[f"legal_{s}"]; gb[f"economy_index_{s}"] = 100 * gb[f"exp_conc_{s}"] / gb[f"conceded_{s}"]
        gb[f"wicket_ratio_{s}"] = gb[f"wk_{s}"] / gb[f"exp_wk_{s}"]; gb[f"dot_rate_{s}"] = gb[f"dots_{s}"] / gb[f"deliveries_{s}"]; gb[f"boundary_conceded_{s}"] = gb[f"bnd_{s}"] / gb[f"deliveries_{s}"]
        gb[f"extras_per_over_{s}"] = 6 * gb[f"extras_{s}"] / gb[f"legal_{s}"]
    alw = d.groupby("bowler_id").agg(legal_all=("is_legal", "sum"), conceded_all=("conceded", "sum"), matches_all=("match_id", "nunique")); alw["economy_all"] = 6 * alw.conceded_all / alw.legal_all
    ws = gb.join(alw).reset_index().rename(columns={"bowler_id": "player_id"})
    bowl_r = bowl_r.merge(ws, on="player_id", how="left")
    # wins added per 100 pressure balls and delivery rate
    for nm, rows, r_ in (("bat", bat, bat_r), ("bowl", bowl, bowl_r)):
        pr = rows[rows.P == 1]
        wa = pr.groupby("player").dWP0.agg(["sum", "size"]); r_["wins_added_per100_pressure"] = r_.player_id.map(100 * wa["sum"] / wa["size"])
        pm = pr.groupby(["player", "match_id"]).dWP0.agg(["sum", "size"]).query("size >= 6")
        dr = (pm["sum"] > 0).groupby(level=0).mean(); r_["delivery_rate"] = r_.player_id.map(dr); r_["delivery_matches"] = r_.player_id.map(pm.groupby(level=0).size())
        r_["pressure_rating"] = (r_["B"] + r_["C"]) if nm == "bat" else (r_["W"] + r_["K"])
    # eligibility (counts of pressure balls faced / bowled, and matches with at least one)
    E_ = R["eligibility"]

    def elig(r_, balls_col, match_col):
        n_ = r_[balls_col].fillna(0); m_ = r_[match_col].fillna(0)
        ok = (n_ >= E_["min_pressure_balls"]) & (m_ >= E_["min_matches"])
        fb = False
        if ok.sum() < E_["fallback_min_players"]:
            ok = (n_ >= E_["fallback_pressure_balls"]) & (m_ >= E_["fallback_matches"]); fb = True
        return ok, fb

    bat_r["eligible"], fb_b = elig(bat_r, "balls_P", "matches_P"); bowl_r["eligible"], fb_w = elig(bowl_r, "deliveries_P", "matches_P")
    log(f"eligible batters {int(bat_r.eligible.sum())} (fallback {fb_b}); eligible bowlers {int(bowl_r.eligible.sum())} (fallback {fb_w})")
    eb, ew = bat_r[bat_r.eligible & bat_r.sr_all.notna()], bowl_r[bowl_r.eligible & bowl_r.economy_all.notna()]
    rho_b = spearmanr(eb.B, eb.sr_all).correlation; rho_w = spearmanr(ew.W, ew.economy_all).correlation
    gate("batter baseline vs strike rate rank correlation", rho_b >= R["gate_batter_rho_min"], f"rho = {rho_b:.3f} (>= {R['gate_batter_rho_min']}), n={len(eb)}")
    gate("bowler baseline vs economy rank correlation", rho_w <= R["gate_bowler_rho_max"], f"rho = {rho_w:.3f} (<= {R['gate_bowler_rho_max']}), n={len(ew)}")

    # names
    mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv")
    names = mp.drop_duplicates("player_id").set_index("player_id").player_name
    bat_r["name"] = bat_r.player_id.map(names); bowl_r["name"] = bowl_r.player_id.map(names)
    bat.to_parquet(OUT / "ball_values_bat.parquet", index=False); bowl.to_parquet(OUT / "ball_values_bowl.parquet", index=False)
    bat_r.to_csv(OUT / "player_ratings_batters_stage4.csv", index=False); bowl_r.to_csv(OUT / "player_ratings_bowlers_stage4.csv", index=False)
    json.dump({"lambda_B": lb, "lambda_C": lc, "cv_mse": best, "fallback_batters": fb_b, "fallback_bowlers": fb_w}, open(OUT / "stage4_choices.json", "w"), indent=1)

    # summary of shrinkage
    shr = pd.DataFrame({"role": ["batters", "bowlers"], "sd_baseline": [bat_r.B.std(), bowl_r.W.std()], "sd_shift": [bat_r.C.std(), bowl_r.K.std()],
                        "sd_baseline_eligible": [eb.B.std(), ew.W.std()], "sd_shift_eligible": [eb.C.std(), ew.K.std()]})
    L = ["# Audit: Stage 4 (ball values, credit split, rating regression)", "", "## Gates", "", md(pd.DataFrame(gates, columns=["gate", "passed", "detail"]).assign(passed=lambda x: x.passed.map({True: "PASS", False: "FAIL"}))), "",
         f"Chosen penalties by 5-fold CV (whole matches held out): lambda_B = {lb}, lambda_C = {lc} (held-out MSE {best:.5f}). Penalty at grid edge: baseline {lam_b_edge}, shift {lam_c_edge}.", "",
         f"Shift penalty / baseline penalty = {lc / lb:.1f}x (blueprint expected the shift penalty to be much larger).", "",
         "## CV grid", "", md(cv_tbl.pivot(index="lambda_B", columns="lambda_C", values="cv_mse").reset_index(), ".6f"), "",
         "## Spread of ratings (shrinkage)", "", md(shr), "",
         f"Ball values: batter rows {len(bat):,}, bowler rows {len(bowl):,}; v quantiles {q}", "",
         f"Eligible batters {int(bat_r.eligible.sum())}, bowlers {int(bowl_r.eligible.sum())}. (Fallback used: batters {fb_b}, bowlers {fb_w}.)", ""]
    (OUT / "audit_stage4.md").write_text("\n".join(L), encoding="utf-8")
    sys.exit(0 if all(g_[1] for g_ in gates) else 1)
