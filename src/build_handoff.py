"""Build the handoff pack: PPT_and_Document_Preparation/ (read-only on the pipeline outputs).   Run: python -I src/build_handoff.py"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd

import handoff_data as H
import handoff_figs as F
import handoff_docs_a as A
import handoff_docs_b as B

PACK = H.PACK
PACK.mkdir(exist_ok=True)

# 0. replicate the trace-case selection and compare with the ids read off the stage-3 figure
tight, lop = H.trace_replication_check()
print("trace selection replicated:", tight, lop, "| used:", H.TRACE_IDS)
assert tight == H.TRACE_IDS["tight"] and lop == H.TRACE_IDS["one_sided"], "trace ids do not match the stage-3 selection rule"

# 1. data and figures
tf = H.trace_frame()
rs, info = F.build_all(tf)
B.copy_originals()
B.copy_files()
ts = H.trace_summary(tf)
ts.to_csv(PACK / "03_trace_summary.csv", index=False, encoding="utf-8")
ser = tf.merge(ts[["match_id", "kind"]], on="match_id")[["match_id", "kind", "innings_ball_num", "overid", "LI", "wp_star", "live", "pressure"]].rename(columns={"innings_ball_num": "ball_of_chase", "overid": "over"})
ser["LI"] = ser.LI.round(4)
ser["wp_star"] = ser.wp_star.round(4)
ser.to_csv(PACK / "03_trace_series.csv", index=False, encoding="utf-8")

# 2. documents
A.doc_00()
A.doc_01()
A.doc_02()
A.doc_03(ts, info)
A.doc_04()
sur, om = B.doc_05()
B.doc_06(rs)
B.write_player_tables()
B.doc_07(ts)
B.doc_08(info)
B.doc_09()
B.doc_10()
B.doc_11(ts, sur)
B.doc_12()

# 3. automated checks, then record the result in 01 and 12
r = subprocess.run([sys.executable, "-I", str(PACK / "check_handoff.py")], capture_output=True, text=True, encoding="utf-8")
print(r.stdout)
if r.stderr:
    print(r.stderr)
block = f"\n## Automated check result (`check_handoff.py`, run {A.TODAY})\n\n```\n{r.stdout.strip()}\n```\n"
for f in ("01_RANKINGS.md", "12_UNSTOP_ENTRIES.md"):
    t = (PACK / f).read_text(encoding="utf-8")
    t = t.split("\n## Automated check result")[0].rstrip() + "\n" + block
    (PACK / f).write_text(t, encoding="utf-8")
print("exit code of check script:", r.returncode)
