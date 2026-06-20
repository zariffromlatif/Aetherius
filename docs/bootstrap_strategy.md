# Aetherius — Bootstrap Strategy & 90-Day Plan

> Internal strategy doc. Honest, not marketing. Written 2026-06-21.
> Situation assumed: **$0 capital, technical founder, not a finance insider, productizing the risk-brief service.**

---

## 1. The one hard truth this plan is built around

You have built a **production-shaped, compliance-grade pipeline for human-supervised risk briefings**. That part is genuinely good. But:

- The "causal world-model / AI that predicts risk" is **not real yet** (fixed 3-node graph + an LLM asked to invent scores). Do not sell it as predictive alpha.
- You are **not a finance insider** and have **no buy-side network**. So the README's stated buyer — "small hedge funds and family offices" — is the *hardest possible first customer* for you: they distrust outsiders, demand track record, and buy on relationships you don't have.

**Conclusion:** Win by selling a *reliable outcome to a reachable buyer*, using the tooling to make you fast — not by selling "AI alpha" to funds you can't get a meeting with. The product is **"a trustworthy, evidence-linked downside-risk brief, delivered like clockwork, that a busy investor reads in 3 minutes."** The AI is an assistant that makes *you* fast. That is the whole game for the first 6 months.

---

## 2. Positioning

**What we say we are:** An evidence-linked downside-risk monitoring service. Every claim is traceable to a source; every "elevated/high" alert carries evidence or it doesn't ship; a human reviews before anything goes out.

**What we never say:** "Our AI predicts crashes / generates alpha / forecasts returns." That dies on the first technical question and is also legally dangerous (see §8).

**Why we're different (and these are *true* today):**
- Evidence-or-it-doesn't-ship (the quality gates are real).
- Operator-reviewed, fully audited (the review/audit layer is real).
- Anti-hype by construction (uncertainty + invalidation markers on every call).
- Cheap to run (prompt cache + token telemetry → we can price low and still profit).

---

## 3. Who we actually sell to first (reachable, not ideal-on-paper)

Ranked by *your ability to reach and close them with zero finance network*:

1. **Self-directed serious retail / "FinTwit"-adjacent investors & small newsletter operators** who hold 15–40 concentrated names and fear blowups. Reachable via content, Reddit (r/investing, r/SecurityAnalysis), Twitter/X, Substack. They pay $30–100/mo and will *talk to you*.
2. **Solo RIAs / small advisory shops** who manage client money but have no research team and live in fear of missing a downgrade/guidance cut on a client holding. Reachable via LinkedIn + cold email. Pay $200–800/mo. **This is the best margin/credibility combo for you.**
3. **Investor-relations / corporate strategy teams** who want to monitor *their own* competitors/suppliers for downside news. Not "investing advice" → far lower legal risk. Pay $500–2k/mo.
4. *(Later, once you have a track record)* family offices / small funds — the original ICP. Earn the right to them; don't start there.

**Pick ONE for the pilot.** Recommendation: **#2 (solo RIAs)** if you can write a decent cold email; **#1 (self-directed investors)** if you'd rather sell via content. Either way, niche down to a *named list of 100 specific people* in week 1.

---

## 4. The offer (concrete)

**"Concierge Downside Brief" pilot:**
- You onboard 15–30 of their holdings/watchlist into the system.
- They get a **weekly** (later daily) brief: top downside signals, each with *why it matters*, *what to watch next*, *what would prove this wrong* (invalidation), and **a source link for every claim**.
- Urgent alert if something material breaks intra-week.
- **You personally review every brief before it sends** (the tool drafts; you approve). This is the "do things that don't scale" core — it's also what makes the output trustworthy while the AI is still weak.

**Pricing for first 10 customers:** "Founding member" $49/mo (retail) or $299/mo (RIA), with the explicit deal: *cheap price in exchange for honest weekly feedback.* Goal of the pilot is **learning + testimonials + a real accuracy track record**, not revenue.

**The trust ladder:** free 2-week pilot → paid founding member → case study/testimonial → referral → raise price for cohort 2.

---

## 5. Build vs. fake vs. fix (what the tooling needs to actually do its job)

You do NOT need the AI to be smart yet. You need the *pipeline* to not embarrass you and to make *you* fast. Priorities:

### Must-fix before any demo (credibility killers)
1. **Entity extraction (THE top fix).** Current logic flags any 2–5-char uppercase token as a ticker (CEO, USD, GDP, FED → "companies"). This destroys trust instantly. Replace with a real **ticker/alias dictionary match** against the watchlist + known securities, with word-boundary matching and a stoplist. *(Starting this in code now.)*
2. **Tenant isolation.** `x_client_scope` is client-supplied → any operator can read any client. Must be server-derived from the operator's allowed clients before a 2nd paying customer exists.
3. **Forage reliability.** Live crawl of Fed/CME/BLS mostly fails and silently falls back to a canned sentence. For the pilot, swap to a small set of *reliable* sources (RSS feeds, an EDGAR filing feed, a news API free tier) so "evidence" is real evidence.

### Should-build during pilot (this is the real product)
4. **A real evidence pipeline:** pull recent news/filings for each watchlist ticker → dedupe → map → draft signal → you review. The *mapping must be precise*, not the *scoring smart*.
5. **An accuracy log:** for every signal you ship, record outcome (was it useful? noisy? too late?) using the existing `ClientFeedback` table. This is how you eventually earn the right to claim a track record — and it's straight out of your own (excellent) `benchmark_spec.md`.

### Explicitly DON'T build yet
- The "causal world-model," graph learning, the shock simulation as a product feature. Keep `core/` as a research sandbox. It's fine as an R&D story; it is not the product.
- Autonomous sending. Human-review gate stays on. It's a feature, not a limitation.

---

## 6. 90-day plan (week by week, solo, $0)

**Weeks 1–2 — Don't-embarrass-yourself + a list**
- Fix entity extraction (#1), tenant isolation (#2), reliable sources (#3).
- Build a named list of 100 target buyers in your chosen ICP.
- Write 1 public "teardown" of a recent stock blowup (e.g. "the 3 signals that preceded X's guidance cut") — proof you can think, generated partly with the tool. This is your top-of-funnel.

**Weeks 3–4 — First pilots (manual, concierge)**
- DM/cold-email the 100. Goal: **3 free 2-week pilots.** Onboard their watchlists.
- Send the first weekly briefs *by hand-reviewing tool output.* Measure how long it takes you. Collect brutal feedback.

**Weeks 5–8 — Tighten the loop**
- Iterate the brief format on real feedback. Get the per-brief review time down (automation only where it saves *you* time).
- Convert ≥1 pilot to a paying founding member. Get 1 testimonial in writing.
- Start the accuracy log; you now have ~4 weeks of real signals to grade.

**Weeks 9–12 — Repeatability**
- 5–10 paying founding members ($300–1,500 MRR is a *real* milestone for a $0 bootstrap).
- Publish a second teardown + your first honest "here's what we caught / here's what we missed" post. Honesty *is* the marketing in finance.
- Only now: decide whether to invest in making the AI scoring actually calibrated (you'll finally have labeled data to do it with).

**Success at day 90 isn't "a startup." It's:** 5–10 people paying you monthly, a written track record, and a clear sense of which buyer pulls hardest. That's a bootstrap base you can compound.

---

## 7. Unit economics (why this works at low price)

- LLM cost per brief is small (your telemetry shows ~400–900 tokens/shock, cache cuts repeats ~80%). A weekly brief for 30 names is cents of compute.
- News/data: start on free tiers (RSS, EDGAR, a free news API). Real data cost only when scaling.
- Your only real cost is **your time per review**, which the tooling is built to shrink. So gross margin is high; the constraint is review hours → that's exactly what to automate, in order of what saves you the most minutes.

---

## 8. Risk & compliance (do not skip — this is finance)

- **You are not giving investment advice.** Frame everything as *information/monitoring*, not "buy/sell." The product surfaces *risks and sources*; the user decides. Your existing banned-language gate ("guaranteed", "must") is the right instinct — keep and expand it.
- Put a clear disclaimer on every brief (the README disclaimer is a good base).
- For RIA customers: they are the regulated party; you're a tool/vendor. Keep it that way — don't take discretion.
- **Never claim performance you haven't measured.** Your `benchmark_spec.md` already forbids this. Live by it; it's also your differentiation.

---

## 9. What would make this fundable later (not now)

If you ever want investors, the asset that matters is **a measured track record**: "we flagged N material downside events a median of X days before the price moved, with a false-positive rate of Y, across Z customer-months." You cannot fake this and you don't have it yet. Everything above is designed to *generate that data as a byproduct of getting paid.* That's the real long game — the code is just the means.

---

## 10. Immediate next action (this session)

Fixing **entity extraction** — the single change that takes the product from "embarrassing in a demo" to "credible." See `aetherius/app/services/entity_mapping/service.py`.
