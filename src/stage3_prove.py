"""Stage 3: prove the pressure definition separates real situations.

Run:  python -I src/stage3_prove.py
Gate: in at least two of three phases, the dismissal rate or the boundary rate differs between pressure and ordinary
(live, non-pressure) balls, within innings x phase x wickets-band strata, with a match-bootstrap interval excluding zero.
Writes outputs/audit_stage3.md and figures/stage3_*.png
"""
import json
import pickle
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy.stats import mannwhitneyu, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp_engine as E

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
S3 = CFG["stage3"]
OUT = ROOT / CFG["paths"]["out_dir"]
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
RNG = np.random.default_rng(CFG["seed"])
gates = []


def gate(name, ok, detail):
    gates.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + " | " + detail, flush=True)


def md(df): return df.to_markdown(index=False, floatfmt=".4f")


b = pd.read_parquet(OUT / "balls_state.parquet")
p = pd.read_parquet(OUT / "balls_pressure.parquet")
b = b.merge(p[["match_id", "innings", "innings_ball_num", "oc", "wp_star", "LI", "live", "pressure", "lband", "swing"]], on=["match_id", "innings", "innings_ball_num"])
mf = pd.read_csv(OUT / "matches_flags.csv")
b["over"] = E.over_from_balls_left(b.balls_left)
b["phase"] = np.select([b.over <= S3["phase_bounds"][0], b.over <= S3["phase_bounds"][1]], [0, 1], 2)
b["wkb"] = np.select([b.wickets_lost <= S3["wicket_bands"][0], b.wickets_lost <= S3["wicket_bands"][1]], [0, 1], 2)
b["cell"] = (b.innings - 1) * 9 + b.phase * 3 + b.wkb
PH = ["powerplay (1-6)", "middle (7-15)", "death (16-20)"]
pool = b[b.live].copy()                          # pressure vs ordinary comparison is among live balls only
pool["P"] = pool.pressure.astype(int)

# --------------------------------------------------------------- indicators
atk, dfn = set(S3["attacking_strokes"]), set(S3["defensive_strokes"])
yor, slw = set(S3["yorker_styles"]), set(S3["slower_styles"])
pool["m_dismissal"] = pool.is_wicket.astype(float)
pool["m_boundary"] = (pool.is_four | pool.is_six).astype(float)
pool["m_dot"] = (pool.oc == 1).astype(float)
pool["m_runs"] = pool.team_runs.astype(float)
pool["m_extras"] = (pool.is_wide | pool.is_noball).astype(float)
pool["m_attacking_stroke"] = np.where(pool.stroke.notna(), pool.stroke.isin(atk).astype(float), np.nan)
pool["m_defensive_stroke"] = np.where(pool.stroke.notna(), pool.stroke.isin(dfn).astype(float), np.nan)
pool["m_yorker"] = np.where(pool.delivery_style.notna(), pool.delivery_style.isin(yor).astype(float), np.nan)
pool["m_slower"] = np.where(pool.delivery_style.notna(), pool.delivery_style.isin(slw).astype(float), np.nan)
METRICS = ["m_dismissal", "m_boundary", "m_dot", "m_runs", "m_extras", "m_attacking_stroke", "m_defensive_stroke", "m_yorker", "m_slower"]
NM, NC = len(METRICS), 18

um = np.sort(pool.match_id.unique()); mi = np.searchsorted(um, pool.match_id.values)
A = np.zeros((len(um), NC, 2, NM, 2))                    # match, cell, P/O, metric, (sum, count)
for j, m_ in enumerate(METRICS):
    v = pool[m_].values; ok = ~np.isnan(v)
    np.add.at(A, (mi[ok], pool.cell.values[ok], pool.P.values[ok], j, 0), v[ok])
    np.add.at(A, (mi[ok], pool.cell.values[ok], pool.P.values[ok], j, 1), 1)
full = A.sum(0)
valid = (full[:, 1, :, 1] >= S3["min_cell_balls"]) & (full[:, 0, :, 1] >= S3["min_cell_balls"])   # cell x metric: both P and O populated


def phase_delta(T):
    """standardised (pressure-weighted) pressure-minus-ordinary difference per phase and metric from totals T[cell, P/O, metric, sum/count]."""
    out = np.full((3, NM), np.nan)
    for ph in range(3):
        cells = [i for i in range(NC) if (i % 9) // 3 == ph]
        for j in range(NM):
            num = den = 0.0
            for c in cells:
                if not valid[c, j]: continue
                nP, nO = T[c, 1, j, 1], T[c, 0, j, 1]
                if nP == 0 or nO == 0: continue
                num += nP * (T[c, 1, j, 0] / nP - T[c, 0, j, 0] / nO); den += nP
            out[ph, j] = num / den if den else np.nan
    return out


point = phase_delta(full)
boots = np.empty((S3["bootstrap_n"], 3, NM))
for r in range(S3["bootstrap_n"]):
    w = np.bincount(RNG.integers(0, len(um), len(um)), minlength=len(um)).astype(float)
    boots[r] = phase_delta(np.tensordot(w, A, axes=(0, 0)))
lo, hi = np.nanpercentile(boots, 2.5, 0), np.nanpercentile(boots, 97.5, 0)
rows = []
for ph in range(3):
    for j, m_ in enumerate(METRICS):
        rows.append(dict(phase=PH[ph], metric=m_[2:], diff_pressure_minus_ordinary=point[ph, j], ci_lo=lo[ph, j], ci_hi=hi[ph, j], excludes_zero=bool(lo[ph, j] > 0 or hi[ph, j] < 0)))
shift = pd.DataFrame(rows)

# gate
gate_rows = []
for ph in range(3):
    s = shift[(shift.phase == PH[ph]) & shift.metric.isin(["dismissal", "boundary"])]
    gate_rows.append(bool(s.excludes_zero.any()))
gate("pressure separates dismissal or boundary rate in >= 2 of 3 phases (match bootstrap)", sum(gate_rows) >= 2,
     "; ".join(f"{PH[i]}: {'yes' if g else 'no'}" for i, g in enumerate(gate_rows)))

# raw cell table (rates pressure vs ordinary)
cell_rows = []
for c in range(NC):
    for j, m_ in enumerate(METRICS[:5]):
        nP, nO = full[c, 1, j, 1], full[c, 0, j, 1]
        if nP and nO:
            cell_rows.append(dict(innings=c // 9 + 1, phase=PH[(c % 9) // 3], wickets_band=["0-%d" % S3["wicket_bands"][0], "%d-%d" % (S3["wicket_bands"][0] + 1, S3["wicket_bands"][1]), "%d+" % (S3["wicket_bands"][1] + 1)][c % 3],
                                  metric=m_[2:], n_pressure=int(nP), n_ordinary=int(nO), rate_pressure=full[c, 1, j, 0] / nP, rate_ordinary=full[c, 0, j, 0] / nO))
cells = pd.DataFrame(cell_rows)

# --------------------------------------------------------------- where pressure lives
c2 = b[b.innings == 2]; c1 = b[b.innings == 1]
rb = [0, 10, 20, 30, 40, 50, 60, 80, 100, 130, 170, 400]; rl = ["1-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-80", "81-100", "101-130", "131-170", "171+"]
c2 = c2.assign(over=c2.over, rrb=pd.cut(c2.runs_required, rb, labels=rl))
h2 = c2.pivot_table(index="rrb", columns="over", values="LI", aggfunc="mean", observed=True)
cnt2 = c2.pivot_table(index="rrb", columns="over", values="LI", aggfunc="size", observed=True)
h2 = h2.where(cnt2 >= S3["heatmap_min_balls"])
h1 = c1.pivot_table(index="wickets_lost", columns="over", values="LI", aggfunc="mean")
share_by_over = b.groupby(["innings", "over"]).pressure.mean().unstack(0)
outside = float((b[b.pressure].over < 16).mean())

# --------------------------------------------------------------- close games vs blowouts
mm = mf[mf.clean][["match_id", "rtype", "margin", "chaser_won", "group"]].copy()
per = b.groupby("match_id").agg(peak_LI=("LI", "max"), total_LI=("LI", lambda s: s[b.loc[s.index, "live"]].sum()), mean_LI=("LI", lambda s: s[b.loc[s.index, "live"]].mean()), live_balls=("live", "sum")).reset_index()
mm = mm.merge(per, on="match_id")
mm["close"] = (mm.rtype == "tie") | ((mm.rtype == "runs") & (mm.margin <= S3["close_runs"])) | ((mm.rtype == "wickets") & (mm.margin <= S3["close_wickets"]))
# closeness score: tie 0; runs margin; wickets in hand converted at 2 runs per wicket-in-hand-equivalent is NOT used; keep the binary definition plus rank test on runs margins
runs_m = mm[mm.rtype == "runs"]
sp_runs = spearmanr(runs_m.margin, runs_m.peak_LI); sp_runs_mean = spearmanr(runs_m.margin, runs_m.mean_LI)
wk_m = mm[mm.rtype == "wickets"]
sp_wk = spearmanr(wk_m.margin, wk_m.peak_LI)
cl_tbl = mm.groupby("close").agg(matches=("match_id", "size"), median_peak_LI=("peak_LI", "median"), mean_peak_LI=("peak_LI", "mean"), median_mean_LI=("mean_LI", "median"), median_total_LI=("total_LI", "median")).reset_index()
mw = mannwhitneyu(mm[mm.close].peak_LI, mm[~mm.close].peak_LI, alternative="greater"); mw2 = mannwhitneyu(mm[mm.close].mean_LI, mm[~mm.close].mean_LI, alternative="greater")

# --------------------------------------------------------------- benchmark: Bhattacharjee-Lemmer pressure index (chase balls)
M_ = pickle.load(open(OUT / "stage2_model.pkl", "rb")); Z = np.load(OUT / "wp_surfaces.npz")
Eexp = {}
for k in Z.files:
    if k.startswith("D_"):
        D = Z[k].astype(np.float64); Eexp[k[2:]] = (D * np.arange(D.shape[2])).sum(2)         # expected runs to come [b, w]
c2 = b[b.innings == 2].copy()
c2["grp"] = c2.group.map({g: i for i, g in enumerate(E.GROUPS)}).astype(int); c2["imp"] = c2.impact_rule.astype(int)
c2["tier"] = c2.env_tier.astype(int) if M_["sm"]["use_env_tier"] else 0
ru = np.zeros(len(c2))
for (g, t, i), idx in c2.groupby(["grp", "tier", "imp"]).indices.items():
    Ex = Eexp[f"g{g}_t{t}_i{i}"]; sub = c2.iloc[idx]
    ru[idx] = 100 * (1 - Ex[sub.balls_left.values, np.minimum(sub.wickets_lost.values, 10)] / Ex[120, 0])
c2["RU"] = ru
W_POS = np.array(S3["lemmer_wicket_weights"])
order = b[b.innings == 2].groupby(["match_id", "striker_id"]).batting_order.first().to_dict()
wt = np.where(c2.is_wicket.values, [W_POS[int(min(max(order.get((m_, d_), np.nan), 1), 11)) - 1] if (m_, d_) in order else W_POS.mean() for m_, d_ in zip(c2.match_id.values, c2.dismissed_player_id.values)], 0.0)
c2["w_fell"] = wt
c2["sum_w"] = c2.groupby("match_id").w_fell.cumsum() - c2.w_fell
c2["PI"] = (c2.required_rate / (c2.target * 6 / 120)) * 0.5 * (np.exp(c2.RU / 100) + np.exp(c2.sum_w / 11))
c2[["match_id", "innings", "innings_ball_num", "PI", "RU", "sum_w"]].to_parquet(OUT / "chase_pi.parquet", index=False)
live2 = c2[c2.live]
sp_pi = spearmanr(live2.PI, live2.LI); sp_pi_all = spearmanr(c2.PI, c2.LI)
sp_ph = [spearmanr(live2[live2.phase == k].PI, live2[live2.phase == k].LI)[0] for k in range(3)]
pi_p80 = live2.PI.quantile(0.8); pi_top = live2.PI >= pi_p80
pi_overlap = float((pi_top & live2.pressure).sum() / max(pi_top.sum(), 1))
# rule of thumb
rule = np.where(b.innings == 2, (b.over >= 16) & b.required_rate.between(8, 15), ((b.over <= 8) & (b.wickets_lost >= 3)) | ((b.over >= 17) & (b.wickets_lost >= 5)))
bl = b.assign(rule=rule)
ov_rows = []
for inn in (1, 2):
    d = bl[(bl.innings == inn) & bl.live]
    both = int((d.rule & d.pressure).sum()); nr, npz = int(d.rule.sum()), int(d.pressure.sum())
    ov_rows.append(dict(innings=inn, rule_balls=nr, pressure_balls=npz, both=both, share_of_rule_that_is_pressure=both / max(nr, 1), share_of_pressure_in_rule=both / max(npz, 1), jaccard=both / max(nr + npz - both, 1)))
rot_tbl = pd.DataFrame(ov_rows)

# --------------------------------------------------------------- figures
BLUE, ORANGE, GREY, GREEN = "#2a6fbb", "#d95f02", "#7f7f7f", "#1b9e77"
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
names = ["dismissal", "boundary", "dot", "runs", "extras"]
for k, (nm_, title) in enumerate((("outcome", "Outcome shift: pressure minus ordinary (stratified)"), ("behaviour", "Behaviour shift: pressure minus ordinary (stratified)"))):
    mets = names if k == 0 else ["attacking_stroke", "defensive_stroke", "yorker", "slower"]
    for ph in range(3):
        s = shift[(shift.phase == PH[ph]) & shift.metric.isin(mets)].set_index("metric").loc[mets]
        x = np.arange(len(mets)) + (ph - 1) * 0.25
        ax[k].errorbar(x, s.diff_pressure_minus_ordinary, yerr=[s.diff_pressure_minus_ordinary - s.ci_lo, s.ci_hi - s.diff_pressure_minus_ordinary], fmt="o", color=[BLUE, ORANGE, GREEN][ph], capsize=3, label=PH[ph])
    ax[k].axhline(0, color=GREY, lw=1); ax[k].set_xticks(range(len(mets))); ax[k].set_xticklabels(mets); ax[k].set_title(title, fontsize=10); ax[k].legend(fontsize=8)
    ax[k].set_ylabel("difference in rate (runs per ball for 'runs')"); ax[k].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(FIG / "stage3_separation.png", dpi=130); plt.close()

fig, ax = plt.subplots(1, 3, figsize=(17, 5.2))
im = ax[0].imshow(h2.values, aspect="auto", origin="lower", cmap="viridis"); ax[0].set_xticks(range(len(h2.columns))); ax[0].set_xticklabels(h2.columns, fontsize=7)
ax[0].set_yticks(range(len(h2.index))); ax[0].set_yticklabels(h2.index, fontsize=8); ax[0].set_xlabel("over of the chase"); ax[0].set_ylabel("runs required"); ax[0].set_title("Innings 2: mean leverage (LI)", fontsize=10); plt.colorbar(im, ax=ax[0])
im = ax[1].imshow(h1.values, aspect="auto", origin="lower", cmap="viridis"); ax[1].set_xticks(range(len(h1.columns))); ax[1].set_xticklabels(h1.columns, fontsize=7)
ax[1].set_yticks(range(len(h1.index))); ax[1].set_yticklabels(h1.index); ax[1].set_xlabel("over"); ax[1].set_ylabel("wickets lost"); ax[1].set_title("Innings 1: mean leverage (LI)", fontsize=10); plt.colorbar(im, ax=ax[1])
ax[2].bar(share_by_over.index - 0.2, share_by_over[1], width=.4, color=BLUE, label="innings 1"); ax[2].bar(share_by_over.index + 0.2, share_by_over[2], width=.4, color=ORANGE, label="innings 2")
ax[2].set_xlabel("over"); ax[2].set_ylabel("share of balls that are pressure"); ax[2].set_title(f"Pressure share by over ({outside:.0%} of pressure balls before over 16)", fontsize=10); ax[2].legend(fontsize=8)
for a_ in ax[2:]: a_.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(FIG / "stage3_where_pressure_lives.png", dpi=130); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
ax[0].boxplot([mm[~mm.close].peak_LI, mm[mm.close].peak_LI], tick_labels=[f"other (n={int((~mm.close).sum())})", f"close (n={int(mm.close.sum())})"], showfliers=False)
ax[0].set_ylabel("peak LI in the match"); ax[0].set_title("Close games (<=10 runs, <=3 wickets, tie) vs the rest", fontsize=10)
ax[1].scatter(runs_m.margin, runs_m.peak_LI, s=10, alpha=.5, color=BLUE); ax[1].set_xlabel("margin (runs), wins by runs"); ax[1].set_ylabel("peak LI"); ax[1].set_title(f"Spearman {sp_runs.correlation:.2f} (peak LI vs margin)", fontsize=10)
for a_ in ax: a_.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(FIG / "stage3_close_games.png", dpi=130); plt.close()

rs = mm[mm.match_id.isin(mf[mf.in_rating_sample].match_id)]
tight = list(rs[(rs.rtype == "tie")].match_id.head(1)) + list(rs[(rs.rtype == "runs") & (rs.margin <= 2)].sort_values(["margin", "match_id"]).match_id.head(1)) + list(rs[(rs.rtype == "wickets") & (rs.margin <= 1)].sort_values("match_id").match_id.head(1))
lop = list(rs[rs.rtype == "runs"].sort_values("margin", ascending=False).match_id.head(2)) + list(rs[rs.rtype == "wickets"].sort_values("margin", ascending=False).match_id.head(1))
fig, ax = plt.subplots(2, 3, figsize=(16, 7.5))
for k, mid in enumerate(tight + lop):
    d = b[(b.match_id == mid) & (b.innings == 2)]; a_ = ax[k // 3, k % 3]
    a_.plot(np.arange(len(d)), d.LI, color=BLUE, lw=1.4, label="LI"); a_.axhline(pd.read_json(OUT / "pressure_thresholds.json", typ="series")["p80"], color=ORANGE, ls="--", lw=1, label="pressure cutoff")
    a2 = a_.twinx(); a2.plot(np.arange(len(d)), d.wp_star, color=GREY, lw=1, alpha=.8); a2.set_ylim(0, 1); a2.set_ylabel("WP* (grey)", fontsize=8)
    r_ = mf[mf.match_id == mid].iloc[0]
    a_.set_title(f"{'TIGHT' if k < 3 else 'ONE-SIDED'}: match {mid}, {r_.result}", fontsize=8); a_.set_xlabel("ball of the chase"); a_.set_ylim(0, max(6, d.LI.quantile(.99) * 1.2))
    if k == 0: a_.legend(fontsize=7, loc="upper left")
plt.tight_layout(); plt.savefig(FIG / "stage3_case_studies.png", dpi=120); plt.close()

# --------------------------------------------------------------- audit
L = ["# Audit: Stage 3 (proving the pressure definition)", "", "## Gate", "", md(pd.DataFrame(gates, columns=["gate", "passed", "detail"]).assign(passed=lambda d: d.passed.map({True: "PASS", False: "FAIL"}))), "",
     f"Comparison is between live pressure balls and live ordinary balls, standardised within innings x phase x wickets band (cells need >= {S3['min_cell_balls']} balls on both sides), 95% match bootstrap ({S3['bootstrap_n']} resamples).", "",
     "## Outcome and behaviour shift (phase-level, stratified)", "", md(shift), "",
     "## Raw cell rates", "", md(cells), "",
     f"## Where pressure lives\n\nShare of pressure balls before over 16: {outside:.1%}. Pressure balls by innings: " + str(b.groupby('innings').pressure.sum().to_dict()) + ".", "",
     md(share_by_over.reset_index().rename(columns={1: "innings 1", 2: "innings 2"})), "",
     "## Close games against blowouts", "", md(cl_tbl), "",
     f"Mann-Whitney (close > other) peak LI p={mw.pvalue:.2e}; mean LI per live ball p={mw2.pvalue:.2e}. Spearman peak LI vs runs margin (wins by runs, n={len(runs_m)}): {sp_runs.correlation:.3f} (p={sp_runs.pvalue:.1e}); mean LI vs margin: {sp_runs_mean.correlation:.3f}; peak LI vs wickets in hand (wins by wickets, n={len(wk_m)}): {sp_wk.correlation:.3f}.", "",
     f"Matches classed close: {int(mm.close.sum())} of {len(mm)} clean matches (blueprint expected about 130 across all matches).", "",
     "## Benchmark agreement (innings 2)", "",
     f"Bhattacharjee-Lemmer PI = (CRRR/IRRR) x 0.5 x [exp(RU/100) + exp(sum w_i / 11)], wicket weights by batting position of the dismissed batter. RU (resources used) is DERIVED from our own scoring model "
     f"(100 x (1 - expected runs to come / expected runs at the start)), because the Duckworth-Lewis table is not in the data. Spearman(PI, LI): live chase balls {sp_pi.correlation:.3f}; all chase balls {sp_pi_all.correlation:.3f}; "
     f"by phase {[round(x, 3) for x in sp_ph]}. Share of the top-20% PI balls that are pressure balls: {pi_overlap:.3f}.", "",
     "Rule-of-thumb overlap (live balls):", "", md(rot_tbl), "",
     "Figures: figures/stage3_separation.png, stage3_where_pressure_lives.png, stage3_close_games.png, stage3_case_studies.png"]
(OUT / "audit_stage3.md").write_text("\n".join(L), encoding="utf-8")
print(shift[shift.metric.isin(["dismissal", "boundary", "dot", "runs", "extras"])].to_string(index=False))
print(cl_tbl.to_string()); print("Spearman peakLI~margin", sp_runs.correlation, "PI~LI", sp_pi.correlation, "outside16-20", outside)
print(rot_tbl.to_string())
sys.exit(0 if all(g_[1] for g_ in gates) else 1)
