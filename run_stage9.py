"""Runs the additive RR stage (Stage 9) on top of a finished pipeline (outputs/ from run_all.py). Does not touch config.yaml or any earlier output."""
import subprocess, sys
for s in ("stage9a_terms.py", "stage9b_main.py", "stage9c_sensitivity.py", "stage9d_crosscheck.py"):
    print("==", s, flush=True)
    r = subprocess.run([sys.executable, "-I", f"src/{s}"])
    if r.returncode: sys.exit(f"{s} failed (stop; do not loosen anything)")
