# Validation Evidence Folder

Use this folder to store completion-check evidence required by:

- `docs/completion_validation_runbook.md`

## Suggested structure

```text
simulations/validation/
  YYYY-MM-DD/
    logs/
    metrics/
    screenshots/
    summary.md
```

## What to store

- 48-hour autonomy run logs (`aetherius_system.log` snapshots)
- replay metrics JSON files used for TTC/cache proof
- provider dashboard screenshots showing cached token usage
- final signoff summary with pass/fail per gate
