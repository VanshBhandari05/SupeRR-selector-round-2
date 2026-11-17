"""Stage 7: final ranking, evidence cards, sanity checks, identity check.

Rule (blueprint): eligible + active players; drop anyone whose pressure shift is reliably negative (90th percentile of the
bootstrap shift below zero); sort by the floor (10th percentile of the bootstrap pressure rating); ties by delivery rate, then
pressure balls. Run: python -I src/stage7_rank.py
Writes outputs/top10_batters.csv, top10_bowlers.csv, evidence_cards.md, eligible_table_*.csv, audit_stage7.md
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import norm

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
R = CFG["rating"]
OUT = ROOT / CFG["paths"]["out_dir"]
def md(df, fl=".3f"): return df.to_markdown(index=False, floatfmt=fl)

bs = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "striker_id", "bowler_id", "batting_team_id", "bowling_team_id", "group", "match_date"])
mf = pd.read_csv(OUT / "matches_flags.csv")
teams = pd.read_csv(ROOT / "teams.csv").drop_duplicates("team_id").set_index("team_id").team_name
mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv")
names = mp.drop_duplicates("player_id").set_index("player_id").player_name
bat_v = pd.read_parquet(OUT / "ball_values_bat.parquet"); bowl_v = pd.read_parquet(OUT / "ball_values_bowl.parquet")
z10 = norm.ppf(1 - R["floor_quantile"])
dup_names = mp.groupby("player_name").player_id.nunique(); dup_names = set(dup_names[dup_names > 1].index)

out = {}; lines = []; checks = []
for role, rv, id_ in (("batters", bat_v, "striker_id"), ("bowlers", bowl_v, "bowler_id")):
    r = pd.read_csv(OUT / f"player_ratings_{role}.csv")
    r["baseline"] = r.B if role == "batters" else r.W; r["shift"] = r.C if role == "batters" else r.K
    sens = pd.read_csv(OUT / f"sensitivity_ratings_{role}.csv"); ids = sens.player_id.values
    sd = r.set_index("player_id").boot_sd.reindex(ids).values
    variants = [c for c in sens.columns if c not in ("player_id", "role", "main")]
    intop = np.zeros(len(ids))
    for v in variants:
        x = sens[v].values - z10 * sd; ok = ~np.isnan(x); top = set(ids[ok][np.argsort(-x[ok])[:R["top_n"]]])
        intop += np.array([p in top for p in ids])
    frag = pd.DataFrame({"player_id": ids, "variants_in_top10": intop, "n_variants": len(variants)}); frag["fragile"] = frag.variants_in_top10 < frag.n_variants / 2
    r = r.merge(frag, on="player_id", how="left")
    pool = r[r.eligible & r.active].copy()
    pool["reliably_negative_shift"] = pool.shift_p90 < 0
    ranked = pool[~pool.reliably_negative_shift].sort_values(["floor_p10", "delivery_rate", "balls_P" if role == "batters" else "deliveries_P"], ascending=[False, False, False]).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)
    top = ranked.head(R["top_n"]).copy()
    # teams, pressure ball split, best pressure match
    pr = rv[rv.P == 1]
    split = pr.groupby(["player", "group"]).size().unstack(fill_value=0)
    split["IPL"] = split.get("IPL", 0); split["T20I"] = split.drop(columns=["IPL"]).sum(axis=1)
    bm = pr.groupby(["player", "match_id"]).dWP0.sum().reset_index().sort_values("dWP0", ascending=False).drop_duplicates("player").set_index("player")
    tm_col = "batting_team_id" if role == "batters" else "bowling_team_id"; opp_col = "bowling_team_id" if role == "batters" else "batting_team_id"
    d = bs[(bs.group == "IPL")]; ipl_team = d.groupby(id_)[tm_col].agg(lambda s: s.mode().iloc[0]) if len(d) else pd.Series(dtype=float)
    d = bs[(bs.group != "IPL")]; nat_team = d.groupby(id_)[tm_col].agg(lambda s: s.mode().iloc[0])
    def cell(pid):
        ipl, nat = ipl_team.get(pid), nat_team.get(pid)
        return " / ".join(x for x in (teams.get(ipl, "") if ipl == ipl and ipl is not None else "", teams.get(nat, "") if nat == nat and nat is not None else "") if x)
    top["name"] = top.player_id.map(names); top["teams"] = top.player_id.map(cell)
    top["pressure_balls_IPL"] = top.player_id.map(split["IPL"]).fillna(0).astype(int); top["pressure_balls_T20I"] = top.player_id.map(split["T20I"]).fillna(0).astype(int)
    def best(pid):
        if pid not in bm.index: return ""
        m_ = int(bm.loc[pid, "match_id"]); row = mf[mf.match_id == m_].iloc[0]
        ball = bs[(bs.match_id == m_) & (bs[id_] == pid)]
        opp = teams.get(ball[opp_col].iloc[0], "?") if len(ball) else "?"
        return f"{row.match_date} vs {opp} (+{bm.loc[pid, 'dWP0']:.2f} win prob. added)"
    top["best_pressure_match"] = top.player_id.map(best)
    # sanity checks
    if role == "batters":
        top["sign_check"] = (top.runs_index_P > 100) | (top.dismissal_ratio_P < 1)
        top["sign_check_strict"] = top["sign_check"]
    else:
        # POST-HOC AMENDMENT (CHANGES_FOR_REVIEW #33a): bowler sign check = economy index above 100 OR wicket ratio above 1 on pressure balls,
        # mirroring the batter check. The original economy-only rule is kept as sign_check_strict and drives the appendix list.
        top["sign_check_strict"] = top.economy_index_P > 100
        top["sign_check"] = (top.economy_index_P > 100) | (top.wicket_ratio_P > 1)
    # identity check
    def ident(pid):
        n = names.get(pid); ids_for_name = mp[mp.player_name == n].player_id.unique()
        return pd.Series({"id_resolves_to_one_name": mp[mp.player_id == pid].player_name.nunique() == 1,
                          "duplicate_name": n in dup_names, "other_ids_same_name": ",".join(str(i) for i in ids_for_name if i != pid),
                          "mapping_teams": "; ".join(sorted(mp[mp.player_id == pid].team_name.unique()))})
    top = pd.concat([top.reset_index(drop=True), top.player_id.apply(ident).reset_index(drop=True)], axis=1)
    out[role] = top
    cols = ["rank", "player_id", "name", "teams", "pressure_rating", "floor_p10", "p90", "baseline", "shift", "p_top10", "p_top20", "rank_p10", "rank_p90", "delivery_rate", "fragile", "variants_in_top10", "sign_check", "sign_check_strict", "duplicate_name"]
    top[cols].to_csv(OUT / f"top10_{role}.csv", index=False)
    ranked.assign(name=ranked.player_id.map(names)).drop(columns=[]).to_csv(OUT / f"eligible_table_{role}.csv", index=False)
    pool_all = r[r.eligible].assign(name=lambda x: x.player_id.map(names)).sort_values("floor_p10", ascending=False)
    pool_all.to_csv(OUT / f"unfiltered_eligible_{role}.csv", index=False)
    lines += [f"## Top 10 {role}", "", md(top[["rank", "name", "player_id", "teams", "pressure_rating", "floor_p10", "p90", "baseline", "shift", "p_top10", "p_top20", "delivery_rate", "fragile", "sign_check"]]), "",
              f"Removed for a reliably negative shift: {int(pool.reliably_negative_shift.sum())}. Candidates (eligible and active): {len(pool)}; ranked pool after removal: {len(ranked)}.", "",
              f"Ranks 11 to 20 (for face validity):", "", md(ranked.iloc[10:20].assign(name=lambda x: x.player_id.map(names))[["rank", "name", "pressure_rating", "floor_p10", "p_top10"]]), ""]
    checks.append(dict(role=role, listed=len(top), top20_prob_below_0_6=int((top.p_top20 < 0.6).sum()), sign_check_fails=int((~top.sign_check).sum()), strict_sign_check_fails=int((~top.sign_check_strict).sum()), fragile=int(top.fragile.sum()), duplicate_names=int(top.duplicate_name.sum()), id_ok=int(top.id_resolves_to_one_name.all())))

cards = ["# Evidence cards", ""]
for role in ("batters", "bowlers"):
    for _, t in out[role].iterrows():
        a, o = ("sr", "sr") if role == "batters" else ("economy", "economy")
        cards += [f"### {role[:-1].title()} #{int(t['rank'])}: {t['name']} (id {int(t.player_id)}; {t.teams})", "",
                  f"- Sample: {int(t.balls_P if role == 'batters' else t.deliveries_P)} pressure balls in {int(t.matches_P)} matches (IPL {t.pressure_balls_IPL}, T20I {t.pressure_balls_T20I})",
                  f"- Rating: pressure rating {t.pressure_rating:.3f}, floor (10th pct) {t.floor_p10:.3f}, 90th pct {t.p90:.3f}; baseline {(t.B if role == 'batters' else t.W):.3f}, pressure shift {(t.C if role == 'batters' else t.K):.4f}",
                  (f"- Cricket numbers: strike rate {t.sr_P:.1f} pressure vs {t.sr_O:.1f} ordinary; runs index {t.runs_index_P:.0f}; dismissal ratio {t.dismissal_ratio_P:.2f}" if role == "batters"
                   else f"- Cricket numbers: economy {t.economy_P:.2f} pressure vs {t.economy_O:.2f} ordinary; economy index {t.economy_index_P:.0f}; wicket ratio {t.wicket_ratio_P:.2f}"),
                  f"- Consistency: delivery rate {t.delivery_rate:.2f} ({int(t.delivery_matches)} matches with 6+ pressure balls); P(top 10) {t.p_top10:.2f}, P(top 20) {t.p_top20:.2f}, 80% rank interval {t.rank_p10:.0f}-{t.rank_p90:.0f}; in the top 10 under {int(t.variants_in_top10)} of {int(t.n_variants)} sensitivity variants ({'FRAGILE' if t.fragile else 'stable'})",
                  f"- Best pressure match: {t.best_pressure_match}", ""]
(OUT / "evidence_cards.md").write_text("\n".join(cards), encoding="utf-8")
chk = pd.DataFrame(checks)
L = ["# Audit: Stage 7 (final ranking)", "", "Rule: eligible + active, drop reliably negative shift, sort by bootstrap floor (10th percentile of pressure rating), ties by delivery rate then pressure balls.", "", md(chk, ".0f"), ""] + lines
(OUT / "audit_stage7.md").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
