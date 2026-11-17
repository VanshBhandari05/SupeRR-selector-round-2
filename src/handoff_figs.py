"""New figure exports for the handoff pack. Colour grammar: blue = normal, pink = pressure. Large text for slides.
Every figure is drawn from existing pipeline results (read-only). PNG at 1920 px wide plus SVG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.collections import LineCollection

import handoff_data as H

BLUE, PINK, GREY, INK, PALE = "#254AA5", "#EA1A85", "#6b7280", "#0B1740", "#E8ECF8"
plt.rcParams.update({"font.size": 16, "axes.titlesize": 20, "axes.labelsize": 16, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "path", "axes.edgecolor": INK, "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
FIG = H.PACK / "08_FIGURES"
FIG.mkdir(parents=True, exist_ok=True)
MADE = []   # (file stem, title)


def save(fig, stem, title):
    fig.savefig(FIG / f"{stem}.png", dpi=120)
    fig.savefig(FIG / f"{stem}.svg")
    plt.close(fig)
    MADE.append((stem, title))


def f169(**kw):
    return plt.subplots(figsize=(16, 9), **kw)


# ---------------------------------------------------------------- F01 leverage heatmap: balls left x runs required (innings 2)
def fig_heatmap():
    g = H.heatmap_data()
    piv = g.pivot(index="rr", columns="bl", values="mean").sort_index()
    cols = sorted(piv.columns, reverse=True)
    piv = piv[cols]
    cut = H.THR["p80"]
    cmap = LinearSegmentedColormap.from_list("bp", [BLUE, "#EEF1FA", PINK])
    norm = TwoSlopeNorm(vmin=0.2, vcenter=cut, vmax=3.0)
    fig, ax = f169()
    im = ax.imshow(piv.values, origin="lower", aspect="auto", cmap=cmap, norm=norm)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([str(c) for c in cols], fontsize=12, rotation=90)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([str(i) for i in piv.index], fontsize=12)
    ax.set_xlabel("balls left in the chase (upper edge of a 6-ball band)")
    ax.set_ylabel("runs required (upper edge of a 10-run band)")
    ax.set_title(f"Where pressure lives in a chase (pink = mean LI above the cutoff {cut:.3f})", fontsize=19)
    cb = fig.colorbar(im, ax=ax)
    cb.set_label("mean leverage index (LI), live balls")
    fig.text(0.01, 0.01, f"Source: outputs/balls_pressure.parquet joined to balls_state.parquet; innings 2, live balls, 808 clean matches; cells with at least {H.CFG['stage3']['heatmap_min_balls']} balls.", fontsize=11, color=GREY)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    save(fig, "F01_leverage_heatmap_balls_left_x_runs_required", "Leverage heatmap, balls left x runs required (chase)")
    return int(g["size"].sum()), len(g)


# ---------------------------------------------------------------- F02 calibration deciles (parsed from audit_stage2.md)
def fig_calibration():
    t = H.rd(H.OUT / "audit_stage2.md")
    fig, axs = plt.subplots(1, 2, figsize=(16, 9), sharey=True)
    for ax, inn in zip(axs, (1, 2)):
        d = H.table_from(H.sec(t, f"Deciles, WP* (innings {inn})"))
        obs = d.obs
        lo = d.pred - d.gap_hi
        hi = d.pred - d.gap_lo
        ax.plot([0, 1], [0, 1], color=GREY, lw=2, ls="--", label="perfect calibration")
        ax.errorbar(d.pred, obs, yerr=[obs - lo, hi - obs], fmt="o", color=PINK, ecolor=PINK, ms=11, capsize=5, lw=2, label="decile, 95% match-bootstrap interval")
        ax.set_title(f"Innings {inn}: predicted vs observed win rate")
        ax.set_xlabel("predicted win probability (WP*)")
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.1, 1.1)
        ax.text(0.03, 0.9, f"largest decile gap {d.gap.abs().max():.3f}\n(limit {H.CFG['calibration']['decile_tolerance']})", fontsize=16, transform=ax.transAxes)
    axs[0].set_ylabel("observed win rate (leave-one-season-out)")
    axs[0].legend(loc="lower right", fontsize=13)
    fig.tight_layout()
    save(fig, "F02_calibration_deciles", "Calibration of the win-probability model by decile, held-out seasons")


# ---------------------------------------------------------------- F03 one clean match trace (16662, Pakistan won by 1 wicket) + all six series exported as CSV
def fig_trace(tf, mid=16662):
    d = tf[tf.match_id == mid].reset_index(drop=True)
    m = H.MFLAGS[H.MFLAGS.match_id == mid].iloc[0]
    x = d.innings_ball_num.values
    y = d.LI.values
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    seg = np.concatenate([pts[:-1], pts[1:]], axis=1)
    cut = H.THR["p80"]
    fig, ax = f169()
    lc = LineCollection(seg, colors=[PINK if v >= cut else BLUE for v in y[:-1]], linewidths=3.5)
    ax.add_collection(lc)
    ax.axhline(cut, color=GREY, ls="--", lw=2)
    ax.text(2, cut + 0.25, f"pressure cutoff LI = {cut:.3f}", color=GREY, fontsize=14)
    ax.set_xlim(0, x.max() + 2)
    ax.set_ylim(0, max(y.max() * 1.08, 4))
    ax.set_xlabel("ball of the chase")
    ax.set_ylabel("leverage index (LI)")
    ax2 = ax.twinx()
    ax2.plot(x, d.wp_star, color=GREY, lw=2, alpha=0.8)
    ax2.set_ylim(0, 1)
    ax2.set_ylabel("chasing side's win probability (WP*, grey)")
    ax2.spines["right"].set_visible(True)
    pk = d.loc[d.LI.idxmax()]
    ax.annotate(f"peak LI {pk.LI:.1f} on ball {int(pk.innings_ball_num)} (over {int(pk.overid)})", xy=(pk.innings_ball_num, pk.LI), xytext=(pk.innings_ball_num - 55, pk.LI * 0.92), fontsize=15,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_title(f"Match {mid}, {m.match_date}: {m.home_team} v {m.away_team}. {m.result}. Pink = pressure ball, blue = ordinary")
    fig.tight_layout()
    save(fig, "F03_match_trace_16662", "Leverage and win probability through one tight chase")


# ---------------------------------------------------------------- F04 raw vs shrunk for the 20 listed players
def raw_shrunk_table():
    rows = []
    for role in ("batters", "bowlers"):
        t = H.TOP[role].merge(H.UNF[role][["player_id", "simple_rating"]], on="player_id", how="left").merge(H.RAW[role][["raw_pressure_mean_v", "n_P"]], left_on="player_id", right_index=True, how="left")
        for _, r in t.iterrows():
            rows.append(dict(role=role, rank=int(r["rank"]), player_id=int(r.player_id), name=r["name"], pressure_balls=int(r.n_P), raw_mean_value_on_pressure_balls=r.raw_pressure_mean_v,
                             simple_shrunk_rating=r.simple_rating, final_ridge_pressure_rating=r.pressure_rating, baseline=r.baseline, shift=r["shift"]))
    return pd.DataFrame(rows)


def fig_raw_shrunk(rs):
    fig, axs = plt.subplots(1, 2, figsize=(16, 9))
    for ax, role in zip(axs, ("batters", "bowlers")):
        d = rs[rs.role == role].iloc[::-1].reset_index(drop=True)
        y = np.arange(len(d))
        for i, r in d.iterrows():
            ax.plot([r.final_ridge_pressure_rating, r.raw_mean_value_on_pressure_balls], [i, i], color="#c9cfe6", lw=3, zorder=1)
        ax.scatter(d.raw_mean_value_on_pressure_balls, y, s=170, facecolor="white", edgecolor=BLUE, lw=3, label="raw: unshrunk mean value, pressure balls", zorder=3)
        ax.scatter(d.simple_shrunk_rating, y, s=120, marker="D", color=BLUE, label="simple shrunk (no opposition terms)", zorder=3)
        ax.scatter(d.final_ridge_pressure_rating, y, s=190, color=PINK, label="final ridge pressure rating", zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels(d.name, fontsize=15)
        ax.axvline(0, color=GREY, lw=1)
        ax.set_xlabel("value per ball (units of expected swing)")
        ax.set_title(f"Top 10 {role}")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=14, frameon=False)
    fig.suptitle("Raw vs shrunk ratings of the 20 listed players", fontsize=22)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "F04_raw_vs_shrunk", "Raw vs shrunk ratings, 20 listed players")


# ---------------------------------------------------------------- F05 baseline vs pressure rating scatter with intervals
def fig_scatter():
    fig, axs = plt.subplots(1, 2, figsize=(16, 9))
    for ax, role in zip(axs, ("batters", "bowlers")):
        e = H.UNF[role].copy()
        e["baseline_"] = e["B"] if role == "batters" else e["W"]
        listed = set(H.TOP[role].player_id)
        col = [PINK if p in listed else BLUE for p in e.player_id]
        ax.errorbar(e.baseline_, e.pressure_rating, yerr=[e.pressure_rating - e.floor_p10, e.p90 - e.pressure_rating], fmt="none", ecolor="#c9cfe6", lw=2, zorder=1)
        ax.scatter(e.baseline_, e.pressure_rating, c=col, s=90, zorder=3)
        lo, hi = min(e.baseline_.min(), e.pressure_rating.min()) - 0.02, max(e.baseline_.max(), e.pressure_rating.max()) + 0.02
        ax.plot([lo, hi], [lo, hi], color=GREY, ls="--", lw=1.5)
        for _, r in e[e.player_id.isin(listed)].iterrows():
            ax.annotate(r["name"].split()[-1], (r.baseline_, r.pressure_rating), textcoords="offset points", xytext=(6, 6), fontsize=12)
        ax.set_xlabel("baseline (normal balls)")
        ax.set_ylabel("pressure rating = baseline + shift (bars: 10th-90th percentile)")
        ax.set_title(f"{role.capitalize()}: eligible players (pink = listed top 10)")
    fig.tight_layout()
    save(fig, "F05_baseline_vs_pressure_scatter", "Baseline vs pressure rating with bootstrap intervals")


# ---------------------------------------------------------------- F06 stability chart (rank intervals)
def fig_stability():
    fig, axs = plt.subplots(1, 2, figsize=(16, 9))
    for ax, role in zip(axs, ("batters", "bowlers")):
        t = H.TOP[role].iloc[::-1].reset_index(drop=True)
        y = np.arange(len(t))
        ax.axvspan(0.5, 10.5, color=PALE, zorder=0)
        for i, r in t.iterrows():
            ax.plot([r.rank_p10, r.rank_p90], [i, i], color=PINK, lw=5, solid_capstyle="round", zorder=2)
            ax.scatter([r["rank"]], [i], s=150, color=INK, zorder=3)
            ax.text(max(r.rank_p90, 12) + 1.2, i, f"P(top10) {r.p_top10:.2f}  P(top20) {r.p_top20:.2f}", va="center", fontsize=12)
        ax.set_yticks(y)
        ax.set_yticklabels(t.name, fontsize=14)
        ax.set_xlim(0, 44)
        ax.set_xlabel("rank in pool (dot = listed rank; bar = 10th-90th pct of 300 resamples)", fontsize=13)
        ax.set_title(f"Top 10 {role}")
    fig.tight_layout()
    save(fig, "F06_rank_stability", "Rank stability of the 20 listed players")


# ---------------------------------------------------------------- F07 sensitivity / fragile table
def fig_sensitivity():
    fig, axs = plt.subplots(2, 1, figsize=(16, 12))
    for ax, role in zip(axs, ("batters", "bowlers")):
        t = H.TOP[role]
        m = H.VM[role].loc[t.player_id].astype(int)
        ax.imshow(m.values, aspect="auto", cmap=LinearSegmentedColormap.from_list("x", [PALE, PINK]), vmin=0, vmax=1)
        ax.set_xticks(range(len(m.columns)))
        ax.set_xticklabels([c.replace("_", " ") for c in m.columns], rotation=35, ha="right", fontsize=12)
        ax.set_yticks(range(len(t)))
        ax.set_yticklabels([f"{r['rank']}. {r['name']}  ({int(r.variants_in_top10)}/14)" for _, r in t.iterrows()], fontsize=13)
        ax.set_title(f"{role.capitalize()}: pink = in the top 10 under that variant (floor proxy), pale = out")
        for s in ax.spines.values():
            s.set_visible(False)
    fig.tight_layout()
    save(fig, "F07_sensitivity_fragile_table", "Sensitivity: which listed players stay in the top 10 under each of 14 variants")


# ---------------------------------------------------------------- top-10 images
def fig_top10(role):
    t = H.TOP[role].iloc[::-1].reset_index(drop=True)
    y = np.arange(len(t))
    fig, ax = f169()
    ax.barh(y + 0.19, t.baseline, height=0.34, color=BLUE, label="baseline (normal balls)")
    ax.barh(y - 0.19, t.pressure_rating, height=0.34, color=PINK, label="pressure rating")
    ax.errorbar(t.pressure_rating, y - 0.19, xerr=[t.pressure_rating - t.floor_p10, t.p90 - t.pressure_rating], fmt="none", ecolor=INK, capsize=5, lw=2)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['rank']}. {r['name']}" for _, r in t.iterrows()], fontsize=19)
    for i, r in t.iterrows():
        ax.text(r.p90 + 0.006, i - 0.19, f"{r.pressure_rating:.3f}", va="center", fontsize=16, color=INK)
        ax.text(0.40, i, r.teams, va="center", ha="left", fontsize=13, color=GREY)
    ax.set_xlim(0, 0.62)
    ax.set_xlabel("rating per ball (units of expected swing in win probability); black bar = 10th to 90th percentile", fontsize=14)
    ax.set_title(f"Top 10 {role}: ranked by floor (10th percentile of pressure rating)", fontsize=22)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=15, frameon=False)
    fig.tight_layout()
    save(fig, f"F08_top10_{role}", f"Top 10 {role} (one image)")


# ---------------------------------------------------------------- paired bars: pressure vs ordinary, league-wide raw rates
def fig_paired():
    o = H.LEAGUE["overall"]
    metrics = [("sr", "Strike rate (runs per 100 balls)"), ("dismissal_pct", "Dismissal rate (% of balls faced)"), ("dot_pct", "Dot-ball share (%)"),
               ("boundary_pct", "Boundary share (%)"), ("economy", "Economy (runs per over)"), ("balls_per_wicket", "Balls per wicket")]
    fig, axs = plt.subplots(2, 3, figsize=(16, 9))
    for ax, (k, ttl) in zip(axs.ravel(), metrics):
        v = [o["normal"][k], o["pressure"][k]]
        b = ax.bar(["normal", "pressure"], v, color=[BLUE, PINK], width=0.6)
        for r, val in zip(b, v):
            ax.text(r.get_x() + r.get_width() / 2, val, f"{val:g}", ha="center", va="bottom", fontsize=18)
        ax.set_title(ttl, fontsize=15)
        ax.set_ylim(0, max(v) * 1.2)
        ax.tick_params(labelsize=15)
    fig.suptitle("Pressure vs ordinary balls, league-wide (live balls of 728 rated matches, raw rates)", fontsize=20)
    fig.text(0.01, 0.005, "Source: website/data/league_split.json 'overall'. Raw rates, NOT standardised by phase and wickets (stratified comparison: 03_EVIDENCE_DEFINITION.md).", fontsize=10.5, color=GREY)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    save(fig, "F09_pressure_vs_ordinary_paired_bars", "Pressure vs ordinary, league-wide paired bars")


# ---------------------------------------------------------------- F10 close games vs the rest (re-render of stage3_close_games.png at full width, same definitions)
def fig_close():
    from scipy.stats import spearmanr
    S3 = H.CFG["stage3"]
    bp = pd.read_parquet(H.OUT / "balls_pressure.parquet", columns=["match_id", "LI"])
    peak = bp.groupby("match_id").LI.max().rename("peak_LI").reset_index()
    mf = H.MFLAGS
    mm = mf[mf.clean][["match_id", "rtype", "margin"]].merge(peak, on="match_id")
    mm["close"] = (mm.rtype == "tie") | ((mm.rtype == "runs") & (mm.margin <= S3["close_runs"])) | ((mm.rtype == "wickets") & (mm.margin <= S3["close_wickets"]))
    runs_m = mm[mm.rtype == "runs"]
    sp = spearmanr(runs_m.margin, runs_m.peak_LI).correlation
    med_c, med_o = mm[mm.close].peak_LI.median(), mm[~mm.close].peak_LI.median()
    assert int(mm.close.sum()) == 137 and (~mm.close).sum() == 671 and round(med_c, 4) == 10.1484 and round(med_o, 4) == 1.6001 and round(sp, 3) == -0.853, (mm.close.sum(), med_c, med_o, sp)
    fig, axs = plt.subplots(1, 2, figsize=(16, 9))
    lab_o = "all other matches (n=%d)" % int((~mm.close).sum())
    lab_c = "close matches (n=%d)" % int(mm.close.sum())
    bx = axs[0].boxplot([mm[~mm.close].peak_LI, mm[mm.close].peak_LI], tick_labels=[lab_o, lab_c], showfliers=False, patch_artist=True, widths=0.55)
    for patch, col in zip(bx["boxes"], (BLUE, PINK)):
        patch.set_facecolor(col)
        patch.set_alpha(0.85)
    for m_ in bx["medians"]:
        m_.set_color(INK)
        m_.set_linewidth(3)
    axs[0].set_ylabel("peak leverage (LI) in the match")
    axs[0].set_title(f"Median peak LI: {med_c:.1f} (close) vs {med_o:.1f} (other)")
    axs[1].scatter(runs_m.margin, runs_m.peak_LI, s=28, alpha=0.55, color=BLUE)
    axs[1].set_xlabel("winning margin (runs), matches won by runs")
    axs[1].set_ylabel("peak leverage (LI)")
    axs[1].set_title(f"Spearman {sp:.3f} between peak LI and margin (n={len(runs_m)})")
    fig.suptitle("Pressure concentrates in games that finished tight (margin is never an input)", fontsize=21)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "F10_close_games_vs_rest", "Peak leverage in close games vs the rest, and against margin")


def build_all(tf):
    info = {}
    info["heat_balls"], info["heat_cells"] = fig_heatmap()
    fig_calibration()
    fig_trace(tf)
    rs = raw_shrunk_table()
    fig_raw_shrunk(rs)
    fig_scatter()
    fig_stability()
    fig_sensitivity()
    fig_top10("batters")
    fig_top10("bowlers")
    fig_paired()
    fig_close()
    return rs, info
