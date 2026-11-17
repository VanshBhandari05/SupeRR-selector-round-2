"""Follow-up analysis (step 2): net value on pressure balls for each listed bowler, and the strict-rule bowler list.

net runs = (actual - expected bowler-credited wickets) x (average run value of a wicket in those states) - (actual - expected runs conceded)
Run value of a wicket in a state = (WP*(after a dot) - WP*(after a wicket)) / (WP* gained per run), per ball, from the stored model.
Nothing here changes the ranking, rules or lists.  Run: python -I src/step2_bowler_net.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
OUT = ROOT / CFG["paths"]["out_dir"]
RNG = np.random.default_rng(CFG["seed"])
CRED = {"Bowled", "Caught", "LBW", "Hit Wicket", "Stump"}
names = pd.read_csv(ROOT / "competition_team_player_mapping.csv").drop_duplicates("player_id").set_index("player_id").player_name

b = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "innings_ball_num", "bowler_id", "is_wicket", "dismissal_type", "runs", "is_wide", "is_noball"])
p = pd.read_parquet(OUT / "balls_pressure.parquet")
mf = pd.read_csv(OUT / "matches_flags.csv")[["match_id", "in_rating_sample"]]
d = b.merge(p, on=["match_id", "innings", "innings_ball_num"]).merge(mf, on="match_id")
d = d[d.live & d.in_rating_sample].copy()                       # same sample as Stage 4 companion statistics
cred = d.is_wicket & d.dismissal_type.isin(CRED)
share = cred.sum() / d.is_wicket.sum()                          # share of wickets credited to the bowler (as in Stage 4)
d["cred"] = cred.astype(float)
d["exp_w"] = d.p_wicket * share
d["conc"] = d.runs + (d.is_wide | d.is_noball).astype(int)
d["exp_conc"] = d.exp_bat_runs + d.p_extra

# run value of a wicket, per ball: WP loss of a wicket vs a dot, divided by WP gained per run (p-weighted slope over the 0,1,2,3,4,6 run classes)
runs = np.array([0, 1, 2, 3, 4, 6.0])
W = d[[f"wpn{k}" for k in range(1, 5 + 1)] + ["wpn6"]].values.astype(float)       # classes 1..6 = R0,R1,R2,R3,R4,R6
Pk = d[[f"p{k}" for k in range(1, 5 + 1)] + ["p6"]].values.astype(float)
Pk = Pk / Pk.sum(1, keepdims=True)
mr = Pk @ runs; mw = (Pk * W).sum(1)
slope = (Pk * (runs[None, :] - mr[:, None]) * (W - mw[:, None])).sum(1) / (Pk * (runs[None, :] - mr[:, None]) ** 2).sum(1)
loss = d.wpn1.values.astype(float) - d.wpn0.values.astype(float)
d["rv"] = loss / np.clip(slope, 1e-6, None)
pr = d[d.pressure].copy()
print("pressure balls (rating sample, live):", len(pr), " share of wickets credited to bowler:", round(share, 4))
print("run value of a wicket per ball (runs): quantiles", pr.rv.quantile([.01, .1, .5, .9, .99]).round(2).to_dict(), " mean", round(pr.rv.mean(), 2), " p_wicket-weighted mean", round(np.average(pr.rv, weights=pr.p_wicket), 2))


def agg(g):
    return pd.Series(dict(pressure_balls=len(g), wk=g.cred.sum(), exp_wk=g.exp_w.sum(), runs=g.conc.sum(), exp_runs=g.exp_conc.sum(), rv_mean=g.rv.mean(), rv_pw=np.average(g.rv, weights=g.p_wicket)))


def net(t, rv_col):
    return (t.wk - t.exp_wk) * t[rv_col] - (t.runs - t.exp_runs)


tab = pr.groupby("bowler_id").apply(agg)
tab["wicket_effect_runs"] = (tab.wk - tab.exp_wk) * tab.rv_mean
tab["runs_effect_runs"] = -(tab.runs - tab.exp_runs)
tab["net_runs"] = net(tab, "rv_mean"); tab["net_runs_pw"] = net(tab, "rv_pw")
tab["net_runs_per100"] = 100 * tab.net_runs / tab.pressure_balls
tab["economy_index"] = 100 * tab.exp_runs / tab.runs; tab["wicket_ratio"] = tab.wk / tab.exp_wk

# match-bootstrap interval for net runs
per_m = pr.groupby(["bowler_id", "match_id"]).apply(lambda g: pd.Series(dict(wk=g.cred.sum(), exp_wk=g.exp_w.sum(), runs=g.conc.sum(), exp_runs=g.exp_conc.sum(), rv_sum=g.rv.sum(), n=len(g)))).reset_index()


def boot(pid, B=1000):
    g = per_m[per_m.bowler_id == pid]
    if len(g) < 2: return (np.nan, np.nan)
    v = g[["wk", "exp_wk", "runs", "exp_runs", "rv_sum", "n"]].values; out = []
    for _ in range(B):
        s = v[RNG.integers(0, len(v), len(v))].sum(0)
        out.append((s[0] - s[1]) * s[4] / s[5] - (s[2] - s[3]))
    return tuple(np.percentile(out, [10, 90]))


rank = pd.read_csv(OUT / "eligible_table_bowlers.csv")[["player_id", "rank", "pressure_rating", "floor_p10", "economy_index_P", "wicket_ratio_P"]]
top = pd.read_csv(OUT / "top10_bowlers.csv")
listed = tab.loc[top.player_id].reset_index().rename(columns={"bowler_id": "player_id"}).merge(rank[["player_id", "rank"]], on="player_id")
listed["name"] = listed.player_id.map(names)
listed["net_p10"], listed["net_p90"] = zip(*[boot(i) for i in listed.player_id])
cols = ["rank", "name", "player_id", "pressure_balls", "wk", "exp_wk", "wicket_ratio", "runs", "exp_runs", "economy_index", "rv_mean", "wicket_effect_runs", "runs_effect_runs", "net_runs", "net_runs_per100", "net_p10", "net_p90", "net_runs_pw"]
listed = listed[cols].sort_values("rank")

# strict rule: drop listed bowlers whose economy index on pressure balls is <= 100, walk down the ranking until 10 remain
full = rank.merge(tab.reset_index().rename(columns={"bowler_id": "player_id"})[["player_id", "economy_index"]], on="player_id").sort_values("rank")
neg = pd.read_csv(OUT / "eligible_table_bowlers.csv")   # already excludes reliably-negative shifts and non-active players
strict = full[full.economy_index > 100].head(10).copy()
strict["name"] = strict.player_id.map(names)
strict_net = tab.loc[strict.player_id].reset_index().rename(columns={"bowler_id": "player_id"})
strict = strict.merge(strict_net[["player_id", "pressure_balls", "wk", "exp_wk", "runs", "exp_runs", "wicket_ratio", "rv_mean", "net_runs", "net_runs_per100"]], on="player_id")
strict["new_vs_main"] = ~strict.player_id.isin(top.player_id)
dropped = top[~top.player_id.isin(strict.player_id)].assign(name=lambda x: x.player_id.map(names))[["rank", "name", "player_id"]]
ext = full[full["rank"].between(11, 14)].assign(name=lambda x: x.player_id.map(names))

listed.to_csv(OUT / "bowler_net_value.csv", index=False); strict.to_csv(OUT / "strict_rule_bowlers.csv", index=False)
fmt = lambda df, f=".2f": df.to_markdown(index=False, floatfmt=f)
L = ["# Step 2: bowler net value on pressure balls and the strict-rule list", "",
     "net runs = (actual - expected bowler-credited wickets) x (mean run value of a wicket on the bowler's pressure balls) - (actual - expected runs conceded). "
     "Expected wickets = sum of the model's wicket probability x the share of wickets credited to bowlers; expected runs = model's expected bat runs + expected wide/no-ball runs. "
     f"Run value of a wicket per ball = (WP* after a dot - WP* after a wicket) / (p-weighted WP* gain per run across the 0,1,2,3,4,6 outcomes). Mean over all pressure balls: {pr.rv.mean():.2f} runs; quantiles {pr.rv.quantile([.1, .5, .9]).round(2).to_dict()}. "
     "net_p10 / net_p90 = 10th/90th percentile of a match bootstrap (1000).", "",
     "## Listed bowlers (current top 10)", "", fmt(listed), "",
     "## Strict-rule list (economy index above 100 on pressure balls required)", "", fmt(strict[["rank", "name", "player_id", "pressure_rating", "floor_p10", "economy_index", "wicket_ratio", "net_runs", "net_runs_per100", "new_vs_main"]], ".3f"), "",
     "Dropped from the current list under the strict rule:", "", fmt(dropped, ".0f"), "", "Ranks 11 to 14 of the pool, for reference:", "", fmt(ext[["rank", "name", "economy_index"]]), ""]
(OUT / "step2_bowler_net.md").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
