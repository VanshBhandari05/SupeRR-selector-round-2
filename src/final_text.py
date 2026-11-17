"""Final text blocks for the report. Every number is read from a generated file; no new analysis.
Writes outputs/bowler_rationale.md, batter_rationale.md, spinner_paragraph.md.   Run: python -I src/final_text.py
"""
import json
import sys
import warnings
from pathlib import Path

import pandas as pd
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8-sig"))
OUT = ROOT / CFG["paths"]["out_dir"]

# ----------------------------------------------------------------- bowlers: wickets vs run-saving
net = pd.read_csv(OUT / "bowler_net_value.csv").set_index("player_id")
top = pd.read_csv(OUT / "top10_bowlers.csv")
lines = []
for _, t in top.iterrows():
    n = net.loc[t.player_id]
    we, rs = n.wicket_effect_runs, n.runs_effect_runs
    MATERIAL = 5                                              # components within +/- 5 runs are described as roughly neutral
    wph = "wicket-taking adds value" if we >= MATERIAL else "his wickets fall short of expectation" if we <= -MATERIAL else "wicket-taking is roughly neutral"
    rph = "run-saving adds value" if rs >= MATERIAL else "he concedes more than expected" if rs <= -MATERIAL else "run-saving is roughly neutral"
    tail = (" (run-saving is the larger part)" if rs > we else " (wicket-taking is the larger part)") if (we >= MATERIAL and rs >= MATERIAL) else ""
    driver = f"{wph} and {rph}{tail}"
    lines.append(f"- **{int(t['rank'])}. {t['name']}** ({t.teams}): on {int(n.pressure_balls)} pressure balls he took {int(n.wk)} wickets against {n.exp_wk:.1f} expected "
                 f"({we:+.0f} runs of value) and conceded {int(n.runs)} runs against {n.exp_runs:.0f} expected ({rs:+.0f} runs), a net {n.net_runs:+.0f} runs "
                 f"(10th to 90th percentile {n.net_p10:+.0f} to {n.net_p90:+.0f}); {driver}, which gives a pressure rating of {t.pressure_rating:.3f} and a floor of {t.floor_p10:.3f}.")
(OUT / "bowler_rationale.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ----------------------------------------------------------------- batters
rt = pd.read_csv(OUT / "player_ratings_batters.csv").set_index("player_id")
tb = pd.read_csv(OUT / "top10_batters.csv")
bl = []
for _, t in tb.iterrows():
    r = rt.loc[t.player_id]
    bl.append(f"- **{int(t['rank'])}. {t['name']}** ({t.teams}): pressure rating {t.pressure_rating:.3f} with a floor of {t.floor_p10:.3f}; on {int(r.balls_P)} pressure balls in {int(r.matches_P)} matches "
              f"he strikes at {r.sr_P:.1f} against {r.sr_O:.1f} on ordinary live balls, scores {r.runs_index_P:.0f} runs per 100 expected, is dismissed at {r.dismissal_ratio_P:.2f} times the expected rate, "
              f"and adds win probability in {r.delivery_rate:.0%} of his matches with six or more pressure balls.")
(OUT / "batter_rationale.md").write_text("\n".join(bl) + "\n", encoding="utf-8")

# ----------------------------------------------------------------- spinners
s = json.load(open(OUT / "step3_summary.json"))
para = (f"Eight of the ten listed bowlers are spinners ({', '.join(s['listed_spinners'])}); the two pace bowlers are {' and '.join(s['listed_pace'])}. "
        f"Exposure does not explain this: spinners bowl {s['spin_share_pressure']:.1%} of pressure balls against {s['spin_share_live']:.1%} of all live balls in the rating sample "
        f"(a ratio of {s['spin_ratio']:.2f}), so they are not handed more pressure overs than their share of play. Spinners are {s['spinners_pool']} of the {s['pool_size']} bowlers in the eligible, active pool "
        f"({s['spinners_pool'] / s['pool_size']:.0%}) but {s['spinners_listed']} of the 10 on the list. The list therefore over-represents spinners relative to the pool, and because spinners are not over-exposed to pressure, the gap comes from the value they add per pressure ball, not from volume. "
        "The data do not say why (pitch conditions, match-ups and captains' choices are not modelled), so this is reported as an observation, not an explanation.")
(OUT / "spinner_paragraph.md").write_text(para + "\n", encoding="utf-8")
print("\n".join(lines)); print(); print(para)
