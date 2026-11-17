"""Stage 6 (second part): sensitivity grid. Re-rate players under each variant with penalties fixed.

Run:  python -I src/stage6b_sensitivity.py
Ranking proxy per variant: floor_v = rating_v - 1.2816 * (main bootstrap SD), because the bootstrap is not rerun per variant.
Variants not run: win probability without recalibration (needs the whole leverage stage rerun).
Writes outputs/sensitivity_ratings.csv, outputs/sensitivity.csv, outputs/audit_stage6b.md
"""
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import kendalltau, norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rating_model as RM
import stage4_ratings as S4

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
R, SV = CFG["rating"], CFG["sensitivity"]
OUT = ROOT / CFG["paths"]["out_dir"]
T0 = time.time()
def log(*a): print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)
def md(df, fl=".4f"): return df.to_markdown(index=False, floatfmt=fl)


ch = json.load(open(OUT / "stage4_choices.json")); lb, lc = ch["lambda_B"], ch["lambda_C"]
b = S4.load_balls()
bat, bowl = S4.build_values(b, "rating")
bat_all, bowl_all = S4.build_values(b, "all")
ratings = {"batters": pd.read_csv(OUT / "player_ratings_batters.csv"), "bowlers": pd.read_csv(OUT / "player_ratings_bowlers.csv")}
pool = {k: v[v.eligible & v.active].player_id.values for k, v in ratings.items()}
z10 = norm.ppf(1 - R["floor_quantile"])
main_sd = {k: v.set_index("player_id").boot_sd for k, v in ratings.items()}
pr = pd.read_parquet(OUT / "balls_pressure.parquet", columns=["match_id", "innings", "innings_ball_num", "LI", "live"])
live_li = pr[pr.live]
thr = json.load(open(OUT / "pressure_thresholds.json"))
pi = pd.read_parquet(OUT / "chase_pi.parquet")
st = b[["match_id", "innings", "innings_ball_num", "over", "required_rate", "wickets_lost"]]
key = ["match_id", "innings", "ball"]


def with_flag(rows, P):
    r = rows.copy(); r["P"] = P.astype(int); return r


def flags(rows, mode, arg=None):
    if mode == "cut":
        return (rows.LI.values >= np.quantile(live_li.LI.values, 1 - arg)).astype(int)
    if mode == "within":
        t = {i: np.quantile(live_li[live_li.innings == i].LI.values, 0.8) for i in (1, 2)}
        return (rows.LI.values >= rows.innings.map(t).values).astype(int)
    m = rows[key].merge(pi.rename(columns={"innings_ball_num": "ball"}), on=key, how="left")
    if mode == "pi":
        q80 = pi.merge(pr[pr.live], on=["match_id", "innings", "innings_ball_num"]).PI.quantile(0.8)
        return ((rows.innings.values == 2) & (m.PI.values >= q80)).astype(int)
    if mode == "rule":
        s = rows[key].merge(st.rename(columns={"innings_ball_num": "ball"}), on=key, how="left")
        rule = np.where(s.innings == 2, (s.over >= 16) & s.required_rate.between(8, 15), ((s.over <= 8) & (s.wickets_lost >= 3)) | ((s.over >= 17) & (s.wickets_lost >= 5)))
        return rule.astype(int)
    raise ValueError(mode)


def fit_role(rows, role, w=None, extra=None):
    own = np.sort(np.unique(rows.player.values)); opp = np.sort(np.unique(rows.opp.values))
    D = RM.Design(rows, own, opp, extra_ctx=extra)
    beta = D.fit(D.lam(lb, lc, R["context_lambda"]), w=w)
    b_, c_ = D.own(beta)
    return pd.Series(b_ + c_, index=own)


def run(name, rows_b, rows_w, wb=None, ww=None, extra_b=None):
    out = {}
    out["batters"] = fit_role(rows_b, "bat", wb, extra_b)
    out["bowlers"] = fit_role(rows_w, "bowl", ww)
    return out


variants = {}
variants["main"] = run("main", bat, bowl)
for q in SV["cutoffs"]:
    variants[f"cutoff_top{int(q * 100)}%"] = run("c", with_flag(bat, flags(bat, "cut", q)), with_flag(bowl, flags(bowl, "cut", q)))
variants["cutoff_within_innings"] = run("w", with_flag(bat, flags(bat, "within")), with_flag(bowl, flags(bowl, "within")))
zlog = lambda r: (np.log(r.LI.values.clip(1e-6)) - np.log(live_li.LI.values.clip(1e-6)).mean()) / np.log(live_li.LI.values.clip(1e-6)).std()
variants["no_cutoff_log_leverage"] = run("n", bat.assign(Pc=zlog(bat)), bowl.assign(Pc=zlog(bowl)))
variants["benchmark_pressure_index"] = run("pi", with_flag(bat, flags(bat, "pi")), with_flag(bowl, flags(bowl, "pi")))
variants["benchmark_rule_of_thumb"] = run("r", with_flag(bat, flags(bat, "rule")), with_flag(bowl, flags(bowl, "rule")))
variants["lower_tier_included"] = run("l", bat_all, bowl_all)
variants["IPL_only"] = run("i", bat, bowl, (bat.group == "IPL").astype(float).values, (bowl.group == "IPL").astype(float).values)
variants["T20I_only"] = run("t", bat, bowl, (bat.group != "IPL").astype(float).values, (bowl.group != "IPL").astype(float).values)
ref = pd.to_datetime(pd.concat([bat.match_date, bowl.match_date])).max()
hl = lambda rows: 0.5 ** (((ref - pd.to_datetime(rows.match_date)).dt.days / 365.25) / SV["recency_half_life_years"]).values
variants["recency_2yr_half_life"] = run("rec", bat, bowl, hl(bat), hl(bowl))
pos = pd.factorize(bat.position_band, sort=True)[0]
variants["position_band_in_context"] = run("pos", bat, bowl, extra_b=pos)
lo_q, hi_q = SV["winsor_quantiles"]
wz = lambda rows: rows.assign(v=rows.v.clip(rows.v.quantile(lo_q), rows.v.quantile(hi_q)))      # per role: batter rows and bowler rows capped separately
variants["winsorised_values_1_99"] = run("wz", wz(bat), wz(bowl))
log("all variants fitted")

rows_out, tab = [], []
for role in ("batters", "bowlers"):
    ids = pool[role]; sd = main_sd[role].reindex(ids).values
    base = variants["main"][role].reindex(ids)
    frame = {"player_id": ids}
    for v, res in variants.items():
        frame[v] = res[role].reindex(ids).values
    pd.DataFrame(frame).assign(role=role).to_csv(OUT / f"sensitivity_ratings_{role}.csv", index=False)
    floor_main = base.values - z10 * sd
    top_main = set(ids[np.argsort(-floor_main)[:10]])
    for v, res in variants.items():
        if v == "main": continue
        r = res[role].reindex(ids).values; ok = ~np.isnan(r)
        floor_v = r - z10 * sd
        top_v = set(ids[ok][np.argsort(-floor_v[ok])[:10]])
        tab.append(dict(role=role, variant=v, top10_overlap_with_main=len(top_v & top_main), kendall_tau=kendalltau(floor_main[ok], floor_v[ok]).correlation, players_missing=int((~ok).sum())))
sens = pd.DataFrame(tab)
sens.to_csv(OUT / "sensitivity.csv", index=False)
med = sens.groupby("role").top10_overlap_with_main.median().reset_index().rename(columns={"top10_overlap_with_main": "median_overlap_of_10"})
L = ["# Audit: Stage 6, sensitivity grid", "", "Main ranking proxy: rating minus 1.2816 x main bootstrap SD (the floor), among eligible and active players. Penalties fixed. Overlap is with the main top 10 by the same proxy.", "",
     md(sens), "", "## Median overlap (blueprint wants >= 7 of 10)", "", md(med), "",
     "Not run: win probability without recalibration (would require rerunning Stage 2c leverage with the recalibration switched off)."]
(OUT / "audit_stage6b.md").write_text("\n".join(L), encoding="utf-8")
log("done"); print(sens.to_string()); print(med.to_string())
