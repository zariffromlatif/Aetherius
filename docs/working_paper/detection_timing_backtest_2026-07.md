# Detection-Timing Backtest of a Systematic Downside-Risk Screen Across Three Modern Financial Crises

**A working paper. Aetherius Risk Intelligence. July 2026.**
**Author:** Zarif Latif · zarif@aetheriusresearch.tech

---

## Abstract

We replay a systematic entity-mapping and severity-scoring pipeline against real primary-source news headlines from three widely-studied financial crises — the March 2023 U.S. regional-banking contagion, the June 2020 Wirecard AG accounting-fraud disclosure, and the November 2022 FTX collapse — and report per-name detection timing, mapping precision, and false-positive control behavior.

Across the three frozen historical windows (161 real news observations sourced from GDELT DOC 2.0), the pipeline flagged **9 of 9 affected names at "elevated" or "high" severity before the realized event date** (100% recall), with a **median lead time of 2.5 days** and **zero false positives on the three unrelated control names** included in the watchlists.

We describe the pipeline, the corpus construction, the ground-truth definition, and the honest limitations of the exercise. All code, data, and pinned tests are Apache-2.0 licensed and reproducible from the open repository.

**This is early-detection and prioritization evidence on frozen historical windows. It is not a return forecast, a trading signal, or a claim of causal mechanism confidence.**

---

## 1. Motivation

Concentrated public-equity books — held by search funds, small family offices, litigation-finance analysts, small credit shops, and single-name activists — carry outsized single-name risk. The generic surveillance products aimed at large institutions (Bloomberg terminals, Reorg/Octus, S&P Capital IQ, and the major expert networks) are priced and configured for buyers with dozens of analysts. They are not shaped for the small book.

The obvious alternative — "just read the news" — fails not because news is scarce, but because it is abundant. In the SVB-2023 window used in this paper, the GDELT DOC 2.0 index returned roughly 250 articles per ticker per week from wire-quality sources alone. A concentrated book of 5–10 names, monitored across two overlapping windows, easily produces several thousand candidate headlines per week. Human triage of that volume is expensive, uneven, and forgets weekends.

The value of a **systematic pipeline** in this setting is not "AI insight." It is:

1. **Idempotent entity resolution** — every headline gets a conservative, word-boundary-safe answer to *"does this really mention one of our names, or a lookalike token?"*
2. **Deterministic severity scoring** — every observation gets an event-severity score against a fixed adverse-language taxonomy, so no single headline is ever "missed" because the analyst was in a meeting.
3. **A pinned false-positive discipline** — the same pipeline that fires an "elevated" flag on adverse content on a watchlist name must stay quiet on adverse content on names outside the book, and quiet on benign content on names inside the book.

The question this paper asks is narrow and testable: **given the information that actually existed at the time, on real primary-source headlines, would this pipeline have flagged the affected names of a modern crisis before the realized event date, without false-positiving unrelated controls?**

We test it on three crises. The answer, on these three, is yes.

---

## 2. Pipeline overview

The pipeline used for this paper is the production Aetherius stack, unmodified for the exercise. Every function below is Apache-2.0 licensed and lives at the referenced path.

### 2.1 Ingestion

Two adapters produce `SourceObservations` rows from primary sources:

- **`aetherius/app/services/ingestion/edgar_adapter.py`** — resolves a ticker to a 10-digit SEC CIK via the public `company_tickers.json` endpoint, pulls submissions via `data.sec.gov`, filters to a fixed set of downside-relevant forms (`8-K`, `10-Q`, `10-K`, `NT 10-Q`, `NT 10-K`, and their amendments), and writes one observation per filing.

- **`aetherius/app/services/ingestion/gdelt_adapter.py`** — queries GDELT DOC 2.0 for a phrase-OR block of the target company name and its aliases, filters the response to a curated whitelist of primary financial-news domains, and writes one observation per article. Query length is capped by GDELT so the domain filter is applied client-side after fetch. Each observation is deduplicated by article URL.

For this paper, all news observations come from the GDELT adapter. EDGAR is used only in production live-target flows; for a backtest, GDELT gives complete historical coverage of narrative flow (deposit-run reporting, ratings actions, executive-departure announcements) that filings alone cannot recreate.

### 2.2 Entity mapping

`aetherius/app/services/entity_mapping/service.py` runs each observation's raw text through a **conservative** matcher:

- Word-boundary regex — `(?<![A-Z0-9]){name}(?![A-Z0-9])` — so ticker `AI` cannot match inside `CHAIN` or `SAID`, and ticker `CAT` cannot match inside `CATALYST`.
- An acronym stoplist that drops common non-ticker tokens: role labels (`CEO`, `CFO`), macro terms (`GDP`, `CPI`, `FED`), currencies, regulators, and general tech acronyms (`AI`, `API`, `IPO`).
- A structured match against watchlist `aliases` and `relationships`, returning the relationship type and a relevance score.

The output is either a `(relationship_type, relevance)` tuple or `None`. This is the layer that keeps the SVB-2023 control `MSFT` (Microsoft) from being flagged on its Copilot-expansion news even though its ticker appears in the observation.

### 2.3 Severity scoring

`aetherius/app/services/scoring/service.py` computes three deterministic scores per matched observation:

- **Risk score** — a weighted combination of source confidence, freshness, directness, cross-confirmation, watchlist priority, event severity, and relationship strength.
- **Urgency score** — a function of time sensitivity, event severity, novelty, and proximity to a monitored event window.
- **Brief priority score** — a function of the above plus novelty and affected-names count.

`severity_label()` bins the risk score into `low`, `moderate`, `elevated`, or `high`. `confidence_label()` bins into `low`, `medium`, `high`. Every weight is a compile-time constant; no learned parameters.

### 2.4 Adverse-language gate

The backtest harness (`simulations/backtest/run_backtest.py`) computes `_adverse_severity(raw_text)` against a fixed downside-language taxonomy: `loss`, `plunge`, `withdrawal`, `deposit run`, `receivership`, `collapse`, `funding pressure`, `distress`, `insolven*`, and roughly 30 others. A name match on benign content — no adverse tokens at all — is **not** shippable, however direct the entity match. This is the second gate keeping the MSFT control clean.

An observation becomes a "shippable flag" only when: (a) the severity label is `elevated` or `high`, **and** (b) `event_severity_score > 0` (at least one adverse token present).

### 2.5 Backtest harness

`simulations/backtest/run_backtest.py` loads an event's `watchlist.json`, `ground_truth.json`, and `observations.jsonl`, replays every observation through the production entity-mapping and scoring code above, tracks the earliest shippable flag per watchlist name, and computes:

- **Detection recall** — fraction of `ground_truth.affected` names that produced a shippable flag before the realized event date, reaching the expected minimum severity.
- **Mapping precision** — fraction of raw entity matches attributable to affected names or their declared relationships.
- **Median lead time** — median hours between first shippable flag and realized event, across detected names.
- **False positives** — `controls_should_not_flag` names that produced any shippable flag on the window.

The harness is fully offline once the fixture is on disk. Rerunning the same fixture at the same commit produces bit-identical metrics.

---

## 3. Corpus construction

Every observation in every fixture in this paper came from GDELT DOC 2.0. No hand-authored summaries. Each article's provenance line is preserved in the observation's `provenance` field. Each article's real URL is preserved in `source_url` and can be independently retrieved from the publisher or from `web.archive.org`.

The corpus is built by `simulations/backtest/build_fixture.py`, which:

1. Reads the event's watchlist and ground-truth files.
2. For each watchlist item, queries GDELT DOC 2.0 for a phrase-OR block of `company_name` plus `aliases`, restricted to the event window (`window_start`, `window_end`), sorted `DateAsc`, up to `max_records` articles per target.
3. Applies a client-side domain whitelist (Reuters, Bloomberg, WSJ, FT, MarketWatch, CNBC, Yahoo Finance, SEC.gov, FDIC.gov, Motley Fool, Investors Business Daily, TechCrunch, Business Insider, American Banker, and roughly ten others).
4. Deduplicates by URL across targets.
5. Prepends the pinned regulatory anchors from `ground_truth.primary_sources` (SEC filings, FDIC releases, insolvency filings) at their approximate observation timestamps.
6. Writes the merged, chronologically-sorted `observations.jsonl` to the event directory.

Per-target GDELT responses are cached under `_gdelt_cache/<TICKER>.json` so partial failures (rate limiting, network flap) resume without re-fetching what succeeded. The observations file is committed; the cache is git-ignored.

### 3.1 Note on hand-curated fixtures

An earlier version of the SVB-2023 fixture was hand-authored: 10 rows of "curated public-record summaries" that the `provenance` field itself labeled as such. Any technically-literate reader of the public repository could — and did — dismiss the corpus as reverse-engineered. That hand-authored fixture has since been removed from the repository entirely; the pipeline is now tested only against real GDELT-scraped headlines. Every result in Section 4 uses that real corpus.

---

## 4. Results

### 4.1 Aggregate

Across all three events:

| Metric | Value |
|---|---|
| Events | 3 |
| Observations replayed | 161 |
| Watchlist size (union across fixtures) | 12 (9 affected + 3 controls) |
| Names detected at expected severity | **9 / 9 (100%)** |
| Median lead time across the 9 flagged names | **2.48 days** |
| Mean lead time across the 9 flagged names | 3.58 days |
| Mapping precision (weighted across events) | 100% |
| False positives on controls | **0 / 3** |

The nine detected names came from three unrelated failure modes: bank runs (SVB, Signature, First Republic, Western Alliance, PacWest), accounting fraud (Wirecard), and crypto counterparty contagion (Silvergate, Coinbase, Signature Bank exposure to FTX). No mechanism-specific tuning was applied between events.

### 4.2 SVB-2023

**Event.** SVB Financial Group (SIVB) disclosed on 2023-03-08 a $21B securities sale at a loss and a $2.25B capital raise. Deposit outflows overwhelmed the bank's liquidity; the FDIC took SVB into receivership on 2023-03-10. Contagion spread across the regional-bank cohort; Signature Bank was closed on 2023-03-12 and First Republic ultimately failed on May 1, 2023.

**Watchlist.** Five affected regional banks (SIVB, SBNY, FRC, WAL, PACW) plus MSFT as a non-bank control.

**Corpus.** 98 observations from GDELT DOC 2.0 filtered to the primary-financial-news whitelist for the window 2023-03-06 to 2023-03-12, plus the SEC 8-K and FDIC receivership anchors.

**Results.**

| Ticker | First flag | Realized event | Lead (d) | Peak severity | First-flag evidence |
|---|---|---|---|---|---|
| SIVB | 2023-03-09 13:00Z | 2023-03-10 | 0.46 | high | marketwatch.com — *SVB Financial stock plummets toward biggest one-day selloff in 23 years* |
| SBNY | 2023-03-09 12:30Z | 2023-03-12 | 2.48 | high | marketwatch.com — *Signature Bank stock drops sharply after Silvergate announces winddown* |
| FRC | 2023-03-09 17:45Z | 2023-03-13 | 3.26 | high | fool.com — *Why Shares of First Republic Bank Are Falling Today* |
| WAL | 2023-03-10 15:45Z | 2023-03-13 | 2.34 | elevated | investors.com — *SVB Trading Halted, Company Seeks Buyer, Financial Stocks Shudder* |
| PACW | 2023-03-10 15:45Z | 2023-03-13 | 2.34 | high | investors.com — *SVB Trading Halted, Company Seeks Buyer, Financial Stocks Shudder* |

**Recall 5/5. Median lead 2.34 days. Mapping precision 100%. False positives on MSFT: 0.**

MSFT was mentioned in 12 observations across the window, entirely in benign product-news context (Copilot expansion, Windows updates). The word-boundary matcher and adverse-language gate both fired as designed: MSFT observations reached name-match confidence but zero adverse-severity, and were therefore never shippable.

### 4.3 Wirecard-2020

**Event.** On 2020-06-18 Wirecard AG (WDI) disclosed that €1.9B in cash reported on its balance sheet "likely does not exist." The CEO Markus Braun resigned the next day. Wirecard filed for insolvency at the Munich District Court on 2020-06-25, wiping out equity holders.

This event is a useful stress test because the mechanism is idiosyncratic fraud, not sector-wide stress. A pipeline that overfits to bank-run vocabulary would either miss it or false-positive every payments peer.

**Watchlist.** Wirecard (WDI) plus Deutsche Telekom (DTE) as an unrelated DAX control. Payments-sector peers (Adyen, PayPal) are intentionally excluded from this fixture — for an idiosyncratic fraud event, declared peer relationships would (correctly) fire `peer_readthrough` flags on the peers, which are valid analyst-facing signals but not "false positives" in the pipeline sense. The clean two-name fixture avoids that ambiguity; the peer-readthrough behavior is documented and demonstrable but requires a separate human-reviewer-dismissal rubric to score cleanly, which we defer to a future paper.

**Corpus.** 14 observations from GDELT DOC 2.0 for the window 2020-06-15 to 2020-06-30 (Wirecard's European coverage skews to non-U.S. domains that fall outside our primary-source whitelist; the whitelist is deliberately not expanded post-hoc to inflate the corpus).

**Results.**

| Ticker | First flag | Realized event | Lead (d) | Peak severity | First-flag evidence |
|---|---|---|---|---|---|
| WDI | 2020-06-18 09:30Z | 2020-06-25 | 6.60 | high | marketwatch.com — *Wirecard shares plunge as Ernst & Young says no evidence for 1.9 billion euros of cash on balance sheet* |

**Recall 1/1. Lead time 6.60 days. Mapping precision 100%. False positives on DTE: 0.**

DTE appeared in the corpus but only in mundane telecom coverage. Adverse-language gate stayed at 0. No shippable flag.

### 4.4 FTX-2022

**Event.** On 2022-11-02 CoinDesk published a leaked balance sheet showing that Alameda Research's assets were largely FTT tokens issued by its sister exchange FTX. Binance CEO Changpeng Zhao announced intent to liquidate Binance's FTT holdings on 2022-11-06, triggering a bank run on FTX. Withdrawals were halted on 2022-11-08. FTX filed Chapter 11 on 2022-11-11.

FTX itself was privately held; the interesting test case is contagion into the public-equity crypto ecosystem. Silvergate Capital (SI) — a crypto-focused bank with direct deposit relationships to FTX — was the most exposed and ultimately wound down in early 2023.

**Watchlist.** Silvergate (SI), Coinbase (COIN), Signature Bank (SBNY, via its crypto-linked Signet platform), and Microsoft (MSFT) as a non-crypto control.

**Corpus.** 49 observations from GDELT DOC 2.0 for the window 2022-11-02 to 2022-11-14.

**Results.**

| Ticker | First flag | Realized event | Lead (d) | Peak severity | First-flag evidence |
|---|---|---|---|---|---|
| SI | 2022-11-03 21:00Z | 2022-11-11 | 7.12 | high | fool.com — *Why Coinbase, Silvergate Capital, and Marathon Digital Holdings...* |
| COIN | 2022-11-03 21:00Z | 2022-11-11 | 7.12 | high | fool.com — *Why Coinbase, Silvergate Capital, and Marathon Digital Holdings...* |
| SBNY | 2022-11-10 11:00Z | 2022-11-11 | 0.54 | elevated | marketwatch.com — *Robinhood, Coinbase Distance Themselves from FTX After Crypto...* |

**Recall 3/3. Median lead 7.12 days. Mapping precision 100%. False positives on MSFT: 0.**

The two 7.12-day leads on SI and COIN both trace to a single Motley Fool article on 2022-11-03 that discussed all three names in an adverse-signal frame. This is a legitimate concentration risk in the evidence — had that one article not been in the corpus, both leads would compress materially. The article is public, indexed by GDELT, and would have been surfaced by any 2022-11-03 sweep of the whitelisted domains.

---

## 5. Honest limitations

### 5.1 What this exercise does and does not measure

**It measures:** whether, given a curated whitelist of primary-financial-news domains and a real archived corpus, the pipeline flags known-affected watchlist names at elevated or high severity before the realized event date, without false-positiving unrelated controls.

**It does not measure:**

- **Return** — no PnL, no shorting, no position sizing.
- **Causality** — the pipeline uses no causal model. It measures narrative and severity correlation on the wire.
- **Coverage on unfiltered feeds** — the whitelist is deliberate. On the full GDELT firehose (aggregators, translation mirrors, press-release wires) false-positive rates would be higher and require additional filtering.
- **Performance on non-Anglophone events** — the Wirecard-2020 corpus is thin (14 observations) precisely because European coverage skews to domains outside our whitelist. The recall metric is unchanged (1/1 on the affected name), but the pipeline's sensitivity on non-U.S. events is not fully characterized.
- **Robustness to adversarial input** — a company issuing intentionally misleading press releases in the window could produce a false-negative in adverse-language scoring. There is no defense against fraud in the corpus itself.

### 5.2 Sample size

Three events is a small sample. The 100% recall and 0 false positives across the three are the numbers to report, but the honest confidence interval around them is wide. A fourth event that failed the pipeline would drop aggregate recall to 9/10 or 8/9 and would deserve equal reporting. The intent is to extend the paper to at least 6–8 events over the next quarter, spanning:

- **Additional bank stress** (First Republic 2023-05, Credit Suisse 2023-03).
- **Additional accounting/fraud events** (Adani Group 2023-01 short-seller report, Luckin Coffee 2020-04).
- **Additional counterparty contagion** (Archegos 2021-03, Terra/Luna 2022-05).
- **Non-Anglophone events** (as coverage-domain support broadens).

### 5.3 Lookahead

Every observation carries a `seendate` from GDELT, and the harness sorts observations chronologically before replay. The `run_backtest.py` harness measures `lead_time_hours = realized_event_date − first_flag_at`; any observation whose GDELT `seendate` is on or after the realized event date can only produce a non-positive lead time and is not counted in the median. A pinned test (`test_time_safety_lead_time_never_negative`) enforces this.

The one exception is the pinned regulatory anchors in `ground_truth.primary_sources`, which are inserted at a computed offset from the realized event date. That offset is a small negative shift (regulatory docs typically post the day of or the trading day before the market event). If a future reader disputes the offset, the harness computes recall and lead time from GDELT news observations alone — removing the regulatory anchors from the fixture does not change the SVB recall (still 5/5) or the median lead (2.34 → 2.34).

### 5.4 Selection risk in the domain whitelist

The primary-financial-news whitelist was fixed before the fixtures were built. It was **not** tuned after seeing per-event results. That said, a reader could reasonably object that the whitelist itself is a selection: adding aggregator wires would raise both recall (more coverage) and false positives (more noise). We chose "high-confidence primary sources" over "coverage" — the same choice a professional analyst makes when deciding which desk to trust.

---

## 6. Reproduction

The full stack is Apache-2.0 licensed and reproducible from the repository at `https://github.com/zariffromlatif/Aetherius` (branch `main`).

```bash
# 1. Install dependencies (pinned in requirements.txt).
pip install -r requirements.txt

# 2. Run the three-event backtest suite.
pytest aetherius/tests/test_backtest_harness.py -v

# 3. Reproduce a single event's metrics.
python simulations/backtest/run_backtest.py --event svb-2023
python simulations/backtest/run_backtest.py --event wirecard-2020
python simulations/backtest/run_backtest.py --event ftx-2022

# 4. (Optional) Rebuild an event's observations.jsonl from GDELT DOC 2.0.
#    Requires internet; per-target responses are cached under _gdelt_cache/.
python simulations/backtest/build_fixture.py --event svb-2023
```

All watchlists, ground-truth files, observation corpora, and pinned tests are committed. Every source URL in every observation is real and independently verifiable.

---

## 7. What this paper is not

This paper is a detection-timing artifact. It is not:

- **A pitch** — pricing, engagement scope, and commercial terms are elsewhere.
- **A trading strategy** — return generation requires a whole layer of position sizing, execution, and risk management that this pipeline does not do.
- **A causal claim** — the fact that the pipeline flagged five regional banks in the SVB window before the FDIC receivership date does not mean the pipeline "predicted" the receivership. Deposit-run narratives on a wire two days before a receivership are a real signal, but they are downstream of the underlying balance-sheet stress, not upstream.
- **A guarantee** — the same pipeline could easily miss a future event that unfolds in a mode we have not yet seen.

The honest use of the artifact is: it demonstrates that a small, deterministic, human-supervised pipeline can be constructed today, on real primary-source news, that would have raised elevated / high flags on nine names across three different modern crises before the realized events, without firing on three unrelated controls. That is a lower-bar and more testable claim than "AI predicts crashes." It is the claim on which Aetherius' engagements rest.

---

## Appendix A — Watchlist definitions

Full watchlist JSON for each event is at `simulations/backtest/events/<event-id>/watchlist.json`. Summarized here:

**SVB-2023 (`simulations/backtest/events/svb-2023/`)**
- SIVB (critical), SBNY (high), FRC (high), WAL (normal), PACW (normal), MSFT (control)

**Wirecard-2020 (`simulations/backtest/events/wirecard-2020/`)**
- WDI (critical), DTE (control)

**FTX-2022 (`simulations/backtest/events/ftx-2022/`)**
- SI (critical), COIN (high), SBNY (normal), MSFT (control)

## Appendix B — Ground-truth definitions

Realized event dates and expected minimum severities per affected name are pinned in each event's `ground_truth.json`. Summary:

| Event | Ticker | Realized event date | Expected min severity |
|---|---|---|---|
| SVB-2023 | SIVB | 2023-03-10 (FDIC receivership) | high |
| SVB-2023 | SBNY | 2023-03-12 (NY DFS closure) | elevated |
| SVB-2023 | FRC | 2023-03-13 (deposit flight) | elevated |
| SVB-2023 | WAL | 2023-03-13 (drawdown) | elevated |
| SVB-2023 | PACW | 2023-03-13 (drawdown) | elevated |
| Wirecard-2020 | WDI | 2020-06-25 (insolvency filing) | high |
| FTX-2022 | SI | 2022-11-11 (FTX Chapter 11) | high |
| FTX-2022 | COIN | 2022-11-11 | elevated |
| FTX-2022 | SBNY | 2022-11-11 | elevated |

## Appendix C — Primary source references

**SVB-2023.**
- SEC EDGAR, SVB Financial Group (CIK 0000719739), Form 8-K filed 2023-03-08.
- FDIC press release pr23016 (2023-03-10): closure of Silicon Valley Bank and appointment of FDIC as receiver.
- Federal Reserve joint statement (2023-03-12) on regional-bank facilities.

**Wirecard-2020.**
- Wirecard AG ad-hoc release, 2020-06-18: €1.9B cash "likely does not exist."
- BaFin statements, 2020-06-18 to 2020-06-25.
- Wirecard AG insolvency filing at Munich District Court, 2020-06-25.

**FTX-2022.**
- CoinDesk Alameda balance-sheet leak, 2022-11-02.
- Changpeng Zhao (Binance) tweet announcing FTT sale, 2022-11-06.
- FTX Chapter 11 bankruptcy filing (D. Del.), 2022-11-11.
- Silvergate Capital 8-K filings, November 2022.

Every news observation in every fixture also carries its own primary-source URL in the `source_url` field.

## Appendix D — Reproducibility manifest

- **Repository:** open-sourced under Apache-2.0.
- **Test coverage:** 44 unit / integration tests pass on the reference commit, of which 12 pin backtest behavior.
- **Determinism:** all scoring weights are compile-time constants. No learned parameters. Rerunning the same fixture at the same commit produces bit-identical metrics.
- **Rebuild-from-source:** the observations corpus can be regenerated end-to-end from GDELT DOC 2.0 via `simulations/backtest/build_fixture.py`. Cached responses under `_gdelt_cache/` make partial reruns free.

---

*Aetherius Risk Intelligence provides research and risk-monitoring services. Analysis is not investment advice and is not a recommendation to buy, sell, or hold any security. Nothing herein is a forecast or a guarantee of any outcome.*
