# First-Dollar Playbook

**How to go from "the code and deliverable are done" to the first paid engagement, step-by-step.**

Written 2026-07-11. Grounded in `01_code_audit.md`, `03_market_research.md`, `04_recommendation.md`, and the actual code state after items 1–8 shipped. Every step below is either (a) a concrete task with a checkbox, (b) a copy-paste-ready template, or (c) a rule with the "why" attached.

---

## 0. Read this first

**You are not doing "AI research sales." You are running a boutique consulting shop of one.**

The code is a force multiplier that turns a 3-week engagement into a 5-day one. It is not the product. The product is: **"I will look at your concentrated position, tell you what public evidence would already fire an elevated flag on it, and give you a written invalidation-marker rubric — in 5–7 business days for $500–$3,000."**

**The one artifact that does 80% of the sales work: the working paper at `docs/working_paper/detection_timing_backtest_2026-07.md`.** Everything below assumes you've published it (Step 2). If it isn't published, none of the outbound will convert.

**Realistic timeline to first paid dollar:** 4–8 weeks from today with warm intros, 8–14 weeks with cold-only. Do not commit to numbers tighter than that publicly.

---

## 1. Prerequisites (do these before any outreach)

Check each. If any is unchecked, do it before Step 2.

- [x] `simulations/backtest/events/{svb-2023,wirecard-2020,ftx-2022}/` — real GDELT-backed fixtures, all pinned, all passing
- [x] `docs/working_paper/detection_timing_backtest_2026-07.md` — written, structured, honest
- [x] `scripts/build_deck.py` — CLI works end-to-end on the SVB fixture
- [x] `aetherius/app/services/reporting/target_stress_test.py` + template + gates
- [x] 75 tests passing
- [x] `landing_page/index.html` — numbers match the working paper (2.5d median, 9/9, 0/3 FP)
- [ ] **Repo is public on GitHub** — buyers WILL clone it. If it's private, half the pitch (the "everything is open, audit us in 15 minutes" claim) evaporates.
- [ ] **Personal LinkedIn profile matches the pitch** — one-line: *"Backtest-validated downside-risk screens for concentrated public-equity books."* Not "founder" or "AI." Add the working-paper link as a featured post as soon as Step 2 is done.
- [ ] **A dedicated Gmail / ProtonMail alias** for engagements — `zarif.latif.biz@gmail.com` already on the landing page. Confirm you actually check it.
- [ ] **Payment rail decided** — pick ONE for the first three engagements. Recommendation ordering below.
- [ ] **A boilerplate engagement letter drafted** (see §7). One page, plain language, no lawyer needed for a $500–$3k memo.

### Payment rail (pick ONE, do not decision-fatigue this)

| Rail | Setup time | Fees | Buyer friction | Recommendation |
|---|---|---|---|---|
| **Stripe Invoicing** | ~1 hour | 2.9% + $0.30 | Zero. Pays with card. | **Default.** Do this first. Handles US, UK, EU buyers. |
| Wise Business | 1–2 days KYC | ~0.5% FX | Low. Wire from any country. | Backup for non-Stripe geographies. |
| PayPal Invoice | ~10 min | 3.5%+ | Low but low-status for finance buyers | Avoid unless the buyer insists. |
| Direct bank wire | Days | Low | High friction on both sides | Only for the $3k+ engagements after the retainer conversation. |

---

## 2. Publish the working paper (this week)

**Rule:** the paper is what earns you the right to be replied to. Publish it on 3 surfaces, in this order, over ~3 days.

### Day 1 — GitHub

- Ensure the repo is public.
- The paper is already at `docs/working_paper/detection_timing_backtest_2026-07.md`. GitHub renders it natively. That URL is your canonical link.
- Pin the repo on your GitHub profile.

### Day 2 — Substack

- Create a Substack under your own name (not "Aetherius"). Solo research shops read better as a person.
- **Free tier only** for month 1. No paywall discussion yet.
- Post title: *"A backtest-validated downside-risk screen: 9 of 9 detections across SVB, Wirecard, and FTX, published open with the code."*
- Paste the entire Markdown from the paper. It will render correctly.
- Enable "recommendations" and follow ~30 finance / research Substacks so yours appears in their reader.

### Day 3 — LinkedIn

- Post a single carousel or long-form post: 5 paragraphs, headline is the same as the Substack title.
- **Do not link Substack in the post body** — LinkedIn suppresses external links. Put the link in the first comment. This is a standard LinkedIn trick.
- Tag no one. Do not @-notify anyone until you have 20+ organic reactions; the algorithm punishes low-engagement notifications.
- The post's first line is the whole game. Use one of:
  - *"I built and open-sourced a downside-risk screening pipeline, then backtested it against three actual crises. Here are the numbers."*
  - *"9 of 9 affected names flagged before the realized event, across SVB, Wirecard, and FTX. Zero false positives on controls. Full code and paper linked below."*

### Day 4 — X / Twitter (optional but cheap)

- One thread of ~10 tweets summarizing the paper.
- Ends with: *"Full open-source paper + code: [github link]."*
- If you have <500 followers, skip this until Substack has proof of readership.

**Success metric for this week:** ≥ 200 GitHub repo views, ≥ 50 Substack subscribers, ≥ 500 LinkedIn views. Not sales — attention. If you hit those, cold outreach in Step 3 converts materially better.

---

## 3. Identify the first 40 targets

Do NOT try to be systematic for the first cohort. **Cast wide, personal, and small-check-friendly.** Ranked buyer list from the research (see `03_market_research.md`):

### Tier A — highest realistic conversion

1. **Search fund principals / independent sponsors** doing pre-LOI on a public comp.
   - Source: [SearchFunder.com](https://searchfunder.com) directory, StanfordGSB search fund database, Villanova ETA.
   - Look for: principals who have named a target sector publicly and might want a "one-hour readout on the public comp you're pricing against."
2. **Small family-office CIOs** ($100M–$1B AUM).
   - Source: FamilyOfficeExchange member lists (public parts), LinkedIn search for "CIO" + "family office" + <keyword> in your region.
3. **Litigation-finance analysts** at Burford, Bench Walk, and the ~40 smaller shops.
   - Source: [Westfleet Advisors report](https://westfleetadvisors.com) publicly lists most of them.
4. **Small credit funds / ABL lenders** ($50M–$500M).
   - Source: LinkedIn "credit analyst" + "distressed" or "special situations" at boutique names.

### Tier B — only if you get a warm intro

5. Concentrated PMs at single-name activist shops (Kerrisdale, Grizzly, etc.).
6. Mid-market PE associates pre-LOI (only via warm intro — 45–60 day TPRM wall).

**Not addressable this year:** bulge-bracket credit desks, top-10 asset managers, big distressed shops. Reorg/Octus already has them.

### Build the list

Create a spreadsheet with these columns exactly:

```
name | title | firm | linkedin_url | email | tier | segment | notes | first_touch_date | last_touch_date | status
```

- **Statuses:** `new`, `messaged`, `replied`, `booked_call`, `sample_sent`, `verbal_yes`, `invoiced`, `paid`, `no`.
- **Target: 40 rows before you send the first message.** Not 500. Forty personal, curated, "I know why I'm messaging this specific person" rows.

Time budget: 6–8 hours over 2 days. This is the highest-leverage work of the whole project.

---

## 4. The first outreach (weeks 3–4)

**Rule:** you are not selling. You are giving away a sample deck. The paid engagement comes 2–3 conversations later.

### 4.1 Cold LinkedIn message template

Personalize the second sentence per person; keep the rest.

> Hi [Name] —
>
> I built and open-sourced a downside-risk screening pipeline that flagged 9 of 9 affected names across SVB, Wirecard, and FTX before the realized event, with zero false positives on the controls. Full paper + code is here: [github link].
>
> Given [one specific concrete thing about their book / recent post / target sector], I'd like to send you a free 8-page stress-test deck on one ticker of your choice — no strings, no follow-up sequence. Would that be useful?
>
> — Zarif

**Rules for the template:**
- Under 700 characters. LinkedIn truncates longer.
- The specific-thing sentence must be real. If you can't write one for this target, they don't belong in the list.
- "One ticker of your choice" is the hook. It's a ~2-hour offer with a real deliverable on the other end.
- Do NOT attach the paper. Do NOT put a calendar link. Both signal automation and kill reply rate.

### 4.2 Cold email variant (if you have their email, higher conversion than LinkedIn DM)

Subject: **[Ticker of interest]: 8-page downside stress-test, no cost, no follow-up sequence**

> [Name] —
>
> Three-line intro of the paper and open-source repo, same as LinkedIn.
>
> I've been running the pipeline on frozen historical windows — full track record and methodology in the paper linked above. I'd like to build one on a public-equity ticker you actually care about — free, 8 pages, delivered as a PDF in 5 business days — because I'd rather have you critique a real deliverable than take a meeting on hypotheticals.
>
> If useful, just reply with a ticker.
>
> — Zarif

### 4.3 Cadence

- **60 messages per week** across LinkedIn + email combined. Not 200. Personal quality > volume at this stage.
- Message → 4 business day gap → one polite follow-up → done.
- Do **not** send a third touch to a non-responder. Their next data point comes from your Substack posts.

### 4.4 Success math (from `03_market_research.md`)

- LinkedIn reply rate with personalization: **~9%**. So 60 messages/wk → ~5 replies/wk.
- Reply → qualified conversation: **~30%**. So ~1–2 qualified conversations/wk.
- Qualified conversation → "yes, send me a sample deck": **~50%**. So ~1 sample deck/wk after week 3.
- Sample deck → paid engagement: **~10–20%**. So ~1 paid engagement per 5–10 samples sent.

**Realistic first-dollar timing:** first sample deck out by week 4, first paid engagement by week 7–10.

---

## 5. The sample-deck workflow (~4 hours per deck)

When someone replies with a ticker, you have 5 business days.

### Day 0 — 15-minute prep

- Add them to the tracking spreadsheet with status `sample_sent`.
- Send: *"Great. I'll send the deck by [date]. Two clarifiers if you have 30 seconds — (1) any specific counterparties I should map in? (2) what window would be most useful — last 90 days, or a specific past window you want to see the pipeline replay?"*
- Their answer defines the engagement.

### Day 1 — build the deck

Run the CLI. Live mode against real GDELT:

```bash
python scripts/build_deck.py \
  --ticker XYZ --name "XYZ Corp" \
  --sector "Sector" --aliases "Alias1,Alias2" \
  --thesis "One-line honest analyst thesis." \
  --counterparty "TICKER1:Name:relationship:0.6:aliases" \
  --counterparty "TICKER2:Name:relationship:0.5:aliases" \
  --window 2026-04-01:2026-07-01 \
  --live \
  --out out/xyz-sample-deck.html
```

If GDELT is slow, wait it out (the retry ladder handles 429s). This step is **~15 minutes of your time**.

### Day 1–2 — analyst review (the real work)

Open the HTML. For each of the top 8 evidence items:

- [ ] Click the source URL. Confirm the article is real and matches the title.
- [ ] Confirm the entity match is correct (no false positive on a lookalike name).
- [ ] Rewrite the analyst thesis in the exec summary to reflect what you actually see in the evidence — mechanical bullets stay, add one prose paragraph before them.
- [ ] Add engagement-specific invalidation markers (replace or extend the three generic ones).
- [ ] Add a "known limitations for this target" section if the coverage is thin.

This is where your judgment goes. The pipeline surfaced the data; you shape it. **~3 hours of focused work.**

### Day 3 — send

- Open HTML in Chrome/Safari → Print → Save as PDF (Letter, portrait, default margins).
- Rename: `Aetherius_Stress-Test_XYZ_2026-07-14.pdf`.
- Email:

  > Subject: XYZ stress-test deck (as requested)
  >
  > [Name] —
  >
  > Attached. 8 pages. Every claim links to a real primary source. Track record and methodology in the appendix.
  >
  > If this is directionally useful, I'd be happy to do a 20-minute call to walk you through the invalidation markers — no obligation to hire on the other side of that call.
  >
  > — Zarif

### Day 5–7 — the follow-up call

If they book: see §6.

If they don't reply: **one polite follow-up** at day 7 (*"Circling back — did the deck land?"*), then let it sit. Add them to your Substack subscriber prompt if they aren't already.

---

## 6. The first call — pricing conversation

**Rule:** you are not pitching. The deck already pitched. You are qualifying and pricing.

### 6.1 First 5 minutes: their reaction

- *"What worked? What didn't? What would you have wanted to see instead?"*
- Take real notes. The feedback from the first 3 free decks is worth more than the fees on the next 5.

### 6.2 Next 10 minutes: the pricing ask (only if they said something positive)

You do not open with a price. They do. If they don't, you say:

> *"If a paid version of that deck — on a target you're actively underwriting, deeper, with the invalidation-marker rubric extended to your specific thesis — would be useful, engagements typically run **$1,500 for a single-ticker deck delivered in 5 business days**, or **$3,000 for a target + up to three declared counterparties, 8 business days**. Retainer clients (one deck per week, up to 3 names) start at **$2,500/month**."*

**Anchors, from the research:**
- Never open above $3,000 for the first engagement. Boutique CDD floor is $25k; you're deliberately far below because that's the correct positioning for a search fund / small FO buyer.
- Never open below $1,000 for a paid engagement. Below $1k, the buyer feels they're doing you a favor and the whole relationship starts wrong.
- **First engagement anchor: $1,500.** Second-anchor: $2,500 if the first went well. Retainer: $2,500/mo (2–3 names).

### 6.3 Handle the objections

- *"That's cheap — what's the catch?"* → *"There isn't one. I'm building a track record; the price will rise to $3k–$5k per deck once I have five delivered paid engagements. If you engage this quarter, you're locking the current rate."*
- *"How is this different from what my $150k Bloomberg terminal already does?"* → *"Bloomberg gives you the raw feed. This gives you an evidence-scored severity flag and an invalidation-marker rubric on one specific target. That's an hour of analyst work that costs your team more than $1,500."*
- *"Can I see three more sample decks first?"* → *"I can share two more; the third would be paid. Genuine deliverables take real hours; I'm keeping the free-sample count at three total."*

### 6.4 Ask for the yes

End the call with: *"Do you want me to send an engagement letter and invoice today? If we start tomorrow, you have the deliverable by [specific date]."*

Silence works here. Do not fill it.

---

## 7. Engagement letter + invoice

Keep it one page. No lawyer needed. Modeled on how independent analysts operate.

### 7.1 Engagement letter template (copy into a Google Doc)

> **Engagement Letter — Aetherius Risk Intelligence**
>
> Between Zarif Latif ("Aetherius") and [Client Name] ("Client"), dated [date].
>
> **Scope.** Aetherius will produce one (1) Target Stress-Test Deck on the following target: [Ticker] ([Company Name]), analysis window [start] to [end], including declared counterparties: [list or "none"]. The Deck will be 8–12 pages, delivered as a PDF, and will include: a target-and-counterparty dependency map, a scored 90-day evidence timeline with primary-source URLs, invalidation markers, and Aetherius' pinned historical detection track record.
>
> **Delivery.** Within [N] business days of the effective date of this letter.
>
> **Fee.** [$1,500 / $3,000] flat, invoiced on execution. Payable via Stripe Invoicing within 14 days.
>
> **What this is not.** The Deck is a research and risk-monitoring artifact. It is not investment advice, a recommendation to buy or sell any security, or a forecast. The Client is solely responsible for its own investment decisions. Aetherius makes no guarantee that signals raised will materialize into realized events.
>
> **Confidentiality.** Aetherius will not disclose the target or the engagement without written consent. The Client may share the Deck internally without restriction; external redistribution requires Aetherius' written consent.
>
> **IP.** Aetherius retains ownership of the pipeline, template, and methodology. The Client receives a perpetual, non-exclusive license to use the Deck internally.
>
> Signed:
> ______________________ (Zarif Latif, Aetherius)
> ______________________ ([Client rep, title])

### 7.2 Invoice

Stripe Invoicing UI: create → add client email → add line item — *"Target Stress-Test Deck: [Ticker], engagement letter dated [date]"* — set price → attach the signed engagement letter PDF → send.

Payment terms: **Net-14, but delivery on Net-0.** In other words: **you deliver the deck when the invoice is paid, not before.** This is the single most important rule to save you from stiffing. First-time clients pay first; established retainer clients on Net-30 later.

If the client pushes back on pay-first: *"Standard for a new-client single engagement. Retainer clients invoice monthly on Net-30."*

---

## 8. Delivery and post-delivery

### 8.1 Delivery

- Send the PDF via email to the addresses on the engagement letter.
- One-line subject: *"[Ticker] stress-test deck — as engaged"*
- Body: *"Attached. Every claim links to its primary source. I'm available for a 30-minute readout this week if useful — otherwise this is complete."*

### 8.2 The readout call (30 minutes, offered free)

Walk the client through:
- The dependency map + why you scoped it that way
- The 3 highest-severity evidence items and what would invalidate them
- The two things you'd watch next quarter

End the call with **the retainer ask**:

> *"If this was useful, retainer clients get one deck like this per week on any target in a 3-name book, plus updates when new signals cross the elevated threshold. That's $2,500/month, month-to-month, cancel anytime. Interested?"*

Retainer conversion is where the business actually works. **Every paid client gets asked. Every time.**

### 8.3 Post-mortem (do this even when it went well)

Add a row to a `post_mortem.md` file in your private notes:

- What did the client value most? Least?
- What took you longer than expected?
- What would you charge next time?
- What Substack post could you write from this engagement (anonymized)?

The last question compounds — every engagement should produce one Substack post that generates two future leads.

---

## 9. Failure modes and hedges

| Failure mode | Signal | Hedge |
|---|---|---|
| Cold outreach reply rate < 3% after 4 weeks | Fewer than 8 replies from ~200 touches | Rewrite the LinkedIn hook. The first sentence is 80% of reply rate. |
| Sample decks going out but no paid conversions after 5 sent | 5+ decks, 0 paid | You are giving away too much. Cap free samples at 3 total, ever. |
| Client pays and then ghosts on delivery scope | Invoice paid, no answer to scoping email | Deliver what you can with public info. Ship on time. Do not chase. |
| GDELT rate-limits you mid-engagement | Live pull returns nothing | Fall back to a 60-day EDGAR-only window + manual news via Wayback Machine. Ship on the timeline; the deck template already handles thin corpus gracefully. |
| Client asks for something outside scope ("can you also model our full 10-name book?") | Scope creep on first engagement | *"Yes — that's the retainer tier at $2,500/month. Happy to start next week."* Do NOT do it for the flat fee. |
| Someone objects to the "open code" positioning ("why would I pay you if the pipeline is on GitHub?") | Objection at pricing call | *"Because the pipeline is 20% of the work. Scoping the target, curating counterparties, reviewing 30 headlines against invalidation criteria — that's 80%, and I do it in 5 days, not 3 weeks."* |
| First-dollar target month slides past 10 weeks with no yes | 40 messages, 3+ sample decks, 0 paid | Rewrite the sample deck's cover: **the first page must convert alone.** Also: revisit the buyer list — you're probably still targeting Tier B when you should be in Tier A. |

---

## 10. Weekly cadence and success metrics

| Week | Action | Success threshold |
|---|---|---|
| 1 | Publish paper on GitHub, Substack, LinkedIn | ≥ 200 GitHub views, ≥ 50 Substack subs |
| 2 | Build 40-target list; write 20 personalized outreach messages | List complete, first 20 messages sent |
| 3 | Send remaining 20 + 40 more (60/week cadence) | ≥ 5 replies |
| 4 | First 1–2 sample decks out | ≥ 1 sample deck delivered |
| 5 | Continue outreach; second Substack post ("what we saw on X ticker last week") | ≥ 3 sample decks delivered cumulatively |
| 6 | First pricing call | ≥ 1 verbal yes OR clear feedback on why not |
| 7–8 | Send engagement letters + invoices | **First dollar in the account.** |
| 9–12 | Deliver first paid deck; ask for retainer; deliver second paid deck | First retainer verbal / first repeat engagement |

**By week 12: honest floor is $1,500–$4,500 collected. Honest ceiling is $10k–$15k collected + one retainer starting.** Both numbers are from `03_market_research.md` benchmarks applied to this specific plan.

---

## 11. What NOT to do

Copied from the recommendation memo because these are the highest-leverage "don'ts":

- **Do NOT lead cold outreach with PE MDs** — 45–60 day TPRM wall kills the timeline.
- **Do NOT SaaS-ify anything for the first six months.** No login page, no dashboard, no subscription webapp.
- **Do NOT register as an RIA** for at least the first $250k of revenue. Regulatory cost + Form ADV is a distraction below that.
- **Do NOT publish free unattributed short reports** — legal exposure a solo non-US founder can't afford.
- **Do NOT undercut $1,000 per engagement.** Below that the buyer treats you as free.
- **Do NOT deliver before payment on new-client engagements.**
- **Do NOT add features to the CLI or template based on the first client's ask.** Take the note, ship the deck as scoped, evaluate at the retainer conversation.
- **Do NOT scale outreach past 60/week until reply rate is ≥ 5%.** More volume on a broken hook just burns the list.

---

## 12. What to build ONLY after first paid dollar

Do not do any of this before revenue. Every one of them is a rationalization for delaying outreach.

- More backtest events (4th, 5th, etc.) — do it, but on paid time, and pitch it as a companion piece to a retainer.
- Live daily-brief automation — only after two retainer clients ask for it in writing.
- A hosted web dashboard — only if a $10k+ engagement requires it explicitly.
- Additional ingestion adapters (Twitter, Reddit, filings full-text search) — one per validated retainer request, not one per hunch.
- A team member — only after $8k+/month recurring revenue across ≥ 2 clients.

---

## 13. Quick-reference: the first-dollar checklist

Cut this out and put it on your wall.

- [ ] Repo is public. Working paper URL is a clean GitHub link.
- [ ] Substack post live. LinkedIn post live. Track view counts.
- [ ] Payment rail set up (Stripe Invoicing).
- [ ] Engagement letter template in Google Docs, ready to duplicate.
- [ ] 40-target spreadsheet built with real personalization notes per row.
- [ ] Send 60 personalized outbound touches per week.
- [ ] Cap free sample decks at 3 total.
- [ ] First engagement letter goes out at $1,500 flat.
- [ ] Get paid before you deliver.
- [ ] Ask for the retainer on every readout call.
- [ ] Every engagement generates one anonymized Substack post.

---

## Appendix — cross-references

- Buyer segment ranking and pricing anchors: `03_market_research.md`
- Full recommendation memo: `04_recommendation.md`
- Code audit and what actually ships: `01_code_audit.md`
- Realistic revenue band: memory `project-realistic-revenue-band.md`
- Credibility artifact priority (why the working paper is the whole game): memory `project-credibility-artifact-priority.md`
- Working paper Markdown: `docs/working_paper/detection_timing_backtest_2026-07.md`
- Deck CLI: `scripts/build_deck.py`
- Deck data service: `aetherius/app/services/reporting/target_stress_test.py`

*Every step in this playbook is derived from artifacts already in the repository. There is no build work remaining before the first outreach message goes out.*
