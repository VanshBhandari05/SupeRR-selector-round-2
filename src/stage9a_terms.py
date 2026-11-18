"""Stage 9a: gates on the reuse of the Stage 5 bootstrap, then refit the rating terms (B,C,W,K) for each pressure-threshold variant.

Run: python -I src/stage9a_terms.py [--skip-variants]
Gates (stop on failure, nothing loosened):
  G1 bootstrap replay: refitting replicate #1 and #150 with replayed match weights reproduces the stored stage-5 ratings
  G2 flag reproduction: top20% flag rebuilt from LI equals the pipeline's pressure flag on every rating row
  G3 RR identification: team / mapping / playing-eleven tables agree on RR matches and players
Writes outputs/rr_fit/terms_<variant>.npz and audit_stage9a.md
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage9_common import *

T0 = time.time()
def log(*a): print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)
gates = []
def gate(name, ok, detail): gates.append((name, "PASS" if ok else "FAIL", detail)); log(("PASS " if ok else "FAIL ") + name + " | " + detail)

D = Data()
log(f"rows: batter {len(D.rows['bat']):,} (non-striker extra rows {D.n_extra_rows}, unresolved position {D.n_pos_unresolved}); bowler {len(D.rows['bowl']):,}; RR team id {D.rr_id}")
gate("batting position resolved for every rating row", D.n_pos_unresolved == 0 and len(D.rows["bat"]) == 150307, f"unresolved {D.n_pos_unresolved}; rows {len(D.rows['bat'])} (stage-4 table has 150,307)")
Wm = D.weights_replay()

# G2 flag reproduction
rb_ = D.flag(D.rows["bat"], "top20%"); rw_ = D.flag(D.rows["bowl"], "top20%")
mism = int((rb_ != D.rows["bat"].P.values).sum() + (rw_ != D.rows["bowl"].P.values).sum())
gate("top20% flag rebuilt from LI equals pipeline pressure flag", mism == 0, f"{mism} mismatching rows of {len(rb_) + len(rw_):,}")

# G1 replay
main = D.main_terms()
Pb, Pw = D.rows["bat"].P.values.astype(int), D.rows["bowl"].P.values.astype(int)
chk = D.refit_terms(Pb, Pw, Wm, log=lambda *a: None, only=[0, 1, 150])
mx = []
for j, i in enumerate([0, 1, 150]):
    mx.append(max(np.abs(chk["B"][j] + chk["C"][j] - (main["B"][i] + main["C"][i])).max(), np.abs(chk["W"][j] + chk["K"][j] - (main["W"][i] + main["K"][i])).max()))
gate("bootstrap replay reproduces stage-5 replicates", max(mx) < 1e-4, f"max |refit - stored| (pressure rating) for point, #1, #150: {[f'{m:.2e}' for m in mx]} (stored values are float32)")

# G3 identification
teams = pd.read_csv(ROOT / "teams.csv"); m = pd.read_csv(ROOT / "matches.csv"); pe = pd.read_csv(ROOT / "playing_eleven.csv"); mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv")
mf = pd.read_csv(OUT / "matches_flags.csv")
ipl = CFG["competition"]["ipl_comp_ids"]
rr_matches = m[m.comp_id.isin(ipl) & ((m.home_team_id == D.rr_id) | (m.away_team_id == D.rr_id))]
rr_in_sample = mf[mf.match_id.isin(rr_matches.match_id) & mf.in_rating_sample]
used = np.unique(D.rows["bat"][D.rows["bat"].rr == 1].match_id)
pe_rr = pe[pe.match_id.isin(rr_matches.match_id) & (pe.team_id == D.rr_id)]
sq = mp[(mp.team_id == D.rr_id) & mp.comp_id.isin(ipl)]
ball_rr_players = set(D.rows["bat"][D.rows["bat"].rr == 1].player) | set(D.rows["bowl"][D.rows["bowl"].rr == 1].player)
gate("RR matches: matches.csv vs rating rows", set(used) == set(rr_in_sample.match_id), f"matches.csv {len(rr_matches)} IPL RR matches 2022-26; {len(rr_in_sample)} in rating sample; {len(used)} in rating rows")
extra_pe = set(pe_rr[pe_rr.match_id.isin(used)].player_id) ; missing_in_balls = {p for p in ball_rr_players if p not in extra_pe}
gate("RR players: ball rows vs playing_eleven", len(missing_in_balls) == 0, f"{len(extra_pe)} RR players in playing_eleven for rating-sample matches; ball-row RR players not in playing_eleven: {sorted(missing_in_balls)}")
log(f"RR squad listings (mapping): {sq.groupby('comp_id').size().to_dict()}; union {sq.player_id.nunique()} players")

(O9 / "audit_stage9a.md").write_text("# Audit: Stage 9a\n\n" + pd.DataFrame(gates, columns=["gate", "result", "detail"]).to_markdown(index=False) + "\n", encoding="utf-8")
if any(g[1] == "FAIL" for g in gates):
    log("GATE FAILURE - stopping"); sys.exit(1)

np.savez_compressed(O9 / "terms_main.npz", **main)
if "--skip-variants" in sys.argv: sys.exit(0)
variants = [f"top{int(q * 100)}%" for q in C9["sensitivity_cutoffs"]] + ["within_innings"]
for v in variants:
    f = O9 / f"terms_{v.replace('%', 'pct')}.npz"
    if f.exists(): log(f"{v}: cached"); continue
    log(f"variant {v}: refitting point + {R['bootstrap_n']} replicates")
    t = D.refit_terms(D.flag(D.rows["bat"], v), D.flag(D.rows["bowl"], v), Wm, log=log)
    np.savez_compressed(f, **t)
log("done")
