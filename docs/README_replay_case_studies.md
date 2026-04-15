# Aetherius Replay Case Studies Template

Use this template to publish historical replay studies in a consistent, credible format.  
Goal: show what Aetherius observed, inferred, and delivered under controlled conditions without overclaiming.

---

## 1) Case Study Header

- **Case ID:** `replay-YYYY-MM-event-name`
- **Event Name:**  
- **Window Covered (UTC):**  
- **Primary Universe / Watchlist Scope:**  
- **Author / Reviewer:**  
- **Spec Version:** `benchmark_spec_vX.Y`
- **Commit SHA:**  
- **Dataset Snapshot ID:**  

---

## 2) Executive Summary (3-5 bullets)

- What happened in the market context.
- What Aetherius detected and when.
- What would have reached operator review.
- What quality/reliability metrics mattered most.
- Key takeaway and limitation.

---

## 3) Event Context

### 3.1 Background

Briefly describe the macro/company event and why it mattered.

### 3.2 Hypothesis

State the replay hypothesis in one sentence:

> "Given observations in this window, Aetherius should surface [type] risk signals for [names/themes] before [baseline trigger]."

### 3.3 Baseline Comparison

Define what baseline you compare against:

- manual analyst workflow
- keyword alerting
- legacy process timing

---

## 4) Experimental Setup

### 4.1 Inputs

- observation sources used
- watchlists, aliases, and relationships loaded
- config profile (alert thresholds, channels, pilot mode)

### 4.2 Run Configuration

- environment (local/staging)
- queue settings
- model/settings flags, if any
- random seed(s), if applicable

### 4.3 Guardrails

- no autonomous client sends
- operator-reviewed workflow only
- no future data leakage

---

## 5) Timeline Replay

Provide a concise timeline table.

| Time (UTC) | Pipeline Stage | Artifact | Notes |
|------------|----------------|----------|-------|
| 00:00 | Observation ingested | `observation_id` | source + freshness |
| 00:05 | Mapping created | `evidence_link_id` | direct / readthrough |
| 00:06 | Signal generated | `risk_signal_id` | severity + urgency |
| 00:10 | Brief drafted | `briefing_run_id` | pending_review |
| 00:20 | Operator action | `operator_action_id` | approved/edited/suppressed |
| 00:21 | Delivery attempt | `delivery_id` | sent/failed + reason |

---

## 6) Output Artifacts

List artifact links/paths:

- observation extracts
- evidence mappings
- generated signals
- draft brief snapshot
- operator action log
- delivery log

If redacting client-sensitive data, state redaction policy.

---

## 7) Results

### 7.1 Core Metrics

Use metrics from `docs/benchmark_spec.md`.

| Metric | Value | Baseline | Delta | Notes |
|--------|-------|----------|-------|-------|
| Lead-Time to Detection |  |  |  |  |
| Mapping Precision@1 |  |  |  |  |
| Signal Precision (elevated/high) |  |  |  |  |
| False Positive Rate |  |  |  |  |
| End-to-End Latency p95 |  |  |  |  |
| Delivery Success Rate |  |  |  |  |

### 7.2 Qualitative Assessment

- Was the signal understandable?
- Was the evidence chain clear?
- Would this have changed operator behavior?

---

## 8) Decision Log Evaluation (A-E format)

Evaluate the output against your response structure:

### A) What Changed

Did the anomaly/event get represented accurately?

### B) Why It Matters

Did the brief connect event to exposure/risk mechanism?

### C) What Happens Next

Was scenario framing (base/bear/bull) useful and bounded?

### D) Considered Actions

Were suggested actions concrete and reviewable?

### E) Invalidation Markers

Were invalidation conditions explicit and testable?

---

## 9) Failure Modes and Limitations

Document what did not work:

- mapping misses
- noisy signals
- latency spikes
- delivery issues
- reasoning gaps

State whether each issue is:

- data issue
- rule/model issue
- operations issue

---

## 10) Remediation Plan

| Issue | Fix | Owner | ETA | Status |
|------|-----|-------|-----|--------|
|  |  |  |  |  |

---

## 11) Reproducibility Checklist

- [ ] commit SHA recorded
- [ ] dataset snapshot ID recorded
- [ ] config hash recorded
- [ ] time window documented
- [ ] artifacts archived
- [ ] no future leakage confirmed
- [ ] benchmark metrics reproducible

---

## 12) Anti-Hype Compliance Statement

Include this statement (edit as needed):

> "This replay demonstrates process quality and timing under a defined protocol.  
> It does not claim guaranteed investment outcomes or deterministic performance."

---

## 13) Publication Snippet (Optional)

Use for README/docs index:

> "In this replay, Aetherius surfaced [risk theme] for [watchlist scope] [X minutes/hours] before baseline workflow, with [metric highlights]. Primary limitations were [top limitations]."

---

## 14) File Naming Convention

Recommended structure:

```text
docs/replays/
  replay-YYYY-MM-event-name.md
  assets/
    replay-YYYY-MM-event-name/
      timeline.csv
      metrics.json
      artifacts-index.md
```

---

## 15) Quick Copy-Paste Skeleton

```markdown
# Replay: <Event Name>

## Executive Summary
- ...

## Event Context
...

## Experimental Setup
...

## Timeline Replay
| Time (UTC) | Pipeline Stage | Artifact | Notes |
|------------|----------------|----------|-------|
| ... | ... | ... | ... |

## Results
| Metric | Value | Baseline | Delta | Notes |
|--------|-------|----------|-------|-------|
| ... | ... | ... | ... | ... |

## Decision Log Evaluation (A-E)
...

## Failure Modes and Limitations
...

## Remediation Plan
| Issue | Fix | Owner | ETA | Status |
|------|-----|-------|-----|--------|
| ... | ... | ... | ... | ... |

## Reproducibility Checklist
- [ ] ...

## Anti-Hype Compliance Statement
...
```
