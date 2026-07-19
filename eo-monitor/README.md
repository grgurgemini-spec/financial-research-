# 🛰️ EO Monitor

Automated Sentinel-2 Earth-observation monitoring. A GitHub Actions cron job
finds new satellite scenes for each configured area of interest (AOI), reads
**only the AOI's pixels** from the cloud-optimized GeoTIFFs, masks clouds,
computes the AOI's index and publishes a static report site — no server, no
manual notebook runs, no cost.

Current products:

| Product | Index | What it monitors | Alert flag |
|---|---|---|---|
| `ndvi` | NDVI (B08/B04) | vegetation vigor (vineyards, crops) | `ndvi_drop` — mean NDVI fell by ≥ `drop_alert` |
| `ndsi` | NDSI (B03/B11) | snow cover fraction | `snowmelt_onset` — snow fraction fell by ≥ `drop_alert` |
| `flood` | NDWI (B03/B08) | open-water fraction | `flood_detected` — water fraction ≥ `water_frac_alert` |

Demo AOIs: Ilok vineyards (NDVI), Zavižan/northern Velebit (NDSI), Lonjsko
polje Sava floodplain (flood).

## How it works

```
aois/*.geojson ──▶ pipeline/search.py   STAC query (Earth Search, sentinel-2-l2a)
                   pipeline/process.py  windowed COG reads · SCL cloud mask · index + stats
                   pipeline/report.py   map PNGs · data/<aoi>/timeseries.json · latest.json
                   site/                static report pages (GitHub Pages)
```

- **Data**: ESA Copernicus Sentinel-2 L2A via the free, no-auth
  [Earth Search STAC API](https://earth-search.aws.element84.com/v1) backed by
  the AWS open-data COG bucket. Windowed reads mean a run downloads megabytes,
  not gigabytes.
- **Correctness details**: cloud/shadow/nodata pixels are masked via the SCL
  band; the processing-baseline ≥ 4.0 BOA reflectance offset (−1000) is
  normalized before computing indices; observations are deduplicated per date
  and runs are idempotent (re-running changes nothing).
- **Automation**: `.github/workflows/eo-monitor.yml` (repo root) runs daily,
  commits new observations to `eo-monitor/data/`, and republishes the site to
  the `gh-pages` branch.

### Why not Google Earth Engine or AWS Lambda?

GEE's free tier is licensed for noncommercial use only — the wrong foundation
for a commercial monitoring service. Lambda adds cold starts, layer limits and
per-invocation cost to what is a low-frequency batch job. GitHub Actions +
direct COG processing is free, license-clean, and the whole pipeline is plain
Python you can run anywhere.

## Quick start (local)

```bash
cd eo-monitor
pip install -r requirements.txt
python -m pipeline.run                 # process new scenes for all AOIs
python -m http.server 8000             # → http://localhost:8000/site/
```

Useful variants:

```bash
python -m pipeline.run --aoi flood-lonjsko          # one AOI
python -m pipeline.run --since 2026-03-01           # backfill from a date
python -m pytest tests/                             # unit tests
```

## Adding an AOI (this is the whole onboarding process)

Drop a GeoJSON Feature into `aois/`:

```json
{
  "type": "Feature",
  "properties": {
    "id": "my-parcel",
    "name": "My vineyard",
    "product": "ndvi",
    "description": "Shown on the report page.",
    "max_cloud_pct": 40,
    "index_threshold": 0.3,
    "drop_alert": 0.15
  },
  "geometry": { "type": "Polygon", "coordinates": [[ ... WGS84 lon/lat ... ]] }
}
```

`flood` AOIs use `water_frac_alert` (alert when the water fraction exceeds it)
instead of `drop_alert`. The next pipeline run bootstraps ~4 months of history
automatically.

## Alerts

Flags are computed per observation, stored in the time series and shown on the
site. To push them (Discord/email), wire a webhook into
`pipeline/report.py:send_alerts` — it receives every flagged observation.

## Deployment

The daily cron (or a manual run of the *EO Monitor - update observations*
workflow) processes new scenes and force-pushes the site to `gh-pages`, which
GitHub Pages already serves for this repo. Live at
`https://grgurgemini-spec.github.io/financial-research-/eo-monitor/`.

Contains modified Copernicus Sentinel data. Sentinel-2 imagery © ESA, provided
under the Copernicus open data licence.
