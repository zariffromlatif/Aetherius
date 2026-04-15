## Summary

- What changed?
- Why was this needed?

## Validation

- [ ] `python simulations/run_replay.py --shock-id shock-rate-50` passes
- [ ] Relevant tests pass (`pytest -q aetherius/tests`)
- [ ] Lint passes (`ruff check aetherius`)
- [ ] Docs updated if behavior changed

## Scope

- [ ] Core simulation (`core/`, `orchestrator.py`, `simulations/`)
- [ ] Backend operations (`aetherius/app/`, workers, templates)
- [ ] Docs/governance only

## Safety Checklist

- [ ] No secrets committed (`.env`, API keys, tokens)
- [ ] No generated artifacts committed (`simulations/artifacts/`, runtime logs, caches)
- [ ] No client-specific/private data included

## Notes for Reviewers

- Any migration impacts?
- Any backward-compatibility concerns?
- Any operational risks?
