"""Shared loaders and NEW aggregations for the handoff pack (PPT_and_Document_Preparation/).

Read-only on outputs/: nothing here refits a model, changes a rule, or rewrites a pipeline file.
Run via:  python -I src/build_handoff.py
"""
import io
import json
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import norm

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
WEB = ROOT / "website"
PACK = ROOT / "PPT_and_Document_Preparation"
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
R = CFG["rating"]


# ------------------------------------------------------------------ text helpers
def rd(p):
    return Path(p).read_text(encoding="utf-8")


def md(df, fl=".3f"):
    return df.to_markdown(index=False, floatfmt=fl)


def sec(text, heading, level=2):
    """Return the body of a markdown section (heading line excluded) up to the next heading of the same or higher level."""
    pat = re.compile(rf"^{'#' * level} {re.escape(heading)}\s*$", re.M)
    m = pat.search(text)
    if not m:
        raise KeyError(f"heading not found: {heading}")
    rest = text[m.end():]
    n = re.search(rf"^#{{1,{level}}} ", rest, re.M)
    return rest[: n.start()].strip() if n else rest.strip()


def table_from(text):
    """Parse the first pipe table in a text block into a DataFrame (numbers converted where possible)."""
    rows = [l for l in text.splitlines() if l.strip().startswith("|")]
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in rows]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    df = pd.DataFrame(rows[1:], columns=rows[0])
    for c in df.columns:
        try:
            df[c] = pd.to_numeric(df[c])
        except (ValueError, TypeError):
            pass
    return df


def ordinal(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


# ------------------------------------------------------------------ pipeline tables
TOP = {"batters": pd.read_csv(OUT / "top10_batters.csv"), "bowlers": pd.read_csv(OUT / "top10_bowlers.csv")}
UNF = {r: pd.read_csv(OUT / f"unfiltered_eligible_{r}.csv") for r in ("batters", "bowlers")}      # all eligible (53 / 56)
POOL = {r: pd.read_csv(OUT / f"eligible_table_{r}.csv") for r in ("batters", "bowlers")}          # eligible, active, not removed (47 / 48)
ALLR = {r: pd.read_csv(OUT / f"player_ratings_{r}.csv") for r in ("batters", "bowlers")}          # everyone with rows
SENS = {r: pd.read_csv(OUT / f"sensitivity_ratings_{r}.csv") for r in ("batters", "bowlers")}
SENS_SUM = pd.read_csv(OUT / "sensitivity.csv")
REMOVED = {r: pd.read_csv(OUT / f"step3_removed_{r}.csv") for r in ("batters", "bowlers")}
META = json.load(open(WEB / "data" / "meta.json", encoding="utf-8"))
ROBUST = json.load(open(WEB / "data" / "robustness.json", encoding="utf-8"))
LEAGUE = json.load(open(WEB / "data" / "league_split.json", encoding="utf-8"))
THR = json.load(open(OUT / "pressure_thresholds.json", encoding="utf-8"))
OMIT = json.load(open(WEB / "data" / "omissions.json", encoding="utf-8"))
MAP = pd.read_csv(ROOT / "competition_team_player_mapping.csv")
MAP_NAME = MAP.drop_duplicates("player_id").set_index("player_id").player_name
MFLAGS = pd.read_csv(OUT / "matches_flags.csv")
TEAMS = pd.read_csv(ROOT / "teams.csv").drop_duplicates("team_id").set_index("team_id").team_name

for r in ("batters", "bowlers"):
    for d in (TOP[r], UNF[r], POOL[r], ALLR[r]):
        pass
PB = {"batters": "balls_P", "bowlers": "deliveries_P"}   # pressure balls column per role


def role_of(pid):
    return "batters" if pid in set(TOP["batters"].player_id) else "bowlers"


# ------------------------------------------------------------------ evidence cards (parsed from outputs/evidence_cards.md)
def parse_cards():
    text = rd(OUT / "evidence_cards.md")
    out = {}
    for blk in re.split(r"(?m)^### ", text)[1:]:
        head, *body = blk.strip().splitlines()
        m = re.match(r"(Batter|Bowler) #(\d+): (.+?) \(id (\d+); (.+)\)$", head)
        role = "batters" if m.group(1) == "Batter" else "bowlers"
        pid = int(m.group(4))
        b = "\n".join(body)
        s = re.search(r"Sample: (\d+) pressure balls in (\d+) matches \(IPL (\d+), T20I (\d+)\)", b)
        c = {"role": role, "rank": int(m.group(2)), "name": m.group(3), "player_id": pid, "teams": m.group(5),
             "pressure_balls": int(s.group(1)), "matches_with_pressure_balls": int(s.group(2)), "ipl_pressure_balls": int(s.group(3)), "t20i_pressure_balls": int(s.group(4)),
             "raw_text": b}
        if role == "batters":
            k = re.search(r"strike rate ([\d.]+) pressure vs ([\d.]+) ordinary; runs index (\d+); dismissal ratio ([\d.]+)", b)
            c.update(sr_pressure=float(k.group(1)), sr_ordinary=float(k.group(2)), runs_index=int(k.group(3)), dismissal_ratio=float(k.group(4)))
        else:
            k = re.search(r"economy ([\d.]+) pressure vs ([\d.]+) ordinary; economy index (\d+); wicket ratio ([\d.]+)", b)
            c.update(econ_pressure=float(k.group(1)), econ_ordinary=float(k.group(2)), economy_index=int(k.group(3)), wicket_ratio=float(k.group(4)))
        bm = re.search(r"Best pressure match: (\d{4}-\d{2}-\d{2}) vs (.+?) \(\+([\d.]+) win prob\. added\)", b)
        c.update(best_match_date=bm.group(1), best_match_opponent=bm.group(2), best_match_wp_added=float(bm.group(3)))
        dm = re.search(r"delivery rate ([\d.]+) \((\d+) matches with 6\+ pressure balls\)", b)
        c.update(delivery_rate_card=float(dm.group(1)), delivery_matches=int(dm.group(2)))
        out[pid] = c
    return out


CARDS = parse_cards()


# ------------------------------------------------------------------ sensitivity: which variants each player is in (reproduces stage7 rule)
def variant_matrix(role):
    sens = SENS[role]
    ids = sens.player_id.values
    sd = ALLR[role].set_index("player_id").boot_sd.reindex(ids).values
    variants = [c for c in sens.columns if c not in ("player_id", "role", "main")]
    z10 = norm.ppf(1 - R["floor_quantile"])
    rows = {}
    for v in variants:
        x = sens[v].values - z10 * sd
        ok = ~np.isnan(x)
        top = set(ids[ok][np.argsort(-x[ok])[: R["top_n"]]])
        rows[v] = [p in top for p in ids]
    return pd.DataFrame(rows, index=ids), variants


VM = {}
for _r in ("batters", "bowlers"):
    VM[_r], _v = variant_matrix(_r)
    got = VM[_r].loc[TOP[_r].player_id].sum(axis=1).values
    assert (got == TOP[_r].variants_in_top10.values).all(), f"variant matrix does not reproduce variants_in_top10 for {_r}"
VARIANTS = list(VM["batters"].columns)


# ------------------------------------------------------------------ raw (unshrunk) pressure value per player, new aggregation of ball_values_*
def raw_values():
    res = {}
    for role, f in (("batters", "ball_values_bat"), ("bowlers", "ball_values_bowl")):
        v = pd.read_parquet(OUT / f"{f}.parquet", columns=["player", "P", "v"])
        g = v.groupby(["player", "P"]).v.agg(["mean", "size"]).unstack("P")
        g.columns = [f"{a}_{'P' if b == 1 else 'O'}" for a, b in g.columns]
        res[role] = g.rename(columns={"mean_P": "raw_pressure_mean_v", "mean_O": "raw_ordinary_mean_v", "size_P": "n_P", "size_O": "n_O"})
    return res


RAW = raw_values()


# ------------------------------------------------------------------ match traces
TRACE_IDS = {"tight": [13613, 13512, 16662], "one_sided": [19717, 40040, 15458]}   # the six matches drawn in figures/stage3_case_studies.png (read off its titles)


def trace_frame():
    bp = pd.read_parquet(OUT / "balls_pressure.parquet", columns=["match_id", "innings", "innings_ball_num", "wp_star", "LI", "live", "pressure"])
    bs = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "innings_ball_num", "overid", "batting_team_id", "target", "score_before", "wickets_lost", "is_legal"])
    ids = TRACE_IDS["tight"] + TRACE_IDS["one_sided"]
    d = bp[bp.match_id.isin(ids) & (bp.innings == 2)].merge(bs, on=["match_id", "innings", "innings_ball_num"])
    return d.sort_values(["match_id", "innings_ball_num"]).reset_index(drop=True)


def trace_replication_check():
    """Re-derive the six case-study ids with the stage3 selection rule and compare to the ids read off the figure."""
    mf = MFLAGS
    rs = mf[mf.clean & mf.in_rating_sample]
    tie = list(rs[rs.rtype == "tie"].match_id.head(1))
    runs = list(rs[(rs.rtype == "runs") & (rs.margin <= 2)].sort_values(["margin", "match_id"]).match_id.head(1))
    wk = list(rs[(rs.rtype == "wickets") & (rs.margin <= 1)].sort_values("match_id").match_id.head(1))
    lop = list(rs[rs.rtype == "runs"].sort_values("margin", ascending=False).match_id.head(2)) + list(rs[rs.rtype == "wickets"].sort_values("margin", ascending=False).match_id.head(1))
    return tie + runs + wk, lop


def trace_summary(tf):
    rows = []
    for kind, ids in TRACE_IDS.items():
        for mid in ids:
            d = tf[tf.match_id == mid]
            m = MFLAGS[MFLAGS.match_id == mid].iloc[0]
            pk = d.loc[d.LI.idxmax()]
            bat = TEAMS[int(d.batting_team_id.iloc[0])]
            rows.append(dict(kind=kind, match_id=mid, date=m.match_date, teams=f"{m.home_team} v {m.away_team}", chasing_team=bat, target=int(d.target.iloc[0]),
                             result=m.result, chase_balls=len(d), peak_LI=round(float(pk.LI), 2), peak_ball_of_chase=int(pk.innings_ball_num),
                             peak_over=int(pk.overid), live_balls=int(d.live.sum()), pressure_balls=int(d.pressure.sum()),
                             pressure_share_of_chase=round(float(d.pressure.mean()), 3), final_wp_star=round(float(d.wp_star.iloc[-1]), 3)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ leverage heatmap data (innings 2, live balls, all 808 clean matches)
def heatmap_data():
    bp = pd.read_parquet(OUT / "balls_pressure.parquet", columns=["match_id", "innings", "innings_ball_num", "LI", "live"])
    bs = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "innings_ball_num", "balls_left", "runs_required"])
    d = bp[(bp.innings == 2) & bp.live].merge(bs, on=["match_id", "innings", "innings_ball_num"])
    d = d[(d.runs_required >= 0) & (d.runs_required <= 200)]
    d["bl"] = (np.ceil(d.balls_left / 6) * 6).clip(6, 120).astype(int)        # balls left, 6-ball bands (label = upper edge)
    d["rr"] = (np.floor((d.runs_required - 1).clip(0) / 10) * 10 + 10).astype(int)   # runs required, 10-run bands (label = upper edge)
    g = d.groupby(["rr", "bl"]).LI.agg(["mean", "size"]).reset_index()
    return g[g["size"] >= CFG["stage3"]["heatmap_min_balls"]]


# ------------------------------------------------------------------ variance share and rank movers (new aggregations of existing columns)
def variance_share(role):
    e = UNF[role]
    b = e["B"] if role == "batters" else e["W"]
    s = e["C"] if role == "batters" else e["K"]
    tot = (b + s).var()
    return dict(role=role, n=len(e), var_baseline=b.var(), var_shift=s.var(), cov_2x=2 * np.cov(b, s)[0, 1], var_rating=tot,
                share_baseline=b.var() / tot, share_shift=s.var() / tot, share_covariance=2 * np.cov(b, s)[0, 1] / tot, corr_baseline_shift=np.corrcoef(b, s)[0, 1])


def movers(role, k=5):
    e = UNF[role][["player_id", "name", "pressure_rating", "simple_rating"]].dropna().copy()
    e["rank_regression"] = e.pressure_rating.rank(ascending=False, method="first").astype(int)
    e["rank_simple"] = e.simple_rating.rank(ascending=False, method="first").astype(int)
    e["moved_up_by_regression"] = e.rank_simple - e.rank_regression    # positive = regression ranks him higher than the simple version
    return e.sort_values("moved_up_by_regression", ascending=False).head(k), e.sort_values("moved_up_by_regression").head(k), e
