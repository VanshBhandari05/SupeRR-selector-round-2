"""Export report.md to report.pdf with the figures embedded (markdown -> HTML -> headless Edge/Chrome print).
Run: python -I src/export_pdf.py     (skipped with a message if no Chromium-based browser is found)
"""
import base64
import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
md = (ROOT / "report.md").read_text(encoding="utf-8")


def embed(m):
    alt, rel = m.group(1), m.group(2)
    data = base64.b64encode((ROOT / rel).read_bytes()).decode()
    return f'<img alt="{alt}" src="data:image/png;base64,{data}"/>'


html_body = markdown.markdown(re.sub(r"!\[(.*?)\]\((figures/.*?\.png)\)", embed, md), extensions=["tables", "sane_lists"])
css = """
@page { size: A4; margin: 14mm 13mm 14mm 13mm; }
body { font-family: 'Segoe UI', Calibri, Arial, sans-serif; font-size: 9.3pt; line-height: 1.38; color: #1c1c1c; }
h1 { font-size: 22pt; margin: 0 0 2pt 0; color: #0b2a4a; }
h3 { font-size: 11pt; color: #55657a; margin: 0 0 8pt 0; font-weight: 500; }
h2 { font-size: 13.5pt; color: #0b2a4a; border-bottom: 1.5px solid #cfd8e3; padding-bottom: 2pt; margin: 14pt 0 6pt 0; break-after: avoid; }
p, li { margin: 3pt 0; }
blockquote { margin: 6pt 0; padding: 6pt 10pt; background: #eef4fb; border-left: 4px solid #2a6fbb; font-size: 10pt; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0 7pt 0; font-size: 7.8pt; break-inside: avoid; }
th { background: #eef2f7; text-align: left; padding: 2.5pt 4pt; border: 1px solid #d5dde8; }
td { padding: 2pt 4pt; border: 1px solid #e1e7ef; }
tr:nth-child(even) td { background: #fafbfd; }
img { max-width: 100%; max-height: 118mm; display: block; margin: 5pt auto 1pt auto; break-inside: avoid; }
em { color: #44546a; }
code { font-family: Consolas, monospace; font-size: 8.2pt; background: #f2f4f7; padding: 0 2pt; }
ul { padding-left: 16pt; }
"""
html = f"<!doctype html><html><head><meta charset='utf-8'><title>Who delivers when it matters</title><style>{css}</style></head><body>{html_body}</body></html>"
(ROOT / "report.html").write_text(html, encoding="utf-8")

browser = next((p for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") if Path(p).exists()), None)
if browser is None:
    print("No Chromium-based browser found; report.html written, PDF skipped."); sys.exit(0)
pdf = ROOT / "report.pdf"
if pdf.exists(): pdf.unlink()
subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={pdf}", (ROOT / "report.html").as_uri()], check=True, timeout=240, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
from pypdf import PdfReader
print("report.pdf written:", len(PdfReader(str(pdf)).pages), "pages,", round(pdf.stat().st_size / 1e6, 2), "MB")
