# Simulations and Replay Runner

This folder is the Aetherius proof stack for historical replay and decision-log artifacts.

## Contents

- `run_replay.py` - CLI runner for a single replay.
- `replay_rate_hike_2026.md` - documented case study template instance.
- `replay_vix_shock.md` - documented volatility shock replay.
- `replay_credit_spread_blowout.md` - third high-fidelity replay for spread-stress scenarios.
- `sample_risk_decision_log.md` - canonical A-E output format.
- `artifacts/` - generated outputs (ignored by git).
- `validation/` - evidence pack template for completion signoff.

## Run a Replay

From repo root:

```bash
python simulations/run_replay.py --shock-id shock-rate-50
```

Optional client-scoped and time-window run:

```bash
python simulations/run_replay.py \
  --shock-id shock-supply \
  --client-id <CLIENT_UUID> \
  --window-start 2026-01-15T09:00:00Z \
  --window-end 2026-01-15T16:00:00Z
```

## Output Artifacts

Each run writes to:

`simulations/artifacts/<run_id>/`

- `<shock_id>.md` - Risk Decision Log (A-E format)
- `<shock_id>.metrics.json` - benchmark-style metrics payload

## Metrics Interpretation

Key fields in `*.metrics.json`:

- `state_metadata.watchlist_items` - how many scoped watchlist items were included in graph state.
- `forage_chunks` and `forage_dropped_chunks` - ingestion/semantic-filter signal.
- `risk_score`, `urgency_score`, `confidence` - replay simulation outputs.
- `evidence_ref_count` and `evidence_refs` - linked evidence traceability.
- `quality_flags` - output shape and minimum quality checks.

Use these artifacts alongside:

- `docs/benchmark_spec.md`
- `docs/README_replay_case_studies.md`

to produce reproducible, non-hyped replay reports.
