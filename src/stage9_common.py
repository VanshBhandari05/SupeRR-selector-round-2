"""Stage 9 shared pieces: row tables, pressure-flag variants, bootstrap weight replay, term refits, aggregation engine.

Additive and read-only on outputs/ from Stages 0-7. Reuses: ball_values_bat/bowl.parquet (ball values v), balls_pressure.parquet (LI),
player_ratings_*.csv (B,C,W,K), bootstrap_ratings.npz (300 whole-match refits), stage4_choices.json (lambda_B, lambda_C).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rating_model as RM

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
C9 = yaml.safe_load(open(ROOT / "config_stage9.yaml", encoding="utf-8-sig"))
OUT = ROOT / CFG["paths"]["out_dir"]
O9 = OUT / "rr_fit"; O9.mkdir(exist_ok=True)
R = CFG["rating"]
BANDS = C9["batting_bands"]; BAND_NAMES = list(BANDS)
PHASE_NAMES = ["powerplay", "middle", "death"]; TYPE_NAMES = ["pace", "spin"]
BOWL_SLOTS = [f"{p}|{t}" for p in PHASE_NAMES for t in TYPE_NAMES]       # slot = phase*2 + type
BAT_SLOTS = BAND_NAMES


def band_of(pos):
    out = np.full(len(pos), -1)
    for i, (lo, hi) in enumerate(BANDS.values()):
        out[(pos >= lo) & (pos <= hi)] = i
    return out


class Data:
    def __init__(self):
        teams = pd.read_csv(ROOT / "teams.csv")
        self.rr_id = int(teams[teams.team_name == C9["rr"]["team_name"]].team_id.unique().item())
        bat = pd.read_parquet(OUT / "ball_values_bat.parquet"); bowl = pd.read_parquet(OUT / "ball_values_bowl.parquet")
        bs = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "innings_ball_num", "batting_team_id", "bowling_team_id",
                                                                    "striker_id", "bowler_id", "batting_position", "pace_or_spin"]).rename(columns={"innings_ball_num": "ball"})
        self.ratings = {"bat": pd.read_csv(OUT / "player_ratings_batters.csv"), "bowl": pd.read_csv(OUT / "player_ratings_bowlers.csv")}
        self.all_bat = self.ratings["bat"].player_id.values; self.all_bowl = self.ratings["bowl"].player_id.values
        bat = bat.merge(bs, on=["match_id", "innings", "ball"], how="left", validate="m:1")
        bowl = bowl.merge(bs, on=["match_id", "innings", "ball"], how="left", validate="m:1")
        assert bat.batting_team_id.notna().all() and bowl.batting_team_id.notna().all()
        # batting slot = pipeline's batting_position of the striker. A dismissed non-striker's extra row has no ball faced: take that
        # player's position from the match (as striker elsewhere in the match, else playing_eleven batting_order).
        bat["is_extra"] = bat.player != bat.striker_id
        posmap = bs.groupby(["match_id", "striker_id"]).batting_position.first()
        pe = pd.read_csv(ROOT / "playing_eleven.csv").drop_duplicates(["match_id", "player_id"]).set_index(["match_id", "player_id"]).batting_order
        pos = bat.batting_position.astype(float).copy()
        ex = bat.is_extra.values
        idx = pd.MultiIndex.from_arrays([bat.match_id[ex], bat.player[ex]])
        pos[ex] = posmap.reindex(idx).values
        still = pos.isna().values & ex
        idx2 = pd.MultiIndex.from_arrays([bat.match_id[still], bat.player[still]])
        pos[still] = pe.reindex(idx2).values
        self.n_extra_rows = int(ex.sum()); self.n_pos_unresolved = int(pos.isna().sum())
        keep = pos.notna().values
        bat = bat[keep].copy(); pos = pos[keep]
        bat["pos"] = pos.astype(int).clip(upper=CFG["batting_position_clip"]); bat["slot"] = band_of(bat.pos.values)
        assert (bat.slot >= 0).all()
        bat["is_ball"] = ~bat.is_extra; bat["team"] = bat.batting_team_id
        bowl["slot"] = bowl.phase.values * 2 + (bowl.pace_or_spin.values == "Spin").astype(int); bowl["is_ball"] = True; bowl["team"] = bowl.bowling_team_id
        for d in (bat, bowl):
            d["grp"] = (d.group != "IPL").astype(int); d["rr"] = ((d.team == self.rr_id) & (d.group == "IPL")).astype(int)
        self.rows = {"bat": bat.reset_index(drop=True), "bowl": bowl.reset_index(drop=True)}
        self.um = np.unique(np.concatenate([bat.match_id.values, bowl.match_id.values]))
        for role, own, opp in (("bat", self.all_bat, self.all_bowl), ("bowl", self.all_bowl, self.all_bat)):
            r = self.rows[role]
            r["own_ix"] = np.searchsorted(own, r.player.values); r["opp_ix"] = np.searchsorted(opp, r.opp.values)
            assert (own[r.own_ix] == r.player.values).all() and (opp[r.opp_ix] == r.opp.values).all()
            r["m_ix"] = np.searchsorted(self.um, r.match_id.values)
        pr = pd.read_parquet(OUT / "balls_pressure.parquet", columns=["match_id", "innings", "innings_ball_num", "LI", "live"])
        pr = pr[pr.live]
        self.live_li = pr.LI.values; self.live_li_inn = pr[["innings", "LI"]]
        ch = json.load(open(OUT / "stage4_choices.json")); self.lb, self.lc = ch["lambda_B"], ch["lambda_C"]
        self.bs = bs

    # ---------------- pressure flag variants (same definitions as stage6b_sensitivity.flags) ----------------
    def flag(self, rows, variant):
        if variant == "main": return rows.P.values.astype(int)
        if variant.startswith("top"):
            q = int(variant[3:-1]) / 100
            return (rows.LI.values >= np.quantile(self.live_li, 1 - q)).astype(int)
        if variant == "within_innings":
            t = {i: np.quantile(self.live_li_inn[self.live_li_inn.innings == i].LI.values, 0.8) for i in (1, 2)}
            return (rows.LI.values >= rows.innings.map(t).values).astype(int)
        raise ValueError(variant)

    def weights_replay(self):
        """Replays stage5_bootstrap's resampling (same seed, same draw order) -> (n_boot+1, n_matches); row 0 = ones (point estimate)."""
        rng = np.random.default_rng(CFG["seed"]); n = len(self.um)
        W = np.ones((R["bootstrap_n"] + 1, n))
        for i in range(R["bootstrap_n"]):
            W[i + 1] = np.bincount(rng.integers(0, n, n), minlength=n)
        return W

    def designs(self, P_bat, P_bowl):
        bat = self.rows["bat"].assign(P=P_bat); bowl = self.rows["bowl"].assign(P=P_bowl)
        return RM.Design(bat, self.all_bat, self.all_bowl), RM.Design(bowl, self.all_bowl, self.all_bat)

    def refit_terms(self, P_bat, P_bowl, Wm, log=print, only=None):
        """Point fit + one refit per bootstrap weight row (penalties fixed). Returns dict B,C (batters), W,K (bowlers), each (n_boot+1, n_players)."""
        Db, Dw = self.designs(P_bat, P_bowl)
        lam_b, lam_w = Db.lam(self.lb, self.lc, R["context_lambda"]), Dw.lam(self.lb, self.lc, R["context_lambda"])
        mb, mw = np.searchsorted(self.um, Db.match), np.searchsorted(self.um, Dw.match)
        idx = range(Wm.shape[0]) if only is None else only
        nb = len(list(idx))
        B = np.empty((nb, len(self.all_bat))); C = np.empty_like(B); Wt = np.empty((nb, len(self.all_bowl))); K = np.empty_like(Wt)
        for j, i in enumerate(idx):
            w = Wm[i]
            B[j], C[j] = Db.own(Db.fit(lam_b, None if i == 0 else w[mb])); Wt[j], K[j] = Dw.own(Dw.fit(lam_w, None if i == 0 else w[mw]))
            if j % 100 == 0: log(f"   refit {j}/{nb - 1}")
        return dict(B=B, C=C, W=Wt, K=K)

    def main_terms(self):
        z = np.load(OUT / "bootstrap_ratings.npz")
        rb, cb, rw, cw = (z[k].astype(float) for k in ("rb", "cb", "rw", "cw"))
        br, wr = self.ratings["bat"], self.ratings["bowl"]
        return dict(B=np.vstack([br.B.values, rb - cb]), C=np.vstack([br.C.values, cb]), W=np.vstack([wr.W.values, rw - cw]), K=np.vstack([wr.K.values, cw]))


class Engine:
    """Weighted sums at key level (player, grp, rr, slot, P) for every replicate. Row 0 = point estimate (unit weights, point-fit terms).

    adjusted value  adj = v + (opposition term):  batter row -> bowler's W + P*K ;  bowler row -> batter's B + P*C
    (the published rating terms, taken from the same replicate, so opposition uncertainty is inside the interval).
    """

    def __init__(self, data, P_bat, P_bowl, terms, Wm):
        self.d = data; self.out = {}; self.Wm = Wm
        for role in ("bat", "bowl"):
            rows = data.rows[role]; P = P_bat if role == "bat" else P_bowl
            key_t = np.stack([rows.own_ix.values, rows.grp.values, rows.rr.values, rows.slot.values, P], 1)
            uk, inv = np.unique(key_t, axis=0, return_inverse=True); inv = inv.ravel()
            nk = len(uk); nr = Wm.shape[0]
            S = np.zeros((nr, nk)); Wt = np.zeros((nr, nk)); SW = np.zeros((nr, nk)); SSW = np.zeros((nr, nk)); NB = np.zeros((nr, nk))
            v = rows.v.values; sw = rows.swing.values; isb = rows.is_ball.values.astype(float); opp = rows.opp_ix.values; m_ix = rows.m_ix.values
            ta, tb = (terms["W"], terms["K"]) if role == "bat" else (terms["B"], terms["C"])
            for r in range(nr):
                w = Wm[r][m_ix]
                adj = v + ta[r][opp] + P * tb[r][opp]
                S[r] = np.bincount(inv, w * adj, nk); Wt[r] = np.bincount(inv, w, nk); SW[r] = np.bincount(inv, w * sw, nk)
                SSW[r] = np.bincount(inv, w * adj * sw, nk); NB[r] = np.bincount(inv, w * isb, nk)
            self.out[role] = dict(uk=uk, S=S, W=Wt, SW=SW, SSW=SSW, NB=NB)
        rrm = np.unique(data.rows["bat"][data.rows["bat"].rr == 1].match_id.values)
        self.rr_matches = rrm
        self.n_inn = Wm[:, np.searchsorted(data.um, rrm)].sum(1)      # weighted RR innings per side (each RR match = 1 batting + 1 bowling innings)

    def mask(self, role, **kw):
        uk = self.out[role]["uk"]; m = np.ones(len(uk), bool)
        for k, val in kw.items():
            m &= np.isin(uk[:, {"own": 0, "grp": 1, "rr": 2, "slot": 3, "P": 4}[k]], val)
        return m

    def sums(self, role, mask):
        o = self.out[role]
        return {k: o[k][:, mask].sum(1) for k in ("S", "W", "SW", "SSW", "NB")}


def interval(x):
    """x[0] = point estimate, x[1:] = bootstrap replicates."""
    x = np.asarray(x, float); b = x[1:]; ok = ~np.isnan(b)
    q = lambda a: float(np.quantile(b[ok], a)) if ok.sum() > 10 else np.nan
    return dict(est=float(x[0]), p025=q(0.025), p10=q(0.10), p90=q(0.90), p975=q(0.975), p_below0=float((b[ok] < 0).mean()) if ok.sum() else np.nan)


def verdict(iv, direction="below"):
    """Plain-language call on a gap vs par from its bootstrap interval (both conventions shown)."""
    if np.isnan(iv["p10"]): return "no estimate"
    if iv["p975"] < 0: return "below par (95% interval excludes 0)"
    if iv["p90"] < 0: return "below par (80% interval excludes 0; 95% does not)"
    if iv["p025"] > 0: return "above par (95% interval excludes 0)"
    if iv["p10"] > 0: return "above par (80% interval excludes 0; 95% does not)"
    return "not distinguishable from par"
