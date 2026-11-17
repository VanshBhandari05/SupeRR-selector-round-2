"""Follow-up analysis (step 3): five reports. Nothing here changes any rule, ranking or list.
Run: python -I src/step3_reports.py   ->  outputs/step3_reports.md
"""
import pickle
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import kendalltau, norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
R = CFG["rating"]
OUT = ROOT / CFG["paths"]["out_dir"]
names = pd.read_csv(ROOT / "competition_team_player_mapping.csv").drop_duplicates("player_id").set_index("player_id").player_name
fmt = lambda df, f=".3f": df.to_markdown(index=False, floatfmt=f)
Z = np.load(OUT / "bootstrap_ratings.npz")
L = ["# Step 3: five reports (no rule, ranking or list changed)", ""]

# ----------------------------------------------------------------- (a) floor ranking on baseline only vs main ranking
L += ["## (a) Top-10 overlap: floor ranking on baseline only vs the main ranking", "",
      "Baseline bootstrap = bootstrap pressure rating minus bootstrap shift. Floor = 10th percentile. Main ranking = the listed top 10 (floor of pressure rating, same pool).", ""]
rows = []
detail = []
for role, rk, ck, ids_k, bcol in (("batters", "rb", "cb", "bat_ids", "B"), ("bowlers", "rw", "cw", "bowl_ids", "W")):
    base_boot = Z[rk] - Z[ck]; ids = Z[ids_k]
    r = pd.read_csv(OUT / f"player_ratings_{role}.csv").set_index("player_id")
    floor_base = pd.Series(np.quantile(base_boot, R["floor_quantile"], 0), index=ids)
    main_top = pd.read_csv(OUT / f"top10_{role}.csv").player_id.tolist()
    ranked_pool = pd.read_csv(OUT / f"eligible_table_{role}.csv").player_id.tolist()           # eligible, active, negative-shift removed
    full_pool = r[r.eligible & r.active].index.tolist()                                         # eligible, active, nothing removed
    for label, pool in (("same pool as main (negative-shift players removed)", ranked_pool), ("eligible + active, nothing removed", full_pool)):
        top_b = floor_base.reindex(pool).sort_values(ascending=False).head(10).index.tolist()
        rows.append(dict(role=role, pool=label, overlap_of_10=len(set(top_b) & set(main_top)), baseline_only_top10_not_in_main="; ".join(names[i] for i in top_b if i not in main_top),
                         main_top10_not_in_baseline_only="; ".join(names[i] for i in main_top if i not in top_b)))
ov_df = pd.DataFrame(rows); ov_df.to_csv(OUT / "step3_overlap_baseline.csv", index=False)
L += [fmt(ov_df, ".0f"), ""]

# ----------------------------------------------------------------- (b) removed for negative shift, with baseline ranks
L += ["## (b) Players removed for a reliably negative pressure shift (90th percentile of the bootstrap shift below zero)", "",
      "Baseline rank = rank by baseline rating among eligible + active players (53 batters, 55 bowlers). Floor rank = rank by floor of pressure rating in the same pool before removal.", ""]
for role, bcol, scol in (("batters", "B", "C"), ("bowlers", "W", "K")):
    r = pd.read_csv(OUT / f"player_ratings_{role}.csv")
    pool = r[r.eligible & r.active].copy()
    pool["baseline_rank"] = pool[bcol].rank(ascending=False, method="min").astype(int)
    pool["floor_rank_if_kept"] = pool.floor_p10.rank(ascending=False, method="min").astype(int)
    pool["name"] = pool.player_id.map(names)
    rem = pool[pool.shift_p90 < 0].sort_values("baseline_rank")
    ranked = pd.read_csv(OUT / f"eligible_table_{role}.csv")
    assert set(rem.player_id) == set(pool.player_id) - set(ranked.player_id)
    rem.to_csv(OUT / f"step3_removed_{role}.csv", index=False)
    L += [f"### {role} removed: {len(rem)} of {len(pool)}", "", fmt(rem[["name", "player_id", "baseline_rank", "floor_rank_if_kept", bcol, scol, "shift_p90", "pressure_rating", "floor_p10"]].rename(columns={bcol: "baseline", scol: "shift"}), ".4f"), ""]

# ----------------------------------------------------------------- (c) recalibration slopes
import wp_engine  # noqa: E402  (needed to unpickle)
M = pickle.load(open(OUT / "stage2_model.pkl", "rb"))
rec = pd.DataFrame([{"innings": i, "a": M["recal"][i]["a"], "c (slope)": M["recal"][i]["c"]} for i in (1, 2)])
rec.to_csv(OUT / "step3_recalibration.csv", index=False)
L += ["## (c) Recalibration logit(WP*) = a + c x logit(WP)", "", fmt(rec, ".4f"), "", "Fitted on out-of-fold raw win probabilities from leave-one-season-out fits (all four competition groups, ties excluded). c < 1 means the exact model was over-confident, as the blueprint expected.", ""]

# ----------------------------------------------------------------- (d) spinner share
b = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "innings_ball_num", "bowler_id", "pace_or_spin", "is_legal"])
p = pd.read_parquet(OUT / "balls_pressure.parquet", columns=["match_id", "innings", "innings_ball_num", "live", "pressure"])
mf = pd.read_csv(OUT / "matches_flags.csv")[["match_id", "in_rating_sample"]]
d = b.merge(p, on=["match_id", "innings", "innings_ball_num"]).merge(mf, on="match_id")
d = d[d.live & d.in_rating_sample].copy(); d["spin"] = (d.pace_or_spin == "Spin")
rows = [dict(subset="all live balls", balls=len(d), spin_share=d.spin.mean()), dict(subset="pressure balls", balls=int(d.pressure.sum()), spin_share=d[d.pressure].spin.mean()),
        dict(subset="ordinary live balls", balls=int((~d.pressure).sum()), spin_share=d[~d.pressure].spin.mean())]
for inn in (1, 2):
    x = d[d.innings == inn]; rows.append(dict(subset=f"innings {inn}: all live", balls=len(x), spin_share=x.spin.mean()))
    if x.pressure.any(): rows.append(dict(subset=f"innings {inn}: pressure", balls=int(x.pressure.sum()), spin_share=x[x.pressure].spin.mean()))
for lo, hi, nm in ((1, 6, "powerplay"), (7, 15, "middle"), (16, 20, "death")):
    pass
sp = pd.DataFrame(rows)
btype = d.groupby("bowler_id").spin.mean().gt(0.5)
top = pd.read_csv(OUT / "top10_bowlers.csv"); rb = pd.read_csv(OUT / "player_ratings_bowlers.csv"); pool = rb[rb.eligible & rb.active].player_id
strict = pd.read_csv(OUT / "strict_rule_bowlers.csv") if (OUT / "strict_rule_bowlers.csv").exists() else None
comp = pd.DataFrame([dict(group="listed top 10 bowlers", spinners=int(btype.reindex(top.player_id).sum()), of=10),
                     dict(group="eligible + active bowler pool", spinners=int(btype.reindex(pool).sum()), of=len(pool))])
import json
sp.to_csv(OUT / "step3_spinner_share.csv", index=False); comp.to_csv(OUT / "step3_spinner_bowlers.csv", index=False)
summary = dict(spin_share_live=float(d.spin.mean()), spin_share_pressure=float(d[d.pressure].spin.mean()), spin_ratio=float(d[d.pressure].spin.mean() / d.spin.mean()),
               spinners_listed=int(comp.iloc[0].spinners), spinners_pool=int(comp.iloc[1].spinners), pool_size=int(comp.iloc[1]["of"]),
               listed_spinners=[names[i] for i in top.player_id if btype.get(i, False)], listed_pace=[names[i] for i in top.player_id if not btype.get(i, False)])
L += ["## (d) Spinner share of pressure balls bowled vs all live balls (rating sample)", "", fmt(sp, ".4f"), "",
      f"Ratio of spinner share on pressure balls to spinner share on all live balls: {d[d.pressure].spin.mean() / d.spin.mean():.3f}.", "",
      "Spinners among the bowlers (a bowler is a spinner if more than half of his live balls are spin):", "", fmt(comp, ".0f"), "",
      "Listed top-10 bowlers who are spinners: " + ", ".join(names[i] for i in top.player_id if btype.get(i, False)) + ".", ""]

# ----------------------------------------------------------------- (e) recency variant, batters only
sens = pd.read_csv(OUT / "sensitivity_ratings_batters.csv"); ids = sens.player_id.values
rb_ = pd.read_csv(OUT / "player_ratings_batters.csv").set_index("player_id"); sd = rb_.boot_sd.reindex(ids).values
z10 = norm.ppf(1 - R["floor_quantile"])
f_main = sens["main"].values - z10 * sd; f_rec = sens["recency_2yr_half_life"].values - z10 * sd
top_main_proxy = set(ids[np.argsort(-f_main)[:10]]); top_rec = ids[np.argsort(-f_rec)[:10]]
final = pd.read_csv(OUT / "top10_batters.csv").player_id.tolist()
rk_main = pd.Series(f_main, index=ids).rank(ascending=False).astype(int); rk_rec = pd.Series(f_rec, index=ids).rank(ascending=False).astype(int)
cmp_ = pd.DataFrame({"name": [names[i] for i in ids], "player_id": ids, "main_rank_proxy": rk_main.values, "recency_rank": rk_rec.values}).sort_values("recency_rank").head(14)
L += ["## (e) Recency variant (two-season half-life), batters only", "",
      f"Top-10 overlap with the main top 10 (floor proxy, the sensitivity-grid definition): **{len(top_main_proxy & set(top_rec))} of 10**. Overlap with the final listed batters: {len(set(final) & set(top_rec))} of 10. "
      f"Kendall tau vs main over the pool: {kendalltau(f_main, f_rec).correlation:.3f}.", "",
      "In the final list but not in the recency top 10: " + (", ".join(names[i] for i in final if i not in set(top_rec)) or "none") + ".",
      "In the recency top 10 but not in the final list: " + (", ".join(names[i] for i in top_rec if i not in set(final)) or "none") + ".", "",
      "Recency top 14 with ranks under each definition:", "", fmt(cmp_, ".0f"), ""]
summary.update(recency_overlap_proxy=len(top_main_proxy & set(top_rec)), recency_overlap_final=len(set(final) & set(top_rec)), recency_kendall=float(kendalltau(f_main, f_rec).correlation),
               recency_out=[names[i] for i in final if i not in set(top_rec)], recency_in=[names[i] for i in top_rec if i not in set(final)])
json.dump(summary, open(OUT / "step3_summary.json", "w"), indent=1)
(OUT / "step3_reports.md").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
