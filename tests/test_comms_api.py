"""
Integration tests for Member 6 FastAPI endpoints.
Tests WhatsApp webhook, verification queue review, CAP feeds, and demo UI endpoint.
"""

# API Tests for Member 6 Comms
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_and_demo_endpoints():
    """Verify root status and demo console HTML."""
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["member_6_comms"] == "Active"

    r_demo = client.get("/demo")
    assert r_demo.status_code == 200
    assert "SafeSlope" in r_demo.text
    assert "Member 6" in r_demo.text


def test_whatsapp_webhook_twiml():
    """Verify Twilio WhatsApp inbound webhook returns valid TwiML XML."""
    payload = {
        "From": "whatsapp:+919436122880",
        "Body": "Hi",
    }
    resp = client.post("/api/comms/webhook/whatsapp", data=payload)
    assert resp.status_code == 200
    assert "<Response>" in resp.text
    assert "<Message>" in resp.text
    assert "SafeSlope" in resp.text


def test_verification_queue_workflow():
    """Verify listing queue, filtering, and DEOC officer review."""
    # List reports
    r_list = client.get("/api/comms/queue")
    assert r_list.status_code == 200
    reports = r_list.json()
    assert len(reports) > 0

    first_rep = reports[0]
    rep_id = first_rep["id"]

    # Review action: Approve
    r_action = client.post(
        f"/api/comms/queue/{rep_id}/action",
        json={"action": "APPROVE", "officer_name": "Senior DEOC Officer", "deoc_notes": "Verified by field team"},
    )
    assert r_action.status_code == 200
    updated = r_action.json()
    assert updated["review_status"] == "VERIFIED_APPROVED"
    assert updated["verified"] is True
    assert updated["reviewed_by"] == "Senior DEOC Officer"


def test_cap_alert_endpoints():
    """Verify CAP alert listing, XML feed, and JSON feed."""
    r_list = client.get("/api/comms/cap")
    assert r_list.status_code == 200
    alerts = r_list.json()
    assert len(alerts) > 0

    identifier = alerts[0]["identifier"]

    # Test XML endpoint
    r_xml = client.get(f"/api/comms/cap/{identifier}.xml")
    assert r_xml.status_code == 200
    assert "application/xml" in r_xml.headers["content-type"]
    assert "<alert" in r_xml.text
    assert identifier in r_xml.text

    # Test JSON endpoint
    r_json = client.get(f"/api/comms/cap/{identifier}.json")
    assert r_json.status_code == 200
    assert r_json.json()["identifier"] == identifier


def test_broadcast_trigger():
    """Verify manual/automated emergency broadcast trigger."""
    payload = {
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "risk_level": "HIGH",
        "source": "physics_floor",
        "isolation_data": {
            "isolated_villages": 4,
            "affected_population": 11000,
            "facilities_cut_off": ["NH-54 km 42"],
            "designated_bypass": "Eastern District Bypass Road B-7",
        },
    }
    resp = client.post("/api/comms/broadcast/trigger", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "HIGH"
    assert "cap_identifier" in data
    assert data["recipients_count"] > 0
