# SupeRR Selector Season 2 - Round 2

**Who delivers when it matters:** a pressure-adjusted rating of T20 batters and bowlers, built from ball-by-ball data.

The model estimates win probability ball by ball, measures how much each delivery moves it, weights that by game leverage, and shrinks the result by sample size. Players are ranked with bootstrap uncertainty and sensitivity checks. A separate "clutch" trait is not reliably measurable in this data (split-half reliability of about 0.13 for batters and 0.15 for bowlers), so the ratings measure proven quality in high-leverage situations.

Live results site: https://vanshbhandari05.github.io/pressure-room

## Contents

| Path | What it is |
|---|---|
| `src/` | Pipeline stages (win-probability engine, leverage, ratings, bootstrap, reliability, sensitivity, ranking, report build) |
| `run_all.py` | Runs every stage in order and stops at the first failed gate |
| `config.yaml` | All parameters and seeds |
| `outputs/` | Audits, rating tables, top-10 lists, rationales (large intermediates are not committed) |
| `figures/` | Charts used in the report |
| `report.md`, `report.html`, `report.pdf` | The write-up |
| `PPT_and_Document_Preparation/` | Numbers, figures and notes prepared for the deck and documents |
| `submission_sheet.csv`, `FINAL_LOCK.md` | Final submission and file hashes |

## Dataset

The competition dataset is proprietary and **not included**. See [DATA.md](DATA.md) for a description and a few sample rows.

## Reproduce

```
pip install -r requirements.txt
# place the six dataset CSVs in the repo root, then:
python run_all.py
```

PDF export needs Edge or Chrome and is skipped otherwise.
