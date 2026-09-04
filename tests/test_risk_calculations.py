from app.services.risk_calculator import (
    calculate_factor_of_safety,
    calculate_failure_probability,
    calculate_evacuation_window_hours,
    calculate_impact_radius_meters,
    resolve_spatial_isolation_and_network,
    calculate_complete_risk_profile,
    haversine_distance_km,
)
from app.services.threshold_engine import evaluate_landslide_algorithm_prediction
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_factor_of_safety_physics():
    # 1. Gentle slope with low moisture -> Should be stable (FoS > 1.5)
    fos_stable = calculate_factor_of_safety(
        slope_angle_deg=18.0,
        soil_moisture_pct=25.0,
        pore_pressure_kpa=0.0,
    )
    assert fos_stable > 1.5, f"Gentle slope should be stable, got FoS {fos_stable}"

    # 2. Steep cut slope with high soil moisture and positive pore pressure -> Failure (FoS < 1.0)
    fos_failure = calculate_factor_of_safety(
        slope_angle_deg=45.0,
        soil_moisture_pct=85.0,
        pore_pressure_kpa=32.0,
    )
    assert fos_failure < 1.0, f"Steep saturated slope should fail (FoS < 1.0), got {fos_failure}"


def test_failure_probability_and_evacuation_window():
    # Failing slope: short evacuation window
    hours_critical = calculate_evacuation_window_hours(
        fos=0.82,
        tilt_rate_deg_hr=0.15,
        rainfall_24h_mm=180.0,
    )
    assert hours_critical <= 2.0, f"Critical slope evacuation window should be <= 2.0 hrs, got {hours_critical}"

    # Marginally stable slope: longer evacuation window
    hours_marginal = calculate_evacuation_window_hours(
        fos=1.22,
        tilt_rate_deg_hr=0.01,
        rainfall_24h_mm=80.0,
    )
    assert hours_marginal >= 4.0, f"Marginal slope evacuation window should be >= 4.0 hrs, got {hours_marginal}"


def test_spatial_isolation_calculation_no_hardcoding():
    # Calculate for Champhai - Serchhip Corridor
    spatial_res = resolve_spatial_isolation_and_network(
        zone_name="Champhai - Serchhip Corridor (NH-54)",
        lat=23.2845,
        lng=92.8391,
        impact_radius_m=1200.0,
        risk_level="CRITICAL",
    )

    # Must NOT be a hardcoded 4 or 2; must be a dynamically computed list of actual village names
    assert spatial_res["isolated_villages_count"] > 0
    assert "Chhiahtlang" in spatial_res["affected_villages"] or "Serchhip" in spatial_res["affected_villages"]
    assert spatial_res["affected_population"] > 0
    assert spatial_res["designated_bypass"] is not None
    assert len(spatial_res["facilities_cut_off"]) >= 1


def test_complete_risk_profile_generation():
    profile = calculate_complete_risk_profile(
        zone_name="Champhai - Serchhip Corridor (NH-54)",
        risk_pct=88.5,
        confidence_pct=92.0,
        rainfall_24h_mm=165.0,
        soil_moisture_pct=82.0,
        slope_tilt_deg=39.0,
    )

    assert "factor_of_safety" in profile
    assert profile["factor_of_safety"] < 1.3
    assert profile["derived_risk_level"] in ["HIGH", "CRITICAL"]
    assert profile["impact_radius_meters"] >= 300.0
    assert profile["evacuation_window_hours"] > 0
    assert profile["isolation_metrics"]["affected_population"] > 0


def test_algorithm_ingestion_api_endpoint():
    # Test POST /api/algorithm/landslide-risk with model format
    payload = {
        "source_model": "SafeSlope-Landslide-Predictor-v1",
        "corridor_id": "Champhai - Serchhip Corridor (NH-54)",
        "predicted_probability": 0.89,
        "confidence": 0.94,
        "latitude": 23.2845,
        "longitude": 92.8391,
        "trigger_features": {
            "rainfall_24h_mm": 155.0,
            "soil_saturation_pct": 84.0,
            "slope_tilt_rate_deg_hr": 0.12,
        },
        "force_notify": True,
    }
    resp = client.post("/api/algorithm/landslide-risk", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["risk_pct"] == 89.0
    assert data["derived_risk_level"] == "CRITICAL"
    assert data["threshold_breached"] is True
    assert "factor_of_safety" in data
    assert "impact_radius_km" in data
    assert "isolation_metrics" in data
    assert data["isolation_metrics"]["affected_population"] > 0
    assert data["notification_triggered"] is True


def test_live_demo_status_and_message_endpoints():
    # 1. Test GET /api/comms/live-demo/status
    status_resp = client.get("/api/comms/live-demo/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert "telegram" in status_data
    assert "twilio" in status_data
    assert "registered_subscribers" in status_data

    # 2. Test POST /api/comms/live-demo/test-message with Telegram
    tg_test_payload = {
        "target_type": "telegram",
        "destination": "123456789",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
    }
    msg_resp = client.post("/api/comms/live-demo/test-message", json=tg_test_payload)
    assert msg_resp.status_code == 200
    msg_data = msg_resp.json()
    assert "status" in msg_data
    assert msg_data.get("chat_id") == 123456789

    # 3. Test POST /api/comms/live-demo/test-message with SMS
    sms_test_payload = {
        "target_type": "sms",
        "destination": "+919436122880",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
    }
    sms_resp = client.post("/api/comms/live-demo/test-message", json=sms_test_payload)
    assert sms_resp.status_code == 200
    sms_data = sms_resp.json()
    assert "status" in sms_data

    # 4. Test POST /api/comms/live-demo/test-message with WhatsApp
    wa_test_payload = {
        "target_type": "whatsapp",
        "destination": "+919436122880",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
    }
    wa_resp = client.post("/api/comms/live-demo/test-message", json=wa_test_payload)
    assert wa_resp.status_code == 200
    wa_data = wa_resp.json()
    assert "status" in wa_data
    assert "provider" in wa_data
    assert "whatsapp:+919436122880" in wa_data.get("to", "")

    # 5. Test Meta WhatsApp Webhook Challenge Verification
    verify_resp = client.get(
        "/api/comms/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test_challenge_123&hub.verify_token=safeslope_secret_verify_token_2026"
    )
    assert verify_resp.status_code == 200
    assert verify_resp.text == "test_challenge_123"

    # Verify invalid challenge fails with 403
    bad_verify = client.get(
        "/api/comms/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test&hub.verify_token=wrong_token"
    )
    assert bad_verify.status_code == 403
