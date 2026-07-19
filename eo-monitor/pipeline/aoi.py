"""AOI definitions: one GeoJSON Feature per monitored area in aois/.

Adding a client/area = dropping a new .geojson file in aois/ with the
properties documented in the README. Nothing else to configure.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
AOI_DIR = ROOT / "aois"
DATA_DIR = ROOT / "data"

PRODUCTS = ("ndvi", "ndsi", "flood")


@dataclass
class Aoi:
    id: str
    name: str
    product: str
    description: str
    max_cloud_pct: float
    index_threshold: float
    geometry: object  # shapely geometry, WGS84
    drop_alert: float | None = None
    water_frac_alert: float | None = None
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return self.geometry.bounds

    @property
    def data_dir(self) -> Path:
        return DATA_DIR / self.id


def load_aoi(path: Path) -> Aoi:
    feature = json.loads(path.read_text())
    props = feature["properties"]
    if props["product"] not in PRODUCTS:
        raise ValueError(f"{path.name}: unknown product {props['product']!r}")
    return Aoi(
        id=props["id"],
        name=props["name"],
        product=props["product"],
        description=props.get("description", ""),
        max_cloud_pct=float(props.get("max_cloud_pct", 50)),
        index_threshold=float(props["index_threshold"]),
        drop_alert=props.get("drop_alert"),
        water_frac_alert=props.get("water_frac_alert"),
        geometry=shape(feature["geometry"]),
        raw=feature,
    )


def load_aois(only: str | None = None) -> list[Aoi]:
    aois = [load_aoi(p) for p in sorted(AOI_DIR.glob("*.geojson"))]
    if only and only != "all":
        aois = [a for a in aois if a.id == only]
        if not aois:
            raise SystemExit(f"No AOI with id {only!r} in {AOI_DIR}")
    return aois
