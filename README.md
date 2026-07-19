# Financial Research — Earning Income with Claude Code

Deep research analysis (July 2026) of **25 ways to earn side income using Claude Code**, scored by income potential, time to first euro, hours/week, skill, upfront cost, automation level, and risk — ranked by a transparent "best = easy × makes money" score. Tailored to Croatia/EU, with a bonus chapter on remote, flexible AI × geospatial work (satellite imagery, GIS, Google Earth Engine, photogrammetry).

## Contents

| File | What it is |
|---|---|
| [`REPORT.md`](REPORT.md) | The full research report: rankings, profiles, geospatial chapter, Croatia tax/payment notes, personalized roadmap |
| [`data/opportunities.json`](data/opportunities.json) | Structured dataset — every opportunity with all metrics, scores, first steps, and source links |
| [`site/index.html`](site/index.html) | Interactive dashboard: sortable/filterable table, effort-vs-income chart, live score re-weighting |
| [`compute_scores.py`](compute_scores.py) | Recomputes scores in `data/opportunities.json` and prints the ranked markdown tables (edit the weights here) |
| [`eo-monitor/`](eo-monitor/) | 🛰️ **EO Monitor** — automated Sentinel-2 NDVI/snow/flood monitoring pipeline + report site (the report's #19 "geospatial micro-SaaS" seed, built) |
| [`LIFEPLAN.md`](LIFEPLAN.md) | 💶 **Life & Work Plan** — Monte Carlo path to financial freedom (10,000 paths × 25 years), phase playbook, decision gates; model in [`lifeplan/`](lifeplan/), interactive page at [`site/lifeplan.html`](site/lifeplan.html) |

## Run the dashboard locally

```bash
python -m http.server 8000
# → open http://localhost:8000/site/
```

(The page fetches `data/opportunities.json`, so serve the repo root rather than opening the file directly. Works on GitHub Pages the same way.)

## Re-score with your own weights

Edit the weights in `compute_scores.py` (default: income 0.40, ease 0.30, automation 0.15, low-risk 0.15) and run:

```bash
python3 compute_scores.py
```

Or just drag the weight sliders in the dashboard — it recomputes live.
