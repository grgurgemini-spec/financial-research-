"""STAC search: find new Sentinel-2 L2A scenes for an AOI.

Data source is the public Earth Search STAC API (element84) backed by the
AWS open-data Sentinel-2 COG bucket - free, no auth, cloud-optimized so we
only ever download the AOI's pixels. Copernicus Data Space is the fallback
if Earth Search ever degrades (swap STAC_URL + asset names).
"""
from __future__ import annotations

import datetime as dt

from pystac_client import Client

from .aoi import Aoi

STAC_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION = "sentinel-2-l2a"


def search_scenes(aoi: Aoi, since: dt.date, until: dt.date | None = None,
                  max_items: int = 12, skip_ids: set[str] | None = None) -> list:
    """Return STAC items for the AOI, oldest first, excluding already-processed ids."""
    client = Client.open(STAC_URL)
    until = until or dt.date.today()
    search = client.search(
        collections=[COLLECTION],
        intersects=aoi.geometry.__geo_interface__,
        datetime=f"{since.isoformat()}/{until.isoformat()}",
        query={"eo:cloud_cover": {"lt": aoi.max_cloud_pct}},
        max_items=200,
    )
    items = sorted(search.items(), key=lambda i: i.datetime)
    if skip_ids:
        items = [i for i in items if i.id not in skip_ids]
    # A single date can appear as several items (datatake split / adjacent
    # granules); keep the least-cloudy item per date.
    by_date: dict[str, object] = {}
    for item in items:
        key = item.datetime.date().isoformat()
        prev = by_date.get(key)
        if prev is None or item.properties.get("eo:cloud_cover", 100) < prev.properties.get("eo:cloud_cover", 100):
            by_date[key] = item
    deduped = sorted(by_date.values(), key=lambda i: i.datetime)
    return deduped[-max_items:]
