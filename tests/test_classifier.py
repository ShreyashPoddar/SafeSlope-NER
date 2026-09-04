"""
Unit tests for Member 6 AI-Assisted Field Media Verification Pipeline
Tests classification across all 5 hazard categories, confidence calibration, and latency.
"""

# Tests for Hazard Classifier
from app.comms.sample_media import build_sample_assets
from app.comms.classifier import classify_field_photo, HAZARD_CLASSES


def test_hazard_classes():
    """Verify all 5 target hazard classes are defined."""
    expected = [
        "Road Tension Crack",
        "Surface Rockfall",
        "Landslide Scar / Mudflow",
        "Blocked Culvert / Drainage Failure",
        "Normal / No Hazard",
    ]
    assert HAZARD_CLASSES == expected


def test_sample_media_classification():
    """Verify each sample image is classified correctly with high confidence and fast latency."""
    paths = build_sample_assets()

    expected_tags = {
        "crack": "Road Tension Crack",
        "rockfall": "Surface Rockfall",
        "mudflow": "Landslide Scar / Mudflow",
        "culvert": "Blocked Culvert / Drainage Failure",
        "clear": "Normal / No Hazard",
    }

    # Warm-up run for JIT / cache
    classify_field_photo(paths["rockfall"])

    for key, expected_tag in expected_tags.items():
        filepath = paths[key]
        res = classify_field_photo(filepath)

        assert res["tag"] == expected_tag, f"Expected {expected_tag} for {key}, got {res['tag']}"
        assert res["confidence_pct"] >= 65.0, f"Confidence {res['confidence_pct']} too low for {key}"
        assert res["latency_ms"] < 500.0, f"Latency {res['latency_ms']}ms exceeds threshold"
        assert "probability_distribution" in res
        assert "visual_features" in res
