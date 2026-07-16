# Website Deploy Guide

**Goal:** get `aetheriusresearch.tech` (or your chosen domain) live, secure, fast, and shareable on LinkedIn / Twitter with a proper OG preview — in one afternoon.

**Stack:** Cloudflare (registrar + Pages + DNS). All free. Everything is production-grade and used by real financial-services firms.

---

## Prerequisites

- The two files in `landing_page/`: `index.html`, `style.css`
- The two brand assets in `landing_page/`: `favicon.svg`, `og.svg`
- A credit card (used only if you register the domain)
- A GitHub account with the repo pushed (public)
- ~90 minutes of focused time

---

## Step 1 — Convert `og.svg` to `og.png` (10 min)

LinkedIn and Twitter do NOT reliably render SVG social previews. You need a **1200×630 PNG**.

Pick the easiest option:

### Option A — Chrome / Edge / Firefox (no install)

1. Open `landing_page/og.svg` in your browser.
2. **Chrome:** right-click the image area → *Save as…* → save `og.png`.
   - If that saves as SVG, use option B or C instead.
3. Verify the resulting PNG is exactly 1200×630 (right-click → Properties on Windows, ⌘I on macOS).
4. Place the PNG at `landing_page/og.png`.

### Option B — CloudConvert (browser, free, no login for small files)

1. Go to [cloudconvert.com/svg-to-png](https://cloudconvert.com/svg-to-png)
2. Upload `og.svg`
3. Click the wrench icon → set **Width: 1200, Height: 630, Fit: max**
4. Convert → download → save as `landing_page/og.png`

### Option C — `svgexport` (Node one-liner if you have Node installed)

```bash
npm install -g svgexport
svgexport landing_page/og.svg landing_page/og.png 1200:630
```

**Sanity check:** on Windows/macOS/Linux, open the PNG in an image viewer. It should show the ink-navy card with the wordmark on the left and the 9/9 · 2.5d · 0 metric card on the right. If it looks broken (wrong fonts, cropped), redo — a broken OG preview is worse than none.

---

## Step 2 — You already have the domain (`aetheriusresearch.tech` at tech.domains)

Since the domain is registered at **tech.domains** (not Cloudflare Registrar), you have two viable paths for connecting it to Cloudflare Pages. Pick one:

### Path A (recommended) — Move DNS to Cloudflare, keep the registrar

You do NOT need to transfer the domain. You only change **which nameservers answer DNS queries** for it. This is free, non-destructive, and makes Steps 3–4 below work exactly as written.

1. Sign up at [cloudflare.com](https://cloudflare.com) with a real email. Enable 2FA immediately.
2. Cloudflare dashboard → **+ Add site** → enter `aetheriusresearch.tech` → pick the **Free** plan.
3. Cloudflare will import any existing DNS records automatically. Verify the list before continuing (usually empty for a new domain).
4. Cloudflare will show you two nameservers, e.g. `nyla.ns.cloudflare.com` and `theo.ns.cloudflare.com`. **Copy both.**
5. Log into **tech.domains** → your domain's DNS / Nameserver settings → replace the default nameservers with the two Cloudflare ones → save.
6. Wait 5–30 minutes for propagation. Cloudflare will email you when it detects the change. From that point, Cloudflare controls DNS but the domain is still owned at tech.domains.

### Path B (alternative) — Keep DNS at tech.domains, use CNAME/A records only

Works but has more moving parts: you'd add CNAME records manually every time Cloudflare Pages gives you a new endpoint. Not recommended unless Path A blocks you.

**Do Path A.** Then continue to Step 3.

---

## One-line reminder before Step 3

Push the four `landing_page/` files to the public GitHub repo now if you haven't already:

```bash
git add landing_page/
git commit -m "Landing page: production-ready site + OG image"
git push
```

Cloudflare Pages only sees what's on GitHub.

---

## Step 3 — Deploy the site via Cloudflare Pages (30 min)

Cloudflare Pages will pull directly from your GitHub repo, rebuild on every push, and serve with automatic HTTPS.

### 3a — Log into Cloudflare and open Pages

1. From the Cloudflare dashboard, left sidebar → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**.
2. Authorize Cloudflare to access your GitHub account (grant it access to the Aetherius repo only, not all repos).

### 3b — Configure the build

1. Select your repo. Click **Begin setup**.
2. Set up:
   - **Project name:** `aetherius-landing`
   - **Production branch:** `main`
   - **Framework preset:** *None*
   - **Build command:** *(leave empty)*
   - **Build output directory:** `landing_page`
3. Click **Save and Deploy**.

Cloudflare will build in ~30 seconds and give you a `aetherius-landing.pages.dev` URL. **Open it now on your phone AND your laptop.** Verify:

- Hero + track record table render correctly on both
- Fonts load (Playfair Display in headlines, Inter in body)
- Mobile hamburger menu opens
- All links go to the right places (working paper, GitHub repo, mailto)
- No console errors (open DevTools → Console)

### 3c — Point your domain at Pages

1. In Cloudflare Pages → your project → **Custom domains** → **Set up a custom domain**.
2. Type `aetheriusresearch.tech` (or whatever you bought).
3. Cloudflare will detect that you own the domain and provision an SSL certificate automatically. Wait ~2 minutes.
4. Also add `www.aetheriusresearch.tech` — Cloudflare creates a redirect to the apex automatically.

**Test on your phone:** visit `https://aetheriusresearch.tech`. It should load in under 2 seconds. HTTPS lock icon should be present. If it doesn't work in 5 minutes, DNS is still propagating — grab a coffee and try again in 10.

---

## Step 4 — Verify OG previews (15 min)

This is the single most-skipped step, and it's the one that makes your LinkedIn post look professional or amateur.

### 4a — LinkedIn Post Inspector

1. Go to [linkedin.com/post-inspector](https://www.linkedin.com/post-inspector/)
2. Paste `https://aetheriusresearch.tech/`
3. Click **Inspect**
4. You should see:
   - **Title:** *Aetherius Risk Intelligence · Backtest-Validated Downside-Risk Screens for Concentrated Public-Equity Books*
   - **Description:** *9 of 9 affected names detected before the realized event across SVB, Wirecard, and FTX...*
   - **Image:** the OG preview PNG with the wordmark + metric card
5. If the image doesn't appear: (a) verify `og.png` is actually at `https://aetheriusresearch.tech/og.png` in a browser, (b) if it's there but LinkedIn shows nothing, click **Refresh** in the inspector.

### 4b — Twitter Card Validator

1. Go to [cards-dev.twitter.com/validator](https://cards-dev.twitter.com/validator) (still works even after Twitter → X)
2. Paste your URL, click **Preview card**
3. Same fields should appear. Card type should show as **summary_large_image**.

### 4c — Slack/iMessage smoke test

- Send yourself the URL in Slack or iMessage. The unfurl preview should match what LinkedIn showed.

**If any preview is broken:** the two most common causes are (a) `og.png` returning 404 (Cloudflare Pages needs a full redeploy — push any tiny change to trigger it), (b) meta tag `og:image` still pointing at the old URL (verify `index.html` line 22).

---

## Step 5 — Meta URLs (already done)

The `<link rel="canonical">`, `og:url`, `og:image`, and `twitter:image` tags in `index.html` are already set to `https://aetheriusresearch.tech/`. No action required.

If you later migrate to a `.com`, update these four lines in `index.html`:

- Line 11: `<link rel="canonical" href="https://YOUR-DOMAIN/">`
- Line 13: `<meta property="og:url" content="https://YOUR-DOMAIN/">`
- Line 17: `<meta property="og:image" content="https://YOUR-DOMAIN/og.png">`
- Line 23: `<meta name="twitter:image" content="https://YOUR-DOMAIN/og.png">`

Commit + push. Cloudflare redeploys automatically in ~30 seconds.

---

## Step 6 — Update GitHub links (5 min)

The site currently has three URLs pointing at `github.com/zariffromlatif/aetherius`. If your GitHub username / repo name is different, update these in `landing_page/index.html`:

- Search for `github.com/zariffromlatif/aetherius`
- Replace with your real repo URL
- Do it in **all four** places: the hero "audit the repository" link, the paper section's two buttons, the evidence-strip cell, and the footer's contact block

Commit + push.

---

## Step 7 — Basic analytics (10 min, optional but recommended)

You need to know if outreach is landing traffic on the site. Cloudflare Web Analytics is free, privacy-friendly, and needs no cookie banner.

1. Cloudflare dashboard → **Analytics & Logs** → **Web Analytics** → **Add a site**
2. Add your domain
3. Copy the beacon `<script>` snippet
4. Add it to `landing_page/index.html` immediately before `</body>` (line ~220)
5. Commit + push

From now on, you'll see daily visitor counts, referrers (which LinkedIn/Substack posts converted), and geography — none of it invasive to visitors, all of it useful to you.

---

## Step 8 — Rate the result honestly (5 min)

Before you send a single outreach message, open the site on:

- Your laptop (Chrome, at 100% zoom)
- Your phone (Safari or Chrome, portrait)
- Your phone rotated to landscape
- A friend's laptop, if possible

For each surface, ask yourself:

- [ ] Does the first thing I see make me want to keep reading? (If not: the hero copy is wrong.)
- [ ] Do the numbers in the hero data card look like they belong in a research paper? (They should.)
- [ ] Would a family-office CIO think "this is a real firm" or "this is a side project"? (If side-project: which specific element gives it away?)
- [ ] Do all three CTA buttons in the hero + footer actually work?
- [ ] Does the mobile hamburger menu open smoothly?
- [ ] Is the mailto pre-filled with a useful subject/body when you tap "Request an Analyst Consultation"?

Fix anything that fails the sniff test before Step 9.

---

## Step 9 — Publish (0 min — it's already live)

Nothing to do. The site is production.

The next actions are all in your private first-dollar playbook (kept locally, not in this public repo):

1. Step 2 there — publish the working paper on GitHub, Substack, LinkedIn (over 3 days)
2. Step 3 — build the 40-target outreach list
3. Step 4 — send the first 20 personalized outbound messages

---

## Common gotchas

**"My domain doesn't resolve after 15 minutes."** DNS propagation can take up to an hour but usually finishes in 5. Verify (a) Cloudflare shows the domain as **Active** in the Domains page, (b) `nslookup aetheriusresearch.tech` from your terminal returns a Cloudflare IP (starts with `104.` or `172.`).

**"Cloudflare says my SSL isn't ready."** In Cloudflare → your domain → **SSL/TLS** → set encryption mode to **Full (strict)**. Wait 5 minutes.

**"LinkedIn preview shows old title/image after I updated the site."** LinkedIn caches previews for 7 days. Re-scrape via the [Post Inspector](https://www.linkedin.com/post-inspector/) — click **Inspect** twice; the second click forces a refresh.

**"The OG PNG looks pixelated on retina displays."** The 1200×630 spec is correct for LinkedIn/Twitter; both display it downscaled. If it still looks bad, you probably exported it at low DPI — redo Step 1 with an explicit width parameter.

**"My hero data table wraps badly on mobile."** Should not happen with the current CSS. If it does, tell me and I'll fix the `data-table` mobile styling — do not manually edit until you've reported it.

**"Someone can find my email in the source code."** Yes — this is deliberate. A mailto in a static site is the correct trust signal at this stage. Once you have 3+ retainer clients, switch to a form (Formspree, Basin) to reduce spam.

---

## The 20-second review the site now passes

A cold visitor lands on the page. Their first 20 seconds:

1. **~1s** — Sees the wordmark and the "Vol. I · Downside-Risk Intelligence · Est. 2026" eyebrow. Reads institutional, not startup.
2. **~3s** — Reads the hero headline: *"Backtest-validated screens for concentrated public-equity books."* Understands what you sell.
3. **~7s** — Eye moves to the hero data card. Sees the three-event track record with real numbers. Registers: "these are specific claims that could be false-verified."
4. **~12s** — Reads the open-source line: *"Every claim in every deck links to a primary source. The full pipeline is open source, Apache-2.0. Audit the repository."* Understands the credibility asymmetry.
5. **~18s** — Sees the "Read the working paper" button. Clicks either that OR "Request a Target Deck."

If they click either, you've won the visit. Everything else on the page reinforces one of those two decisions.

---

## When to revise the site

**Don't revise for the first 20 outreach messages.** Watch the analytics + reply data. Only revise if a specific pattern emerges — e.g. every reply says "I wasn't sure what you actually charge" → tighten the engagement tiers copy. Do not revise on gut feel.

After the first paid engagement, add: (a) an anonymized case-study section between § III and § IV, (b) a testimonial line above the trust banner. Not before.
