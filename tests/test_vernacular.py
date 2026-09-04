"""
Unit tests for Member 6 Vernacular Adaptation Engine
Tests 6 North East languages, universal visual icons, and IVR voice templates.
"""

# Tests for Member 6 Vernacular Engine
from app.comms.vernacular import (
    SUPPORTED_LANGUAGES,
    TRANSLATIONS,
    ICONS,
    get_text,
    get_ivr_script,
)


def test_supported_languages_coverage():
    """Verify all 6 required North East regional languages are present."""
    required_codes = {"en", "as", "kha", "lus", "mni", "bn"}
    assert set(SUPPORTED_LANGUAGES.keys()) == required_codes


def test_translation_keys_across_all_languages():
    """Verify each language has all mandatory message templates."""
    mandatory_keys = [
        "welcome_banner",
        "menu_prompt",
        "lang_select_prompt",
        "lang_updated",
        "report_step1_hazard",
        "report_step2_photo",
        "report_step3_location",
        "report_confirm_title",
        "report_confirm_body",
        "shelter_title",
        "shelter_default",
        "sos_prompt",
        "alert_broadcast_high",
        "alert_broadcast_moderate",
    ]

    for lang in ["en", "as", "kha", "lus", "mni", "bn"]:
        for key in mandatory_keys:
            text = get_text(
                key,
                lang=lang,
                tracking_id="TEST-001",
                classification="Surface Rockfall",
                confidence="85.0",
                location_str="NH-54 km 42",
                timestamp="2026-09-03 12:00:00",
                zone_name="Zone 1",
                trigger_source="Physics Floor",
                isolation_summary="2 villages cut off",
                bypass_route="Eastern Bypass B-7",
            )
            assert text is not None and len(text) > 5, f"Missing or empty template '{key}' for language '{lang}'"


def test_universal_visual_icons():
    """Verify non-literate visual icons are available."""
    assert "alert" in ICONS
    assert "rockfall" in ICONS
    assert "crack" in ICONS
    assert "landslide" in ICONS
    assert "sos" in ICONS
    assert "shelter" in ICONS


def test_ivr_scripts():
    """Verify IVR voice prompt generation."""
    for lang in ["en", "lus", "as"]:
        intro = get_ivr_script("intro", lang)
        assert len(intro) > 10
