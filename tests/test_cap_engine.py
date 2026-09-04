"""
Unit tests for Member 6 National Alerting Protocol (CAP) Compliance Engine
Validates ITU-T X.1303 & NDMA SACHET Common Alerting Protocol v1.2 XML output.
"""

import xml.etree.ElementTree as ET
from app.comms.cap_engine import CAPAlert, cap_registry


def test_cap_alert_creation_and_fields():
    """Verify CAP alert fields conform to OASIS CAP 1.2 standards."""
    alert = CAPAlert(
        zone_name="Champhai-Serchhip Corridor",
        severity="Severe",
        urgency="Immediate",
        certainty="Likely",
        isolation_data={
            "isolated_villages": 3,
            "affected_population": 8400,
            "facilities_cut_off": ["NH-54 km 42"],
            "designated_bypass": "Eastern District Bypass Road B-7",
        },
    )

    assert alert.identifier.startswith("IN-NDMA-SACHET")
    assert alert.status == "Actual"
    assert alert.msg_type == "Alert"
    assert alert.scope == "Public"

    # Test dictionary output
    d = alert.to_dict()
    assert d["info"]["category"] == "Geo"
    assert d["info"]["severity"] == "Severe"
    assert d["info"]["urgency"] == "Immediate"
    assert "parameters" in d["info"]


def test_cap_xml_validity():
    """Verify generated XML parses and contains ITU-T X.1303 elements."""
    alert = CAPAlert(
        zone_name="Champhai - Serchhip Corridor",
        severity="Extreme",
        urgency="Immediate",
    )
    xml_str = alert.to_xml()

    # Parse with ElementTree to verify syntactical validity
    root = ET.fromstring(xml_str)
    assert "alert" in root.tag
    assert root.find("{urn:oasis:names:tc:emergency:cap:1.2}identifier") is not None or root.find("identifier") is not None

    # Check that Isolation Twin metrics are embedded in parameters
    assert "IsolationTwin" in xml_str
    assert "NDMA-SACHET" in xml_str


def test_cap_registry_lifecycle():
    """Verify alerts can be registered and retrieved."""
    alert = CAPAlert(zone_name="Test Zone")
    cap_registry.register(alert)

    retrieved = cap_registry.get(alert.identifier)
    assert retrieved is not None
    assert retrieved.zone_name == "Test Zone"
