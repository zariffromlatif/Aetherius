# Aetherius Risk Intelligence

**Backtest-validated downside-risk screens for concentrated public-equity books.**

![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![Backtests: 3 events, 9/9 recall](https://img.shields.io/badge/Backtests-3%20events%20%C2%B7%209%2F9%20recall-informational)

Aetherius produces per-target Stress-Test Decks: 8–15 page PDFs that map a public-equity target's counterparties and funding sources, timeline the 90 days of filings and news scored by severity, and disclose the pipeline's historical detection track record on structurally comparable names.

Positioning: *"Backtest-validated downside-risk screens. Detection timing disclosed on the cover page, not asserted in marketing."*

## Who it is for

- Search funds and independent sponsors doing pre-LOI diligence on public comps
- Small and mid family offices ($100M–$1B AUM) running concentrated books
- Litigation-finance analysts and small credit funds
- Single-name activist funds and concentrated PMs
- Asset-based lenders assessing borrower counterparty risk

## What Aetherius Is (and Is Not)

- **Is:** an evidence-backed risk screening and reporting workflow
- **Is:** a historical detection-timing pipeline with pinned backtests
- **Is not:** autonomous investment execution or a return forecast
- **Is not:** investment advice

## The pipeline

```text
aetherius/app/services/
  ingestion/
    edgar_adapter.py      # SEC EDGAR filings (8-K, 10-Q, 10-K, ...)
    gdelt_adapter.py      # Real news headlines via GDELT DOC 2.0
  entity_mapping/          # Word-boundary regex + acronym stoplist
  scoring/                 # Deterministic 7-factor risk formula
  signals/                 # 15-type downside signal taxonomy
  reporting/               # Deck data assembly
  delivery/                # PDF render + disclaimer & banned-language gates
  review/                  # Human review gate before client delivery

simulations/backtest/      # Historical detection-timing proofs
  events/svb-2023/         # Frozen fixture: SVB regional-bank contagion
  run_backtest.py          # Replay harness (uses production match + scoring)
```

## Quick start

```bash
pip install -r requirements.txt
pytest aetherius/tests
```

To run the SVB-2023 backtest:

```bash
python simulations/backtest/run_backtest.py --event svb-2023
```

To build a Target Stress-Test Deck for a ticker (fixture mode, fully offline):

```bash
python scripts/build_deck.py \
  --ticker SIVB --name "SVB Financial Group" \
  --sector "Regional Banks" --aliases "Silicon Valley Bank,SVB" \
  --thesis "Concentrated regional-bank position with rate-sensitive HTM book." \
  --counterparty "FRC:First Republic Bank:peer:0.6:First Republic" \
  --window 2023-03-06:2023-03-12 \
  --fixture-jsonl simulations/backtest/events/svb-2023/observations.jsonl \
  --out sivb-deck.html
```

Open the resulting HTML in a browser and use **File → Print → Save as PDF** to produce the deliverable PDF. For a live pull against GDELT for a real target, replace `--fixture-jsonl PATH` with `--live`.

## Detection track record

The pipeline's honest metrics are disclosed on every engagement. Three frozen historical events, each replayed against real primary-source news from the GDELT archive:

| Event | Watchlist | Recall | Median lead | False positives on control |
|---|---|---|---|---|
| **SVB-2023** — regional-bank contagion (Mar 6–12) | 5 affected + 1 control (MSFT) | **5 / 5 (100%)** | **2.34 days** | **0** |
| **Wirecard-2020** — accounting fraud + insolvency (Jun 15–30) | 1 affected + 1 control (DTE) | **1 / 1 (100%)** | **6.60 days** | **0** |
| **FTX-2022** — crypto counterparty contagion (Nov 2–14) | 3 affected + 1 control (MSFT) | **3 / 3 (100%)** | **7.12 days** | **0** |

Full methodology, watchlists, ground-truth files, GDELT observation corpora, and pinned tests are published in `simulations/backtest/events/` and `aetherius/tests/test_backtest_harness.py`.

The full write-up is in `docs/working_paper/detection_timing_backtest_2026-07.md`.

**Anti-hype note.** Detection-timing evidence on frozen historical windows. Not a return forecast. Not a guarantee of future results.

## Engagements

Per-target Stress-Test Decks are priced per engagement. See the landing page at `landing_page/index.html` or email `zarif@aetheriusresearch.tech`.

## Repository policy

- Root `README.md` is the canonical project entry point.
- `aetherius/README.md` covers backend implementation details.
- Generated runtime outputs (`simulations/artifacts/`, logs) are ephemeral.

## License

Apache License 2.0. See `LICENSE`.

## Disclaimer

Aetherius Risk Intelligence provides research and risk-monitoring services. Analysis is not investment advice and is not a recommendation to buy, sell, or hold any security. Nothing herein is a forecast or a guarantee of any outcome.
