# Working Paper

**Detection-Timing Backtest of a Systematic Downside-Risk Screen Across Three Modern Financial Crises**
Aetherius Risk Intelligence — July 2026

## Files

- `detection_timing_backtest_2026-07.md` — the paper. Renders on GitHub, Substack, arXiv-style preprint sites. **This is the primary artifact.**
- `detection_timing_backtest_2026-07.html` — self-contained HTML. Open in any browser. Save-as-PDF via browser print dialog for a shareable attachment.

## Rebuild the HTML

```bash
python scripts/render_working_paper.py
```

The HTML has all CSS inlined and no external assets, so a single file emailed / posted anywhere renders correctly on any modern browser.

## Reproduce the results

The paper's numbers come from three pinned fixtures at `simulations/backtest/events/`:

```bash
# Reproduce all three events (offline, uses the committed observations.jsonl).
pytest aetherius/tests/test_backtest_harness.py -v

# Or per-event:
python simulations/backtest/run_backtest.py --event svb-2023
python simulations/backtest/run_backtest.py --event wirecard-2020
python simulations/backtest/run_backtest.py --event ftx-2022
```

To rebuild an event's observations corpus from live GDELT DOC 2.0:

```bash
python simulations/backtest/build_fixture.py --event svb-2023
```

Per-target GDELT responses are cached under `simulations/backtest/events/<event-id>/_gdelt_cache/` (git-ignored) so partial failures resume without re-fetching.

## Intended distribution channels

- **Substack post** — paste the Markdown; embed the results tables inline.
- **GitHub Pages / repo README** — the Markdown renders natively.
- **PDF attachment** — open the HTML in a browser, print to PDF.
- **arXiv q-fin preprint** — the paper is written in the working-paper style expected by q-fin.CP / q-fin.RM.
- **Cold outbound email** — link to the GitHub-rendered Markdown, attach the HTML.

The paper is the credibility asset that unlocks the outbound sales channels.
