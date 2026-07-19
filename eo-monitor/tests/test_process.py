import datetime as dt
from types import SimpleNamespace

import numpy as np
import pytest

from pipeline.aoi import Aoi
from pipeline.process import (boa_offset, compute_flags, compute_index,
                              normalized_difference, scl_valid_mask, summarize)
from shapely.geometry import box


def make_aoi(product="ndvi", **props):
    defaults = dict(index_threshold=0.3, drop_alert=0.15, water_frac_alert=0.15)
    defaults.update(props)
    return Aoi(id="t", name="t", product=product, description="",
               max_cloud_pct=50, geometry=box(0, 0, 1, 1),
               index_threshold=defaults["index_threshold"],
               drop_alert=defaults["drop_alert"],
               water_frac_alert=defaults["water_frac_alert"])


def test_normalized_difference_basic():
    a = np.array([[3000.0, 1000.0]])
    b = np.array([[1000.0, 3000.0]])
    valid = np.ones_like(a, dtype=bool)
    nd = normalized_difference(a, b, valid)
    assert nd[0, 0] == pytest.approx(0.5)
    assert nd[0, 1] == pytest.approx(-0.5)


def test_normalized_difference_masks_invalid_and_zero_denominator():
    a = np.array([[1000.0, 0.0]])
    b = np.array([[1000.0, 0.0]])
    valid = np.array([[False, True]])
    nd = normalized_difference(a, b, valid)
    assert np.isnan(nd).all()


def test_compute_index_orientations():
    # Vegetated pixel: NIR >> red -> NDVI positive.
    valid = np.ones((1, 1), dtype=bool)
    red, nir = np.array([[500.0]]), np.array([[4000.0]])
    assert compute_index("ndvi", red, nir, valid)[0, 0] > 0.7
    # Snow: green >> swir16 -> NDSI positive.
    green, swir = np.array([[5000.0]]), np.array([[500.0]])
    assert compute_index("ndsi", green, swir, valid)[0, 0] > 0.8
    # Water: green > nir -> NDWI positive.
    green, nir = np.array([[3000.0]]), np.array([[1000.0]])
    assert compute_index("flood", green, nir, valid)[0, 0] == pytest.approx(0.5)


def test_scl_valid_mask():
    scl = np.array([[0, 1, 3, 4, 5, 8, 9, 10, 6, 11]])
    valid = scl_valid_mask(scl)
    assert valid.tolist() == [[False, False, False, True, True,
                               False, False, False, True, True]]


def test_summarize_counts_threshold_fraction():
    index = np.array([[0.5, 0.1, np.nan, 0.6]])
    s = summarize(index, threshold=0.3)
    assert s["valid_frac"] == 0.75
    assert s["frac_above"] == pytest.approx(2 / 3, abs=1e-4)
    assert s["mean_index"] == pytest.approx(0.4, abs=1e-4)


def test_summarize_all_invalid():
    s = summarize(np.full((2, 2), np.nan), 0.3)
    assert s["valid_frac"] == 0.0 and s["mean_index"] is None


def item_with(props):
    return SimpleNamespace(properties=props, datetime=dt.datetime(2026, 6, 1))


def test_boa_offset_applied_by_baseline():
    assert boa_offset(item_with({"s2:processing_baseline": "05.00"})) == -1000.0
    assert boa_offset(item_with({"s2:processing_baseline": "03.01"})) == 0.0
    assert boa_offset(item_with({"s2:processing_baseline": "05.00",
                                 "earthsearch:boa_offset_applied": True})) == 0.0


def test_flood_flag_from_water_fraction():
    aoi = make_aoi("flood")
    obs = {"frac_above": 0.30, "mean_index": 0.0}
    assert compute_flags(aoi, obs, None) == ["flood_detected"]
    obs = {"frac_above": 0.05, "mean_index": 0.0}
    assert compute_flags(aoi, obs, None) == []


def test_ndvi_drop_flag_needs_previous():
    aoi = make_aoi("ndvi")
    now = {"frac_above": 0.5, "mean_index": 0.30}
    prev = {"frac_above": 0.6, "mean_index": 0.50}
    assert compute_flags(aoi, now, prev) == ["ndvi_drop"]
    assert compute_flags(aoi, now, None) == []
    assert compute_flags(aoi, now, {"mean_index": 0.35}) == []


def test_snowmelt_flag_on_fraction_drop():
    aoi = make_aoi("ndsi", drop_alert=0.20)
    now = {"frac_above": 0.30, "mean_index": 0.2}
    assert compute_flags(aoi, now, {"frac_above": 0.60}) == ["snowmelt_onset"]
    assert compute_flags(aoi, now, {"frac_above": 0.45}) == []
