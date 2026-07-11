# Validation Evidence Folder

Per-event validation artifacts live in dated subfolders here. Each event's folder should contain:

```text
simulations/validation/
  <event-id>/
    metrics.json     # produced by simulations/backtest/run_backtest.py
    summary.md       # human-readable writeup: methodology, corpus provenance, limitations
```

See `simulations/validation/svb-2023/` for the reference format.

The `metrics.json` schema is defined by the backtest harness itself (`simulations/backtest/run_backtest.py`) and includes:

- `detection_recall`, `mapping_precision`, `false_positive_count`, `median_lead_time_days`
- per-ticker `detections` and `misses`
- an `anti_hype_note` making the scope of the evidence explicit

Every new event must include a real primary-source `observations.jsonl` under `simulations/backtest/events/<event-id>/` — see `CONTRIBUTING.md` §5.
