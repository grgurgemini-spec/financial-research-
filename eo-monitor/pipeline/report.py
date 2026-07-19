"""Run outputs: map PNG per observation, per-AOI time series JSON, and the
cross-AOI summary the report site reads. Everything is committed to data/,
so the GitHub Pages site is fully static and each Actions run just appends."""
from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .aoi import Aoi, DATA_DIR

MAX_MAPS = 6  # keep the repo bounded: only the most recent maps are retained

CMAP = {"ndvi": "YlGn", "ndsi": "PuBu", "flood": "PuBu"}
VMINMAX = {"ndvi": (-0.1, 0.9), "ndsi": (-0.4, 1.0), "flood": (-0.6, 0.6)}
INDEX_LABEL = {"ndvi": "NDVI", "ndsi": "NDSI", "flood": "NDWI"}


def timeseries_path(aoi: Aoi) -> Path:
    return aoi.data_dir / "timeseries.json"


def load_timeseries(aoi: Aoi) -> list[dict]:
    p = timeseries_path(aoi)
    return json.loads(p.read_text()) if p.exists() else []


def save_map_png(aoi: Aoi, obs: dict, index: np.ndarray) -> str:
    maps_dir = aoi.data_dir / "maps"
    maps_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{obs['date']}.png"

    fig, ax = plt.subplots(figsize=(6, 6 * index.shape[0] / max(index.shape[1], 1)))
    shown = np.ma.masked_invalid(index)
    vmin, vmax = VMINMAX[aoi.product]
    im = ax.imshow(shown, cmap=CMAP[aoi.product], vmin=vmin, vmax=vmax)
    if aoi.product == "flood":  # outline detected water on top of the index
        ax.contour(index > aoi.index_threshold, levels=[0.5], colors="#0d366b", linewidths=0.8)
    ax.set_axis_off()
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label(INDEX_LABEL[aoi.product])
    ax.set_title(f"{aoi.name} — {obs['date']}", fontsize=10)
    fig.savefig(maps_dir / fname, dpi=110, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)

    keep = sorted(maps_dir.glob("*.png"))[-MAX_MAPS:]
    for old in maps_dir.glob("*.png"):
        if old not in keep:
            old.unlink()
    return f"maps/{fname}"


def append_observations(aoi: Aoi, new_entries: list[dict]) -> list[dict]:
    series = load_timeseries(aoi)
    known = {e["item_id"] for e in series}
    series += [e for e in new_entries if e["item_id"] not in known]
    series.sort(key=lambda e: e["date"])
    aoi.data_dir.mkdir(parents=True, exist_ok=True)
    timeseries_path(aoi).write_text(json.dumps(series, indent=1) + "\n")
    return series


def write_latest(aoi: Aoi, series: list[dict]) -> dict:
    maps = sorted((aoi.data_dir / "maps").glob("*.png")) if (aoi.data_dir / "maps").exists() else []
    latest = {
        "id": aoi.id,
        "name": aoi.name,
        "product": aoi.product,
        "index_label": INDEX_LABEL[aoi.product],
        "description": aoi.description,
        "index_threshold": aoi.index_threshold,
        "last_run": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "n_observations": len(series),
        "latest": series[-1] if series else None,
        "maps": [f"maps/{m.name}" for m in maps],
    }
    (aoi.data_dir / "latest.json").write_text(json.dumps(latest, indent=1) + "\n")
    return latest


def write_summary(latests: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "index.json").write_text(json.dumps({
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "aois": latests,
    }, indent=1) + "\n")


def send_alerts(aoi: Aoi, obs: dict) -> None:
    """Alert delivery hook. Flags are already stored in the observation and
    shown on the site; wire a Discord/email webhook here when a client wants
    push delivery (read the URL from an env var / Actions secret)."""
    if obs.get("flags"):
        print(f"  ALERT [{aoi.id}] {obs['date']}: {', '.join(obs['flags'])}")
