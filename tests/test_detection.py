import numpy as np
from app.detection.postprocessing import clean_mask, threshold_mask, remove_small_objects
from app.detection.change_calculator import compute_change_stats
from app.detection.region_analysis import analyze_regions
from app.visualization.overlays import build_overlay


def test_threshold_mask_binarizes_correctly():
    prob = np.array([[0.1, 0.6], [0.9, 0.3]])
    result = threshold_mask(prob, threshold=0.5)
    assert result.tolist() == [[0, 1], [1, 0]]


def test_remove_small_objects_drops_tiny_regions():
    mask = np.zeros((20, 20), dtype=np.uint8)
    mask[0:2, 0:2] = 1
    mask[10:18, 10:18] = 1
    cleaned = remove_small_objects(mask, min_size=20)
    assert cleaned[0, 0] == 0
    assert cleaned[14, 14] == 1


def test_compute_change_stats_matches_manual_calculation():
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[0:5, 0:2] = 1
    stats = compute_change_stats(mask)
    assert stats["total_pixels"] == 100
    assert stats["changed_pixels"] == 10
    assert stats["change_percent"] == 10.0
    assert stats["severity"] == "LOW"


def test_analyze_regions_finds_expected_region_count():
    mask = np.zeros((50, 50), dtype=np.uint8)
    mask[5:15, 5:15] = 1
    mask[30:40, 30:40] = 1
    regions = analyze_regions(mask)
    assert len(regions) == 2
    assert regions[0]["area"] > 0


def test_build_overlay_highlights_changed_pixels():
    base = np.zeros((10, 10, 3), dtype=np.uint8)
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[2:5, 2:5] = 1
    overlay = build_overlay(base, mask, opacity=1.0)
    assert overlay[3, 3].tolist() != [0, 0, 0]
    assert overlay[0, 0].tolist() == [0, 0, 0]
