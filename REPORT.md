# Earning Income with Claude Code — Deep Research Report

*Research date: 18 July 2026 · Currency: EUR · Tailored to: Croatia/EU, part-time, flexible hours*
*Interactive version: open `site/index.html` (sortable/filterable dashboard).*

---

## TL;DR — where to start

**Best overall (easy × money):** Freelance automation & scripting gigs — first money in ~2 weeks, €1,500/mo realistic by month 3–6, and your existing price-tracker project is already the portfolio piece.

**Best fully-automated:** A three-legged stack that reuses one codebase: (1) publish your scrapers as paid **Apify actors**, (2) upgrade the MTG tracker into a **paid arbitrage-alert service**, (3) an **Etsy map-poster generator** (geodesy + automation, ~80% hands-off).

**Best geospatial:** **GIS/Earth Engine freelancing** now (€20–30/hr entry, $50+/hr specialized, fully remote, work as much as you like), building toward an **automated EO-monitoring micro-SaaS** (vineyard/coastal change reports for Croatian clients) as the long-term compounding play.

**Skip:** trading bots (negative expectation, capital risk) and pure programmatic-SEO sites (60% failure rate, Google actively penalizes thin AI pages).

---

## 1. Method

25 income opportunities were researched live (July 2026), each profiled on:

| Metric | Meaning |
|---|---|
| Income €/mo (low–mid–high) | Realistic monthly net-of-platform-fees range after ~6 months of consistent part-time effort |
| First € (days) | Typical time from starting to first payment |
| Hours/week | Ongoing time commitment |
| Skill (1–5) | 1 = anyone with Claude Code + patience · 3 = can review code Claude writes · 5 = specialist |
| Cost (€) | Upfront + first-month tooling (a Claude Pro subscription at ~€20/mo is assumed as the baseline everywhere; Max is $100–200/mo but not needed to start) |
| Automation (%) | Share of the running business that operates without you |
| Risk (1–5) | 1 = almost guaranteed some income · 5 = lottery-like or ToS/legal/capital risk |

**Best Option score** (0–10), computed in `compute_scores.py`, weighting exactly your criterion — *best = easy and makes a lot of money*:

```
total = 0.40·income + 0.30·ease + 0.15·automation + 0.15·low-risk
income = 10·log10(mid €/mo)/log10(20 000)      (log scale, €20k/mo = 10)
ease   = mean(low-skill, fast-first-euro, low-cost components)
```

Change the weights in `compute_scores.py` (or live in the dashboard) if your priorities shift. All raw data + sources: `data/opportunities.json`.

---

## 2. Master ranking (best first)

| # | Opportunity | Category | Income €/mo (mid) | First € | Skill | Auto | Risk | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | Freelance automation & scripting gigs | freelance | 300–4500 (1500) | 10 d | 2/5 | 30% | 2/5 | **7.09** |
| 2 | Etsy/Gumroad digital products factory | automated | 100–3000 (500) | 30 d | 1/5 | 80% | 3/5 | **7.01** |
| 3 | Websites & tools for local Croatian businesses | freelance | 300–2500 (1000) | 21 d | 2/5 | 40% | 2/5 | **6.91** |
| 4 | GIS / Earth Engine / QGIS freelancing | geospatial | 300–3500 (1200) | 14 d | 3/5 | 40% | 2/5 | **6.85** |
| 5 | Technical writing & documentation | freelance | 200–2000 (800) | 10 d | 2/5 | 50% | 3/5 | **6.80** |
| 6 | Google Maps Platform / web-map development | geospatial | 300–3000 (1000) | 21 d | 3/5 | 45% | 2/5 | **6.78** |
| 7 | Sell scrapers & data APIs (Apify/RapidAPI) | automated | 50–3000 (500) | 30 d | 3/5 | 90% | 3/5 | **6.70** |
| 8 | Drone photogrammetry processing (desk-only) | geospatial | 300–3000 (1000) | 30 d | 3/5 | 60% | 3/5 | **6.51** |
| 9 | TCG price-arbitrage alert service (paid) | automated | 50–1500 (400) | 45 d | 3/5 | 90% | 3/5 | **6.42** |
| 10 | AI training / RLHF platforms | freelance | 200–1500 (600) | 7 d | 2/5 | 0% | 2/5 | **6.38** |
| 11 | AI-automation consulting for SMBs | freelance | 500–6000 (2000) | 30 d | 3/5 | 30% | 3/5 | **6.32** |
| 12 | Part-time remote EO/GIS contracting | geospatial | 800–5000 (2000) | 45 d | 4/5 | 20% | 2/5 | **6.24** |
| 13 | Dashcam drive-to-earn (Bee Maps/Hivemapper) | geospatial | 10–200 (50) | 14 d | 1/5 | 95% | 3/5 | **6.16** |
| 14 | Satellite imagery annotation / geo AI data | geospatial | 200–2000 (600) | 14 d | 2/5 | 10% | 3/5 | **6.08** |
| 15 | Sell automation templates (n8n/Make/Actions) | product | 0–1000 (150) | 45 d | 2/5 | 80% | 4/5 | **5.81** |
| 16 | Chrome extension (freemium) | product | 0–2500 (300) | 60 d | 3/5 | 75% | 4/5 | **5.58** |
| 17 | Automated niche newsletter | automated | 0–1500 (200) | 90 d | 2/5 | 85% | 4/5 | **5.48** |
| 18 | Open-source bounties (Algora) | freelance | 0–800 (150) | 30 d | 3/5 | 60% | 4/5 | **5.43** |
| 19 | Niche geospatial micro-SaaS (EO monitoring) | geospatial | 0–5000 (600) | 90 d | 4/5 | 85% | 4/5 | **5.28** |
| 20 | Cross-market card arbitrage (flipping) | automated | 0–1200 (300) | 30 d | 3/5 | 60% | 4/5 | **4.75** |
| 21 | MCP servers & Claude Code plugins | product | 0–1000 (100) | 90 d | 3/5 | 70% | 4/5 | **4.75** |
| 22 | Micro-SaaS (general) | product | 0–8000 (500) | 90 d | 4/5 | 70% | 5/5 | **4.61** |
| 23 | Programmatic SEO / AI content sites | automated | 0–2000 (100) | 120 d | 3/5 | 90% | 5/5 | **4.51** |
| 24 | Geospatial ML competitions | geospatial | 0–3000 (100) | 120 d | 4/5 | 30% | 5/5 | **3.52** |
| 25 | Trading bots / crypto agent economy | automated | 0–500 (0) | 60 d | 4/5 | 95% | 5/5 | **2.01** |

Full profiles with first-steps and source links for every row are in `data/opportunities.json` and browsable in the dashboard. Highlights and context below.

---

## 3. The top tier, explained

### #1 Freelance automation & scripting gigs — score 7.09
Sell small Python automations, scrapers, data-cleaning and API-glue jobs on [Upwork](https://www.upwork.com/hire/web-scrapers/cost/), Fiverr and [Freelancer](https://www.freelancer.com/jobs/claude-code) (which literally has a "Claude Code" jobs category now). Median Python/scraping rate is ~$30/hr ($20–40 typical, $50–100+ top-rated). Realistic arc reported across 2026 sources: €300–1,500 in month one → €2,000–5,000/mo by month 3–6. Claude Code writes ~80% of the code; your job is client communication and QA. **Your unfair advantage: the `pokusaj` tracker is exactly the portfolio piece these clients want to see.** Not automated — but the fastest reliable money here.

### #2 Etsy/Gumroad digital products factory — score 7.01
The easiest automated option: Claude Code builds a generator (e.g. **custom map posters from OSM data** — a proven niche where your cartography taste is the moat), you list 30–50 hyper-specific designs (Croatian coastal towns, islands, hiking areas), Etsy's 95M buyers do the rest. Realistic: €100–500 in month one, €1,000–3,000/mo at 3–6 months with a big catalog. Generic niches are saturated; hyper-specific still works ([2026 guide](https://www.listifyai.net/blog/etsy-digital-downloads-guide-2026)). ~95% margin, ~80% automated after setup.

### #3 Local Croatian business websites — score 6.91
€300–800 per site, each a weekend job with Claude Code, plus €10–30/mo maintenance retainers that stack. Zero international competition, no platform fees, and local trust sells. Boring, reliable, immediate.

### The automated stack (#7 + #9 + #2) — one codebase, three incomes
These three share DNA with what you've already built:

1. **Apify actors** ([partner program](https://apify.com/partners/actor-developers)): port your Scryfall/Cardmarket pipeline into pay-per-result actors. Apify handles billing/hosting/customers, you keep ~80%. Top solo devs make $10–50k/mo; a realistic first-year catalog of 3–5 niche actors: €50–500/mo, ~90% passive. Croatian/EU data sources are underserved on the store.
2. **TCG arbitrage-alert service**: commercial precedents ([TCGSniper](https://tcgsniper.com/), [TCG Price Tracker](https://tcgpricetracker.com/)) prove people pay €5–15/mo for this. Your EU/Cardmarket depth + Croatian seller data is a real niche. [2026 analysis](https://rippr.app/blog/topic-market-analysis-1783323152716-6176-market-cardmarket-eu-us-arbitrage-2026-): cross-border gaps >7% close within 48h — speed of alerts is the product. Runs on GitHub Actions like your current tracker. Caveat: keep Cardmarket scraping personal-risk; build the paid product on Scryfall/official data.
3. **Actually flipping the arbitrage yourself (#20)** scores lower: fees (Cardmarket 5–8%, TCGplayer 10–15%, eBay ~13%) mean it only clears on ~$150+ cards, and it needs capital and shipping work.

### Honorable mention: AI training platforms (#10)
[Outlier](https://outlier.ai/), DataAnnotation, Toloka, Mindrift — $10–15/hr basic, **$20–40/hr for coding/STEM-qualified**, $200+/hr for rare experts. The purest "work exactly as much as you want, first payment within a week" option, available in Croatia (region-tiered pay). This is real human hours (AI use violates ToS) — zero automation, zero buildup, but zero risk too.

---

## 4. Bonus chapter: remote, flexible AI × geospatial work

This is where your geodesy background stops being a hobby detail and becomes pricing power. Ranked within the category:

### 4.1 GIS / Earth Engine / QGIS freelancing — score 6.85 (best geospatial)
Advertised GIS rates on [Upwork](https://www.upwork.com/freelance-jobs/gis/) run $20–30/hr; **remote-sensing / Earth Engine specialists clear $50+/hr**. Demand drivers in 2026: agriculture monitoring, climate-risk assessment, urban planning. Claude Code is a force multiplier nobody in classic GIS teams has adopted yet — it writes GEE JavaScript/Python, PyQGIS and GDAL pipelines in minutes. Fully remote, choose your own volume. *Start: 3 GEE portfolio demos (NDVI change, flood mapping, urban growth), list under Remote Sensing + QGIS categories.*

### 4.2 Google Maps / web-map development — score 6.78
Store locators, tourism maps, delivery zones — pays web-dev rates ($30–60/hr) while your geo knowledge removes the pain (projections, geocoding). Croatian tourism = endless demand for interactive apartment/marina/trail maps. Productize it: "store locator in 48h" as a Fiverr gig.

### 4.3 Drone photogrammetry processing, desk-only — score 6.51
You don't need a drone: process **other pilots' data** into orthomosaics/DEMs/3D models with free WebODM (or Metashape). US desk rates $29–48/hr; part-timers bill €2–5k/mo with 2–3 steady clients ([Emlid career guide](https://blog.emlid.com/why-get-into-drone-mapping-salary-pros-cons-opportunities/)). Small drone/survey firms hate the desk work — your geodesy training (datums, GCPs, accuracy reports) is exactly what they can't hire cheaply. Claude Code automates the WebODM→GDAL→report pipeline so each job takes hours, not days.

### 4.4 Part-time remote EO/GIS contracting — score 6.24 (highest reliable €)
Remote GIS roles post $21–115/hr on the boards; remote analyst salaries average ~$58–120k/yr with only a ~10% remote discount. Least flexible option (set hours), best €/hr. Watch: [Space-Careers](https://www.space-careers.com/jobs/remote_sensing_optics_and_gis), [GEO CAREERS](https://www.geo-careers.com/), [EGU jobs](https://www.egu.eu/jobs/), and the [EO-jobs company list](https://github.com/DahnJ/EO-jobs). Being in the EU helps with the Copernicus/ESA ecosystem.

### 4.5 Satellite imagery annotation — score 6.08
Labeling buildings/roads/crops/SAR features for CV models. Honest numbers: generic image labeling is only $12–20/hr and region-tiered; domain-qualified geospatial annotation/QA pays more, and full remote satellite-imagery-analyst roles average ~$77k/yr. Perfectly flexible filler income; register expertise on Outlier/Toloka/iMerit and wait for geo projects.

### 4.6 Dashcam drive-to-earn (Bee Maps/Hivemapper) — score 6.16
Genuinely passive: mount a dashcam ($19/mo subscription model), drive, earn HONEY tokens. Reality check from [2026 earnings data](https://oneshekel.com/how-much-does-a-hivemapper-dashcam-actually-make-per-month-real-data-2026/): modest income that decays 50–70% on repeated routes. **Croatia angle: thinner coverage than US/Germany → better freshness multipliers.** Pocket money (€10–200/mo), not income — but 100% effortless if your routes qualify.

### 4.7 Geospatial ML competitions — score 3.52 (but strategic)
[Solafune](https://solafune.com/) (Sentinel-based tasks), Kaggle's geospatial track, [SpaceNet 9](https://spacenet.ai/challenges/) (SAR-optical registration), and [Copernicus Masters](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Copernicus_Masters_bigger_than_ever) (prize pool > €1.5M, EU-friendly). Lottery-like as income, excellent as portfolio — one finished Solafune entry outweighs any CV line for the freelance tiers above.

### 4.8 The compounding endgame: automated EO-monitoring micro-SaaS — score 5.28 now, highest ceiling here
Free Sentinel/Landsat data + Google Earth Engine + Claude Code = subscription monitoring reports: vineyard/olive NDVI for Croatian farms (EU CAP subsidies push demand), coastal construction change detection, solar-site suitability, illegal-dump detection for municipalities. €20–50/mo per client, ~85% automated once running. Few people combine EO skills + automation + Croatian market access — that's a real moat. Do this *after* freelancing proves which report clients actually pay for.

---

## 5. Croatia/EU practicalities

**Getting paid** — all major rails work from Croatia: Upwork/Fiverr → **Payoneer** (best platform integration) or **Wise** (lowest FX fees) → EUR account; **Stripe** is available for your own products; Etsy pays Croatian sellers via Payoneer; Apify pays out from $20 (PayPal)/$100 (bank). Euro membership makes EU client payments trivial (SEPA).

**Tax structure (verify with an accountant — this is research, not tax advice).** The standard vehicle is the **paušalni obrt** (flat-tax trade), 2026 rules:
- Revenue limit **€60,000/yr** (raised from €40k; [HOK confirmation](https://www.hok.hr/novosti-iz-hok/prihvacen-zahtjev-hok-prag-za-pausalno-oporezivanje-podignut-na-60000-eur)) — above it you must switch to books/regular taxation.
- Flat tax **12%** on a base of 15% of your bracket ceiling → effective **€203–1,080/yr** total tax depending on bracket ([calculator](https://www.fiskai.hr/izracun/porez-pausalni-obrt/)), paid quarterly.
- Contributions: **€290.98/mo** (pension + health) if the obrt is your main activity. **If you're employed elsewhere and this is a second activity (druga djelatnost), you pay no monthly contributions** — they're settled annually via the PO-SD form, which makes low-volume side income dramatically cheaper.
- Worldwide income is taxable for Croatian residents; foreign platform income is not invisible — keep invoices.
- Crypto proceeds (Hivemapper HONEY) are separately taxable (capital gains rules).

**Cost baseline:** Claude Pro **€20/mo** is enough for every option in this report ([pricing](https://claude.com/pricing)); Max ($100/200) only pays for itself once freelance volume is real.

---

## 6. Recommended roadmap (for you specifically)

Your assets: Python + scraping + GitHub Actions automation (proven by `pokusaj`), geodesy/GIS domain knowledge, EU/Croatia location, flexible time.

**Week 1–2 — instant cash flow, zero build:** sign up for Outlier/DataAnnotation/Mindrift (STEM tiers) → first payment within ~a week. In parallel, create the Upwork profile: niche = *web scraping & price monitoring*, portfolio = pokusaj.

**Month 1–2 — freelance flywheel:** win 5–10 small Upwork jobs (automation + GIS categories both), build reviews. Build the 3 GEE portfolio demos. This is the #1 and #4 ranked income combined — realistic €500–1,500 by month 2.

**Month 2–4 — automate in parallel (the unconventional layer):** publish 2–3 Apify actors from code you already have; add the arbitrage-gap alerts to the MTG tracker and start the free Discord/Reddit audience; weekend-build the Etsy map-poster generator and list 30 designs. Each is ~90/80% hands-off after launch.

**Month 4–6 — raise rates, pick the winner:** freelance rate to €40–60/hr once reviewed; whichever automated stream shows organic traction gets the next 20 hours. If a GIS client keeps paying for the same report → that's your EO micro-SaaS seed. Register paušalni obrt as druga djelatnost once monthly income is steady.

**Realistic totals:** €300–800/mo by month 2 · €1,000–2,500/mo by month 6 (mostly freelance) · automated streams compounding from €50 to €500+/mo behind it. The €5k+/mo outcomes in this report all come from the same path: freelance proves demand → product automates it.

---

## 7. Sources

Key sources (full per-opportunity links in `data/opportunities.json`):
[Upwork rate guides](https://www.upwork.com/resources/upwork-hourly-rates) · [Web-scraper rates](https://www.upwork.com/hire/web-scrapers/cost/) · [AI-freelancer case study](https://medium.com/codetodeploy/how-i-make-4-200-month-as-an-ai-automation-freelancer-using-claude-code-and-gemini-ea0da4df8f30) · [Micro-SaaS reality data](https://www.buildmvpfast.com/blog/saas-only-way-out-indie-hacker-dream-desperation-2026) · [Chrome-extension benchmarks](https://chromegoldmine.com/blog/chrome-extension-monetization/chrome-extension-revenue-benchmarks/) · [Algora bounties](https://algora.io/bounties) + [saturation analysis](https://dev.to/zeroknowledge0x/the-open-source-money-map-every-way-developers-are-actually-making-money-in-2026-with-real-45ba) · [Apify monetization](https://docs.apify.com/platform/actors/publishing/monetize) · [RapidAPI monetization](https://1xapi.com/blog/how-to-monetize-api-rapidapi-pricing-strategy-usage-tracking-2026) · [Cardmarket–US arbitrage analysis](https://rippr.app/blog/topic-market-analysis-1783323152716-6176-market-cardmarket-eu-us-arbitrage-2026-) · [Etsy digital 2026](https://www.listifyai.net/blog/etsy-digital-downloads-guide-2026) · [Newsletter economics](https://medium.com/@automation.labs/6-ways-an-ai-newsletter-makes-money-two-scale-four-stall-b7ae05c3ac61) · [Programmatic-SEO risk](https://www.dualmedia.com/programmatic-seo-2026/) · [AI-training platforms](https://remowork.life/blog/top-ai-training-platforms-that-pay-you-to-train-ai-models-in-2026) · [Remote GIS salaries](https://www.geo-careers.com/posts/geospatial-salaries-2026/) · [Drone-mapping careers](https://blog.emlid.com/why-get-into-drone-mapping-salary-pros-cons-opportunities/) · [Hivemapper earnings data](https://oneshekel.com/how-much-does-a-hivemapper-dashcam-actually-make-per-month-real-data-2026/) · [Copernicus Masters](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Copernicus_Masters_bigger_than_ever) · [ML contests](https://mlcontests.com/) · [Paušalni obrt 2026](https://mojnovac.hr/pausalni-obrt-2026/) + [HOK €60k threshold](https://www.hok.hr/novosti-iz-hok/prihvacen-zahtjev-hok-prag-za-pausalno-oporezivanje-podignut-na-60000-eur) · [Croatia freelance payments](https://www.flexhire.com/blog/ai/full-guide-how-to-become-a-freelancer-in-croatia-2026) · [Claude pricing](https://claude.com/pricing)

*Note on source quality: blog-derived income figures (Medium/affiliate sites) skew optimistic; where possible this report anchors on platform-published rates, marketplace fee schedules and salary aggregators, and the scoring uses the conservative mid estimates.*
