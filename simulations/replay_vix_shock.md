# Replay: Volatility Spike (VIX Shock)

## Executive Summary
- A volatility shock scenario was replayed to test contagion propagation across the graph.
- Aetherius surfaced elevated urgency for names with weak pricing power and financing sensitivity.
- The response pipeline generated structured A-E output and review-ready actions.

## Event Context
- **Case ID:** `replay-2026-02-vix-shock`
- **Window Covered (UTC):** 2026-02-03 10:00 to 2026-02-03 16:00
- **Primary Scope:** Multi-sector downside watchlist
- **Shock Type:** Volatility/liquidity stress proxy

## Replay Flow
1. Ingest volatility and spread-stress context.
2. Build graph state with macro and sector-level transmission edges.
3. Apply adversarial shock and simulate transition outcomes.
4. Evaluate threshold crossings and create risk decision output.

## Preliminary Findings
- Bear pathway indicated broader spread-pressure transmission than base case.
- Invalidation markers highlighted the need for rapid spread normalization signals.
- Output remained operator-supervised in pilot-safe mode.

## Limitations
- Replay uses current scaffolding and should be treated as a methodology proof.
- Full quality claims require benchmarked live/replay datasets per `docs/benchmark_spec.md`.
