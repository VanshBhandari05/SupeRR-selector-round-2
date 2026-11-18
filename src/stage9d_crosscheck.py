"""Stage 9d: independent recomputation of the main point estimates with plain pandas (no Engine), and consistency checks. Writes audit_stage9.md pieces."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage9_analysis import *

D = Data(); gates = []
def gate(n, ok, d): gates.append((n, "PASS" if ok else "FAIL", d)); print(("PASS " if ok else "FAIL "), n, "|", d)
br, wr = D.ratings["bat"].set_index("player_id"), D.ratings["bowl"].set_index("player_id")
bat, bowl = D.rows["bat"].copy(), D.rows["bowl"].copy()
bat["adj"] = bat.v + bat.opp.map(wr.W) + bat.P * bat.opp.map(wr.K)
bowl["adj"] = bowl.v + bowl.opp.map(br.B) + bowl.P * bowl.opp.map(br.C)
gr = pd.read_csv(O9 / "rr_02_gap_ranking.csv")
mx = 0
for role, df, names in (("bat", bat, BAT_SLOTS), ("bowl", bowl, BOWL_SLOTS)):
    for i, s in enumerate(names):
        c = df[(df.slot == i) & (df.P == 1) & (df.grp == 0)]
        rr = c[c.rr == 1].adj.mean(); rest = c[c.rr == 0].adj.mean()
        row = gr[gr.slot == s].iloc[0]
        mx = max(mx, abs((rr - rest) - row.gap_vs_par), abs(rr - row.rr_value_per_ball), abs(rest - row.league_par_per_ball))
        assert int(row.rr_pressure_balls) == int(c[(c.rr == 1) & c.is_ball].shape[0]), (s, row.rr_pressure_balls)
gate("independent pandas recompute of RR cell means / par / gap (10 slots, pressure)", mx < 1e-9, f"max abs difference {mx:.2e}; ball counts identical")
# NOTE (correction to my first draft): the first version tested "mean of adjusted value ~ 0". That property does not exist: adj = v + opposition term, and only the
# unadjusted dWP0 is bin-centred (Stage 4). The adjusted par is therefore not zero (it is the mean of context + batter terms). The right check is dWP0 centring per bin.
for nm, df in (("batters", bat), ("bowlers", bowl)):
    mx_bin = df.groupby("bin").dWP0.mean().abs().max()
    gate(f"dWP0 is centred within every Stage-4 bin ({nm})", mx_bin < 1e-9, f"max |bin mean| {mx_bin:.2e}; mean adjusted value {df.adj.mean():.4f} (not expected to be 0)")
# pressure flag row counts vs pipeline (stage 3 / 2c): rating-sample pressure rows
gate("pressure rows in rating sample equal pipeline P column", int(bat.P.sum()) == int(D.flag(bat, "top20%").sum()), f"batter pressure rows {int(bat.P.sum()):,}; bowler {int(bowl.P.sum()):,}")
# every RR batting innings has 1 team; each rating-sample RR match has both an RR batting and RR bowling innings
bm = set(bat[bat.rr == 1].match_id); wm = set(bowl[bowl.rr == 1].match_id)
gate("each RR match has an RR batting innings and an RR bowling innings (usage denominators)", bm == wm and len(bm) == 75, f"batting {len(bm)}, bowling {len(wm)} matches")
# slots exhaustive: 4 bands + 6 cells cover all RR pressure rows
gate("slots are exhaustive and non-overlapping", int(((bat.rr == 1) & (bat.P == 1)).sum()) == int(sum(((bat.rr == 1) & (bat.P == 1) & (bat.slot == i)).sum() for i in range(4))) and (bowl.slot.between(0, 5)).all(), "all rows fall in exactly one slot")
pd.DataFrame(gates, columns=["gate", "result", "detail"]).to_csv(O9 / "stage9d_gates.csv", index=False)
sys.exit(0 if all(g[1] == "PASS" for g in gates) else 1)
