# Aetherius Completion Validation Runbook

This runbook defines how to verify that Aetherius is truly production-complete against the final five acceptance gates.

Use this as the single source of truth before declaring the project complete.

---

## 0) Validation Rules

- No checkbox can be marked complete without **saved artifacts**.
- Use UTC timestamps for all logs and screenshots.
- Keep all validation artifacts under:

```text
simulations/validation/
  <yyyy-mm-dd>/
```

Recommended subfolders:

```text
simulations/validation/<date>/
  logs/
  metrics/
  screenshots/
  summary.md
```

---

## 1) Gate: Autonomy (48-hour stability)

### Objective

Prove `orchestrator.py` can run for 48 hours without crashing and continue producing logs/artifacts.

### Setup

Set environment:

```bash
set AETHERIUS_MODE=autonomous_research
set AETHERIUS_LOOP_SECONDS=21600
set AETHERIUS_WINDOW_HOURS=6
set AETHERIUS_MODEL_NAME=gpt-4o-mini
```

Optional for faster soak in staging:

```bash
set AETHERIUS_LOOP_SECONDS=900
```

### Execution

Start orchestrator:

```bash
python orchestrator.py
```

Run for 48h (or accelerated equivalent with documented compression factor).

### Evidence to Collect

- `aetherius_system.log` covering full window
- Count of `run_started`, `run_completed`, `run_failed` events
- Generated logs in `simulations/generated_logs/`
- If running as service: `systemctl status` and `journalctl` export

### Pass Criteria

- No unrecovered crash loop
- `run_completed` appears for each expected cycle
- `run_failed` events (if any) are retried and recovered
- Artifacts continuously generated across the test window

### Fail Criteria

- Orchestrator stops unexpectedly and does not recover
- Repeated failure backoff without successful completion
- Missing outputs for one or more expected cycles

---

## 2) Gate: Cost-Efficiency (cache discount proof)

### Objective

Prove prompt caching is active in real provider billing and discount path is working.

### Preconditions

- `AETHERIUS_API_KEY` configured
- `AETHERIUS_ENABLE_TTC=true`
- Correct provider base URL (`AETHERIUS_API_BASE_URL`) for OpenAI-compatible endpoint

### Execution

Run same replay repeatedly with same model/shock/state prefix:

```bash
python simulations/run_replay.py --shock-id shock-rate-50 --model-name gpt-4o-mini
python simulations/run_replay.py --shock-id shock-rate-50 --model-name gpt-4o-mini
python simulations/run_replay.py --shock-id shock-rate-50 --model-name gpt-4o-mini
```

### Evidence to Collect

- `*.metrics.json` files showing:
  - `cache_hit=true` on repeated runs
  - lower `token_spend_estimate` on cache hits
  - non-zero `provider_total_tokens` when provider call succeeds
- Provider dashboard screenshots (OpenAI/DeepSeek):
  - cached token usage
  - total token usage by run window

### Pass Criteria

- Dashboard confirms cached usage (target: `cached_tokens > 1024` during test window)
- Local metrics consistently show cache-hit behavior on repeated prefix
- Spend trend lower on repeated runs vs first run

### Fail Criteria

- No cached token evidence in dashboard
- No cache-hit observed in local metrics under repeated identical runs
- Provider usage absent due to failing TTC path

---

## 3) Gate: Causal Rigor (second-order reasoning)

### Objective

Demonstrate model outputs include second-order transmission (A -> B) instead of surface-level news summaries.

### Execution

Run two controlled replay scenarios with known graph linkages:

1. Upstream cost shock
2. Liquidity/refinancing shock

Use client-scoped and window-scoped replays where possible:

```bash
python simulations/run_replay.py --shock-id shock-supply --client-id <CLIENT_UUID> --window-start <ISO> --window-end <ISO>
python simulations/run_replay.py --shock-id shock-liquidity --client-id <CLIENT_UUID> --window-start <ISO> --window-end <ISO>
```

### Evidence to Collect

- Decision logs with explicit A-E sections
- Section B/C content showing transmission chains
- State metadata showing graph nodes/edges and watchlist/relationship enrichment
- Annotated review notes labeling each output as:
  - causal-pathway present
  - summary-only

### Pass Criteria

- At least 80% of evaluated outputs contain explicit second-order pathways
- Pathways reference entity relationships/exposure mechanics, not only headlines
- Invalidation markers are measurable and non-generic

### Fail Criteria

- Outputs are mostly narrative summaries of observations
- No consistent mapping from graph structure to scenario pathway

---

## 4) Gate: Proof Stack (3 high-fidelity historical replays)

### Objective

Have at least 3 replay documents that demonstrate meaningful historical flagging performance.

### Required Files (minimum)

- `simulations/replay_rate_hike_2026.md`
- `simulations/replay_vix_shock.md`
- `simulations/replay_<third_event>.md`  (new)

### Third Replay Suggestions

- `replay_commodity_input_spike.md`
- `replay_credit_spread_blowout.md`
- `replay_guidance_reset.md`

### Evidence to Collect

Each replay must include:

- event window and hypothesis
- timeline artifacts
- generated risk decision output
- benchmark metrics table
- failure modes and limitations

Use template:

- `docs/README_replay_case_studies.md`

### Pass Criteria

- 3 or more replay docs exist
- All three include reproducibility metadata and metric summaries
- At least two show clear lead-time or prioritization value over baseline process

### Fail Criteria

- Fewer than 3 replay docs
- Missing metrics or methodology details
- Unverifiable claims

---

## 5) Gate: Deployable & Research-Decoupled

### Objective

Confirm core modules can be reused in external thesis pipelines without tightly coupling to app internals.

### Execution

1. Run top-level pipeline directly (`core/* + orchestrator.py`) in isolation.
2. Run replay script with and without backend DB available.
3. Verify graceful fallback behavior when DB/API provider not present.

### Evidence to Collect

- Successful replay output with DB unavailable (fallback mode)
- Successful replay output with DB available (enriched mode)
- Import graph showing core modules independent from FastAPI routers
- Notes on integration points for thesis pipeline

### Pass Criteria

- Core pipeline executes standalone
- DB enrichment is optional, not hard dependency
- Interfaces are stable enough for external experimental loops

### Fail Criteria

- Core crashes without backend app context
- Hard dependency on API layer for simulation pipeline

---

## Final Signoff Matrix

Mark only after evidence is saved:

- [ ] Autonomy (48h)
- [ ] Cost-Efficiency (cached tokens proof)
- [ ] Causal Rigor (second-order mapping)
- [ ] Proof Stack (>= 3 high-fidelity replays)
- [ ] Deployable & Decoupled

Project can be declared complete only when all five boxes are checked with linked artifacts.

---

## Suggested `summary.md` Template

Create `simulations/validation/<date>/summary.md`:

```markdown
# Aetherius Completion Validation Summary

Date:
Validator:

## Results
- Autonomy: PASS/FAIL
- Cost-Efficiency: PASS/FAIL
- Causal Rigor: PASS/FAIL
- Proof Stack: PASS/FAIL
- Deployable & Decoupled: PASS/FAIL

## Evidence Links
- logs:
- metrics:
- screenshots:
- replay docs:

## Final Decision
- Complete / Not Complete
- Notes:
```
