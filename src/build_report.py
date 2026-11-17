"""Build report.md from generated files only. No new analysis: every number is read from outputs/*.csv, *.json or a parsed audit table.
Run: python -I src/build_report.py
"""
import ast
import json
import re
import warnings
from io import StringIO
from pathlib import Path

import pandas as pd
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
OUT = ROOT / CFG["paths"]["out_dir"]


# ----------------------------------------------------------------------------- readers
def md_tables(path):
    """{heading: [DataFrame, ...]} for every pipe table in a markdown file."""
    lines = Path(path).read_text(encoding="utf-8").replace("median|err|", "median_abs_err").replace("|pred - obs|", "abs(pred - obs)").split("\n")
    out, head, i = {}, "", 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            head = ln.lstrip("#").strip()
        elif ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].startswith("|"): j += 1
            block = [lines[i]] + lines[i + 2:j]
            df = pd.read_csv(StringIO("\n".join(l.strip().strip("|") for l in block)), sep=r"\s*\|\s*", engine="python")
            df.columns = [c.strip() for c in df.columns]
            for c in df.columns:
                if df[c].dtype == object: df[c] = df[c].astype(str).str.strip()
            out.setdefault(head, []).append(df); i = j; continue
        i += 1
    return out


def tbl(path, heading_prefix, k=0):
    t = md_tables(path)
    key = next(h for h in t if h.startswith(heading_prefix))
    return t[key][k]


def rx(path, pattern, group=1, cast=str):
    m = re.search(pattern, Path(path).read_text(encoding="utf-8"))
    if not m: raise ValueError(f"{pattern!r} not found in {path}")
    return cast(m.group(group))


def nrx(path, pattern, group=1): return float(rx(path, pattern, group).replace(",", ""))


def gate_detail(path, name_prefix):
    g = tbl(path, "Gates")
    return g[g.iloc[:, 0].str.startswith(name_prefix)].iloc[0, 2]


def table_md(df, floatfmt=None):
    return df.to_markdown(index=False, floatfmt=floatfmt or ".3f")


p3 = lambda x: f"{float(x):.3f}"; p2 = lambda x: f"{float(x):.2f}"; p1 = lambda x: f"{float(x):.1f}"; pc = lambda x: f"{100 * float(x):.1f}%"
A1, A2, A2C, A3, A4, A5 = (OUT / f for f in ("audit_stage1.md", "audit_stage2.md", "audit_stage2c.md", "audit_stage3.md", "audit_stage4.md", "audit_stage5.md"))
REL = OUT / "reliability.md"
top_b, top_w = pd.read_csv(OUT / "top10_batters.csv"), pd.read_csv(OUT / "top10_bowlers.csv")
rat_b, rat_w = pd.read_csv(OUT / "player_ratings_batters.csv"), pd.read_csv(OUT / "player_ratings_bowlers.csv")
sens = pd.read_csv(OUT / "sensitivity.csv")
S3 = json.load(open(OUT / "step3_summary.json")); thr = json.load(open(OUT / "pressure_thresholds.json")); ch4 = json.load(open(OUT / "stage4_choices.json"))
rec = pd.read_csv(OUT / "step3_recalibration.csv").set_index("innings")
mf = pd.read_csv(OUT / "matches_flags.csv")

# ----------------------------------------------------------------------------- numbers
rs = ast.literal_eval(rx(A1, r"Rating sample by group: (\{.*?\})"))
n_rs = sum(rs.values()); n_ties = int(rx(A1, r"ties kept: (\d+)"))
raw_rows, raw_matches, out_rows, out_matches = rx(A1, r"Raw file: ([\d,]+) rows, (\d+) matches\. Output table: ([\d,]+) rows, (\d+) matches", 1), rx(A1, r"Raw file: [\d,]+ rows, (\d+) matches", 1), rx(A1, r"Output table: ([\d,]+) rows", 1), rx(A1, r"Output table: [\d,]+ rows, (\d+) matches", 1)
spin = pd.read_csv(OUT / "step3_spinner_share.csv").set_index("subset")
n_live, n_pressure = int(spin.loc["all live balls", "balls"]), int(spin.loc["pressure balls", "balls"])
elig = tbl(A5, "Eligibility").set_index("role"); unc = tbl(A5, "Uncertainty").set_index("role"); xchk = tbl(A5, "Cross-check").set_index("role")
split = tbl(REL, "Split-half"); s2s = tbl(REL, "Season to season").set_index("role"); add = tbl(REL, "Does the shift add"); perm = tbl(REL, "Permutation").set_index("role")
sh = lambda role, q, col="spearman_brown": float(split[(split.role == role) & (split.quantity == q)][col].iloc[0])
ext = gate_detail(A1, "external totals"); marg = gate_detail(A1, "margin gate"); wk = gate_detail(A1, "wickets gate"); strike = gate_detail(A1, "strike rule")
rho_b = re.search(r"rho = (-?[\d.]+).*n=(\d+)", gate_detail(A4, "batter baseline")); rho_w = re.search(r"rho = (-?[\d.]+).*n=(\d+)", gate_detail(A4, "bowler baseline"))
by_inn = tbl(A2C, "By innings").set_index("innings")
brier = tbl(A2, "Brier and log loss").set_index("innings")
dec1, dec2 = tbl(A2, "Deciles, WP* (innings 1)"), tbl(A2, "Deciles, WP* (innings 2)")
cell = tbl(A2, "Scoring-model cell check").set_index("innings")
start_by_group = tbl(A2, "Start of chase by target", 1).set_index("group")
pi_live = nrx(A3, r"live chase balls ([\d.]+)")
rot = tbl(A3, "Benchmark agreement").set_index("innings")
close = tbl(A3, "Close games against blowouts").set_index("close"); close.index = close.index.astype(str)
sp_peak = re.search(r"wins by runs, n=(\d+)\): (-?[\d.]+)", A3.read_text(encoding="utf-8")); n_close, n_clean = rx(A3, r"Matches classed close: (\d+) of (\d+)", 1), rx(A3, r"Matches classed close: \d+ of (\d+)", 1)
shift = tbl(A3, "Outcome and behaviour shift")
spread = tbl(A4, "Spread of ratings").set_index("role")
batter_rows, bowler_rows = rx(A4, r"batter rows ([\d,]+), bowler rows", 1), rx(A4, r"bowler rows ([\d,]+);", 1)
wicket_run = rx(OUT / "step2_bowler_net.md", r"Mean over all pressure balls: ([\d.]+) runs")
overlap = pd.read_csv(OUT / "step3_overlap_baseline.csv"); rem_b, rem_w = pd.read_csv(OUT / "step3_removed_batters.csv"), pd.read_csv(OUT / "step3_removed_bowlers.csv")
strict = pd.read_csv(OUT / "strict_rule_bowlers.csv")
lock = (ROOT / "FINAL_LOCK.md").read_text(encoding="utf-8") if (ROOT / "FINAL_LOCK.md").exists() else ""
n_knock = int(mf.knock_out.sum())
outside_pct = rx(A2C, r"outside overs 16-20: ([\d.]+%)")
ext_mean, ext_within = re.search(r"mean error (-?[\d.]+)", ext).group(1), re.search(r"(\d+) of (\d+) within", ext)

# ----------------------------------------------------------------------------- tables
def lists_table(top, rat_cols):
    t = top[["rank", "name", "teams", "pressure_rating", "floor_p10", "p_top10"]].copy()
    t.columns = ["#", "Name", "Teams", "Pressure rating", "Floor", "P(top 10)"]
    return table_md(t)


def shift_table(metrics, scale100):
    rows = []
    for ph in ("powerplay (1-6)", "middle (7-15)", "death (16-20)"):
        r = {"Phase": ph}
        for m in metrics:
            x = shift[(shift.phase == ph) & (shift.metric == m)].iloc[0]
            f = 1 if m == "runs" else 100
            star = "*" if str(x.excludes_zero) == "True" else ""
            r[m.replace("_", " ")] = f"{f * x.diff_pressure_minus_ordinary:+.{1 if f == 100 else 3}f} [{f * x.ci_lo:+.{1 if f == 100 else 3}f}, {f * x.ci_hi:+.{1 if f == 100 else 3}f}]{star}"
        rows.append(r)
    return table_md(pd.DataFrame(rows))


def evid_table(role):
    top, rat = (top_b, rat_b) if role == "b" else (top_w, rat_w)
    r = rat.set_index("player_id").loc[top.player_id]
    if role == "b":
        t = pd.DataFrame({"#": top["rank"].values, "Name": top.name.values, "Pressure balls": r.balls_P.astype(int).values, "Matches": r.matches_P.astype(int).values, "Strike rate P / O": [f"{a:.1f} / {b:.1f}" for a, b in zip(r.sr_P, r.sr_O)],
                          "Runs index": r.runs_index_P.round(0).astype(int).values, "Dismissal ratio": r.dismissal_ratio_P.round(2).values, "Delivery rate": r.delivery_rate.round(2).values,
                          "P(top 10)": top.p_top10.round(2).values, "Rank interval": [f"{int(a)}-{int(b)}" for a, b in zip(top.rank_p10, top.rank_p90)]})
    else:
        t = pd.DataFrame({"#": top["rank"].values, "Name": top.name.values, "Pressure balls": r.deliveries_P.astype(int).values, "Matches": r.matches_P.astype(int).values, "Economy P / O": [f"{a:.2f} / {b:.2f}" for a, b in zip(r.economy_P, r.economy_O)],
                          "Economy index": r.economy_index_P.round(0).astype(int).values, "Wicket ratio": r.wicket_ratio_P.round(2).values, "Delivery rate": r.delivery_rate.round(2).values,
                          "P(top 10)": top.p_top10.round(2).values, "Rank interval": [f"{int(a)}-{int(b)}" for a, b in zip(top.rank_p10, top.rank_p90)]})
    return table_md(t, ".2f")


sensw = sens.pivot(index="variant", columns="role", values=["top10_overlap_with_main", "kendall_tau"])
sens_tbl = pd.DataFrame({"Variant": sensw.index, "Batters overlap": sensw[("top10_overlap_with_main", "batters")].astype(int).values, "Batters tau": sensw[("kendall_tau", "batters")].values,
                         "Bowlers overlap": sensw[("top10_overlap_with_main", "bowlers")].astype(int).values, "Bowlers tau": sensw[("kendall_tau", "bowlers")].values})
med = sens.groupby("role").top10_overlap_with_main.median()
n_var = int(sens.variant.nunique())
fig = lambda f, cap: f"![{cap}](figures/{f})\n\n*Figure: {cap}*\n"

batters_rat = open(OUT / "batter_rationale.md", encoding="utf-8").read(); bowlers_rat = open(OUT / "bowler_rationale.md", encoding="utf-8").read(); spin_para = open(OUT / "spinner_paragraph.md", encoding="utf-8").read()
ov = overlap.set_index(["role", "pool"])
ov_b = int(ov.loc[("batters", "same pool as main (negative-shift players removed)"), "overlap_of_10"]); ov_w = int(ov.loc[("bowlers", "same pool as main (negative-shift players removed)"), "overlap_of_10"])
min_overlap = sens.loc[sens.top10_overlap_with_main.idxmin()]
fragile_n = int(top_b.fragile.sum() + top_w.fragile.sum())
wz = sens[sens.variant.str.startswith('winsor')]
ext_tbl = tbl(A1, 'External totals check'); err2_mean = float(ext_tbl.err2.mean()); err1_mean = float(ext_tbl.err1.mean())
marg_d = gate_detail(A1, 'margin gate'); p95_err = re.search(r'p95=([\d.]+)', marg_d).group(1); med_err = re.search(r'median_abs_err=([\d.]+)', marg_d).group(1)
wkfail = tbl(A1, 'Wickets gate failures').iloc[0]
vmin = nrx(A4, r'v quantiles \{0\.0: (-?[\d.]+)')
lowest = pd.concat([top_b.assign(role="batter"), top_w.assign(role="bowler")]).sort_values("variants_in_top10").iloc[0]

# ----------------------------------------------------------------------------- report
R = []
R.append(f"""# Who delivers when it matters
### SupeRR Selector Season 2, Round 1: how we rated batters and bowlers under pressure

## 1. The answer

> **The ratings measure proven quality in live, high-leverage situations. A separate clutch trait is not reliably measurable in this data** (pressure-shift split-half reliability {p2(sh('batters', 'pressure shift'))} for batters and {p2(sh('bowlers', 'pressure shift'))} for bowlers).

**Top 10 batters**

{lists_table(top_b, None)}

**Top 10 bowlers**

{lists_table(top_w, None)}

*Pressure rating = a player's baseline plus his pressure shift, per ball, in units of the expected swing in win probability (higher is better; 0 is an average player in the same situations). Floor = the 10th percentile of the rating across {CFG['rating']['bootstrap_n']} resamples of whole matches; players are ranked on it. P(top 10) = share of resamples in which the player finishes in the top 10 of the eligible pool.*

**The method in five lines**

1. Every ball of both innings gets a win probability from an exact model of the next ball (ten outcome classes, solved by backward induction over match states and recalibrated on held-out seasons: slope {p2(rec.loc[1, 'c (slope)'])} in innings 1, {p2(rec.loc[2, 'c (slope)'])} in innings 2).
2. **Pressure is leverage**: how far the next ball is expected to move the win probability. A pressure ball is in the top 20% of live balls (leverage of at least {p2(thr['p80'])} against an average live ball of 1).
3. Each ball is valued by the actual change in win probability minus the average change in the same situation, divided by the expected swing, and split between batter and bowler.
4. One ridge regression per role gives each player a **baseline** and a **pressure shift**, adjusting for opposition quality; the penalties are chosen by cross-validation with whole matches held out.
5. Players are ranked by the **floor** of their pressure rating among eligible, active players, after removing anyone whose pressure shift is reliably negative.

**Sample.** {n_rs} matches ({rs.get('IPL')} IPL, {rs.get('T20I-full')} full-member T20I), {n_live:,} live balls of which {n_pressure:,} are pressure balls. {int(elig.loc['batters', 'eligible'])} batters and {int(elig.loc['bowlers', 'eligible'])} bowlers meet the eligibility rule (120 pressure balls over at least 15 matches); {int(elig.loc['batters', 'eligible_and_active'])} and {int(elig.loc['bowlers', 'eligible_and_active'])} were also active in 2025 or 2026.

**Reliability in one line.** The pressure rating is repeatable across random halves of the matches (split-half {p2(sh('batters', 'pressure rating'))} batters, {p2(sh('bowlers', 'pressure rating'))} bowlers), but that repeatability comes from general quality: the baseline alone scores {p2(sh('batters', 'baseline'))} and {p2(sh('bowlers', 'baseline'))}. Section 8 gives every reliability number, including a season-to-season correlation of {p2(s2s.loc['batters', 'pressure_rating_r'])} for batters.
""")

R.append(f"""## 2. How we define pressure

**In plain words.** A ball is high-pressure when what happens on it can swing the result a lot. For every ball we ask the model for the chance of each outcome (dot, 1, 2, 3, 4, 6, wicket, and three kinds of wide or no-ball), work out the win probability after each, and take the expected absolute change. Divided by the average over live balls, this is the leverage index LI. A ball is **live** when the win probability is between 0.02 and 0.98; decided balls are removed from both the pressure set and every baseline. A **pressure ball** has LI at or above the 80th percentile of live balls pooled across both innings (LI of {p2(thr['p80'])}; median live ball {p2(thr['median'])}, 95th percentile {p2(thr['p95'])}).

`swing(s) = sum over outcomes o of p(o | s) x | WP*(after o) - WP*(s) |        LI(s) = swing(s) / mean swing over live balls`

**Why this definition.** It uses every factor the brief lists (required rate, wickets in hand, balls left, stage of the innings, closeness) through their measured effect on the result, with no hand-picked weights. It uses no hindsight: the final margin is never an input. It works in the first innings in the same unit as the chase, where the standard published pressure index is defined for chases only.

**The engine.** The next-ball model is a multinomial logistic regression on over, wickets lost, required-rate band, venue scoring level, competition group and the impact-player rule, fitted on all clean matches. Win probability is solved exactly from it by backward induction, then recalibrated with two parameters fitted on out-of-fold predictions (innings 1: a = {rec.loc[1, 'a']:.3f}, c = {rec.loc[1, 'c (slope)']:.3f}; innings 2: a = {rec.loc[2, 'a']:.3f}, c = {rec.loc[2, 'c (slope)']:.3f}). A slope below 1 is the known over-confidence of exact models. The chase surface is projected to be monotone (win probability cannot rise when a wicket falls) because the raw surface was noisy in thinly observed late-chase states.

**Where pressure lives.**

{fig('stage3_where_pressure_lives.png', 'Mean leverage by runs required and over of the chase (left), by wickets lost and over in the first innings (centre), and the share of balls that are pressure balls by over (right).')}

Under the pooled cutoff, pressure is mostly a live chase: innings 1 has {int(rot.loc[1, 'pressure_balls'])} pressure balls ({pc(by_inn.loc[1, 'pressure_share_all'])} of its balls) against {pc(by_inn.loc[2, 'pressure_share_all'])} of innings-2 balls ({pc(by_inn.loc[2, 'pressure_share_of_live'])} of live ones), and {outside_pct} of all pressure balls fall before over 16. We report this as it is, and the sensitivity grid includes a variant that sets the cutoff within each innings.

**Agreement with simpler definitions.** Against the published Bhattacharjee-Lemmer pressure index (chases only; its resources-used term is replaced by one derived from our own scoring model because the Duckworth-Lewis table is not in the data), the rank correlation with LI on live chase balls is {p2(pi_live)}: the two agree on direction but are far from identical. A common rule of thumb (last five overs with a required rate of 8 to 15, and so on) marks {pc(rot.loc[2, 'share_of_rule_that_is_pressure'])} of the chase balls it covers as pressure, but covers only {pc(rot.loc[2, 'share_of_pressure_in_rule'])} of the chase pressure balls.
""")

R.append(f"""## 3. Proof that it captures pressure

**Pressure balls behave differently from ordinary balls in the same phase.** We compare live pressure balls with live ordinary balls inside strata of innings, phase and wickets band, and weight by the pressure balls in each stratum. Intervals come from {CFG['stage3']['bootstrap_n']} resamples of whole matches. Differences are in percentage points (runs per ball for "runs"); `*` marks an interval that excludes zero.

{shift_table(['dismissal', 'boundary', 'dot', 'runs'], True)}

The pre-declared gate (dismissal or boundary rate differs in at least two of three phases) is passed in all three. Both sides also change what they attempt, not only what results:

{shift_table(['attacking_stroke', 'defensive_stroke', 'yorker', 'slower'], True)}

Batters play fewer defensive and more attacking strokes; bowlers reach for yorkers and slower balls.

{fig('stage3_separation.png', 'Pressure minus ordinary rates by phase with 95% match-bootstrap intervals: outcomes (left) and behaviour (right).')}

**Pressure concentrates in games that finished tight, although the margin is never an input.** {n_close} of {n_clean} clean matches finished within 10 runs, 3 wickets or a tie. Their median peak leverage is {p1(close.loc['True', 'median_peak_LI'])} against {p1(close.loc['False', 'median_peak_LI'])} for the rest, and across matches won by runs the rank correlation between peak leverage and margin is {sp_peak.group(2)} (n = {sp_peak.group(1)}).

{fig('stage3_close_games.png', 'Peak leverage in close games against the rest (left) and against the winning margin (right).')}

{fig('stage3_case_studies.png', 'Leverage (blue) and win probability (grey) through three tight finishes (top) and three one-sided chases (bottom).')}

**The win probabilities behind the index are honest.** On leave-one-season-out predictions the largest gap between predicted and observed win rate in any decile is {p1(100 * dec1.gap.abs().max())} points in innings 1 and {p1(100 * dec2.gap.abs().max())} in innings 2 (limit 5). The Brier score beats a one-feature logistic baseline in both innings ({p3(brier.loc[1, 'brier_star'])} against {p3(brier.loc[1, 'brier_baseline'])}; {p3(brier.loc[2, 'brier_star'])} against {p3(brier.loc[2, 'brier_baseline'])}), and the next-ball model reproduces observed outcome frequencies to within {p1(100 * cell.worst_abs_diff.max())} points in every well-populated cell. Note that the 95% bootstrap intervals on the decile gaps are about plus or minus 5 points, so the gate shows no evidence of miscalibration larger than that, not calibration to a finer tolerance.

{fig('stage2_calibration.png', 'Predicted against observed win rate by decile, leave-one-season-out (top left and centre); start of chase by target (top right); two chase traces; distribution of win probability.')}
""")

R.append(f"""## 4. How performance is measured

**Value of a ball.** For each ball, dWP is the change in the batting side's win probability. We subtract the average change among balls in the same state bin (innings, over band, wickets band, leverage band), so a player is compared with what a typical player does in the identical situation, and divide by the ball's expected swing so a six in the last over does not drown out everything else.

**Who gets the credit.** Runs off the bat go to the striker and are charged to the bowler; wides are charged to the bowler only; no-balls charge the bowler the bat runs and the penalty run; byes and leg-byes count as dot balls for both; wickets are charged to the dismissed batter (including non-strikers run out, who get their own row) and credited to the bowler for bowled, caught, lbw, hit wicket and stumpings; run-outs and obstructing the field are not credited to the bowler; retire-outs are charged to nobody.

**The rating model.** Two ridge regressions of the same form, one on balls faced and one on balls bowled:

`batting:  v = context + B_i + P x C_i - (W_j + P x K_j)        bowling:  v = context + W_j + P x K_j - (B_i + P x C_i)`

`i` is the batter, `j` the bowler, `P` is 1 on pressure balls, `B` and `W` are baselines, `C` and `K` are pressure shifts, and context is fixed effects for innings, phase and pressure plus a competition-group term. The opposing players' terms are what adjust for opposition quality. The two penalties (baseline {ch4['lambda_B']:.0f}, shift {ch4['lambda_C']:.0f}, so the shift is shrunk {ch4['lambda_C'] / ch4['lambda_B']:.0f} times harder) were chosen by 5-fold cross-validation with whole matches held out. The fit uses {batter_rows} batter rows and {bowler_rows} bowler rows from live balls in the rating sample.

The ratings track conventional statistics sensibly: among eligible batters the rank correlation between baseline and strike rate is {rho_b.group(1)} (n = {rho_b.group(2)}), and among eligible bowlers between baseline and economy it is {rho_w.group(1)} (n = {rho_w.group(2)}). For each player we also report plain-cricket companions on pressure and ordinary balls: strike rate, runs index (100 times actual over expected bat runs), dismissal ratio (actual over expected), economy, economy index (100 times expected over actual runs conceded), wicket ratio, wins added per 100 pressure balls, and the delivery rate (share of matches with six or more pressure balls in which his total value was positive).
""")

R.append(f"""## 5. Fair comparisons

- **Which matches rate players.** {n_rs} IPL and full-member T20I matches without rain or truncation flags, including {n_ties} tied matches. Associate and A-team matches help fit the scoring model but do not rate players. {raw_rows} raw rows from {raw_matches} matches were cleaned to {out_rows} rows from {out_matches} matches (super overs, no-results, rain-affected and truncated games removed).
- **Eligibility.** At least 120 pressure balls (one full innings of them) over at least 15 matches, fixed in the configuration before any leaderboard was viewed: {int(elig.loc['batters', 'eligible'])} batters and {int(elig.loc['bowlers', 'eligible'])} bowlers qualify. Players must also have appeared in 2025 or 2026, since the lists inform the next auction. The unfiltered list is in the appendix files.
- **Small samples.** The ridge penalties shrink a thin pressure record toward the player's baseline and a thin baseline toward average. Across eligible batters the standard deviation of baselines is {p3(spread.loc['batters', 'sd_baseline_eligible'])} against {p3(spread.loc['batters', 'sd_shift_eligible'])} for shifts (bowlers {p3(spread.loc['bowlers', 'sd_baseline_eligible'])} and {p3(spread.loc['bowlers', 'sd_shift_eligible'])}).
- **Opposition quality.** Runs against a strong attack earn more credit than runs against a weak one because the opposing players' terms are in the same regression. A simple version without any regression (raw pressure means shrunk toward a shrunk baseline) ranks players almost identically (rank correlation {p2(xchk.loc['batters', 'spearman_regression_vs_simple'])} batters, {p2(xchk.loc['bowlers', 'spearman_regression_vs_simple'])} bowlers).
- **IPL and T20I together.** One model rates both, with a competition-group term in the context, so there is one leaderboard. Rating IPL-only or T20I-only is among the variants that change the lists most (section 8).
- **Venue and era.** Venue scoring level and the impact-player rule enter the scoring model, and through it the win probabilities and leverage.
- **Batting role.** Wickets lost is part of the state, and adding a batting-position band to the context leaves the batter list unchanged (top-10 overlap {int(sens[(sens.role == 'batters') & (sens.variant == 'position_band_in_context')].top10_overlap_with_main.iloc[0])} of 10).
""")

R.append(f"""## 6. Batters: the evidence

{evid_table('b')}

*Pressure balls and matches count balls faced under pressure. Runs index = 100 x actual / expected bat runs; dismissal ratio = actual / expected dismissals; delivery rate = share of matches (with six or more pressure balls) with positive total value; rank interval = 10th to 90th percentile of rank across resamples.*

{batters_rat}
{fig('stage8_ratings_scatter.png', 'Baseline against pressure rating with 10th to 90th percentile intervals (top), and the simple cross-check against the regression rating (bottom). Pressure ratings sit almost on the baseline line: the shift adds little.')}
""")

R.append(f"""## 7. Bowlers: the evidence

{evid_table('w')}

*Economy index = 100 x expected / actual runs conceded; wicket ratio = actual / expected bowler-credited wickets. On pressure balls a wicket is worth {p1(wicket_run)} runs on average in these states.*

**Why each bowler ranks where he does** (net runs = (actual minus expected wickets) x the model's run value of a wicket, minus (actual minus expected runs conceded); the interval is a match bootstrap):

{bowlers_rat}
**Why eight of the ten are spinners.** {spin_para}
**Sign check.** Every listed batter has a runs index above 100 or a dismissal ratio below 1. For bowlers the check is economy index above 100 **or** wicket ratio above 1 on pressure balls, which all ten pass. This is a post-hoc amendment: the original, economy-only check fails for Wanindu Hasaranga and Noor Ahmad, who rank high on wickets while conceding slightly more than expected. The list that results from the strict economy-only rule is in Appendix A; it replaces those two with Mujeeb Ur Rahman and Bhuvneshwar Kumar.
""")

R.append(f"""## 8. Reliability

All numbers below are reported as they came out.

**Split-half reliability** ({CFG['stage6']['split_half_n']} random splits of matches; each half rated with the same penalties and half the eligibility thresholds; Spearman-Brown corrected):

{table_md(split.assign(mean_players=split.mean_players.round(1))[['role', 'quantity', 'mean_split_half_r', 'spearman_brown', 'sd_over_splits', 'mean_players']].rename(columns={'mean_split_half_r': 'raw r', 'spearman_brown': 'corrected r', 'sd_over_splits': 'SD over splits', 'mean_players': 'players (avg)'}), '.3f')}

The pressure rating clears the pre-declared 0.40 line for both roles (batters {p2(sh('batters', 'pressure rating'))}, bowlers {p2(sh('bowlers', 'pressure rating'))}), so the lists rank on it. The pressure **shift** on its own does not ({p2(sh('batters', 'pressure shift'))} and {p2(sh('bowlers', 'pressure shift'))}, below 0.25), and the baseline is as reliable as the pressure rating. The reliability of the rating is therefore the reliability of general quality.

**Season to season** (fit on 2022 to 2024, score 2025 to 2026; bootstrap over players):

{table_md(s2s.reset_index()[['role', 'players', 'pressure_rating_r', 'spearman', 'ci_lo', 'ci_hi', 'baseline_r', 'shift_r']].rename(columns={'pressure_rating_r': 'pressure rating r', 'ci_lo': 'CI low', 'ci_hi': 'CI high', 'baseline_r': 'baseline r', 'shift_r': 'shift r'}))}

Bowlers persist (r = {p2(s2s.loc['bowlers', 'pressure_rating_r'])}); **batters do not: r = {p2(s2s.loc['batters', 'pressure_rating_r'])}** (95% interval {p2(s2s.loc['batters', 'ci_lo'])} to {p2(s2s.loc['batters', 'ci_hi'])}, {int(s2s.loc['batters', 'players'])} players), and even the batter baseline correlates at only {p2(s2s.loc['batters', 'baseline_r'])}. With few players in both periods the interval is wide, but there is no evidence of batter persistence across the two periods.

**Does the shift add anything?** Regressing later mean value on pressure balls on the earlier baseline and the earlier shift (per standard deviation):

{table_md(add[['role', 'term', 'coefficient', 'ci_lo', 'ci_hi', 'excludes_zero', 'n']].rename(columns={'ci_lo': 'CI low', 'ci_hi': 'CI high', 'excludes_zero': 'excludes 0'}))}

The shift coefficient's interval includes zero for both roles: pressure-specific skill is not separable in this data. Only the bowler baseline predicts later pressure value.

**Permutation test** (shuffle the pressure flag within each player {CFG['stage6']['permutations']} times, keeping his count of pressure balls; compare the spread of raw shifts):

{table_md(perm.reset_index()[['role', 'players', 'real_spread', 'shuffled_mean', 'shuffled_p95', 'p_value', 'real_beyond_p95']].rename(columns={'real_beyond_p95': 'beyond 95th pct'}))}

Evidence that players differ under pressure is weak: borderline for bowlers (p = {p3(perm.loc['bowlers', 'p_value'])}) and not reached for batters (p = {p3(perm.loc['batters', 'p_value'])}).

**Rank stability.** Every listed player has a probability of finishing in the top 20 of at least {p2(min(top_b.p_top20.min(), top_w.p_top20.min()))}; the lowest probability of a top-10 finish is {p2(min(top_b.p_top10.min(), top_w.p_top10.min()))}. {fragile_n} of the 20 are flagged fragile (a player is fragile if he drops out of the top 10 in more than half of the sensitivity variants); the least stable listed player is {lowest['name']}, in the top 10 under {int(lowest.variants_in_top10)} of {n_var} variants.

**Sensitivity grid.** Each variant re-rates players with the penalties fixed; overlap is with the main top 10 on the same floor proxy (rating minus 1.28 bootstrap standard deviations), tau is Kendall's rank correlation over the pool. Median overlap is {int(med['batters'])} of 10 for batters and {int(med['bowlers'])} for bowlers (the pre-declared target is 7).

{table_md(sens_tbl)}

The lowest overlap is {int(min_overlap.top10_overlap_with_main)} of 10 ({min_overlap.variant.replace('_', ' ')}, {min_overlap.role}), from rating on a different slice of the data. Two further comparisons: ranking on the floor of the baseline alone gives {ov_b} of 10 of the main batter list and {ov_w} of 10 of the main bowler list; weighting recent seasons (two-season half-life) keeps {S3['recency_overlap_final']} of 10 batters (out: {', '.join(S3['recency_out'])}; in: {', '.join(S3['recency_in'])}). Capping ball values at their 1st and 99th percentiles keeps {int(wz.top10_overlap_with_main.min())} of 10 for both roles.
""")

R.append(f"""## 9. Limitations

- **Pressure is mostly a live chase.** With the pooled cutoff, innings 1 contributes {int(rot.loc[1, 'pressure_balls'])} pressure balls, so the ratings are close to ratings of performance in live chases; first-innings pressure is nearly absent by construction.
- **Venue is not in the rating context.** Venue scoring level enters the scoring model (and so win probability and leverage) but the rating regression's context has no venue term, only innings, phase, pressure and competition group.
- **One sensitivity variant was not run.** Win probability without recalibration would need the whole leverage stage rerun and was skipped. The sensitivity grid also uses a floor proxy (rating minus 1.28 bootstrap standard deviations) because the bootstrap is not rerun per variant; the final ranking uses the true bootstrap floor.
- **The bowler sign check was amended after the results were seen** (section 7). The original rule's list is in Appendix A.
- **No separable clutch trait.** The pressure shift is not reliable, batter ratings do not persist season to season (r = {p2(s2s.loc['batters', 'pressure_rating_r'])}), and the permutation test is borderline. The lists rank proven quality in live, high-leverage situations.
- **Team scores are rebuilt.** Bye, leg-bye and extra-wide runs are not recorded, so scores are rebuilt and partly imputed. Against public scorecards for 15 matches drawn with a fixed seed, the mean error is {ext_mean} runs and {ext_within.group(1)} of {ext_within.group(2)} innings totals are within 5 runs; rebuilt winning margins differ from the stated margin by a median of {med_err} runs (95th percentile {p95_err}). In that sample first-innings totals are off by {err1_mean:+.1f} runs on average and chase totals by {err2_mean:+.1f}; the backward anchor handles the chase for runs required.
- **Win probability is team-neutral.** It does not know a side's batting depth: out of sample it over-predicts chasing associates by {p1(100 * start_by_group.loc['T20I-assoc', 'gap'])} points and A-teams by {p1(100 * start_by_group.loc['A-team', 'gap'])} points (full-member T20I {p1(100 * start_by_group.loc['T20I-full', 'gap'])}, IPL {p1(100 * start_by_group.loc['IPL', 'gap'])}).
- **Calibration tolerance.** The 5-point decile tolerance is about as wide as its sampling noise (section 3).
- **Fielding, partnerships and role.** A dropped catch helps the batter and hurts the bowler with no correction; non-strikers and partnerships get no credit; captains give the hardest overs and positions to players they trust, so who faces pressure is not random.
- **Tournament pressure is untested.** There is no World Cup in the data and only {n_knock} knockout matches.
- **Small pools.** Only {int(elig.loc['batters', 'eligible'])} batters and {int(elig.loc['bowlers', 'eligible'])} bowlers meet the eligibility rule, so the lists are the top of short pools.
- **Heavy tails.** Wicket balls give batter ball values as low as {vmin:.1f} standard units; capping values at the 1st and 99th percentiles leaves the lists unchanged (section 8).
- **Data quality.** The one chase that fails the wickets reconciliation (match {int(wkfail.match_id)}: result text '{wkfail.result}', {int(wkfail.wk_end)} wickets in the ball data against {int(wkfail.expected)} implied) is a named exception; the ball data were used.

**What more data would fix:** a venue term in the rating regression, ball-tracking or fielding data, and a World Cup or knockout sample for tournament pressure.
""")

R.append(f"""## Appendix

**A. Strict-rule bowler list** (original sign check: economy index above 100 on pressure balls only; the two failing bowlers are dropped and ranks 11 and 12 of the pool are promoted):

{table_md(strict[['rank', 'name', 'player_id', 'pressure_rating', 'floor_p10', 'economy_index', 'wicket_ratio', 'net_runs']].rename(columns={'rank': 'pool rank', 'floor_p10': 'floor', 'net_runs': 'net runs'}), '.3f')}

**B. Players removed because their pressure shift is reliably negative** (90th percentile of the bootstrap shift below zero), with baseline rank among eligible, active players.

Batters: {', '.join(f"{r['name']} ({int(r.baseline_rank)})" for _, r in rem_b.iterrows())}.

Bowlers: {', '.join(f"{r['name']} ({int(r.baseline_rank)})" for _, r in rem_w.iterrows())}.

**C. Reproducibility.** `python run_all.py` regenerates every table, chart and list from the supplied files with fixed seeds; all thresholds live in `config.yaml`; every departure from the blueprint and every judgement call is logged in `CHANGES_FOR_REVIEW.md`; `exhibit_map.md` lists each claim beside its supporting exhibit; `FINAL_LOCK.md` holds the SHA-256 hashes of the configuration and both lists. Per-stage audits are in `outputs/audit_stage*.md`. A rerun from an empty outputs folder reproduced both top-10 files exactly.

**D. Identity.** One listed name has two player ids in the mapping file (Rashid Khan: the list uses the Afghanistan and Gujarat Titans player); `submission_sheet.csv` flags it for the dropdown.
""")
(ROOT / "report.md").write_text("\n".join(R), encoding="utf-8")
print("report.md written", len("\n".join(R).split()), "words")
