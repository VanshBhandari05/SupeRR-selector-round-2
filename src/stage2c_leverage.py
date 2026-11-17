"""Stage 2c: leverage and the pressure flag.

swing(s) = sum_o p(o|s) |WP*(after o) - WP*(s)|     LI = swing / mean swing over live balls
Live ball: WP* in (0.02, 0.98).  Pressure ball: LI >= 80th percentile of live balls, pooled across both innings.
Uses the full-data scoring models and chase surfaces from Stage 2 (out-of-sample calibration was gated there).
Writes outputs/balls_pressure.parquet, outputs/pressure_thresholds.json, outputs/audit_stage2c.md
"""
import json
import pickle
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp_engine as E

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
SM, PR = CFG["scoring_model"], CFG["pressure"]
OUT = ROOT / CFG["paths"]["out_dir"]
EPS = CFG["calibration"]["wp_clip"]

M = pickle.load(open(OUT / "stage2_model.pkl", "rb"))
m1, m2, bands, recal, RUNS, N_MAX = M["m1"], M["m2"], M["bands"], M["recal"], M["runs"], M["n_max"]
Z = np.load(OUT / "wp_surfaces.npz")

b = pd.read_parquet(OUT / "balls_state.parquet")
w = pd.read_parquet(OUT / "balls_wp.parquet")[["match_id", "innings", "innings_ball_num", "star_full"]]
b = b.merge(w, on=["match_id", "innings", "innings_ball_num"], how="left")
b["grp"] = b.group.map({g: i for i, g in enumerate(E.GROUPS)}).astype(int)
b["imp"] = b.impact_rule.astype(int)
b["tier"] = b.env_tier.astype(int) if SM["use_env_tier"] else 0
b["over_b"] = E.over_from_balls_left(b.balls_left)
b["oc"] = E.outcome_class(b.is_legal.values, b.is_wicket.values, b.team_runs.values)
n = len(b)

# next-ball outcome probabilities p(o | s)
P = np.zeros((n, 10))
for inn, mod in ((1, m1), (2, m2)):
    ix = np.where(b.innings.values == inn)[0]; d = b.iloc[ix]
    P[ix] = mod.predict_proba(bands.design(d.over_b.values, d.wickets_lost.values, d.tier.values, d.imp.values, d.grp.values,
                                           d.required_rate.values if inn == 2 else None))
print("probabilities done", flush=True)

# WP* after each possible outcome
WPN = np.zeros((n, 10))
r_max = int(b.score_before.max()) + 10
for (g, t, i), idx in b.groupby(["grp", "tier", "imp"]).indices.items():
    key = f"g{g}_t{t}_i{i}"
    wp2, D = Z[f"wp2_{key}"].astype(np.float64), Z[f"D_{key}"].astype(np.float64)
    wp1 = E.wp1_table(D, wp2[120, 0].copy(), r_max)
    sub = b.iloc[idx]
    bb, ww = sub.balls_left.values.astype(int), sub.wickets_lost.values.astype(int)
    first = (sub.innings.values == 1)
    nn = np.where(first, 0, np.round(sub.runs_required.fillna(0).values)).astype(int)
    rr_ = sub.score_before.values.astype(int)
    for k in range(10):
        b2 = bb - (1 if k < 7 else 0); w2 = ww + (1 if k == 0 else 0); run = int(RUNS[k])
        out = np.empty(len(sub))
        # innings 2: chase table, exact terminal values
        n2 = nn - run
        raw2 = wp2[b2, np.minimum(w2, 10), np.clip(n2, 0, N_MAX)]
        term = (n2 <= 0) | (b2 == 0) | (w2 == 10)
        s2 = np.where(term, raw2, E.apply_recal(raw2, recal[2]["a"], recal[2]["c"], EPS))
        # innings 1: first-innings table
        raw1 = wp1[b2, np.minimum(w2, 10), np.minimum(rr_ + run, r_max)]
        s1 = E.apply_recal(raw1, recal[1]["a"], recal[1]["c"], EPS)
        out[:] = np.where(first, s1, s2)
        WPN[idx, k] = out
print("next-state WP* done", flush=True)

star0 = b.star_full.values
swing = (P * np.abs(WPN - star0[:, None])).sum(1)
live = (star0 > PR["live_low"]) & (star0 < PR["live_high"])
mean_swing = swing[live].mean()
LI = swing / mean_swing
q = {"median": float(np.quantile(LI[live], 0.5)), "p80": float(np.quantile(LI[live], PR["pressure_quantile"])), "p95": float(np.quantile(LI[live], 0.95)),
     "mean_swing_live": float(mean_swing)}
pressure = live & (LI >= q["p80"])
lband = np.select([~live, LI < q["median"], LI < q["p80"], LI < q["p95"]], ["dead", "ordinary", "elevated", "high"], "extreme")

# expected quantities for companion statistics (Stage 4c)
bat_runs_by_class = b.groupby("oc").runs.mean().reindex(range(10)).fillna(0).values
res = pd.DataFrame({"match_id": b.match_id, "innings": b.innings, "innings_ball_num": b.innings_ball_num, "oc": b.oc, "wp_star": star0,
                    "swing": swing, "LI": LI, "live": live, "pressure": pressure, "lband": lband,
                    "exp_runs": P @ RUNS, "exp_bat_runs": P @ bat_runs_by_class, "p_wicket": P[:, 0], "p_dot": P[:, 1], "p_boundary": P[:, 5] + P[:, 6], "p_extra": P[:, 7:].sum(1)})
for k in range(10):
    res[f"p{k}"] = P[:, k].astype(np.float32); res[f"wpn{k}"] = WPN[:, k].astype(np.float32)
res["wp_after_actual"] = WPN[np.arange(n), b.oc.values]
res.to_parquet(OUT / "balls_pressure.parquet", index=False)
json.dump({**q, "live_low": PR["live_low"], "live_high": PR["live_high"], "runs": RUNS.tolist(), "bat_runs_by_class": bat_runs_by_class.tolist()}, open(OUT / "pressure_thresholds.json", "w"), indent=1)

# audit
bb_ = b[["match_id", "innings", "balls_left", "over_b", "wickets_lost"]].copy(); bb_["pressure"] = pressure; bb_["live"] = live; bb_["LI"] = LI
sh = bb_.groupby("innings").agg(balls=("live", "size"), live_share=("live", "mean"), pressure_share_all=("pressure", "mean")).reset_index()
sh["pressure_share_of_live"] = bb_[bb_.live].groupby("innings").pressure.mean().values
sh["mean_LI_live"] = bb_[bb_.live].groupby("innings").LI.mean().values
byover = bb_.groupby(["innings", "over_b"]).agg(balls=("live", "size"), pressure_share=("pressure", "mean"), mean_LI=("LI", "mean")).reset_index()
pp = bb_[bb_.pressure]
outside = float((pp.over_b < 16).mean())
exp_check = pd.DataFrame({"check": ["mean of sum_o p(o|s) WP*(after o) - WP*(s)  (should be near 0)", "share of balls where swing is exactly 0", "min swing among live balls", "LI max"],
                          "value": [float((P * WPN).sum(1).mean() - star0.mean()), float((swing == 0).mean()), float(swing[live].min()), float(LI.max())]})
L = ["# Audit: Stage 2c (leverage and pressure flag)", "", f"Thresholds on live balls (WP* in ({PR['live_low']}, {PR['live_high']})): {json.dumps(q)}", "",
     f"Pressure balls: {int(pressure.sum()):,} of {n:,} balls ({pressure.mean():.1%}); {pressure.sum() / live.sum():.1%} of live balls. Pressure balls outside overs 16-20: {outside:.1%}.", "",
     "## By innings", "", sh.to_markdown(index=False, floatfmt=".4f"), "", "## By over", "", byover.to_markdown(index=False, floatfmt=".4f"), "",
     "## Sanity", "", exp_check.to_markdown(index=False, floatfmt=".6f"), ""]
(OUT / "audit_stage2c.md").write_text("\n".join(L), encoding="utf-8")
print(sh.to_string()); print("pressure outside overs 16-20:", round(outside, 3)); print(exp_check.to_string())
