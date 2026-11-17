"""Stage 4 engine: ball values, credit split, and the two-penalty ridge rating model.

v = dWP0 / swing, split between batter and bowler by the credit table in the blueprint (4a).
Batting fit  v_bat  = context + B_i + P*C_i - (W_j + P*K_j)
Bowling fit  v_bowl = context + W_j + P*K_j - (B_i + P*C_i)
Two penalties: lambda_B on baselines, lambda_C on pressure shifts; context is (almost) unpenalised.
"""
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.linalg import solve

import wp_engine as E

BOWLER_CREDITED = {"Bowled", "Caught", "LBW", "Hit Wicket", "Stump"}
NOT_CHARGED = {"Retire Out"}


def event_rows(d, over_band_fn):
    """d: live rating-sample balls with wpn0..9, wp_star, swing, oc, flags. Returns (bat_rows, bowl_rows) with recentred values."""
    n = len(d)
    ar = np.arange(n)
    WPN = d[[f"wpn{k}" for k in range(10)]].values.astype(float)
    star = d.wp_star.values
    oc_nw = E.outcome_class(d.is_legal.values, np.zeros(n, bool), d.team_runs.values)
    dW = WPN[:, 0] - star
    dOC = WPN[ar, d.oc.values] - star
    dNW = WPN[ar, oc_nw] - star
    d1 = WPN[:, 1] - star
    kind = d.extras1_runs.values
    dt = d.dismissal_type.fillna("").values
    wick = d.is_wicket.values
    charged = wick & ~np.isin(dt, list(NOT_CHARGED))
    striker_out = charged & (d.dismissed_player_id.values == d.striker_id.values)
    nonstriker_out = charged & ~striker_out
    wide = d.is_wide.values
    bye_dot = np.isin(kind, [3, 4]) & (d.runs.values == 0)
    nb = np.isin(kind, [1, 5])
    penalty = kind == 7

    sv = np.where(bye_dot, d1, np.where(nb, WPN[ar, d.oc.values] - WPN[:, 7], dOC))
    s_has = ~wide & ~penalty
    sv = np.where(striker_out, dW, np.where(nonstriker_out | (wick & ~charged), dNW, sv))
    s_has = np.where(striker_out, ~penalty, s_has)
    ball = d.innings_ball_num.values
    bat = pd.DataFrame({"match_id": d.match_id.values, "innings": d.innings.values, "ball": ball, "player": d.striker_id.values, "opp": d.bowler_id.values, "raw": sv}).loc[s_has]
    bat_ix = np.where(s_has)[0]
    # dismissed non-striker: own row, value = incremental effect of the wicket
    ns = np.where(nonstriker_out)[0]
    bat2 = pd.DataFrame({"match_id": d.match_id.values[ns], "innings": d.innings.values[ns], "ball": ball[ns], "player": d.dismissed_player_id.values[ns].astype(int),
                         "opp": d.bowler_id.values[ns], "raw": (dW - dNW)[ns]})
    bat_all = pd.concat([bat.assign(src=bat_ix), bat2.assign(src=ns)], ignore_index=True)

    credited = wick & np.isin(dt, list(BOWLER_CREDITED))
    bv = np.where(credited, -dW, np.where(wick, -dNW, np.where(bye_dot, -d1, -dOC)))
    keep = ~penalty
    bowl = pd.DataFrame({"match_id": d.match_id.values, "innings": d.innings.values, "ball": ball, "player": d.bowler_id.values, "opp": d.striker_id.values, "raw": bv}).loc[keep]
    bowl["src"] = np.where(keep)[0]

    ctx = pd.DataFrame({"over_band": over_band_fn(d.over.values), "wkb": np.minimum(d.wickets_lost.values, 7), "lband": d.lband.values, "swing": d.swing.values,
                        "phase": d.phase.values, "P": d.pressure.values.astype(int), "group": d.group.values, "year": d.year.values, "position_band": d.position_band.values,
                        "match_date": d.match_date.values, "LI": d.LI.values,
                        "is_wicket": wick, "oc": d.oc.values, "exp_bat_runs": d.exp_bat_runs.values, "p_wicket": d.p_wicket.values, "p_dot": d.p_dot.values, "p_boundary": d.p_boundary.values})
    out = []
    for df in (bat_all, bowl):
        c = ctx.iloc[df.src.values].reset_index(drop=True)
        df = pd.concat([df.reset_index(drop=True), c], axis=1)
        df["bin"] = df.innings.astype(str) + "_" + df.over_band.astype(str) + "_" + df.wkb.astype(str) + "_" + df.lband.astype(str)
        df["dWP0"] = df.raw - df.groupby("bin").raw.transform("mean")
        df["v"] = df.dWP0 / df.swing
        out.append(df)
    return out[0], out[1]


class Design:
    """Sparse design for one fit. role = 'bat' or 'bowl' (own player = player, opposition = opp)."""

    def __init__(self, rows, own_ids, opp_ids, extra_ctx=None):
        self.n = len(rows)
        own = np.searchsorted(own_ids, rows.player.values); opp = np.searchsorted(opp_ids, rows.opp.values)
        assert (own_ids[own] == rows.player.values).all() and (opp_ids[opp] == rows.opp.values).all()
        P = rows.P.values.astype(float) if "Pc" not in rows.columns else rows.Pc.values.astype(float)   # Pc: continuous pressure for the no-cutoff variant
        ctx_cols = [(rows.innings.values - 1) * 6 + rows.phase.values * 2 + rows.P.values]            # innings x phase x P (12)
        ctx_cols.append(12 + (rows.group.values != "IPL").astype(int))                                # competition group (2)
        n_ctx = 14
        if extra_ctx is not None:                                                                     # e.g. batting-position band (3), added on top
            ctx_cols.append(n_ctx + extra_ctx); n_ctx += extra_ctx.max() + 1
        no, nq = len(own_ids), len(opp_ids)
        self.offs = dict(ctx=0, own_b=n_ctx, own_c=n_ctx + no, opp_b=n_ctx + 2 * no, opp_c=n_ctx + 2 * no + nq)
        self.p = n_ctx + 2 * no + 2 * nq
        rows_i, cols, vals = [], [], []
        r = np.arange(self.n)
        for c in ctx_cols:
            rows_i.append(r); cols.append(c); vals.append(np.ones(self.n))
        rows_i += [r, r, r, r]
        cols += [self.offs["own_b"] + own, self.offs["own_c"] + own, self.offs["opp_b"] + opp, self.offs["opp_c"] + opp]
        vals += [np.ones(self.n), P, -np.ones(self.n), -P]
        self.X = sparse.csr_matrix((np.concatenate(vals), (np.concatenate(rows_i), np.concatenate(cols))), shape=(self.n, self.p))
        self.y = rows.v.values.astype(float)
        self.n_own, self.n_opp, self.n_ctx = no, nq, n_ctx
        self.match = rows.match_id.values

    def lam(self, lam_b, lam_c, lam_ctx):
        v = np.full(self.p, lam_ctx)
        v[self.offs["own_b"]:self.offs["own_c"]] = lam_b; v[self.offs["own_c"]:self.offs["opp_b"]] = lam_c
        v[self.offs["opp_b"]:self.offs["opp_c"]] = lam_b; v[self.offs["opp_c"]:] = lam_c
        return v

    def fit(self, lam, w=None):
        X, y = self.X, self.y
        if w is None:
            G = (X.T @ X).toarray(); r = X.T @ y
        else:
            Xw = sparse.diags(w) @ X
            G = (X.T @ Xw).toarray(); r = Xw.T @ y
        G[np.diag_indices_from(G)] += lam
        return solve(G, r, assume_a="pos")

    def own(self, beta):
        o = self.offs
        return beta[o["own_b"]:o["own_c"]], beta[o["own_c"]:o["opp_b"]]


def cv_select(designs, lam_b_grid, lam_c_grid, lam_ctx, folds, seed):
    """Choose (lambda_B, lambda_C) by k-fold CV with whole matches held out; loss = summed held-out squared error over both fits."""
    rng = np.random.default_rng(seed)
    um = np.unique(np.concatenate([d.match for d in designs]))
    fold_of = dict(zip(um, rng.integers(0, folds, len(um))))
    parts = []
    for d in designs:
        f = np.array([fold_of[m] for m in d.match])
        per = []
        for k in range(folds):
            te = f == k
            Xt, yt = d.X[te], d.y[te]
            Xtr, ytr = d.X[~te], d.y[~te]
            per.append(((Xtr.T @ Xtr).toarray(), Xtr.T @ ytr, Xt, yt))
        parts.append(per)
    res = {}
    for lb in lam_b_grid:
        for lc in lam_c_grid:
            sse = 0.0; cnt = 0
            for d, per in zip(designs, parts):
                lam = d.lam(lb, lc, lam_ctx)
                for G, r, Xt, yt in per:
                    G2 = G.copy(); G2[np.diag_indices_from(G2)] += lam
                    beta = solve(G2, r, assume_a="pos")
                    e = yt - Xt @ beta; sse += float(e @ e); cnt += len(yt)
            res[(lb, lc)] = sse / cnt
    return res
