# Simulations

This folder contains the historical detection-timing backtests that anchor Aetherius' credibility.

## Contents

- `backtest/` — the honest asset: pinned historical events with real observations, ground truth, and a replay harness that uses the production entity-mapping and scoring code.
- `validation/` — completion-signoff evidence for individual events.
- `artifacts/` — generated outputs (git-ignored).

## Running a backtest

From repo root:

```bash
python simulations/backtest/run_backtest.py --event svb-2023
```

Each event directory (`simulations/backtest/events/<event-id>/`) contains:

- `watchlist.json` — the concentrated book being surveilled, plus at least one non-affected control name for false-positive testing
- `ground_truth.json` — the realized event date(s) and expected severity per ticker
- `observations.jsonl` — real primary-source observations from GDELT, SEC EDGAR, Wayback, or other archives (never hand-authored)

The harness scores each observation with the production `entity_mapping/service.py` + `scoring/service.py`, and reports:

- detection recall (fraction of affected names flagged elevated / high before the realized event)
- median lead time (hours between first flag and realized event)
- false positives on the control name
- per-ticker detection detail

See the SVB-2023 fixture for the reference format.

## Anti-hype note

These are early-detection and prioritization proofs on frozen historical windows. Not return forecasts. Not guarantees of future results. Causal-mechanism confidence is not claimed.
