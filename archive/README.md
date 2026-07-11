# Archive — deprecated as of 2026-07-11

Files in this directory are retained for historical reference only. They are **not** part of the shipped Aetherius product.

## Why archived

Aetherius was originally positioned as an open-core "causal simulation" platform. That framing was falsified by these files themselves:

- `core/causal_brain.py` — hardcoded 5-node Discord/AWS graph and a 3-shock library
- `core/response_engine.py` — 3 hardcoded action strings
- `orchestrator.py` — a resilient async loop with nothing meaningful to loop over
- `sensory_core.py` — a Hacker News scraper with no risk-relevant output
- `run_replay.py` and the `replay_*.md` files — LLM-narrated shock simulations against the hardcoded graph, unrelated to the honest backtest evidence
- `completion_validation_runbook.md`, `deployment_guide.md` — operational docs for the deprecated 24/7 orchestrator loop

## What replaced them

The commercial product now centers on **per-target Stress-Test Decks** built from the honest asset:

- Real SEC EDGAR ingestion (`aetherius/app/services/ingestion/edgar_adapter.py`)
- Conservative entity mapping (`aetherius/app/services/entity_mapping/service.py`)
- Deterministic 7-factor risk scoring (`aetherius/app/services/scoring/service.py`)
- Historical detection-timing backtests (`simulations/backtest/`)
- Human-supervised delivery with disclaimer/banned-language gates (`aetherius/app/services/delivery/service.py`)

See the root `README.md` for the current scope.

## Retention policy

Kept in `archive/` so external readers who cloned older commits can find the deprecated code without git spelunking. Do not import from `archive/` in shipping code. New work does not go here.
