"""Stage 8: charts and tables for the report. Run after Stage 7:  python -I src/stage8_exhibits.py
Writes figures/stage8_*.png and outputs/report_tables.md
"""
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
OUT = ROOT / CFG["paths"]["out_dir"]; FIG = ROOT / "figures"
mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv").drop_duplicates("player_id").set_index("player_id").player_name
BLUE, ORANGE, GREY = "#2a6fbb", "#d95f02", "#9a9a9a"

fig, axes = plt.subplots(2, 2, figsize=(15, 11))
for k, (role, bcol, scol) in enumerate((("batters", "B", "C"), ("bowlers", "W", "K"))):
    r = pd.read_csv(OUT / f"player_ratings_{role}.csv"); top = pd.read_csv(OUT / f"top10_{role}.csv"); e = r[r.eligible]
    ax = axes[0, k]
    ax.errorbar(e[bcol], e.pressure_rating, yerr=[e.pressure_rating - e.floor_p10, e.p90 - e.pressure_rating], fmt="o", color=GREY, ms=3.5, alpha=.55, lw=.7, label="eligible players (10th-90th pct)")
    t = r[r.player_id.isin(top.player_id)].merge(top[["player_id", "rank"]], on="player_id")
    ax.errorbar(t[bcol], t.pressure_rating, yerr=[t.pressure_rating - t.floor_p10, t.p90 - t.pressure_rating], fmt="o", color=BLUE, ms=6, lw=1.4, label="listed top 10")
    for _, x in t.iterrows(): ax.annotate(f"{int(x['rank'])} {mp.get(x.player_id, '')}", (x[bcol], x.pressure_rating), fontsize=7, xytext=(4, 3), textcoords="offset points")
    lim = [min(e[bcol].min(), e.pressure_rating.min()), max(e[bcol].max(), e.pressure_rating.max())]; ax.plot(lim, lim, color=ORANGE, lw=1, ls="--", label="pressure rating = baseline")
    ax.set_xlabel(f"baseline rating ({bcol})"); ax.set_ylabel("pressure rating (baseline + shift)"); ax.set_title(f"{role.title()}: baseline vs pressure rating with intervals", fontsize=10); ax.legend(fontsize=8)
    ax = axes[1, k]
    ax.scatter(e.simple_rating, e.pressure_rating, s=14, color=BLUE, alpha=.7)
    ax.set_xlabel("simple shrunk rating (no opposition adjustment)"); ax.set_ylabel("regression pressure rating"); ax.set_title(f"{role.title()}: cross-check, simple vs regression", fontsize=10)
    for a in (axes[0, k], ax): a.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(FIG / "stage8_ratings_scatter.png", dpi=130); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(14, 5))
for k, role in enumerate(("batters", "bowlers")):
    r = pd.read_csv(OUT / f"player_ratings_{role}.csv"); r = r[r.eligible]
    ax[k].scatter(r.shift_boot_mean, r.pressure_rating - (r.B if role == "batters" else r.W), s=0)
    ax[k].hist(r.shift_boot_mean, bins=25, color=BLUE, alpha=.8); ax[k].axvline(0, color=GREY)
    ax[k].set_title(f"{role.title()}: pressure shift (bootstrap mean), eligible players", fontsize=10); ax[k].set_xlabel("shift"); ax[k].spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(FIG / "stage8_shift_distribution.png", dpi=130); plt.close()

sens = pd.read_csv(OUT / "sensitivity.csv")
tabs = ["# Report tables (generated)", "", "## Final lists", ""]
for role in ("batters", "bowlers"):
    t = pd.read_csv(OUT / f"top10_{role}.csv"); tabs += [f"### Top 10 {role}", "", t[["rank", "name", "player_id", "pressure_rating", "floor_p10", "p_top10", "p_top20", "delivery_rate", "fragile"]].to_markdown(index=False, floatfmt=".3f"), ""]
tabs += ["## Sensitivity grid", "", sens.to_markdown(index=False, floatfmt=".3f"), "", "## Reliability", "", (OUT / "reliability.md").read_text(encoding="utf-8")]
(OUT / "report_tables.md").write_text("\n".join(tabs), encoding="utf-8")
print("wrote figures/stage8_*.png and outputs/report_tables.md")
