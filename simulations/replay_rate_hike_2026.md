# Replay: Unexpected Rate Hike 2026

## Executive Summary
- A 50 bps policy shock was replayed against the current synthetic graph state.
- Aetherius produced elevated risk on margin-sensitive consumer SaaS pathways.
- The run generated an A-E Risk Decision Log and flagged same-day review actions.
- Threshold trigger occurred in under one simulated cycle with reproducible artifacts.

## Event Context
- **Case ID:** `replay-2026-01-rate-hike`
- **Window Covered (UTC):** 2026-01-14 08:00 to 2026-01-14 14:00
- **Primary Scope:** US growth/consumer SaaS watchlist
- **Shock:** `Unexpected Rate Hike` (`+0.50`)

## What Aetherius Did
1. Foraged macro/rates context.
2. Constructed graph state $S_t$ with rates, input costs, and downstream margin nodes.
3. Applied intervention $do(A_t)$ with a +50 bps rate shock.
4. Simulated Base/Bear/Bull pathways and evaluated threshold $\tau$.
5. Emitted risk log with review actions and invalidation markers.

## Key Outputs
- **Risk score (shock):** 0.65 (example scaffold value may change with live model integration)
- **Urgency score (shock):** 0.65
- **Decision output:** Risk Decision Log generated and queued for operator review.

## Limitations
- This replay currently runs on deterministic scaffolding before full Crawl4AI + model integration.
- Margin pathway estimates are directional placeholders and must be calibrated with benchmark data.

## Next Iteration
- Replace synthetic forager content with live Crawl4AI extraction.
- Add calibrated transition model and benchmarked confidence bands.
