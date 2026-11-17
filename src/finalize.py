"""Write submission_sheet.csv and FINAL_LOCK.md (project root) from the generated top-10 files.   Run: python -I src/finalize.py"""
import datetime
import hashlib
import warnings
from pathlib import Path

import pandas as pd
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
OUT = ROOT / CFG["paths"]["out_dir"]
mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv")
ids_by_name = mp.groupby("player_name").player_id.unique()

rows = []
for role in ("batters", "bowlers"):
    t = pd.read_csv(OUT / f"top10_{role}.csv")
    for _, r in t.iterrows():
        others = [i for i in ids_by_name[r["name"]] if i != r.player_id]
        other_txt = "; ".join(f"{i} ({', '.join(sorted(mp[mp.player_id == i].team_name.unique()))})" for i in others)
        rows.append(dict(list=role[:-1], rank=int(r["rank"]), name=r["name"], player_id=int(r.player_id), team=r.teams, name_has_two_ids=bool(others), other_id_with_same_name=other_txt))
sub = pd.DataFrame(rows)
sub.to_csv(ROOT / "submission_sheet.csv", index=False, encoding="utf-8")


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


files = [("config.yaml", ROOT / "config.yaml"), ("outputs/top10_batters.csv", OUT / "top10_batters.csv"), ("outputs/top10_bowlers.csv", OUT / "top10_bowlers.csv")]
L = ["# FINAL LOCK", "", f"Locked on {datetime.date.today().isoformat()} after a full `python run_all.py` from an empty `outputs/` folder.", "",
     "SHA-256 of the files that define the submission:", "", "| File | SHA-256 |", "|---|---|"] + [f"| {n} | `{sha(p)}` |" for n, p in files]
L += ["", "To verify: `python -c \"import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())\" <file>` and compare. Any change to config.yaml or either list changes a hash.", "",
      "Names with two player ids (check the Unstop dropdown by team): " + ("; ".join(f"{r['name']} (list uses {r.player_id}; other: {r.other_id_with_same_name})" for _, r in sub[sub.name_has_two_ids].iterrows()) or "none") + "."]
(ROOT / "FINAL_LOCK.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(sub.to_string(index=False)); print("\n".join(L))
