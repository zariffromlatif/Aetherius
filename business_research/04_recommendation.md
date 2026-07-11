# Aetherius — Bootstrapped Monetization Recommendation

Written 2026-07-11 by Claude after auditing the codebase (`01_code_audit.md`), the closest large comparable (`02_reorg_octus_comparable.md`), and web research on buyers, pricing, cold-outbound conversion, and TPRM friction (`03_market_research.md`).

---

## TL;DR (read this first)

**Keep the pivot from SaaS. Adjust three things about it, based on evidence:**

1. **Two-track, sequenced, not one.** Track A = paid tiered newsletter (Doomberg / PETITION model) for compounding credibility. Track B = narrow-scope per-target memos ($500–$3,000, not $2,500–$10,000) to small-check buyers who can decide alone. Both run in parallel from day 1; the newsletter is the credibility engine, the memos are the cash engine.
2. **Buyer segment inversion.** Cold outbound to PE MDs will hit a 45–60 day TPRM wall. Target instead: **search funds, small family offices ($100M–$1B AUM), litigation-finance analysts, small credit funds, single-name activists, asset-based lenders**. These are one-decision-maker, P-Card-payable buyers.
3. **Fix the credibility artifact before selling anything.** The SVB "backtest" is a 10-row hand-curated demo that any technical buyer will disqualify in five minutes. Reject-out risk > sales risk right now. Rebuild the backtest against a real historical archive of at least 3 events before the first paid outreach.

**Realistic 12-month band (solo, cold, no rolodex, non-US):** floor ~**$15k**, ceiling ~**$120k**. The pivot memo's "$60k–$400k" ceiling is aspirational — cold conversion math doesn't support it.

---

## Where I disagree with the current stated plan

| Current plan | What research says | Revised |
|---|---|---|
| $2,500–$10,000 per Stress-Test Deck | Boutique CDD floor is $25k; below that price your buyer is NOT a PE MD | **$500–$3,000 per memo**, small-check buyers |
| Buyers = PE / distressed / family office / activist / lit-fin (all 5) | PE has TPRM wall; big distressed uses Reorg; large family offices too | **Rank: search funds > small FOs > lit-fin > small credit > single-name activists** |
| Weeks 1–2: rewrite landing + add Wirecard/crypto backtests | Right list, wrong order — the backtest is the credibility bottleneck | **Do the backtest rebuild FIRST**, before landing rewrite |
| Weeks 3–4: 10 free sample decks + LinkedIn DM 200 targets | 200 targets is too few. Conversion math needs 5,000+ touches/yr | **Warm-up: 3 free sample decks to warm intros, THEN cold at scale** |
| First $3–5k/mo retainer weeks 9–12 | Retainer requires a proof engagement first; timing is right, ACV low | **Retainer target $1.5–3k/mo, single family office** |
| Revenue: $10–25k month 3, $60–150k base yr 1 | Cold benchmarks don't support this | **$3–8k month 3, $15–60k base yr 1** |

**The pivot memo is still directionally correct — the deliverable, the timing rhythm, and the anti-causal framing are all right.** The revisions above are calibrations, not a re-pivot.

---

## The recommended 12-week concrete plan (revised)

### Weeks 1–3 — Fix the credibility artifact
**Goal:** replace the 10-row hand-curated SVB fixture with something a skeptical quant can't dismiss.
- **Rebuild SVB fixture from GDELT / Common Crawl / Wayback archives** — pull every Reuters/Bloomberg/FT/CNBC headline mentioning regional banks between 2023-02-01 and 2023-03-13 (not just SIVB). Yields ~300–1,000 real observations, not 10 curated ones.
- **Add 2 more events with the same discipline:** Wirecard collapse (2020-06), FTX collapse (2022-11). Each proves the pipeline on a different failure mode (accounting fraud, counterparty run) and lets you claim "3 crises, 3× 100% recall, 3× 0 FP on control" honestly.
- **Delete or move to `archive/`:** `core/causal_brain.py`, `core/response_engine.py`, `orchestrator.py`, `sensory_core.py`. Any technical buyer reading the repo currently sees hardcoded Discord/AWS scaffolding and disqualifies. This is the highest-leverage 30 minutes of work in the plan.
- **Ship one primary-news adapter** (GDELT is free and easiest — no API key, no rate limit worth mentioning). EDGAR-only ingestion cannot recreate on a real target what the demo "detected."

### Weeks 4–5 — Build the deliverable that doesn't exist yet
**Goal:** actual `services/reporting/target_stress_test.py`.
- **Deck template** (`aetherius/app/templates/pdf/target_stress_test.html`): cover, thesis, dependency map, 90-day timeline, top-5 severity-scored evidence, invalidation markers, historical detection track record on structurally similar names, disclaimer. 8–12 pages.
- **Manual dossier builder**: input = ticker + counterparty list + timeframe. Output = deck bytes. Human-in-the-loop (analyst reviews, edits, ships).
- **Landing page rewrite** (already partially done): keep the current version — it's honest, on-brand, and the SVB numbers section becomes true after the week 1–3 rebuild.

### Weeks 6–7 — Warm intros first, then cold
- **3 free sample decks** to warm-network contacts (search fund friends, ex-classmates in small credit, one family-office CIO if any warm door exists). Purpose: get testimonials/logos and shake out deck defects.
- **Publish the SVB + Wirecard + FTX backtest as a working paper** on your personal Substack or GitHub Pages. Post it to r/finance, r/SecurityAnalysis, Hacker News, Fintwit. Aim for 500–2,000 reads. This is the paid-newsletter seed.
- **Start the Substack**: free tier from day 1. One post/week. Topics: named-position teardowns, methodology explainers, "what would our pipeline have flagged on X" retrospectives. This is a **12-month audience-building play, not a 12-week revenue play** — do it now anyway.

### Weeks 8–12 — Cold outbound to the corrected buyer list
- **1,500 cold touches** across LinkedIn + email in weeks 8–12 (300/wk = 60/day, hard but doable). Segmentation:
  - 500 to search funds (Searchfunder.com database)
  - 400 to small family offices (Preqin, family-office directories)
  - 300 to litigation-finance analysts (Burford, Bench Walk, small shops on LinkedIn)
  - 200 to ABL / factoring shops
  - 100 to single-name activists
- **Conversion math at benchmarks** (5% reply, 30% qualified, 20% close on qualified): ~4–5 paid engagements at $1,500–$2,500 = **$6–12k by week 12**.
- **Retainer conversion:** offer the first family office a "weekly 1-page brief on your top 5 positions" at $1,500–$3,000/mo. Small check, low-friction.

---

## Where the money actually comes from in year 1

| Revenue line | Realistic yr-1 range | Effort profile |
|---|---|---|
| Per-target memos ($500–$3,000) | 10–25 sold = **$10–50k** | Sales-heavy, per-engagement labor |
| Small retainer ($1,500–$3,000/mo × 1–3 clients) | 4–10 client-months = **$6–30k** | Sales-heavy upfront, low delivery labor |
| Substack paid tier ($15/mo, first 100–300 subs) | Late-year only = **$0–15k** | Content-heavy, compounds into yr 2 |
| Paid research reports (one-off) or Pro tier ($500–$1,200) | 5–20 sold = **$3–20k** | Content-heavy, requires audience |
| **Total honest band** | **$15k–$120k** | |

Year 2 is where either path compounds. Substack subscriber curves and retainer stacking both work exponentially once you cross ~200 paid subs or ~5 retainers.

---

## What NOT to do (evidence-based)

- **Do NOT chase PE pre-LOI CDD as a primary buyer** unless you have a warm intro. The 45–60 day TPRM onboarding kills the timeline, and $2,500 undercuts CDD pricing enough that you register as "not a real vendor" to the buyer.
- **Do NOT go SaaS / subscription-only.** You already ruled this out for the right reasons (SOC 2, procurement). Don't revisit.
- **Do NOT register as an RIA in year 1.** Regulatory cost + Form ADV is a distraction below $250k ARR. The Substack model dodges this cleanly by publishing generalized commentary rather than personalized advice.
- **Do NOT try to become Muddy Waters / Culper / Kerrisdale.** They run their own book. That is a hedge-fund launch, not a bootstrapped services business.
- **Do NOT sell to bulge-bracket or top-10 asset managers.** Reorg/Octus already has 100% penetration ([Businesswire](https://www.businesswire.com/news/home/20241029189151/en/Reorg-Rebrands-to-Octus)).
- **Do NOT publish free unattributed short reports.** Legal exposure (defamation, market manipulation) is not something a solo, non-US founder can afford to litigate.

---

## The one bet that changes everything

**A rigorous 3-event backtest (SVB + Wirecard + FTX) built on real archives, published as an open working paper, is the single artifact that unlocks all three revenue paths above.**

- It's what turns a Substack post into "I saw the Doomberg guy on Forward Guidance."
- It's what turns a cold LinkedIn message into a booked call.
- It's what lets you charge $2,500 instead of $500.
- It's what makes a family-office CIO say "OK, walk me through what you'd flag on my 5 largest positions."

Everything else in the plan is either standard consulting execution or standard newsletter mechanics. **The credibility artifact is the moat, and it's the one thing that isn't real yet.** Weeks 1–3 are the whole ballgame.

---

## Decision the founder must make now

Two forks, pick one:

**Fork A — Ship revenue fast, compound audience slowly.** Spend weeks 1–5 on backtest + deck + landing, weeks 6–12 on cold outbound to search funds and small FOs. Target $10–30k by year-end. Substack is a side channel.

**Fork B — Build the audience asset first, monetize slower but bigger.** Spend weeks 1–3 on backtest, weeks 4–12 on 12 substantial Substack posts + podcast appearances, paywall in month 4–6. Target $5–20k by year-end but with 500–1,500 paid subs by month 12 → $60–200k run-rate entering year 2.

**My recommendation: Fork A.** The founder has ingestion + scoring + delivery code already; the marginal effort to ship the deliverable is < 3 weeks. Fork B is the higher long-run EV but requires content-writing endurance the current codebase isn't set up to support, and burns runway before revenue. Do Fork A, run Substack in parallel at low intensity, and reassess in month 6 based on which channel is actually pulling.

---

## Immediate next actions (this week)

1. **Delete or archive** `core/causal_brain.py`, `core/response_engine.py`, `orchestrator.py`, `sensory_core.py`. (30 min.)
2. **Sketch the GDELT-based backtest rebuild plan**: pull filter, event windows, ground truth definitions, control names. (2 hrs.)
3. **Draft the deck template outline** (8-page skeleton with placeholder sections). (2 hrs.)
4. **Draft one Substack post**: "How I built a downside-risk screen that flagged 5/5 regional banks 3–6 days before SVB failed — full methodology and open code." Ship it. (4 hrs.)
5. **List 20 warm-network contacts** who might refer to a small FO / search fund / small credit shop. (1 hr.)

That's a single week of work with clear deliverables. Report back on any friction.
