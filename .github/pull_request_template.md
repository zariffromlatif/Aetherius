## Summary

- What changed?
- Why was this needed?

## Validation

- [ ] Relevant tests pass (`pytest -q aetherius/tests`)
- [ ] SVB-2023 backtest still passes if scoring / mapping / ingestion changed
- [ ] Lint passes (`ruff check aetherius`)
- [ ] Docs updated if behavior changed

## Scope

- [ ] Ingestion, entity mapping, scoring, or signals (`aetherius/app/services/...`)
- [ ] Delivery / templates / review workflow
- [ ] Backtests (`simulations/backtest/...`)
- [ ] Docs / governance / landing page only

## Safety Checklist

- [ ] No secrets committed (`.env`, API keys, tokens)
- [ ] No generated artifacts committed (`simulations/artifacts/`, runtime logs)
- [ ] No client-specific / private data included
- [ ] Marketing / README claims still match implementation reality

## Notes for Reviewers

- Any migration impacts?
- Any backward-compatibility concerns?
- Any operational risks?
