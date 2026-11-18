"""Stage 9c: item 4. Re-run the gap ranking (2) and the candidate mapping (3) under the pressure-threshold variants already in the sensitivity grid.

Each variant: pressure flag rebuilt from LI (same code path as stage6b), ridge fits redone with penalties fixed (point + the same 300 replayed whole-match
resamples), then the identical analyse() as the main run. The main run's target slots, candidates and rules are NOT re-chosen from the variant: the candidate list is the
Stage-7 top 20 as submitted; gap slots and 'supported' names are recomputed in each variant and compared with main.
Run (after stage9a has written terms_*.npz): python -I src/stage9c_sensitivity.py
"""
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage9_analysis import *

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 400)
T0 = time.time()
def log(*a): print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)
def show(title, df, fl=".3f"): print(f"\n=== {title} ===\n" + df.to_markdown(index=False, floatfmt=fl), flush=True)

VARIANTS = [f"top{int(q * 100)}%" for q in C9["sensitivity_cutoffs"]] + ["within_innings"]
ASKED = ["top15%", "top25%", "top30%", "within_innings"]     # the four named in the brief; top10% is in the grid too and is shown as an extra


def load_terms(v):
    z = np.load(O9 / f"terms_{v.replace('%', 'pct')}.npz"); return {k: z[k] for k in z.files}


def slot_key(r): return f"{r.side}:{r.slot}"


def main():
    D = Data(); Wm = D.weights_replay(); ctx = Ctx(D)
    runs = {"main": analyse(D, ctx, Wm, D.main_terms(), D.rows["bat"].P.values.astype(int), D.rows["bowl"].P.values.astype(int), with_profile=False)}
    for v in VARIANTS:
        runs[v] = analyse(D, ctx, Wm, load_terms(v), D.flag(D.rows["bat"], v), D.flag(D.rows["bowl"], v), with_profile=False)
        log(f"{v}: done; target slots {runs[v]['tg']}")
    # ------------------------------------------------ gap ranking comparison
    main_gr = runs["main"]["gr"].set_index(runs["main"]["gr"].apply(slot_key, axis=1))
    slots = list(main_gr.index)
    tab = []
    for k, r in runs.items():
        g = r["gr"].set_index(r["gr"].apply(slot_key, axis=1)).reindex(slots)
        for s in slots:
            tab.append(dict(variant=k, slot=s, rr_pressure_balls=int(g.loc[s, "rr_pressure_balls"]), per_innings=g.loc[s, "rr_pressure_balls_per_innings"], gap_vs_par=g.loc[s, "gap_vs_par"], gap_p10=g.loc[s, "gap_p10"], gap_p90=g.loc[s, "gap_p90"],
                            p_gap_below0=g.loc[s, "p_gap_below0"], priority=g.loc[s, "priority_value_per_innings"], rank_below_par=g.loc[s, "rank_below_par_slots"], distinguishable_80=bool(g.loc[s, "distinguishable_below_par_80"]),
                            distinguishable_95=bool(g.loc[s, "distinguishable_below_par_95"]), coverage=g.loc[s, "coverage_status"]))
    gtab = pd.DataFrame(tab); gtab.to_csv(O9 / "rr_04_sensitivity_gap_ranks.csv", index=False)
    wide = gtab.pivot(index="slot", columns="variant", values="rank_below_par")[["main"] + VARIANTS].reindex(slots)
    show("4a. Gap rank by variant (NaN = slot is at or above par under that variant, so not a gap)", wide.reset_index(), ".0f")
    d80 = gtab.pivot(index="slot", columns="variant", values="distinguishable_80")[["main"] + VARIANTS].reindex(slots)
    show("4a'. Gap distinguishable from par at 80% (interval excludes 0)", d80.reset_index())
    pb0 = gtab.pivot(index="slot", columns="variant", values="p_gap_below0")[["main"] + VARIANTS].reindex(slots)
    show("4a''. P(gap < 0) in the bootstrap by variant", pb0.reset_index(), ".2f")

    main_top3 = list(main_gr.sort_values("rank_below_par_slots").head(3).index)
    main_below = set(main_gr.index[main_gr.rank_below_par_slots.notna()])
    summ = []
    for v in VARIANTS:
        g = gtab[gtab.variant == v].set_index("slot").reindex(slots)
        top3 = list(g.sort_values("rank_below_par").head(3).index); below = set(g.index[g.rank_below_par.notna()])
        tau = kendalltau(main_gr.priority_value_per_innings.reindex(slots).values, g.priority.values).correlation
        kept_exact = int(sum(1 for s in main_below if g.loc[s, "rank_below_par"] == main_gr.loc[s, "rank_below_par_slots"]))
        summ.append(dict(variant=v, in_brief=v in ASKED, kendall_tau_priority_all10=tau, below_par_set_overlap=f"{len(main_below & below)} of {len(main_below)} (variant has {len(below)})",
                         top3_set_overlap=len(set(top3) & set(main_top3)), top3_same_order=top3 == main_top3, rank1_same=top3[0] == main_top3[0], main_below_slots_keeping_exact_rank=f"{kept_exact} of {len(main_below)}",
                         variant_top3="; ".join(top3), distinguishable80_slots="; ".join(g.index[g.distinguishable_80]) or "none", distinguishable95_slots="; ".join(g.index[g.distinguishable_95]) or "none"))
    gsum = pd.DataFrame(summ); gsum.to_csv(O9 / "rr_04_sensitivity_gap_summary.csv", index=False)
    show(f"4b. Gap-ranking survival. Main top 3: {main_top3}; main distinguishable-at-80%: {list(main_gr.index[main_gr.distinguishable_below_par_80])}", gsum)

    # ------------------------------------------------ names
    def supported(r):
        e = r["ev"]; e = e[~e.slot.str.startswith("ALL")]
        return e.assign(key=e.slot_role + ":" + e.slot)
    main_ev = supported(runs["main"]); main_sup = main_ev[main_ev.supported & main_ev.key.isin([f"{'bat' if s.startswith('batting') else 'bowl'}:{s.split(':')[1]}" for s in main_top3])]
    recs = []
    for r in main_sup.itertuples():
        row = dict(slot=r.key, name=r.name, nationality_class=r.nationality_class, list_role=r.list_role, list_rank=r.list_rank, main_n=r.n_pressure_balls, main_excess=r.excess_per_ball, main_p10=r.p10)
        n_sup = 0; n_sup_asked = 0
        for v in VARIANTS:
            ev = supported(runs[v]); x = ev[(ev.key == r.key) & (ev.player_id == r.player_id)]
            ok = bool(len(x) and x.supported.iloc[0]); pt = bool(len(x) and (x.n_pressure_balls.iloc[0] >= C9["min_slot_pressure_balls"]) and x.excess_per_ball.iloc[0] > 0)
            row[f"{v}: n"] = int(x.n_pressure_balls.iloc[0]) if len(x) else 0
            row[f"{v}: excess"] = x.excess_per_ball.iloc[0] if len(x) else np.nan
            row[f"{v}: p10"] = x.p10.iloc[0] if len(x) else np.nan
            row[f"{v}: supported"] = ok; row[f"{v}: point>0"] = pt
            n_sup += ok; n_sup_asked += ok and v in ASKED
        row["supported_in_variants_of_5"] = n_sup; row["supported_in_brief_variants_of_4"] = n_sup_asked
        recs.append(row)
    names = pd.DataFrame(recs)
    # new names: supported at a main target slot in some variant but not in main
    new = []
    for v in VARIANTS:
        ev = supported(runs[v]); keys = [f"{'bat' if s.startswith('batting') else 'bowl'}:{s.split(':')[1]}" for s in main_top3]
        for r in ev[ev.supported & ev.key.isin(keys)].itertuples():
            if not ((main_sup.key == r.key) & (main_sup.player_id == r.player_id)).any():
                new.append(dict(variant=v, slot=r.key, name=r.name, nationality_class=r.nationality_class, n=r.n_pressure_balls, excess=r.excess_per_ball, p10=r.p10))
    newdf = pd.DataFrame(new)
    names.to_csv(O9 / "rr_04_sensitivity_names.csv", index=False); newdf.to_csv(O9 / "rr_04_sensitivity_new_names.csv", index=False)
    show("4c. Main 'supported' names at main's top-3 gap slots: survival by variant", names[["slot", "name", "nationality_class", "main_n", "main_excess", "main_p10"] + [f"{v}: supported" for v in VARIANTS] + ["supported_in_variants_of_5", "supported_in_brief_variants_of_4"]])
    show("4d. Names supported at a main target slot in a variant but NOT in main", newdf if len(newdf) else pd.DataFrame({"note": ["none"]}))
    # also: per-variant, supported names under the variant's OWN top-3 slots
    own = []
    for v in VARIANTS:
        ev = supported(runs[v])
        for (role, slot) in runs[v]["tg"]:
            for r in ev[(ev.key == f"{role}:{slot}") & ev.supported].itertuples():
                own.append(dict(variant=v, variant_target_slot=f"{role}:{slot}", name=r.name, nationality_class=r.nationality_class, n=r.n_pressure_balls, excess=r.excess_per_ball, p10=r.p10))
    pd.DataFrame(own).to_csv(O9 / "rr_04_sensitivity_names_own_targets.csv", index=False)

    n_main = len(names)
    ssum = pd.DataFrame([dict(item="main top-3 gap slots", value="; ".join(main_top3)),
                         dict(item="main supported (slot, name) pairs at those slots", value=n_main),
                         dict(item="pairs still supported in ALL 5 grid variants", value=int((names.supported_in_variants_of_5 == 5).sum())),
                         dict(item="pairs still supported in ALL 4 variants named in the brief", value=int((names.supported_in_brief_variants_of_4 == 4).sum())),
                         dict(item="pairs supported in at least 3 of 5", value=int((names.supported_in_variants_of_5 >= 3).sum())),
                         dict(item="pairs supported in none of the variants", value=int((names.supported_in_variants_of_5 == 0).sum())),
                         dict(item="variants whose top-3 gap set equals main's (of 5)", value=int(gsum.top3_set_overlap.eq(3).sum())),
                         dict(item="variants whose top-3 gap ORDER equals main's (of 5)", value=int(gsum.top3_same_order.sum())),
                         dict(item="variants whose #1 gap equals main's (of 5)", value=int(gsum.rank1_same.sum())),
                         dict(item="variants in which main's one 80%-distinguishable gap is still distinguishable (of 5)", value=int(sum(bool(d80.loc[s, v]) for v in VARIANTS for s in main_gr.index[main_gr.distinguishable_below_par_80])))])
    ssum.to_csv(O9 / "rr_04_sensitivity_summary.csv", index=False)
    show("4e. Survival summary", ssum)
    log("sensitivity outputs written")


if __name__ == "__main__":
    main()
