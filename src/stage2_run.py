"""Stage 2a + 2b: scoring model, exact win probability, recalibration, calibration gate.

Run:  python -I src/stage2_run.py
Choices made here are logged in CHANGES_FOR_REVIEW.md:
  - env_tier removed (config use_env_tier=false)
  - regularisation C chosen per innings by leave-one-season-out next-ball log loss
  - monotone projection of the chase surface, kept only if held-out Brier worsens by <= projection_max_brier_loss
Writes outputs/audit_stage2.md, balls_wp.parquet, wp_surfaces.npz, stage2_model.pkl, stage2_choices.json, figures/stage2_calibration.png.
"""
import json
import pickle
import sys
import time
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp_engine as E

import os
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
SM, CAL = CFG["scoring_model"], CFG["calibration"]
EXPLORE = os.environ.get("S2_EXPLORE")          # "tier,C"  e.g. "1,0.3": compare candidate configurations, write nothing
if EXPLORE:
    _t, _c = EXPLORE.split(","); SM["use_env_tier"] = bool(int(_t)); FORCED_C = float(_c)
OUT = ROOT / CFG["paths"]["out_dir"]
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
EPS = CAL["wp_clip"]
RNG = np.random.default_rng(CFG["seed"])
T0 = time.time()
gates = []


def log(*a):
    print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)


def gate(name, ok, detail):
    gates.append((name, bool(ok), detail))
    log(("PASS " if ok else "FAIL ") + name + " | " + detail)


def md(df, index=False):
    return df.to_markdown(index=index, floatfmt=".4f")


# ------------------------------------------------------------------ data
b = pd.read_parquet(OUT / "balls_state.parquet")
mf = pd.read_csv(OUT / "matches_flags.csv")[["match_id", "rtype", "first_won", "chaser_won"]]
b = b.merge(mf, on="match_id", how="left")
b["y"] = np.where(b.innings == 1, b.first_won, b.chaser_won).astype(float)
b.loc[b.rtype == "tie", "y"] = np.nan
b["grp"] = b.group.map({g: i for i, g in enumerate(E.GROUPS)}).astype(int)
b["imp"] = b.impact_rule.astype(int)
b["tier"] = b.env_tier.astype(int) if SM["use_env_tier"] else 0
b["over_b"] = E.over_from_balls_left(b.balls_left)
b["oc"] = E.outcome_class(b.is_legal.values, b.is_wicket.values, b.team_runs.values)
RUNS = E.class_run_values(b.oc.values, b.team_runs.values, b.is_legal.values)
N_MAX = int(b.runs_required.max()) + SM["n_pad"]
b["legal_before"] = CFG["innings_balls"] - b.balls_left
years = sorted(b.year.unique())
I1, I2 = (b.innings == 1).values, (b.innings == 2).values
BANDS = E.Bands(SM)
log(f"balls {len(b):,}; matches {b.match_id.nunique()}; N_MAX {N_MAX}; env_tier used: {SM['use_env_tier']}")


def design_rows(d, inn, bands=BANDS):
    return bands.design(d.over_b.values, d.wickets_lost.values, d.tier.values, d.imp.values, d.grp.values, d.required_rate.values if inn == 2 else None)


def fit_one(mask, inn, C):
    d = b[mask & (I1 if inn == 1 else I2)]
    return E.fit_scoring(BANDS, SM, d.over_b.values, d.wickets_lost.values, d.tier.values, d.imp.values, d.grp.values, d.oc.values,
                         rr=d.required_rate.values if inn == 2 else None, C=C)


def nextball_logloss(mod, d, inn):
    p = mod.predict_proba(design_rows(d, inn))
    return -np.log(np.clip(p[np.arange(len(d)), d.oc.values], 1e-12, None)).sum()


# ------------------------------------------------------------------ choose C per innings (leave-one-season-out log loss)
cpath = OUT / "stage2_choices.json"
if EXPLORE:
    choices = {"grid": SM["C_grid"], "C1": FORCED_C, "C2": FORCED_C, "logloss": {"1": {}, "2": {}}}
elif SM.get("C_fixed") is not None:
    prev = json.loads(cpath.read_text()) if cpath.exists() else {}
    choices = {"grid": SM["C_grid"], "C1": SM["C_fixed"], "C2": SM["C_fixed"], "logloss": prev.get("logloss", {"1": {}, "2": {}})}
elif cpath.exists() and json.loads(cpath.read_text()).get("grid") == SM["C_grid"]:
    choices = json.loads(cpath.read_text()); log("loaded C choices", choices)
else:
    res = {1: {}, 2: {}}
    for C in SM["C_grid"]:
        for inn in (1, 2):
            tot = 0.0
            for s in years:
                tot += nextball_logloss(fit_one((b.year != s).values, inn, C), b[(b.year == s).values & (I1 if inn == 1 else I2)], inn)
            res[inn][C] = tot / (I1 if inn == 1 else I2).sum()
        log(f"C={C}: LOSO next-ball log loss inn1 {res[1][C]:.5f} inn2 {res[2][C]:.5f}")
    choices = {"grid": SM["C_grid"], "C1": min(res[1], key=res[1].get), "C2": min(res[2], key=res[2].get),
               "logloss": {str(i): {str(k): v for k, v in res[i].items()} for i in (1, 2)}}
    cpath.write_text(json.dumps(choices, indent=1))
C1, C2 = choices["C1"], choices["C2"]
log(f"chosen C: innings 1 = {C1}, innings 2 = {C2}")


def fit_pair(mask):
    return fit_one(mask, 1, C1), fit_one(mask, 2, C2)


def raw_wp(rows, cache, m1, m2, tag, project):
    sub = b.iloc[rows]
    out = np.full(len(rows), np.nan); pos = np.arange(len(sub))
    for (g, t, i), idx in sub.groupby(["grp", "tier", "imp"]).indices.items():
        key = (tag, g, t, i)
        if key not in cache:
            cache[key] = E.Surface(m1, m2, BANDS, (g, t, i), N_MAX, SM["x_max"], RUNS, project=project)
        S = cache[key]; part = sub.iloc[idx]; r1 = (part.innings == 1).values; v = np.empty(len(part))
        if r1.any():
            p = part[r1]
            v[r1] = S.wp_first(p.balls_left.values.astype(np.int64), np.minimum(p.wickets_lost.values, 10).astype(np.int64), p.score_before.values.astype(np.int64))
        if (~r1).any():
            p = part[~r1]
            v[~r1] = S.wp_chase(p.balls_left.values.astype(np.int64), p.wickets_lost.values.astype(np.int64), np.round(p.runs_required.values).astype(np.int64))
        out[pos[idx]] = v
    return out


def run_loso(project, label):
    raw = np.full(len(b), np.nan); exp_tot = {}
    for s in years:
        m1, m2 = fit_pair((b.year != s).values)
        cache = {}; rows = np.where((b.year == s).values)[0]
        raw[rows] = raw_wp(rows, cache, m1, m2, f"{label}{s}", project)
        for (_, g, t, i), S in cache.items():
            exp_tot[(s, g, t, i)] = (S.runs_to_come_mean, S.D[120, 0])
        log(f"  fold {label} {s}: {len(rows):,} held-out balls, {len(cache)} surfaces")
    return raw, exp_tot


def recalibrate(raw):
    star = np.full(len(b), np.nan); rc = {}
    for inn, I in ((1, I1), (2, I2)):
        ok = b.y.notna().values & I
        for s in years:
            tr, te = ok & (b.year != s).values, I & (b.year == s).values
            a, c = E.fit_recal(raw[tr], b.y.values[tr], EPS)
            star[te] = E.apply_recal(raw[te], a, c, EPS)
        a, c = E.fit_recal(raw[ok], b.y.values[ok], EPS); rc[inn] = {"a": a, "c": c}
    return star, rc


def brier(p, y): return float(np.mean((p - y) ** 2))
def logloss(p, y): p = np.clip(p, 1e-6, 1 - 1e-6); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


if EXPLORE:                                   # exploration: projected surface only, skip the unprojected comparison
    log("LOSO with monotone projection"); raw_pr, exp_pr = run_loso(True, "pr"); raw_np, exp_np = raw_pr, exp_pr
else:
    log("LOSO without projection"); raw_np, exp_np = run_loso(False, "np")
    log("LOSO with monotone projection"); raw_pr, exp_pr = run_loso(True, "pr")
star_np, rc_np = recalibrate(raw_np); star_pr, rc_pr = recalibrate(raw_pr)
lab_mask = b.y.notna().values
proj_rows = []
for inn, I in ((1, I1), (2, I2)):
    k = lab_mask & I
    proj_rows.append(dict(innings=inn, brier_star_no_projection=brier(star_np[k], b.y.values[k]), brier_star_projected=brier(star_pr[k], b.y.values[k])))
proj_tbl = pd.DataFrame(proj_rows)
worst_loss = max(proj_tbl.brier_star_projected - proj_tbl.brier_star_no_projection)
USE_PROJ = bool(SM["monotone_projection"] and worst_loss <= SM["projection_max_brier_loss"])
log(f"projection: worst Brier loss {worst_loss:.5f} (limit {SM['projection_max_brier_loss']}) -> use projection = {USE_PROJ}")
b["raw_oof"], b["star_oof"] = (raw_pr, star_pr) if USE_PROJ else (raw_np, star_np)
b["raw_oof_noproj"], b["star_oof_noproj"] = raw_np, star_np
recal = rc_pr if USE_PROJ else rc_np
exp_tot = exp_pr if USE_PROJ else exp_np
for inn in (1, 2): log(f"recalibration innings {inn}: a={recal[inn]['a']:.4f} c={recal[inn]['c']:.4f}")
if not EXPLORE:
    cpath.write_text(json.dumps({**choices, "use_projection": USE_PROJ, "projection_brier": proj_tbl.to_dict("records")}, indent=1))


def baseline_oof():
    out = np.full(len(b), np.nan)
    for s in years:
        tr, te = (b.year != s).values, (b.year == s).values
        par = b[tr & I1].groupby("legal_before").score_before.mean()
        for inn, I in ((1, I1), (2, I2)):
            d_tr, d_te = b[tr & I & lab_mask], b[te & I]
            f = (lambda d: (d.score_before - d.legal_before.map(par).fillna(par.iloc[-1])).values) if inn == 1 else (lambda d: np.clip(d.required_rate.values, 0, 36))
            lr = LogisticRegression(penalty=None, max_iter=300).fit(f(d_tr).reshape(-1, 1), d_tr.y.values)
            out[np.where(te & I)[0]] = lr.predict_proba(f(d_te).reshape(-1, 1))[:, 1]
    return out


b["base_oof"] = baseline_oof()
lab = b[b.y.notna()].copy()
rows = []
for inn in (1, 2):
    d = lab[lab.innings == inn]
    rows.append(dict(innings=inn, balls=len(d), brier_const=brier(d.y.mean(), d.y), brier_baseline=brier(d.base_oof, d.y), brier_raw=brier(d.raw_oof, d.y),
                     brier_star=brier(d.star_oof, d.y), logloss_baseline=logloss(d.base_oof, d.y), logloss_raw=logloss(d.raw_oof, d.y), logloss_star=logloss(d.star_oof, d.y)))
brier_tbl = pd.DataFrame(rows)
gate("WP* Brier beats one-feature baseline (both innings)", bool((brier_tbl.brier_star < brier_tbl.brier_baseline).all()),
     "; ".join(f"inn{int(r.innings)}: WP* {r.brier_star:.4f} vs baseline {r.brier_baseline:.4f} (raw {r.brier_raw:.4f})" for r in brier_tbl.itertuples()))


def decile_table(d, col, nb=10, boot=CAL["bootstrap_n"]):
    d = d.copy(); d["bin"] = pd.qcut(d[col], nb, labels=False, duplicates="drop")
    g = d.groupby("bin").agg(balls=("y", "size"), pred=(col, "mean"), obs=("y", "mean")); g["gap"] = g.pred - g.obs
    um = np.unique(d.match_id.values); mi = np.searchsorted(um, d.match_id.values)
    cnt = np.zeros((len(um), nb)); sp = np.zeros_like(cnt); sy = np.zeros_like(cnt)
    np.add.at(cnt, (mi, d.bin.values), 1); np.add.at(sp, (mi, d.bin.values), d[col].values); np.add.at(sy, (mi, d.bin.values), d.y.values)
    gaps = []
    for _ in range(boot):
        s = RNG.integers(0, len(um), len(um)); gaps.append((sp[s].sum(0) - sy[s].sum(0)) / np.maximum(cnt[s].sum(0), 1))
    gaps = np.array(gaps); g["gap_lo"], g["gap_hi"] = np.percentile(gaps, 2.5, 0)[:len(g)], np.percentile(gaps, 97.5, 0)[:len(g)]
    return g.reset_index()


dec = {}
for inn in (1, 2):
    d = lab[lab.innings == inn]
    dec[(inn, "star")] = decile_table(d, "star_oof"); dec[(inn, "raw")] = decile_table(d, "raw_oof")
    mx = dec[(inn, "star")].gap.abs().max()
    gate(f"decile gap <= {CAL['decile_tolerance']} innings {inn} (WP*, LOSO)", mx <= CAL["decile_tolerance"], f"max |pred - obs| = {mx:.4f}; raw WP max = {dec[(inn, 'raw')].gap.abs().max():.4f}")

# ------------------------------------------------------------------ full fit and cell check
log("full fit")
m1f, m2f = fit_pair(np.ones(len(b), bool))
cache_full = {}
b["raw_full"] = raw_wp(np.arange(len(b)), cache_full, m1f, m2f, "full", USE_PROJ)
for inn in (1, 2):
    ok = (b.innings == inn).values
    b.loc[ok, "star_full"] = E.apply_recal(b.raw_full.values[ok], recal[inn]["a"], recal[inn]["c"], EPS)
worst = []
for inn, mod in ((1, m1f), (2, m2f)):
    d = b[b.innings == inn]; P = mod.predict_proba(design_rows(d, inn))
    nlast = BANDS.n_wk if inn == 1 else BANDS.n_rr
    cell = BANDS.over_band(d.over_b.values) * nlast + (BANDS.wk_band(d.wickets_lost.values) if inn == 1 else BANDS.rr_band(d.required_rate.values))
    obs = np.zeros((cell.max() + 1, 10)); pred = np.zeros_like(obs); n = np.bincount(cell)
    np.add.at(obs, (cell, d.oc.values), 1); np.add.at(pred, cell, P)
    big = n >= CAL["min_cell_balls"]
    diff = np.abs(pred[big] / n[big, None] - obs[big] / n[big, None])
    worst.append(dict(innings=inn, cells_checked=int(big.sum()), worst_abs_diff=float(diff.max()), cells_over_tol=int((diff.max(1) > CAL["cell_tolerance"]).sum())))
cell_tbl = pd.DataFrame(worst)
gate("scoring model fits observed outcome frequencies (cells >= 500 balls)", bool((cell_tbl.worst_abs_diff <= CAL["cell_tolerance"]).all()),
     "; ".join(f"inn{r.innings}: {r.cells_checked} cells, worst gap {r.worst_abs_diff:.4f}" for r in cell_tbl.itertuples()))

if EXPLORE:
    summ = dict(variant=EXPLORE, brier_star=brier_tbl.brier_star.round(4).tolist(), brier_base=brier_tbl.brier_baseline.round(4).tolist(),
                max_decile_gap=[round(dec[(i, "star")].gap.abs().max(), 4) for i in (1, 2)], worst_cell_gap=cell_tbl.worst_abs_diff.round(4).tolist(),
                all_gates_pass=all(g_[1] for g_ in gates))
    print("EXPLORE_RESULT", json.dumps(summ)); sys.exit(0)

# ------------------------------------------------------------------ independent checks (not gates)
chk = {}
viol = []
for key, S in cache_full.items():
    before, after = E.monotone_violations(S.wp2_unprojected), E.monotone_violations(S.wp2)
    viol.append(dict(group=E.GROUPS[key[1]], impact=key[3], **{f"{k}_before": v for k, v in before.items()}, **{f"{k}_after": v for k, v in after.items()},
                     start_wp_target_160=float(S.wp2[120, 0, 160]), exp_first_inn_total=float(S.runs_to_come_mean)))
chk["monotonic"] = pd.DataFrame(viol).sort_values(["group", "impact"])
chk["prob_rows_sum_to_1"] = float(max(np.abs(S.P1.reshape(-1, 10)[10:].sum(1)[S.P1.reshape(-1, 10)[10:].sum(1) > 0] - 1).max() for S in cache_full.values()))
first2 = lab[(lab.innings == 2) & (lab.legal_before == 0)].copy()
first2["target_bin"] = pd.cut(first2.target, [0, 129, 149, 169, 189, 400], labels=["<=129", "130-149", "150-169", "170-189", "190+"])
sc = first2.groupby("target_bin", observed=True).agg(matches=("y", "size"), pred_wp_star=("star_oof", "mean"), obs_chase_win=("y", "mean")); sc["gap"] = sc.pred_wp_star - sc.obs_chase_win
chk["start_of_chase"] = sc.reset_index()
sg = first2.groupby("group", observed=True).agg(matches=("y", "size"), pred_wp_star=("star_oof", "mean"), obs_chase_win=("y", "mean")); sg["gap"] = sg.pred_wp_star - sg.obs_chase_win
chk["start_by_group"] = sg.reset_index()
f1 = b[(b.innings == 1) & (b.legal_before == 0)].drop_duplicates("match_id").copy()
f1["R1"] = f1.match_id.map(pd.read_csv(OUT / "matches_clean_totals.csv").set_index("match_id").R1)
f1["pred_total"] = [exp_tot[(y_, g, t, i)][0] for y_, g, t, i in zip(f1.year, f1.grp, f1.tier, f1.imp)]
def sd(d): x = np.arange(len(d)); m_ = (d * x).sum(); return np.sqrt((d * x ** 2).sum() - m_ ** 2)
f1["pred_sd"] = [sd(exp_tot[(y_, g, t, i)][1]) for y_, g, t, i in zip(f1.year, f1.grp, f1.tier, f1.imp)]
chk["first_innings_totals"] = f1.groupby("group").agg(matches=("R1", "size"), actual_mean=("R1", "mean"), predicted_mean=("pred_total", "mean"), actual_sd=("R1", "std"), predicted_sd=("pred_sd", "mean")).reset_index()
sc_def = [("need ~10 off last over, <=4 down", 1, 6, 8, 12, 0, 4), ("need 13-20 off last over, <=5 down", 1, 6, 13, 20, 0, 5), ("penultimate over, need 12-18, <=4 down", 7, 12, 12, 18, 0, 4),
          ("balls 55-66 left, need 70-90, 2-4 down", 55, 66, 70, 90, 2, 4), ("overs 15-18, need 25-40, 5-7 down", 13, 30, 25, 40, 5, 7),
          ("one run needed, any ball, <=8 down", 1, 120, 1, 1, 0, 8), ("need <= 6 with >= 18 balls left", 18, 120, 1, 6, 0, 9)]
rws = []
for name, b0, b1, n0, n1, w0, w1 in sc_def:
    d = lab[(lab.innings == 2) & lab.balls_left.between(b0, b1) & lab.runs_required.between(n0, n1) & lab.wickets_lost.between(w0, w1)]
    rws.append(dict(scenario=name, balls=len(d), matches=d.match_id.nunique(), pred_wp_star=d.star_oof.mean(), obs_win_rate=d.y.mean()))
chk["scenarios"] = pd.DataFrame(rws)
edges = [0, .02, .05, .1, .2, .5, .8, .9, .95, .98, 1]
lab["pbin"] = pd.cut(lab.star_oof, edges, include_lowest=True)
eb = lab.groupby(["innings", "pbin"], observed=True).agg(balls=("y", "size"), matches=("match_id", "nunique"), pred=("star_oof", "mean"), obs=("y", "mean")); eb["gap"] = eb.pred - eb.obs
chk["bins"] = eb.reset_index().astype({"pbin": str})
chk["by_group"] = lab.groupby(["innings", "group"]).apply(lambda d: pd.Series(dict(balls=len(d), brier_star=brier(d.star_oof, d.y), brier_base=brier(d.base_oof, d.y), mean_gap=(d.star_oof - d.y).mean()))).reset_index()
chk["live_share"] = {inn: float(((lab[lab.innings == inn].star_oof > .02) & (lab[lab.innings == inn].star_oof < .98)).mean()) for inn in (1, 2)}

# ------------------------------------------------------------------ figure
BLUE, ORANGE, GREY = "#2a6fbb", "#d95f02", "#7f7f7f"
fig, ax = plt.subplots(2, 3, figsize=(15.5, 9)); ax = ax.ravel()
for k, inn in enumerate((1, 2)):
    s, r = dec[(inn, "star")], dec[(inn, "raw")]
    ax[k].plot([0, 1], [0, 1], color=GREY, lw=1, ls="--", label="perfect")
    ax[k].plot(r.pred, r.obs, "o-", color=ORANGE, ms=5, lw=1.2, label="raw (before recalibration)")
    ax[k].errorbar(s.pred, s.obs, yerr=[(s.gap_hi - s.gap).clip(lower=0), (s.gap - s.gap_lo).clip(lower=0)], fmt="o-", color=BLUE, ms=5, lw=1.5, capsize=3, label="WP* (recalibrated), 95% match-bootstrap")
    ax[k].set_title(f"Innings {inn}: predicted vs observed win rate by decile\n(leave-one-season-out, a={recal[inn]['a']:.2f}, c={recal[inn]['c']:.2f})", fontsize=10)
    ax[k].set_xlabel("predicted win probability"); ax[k].set_ylabel("observed win rate"); ax[k].legend(fontsize=8, loc="upper left"); ax[k].set_xlim(0, 1); ax[k].set_ylim(0, 1)
sc_ = chk["start_of_chase"]
ax[2].bar(sc_.target_bin.astype(str), sc_.obs_chase_win, color="#bbbbbb", label="observed chase win rate")
ax[2].plot(sc_.target_bin.astype(str), sc_.pred_wp_star, "o", color=BLUE, ms=8, label="model WP* at ball 1")
for i_, r in sc_.iterrows(): ax[2].text(i_, 0.02, f"n={r.matches}", ha="center", fontsize=8)
ax[2].set_title("Start of chase by target (out-of-sample)", fontsize=10); ax[2].set_ylabel("chasing side win rate"); ax[2].set_ylim(0, 1); ax[2].legend(fontsize=8)
tie_ids = b[(b.rtype == "tie") & (b.innings == 2)].match_id.unique()
for k, mid in enumerate([14159, int(tie_ids[0]) if len(tie_ids) else 14159]):
    d = b[(b.match_id == mid) & (b.innings == 2)]; a_ = ax[3 + k]
    a_.plot(np.arange(len(d)), d.star_oof, color=BLUE, lw=1.6, label="WP* (chasing side)")
    wk = np.where(d.is_wicket.values)[0]; a_.plot(wk, d.star_oof.values[wk], "v", color=ORANGE, ms=7, label="wicket")
    a_.axhline(0.5, color=GREY, lw=.8, ls=":"); a_.set_ylim(0, 1); a_.set_xlabel("ball of the chase")
    a_.set_title(f"Match {mid}: chase trace ({'tie' if mf[mf.match_id == mid].rtype.iloc[0] == 'tie' else 'close finish'})", fontsize=10); a_.legend(fontsize=8)
ax[5].hist(lab[lab.innings == 1].star_oof, bins=40, alpha=.6, color=BLUE, label="innings 1"); ax[5].hist(lab[lab.innings == 2].star_oof, bins=40, alpha=.6, color=ORANGE, label="innings 2")
ax[5].set_title("Distribution of WP* on all balls", fontsize=10); ax[5].set_xlabel("WP*"); ax[5].legend(fontsize=8)
for a_ in ax: a_.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(FIG / "stage2_calibration.png", dpi=130); plt.close()

# ------------------------------------------------------------------ persist
b[["match_id", "innings", "innings_ball_num", "raw_oof", "star_oof", "raw_full", "star_full", "base_oof", "raw_oof_noproj", "star_oof_noproj"]].to_parquet(OUT / "balls_wp.parquet", index=False)
np.savez_compressed(OUT / "wp_surfaces.npz", **{f"wp2_g{k[1]}_t{k[2]}_i{k[3]}": S.wp2 for k, S in cache_full.items()}, **{f"D_g{k[1]}_t{k[2]}_i{k[3]}": S.D for k, S in cache_full.items()})
pickle.dump(dict(m1=m1f, m2=m2f, bands=BANDS, recal=recal, runs=RUNS, n_max=N_MAX, sm=SM, use_projection=USE_PROJ, C1=C1, C2=C2), open(OUT / "stage2_model.pkl", "wb"))

L = ["# Audit: Stage 2a and 2b (scoring model and win probability)", "",
     f"{len(b):,} balls, {b.match_id.nunique()} clean matches (all four competition groups train the scoring model). env_tier used: {SM['use_env_tier']}. "
     f"Chosen C: innings 1 = {C1}, innings 2 = {C2}. Monotone projection used: {USE_PROJ}. Tie matches excluded from calibration.", "",
     "## Gates", "", md(pd.DataFrame(gates, columns=["gate", "passed", "detail"]).assign(passed=lambda d: d.passed.map({True: "PASS", False: "FAIL"}))), "",
     "## Choice of C (leave-one-season-out next-ball log loss)", "", md(pd.DataFrame(choices["logloss"]).rename_axis("C").reset_index().rename(columns={"1": "innings 1", "2": "innings 2"})), "",
     "## Monotone projection: held-out Brier of WP*", "", md(proj_tbl), f"Rule: use if worst loss <= {SM['projection_max_brier_loss']}. Worst loss {worst_loss:.5f}.", "",
     "## Recalibration", "", md(pd.DataFrame(recal).T.reset_index().rename(columns={"index": "innings"})), "",
     "## Brier and log loss (leave-one-season-out)", "", md(brier_tbl), "",
     "## Deciles, WP* (innings 1)", "", md(dec[(1, "star")]), "", "## Deciles, WP* (innings 2)", "", md(dec[(2, "star")]), "",
     "## Deciles, raw WP (innings 1)", "", md(dec[(1, "raw")]), "", "## Deciles, raw WP (innings 2)", "", md(dec[(2, "raw")]), "",
     "## Scoring-model cell check (in-sample, cells >= 500 balls)", "", md(cell_tbl), "",
     "## Independent checks (not gates)", "",
     f"Probability rows sum to 1 (max abs error): {chk['prob_rows_sum_to_1']:.2e}. Live-ball share (0.02 < WP* < 0.98): {chk['live_share']}", "",
     "### Surface monotonicity, largest violation before and after projection (runs required < 250)", "", md(chk["monotonic"]), "",
     "### Start of chase by target, out-of-sample", "", md(chk["start_of_chase"]), "", md(chk["start_by_group"]), "",
     "### First-innings total: model vs actual (out-of-sample)", "", md(chk["first_innings_totals"]), "",
     "### Scenario neighbourhoods, innings 2 (out-of-sample WP* vs observed)", "", md(chk["scenarios"]), "",
     "### Extreme bins", "", md(chk["bins"]), "", "### By competition group", "", md(chk["by_group"]), "",
     "Figure: figures/stage2_calibration.png"]
(OUT / "audit_stage2.md").write_text("\n".join(L), encoding="utf-8")
log("done")
sys.exit(0 if all(g_[1] for g_ in gates) else 1)
