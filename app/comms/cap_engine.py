"""
ResiliNER / SafeSlope-NER - National Alerting Protocol (CAP) Compliance Engine
Member 6: Communications & Bot Developer

Generates ITU-T X.1303 & NDMA SACHET Common Alerting Protocol (CAP) v1.2 XML & JSON
ensuring compatibility with national emergency broadcasting infrastructure (C-DoT, NDMA SACHET, SEOC).
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import xml.etree.ElementTree as ET


class CAPAlert:
    """OASIS CAP v1.2 / ITU-T X.1303 Compliant Alert Object."""

    def __init__(
        self,
        identifier: Optional[str] = None,
        sender: str = "deoc.aizawl@safeslope.ndma.gov.in",
        status: str = "Actual",  # Actual, Exercise, Draft, Test
        msg_type: str = "Alert",  # Alert, Update, Cancel
        scope: str = "Public",
        zone_name: str = "Champhai-Serchhip Corridor",
        severity: str = "Severe",  # Extreme, Severe, Moderate, Minor
        urgency: str = "Immediate",  # Immediate, Expected, Future
        certainty: str = "Likely",  # Observed, Likely, Possible
        headline: Optional[str] = None,
        description: Optional[str] = None,
        instruction: Optional[str] = None,
        lat: float = 23.3102,
        lng: float = 92.8524,
        radius_km: float = 12.0,
        isolation_data: Optional[Dict[str, Any]] = None,
        language: str = "en-IN",
    ):
        now_utc = datetime.now(timezone.utc)
        self.identifier = identifier or f"IN-NDMA-SACHET-MZ-SLOPE-{now_utc.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.sender = sender
        self.sent = now_utc.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        self.expires = (now_utc + timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        self.status = status
        self.msg_type = msg_type
        self.scope = scope
        self.zone_name = zone_name
        self.severity = severity
        self.urgency = urgency
        self.certainty = certainty
        self.lat = lat
        self.lng = lng
        self.radius_km = radius_km
        self.language = language
        self.isolation_data = isolation_data or {}

        # Default standard NDMA headline & descriptions dynamically resolved
        self.headline = headline or f"LANDSLIDE ALERT: {severity.upper()} Threat Detected in {zone_name}"
        
        # If isolation data is not provided, dynamically compute it
        if not self.isolation_data:
            from app.services.risk_calculator import calculate_complete_risk_profile
            calc_prof = calculate_complete_risk_profile(
                zone_name=zone_name,
                lat=lat,
                lng=lng,
            )
            self.isolation_data = calc_prof["isolation_metrics"]
            self.isolation_data["factor_of_safety"] = calc_prof["factor_of_safety"]
            self.isolation_data["evacuation_window_hours"] = calc_prof["evacuation_window_hours"]
            self.radius_km = calc_prof["impact_radius_km"]

        iso_villages = self.isolation_data.get("isolated_villages", len(self.isolation_data.get("affected_villages", [1])))
        affected_pop = self.isolation_data.get("affected_population", 0)
        cut_off_roads = self.isolation_data.get("facilities_cut_off", [f"{zone_name} Main Highway"])
        bypass_route = self.isolation_data.get("designated_bypass", "Designated Emergency Bypass")
        fos_val = self.isolation_data.get("factor_of_safety")
        evac_hrs = self.isolation_data.get("evacuation_window_hours")

        fos_str = f"Geotechnical Factor of Safety: {fos_val:.2f}. " if fos_val is not None else ""
        evac_str = f"Estimated evacuation window: {evac_hrs} hrs. " if evac_hrs is not None else ""

        self.description = description or (
            f"Geotechnical slope instrumentation and predictive risk engine detected critical slope destabilization "
            f"in {zone_name}. {fos_str}{evac_str}Soil moisture is saturated and pore-water pressure exceeds safety margins. "
            f"Isolation Twin projects {iso_villages} settlements and {affected_pop} citizens at risk of road cutoff. "
            f"Impending blockages: {', '.join(cut_off_roads)}."
        )

        self.instruction = instruction or (
            f"EVACUATION ADVISORY: Inhabitants of low-lying and steep slope cuts must relocate to designated community relief shelters. "
            f"Traffic along {cut_off_roads[0] if cut_off_roads else zone_name} is suspended. "
            f"Emergency traffic must divert to {bypass_route}. Call DEOC Helpline 1077 / 112 for rescue assistance."
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert CAP Alert to dictionary / JSON structure."""
        return {
            "identifier": self.identifier,
            "sender": self.sender,
            "sent": self.sent,
            "status": self.status,
            "msgType": self.msg_type,
            "scope": self.scope,
            "code": ["NDMA-SACHET-v1.2", "ITU-T X.1303"],
            "info": {
                "language": self.language,
                "category": "Geo",
                "event": "Landslide Hazard Warning",
                "responseType": "Evacuate" if self.severity in ["Extreme", "Severe"] else "Monitor",
                "urgency": self.urgency,
                "severity": self.severity,
                "certainty": self.certainty,
                "eventCode": {"valueName": "SAME", "value": "LSW"},
                "expires": self.expires,
                "senderName": "SafeSlope-NER District Emergency Operation Center",
                "headline": self.headline,
                "description": self.description,
                "instruction": self.instruction,
                "web": "https://safeslope.ndma.gov.in/live-feed",
                "contact": "DEOC Control Room: 1077 / SEOC Mizoram: 112",
                "parameters": [
                    {"valueName": "IsolationTwin:CutOffCount", "value": str(self.isolation_data.get("isolated_villages", 0))},
                    {"valueName": "IsolationTwin:AffectedPopulation", "value": str(self.isolation_data.get("affected_population", 0))},
                    {"valueName": "IsolationTwin:DesignatedBypass", "value": str(self.isolation_data.get("designated_bypass", "Designated Emergency Bypass"))},
                    {"valueName": "Geotech:FactorOfSafety", "value": str(self.isolation_data.get("factor_of_safety", "N/A"))},
                    {"valueName": "Evacuation:WindowHours", "value": str(self.isolation_data.get("evacuation_window_hours", "N/A"))},
                ],
                "area": {
                    "areaDesc": self.zone_name,
                    "circle": f"{self.lat:.4f},{self.lng:.4f},{self.radius_km:.1f}",
                    "geocode": {"valueName": "NDMA_SUBDISTRICT", "value": "MZ-SER-01"},
                },
            },
        }

    def to_xml(self) -> str:
        """Serialize into official ITU-T X.1303 / OASIS CAP v1.2 XML string."""
        ns = "urn:oasis:names:tc:emergency:cap:1.2"
        root = ET.Element("alert", xmlns=ns)

        ET.SubElement(root, "identifier").text = self.identifier
        ET.SubElement(root, "sender").text = self.sender
        ET.SubElement(root, "sent").text = self.sent
        ET.SubElement(root, "status").text = self.status
        ET.SubElement(root, "msgType").text = self.msg_type
        ET.SubElement(root, "scope").text = self.scope
        ET.SubElement(root, "code").text = "NDMA-SACHET-1.2"

        info = ET.SubElement(root, "info")
        ET.SubElement(info, "language").text = self.language
        ET.SubElement(info, "category").text = "Geo"
        ET.SubElement(info, "event").text = "Landslide Hazard Warning"
        ET.SubElement(info, "responseType").text = "Evacuate" if self.severity in ["Extreme", "Severe"] else "Monitor"
        ET.SubElement(info, "urgency").text = self.urgency
        ET.SubElement(info, "severity").text = self.severity
        ET.SubElement(info, "certainty").text = self.certainty

        event_code = ET.SubElement(info, "eventCode")
        ET.SubElement(event_code, "valueName").text = "SAME"
        ET.SubElement(event_code, "value").text = "LSW"

        ET.SubElement(info, "expires").text = self.expires
        ET.SubElement(info, "senderName").text = "SafeSlope-NER District Emergency Operation Center"
        ET.SubElement(info, "headline").text = self.headline
        ET.SubElement(info, "description").text = self.description
        ET.SubElement(info, "instruction").text = self.instruction
        ET.SubElement(info, "web").text = "https://safeslope.ndma.gov.in/live-feed"
        ET.SubElement(info, "contact").text = "DEOC Helpline: 1077 / SEOC: 112"

        # Parameters for Member 3 Isolation Twin data
        for k, v in [
            ("IsolationTwin:CutOffCount", str(self.isolation_data.get("isolated_villages", 2))),
            ("IsolationTwin:AffectedPopulation", str(self.isolation_data.get("affected_population", 8400))),
            ("IsolationTwin:DesignatedBypass", self.isolation_data.get("designated_bypass", "Eastern District Bypass Road B-7")),
        ]:
            param = ET.SubElement(info, "parameter")
            ET.SubElement(param, "valueName").text = k
            ET.SubElement(param, "value").text = v

        area = ET.SubElement(info, "area")
        ET.SubElement(area, "areaDesc").text = self.zone_name
        ET.SubElement(area, "circle").text = f"{self.lat:.4f},{self.lng:.4f},{self.radius_km:.1f}"
        geocode = ET.SubElement(area, "geocode")
        ET.SubElement(geocode, "valueName").text = "NDMA_SUBDISTRICT"
        ET.SubElement(geocode, "value").text = "MZ-SER-01"

        # Pretty-print XML string
        xml_str = ET.tostring(root, encoding="utf-8")
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")


class CAPRegistry:
    """In-memory & persistent registry of generated CAP alerts."""

    def __init__(self):
        self._alerts: Dict[str, CAPAlert] = {}
        self._init_seed_alerts()

    def _init_seed_alerts(self):
        seed = CAPAlert(
            zone_name="Champhai - Serchhip Corridor (NH-54)",
            severity="Severe",
            urgency="Immediate",
            certainty="Observed",
            isolation_data={
                "isolated_villages": 3,
                "affected_population": 9200,
                "facilities_cut_off": ["NH-54 km 42 (Chhiahtlang)", "Thenzawl Link Road"],
                "designated_bypass": "Eastern District Bypass Road B-7",
            },
        )
        self._alerts[seed.identifier] = seed

    def register(self, alert: CAPAlert) -> CAPAlert:
        self._alerts[alert.identifier] = alert
        return alert

    def get(self, identifier: str) -> Optional[CAPAlert]:
        return self._alerts.get(identifier)

    def list_all(self, limit: int = 50) -> List[CAPAlert]:
        return list(self._alerts.values())[-limit:]


# Global Singleton Registry
cap_registry = CAPRegistry()
