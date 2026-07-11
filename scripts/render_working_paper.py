"""Render the detection-timing backtest working paper to a self-contained HTML.

Reads:  docs/working_paper/detection_timing_backtest_2026-07.md
Writes: docs/working_paper/detection_timing_backtest_2026-07.html

The HTML uses inline CSS and no external dependencies so it can be:
  * opened directly in a browser
  * printed to PDF via the browser (Ctrl+P -> Save as PDF)
  * emailed / attached to outreach
  * copy-pasted into Substack (which already renders the Markdown)

No WeasyPrint dependency required (WeasyPrint on Windows needs GTK bundles
that solo/non-US environments won't have pre-installed).
"""
from __future__ import annotations

from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parents[1]
IN_PATH = REPO_ROOT / "docs" / "working_paper" / "detection_timing_backtest_2026-07.md"
OUT_PATH = REPO_ROOT / "docs" / "working_paper" / "detection_timing_backtest_2026-07.html"

CSS = """
:root { color-scheme: light dark; }
body {
    font-family: 'Georgia', 'Times New Roman', serif;
    max-width: 780px;
    margin: 2.5rem auto;
    padding: 0 1.25rem;
    line-height: 1.6;
    color: #1a1a1a;
    background: #fdfdfb;
}
h1 { font-size: 2.05rem; margin-top: 0; line-height: 1.25; }
h2 { font-size: 1.5rem; margin-top: 2.25rem; border-bottom: 1px solid #d8d3c8; padding-bottom: 0.35rem; }
h3 { font-size: 1.15rem; margin-top: 1.5rem; }
p, li { font-size: 1.02rem; }
code { font-family: 'Consolas', 'Menlo', monospace; font-size: 0.92em; background: #eee7d6; padding: 0.1rem 0.3rem; border-radius: 3px; }
pre { background: #1c1c1c; color: #f3ecdc; padding: 1rem; border-radius: 5px; overflow-x: auto; font-size: 0.9rem; }
pre code { background: none; color: inherit; padding: 0; }
table { border-collapse: collapse; margin: 1rem 0; width: 100%; font-size: 0.95rem; }
th, td { border: 1px solid #ccc4b0; padding: 0.4rem 0.65rem; text-align: left; vertical-align: top; }
th { background: #efe7d0; font-weight: 600; }
blockquote { border-left: 3px solid #b8893a; padding: 0.2rem 1rem; margin: 1rem 0; color: #4a4030; background: #f5efdd; }
hr { border: 0; border-top: 1px solid #d8d3c8; margin: 2rem 0; }
em { color: #4a4030; }
strong { color: #14161e; }
a { color: #b8893a; text-decoration: none; border-bottom: 1px solid #d5b976; }
a:hover { color: #14161e; }
@media print {
    body { background: #fff; margin: 1rem; max-width: none; }
    pre { border: 1px solid #ccc; }
}
"""


def render() -> Path:
    md_text = IN_PATH.read_text(encoding="utf-8")
    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc"],
    )
    html = (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<title>Detection-Timing Backtest of a Systematic Downside-Risk Screen Across Three Modern Financial Crises</title>\n"
        f"<style>{CSS}</style>\n"
        "</head>\n<body>\n"
        f"{body_html}\n"
        "</body>\n</html>\n"
    )
    OUT_PATH.write_text(html, encoding="utf-8")
    return OUT_PATH


if __name__ == "__main__":
    out = render()
    print(f"Rendered -> {out}")
