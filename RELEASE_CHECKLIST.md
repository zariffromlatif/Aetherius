# GitHub Open-Source Release Checklist

Use this checklist before making the repository public.

## 1) Security and Secret Hygiene

- [ ] Rotate any credentials that were ever stored locally during development (API keys, SMTP tokens, DB passwords).
- [ ] Confirm `.env` is not committed and remains git-ignored.
- [ ] Confirm `.env.example` contains placeholders only.
- [ ] Run a final secret scan across the workspace.
- [ ] Verify no sensitive values exist in docs, screenshots, or replay artifacts.

## 2) Repository Content Hygiene

- [ ] Keep generated runtime outputs out of commits (`simulations/artifacts/`, logs, caches).
- [ ] Keep only synthetic/non-client examples.
- [ ] Remove any private business or customer-only documents.
- [ ] Ensure root `README.md` is canonical and `aetherius/README.md` remains backend-scoped.

## 3) Open-Source Governance Files

- [ ] `LICENSE` is Apache-2.0.
- [ ] `OPEN_SOURCE_POLICY.md` is present and accurate.
- [ ] `CONTRIBUTING.md` is present and up to date.
- [ ] `SECURITY.md` contains a real reporting contact.
- [ ] `CODEOWNERS` references real GitHub usernames/teams.

## 4) Build and Quality Signals

- [ ] CI workflow exists and runs lint/tests.
- [ ] Local smoke check passes:
  - [ ] Test suite passes (`pytest aetherius/tests`)
  - [ ] SVB-2023 backtest passes (`python simulations/backtest/run_backtest.py --event svb-2023`)
  - [ ] Key docs render cleanly in Markdown preview
- [ ] No broken links in README/docs.

## 5) Public Positioning

- [ ] README clearly states what Aetherius is and is not.
- [ ] Disclaimer is present (not investment advice, no guaranteed outcomes).
- [ ] Detection track record references are current (`simulations/backtest/events/...`).
- [ ] No causal-simulation language in README, landing page, or outbound copy — the honest artifact is detection-timing, not causal inference.

## 6) GitHub Launch Steps

If this folder is not yet a git repository:

1. `git init`
2. `git add .`
3. `git commit -m "Initial open-source release"`
4. Create GitHub repo (empty) and copy its URL.
5. `git branch -M main`
6. `git remote add origin <your-repo-url>`
7. `git push -u origin main`

If this is already a git repository:

1. `git status`
2. `git add .`
3. `git commit -m "Prepare repository for open-source release"`
4. `git push`

## 7) Immediate Post-Launch Actions

- [ ] Enable GitHub Security Advisories.
- [ ] Enable Dependabot alerts and updates.
- [ ] Verify CI runs on the default branch.
- [ ] Create first release tag and changelog entry.
- [ ] Pin the best replay/validation docs in README for first-time visitors.
