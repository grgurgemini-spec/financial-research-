"""Windowed Sentinel-2 processing: read only the AOI's pixels from the COGs,
mask clouds via the SCL band, compute the AOI's index and summary stats.

All arrays are on the 20 m SCL grid (NDSI needs 20 m SWIR anyway and a
2-10 km AOI stays a few hundred pixels across, so runs are seconds, not
minutes). 10 m bands are decimated to that grid with average resampling.
"""
from __future__ import annotations

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

from .aoi import Aoi

# SCL classes treated as unusable: nodata, saturated, cloud shadow,
# medium/high-probability cloud, thin cirrus.
BAD_SCL = (0, 1, 3, 8, 9, 10)

# Bands needed per product (Earth Search asset keys).
PRODUCT_BANDS = {
    "ndvi": ("red", "nir"),
    "ndsi": ("green", "swir16"),
    "flood": ("green", "nir"),
}


def boa_offset(item) -> float:
    """Reflectance offset to add before ratioing.

    Processing baseline >= 04.00 stores L2A reflectance with a -1000 offset.
    Earth Search marks whether it already removed it; index ratios are wrong
    by several percent if the offset is left in, so normalize here.
    """
    props = item.properties
    baseline = str(props.get("s2:processing_baseline", "99.99"))
    try:
        needs = float(baseline) >= 4.0
    except ValueError:
        needs = True
    applied = props.get("earthsearch:boa_offset_applied", False)
    return -1000.0 if (needs and not applied) else 0.0


def read_window(href: str, bounds_wgs84, out_shape=None, resampling=Resampling.average):
    """Read the AOI window from one COG; returns (array float32, transform, crs)."""
    with rasterio.open(href) as src:
        bounds = transform_bounds("EPSG:4326", src.crs, *bounds_wgs84, densify_pts=5)
        window = from_bounds(*bounds, transform=src.transform)
        if out_shape is None:
            out_shape = (round(window.height), round(window.width))
        data = src.read(1, window=window, out_shape=out_shape,
                        resampling=resampling, boundless=True, fill_value=0)
        transform = src.window_transform(window)
        return data.astype("float32"), transform, src.crs


def normalized_difference(a: np.ndarray, b: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """(a - b) / (a + b) where valid and the denominator is usable; NaN elsewhere."""
    denom = a + b
    ok = valid & (denom != 0)
    out = np.full(a.shape, np.nan, dtype="float32")
    np.divide(a - b, denom, out=out, where=ok)
    return out


def compute_index(product: str, band1: np.ndarray, band2: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """band1/band2 in PRODUCT_BANDS order. NDVI=(nir-red)/(nir+red),
    NDSI=(green-swir)/(green+swir), flood NDWI=(green-nir)/(green+nir)."""
    if product == "ndvi":
        return normalized_difference(band2, band1, valid)   # (nir - red)
    if product == "ndsi":
        return normalized_difference(band1, band2, valid)   # (green - swir16)
    if product == "flood":
        return normalized_difference(band1, band2, valid)   # (green - nir)
    raise ValueError(product)


def scl_valid_mask(scl: np.ndarray) -> np.ndarray:
    return ~np.isin(scl.astype("int16"), BAD_SCL)


def summarize(index: np.ndarray, threshold: float) -> dict:
    valid = ~np.isnan(index)
    n_valid = int(valid.sum())
    total = index.size
    if n_valid == 0:
        return {"valid_frac": 0.0, "mean_index": None, "frac_above": None}
    return {
        "valid_frac": round(n_valid / total, 4),
        "mean_index": round(float(np.nanmean(index)), 4),
        "frac_above": round(float((index[valid] > threshold).sum() / n_valid), 4),
    }


def process_item(aoi: Aoi, item) -> dict | None:
    """Process one STAC item for the AOI. Returns the observation dict, its
    index array and map transform - or None when the AOI is fully clouded."""
    b1_key, b2_key = PRODUCT_BANDS[aoi.product]
    offset = boa_offset(item)

    scl, transform, crs = read_window(item.assets["scl"].href, aoi.bounds,
                                      resampling=Resampling.nearest)
    shape = scl.shape
    b1, _, _ = read_window(item.assets[b1_key].href, aoi.bounds, out_shape=shape)
    b2, _, _ = read_window(item.assets[b2_key].href, aoi.bounds, out_shape=shape)
    b1, b2 = b1 + offset, b2 + offset

    valid = scl_valid_mask(scl) & (b1 > -offset if offset else b1 > 0)
    index = compute_index(aoi.product, b1, b2, valid)
    stats = summarize(index, aoi.index_threshold)
    if stats["valid_frac"] < 0.2:      # AOI essentially unobserved this pass
        return None

    obs = {
        "date": item.datetime.date().isoformat(),
        "item_id": item.id,
        "cloud_cover_scene": round(float(item.properties.get("eo:cloud_cover", -1)), 2),
        **stats,
    }
    return {"obs": obs, "index": index, "transform": transform, "crs": str(crs)}


def compute_flags(aoi: Aoi, obs: dict, previous: dict | None) -> list[str]:
    """Alert flags for one new observation vs. the previous usable one."""
    flags: list[str] = []
    frac, mean = obs.get("frac_above"), obs.get("mean_index")
    if aoi.product == "flood" and aoi.water_frac_alert is not None:
        if frac is not None and frac >= aoi.water_frac_alert:
            flags.append("flood_detected")
    if previous:
        if aoi.product == "ndvi" and aoi.drop_alert is not None:
            prev_mean = previous.get("mean_index")
            if mean is not None and prev_mean is not None and prev_mean - mean >= aoi.drop_alert:
                flags.append("ndvi_drop")
        if aoi.product == "ndsi" and aoi.drop_alert is not None:
            prev_frac = previous.get("frac_above")
            if frac is not None and prev_frac is not None and prev_frac - frac >= aoi.drop_alert:
                flags.append("snowmelt_onset")
    return flags
