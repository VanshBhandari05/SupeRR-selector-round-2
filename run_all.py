"""Regenerate every table, chart, list and the report from the supplied CSVs with one command:  python run_all.py

Stops at the first stage whose gates fail (never loosens anything). Seeds are fixed in config.yaml.
Stage 0/1 needs data_external/external_totals.csv (public scorecard totals, validation only).
The PDF export needs a Chromium-based browser (Edge or Chrome); it is skipped with a message otherwise.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGES = ["stage0_1.py", "stage2_run.py", "stage2c_leverage.py", "stage3_prove.py", "stage4_ratings.py", "stage5_bootstrap.py",
          "stage6_reliability.py", "stage6b_sensitivity.py", "stage7_rank.py", "stage8_exhibits.py",
          "step2_bowler_net.py", "step3_reports.py", "final_text.py", "finalize.py", "build_report.py", "export_pdf.py"]
for s in STAGES:
    print(f"=== {s}", flush=True)
    rc = subprocess.call([sys.executable, "-I", str(ROOT / "src" / s)], cwd=ROOT)
    if rc != 0:
        print(f"STOP: {s} exited with code {rc}. Read outputs/audit for that stage before continuing.")
        sys.exit(rc)
print("all stages complete")
