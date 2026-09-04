import os
import sys
import asyncio

os.environ["TESTING"] = "1"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))

from starlette.testclient import TestClient

from app.main import app
from app.services.threshold_engine import (
    get_threshold_settings,
    update_threshold_settings,
    determine_risk_level,
    evaluate_landslide_algorithm_prediction,
)
from app.comms.dispatcher import alert_dispatcher
from app.comms.twilio_client import comms_client

client = TestClient(app)


def test_threshold_settings_defaults_and_updates():
    """Verify default threshold settings and dynamic updating."""
    defaults = get_threshold_settings()
    assert defaults.advisory_threshold == 40.0
    assert defaults.warning_threshold == 70.0
    assert defaults.critical_threshold == 85.0
    assert defaults.auto_notify_on_breach is True

    # Test dynamic adjustment
    updated = update_threshold_settings({
        "warning_threshold": 65.0,
        "critical_threshold": 80.0,
    })
    assert updated.warning_threshold == 65.0
    assert updated.critical_threshold == 80.0

    # Reset back to standard
    update_threshold_settings({
        "warning_threshold": 70.0,
        "critical_threshold": 85.0,
    })


def test_determine_risk_level():
    """Verify risk classification against active thresholds."""
    # Under 40%: LOW
    level, breached = determine_risk_level(25.0)
    assert level == "LOW"
    assert breached is False

    # 40% - 69.9%: MODERATE
    level, breached = determine_risk_level(55.0)
    assert level == "MODERATE"
    assert breached is False

    # 70% - 84.9%: HIGH (Breached warning threshold)
    level, breached = determine_risk_level(75.0)
    assert level == "HIGH"
    assert breached is True

    # >= 85%: CRITICAL (Breached critical threshold)
    level, breached = determine_risk_level(91.0)
    assert level == "CRITICAL"
    assert breached is True


def test_area_directory_subscribers():
    """Verify community subscriber registry and area-specific targeting."""
    # Register a new community member in Serchhip
    new_sub = alert_dispatcher.register_subscriber(
        phone="+919436199999",
        name="Test Volunteer",
        zone_name="Champhai - Serchhip Corridor (NH-54)",
        village="Keitum",
        role="aapda_mitra",
        channel="whatsapp",
        lang="lus",
    )
    assert new_sub["name"] == "Test Volunteer"

    # Targeted area lookup for Champhai - Serchhip Corridor
    area_subs = alert_dispatcher.get_subscribers_for_area(
        zone_name="Champhai - Serchhip Corridor (NH-54)",
        audience_filter="all_in_area",
    )
    assert len(area_subs) >= 4
    phones = [s["phone"] for s in area_subs]
    assert "+919436199999" in phones

    # Filter by volunteers & village heads only
    volunteers = alert_dispatcher.get_subscribers_for_area(
        zone_name="Champhai - Serchhip Corridor (NH-54)",
        audience_filter="volunteers_only",
    )
    assert all(s["role"] in ["aapda_mitra", "village_head", "deoc"] for s in volunteers)


def test_multi_channel_broadcast_cascade():
    """Verify alert dispatch across WhatsApp, Cellular SMS, Telegram, and CAP protocol."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        res = loop.run_until_complete(
            alert_dispatcher.evaluate_risk_trigger(
                zone_id=1,
                zone_name="Champhai - Serchhip Corridor (NH-54)",
                risk_level="HIGH",
                source="test_runner",
                force_broadcast=True,
                notification_settings={
                    "channels": ["whatsapp", "sms", "telegram", "cap", "siren"],
                    "target_audience": "all_in_area",
                    "custom_instructions": "Test Evacuation Notice",
                },
            )
        )
    finally:
        loop.close()

    assert res is not None
    assert "cap_identifier" in res
    assert res["successful_deliveries"] > 0
    assert "breakdown" in res
    assert res["breakdown"]["whatsapp"] >= 1
    assert res["breakdown"]["sms"] >= 1
    assert res["breakdown"]["telegram"] >= 1
    assert res["breakdown"]["village_sirens_activated"] is True
    assert len(res["targeted_villages"]) > 0


def test_api_thresholds_endpoints():
    """Verify GET and POST /api/comms/thresholds endpoints."""
    # GET thresholds
    resp = client.get("/api/comms/thresholds")
    assert resp.status_code == 200
    data = resp.json()
    assert "settings" in data
    assert "warning_threshold" in data["settings"]

    # POST update thresholds
    update_resp = client.post(
        "/api/comms/thresholds",
        json={"warning_threshold": 68.0, "auto_notify_on_breach": True},
    )
    assert update_resp.status_code == 200
    up_data = update_resp.json()
    assert up_data["settings"]["warning_threshold"] == 68.0


def test_api_subscribers_endpoints():
    """Verify community directory endpoints."""
    # List subscribers
    resp = client.get("/api/comms/subscribers?role=aapda_mitra")
    assert resp.status_code == 200
    subs = resp.json()
    assert len(subs) > 0
    assert all(s["role"] == "aapda_mitra" for s in subs)

    # Register new citizen
    reg_resp = client.post(
        "/api/comms/subscribers",
        json={
            "phone": "+919862888777",
            "name": "Zosangliana",
            "zone_name": "Champhai - Serchhip Corridor (NH-54)",
            "village": "Chhiahtlang",
            "role": "citizen",
            "lang": "lus",
        },
    )
    assert reg_resp.status_code == 200
    assert reg_resp.json()["status"] == "registered"


def test_api_broadcast_trigger_with_notification_settings():
    """Verify POST /api/comms/broadcast/trigger with explicit notification settings."""
    payload = {
        "zone_name": "Aizawl South Mountain Slopes",
        "risk_level": "CRITICAL",
        "source": "physics_floor",
        "notification_settings": {
            "channels": ["whatsapp", "sms", "telegram", "cap", "siren"],
            "target_audience": "all_in_area",
            "custom_instructions": "NH-54 km 42 tension crack widening. Evacuate immediately.",
            "severity": "Extreme",
            "urgency": "Immediate",
        },
    }
    resp = client.post("/api/comms/broadcast/trigger", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    assert "dispatch_id" in res
    assert res["risk_level"] == "CRITICAL"
    assert res["breakdown"]["village_sirens_activated"] is True


def test_api_algorithm_landslide_risk_ingestion():
    """Verify POST /api/algorithm/landslide-risk evaluating threshold and auto-broadcasting."""
    payload = {
        "zone_id": 1,
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "risk_pct": 86.4,
        "confidence_pct": 89.0,
        "model_version": "xgboost-landslide-v2",
        "rainfall_mm_24h": 156.0,
        "soil_moisture_pct": 82.5,
        "slope_tilt_deg": 5.2,
        "force_notify": True,
    }
    resp = client.post("/api/algorithm/landslide-risk", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_pct"] == 86.4
    assert data["derived_risk_level"] == "CRITICAL"
    assert data["threshold_breached"] is True
    assert data["notification_triggered"] is True
    assert data["dispatch_summary"] is not None
    assert data["dispatch_summary"]["successful_deliveries"] > 0


if __name__ == "__main__":
    tests = [
        test_threshold_settings_defaults_and_updates,
        test_determine_risk_level,
        test_area_directory_subscribers,
        test_multi_channel_broadcast_cascade,
        test_api_thresholds_endpoints,
        test_api_subscribers_endpoints,
        test_api_broadcast_trigger_with_notification_settings,
        test_api_algorithm_landslide_risk_ingestion,
    ]
    print(f"Running {len(tests)} tests for Landslide Risk Thresholds & Area Notifications...")
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  [PASS] {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\nCompleted: {passed}/{len(tests)} passed.")
    if passed != len(tests):
        exit(1)

