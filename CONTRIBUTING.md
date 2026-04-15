# Contributing to Aetherius

Thanks for contributing to Aetherius.

This project combines:
- a research-oriented causal simulation core (`core/`, `orchestrator.py`)
- a supporting pilot backend (`aetherius/`)

Please keep contributions reproducible, benchmark-aware, and showcase-clean.

## 1) Contribution Workflow

1. Create a feature branch.
2. Keep changes focused to one area (core, simulations, docs, or backend).
3. Run tests/lint locally before opening a PR.
4. In the PR description, include:
   - what changed
   - why it changed
   - how it was validated

## 2) Repository Hygiene (Required)

- Treat generated outputs as ephemeral:
  - `simulations/artifacts/`
  - `.aetherius_prompt_cache.json`
  - runtime logs
- Do not commit secrets (`.env`, API keys, tokens).
- Keep canonical implementations only; remove duplicate legacy scripts.
- Keep root docs technical and evidence-based.
- Move internal planning/business-only drafts to private storage or an archive branch.

## 3) Coding Guidelines

- Prefer small, testable functions.
- Preserve deterministic fallback behavior for critical paths.
- Keep risk outputs in strict A-E format.
- Maintain backward-compatible interfaces where possible (`core/contracts.py`).
- Use ASCII text unless a file already depends on Unicode symbols.

## 4) Testing and Validation

Minimum expected validation:

```bash
python simulations/run_replay.py --shock-id shock-rate-50
```

For code changes touching orchestrator/core behavior:
- verify replay artifacts are generated
- verify metrics JSON includes expected fields
- confirm no linter errors

For completion-level changes, follow:
- `docs/completion_validation_runbook.md`

## 5) Simulation/Benchmark Standards

If you add or update replay studies:
- use `docs/README_replay_case_studies.md` template
- include methodology, limitations, and reproducibility metadata
- avoid unverified performance claims

If you add scoring or causal logic:
- align outputs with `docs/benchmark_spec.md`
- include at least one measurable validation artifact

## 6) TTC Provider Changes

When modifying model/provider integrations:
- preserve safe fallback when provider keys/calls fail
- keep cache behavior and telemetry intact
- ensure env-driven configuration remains supported:
  - `AETHERIUS_ENABLE_TTC`
  - `AETHERIUS_MODEL_NAME`
  - `AETHERIUS_API_KEY`
  - `AETHERIUS_API_BASE_URL`
  - `AETHERIUS_API_TIMEOUT_SECONDS`

## 7) Pull Request Checklist

- [ ] Scope is focused and documented
- [ ] No secrets committed
- [ ] No generated artifacts committed
- [ ] Replay run succeeds for affected flow
- [ ] Docs updated when behavior changes
- [ ] Claims in README/docs match implementation reality
