# Contributing to Aetherius

Thanks for contributing to Aetherius.

This project is a per-target risk-report pipeline: SEC EDGAR ingestion, conservative entity mapping, deterministic scoring, and human-supervised PDF delivery — with historical detection-timing backtests as its credibility artifact.

Please keep contributions reproducible, evidence-based, and honest.

## 1) Contribution Workflow

1. Create a feature branch.
2. Keep changes focused to one area (ingestion, mapping, scoring, delivery, backtests, docs).
3. Run tests locally before opening a PR.
4. In the PR description, include:
   - what changed
   - why it changed
   - how it was validated

## 2) Repository Hygiene (Required)

- Treat generated outputs as ephemeral: `simulations/artifacts/`, runtime logs.
- Do not commit secrets (`.env`, API keys, tokens).
- Do not import from `archive/` — it retains deprecated scaffolding from an earlier positioning that was walked back.
- Keep root docs technical and evidence-based. Marketing claims must match implementation reality.

## 3) Coding Guidelines

- Prefer small, testable functions.
- Preserve deterministic behavior in the scoring and mapping paths — an LLM must never gate what the pipeline flags.
- Match the surrounding code's style (comment density, naming, idiom).
- Use ASCII unless the file already uses Unicode.

## 4) Testing and Validation

Run the full test suite:

```bash
pytest aetherius/tests
```

The SVB-2023 backtest is a pinned integration test — any change that breaks it must be justified in the PR description.

For scoring, mapping, or ingestion changes, add or update a fixture-driven test alongside the change.

## 5) Backtest Standards

When adding a new backtest event under `simulations/backtest/events/`:

- Include `watchlist.json`, `ground_truth.json`, and `observations.jsonl`.
- **Observations must come from a real primary-source archive** (GDELT, SEC EDGAR, Wayback, etc.) — not hand-authored summaries. The `provenance` field must state the archive and query used.
- Include a non-affected control name in the watchlist to test for false positives.
- Do not tune the pipeline against a fixture, then claim the fixture as validation.

## 6) Pull Request Checklist

- [ ] Scope is focused and documented
- [ ] No secrets committed
- [ ] No generated artifacts committed
- [ ] `pytest aetherius/tests` passes
- [ ] SVB backtest still passes if scoring/mapping changed
- [ ] Docs updated when behavior changes
- [ ] Claims in README / landing page match implementation reality
