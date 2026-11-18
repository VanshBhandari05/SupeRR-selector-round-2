"""Stage 9b: main-threshold (top 20%) analysis: items 1-3. Writes CSVs to outputs/rr_fit/ and prints the tables.

Run: python -I src/stage9b_main.py
Nothing here changes pressure, ratings, gates or ranks; every number comes from the Stage 4/5 artefacts via stage9_common.
"""
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage9_analysis import *

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 400)
T0 = time.time()
def log(*a): print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)
def show(title, df, fl=".3f"): print(f"\n=== {title} ===\n" + df.to_markdown(index=False, floatfmt=fl), flush=True)


def main():
    D = Data(); Wm = D.weights_replay(); terms = D.main_terms(); ctx = Ctx(D)
    A = analyse(D, ctx, Wm, terms, D.rows["bat"].P.values.astype(int), D.rows["bowl"].P.values.astype(int))
    E, gr, ev, sq_ev, gm, tg, prof = A["E"], A["gr"], A["ev"], A["sq_ev"], A["gm"], A["tg"], A["prof"]
    rr_id = ctx.rr_id
    log(f"RR id {rr_id}; RR innings (matches) {int(E.n_inn[0])}; target slots {tg}")

    # ------------------------------------------------ 0. identification
    mf = pd.read_csv(OUT / "matches_flags.csv"); m = pd.read_csv(ROOT / "matches.csv"); pe = pd.read_csv(ROOT / "playing_eleven.csv")
    rrm = m[m.comp_id.isin(CFG["competition"]["ipl_comp_ids"]) & ((m.home_team_id == rr_id) | (m.away_team_id == rr_id))]
    flags = mf[mf.match_id.isin(rrm.match_id)]
    dropped = flags[~flags.in_rating_sample][["match_id", "match_date", "result", "drop_reason"]]
    bb = pd.read_parquet(OUT / "balls_state.parquet", columns=["match_id", "innings", "innings_ball_num", "batting_team_id", "bowling_team_id", "group", "in_rating_sample"])
    pr = pd.read_parquet(OUT / "balls_pressure.parquet", columns=["match_id", "innings", "innings_ball_num", "live", "pressure"])
    x = bb.merge(pr, on=["match_id", "innings", "innings_ball_num"]); x = x[(x.group == "IPL") & x.in_rating_sample & x.live]
    n_live_bat = int((x.batting_team_id == rr_id).sum()); n_live_bowl = int((x.bowling_team_id == rr_id).sum())
    n_p_bat = int(((x.batting_team_id == rr_id) & x.pressure).sum()); n_p_bowl = int(((x.bowling_team_id == rr_id) & x.pressure).sum())
    rb, rw = D.rows["bat"], D.rows["bowl"]
    ident = pd.DataFrame([
        ("RR team id (teams.csv name match)", rr_id),
        ("RR IPL matches 2022-26 in matches.csv", len(rrm)),
        ("  excluded by Stage 1 cleaning (no ball data / rain)", len(dropped)),
        ("RR IPL matches in the rating sample (used here)", int(E.n_inn[0])),
        ("RR players in playing_eleven for those matches", int(pe[pe.match_id.isin(E.rr_matches) & (pe.team_id == rr_id)].player_id.nunique())),
        ("RR players listed in mapping, IPL squads 2022-26 (union)", len(ctx.anyrr)),
        ("RR players listed in mapping, IPL 2026 squad", len(ctx.sq26)),
        ("RR live balls batting (rating sample)", n_live_bat), ("RR live balls bowling (rating sample)", n_live_bowl),
        ("RR PRESSURE deliveries batting", n_p_bat), ("RR PRESSURE deliveries bowling", n_p_bowl),
        ("RR PRESSURE deliveries total (batting + bowling, disjoint)", n_p_bat + n_p_bowl),
        ("  of the batting ones: balls faced excluding wides (rows behind batting cells)", int(((rb.rr == 1) & (rb.P == 1) & rb.is_ball).sum())),
        ("  of the bowling ones: rows behind bowling cells", int(((rw.rr == 1) & (rw.P == 1)).sum())),
        ("league IPL pressure deliveries in rating sample (all teams)", int(x.pressure.sum())),
        ("RR pressure deliveries per RR match (batting / bowling)", f"{n_p_bat / E.n_inn[0]:.1f} / {n_p_bowl / E.n_inn[0]:.1f}"),
    ], columns=["item", "value"])
    ident.to_csv(O9 / "rr_00_identification.csv", index=False); dropped.to_csv(O9 / "rr_00_rr_matches_excluded.csv", index=False)
    show("0. RR identification", ident); show("RR matches excluded by Stage-1 cleaning", dropped)

    # ------------------------------------------------ 1. profile
    prof[prof.side == "batting"].to_csv(O9 / "rr_01_batting_profile.csv", index=False); prof[prof.side == "bowling"].to_csv(O9 / "rr_01_bowling_profile.csv", index=False)
    cols = ["slot", "state", "rr_balls", "rr_balls_per_innings", "rr_value_per_ball", "league_par_per_ball", "gap_vs_par", "gap_p10", "gap_p90", "gap_p025", "gap_p975", "call"]
    show("1a. RR batting by position band (value = opposition-adjusted v per ball; gap vs rest-of-IPL; 80% interval p10-p90, 95% p025-p975)", prof[(prof.side == "batting")][cols])
    show("1b. RR bowling by phase x pace/spin cells and marginals", prof[(prof.side == "bowling")][cols])

    # ------------------------------------------------ 2. gap ranking + coverage
    gr.to_csv(O9 / "rr_02_gap_ranking.csv", index=False)
    show("2. RR pressure gaps (rank = below-par slots by gap x pressure balls per RR innings; d80/d95 = interval excludes 0)",
         gr.assign(d80=gr.distinguishable_below_par_80, d95=gr.distinguishable_below_par_95)[["rank_below_par_slots", "side", "slot", "rr_pressure_balls", "rr_pressure_balls_per_innings", "gap_vs_par", "gap_p10", "gap_p90", "p_gap_below0",
                                                                                                "priority_value_per_innings", "priority_p10", "priority_p90", "winprob_vs_par_per_innings", "p_in_boot_top3", "d80", "d95", "coverage_status"]])
    sq_ev.assign(rr_gap_rank=[None] * len(sq_ev)).drop(columns=["rr_gap_rank"]).to_csv(O9 / "rr_02b_rr_squad_slot_evidence.csv", index=False)

    # ------------------------------------------------ 3. candidates
    gmap = {(("bat" if r.side == "batting" else "bowl"), r.slot): r.rank_below_par_slots for r in gr.itertuples()}
    ev["rr_gap_rank"] = [gmap.get((r, s), np.nan) for r, s in zip(ev.slot_role, ev.slot)]
    allr = ev[ev.slot.str.startswith("ALL")].set_index(["slot_role", "player_id"])
    ev["record_overall_in_slot_role"] = [allr.loc[(r, p), "slot_record"] for r, p in zip(ev.slot_role, ev.player_id)]
    ev.to_csv(O9 / "rr_03_candidate_slot_evidence.csv", index=False)
    keep = ["target_slot", "rr_gap_rank", "rr_gap_vs_par", "rr_gap_p_below0", "rr_gap_distinguishable_80", "list_role", "list_rank", "name", "nationality", "nationality_class", "slot_record", "n_pressure_balls", "n_ipl", "n_t20i",
            "excess_per_ball", "p10", "p90", "p025", "p975", "excess_winprob_per_100_balls", "supported", "rank_in_class_among_supported", "rr_2026_squad", "rr_any_ipl_2022_26", "clears_gates_in_slot_role", "note"]
    gm = gm.sort_values(["target_slot", "supported", "nationality_class", "rank_in_class_among_supported", "n_pressure_balls"], ascending=[True, False, True, True, False])
    gm[keep].to_csv(O9 / "rr_03_candidate_gap_map.csv", index=False)
    show("3. Candidates with >=40 pressure balls in a target slot (all 40 listed players were evaluated; the rest are suppressed in the CSV). supported = 10th pct of excess > 0",
         gm[gm.n_pressure_balls >= C9["min_slot_pressure_balls"]][[k for k in keep if k not in ("note", "rr_gap_distinguishable_80", "clears_gates_in_slot_role")]])
    sup_counts = gm.groupby("target_slot").apply(lambda d: pd.Series(dict(players_evaluated=len(d), with_40plus_balls=int((d.n_pressure_balls >= 40).sum()), supported=int(d.supported.sum()),
                                                                           supported_indian=int((d.supported & (d.nationality_class == "Indian")).sum()), supported_overseas=int((d.supported & (d.nationality_class == "overseas")).sum()),
                                                                           supported_nationality_unknown=int((d.supported & (d.nationality_class == "not in supplied data")).sum()))), include_groups=False).reset_index()
    show("3a. How many of the 40 listed players can speak to each target slot", sup_counts, ".0f")
    summ = ev[ev.slot.str.startswith("ALL") & (ev.slot_role == ev.list_role)][["list_role", "list_rank", "name", "player_id", "nationality", "nationality_class", "slot_record", "n_ipl", "n_t20i", "n_pressure_balls",
                                                                                "excess_per_ball", "p10", "p90", "excess_winprob_per_100_balls", "pressure_rating", "floor_p10", "rr_2026_squad", "rr_any_ipl_2022_26"]]
    summ.rename(columns={"slot_record": "pressure_record", "n_pressure_balls": "pressure_balls_in_listed_role", "excess_per_ball": "excess_vs_par_per_ball_slot_mix_adj"}).to_csv(O9 / "rr_03_candidate_summary.csv", index=False)
    show("3b. Overall pressure excess vs league par (slot-mix adjusted) in the listed role, with nationality, record and RR flags", summ.drop(columns=["player_id"]))

    # RR squad overseas/Indian composition (2026 listing) for the 4-overseas-slot context
    sqc = sq_ev[sq_ev.slot.str.startswith("ALL")].drop_duplicates("player_id")[["player_id", "name", "nationality", "nationality_class"]]
    sqc["clears_gates_bat_or_bowl"] = sqc.player_id.map(lambda p: any(bool(D.ratings[r].set_index("player_id").eligible.get(p, False) and D.ratings[r].set_index("player_id").active.get(p, False)) for r in ("bat", "bowl")))
    sqc.to_csv(O9 / "rr_02c_rr_2026_squad_nationality.csv", index=False)
    show("RR 2026 squad listing: nationality (derived from T20I squad listings) and gate status", sqc.drop(columns=["player_id"]))
    log("main outputs written")


if __name__ == "__main__":
    main()
