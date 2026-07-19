"""Pipeline orchestrator.

  python -m pipeline.run                 # all AOIs, continue from last observation
  python -m pipeline.run --aoi flood-lonjsko
  python -m pipeline.run --since 2026-03-01 --max-items 20

Each run: STAC-search new scenes -> windowed process -> append time series,
render maps, refresh latest.json + data/index.json. Idempotent: already
processed item ids are skipped, so an empty run changes nothing.
"""
from __future__ import annotations

import argparse
import datetime as dt

from .aoi import load_aois
from .process import compute_flags, process_item
from .report import (append_observations, load_timeseries, save_map_png,
                     send_alerts, write_latest, write_summary)
from .search import search_scenes

BOOTSTRAP_DAYS = 120   # history depth for an AOI's very first run
LOOKBACK_DAYS = 10     # re-check window behind the last observation


def run_aoi(aoi, since: dt.date | None, max_items: int) -> dict:
    series = load_timeseries(aoi)
    known = {e["item_id"] for e in series}
    if since is None:
        if series:
            last = dt.date.fromisoformat(series[-1]["date"])
            since = last - dt.timedelta(days=LOOKBACK_DAYS)
        else:
            since = dt.date.today() - dt.timedelta(days=BOOTSTRAP_DAYS)

    items = search_scenes(aoi, since=since, max_items=max_items, skip_ids=known)
    known_dates = {e["date"] for e in series}
    items = [i for i in items if i.datetime.date().isoformat() not in known_dates]
    print(f"[{aoi.id}] {len(items)} new scene(s) since {since}")

    new_entries = []
    prev = series[-1] if series else None
    for item in items:
        result = process_item(aoi, item)
        if result is None:
            print(f"  {item.datetime.date()} skipped (AOI cloud-covered)")
            continue
        obs = result["obs"]
        obs["flags"] = compute_flags(aoi, obs, prev)
        obs["map"] = save_map_png(aoi, obs, result["index"])
        print(f"  {obs['date']} mean={obs['mean_index']} frac>{aoi.index_threshold}={obs['frac_above']}"
              + (f" flags={obs['flags']}" if obs["flags"] else ""))
        send_alerts(aoi, obs)
        new_entries.append(obs)
        prev = obs

    series = append_observations(aoi, new_entries)
    return write_latest(aoi, series)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sentinel-2 AOI monitoring pipeline")
    ap.add_argument("--aoi", default="all", help="AOI id (default: all)")
    ap.add_argument("--since", type=dt.date.fromisoformat, default=None,
                    help="Process scenes from this date (default: continue)")
    ap.add_argument("--max-items", type=int, default=12, help="Scene cap per AOI per run")
    args = ap.parse_args()

    latests = [run_aoi(aoi, args.since, args.max_items) for aoi in load_aois(args.aoi)]
    if args.aoi == "all":
        write_summary(latests)
    print("done")


if __name__ == "__main__":
    main()
