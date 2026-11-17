"""Stage 6: reliability. Split-half, season-to-season, does-the-shift-add-anything, permutation test.

Run:  python -I src/stage6_reliability.py
Penalties are held fixed at the Stage 4 choice. Eligibility thresholds are halved for split-half and season-to-season.
Writes outputs/reliability.md (and audit_stage6.md copy).
"""
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import sparse
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rating_model as RM

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
R, S6 = CFG["rating"], CFG["stage6"]
OUT = ROOT / CFG["paths"]["out_dir"]
T0 = time.time()
def log(*a): print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)
def md(df, fl=".4f"): return df.to_markdown(index=False, floatfmt=fl)


bat = pd.read_parquet(OUT / "ball_values_bat.parquet"); bowl = pd.read_parquet(OUT / "ball_values_bowl.parquet")
ch = json.load(open(OUT / "stage4_choices.json")); lb, lc = ch["lambda_B"], ch["lambda_C"]
bat_r = pd.read_csv(OUT / "player_ratings_batters_stage4.csv"); bowl_r = pd.read_csv(OUT / "player_ratings_bowlers_stage4.csv")
all_bat, all_bowl = bat_r.player_id.values, bowl_r.player_id.values
ROLES = {"batters": (bat, RM.Design(bat, all_bat, all_bowl), all_bat), "bowlers": (bowl, RM.Design(bowl, all_bowl, all_bat), all_bowl)}
um = np.unique(np.concatenate([bat.match_id.values, bowl.match_id.values]))
half_balls = S6["half_min_pressure_balls"]; half_matches = S6["half_min_matches"]


def pressure_counts(rows, ids):
    r = rows[rows.P == 1]
    M = sparse.coo_matrix((np.ones(len(r)), (np.searchsorted(ids, r.player.values), np.searchsorted(um, r.match_id.values))), shape=(len(ids), len(um))).tocsr()
    return M


def fit_weighted(D, wmatch, rows):
    w = wmatch[np.searchsorted(um, rows.match_id.values)]
    beta = D.fit(D.lam(lb, lc, R["context_lambda"]), w=w)
    own_b, own_c = D.own(beta)
    return own_b, own_c


rng = np.random.default_rng(CFG["seed"])
out_rows, sh_curves = [], {}
# ---------------------------------------------------------------- A. split-half
for role, (rows, D, ids) in ROLES.items():
    M = pressure_counts(rows, ids); Mb = (M > 0).astype(float)
    rs = {k: [] for k in ("B", "R", "C")}; rsb = {k: [] for k in ("B", "R", "C")}; n_pl = []
    for s in range(S6["split_half_n"]):
        h = (rng.random(len(um)) < 0.5).astype(float)
        fits = []
        for part in (h, 1 - h):
            b_, c_ = fit_weighted(D, part, rows); fits.append((b_, c_))
        ok = np.ones(len(ids), bool)
        for part in (h, 1 - h):
            ok &= ((M @ part) >= half_balls) & ((Mb @ part) >= half_matches)
        if ok.sum() < 10: continue
        n_pl.append(int(ok.sum()))
        for key, f in (("B", lambda t: t[0]), ("R", lambda t: t[0] + t[1]), ("C", lambda t: t[1])):
            r = np.corrcoef(f(fits[0])[ok], f(fits[1])[ok])[0, 1]
            rs[key].append(r); rsb[key].append(2 * r / (1 + r))
        if (s + 1) % 50 == 0: log(f"split-half {role} {s + 1}/{S6['split_half_n']}")
    for key, nm in (("B", "baseline"), ("R", "pressure rating"), ("C", "pressure shift")):
        out_rows.append(dict(role=role, quantity=nm, mean_split_half_r=np.nanmean(rs[key]), spearman_brown=np.nanmean(rsb[key]), sd_over_splits=np.nanstd(rsb[key]), mean_players=np.mean(n_pl)))
sh = pd.DataFrame(out_rows)
log("split-half done")

# ---------------------------------------------------------------- B. season to season, C. does the shift add anything
split_year = S6["season_split_year"]
s2s_rows, add_rows = [], []
for role, (rows, D, ids) in ROLES.items():
    early = (rows.year.values <= split_year).astype(float)
    # period weights at match level
    my = rows.groupby("match_id").year.first()
    w_early = np.array([1.0 if my.get(m, 9999) <= split_year else 0.0 for m in um]); w_late = 1 - w_early
    (b1, c1), (b2, c2) = fit_weighted(D, w_early, rows), fit_weighted(D, w_late, rows)
    M = pressure_counts(rows, ids); Mb = (M > 0).astype(float)
    ok = (((M @ w_early) >= half_balls) & ((Mb @ w_early) >= half_matches) & ((M @ w_late) >= half_balls) & ((Mb @ w_late) >= half_matches))
    r1, r2 = (b1 + c1)[ok], (b2 + c2)[ok]
    corr = pearsonr(r1, r2)[0]; rho = spearmanr(r1, r2).correlation
    boots = [np.corrcoef(r1[i], r2[i])[0, 1] for i in (rng.integers(0, ok.sum(), ok.sum()) for _ in range(1000))]
    cb = lambda x, y: np.corrcoef(x, y)[0, 1]
    corr_b = cb(b1[ok], b2[ok]); corr_c = cb(c1[ok], c2[ok])
    s2s_rows.append(dict(role=role, players=int(ok.sum()), pressure_rating_r=corr, spearman=rho, ci_lo=np.percentile(boots, 2.5), ci_hi=np.percentile(boots, 97.5), baseline_r=corr_b, shift_r=corr_c))
    # later pressure value ~ earlier baseline + earlier shift (WLS by later pressure balls)
    late_p = rows[(rows.year.values > split_year) & (rows.P == 1)].groupby("player").v.agg(["mean", "size"])
    idx = np.where(ok)[0]; pid = ids[idx]
    y = late_p["mean"].reindex(pid).values; wt = late_p["size"].reindex(pid).values
    keep = ~np.isnan(y)
    X = np.column_stack([np.ones(keep.sum()), (b1[idx][keep] - b1[ok].mean()) / b1[ok].std(), (c1[idx][keep] - c1[ok].mean()) / c1[ok].std()]); yy = y[keep]; ww = wt[keep]
    def wls(X, y, w): Xw = X * np.sqrt(w)[:, None]; return np.linalg.lstsq(Xw, y * np.sqrt(w), rcond=None)[0]
    coef = wls(X, yy, ww)
    bs = np.array([wls(X[i], yy[i], ww[i]) for i in (rng.integers(0, len(yy), len(yy)) for _ in range(1000))])
    for j, nm in ((1, "earlier baseline (per SD)"), (2, "earlier shift (per SD)")):
        add_rows.append(dict(role=role, term=nm, coefficient=coef[j], ci_lo=np.percentile(bs[:, j], 2.5), ci_hi=np.percentile(bs[:, j], 97.5), excludes_zero=bool(np.percentile(bs[:, j], 2.5) > 0 or np.percentile(bs[:, j], 97.5) < 0), n=int(keep.sum())))
s2s = pd.DataFrame(s2s_rows); add = pd.DataFrame(add_rows)
log("season-to-season done")

# ---------------------------------------------------------------- D. permutation test on raw shifts
perm_rows = []
for role, (rows, D, ids) in ROLES.items():
    r = rows[["player", "P", "v"]].copy()
    grp_n = r.groupby(["player", "P"]).size().unstack(fill_value=0)
    elig = grp_n[(grp_n.get(1, 0) >= S6["perm_min_pressure_rows"]) & (grp_n.get(0, 0) >= S6["perm_min_pressure_rows"])].index
    r = r[r.player.isin(elig)].sort_values("player").reset_index(drop=True)
    codes = np.searchsorted(elig.values, r.player.values) if False else pd.factorize(r.player)[0]
    nP = np.bincount(codes, weights=r.P.values); n = np.bincount(codes).astype(float)

    def spread(Pv):
        sP = np.bincount(codes, weights=r.v.values * Pv); sA = np.bincount(codes, weights=r.v.values)
        shift = sP / nP - (sA - sP) / (n - nP)
        return shift.std(), shift
    real, shifts = spread(r.P.values.astype(float))
    perms = []
    for _ in range(S6["permutations"]):
        key = rng.random(len(r)); order = np.lexsort((key, codes)); rank = np.empty(len(r)); starts = np.concatenate([[0], np.cumsum(n)[:-1]])
        rank[order] = np.arange(len(r)) - np.repeat(starts, n.astype(int))
        perms.append(spread((rank < np.repeat(nP, n.astype(int))).astype(float))[0])
    perm_rows.append(dict(role=role, players=len(nP), real_spread=real, shuffled_mean=np.mean(perms), shuffled_p95=np.percentile(perms, 95), p_value=float((np.array(perms) >= real).mean()), real_beyond_p95=bool(real > np.percentile(perms, 95))))
perm = pd.DataFrame(perm_rows)
log("permutation done")

rule = []
for role in ROLES:
    rr = float(sh[(sh.role == role) & (sh.quantity == "pressure rating")].spearman_brown.iloc[0])
    rule.append(dict(role=role, split_half_pressure_rating=rr, decision="rank on it (>= 0.40)" if rr >= 0.4 else "widen pressure to top 30% and say so (0.25-0.40)" if rr >= 0.25 else "still submit the pressure-rating ranking; lead with 'proven quality under pressure, not a separate clutch trait' (< 0.25)"))
rule = pd.DataFrame(rule)
L = ["# Audit: Stage 6 (reliability)", "", "Penalties fixed; thresholds halved for split-half and season-to-season (" + f"{half_balls} pressure balls, {half_matches} matches). The numbers below are reported whatever they are.", "",
     f"## Split-half reliability ({S6['split_half_n']} random match splits, Spearman-Brown corrected)", "", md(sh), "",
     "## Decision rule fixed in the blueprint", "", md(rule), "",
     f"## Season to season (fit on <= {split_year}, score later; bootstrap over players)", "", md(s2s), "",
     "## Does the shift add anything? (later mean value on pressure balls ~ earlier baseline + earlier shift, WLS)", "", md(add), "",
     "## Permutation test on raw pressure shifts (shuffle the pressure flag within each player)", "", md(perm), ""]
(OUT / "audit_stage6.md").write_text("\n".join(L), encoding="utf-8"); (OUT / "reliability.md").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
