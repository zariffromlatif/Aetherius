# Aetherius

**A production-ready watchlist risk intelligence platform with an emerging causal world-model research core.**

![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![Status: Pilot Ready](https://img.shields.io/badge/Status-Pilot%20Ready-success)
![Model: Open Core](https://img.shields.io/badge/Model-Open%20Core-informational)

Aetherius combines a pilot-ready risk operations backend with a top-level causal simulation stack:

- **Sensory Core** (`core/sensory_forager.py`) for high-entropy market context foraging
- **Causal Brain** (`core/causal_brain.py`) for state construction and shock simulation
- **Response Engine** (`core/response_engine.py`) for strict A-E Risk Decision Logs
- **Master Orchestrator** (`orchestrator.py`) for resilient 24/7 async operation

## Who This Is For

- Small hedge funds and family offices running concentrated watchlists
- Operators who need evidence-backed downside surveillance, not generic AI commentary
- Teams that want human-supervised delivery with clear auditability

## What Aetherius Is (and Is Not)

- **Is:** an event-driven risk surveillance and decision-support workflow
- **Is:** an open-core system with reproducible replay and validation evidence
- **Is not:** autonomous investment execution or guaranteed return forecasting
- **Is not:** investment advice

## Why It Is Different

- Causal shock simulation over a graph-enhanced state (`S_t -> S_{t+1}`)
- Structured A-E Risk Decision Logs with explicit invalidation markers
- Built-in prompt-cache economics and token telemetry for cost control
- Operator review gates before client-visible outputs

## Core Framing

```text
S_{t+1} ~ T(S_t, A_t, w)
```

Where `S_t` is the current graph-enhanced market state, `A_t` is a causal shock, and `w` captures latent uncertainty.

## Repository Highlights

```text
/core
  sensory_forager.py
  causal_brain.py
  response_engine.py
  optimizer.py

/simulations
  run_replay.py
  replay_rate_hike_2026.md
  replay_vix_shock.md
  sample_risk_decision_log.md

/docs
  mathematical_foundations.md
  benchmark_spec.md
  deployment_guide.md
```

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run a replay:

```bash
python simulations/run_replay.py --shock-id shock-rate-50
```

3. Run orchestrator loop:

```bash
python orchestrator.py
```

## Proof and Validation

- Replay runner: `simulations/run_replay.py`
- Validation runbook: `docs/completion_validation_runbook.md`
- Benchmark protocol: `docs/benchmark_spec.md`
- Evidence packs: `simulations/validation/`

## Prompt Cache and Telemetry

- 24h prompt-cache store is persisted to `.aetherius_prompt_cache.json`.
- Each shock result logs:
  - `cache_hit`
  - `cache_key`
  - `token_spend_estimate`
- `aetherius_system.log` captures run-level cache-hit ratios and token-spend estimates.

## TTC Provider Integration

The causal brain supports OpenAI-compatible test-time compute calls on cache misses.

Environment variables:

- `AETHERIUS_ENABLE_TTC=true|false` (default: true)
- `AETHERIUS_MODEL_NAME=<model>` (default: `gpt-4o-mini`)
- `AETHERIUS_API_KEY=<provider_api_key>`
- `AETHERIUS_API_BASE_URL=<openai_compatible_base_url>` (default: `https://api.openai.com/v1`)
- `AETHERIUS_API_TIMEOUT_SECONDS=45`

If provider calls fail or keys are missing, Aetherius safely falls back to deterministic local simulation.

## Supporting Backend

The existing modular monolith backend remains under `aetherius/` (API, DB models, delivery, review workflows) and is used to enrich core graph state with watchlist/evidence context.

## Repository Ownership Map

This repository intentionally has two implementation layers:

- **Research and simulation layer (root):** `core/`, `orchestrator.py`, and `simulations/`
  - Purpose: causal state-transition experimentation, replay proofs, and cost/cache telemetry.
- **Operational delivery layer (`aetherius/`):**
  - Purpose: API, data model, review console, queues, rendering, and delivery workflows for pilot operation.

Contributor rule of thumb:
- If the change affects shock simulation, pathways, or replay outputs, start in root `core/` and `simulations/`.
- If the change affects auth, watchlists, review actions, or client-facing delivery, start in `aetherius/app/`.

## Documentation

- `docs/mathematical_foundations.md`
- `docs/benchmark_spec.md`
- `docs/README_replay_case_studies.md`
- `docs/deployment_guide.md`

## Repository Hygiene Policy

To keep Aetherius showcase-ready:

- Treat generated runtime outputs as ephemeral (`simulations/artifacts/`, `.aetherius_prompt_cache.json`, logs).
- Keep only canonical implementations (for example, `core/` modules) and remove legacy duplicate scripts.
- Move internal planning/business drafts to a private workspace or `archive/` branch instead of main.
- Keep root-level docs focused on reproducible technical evidence and deployment clarity.
- Keep `aetherius/README.md` as backend-scope documentation; keep root `README.md` as the canonical project entry point.

## License and Commercial Offering

Aetherius is licensed under the Apache License 2.0 (`LICENSE`).

Open-source scope:
- Core simulation and replay framework
- Research and benchmark documentation
- Community contribution workflow

Commercial/managed scope:
- Managed pilot operations and support
- Customer-specific onboarding and workflows
- Private deployment, monitoring, and SLA process layers

This open-core model is designed to keep the technical foundation transparent while allowing a managed pilot service for production users.

## Disclaimer

Aetherius is a decision-support workflow and research framework. It does not guarantee investment outcomes or performance.
