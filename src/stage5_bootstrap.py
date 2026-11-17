"""Stage 5: fair comparison. Match bootstrap of both ridge fits (penalties fixed), eligibility, active filter, cross-check.

Run:  python -I src/stage5_bootstrap.py
Writes outputs/bootstrap_ratings.npz, player_ratings_batters.csv, player_ratings_bowlers.csv, audit_stage5.md
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

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
R = CFG["rating"]
OUT = ROOT / CFG["paths"]["out_dir"]
T0 = time.time()
def log(*a): print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)
def md(df, fl=".4f"): return df.to_markdown(index=False, floatfmt=fl)


bat = pd.read_parquet(OUT / "ball_values_bat.parquet"); bowl = pd.read_parquet(OUT / "ball_values_bowl.parquet")
ch = json.load(open(OUT / "stage4_choices.json")); lb, lc = ch["lambda_B"], ch["lambda_C"]
bat_r = pd.read_csv(OUT / "player_ratings_batters_stage4.csv"); bowl_r = pd.read_csv(OUT / "player_ratings_bowlers_stage4.csv")
all_bat, all_bowl = bat_r.player_id.values, bowl_r.player_id.values
Db, Dw = RM.Design(bat, all_bat, all_bowl), RM.Design(bowl, all_bowl, all_bat)
lam_b, lam_w = Db.lam(lb, lc, R["context_lambda"]), Dw.lam(lb, lc, R["context_lambda"])
um = np.unique(np.concatenate([Db.match, Dw.match]))
mb, mw_ = np.searchsorted(um, Db.match), np.searchsorted(um, Dw.match)
rng = np.random.default_rng(CFG["seed"])
NB = R["bootstrap_n"]
rb = np.empty((NB, len(all_bat)), np.float32); cb = np.empty_like(rb); rw = np.empty((NB, len(all_bowl)), np.float32); cw = np.empty_like(rw)
for i in range(NB):
    w = np.bincount(rng.integers(0, len(um), len(um)), minlength=len(um)).astype(float)
    B_, C_ = Db.own(Db.fit(lam_b, w[mb])); W_, K_ = Dw.own(Dw.fit(lam_w, w[mw_]))
    rb[i], cb[i], rw[i], cw[i] = B_ + C_, C_, W_ + K_, K_
    if (i + 1) % 50 == 0: log(f"bootstrap {i + 1}/{NB}")
np.savez_compressed(OUT / "bootstrap_ratings.npz", rb=rb, cb=cb, rw=rw, cw=cw, bat_ids=all_bat, bowl_ids=all_bowl)

# active players: any appearance (striker, non-striker, bowler) in a clean match in the active years
bs = pd.read_parquet(OUT / "balls_state.parquet", columns=["year", "striker_id", "non_striker_id", "bowler_id"])
act = bs[bs.year.isin(R["active_years"])]
active_ids = set(act.striker_id) | set(act.non_striker_id) | set(act.bowler_id)

fq = R["floor_quantile"]
def finish(r_, pr_mat, sh_mat, rating_col, role):
    r_ = r_.copy()
    r_["active"] = r_.player_id.isin(active_ids)
    r_["boot_mean"] = pr_mat.mean(0); r_["boot_sd"] = pr_mat.std(0)
    r_["floor_p10"] = np.quantile(pr_mat, fq, 0); r_["p90"] = np.quantile(pr_mat, 0.90, 0)
    r_["shift_boot_mean"] = sh_mat.mean(0); r_["shift_p90"] = np.quantile(sh_mat, R["negative_shift_quantile"], 0); r_["shift_p10"] = np.quantile(sh_mat, 0.10, 0)
    pool = (r_.eligible & r_.active).values                      # ranks are among eligible, active players
    ranks = (-pr_mat[:, pool]).argsort(1).argsort(1) + 1
    r_["p_top10"] = np.nan; r_["p_top20"] = np.nan; r_["rank_p10"] = np.nan; r_["rank_p90"] = np.nan
    r_.loc[pool, "p_top10"] = (ranks <= 10).mean(0); r_.loc[pool, "p_top20"] = (ranks <= 20).mean(0)
    r_.loc[pool, "rank_p10"] = np.quantile(ranks, 0.1, 0); r_.loc[pool, "rank_p90"] = np.quantile(ranks, 0.9, 0)
    return r_

bat_r = finish(bat_r, rb, cb, "pressure_rating", "bat"); bowl_r = finish(bowl_r, rw, cw, "pressure_rating", "bowl")
bat_r["pressure_rating_check"] = bat_r.B + bat_r.C; bowl_r["pressure_rating_check"] = bowl_r.W + bowl_r.K


def cross_check(rows, role_ratings, id_col="player", idcol_out="player_id"):
    """Simple version without the regression: shrunk raw means, baseline from ordinary balls, shift on pressure balls."""
    g = rows.groupby(["player", "P"]).v.agg(["mean", "size"]).unstack("P"); g.columns = [f"{a}_{b}" for a, b in g.columns]
    g = g.fillna({"size_0": 0, "size_1": 0})
    sig2 = float(rows.v.var())
    def shrink_k(means, sizes):
        ok = sizes > 20; m = means[ok]; n = sizes[ok]
        tau2 = max(float(m.var() - sig2 * np.mean(1 / n)), 1e-6); return sig2 / tau2
    kb = shrink_k(g.mean_0.fillna(0), g.size_0); base = g.size_0 / (g.size_0 + kb) * g.mean_0.fillna(0)
    diff = (g.mean_1.fillna(0) - base)
    kc = shrink_k(diff, g.size_1); shift = g.size_1 / (g.size_1 + kc) * diff
    out = (base + shift).rename("simple_rating").reset_index().rename(columns={"player": idcol_out})
    return out, kb, kc


chk_rows = []
for nm, rows, r_, col in (("batters", bat, bat_r, "pressure_rating"), ("bowlers", bowl, bowl_r, "pressure_rating")):
    simple, kb, kc = cross_check(rows, r_)
    r_.drop(columns=[c for c in ("simple_rating",) if c in r_.columns], inplace=True)
    m_ = r_.merge(simple, on="player_id", how="left")
    r_["simple_rating"] = m_.simple_rating.values
    e = r_[r_.eligible & r_.simple_rating.notna()]
    rho = spearmanr(e[col], e.simple_rating).correlation
    chk_rows.append(dict(role=nm, spearman_regression_vs_simple=rho, k_baseline=kb, k_shift=kc, n=len(e)))
chk = pd.DataFrame(chk_rows)
log("cross-check:", chk.to_dict("records"))

for nm, r_ in (("batters", bat_r), ("bowlers", bowl_r)):
    r_.to_csv(OUT / f"player_ratings_{nm}.csv", index=False)

elig_tbl = pd.DataFrame({"role": ["batters", "bowlers"], "eligible": [int(bat_r.eligible.sum()), int(bowl_r.eligible.sum())],
                         "eligible_and_active": [int((bat_r.eligible & bat_r.active).sum()), int((bowl_r.eligible & bowl_r.active).sum())]})
unc = pd.DataFrame({"role": ["batters", "bowlers"],
                    "median_boot_sd_eligible": [bat_r[bat_r.eligible].boot_sd.median(), bowl_r[bowl_r.eligible].boot_sd.median()],
                    "sd_of_ratings_eligible": [bat_r[bat_r.eligible].pressure_rating.std(), bowl_r[bowl_r.eligible].pressure_rating.std()],
                    "share_eligible_shift_interval_excludes_zero": [float(((bat_r.shift_p10 > 0) | (bat_r.shift_p90 < 0))[bat_r.eligible].mean()), float(((bowl_r.shift_p10 > 0) | (bowl_r.shift_p90 < 0))[bowl_r.eligible].mean())]})
L = ["# Audit: Stage 5 (fair comparison)", "", f"Penalties fixed at lambda_B={lb}, lambda_C={lc}. {NB} whole-match bootstrap resamples of both fits. Rules came from config.yaml (locked before any leaderboard was viewed).", "",
     "## Eligibility", "", md(elig_tbl, ".0f"), "", "## Uncertainty", "", md(unc), "",
     "## Cross-check: simple shrunk version vs regression (blueprint wants Spearman >= 0.8)", "", md(chk), ""]
(OUT / "audit_stage5.md").write_text("\n".join(L), encoding="utf-8")
log("done")
