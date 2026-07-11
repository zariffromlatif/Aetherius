# Honest code audit — Aetherius as of 2026-07-11

Written by a skeptical technical auditor after reading the pivot memo, landing page, and the actual services / templates / backtest fixture.

## 1. What the code can do end-to-end today

There is a working pipeline:

- `edgar_adapter.ingest_filings_for_ticker` pulls SEC filings for a ticker via the public EDGAR JSON API (`aetherius/app/services/ingestion/edgar_adapter.py:104`)
- `ingestion/service.ingest_observation` writes `SourceObservations` rows with dedupe + freshness
- `entity_mapping/service.map_to_watchlist` scores matches with a conservative word-boundary regex and a real acronym stoplist
- `signals/service.create_signal_from_evidence` produces a `RiskSignals` row
- `delivery/service.deliver_briefing` renders Jinja HTML/PDF, runs banned-language + disclaimer + evidence-ref gates, and SMTPs it

But the "brief" template `aetherius/app/templates/pdf/daily_brief.html` is 20 lines: header, `for item in items` loop with title + body, and a disclaimer. **The 8–15 page "Target Stress-Test Deck" the landing page promises does not exist in code.** No cover, thesis, counterparty graph, scenario table, downside PnL, or appendix template. Reporting today is `reporting/service.build_pilot_report`, which returns four integers (`sent_daily_briefs`, `open_signals`, `feedback_entries`). The deck is entirely aspirational.

## 2. SVB backtest credibility

`simulations/backtest/events/svb-2023/observations.jsonl` has **10 lines**, one of which is a benign MSFT control. The remaining 9 are hand-authored "curated public-record summaries" (their own `provenance` field literally says so) — not scraped from an archive. `ground_truth.json` names exactly the tickers the observations discuss (SIVB, SBNY, FRC, WAL, PACW).

This is a hindsight-curated demonstration, not a backtest. A PE MD or activist quant will spot the 10-row corpus and the "curated summary" provenance in five minutes and dismiss it as a rigged demo.

`run_backtest.py` itself is a legitimate replay harness (uses the production `match_item` + scoring functions) — the corpus it replays is the problem, not the harness.

## 3. Shortest path to a shippable first paid deck

**Reusable as-is:** `edgar_adapter.py`, `ingestion/service.py`, `entity_mapping/service.py` (word-boundary matcher + stoplist), `scoring/service.py`, `delivery/service.py` gates.

**Must be written:**
- A real deck template replacing `templates/pdf/daily_brief.html` — cover, thesis, evidence appendix, invalidation markers, disclaimer
- A manual "target dossier" builder that takes a ticker + timeframe and produces the deck from queried `SourceObservations`
- At minimum one primary-news adapter, since EDGAR-only produces filings, not the narrative flow the deck needs

## 4. Single biggest technical risk

**Ingestion coverage.** EDGAR is the only real adapter; everything narrative (news, ratings actions, deposit-flight reporting) is absent. The SVB backtest looks strong precisely because those observations were hand-written. On live targets there is no source of them. Without at least one news / ratings-action adapter, the pipeline cannot recreate on a real target what it "detected" in the demo — meaning the second paid engagement, on a target the founder hasn't hand-curated, will either underperform or require days of manual assembly (killing margins).

Secondary risks: entity-mapping precision on real messy news text (the SVB fixture uses clean tickers in every sentence), and the fact that `core/causal_brain.py` still ships hardcoded Discord/AWS scaffolding that any Apache-2.0 repo reader will find in five minutes.
