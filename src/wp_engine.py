"""Stage 2a/2b engine: next-ball scoring model + exact win probability by backward induction.

Pure functions, no I/O. Used by stage2_run.py. All thresholds come from config.yaml.
"""
import numpy as np
import numba as nb
from scipy import sparse
from sklearn.linear_model import LogisticRegression

# outcome classes: 0 W, 1 R0, 2 R1, 3 R2, 4 R3, 5 R4, 6 R6 (legal) ; 7 I1, 8 I2, 9 I3+ (illegal)
N_CLASS = 10
LEGAL_CLASSES = 7
GROUPS = ["IPL", "A-team", "T20I-full", "T20I-assoc"]
CLASS_NAMES = ["W", "0", "1", "2", "3", "4", "6", "wd/nb 1", "wd/nb 2", "wd/nb 3+"]


def outcome_class(is_legal, is_wicket, team_runs):
    tr = np.asarray(team_runs)
    oc = np.empty(len(tr), dtype=np.int8)
    legal_map = np.array([1, 2, 3, 4, 5, 5, 6])            # runs 0..6 -> class; 5 folds into the 4 class
    lm = legal_map[np.clip(tr, 0, 6)]
    il = np.where(tr <= 1, 7, np.where(tr == 2, 8, 9))
    oc[:] = np.where(is_legal, lm, il)
    oc[np.asarray(is_wicket)] = 0                           # any wicket (incl. on a wide/no-ball) -> W, consumes the ball
    return oc


def class_run_values(oc, team_runs, is_legal):
    """Run value of each class: exact for 0,1,2,3,4,6; I3+ valued at its observed mean."""
    v = np.array([0, 0, 1, 2, 3, 4, 6, 1, 2, 0], dtype=float)
    m = oc == 9
    v[9] = float(np.round(np.asarray(team_runs)[m].mean())) if m.any() else 5.0
    return v


class Bands:
    def __init__(self, sm):
        self.over_edges = np.array(sm["over_band_starts"])
        self.n_over = len(self.over_edges)
        self.wk_max = sm["wicket_band_max"]
        self.n_wk = self.wk_max + 1
        self.rr_edges = np.array(sm["rr_band_edges"])
        self.n_rr = len(self.rr_edges) + 1
        self.use_tier = sm["use_env_tier"]

    def over_band(self, over):
        return np.searchsorted(self.over_edges, over, side="right") - 1

    def wk_band(self, w):
        return np.minimum(w, self.wk_max)

    def rr_band(self, rr):
        return np.searchsorted(self.rr_edges, rr, side="right")

    def design(self, over, wk, tier, imp, grp, rr=None):
        ob, wb = self.over_band(over), self.wk_band(wk)
        blocks = [(ob, self.n_over), (wb, self.n_wk)]
        if self.use_tier:
            blocks.append((tier, 3))
        blocks += [(imp.astype(int), 2), (grp, 4), (ob * self.n_wk + wb, self.n_over * self.n_wk)]
        if rr is not None:
            rb = self.rr_band(rr)
            blocks += [(rb, self.n_rr), (rb * self.n_over + ob, self.n_rr * self.n_over)]
        n = len(ob)
        off, cols = 0, []
        for idx, size in blocks:
            cols.append(np.asarray(idx) + off)
            off += size
        cols = np.column_stack(cols)
        rows = np.repeat(np.arange(n), cols.shape[1])
        return sparse.csr_matrix((np.ones(cols.size), (rows, cols.ravel())), shape=(n, off))


def fit_scoring(bands, sm, over, wk, tier, imp, grp, oc, rr=None, C=1.0):
    X = bands.design(over, wk, tier, imp, grp, rr)
    clf = LogisticRegression(C=C, max_iter=sm["max_iter"])
    clf.fit(X, oc)
    assert list(clf.classes_) == list(range(N_CLASS)), "an outcome class is missing from the training data"
    return clf


def over_from_balls_left(b):
    return 20 - (np.asarray(b) - 1) // 6


# ----------------------------------------------------------------- dynamic programs
@nb.njit(cache=True)
def _solve_wp2(P, runs, n_max):
    B = P.shape[0] - 1
    wp = np.zeros((B + 1, 11, n_max + 1))
    for b in range(B + 1):
        for w in range(11):
            wp[b, w, 0] = 1.0
            if b == 0 or w == 10:
                wp[b, w, 1] = 0.5            # scores level when the innings ends: a tie
    for b in range(1, B + 1):
        for w in range(10):
            for n in range(1, n_max + 1):
                s = 0.0
                for k in range(10):
                    p = P[b, w, n, k]
                    n2 = n - int(runs[k])
                    if k < 7:
                        w2 = w + 1 if k == 0 else w
                        v = 1.0 if n2 <= 0 else wp[b - 1, w2, n2]
                    else:
                        v = 1.0 if n2 <= 0 else wp[b, w, n2]
                    s += p * v
                wp[b, w, n] = s
    return wp


@nb.njit(cache=True)
def _solve_runs_to_come(P1, runs, x_max):
    B = P1.shape[0] - 1
    D = np.zeros((B + 1, 11, x_max + 1))
    for b in range(B + 1):
        for w in range(11):
            if b == 0 or w == 10:
                D[b, w, 0] = 1.0
    for b in range(1, B + 1):
        for w in range(10):
            for x in range(x_max + 1):
                s = 0.0
                for k in range(7):
                    r = int(runs[k])
                    if x - r >= 0:
                        w2 = w + 1 if k == 0 else w
                        s += P1[b, w, k] * D[b - 1, w2, x - r]
                for k in range(7, 10):
                    r = int(runs[k])
                    if x - r >= 0:
                        s += P1[b, w, k] * D[b, w, x - r]
                D[b, w, x] = s
    return D


@nb.njit(cache=True)
def _wp1_lookup(D, wp2_start, b, w, r):
    out = np.empty(len(b))
    n_max = len(wp2_start) - 1
    x_max = D.shape[2] - 1
    for i in range(len(b)):
        s = 0.0
        for x in range(x_max + 1):
            t = r[i] + x + 1
            v = 1.0 if t > n_max else 1.0 - wp2_start[t]
            s += D[b[i], w[i], x] * v
        out[i] = s
    return out


def _env_avg(x, axis, increasing):
    """Average of the lower and upper monotone envelopes along one axis (approximates isotonic regression)."""
    x = np.moveaxis(x, axis, 0)
    if increasing:
        lo = np.minimum.accumulate(x[::-1], axis=0)[::-1]; hi = np.maximum.accumulate(x, axis=0)
    else:
        lo = np.minimum.accumulate(x, axis=0); hi = np.maximum.accumulate(x[::-1], axis=0)[::-1]
    return np.moveaxis((lo + hi) / 2, 0, axis)


def project_monotone(wp):
    """Chase surface wp[b, w, n]: non-increasing in w and n, non-decreasing in b. Terminals are re-imposed afterwards."""
    x = _env_avg(wp.astype(np.float64), 1, increasing=False)    # more wickets lost -> lower
    x = _env_avg(x, 0, increasing=True)                         # more balls left -> higher
    x = _env_avg(x, 2, increasing=False)                        # more runs required -> lower
    x[:, :, 0] = 1.0
    x[0, :, 2:] = 0.0; x[0, :, 1] = 0.5
    x[:, 10, 2:] = 0.0; x[:, 10, 1] = 0.5
    return np.clip(x, 0.0, 1.0)


def monotone_violations(w2, n_cap=250):
    w2 = w2[:, :, :n_cap].astype(float)
    return dict(up_in_runs_required=float(np.maximum(w2[:, :, 1:] - w2[:, :, :-1], 0).max()),
                up_in_wickets_lost=float(np.maximum(w2[1:, 1:10, 1:] - w2[1:, 0:9, 1:], 0).max()),
                down_in_balls_left=float(np.maximum(w2[1:-1, :10, 1:] - w2[2:, :10, 1:], 0).max()))


@nb.njit(cache=True)
def wp1_table(D, wp2_start, r_max):
    """WP1[b, w, r] = sum_x D[b, w, x] * (1 - WP2(120, 0, r + x + 1)) for every state (b 0..120, w 0..10, r 0..r_max)."""
    B, W, X = D.shape[0], D.shape[1], D.shape[2]
    n_max = len(wp2_start) - 1
    out = np.zeros((B, W, r_max + 1))
    for b in range(B):
        for w in range(W):
            for r in range(r_max + 1):
                s = 0.0
                for x in range(X):
                    p = D[b, w, x]
                    if p == 0.0:
                        continue
                    t = r + x + 1
                    s += p * (1.0 if t > n_max else 1.0 - wp2_start[t])
                out[b, w, r] = s
    return out


class Surface:
    """Win-probability surface for one (group, impact_rule) configuration (env_tier is a constant 0 when unused)."""

    def __init__(self, m1, m2, bands, cfg, n_max, x_max, runs, project=False):
        grp, tier, imp = cfg
        self.cfg, self.n_max, self.runs = cfg, n_max, runs
        # innings 2 states (b=1..120, w=0..9, n=1..n_max)
        b = np.arange(1, 121); w = np.arange(10); n = np.arange(1, n_max + 1)
        bb, ww, nn = np.meshgrid(b, w, n, indexing="ij")
        bb, ww, nn = bb.ravel(), ww.ravel(), nn.ravel()
        rr = nn * 6.0 / bb
        X = bands.design(over_from_balls_left(bb), ww, np.full(bb.size, tier), np.full(bb.size, imp), np.full(bb.size, grp), rr)
        pr = m2.predict_proba(X)
        P = np.zeros((121, 10, n_max + 1, N_CLASS))
        P[bb, ww, nn, :] = pr
        wp2 = _solve_wp2(P, runs, n_max)
        self.wp2_unprojected = wp2.astype(np.float32)
        self.wp2 = (project_monotone(wp2) if project else wp2).astype(np.float32)
        # innings 1 states (b, w)
        b1, w1 = np.meshgrid(b, w, indexing="ij"); b1, w1 = b1.ravel(), w1.ravel()
        X1 = bands.design(over_from_balls_left(b1), w1, np.full(b1.size, tier), np.full(b1.size, imp), np.full(b1.size, grp))
        P1 = np.zeros((121, 10, N_CLASS)); P1[b1, w1, :] = m1.predict_proba(X1)
        self.P1, self.P2_start = P1, None
        self.D = _solve_runs_to_come(P1, runs, x_max).astype(np.float32)
        self.runs_to_come_mean = (self.D[120, 0] * np.arange(x_max + 1)).sum()

    def wp_chase(self, b, w, n):
        return self.wp2[b, np.minimum(w, 10), np.clip(n, 0, self.n_max)]

    def wp_first(self, b, w, r):
        return _wp1_lookup(self.D, self.wp2[120, 0].astype(np.float64), np.asarray(b), np.asarray(w), np.asarray(r))


def logit(p, eps):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def fit_recal(raw, y, eps):
    """logit(WP*) = a + c * logit(WP). Returns (a, c)."""
    z = logit(raw, eps).reshape(-1, 1)
    lr = LogisticRegression(penalty=None, max_iter=200).fit(z, y)
    return float(lr.intercept_[0]), float(lr.coef_[0, 0])


def apply_recal(raw, a, c, eps):
    return 1 / (1 + np.exp(-(a + c * logit(raw, eps))))
