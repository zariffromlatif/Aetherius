# Replay: Credit Spread Blowout

## Case Header
- **Case ID:** `replay-2026-03-credit-spread-blowout`
- **Window Covered (UTC):** 2026-03-11 08:00 to 2026-03-11 18:00
- **Primary Watchlist Scope:** Rate-sensitive software and refinancing-dependent growth names
- **Shock Applied:** `shock-liquidity` (credit spread widening + liquidity squeeze proxy)
- **Replay Method:** `python simulations/run_replay.py --shock-id shock-liquidity --model-name gpt-4o-mini`

## Executive Summary
- Aetherius ingested macro + rates context and built the graph state with stress propagation edges.
- The liquidity shock replay produced elevated urgency and downside pathway concentration in financing-sensitive names.
- The generated Risk Decision Log passed A-E structure checks and included measurable invalidation markers.
- Replay output quality was deterministic and reproducible with a saved metrics artifact.

## Event Context and Hypothesis
### Background
In spread-widening episodes, refinancing-dependent names often re-rate before fundamentals confirm stress in reported earnings.

### Replay Hypothesis
If funding stress is forced as an intervention, Aetherius should surface second-order margin pressure pathways before broad consensus narrative catches up.

## Timeline Replay
| Time (UTC) | Pipeline Stage | Artifact | Notes |
|------------|----------------|----------|-------|
| 08:00 | Foraging | `forage_result` | Rates and macro context ingested |
| 08:03 | State Build | `state_id` | Graph created with macro/factor/sector nodes |
| 08:04 | Shock Simulation | `shock-liquidity` | Base/Bear/Bull pathways generated |
| 08:05 | Response Engine | risk log markdown | A-E sections generated |
| 08:06 | Metrics Export | `*.metrics.json` | Telemetry and quality flags persisted |

## Core Results
| Metric | Value | Notes |
|--------|-------|-------|
| `pathway_count` | 3 | Base/Bear/Bull present |
| `has_ae_sections` | true | Output formatting gate passed |
| `has_invalidation_markers` | true | Measurable invalidation present |
| `provider_total_tokens` | See run artifact | Non-zero when TTC path succeeds |
| `cache_hit` | Context-dependent | false on fresh run, true on repeat |

## Decision Log Quality (A-E)
- **A. What Changed:** Funding conditions worsened under simulated liquidity stress.
- **B. Why It Matters:** Direct financing pressure + second-order margin drag via cost of capital.
- **C. What Happens Next:** Explicit Base/Bear/Bull pathways with quantified margin-delta fields.
- **D. Considered Actions:** Hedge review and reprioritization steps were concrete and operator-ready.
- **E. Invalidation Markers:** Spread normalization and pricing-power confirmation used as falsifiability checks.

## Limitations
- Current replay uses constrained synthetic graph seeds unless DB enrichment is available.
- Mapping quality is bounded by active watchlist/relationship coverage in the local data store.
- This replay demonstrates workflow rigor, not guaranteed performance outcomes.

## Reproducibility Notes
- Save linked artifacts under: `simulations/artifacts/<run_id>/`
- Record:
  - model name
  - environment mode
  - run command
  - metrics JSON and generated markdown output
