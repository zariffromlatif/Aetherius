# Aetherius Benchmark Specification

This document defines how Aetherius is evaluated for technical quality, operational reliability, and economic viability.

## 1) Purpose

Establish a reproducible benchmark framework across four dimensions:

1. Ingestion and mapping quality
2. Signal and briefing quality
3. Production reliability and latency
4. Unit economics and research-track causal simulation quality

## 2) Benchmark Principles

- **Reproducible:** every run must include commit hash, config snapshot, and dataset window.
- **Time-safe:** no future leakage into historical/replay evaluations.
- **Traceable:** metrics must tie back to concrete run IDs and evidence IDs.
- **Comparable:** every metric should have a baseline reference.
- **Actionable:** every report must end with fix plans, not only scores.

## 3) Evaluation Datasets

### 3.1 Live Pilot Dataset

- Real observations captured during pilot operation.
- Ground truth from operator adjudication and client feedback tags.

### 3.2 Historical Replay Dataset

- Frozen event windows for known market disruptions.
- Includes observations, watchlists, aliases/relationships, and timestamps.
- Used to compare detection timing and ranking behavior.

### 3.3 Synthetic Stress Dataset

- Purpose-built noisy inputs:
  - duplicate payloads
  - stale items
  - malformed text
  - low-signal chatter
- Used for resilience and false-positive pressure tests.

## 4) Metric Families

### A) Ingestion and Mapping

1. **Deduplication Precision**  
   Share of dropped items that are true duplicates.
2. **Deduplication Recall**  
   Share of true duplicates successfully dropped.
3. **Freshness Classification Accuracy**  
   Correct stale/non-stale labeling.
4. **Watchlist Mapping Precision@1**  
   Correctness of top mapped watchlist item.
5. **Readthrough Mapping Precision**  
   Correctness of supplier/customer/peer relationship mapping.

### B) Signal Quality

6. **Signal Precision by Severity** (`low`, `normal`, `elevated`, `high`)  
   Precision based on operator adjudication.
7. **False Positive Rate**  
   Fraction tagged as noisy/generic/not-actionable.
8. **Lead-Time to Detection**  
   Time from first relevant observation to first approved signal.
9. **Priority Ranking Quality (NDCG@k)**  
   Ranking quality of `brief_priority_score` vs operator labels.
10. **Evidence Completeness Rate**  
   Share of elevated/high outputs with valid evidence refs.

### C) Operational Reliability

11. **Draft-to-Send Success Rate**
12. **Delivery Success Rate**
13. **Retry Recovery Rate**
14. **Queue Delay p50/p95**
15. **End-to-End Latency p50/p95**  
   From observation ingestion time to successful send time.

### D) Unit Economics

16. **Cost per 100 Observations**
17. **Cost per Sent Brief**
18. **Prompt/Cache Hit Rate** (for optimizer module when enabled)
19. **Compute Time per End-to-End Run**

### E) Causal World-Model (Research Track)

20. **Transition Forecast Calibration**
21. **Scenario Ranking Accuracy** (base/bear/bull ordering quality)
22. **Causal Link Precision** (expert-reviewed)
23. **Counterfactual Consistency Score**

## 5) Ground Truth Policy

Ground truth should be layered:

1. **Primary:** operator adjudication labels.
2. **Secondary:** client feedback tags (useful/noisy/too_late/etc.).
3. **Tertiary:** realized event outcomes in replay windows.

Adjudication rubric must be versioned and shared with benchmark outputs.

## 6) Experimental Modes

### 6.1 Offline Replay Mode

- Run pipeline on frozen historical windows.
- Measure ranking, lead-time, and causal-research metrics.

### 6.2 Shadow Mode (Live)

- Run Aetherius beside existing analyst workflow.
- No autonomous action.
- Compare timing and quality against baseline manual process.

### 6.3 Pilot Production Mode

- Operator-approved sends only.
- Track reliability, quality, and cost weekly.

## 7) Initial Acceptance Targets (Pilot Phase)

These are initial targets and should be tuned with real pilot data:

- Mapping Precision@1: **>= 0.80**
- Elevated/high evidence completeness: **100%**
- Delivery success rate: **>= 0.98**
- End-to-end latency p95: **within agreed client SLA**
- False positive rate: **decreasing trend week-over-week**
- Cost per sent brief: **within pilot budget envelope**

## 8) Weekly Benchmark Report Format

Each report should include:

1. Executive summary (3 to 5 bullets)
2. Metric table (current vs previous vs delta)
3. Highest-impact failure modes
4. Changes applied this week
5. Open risks and blocked items
6. Next-week tuning plan

## 9) Reproducibility Requirements

Every benchmark run must log:

- git commit SHA
- config hash/version
- model version(s), if any
- dataset snapshot/window ID
- random seed(s)
- timestamp range
- output artifact location

Store artifacts for audit:

- generated signals
- evidence mappings
- briefing outputs
- delivery logs
- metric JSON/CSV

## 10) Anti-Hype Reporting Rules

- Do not claim guaranteed outcomes or deterministic alpha.
- Separate clearly:
  - early detection
  - high-priority ranking
  - causal mechanism confidence
- Publish uncertainty and known failure modes.

## 11) Versioning

This spec should be versioned.  
Recommended format: `benchmark_spec_v{major}.{minor}` with change log entries for metric additions or threshold changes.
