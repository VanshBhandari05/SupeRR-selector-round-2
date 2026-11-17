"""Automated checks for the handoff pack. Standard library only.

Run from anywhere:  python -I PPT_and_Document_Preparation/check_handoff.py
Checks: (a) required files exist, (b) the top-10 lists in 01_RANKINGS.md, 12_UNSTOP_ENTRIES.md, top10_*.csv (pack and pipeline),
submission_sheet.csv and the website's top10_*.json are identical in order and player_id, (c) every number in 10_NUMBERS_FOR_DECK.json
traces to its source file, (d) no raw organiser file is inside the pack, (e) total size under 15 MB, plus hash checks against FINAL_LOCK.md.
Exit code 0 only if every check passes.
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent
ROOT = PACK.parent
RESULTS = []


def rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("PASS  " if ok else "FAIL  ") + name + (" | " + detail if detail else ""))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


REQUIRED = ["00_DEVIATIONS.md", "01_RANKINGS.md", "02_METHOD_AS_RUN.md", "03_EVIDENCE_DEFINITION.md", "04_EVIDENCE_RELIABILITY.md", "05_PLAYER_CARDS.md", "player_cards.csv",
            "06_FAIRNESS_AND_ADJUSTMENT.md", "player_ratings.csv", "players_unfiltered.csv", "07_LIMITATIONS_OBSERVED.md", "08_FIGURES", "08_FIGURE_INDEX.md", "09_WEBSITE.md",
            "10_NUMBERS_FOR_DECK.json", "10_NUMBERS_FOR_DECK.md", "11_STORY_BEATS.md", "12_UNSTOP_ENTRIES.md", "config.yaml", "sensitivity.csv", "top10_batters.csv", "top10_bowlers.csv",
            "03_trace_series.csv", "03_trace_summary.csv", "check_handoff.py"]
ALLOWED_EXT = {".md", ".csv", ".json", ".png", ".svg", ".yaml", ".py"}   # .yaml = config.yaml copy; .py = this script (both requested)
ORGANISER = ["ball_by_ball.csv", "matches.csv", "playing_eleven.csv", "competition_team_player_mapping.csv", "competitions.csv", "teams.csv"]


def md_section_ids(path, heading):
    """player_id column of the first pipe table under '## heading'."""
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r"^## ", rest, re.M)
    block = rest[: n.start()] if n else rest
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in block.splitlines() if l.strip().startswith("|")]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    if not rows:
        return None
    col = rows[0].index("player_id")
    return [int(r[col]) for r in rows[1:]]


def csv_ids(path):
    with open(path, encoding="utf-8", newline="") as f:
        return [int(r["player_id"]) for r in csv.DictReader(f)]


def main():
    # (a) required files
    missing = [r for r in REQUIRED if not (PACK / r).exists()]
    rec("(a) all required files exist", not missing, f"{len(REQUIRED)} required; missing: {missing}" if missing else f"{len(REQUIRED)} required items present")
    figs = sorted(p.name for p in (PACK / "08_FIGURES").glob("*")) if (PACK / "08_FIGURES").exists() else []
    rec("(a) 08_FIGURES has PNG and SVG files", sum(f.endswith(".png") for f in figs) >= 10 and sum(f.endswith(".svg") for f in figs) >= 9, f"{sum(f.endswith('.png') for f in figs)} png, {sum(f.endswith('.svg') for f in figs)} svg")
    try:
        from struct import unpack
        narrow = []
        for f in figs:
            if f.endswith(".png"):
                with open(PACK / "08_FIGURES" / f, "rb") as fh:
                    head = fh.read(24)
                w = unpack(">I", head[16:20])[0]
                if w < 1600:
                    narrow.append((f, w))
        rec("(a) PNG width >= 1600 px (informational; originals may be narrower)", not narrow, f"below 1600: {narrow}" if narrow else "all PNG >= 1600 px")
    except Exception as e:
        rec("(a) PNG width check", False, repr(e))

    # (b) top-10 identity everywhere
    for role in ("batters", "bowlers"):
        ref = csv_ids(ROOT / "outputs" / f"top10_{role}.csv")
        srcs = {
            "pack top10 csv": csv_ids(PACK / f"top10_{role}.csv"),
            "01_RANKINGS.md": md_section_ids(PACK / "01_RANKINGS.md", f"Top 10 {role}"),
            "12_UNSTOP_ENTRIES.md": md_section_ids(PACK / "12_UNSTOP_ENTRIES.md", f"Top 10 {role}"),
            "website top10 json": [d["id"] for d in json.load(open(ROOT / "website" / "data" / f"top10_{role}.json", encoding="utf-8"))["list"]],
        }
        with open(ROOT / "submission_sheet.csv", encoding="utf-8", newline="") as f:
            srcs["submission_sheet.csv"] = [int(r["player_id"]) for r in csv.DictReader(f) if r["list"] == role[:-1]]
        bad = {k: v for k, v in srcs.items() if v != ref}
        rec(f"(b) top-10 {role}: identical in order and player_id across {len(srcs) + 1} sources", not bad and len(ref) == 10, f"reference outputs/top10_{role}.csv = {ref}" + (f"; MISMATCH: {bad}" if bad else ""))

    # hashes against FINAL_LOCK.md
    lock = (ROOT / "FINAL_LOCK.md").read_text(encoding="utf-8")
    for rel, p in (("config.yaml", PACK / "config.yaml"), ("outputs/top10_batters.csv", PACK / "top10_batters.csv"), ("outputs/top10_bowlers.csv", PACK / "top10_bowlers.csv")):
        m = re.search(rf"\| {re.escape(rel)} \| `([0-9a-f]{{64}})` \|", lock)
        rec(f"(b) pack copy of {Path(rel).name} has the FINAL_LOCK.md SHA-256", bool(m) and sha(p) == m.group(1), (m.group(1)[:12] + "...") if m else "hash not found in FINAL_LOCK.md")

    # (c) deck numbers trace to sources
    nums = json.load(open(PACK / "10_NUMBERS_FOR_DECK.json", encoding="utf-8"))
    bad = []
    for n in nums:
        src = ROOT / n["source_file"]
        if not src.exists():
            bad.append((n["label"], "source file missing"))
            continue
        if n.get("derived"):
            r = n["recompute"]
            with open(ROOT / r["csv"], encoding="utf-8", newline="") as f:
                vals = [float(x[r["col"]]) for x in csv.DictReader(f)]
            got = sum(v == r["arg"] for v in vals) if r["op"] == "count_eq" else sum(v >= r["arg"] for v in vals)
            if got != n["value"]:
                bad.append((n["label"], f"recomputed {got} != {n['value']}"))
            continue
        text = src.read_text(encoding="utf-8")
        if n["source_text"] not in text:
            bad.append((n["label"], "source_text not found in file"))
            continue
        found = [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*\.?\d*", n["source_text"])]
        if not any(abs(f - float(n["value"])) < 1e-12 * max(1.0, abs(f)) for f in found):
            bad.append((n["label"], f"value {n['value']} not in its source_text"))
    rec("(c) every number in 10_NUMBERS_FOR_DECK.json traces to its source file", not bad and len(nums) >= 40, f"{len(nums)} numbers checked" + (f"; PROBLEMS: {bad}" if bad else ""))
    need = ["label", "value", "unit", "source_file", "source_location"]
    rec("(c) every deck number has label, value, unit, source_file, source_location", all(all(k in n and n[k] not in (None, "") for k in need) for n in nums))

    # (d) no raw organiser files
    pack_files = [p for p in PACK.rglob("*") if p.is_file()]
    forbidden = [p.name for p in pack_files if p.name in ORGANISER or p.suffix.lower() in (".parquet", ".pkl", ".ipynb", ".npz")]
    org_hashes = {sha(ROOT / o): o for o in ORGANISER if (ROOT / o).exists()}
    same = [p.name for p in pack_files if sha(p) in org_hashes]
    ballish = []
    for p in pack_files:
        if p.suffix.lower() == ".csv":
            head = p.open(encoding="utf-8", errors="replace").readline()
            if "striker_id" in head and "innings_ball_num" in head or head.startswith("match_id,innings,innings_ball_num,innings,"):
                ballish.append(p.name)
    rec("(d) no raw organiser file in the pack (by name, by hash, by ball-level header)", not (forbidden or same or ballish), f"forbidden={forbidden} identical-to-organiser={same} ball-level-header={ballish}")
    badext = sorted({p.suffix.lower() for p in pack_files} - ALLOWED_EXT)
    rec("(d) only plain files (.md .csv .json .png .svg, plus config.yaml and this script)", not badext, f"unexpected extensions: {badext}" if badext else "ok")

    # (e) size
    total = sum(p.stat().st_size for p in pack_files)
    rec("(e) total size under 15 MB", total < 15 * 1024 * 1024, f"{total / 1024 / 1024:.2f} MB across {len(pack_files)} files")

    ok = all(r[1] for r in RESULTS)
    print(f"\nRESULT: {sum(r[1] for r in RESULTS)} of {len(RESULTS)} checks passed" + ("" if ok else "  <-- FAILURES ABOVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
