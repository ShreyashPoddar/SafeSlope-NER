"""
ResiliNER / SafeSlope-NER - DEOC Verification Queue & Human-in-the-Loop Service
Member 6: Communications & Bot Developer

Enforces human-in-the-loop governance:
Crowdsourced submissions from Aapda Mitra volunteers and local residents are
routed to Member 5's DEOC control dashboard for officer review, ensuring community
reports serve as supporting evidence rather than directly shifting regional threat calculations.
"""

import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.comms.event_stream import broadcaster
from app.database import database

# In-memory store for high-speed queue operations & local dev fallback
_IN_MEMORY_REPORTS: List[Dict[str, Any]] = []
_NEXT_REPORT_ID = 101


def _generate_tracking_id() -> str:
    now_str = datetime.now(timezone.utc).strftime("%y%m")
    rand_num = random.randint(1000, 9999)
    return f"SLOPE-{now_str}-{rand_num}"


class VerificationQueueService:
    def __init__(self):
        self._init_seed_data()

    def _init_seed_data(self):
        """Seed a few realistic field reports for immediate demo readiness."""
        seeds = [
            {
                "id": 1,
                "tracking_id": "SLOPE-2609-1402",
                "sender_phone": "+919436199201",
                "hazard_type": "Surface Rockfall",
                "classification": "Surface Rockfall",
                "confidence_pct": 90.1,
                "severity": "CRITICAL",
                "image_url": "/api/comms/samples/rockfall",
                "lat": 23.3150,
                "lng": 92.8540,
                "location_str": "NH-54 km 42 near Chhiahtlang",
                "raw_notes": "Boulders collapsed onto northbound lane after heavy shower",
                "review_status": "PENDING_REVIEW",
                "verified": False,
                "submitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "reviewed_by": None,
                "reviewed_at": None,
                "deoc_notes": None,
            },
            {
                "id": 2,
                "tracking_id": "SLOPE-2609-1188",
                "sender_phone": "+919862044812",
                "hazard_type": "Road Tension Crack",
                "classification": "Road Tension Crack",
                "confidence_pct": 74.3,
                "severity": "HIGH",
                "image_url": "/api/comms/samples/crack",
                "lat": 23.4720,
                "lng": 93.3280,
                "location_str": "Champhai Bypass Ridge km 14",
                "raw_notes": "Wide fissure opening along slope shoulder, approx 4 inches wide",
                "review_status": "PENDING_REVIEW",
                "verified": False,
                "submitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "reviewed_by": None,
                "reviewed_at": None,
                "deoc_notes": None,
            },
            {
                "id": 3,
                "tracking_id": "SLOPE-2609-0821",
                "sender_phone": "+919402177309",
                "hazard_type": "Blocked Culvert / Drainage Failure",
                "classification": "Blocked Culvert / Drainage Failure",
                "confidence_pct": 68.1,
                "severity": "MODERATE",
                "image_url": "/api/comms/samples/culvert",
                "lat": 23.2980,
                "lng": 92.8420,
                "location_str": "Serchhip Town Outskirts culvert #12",
                "raw_notes": "Heavy debris choked outlet, water overflowing onto tarmac",
                "review_status": "VERIFIED_APPROVED",
                "verified": True,
                "submitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "reviewed_by": "Officer L. Ralte (DEOC)",
                "reviewed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "deoc_notes": "Verified by PWD local field engineer; clearance crew dispatched",
            },
        ]
        for s in seeds:
            if not any(r["id"] == s["id"] for r in _IN_MEMORY_REPORTS):
                _IN_MEMORY_REPORTS.append(s)

    async def ingest_report(
        self,
        hazard_type: str,
        classification: str,
        confidence_pct: float,
        severity: str,
        lat: float,
        lng: float,
        sender_phone: str = "Unknown",
        sender_name: Optional[str] = None,
        sender_username: Optional[str] = None,
        channel: str = "WhatsApp",
        telegram_chat_id: Optional[Any] = None,
        image_url: Optional[str] = None,
        location_str: Optional[str] = None,
        raw_notes: Optional[str] = None,
        cv_details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Ingest incoming citizen/volunteer report into the review queue."""
        global _NEXT_REPORT_ID
        _NEXT_REPORT_ID += 1
        rep_id = _NEXT_REPORT_ID

        tracking_id = _generate_tracking_id()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        report_record = {
            "id": rep_id,
            "tracking_id": tracking_id,
            "sender_phone": sender_phone,
            "sender_name": sender_name or (f"@{sender_username}" if sender_username else sender_phone),
            "sender_username": sender_username,
            "channel": channel,
            "telegram_chat_id": telegram_chat_id,
            "hazard_type": hazard_type,
            "classification": classification,
            "confidence_pct": round(confidence_pct, 1),
            "severity": severity,
            "assessed_severity": severity,
            "image_url": image_url or "/api/comms/samples/crack",
            "lat": lat,
            "lng": lng,
            "location_str": location_str or f"GPS: {lat:.4f}°N, {lng:.4f}°E",
            "raw_notes": raw_notes or f"Crowdsourced field report via {channel} from {sender_phone}",
            "cv_details": cv_details or {},
            "review_status": "PENDING_REVIEW",
            "verified": False,
            "submitted_at": now_str,
            "reviewed_by": None,
            "reviewed_at": None,
            "deoc_notes": None,
            "assigned_unit": None,
        }

        # Store in memory for instant API responsiveness
        _IN_MEMORY_REPORTS.insert(0, report_record)

        # Attempt to persist to Postgres if database is connected
        try:
            query = """
                INSERT INTO reports (location, classification, confidence_pct, image_url, verified)
                VALUES (ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :classification, :confidence_pct, :image_url, FALSE)
                RETURNING id
            """
            row = await database.fetch_one(
                query,
                {
                    "lng": lng,
                    "lat": lat,
                    "classification": classification,
                    "confidence_pct": confidence_pct,
                    "image_url": image_url,
                },
            )
            if row:
                report_record["db_id"] = row["id"]
        except Exception:
            # Running standalone or table not yet migrated — in-memory store keeps it live
            pass

        # Broadcast live event to Member 5's GIS stream & localhost real-time dashboard
        broadcaster.publish_nowait("NEW_FIELD_REPORT", report_record)

        return report_record

    def list_reports(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List reports in queue, optionally filtered by status."""
        reports = _IN_MEMORY_REPORTS
        if status:
            status_upper = status.upper()
            reports = [r for r in reports if r["review_status"] == status_upper]
        return reports[:limit]

    def get_report(self, report_id: int) -> Optional[Dict[str, Any]]:
        for r in _IN_MEMORY_REPORTS:
            if r["id"] == report_id:
                return r
        return None

    async def review_report(
        self,
        report_id: int,
        action: str,  # "APPROVE" or "REJECT"
        officer_name: str = "DEOC Duty Officer",
        deoc_notes: Optional[str] = None,
        adjusted_severity: Optional[str] = None,
        assigned_unit: Optional[str] = None,
        notify_citizen: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """DEOC officer reviews and approves or rejects a crowdsourced report."""
        report = self.get_report(report_id)
        if not report:
            return None

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        is_approved = action.upper() == "APPROVE"

        report["review_status"] = "VERIFIED_APPROVED" if is_approved else "REJECTED"
        report["verified"] = is_approved
        report["reviewed_by"] = officer_name
        report["reviewed_at"] = now_str
        report["deoc_notes"] = deoc_notes or ("Confirmed by DEOC field operator" if is_approved else "Spurious / unverified report")

        if adjusted_severity:
            report["severity"] = adjusted_severity
            report["assessed_severity"] = adjusted_severity

        if assigned_unit:
            report["assigned_unit"] = assigned_unit

        # Notify Telegram citizen directly if submission originated from Telegram
        if notify_citizen and report.get("telegram_chat_id"):
            try:
                from app.comms.telegram_bot import send_assessment_notification
                send_assessment_notification(
                    chat_id=report["telegram_chat_id"],
                    report=report,
                    action=action,
                    notes=report["deoc_notes"],
                    officer_name=officer_name,
                    assigned_unit=assigned_unit,
                )
            except Exception as err:
                print(f"Notice: Could not dispatch Telegram assessment notification: {err}")

        # Update Postgres database if available
        if "db_id" in report or report_id:
            try:
                target_id = report.get("db_id", report_id)
                query = """
                    UPDATE reports
                    SET verified = :verified
                    WHERE id = :id
                """
                await database.execute(query, {"verified": is_approved, "id": target_id})
            except Exception:
                pass

        # Publish review event to Member 5's GIS stream & localhost real-time dashboard
        broadcaster.publish_nowait(
            "REPORT_REVIEWED",
            {
                "report_id": report_id,
                "tracking_id": report["tracking_id"],
                "status": report["review_status"],
                "verified": report["verified"],
                "reviewed_by": officer_name,
                "lat": report["lat"],
                "lng": report["lng"],
                "classification": report["classification"],
                "severity": report["severity"],
                "assigned_unit": report.get("assigned_unit"),
                "deoc_notes": report.get("deoc_notes"),
            },
        )

        return report

    def get_queue_stats(self) -> Dict[str, Any]:
        """Summary metrics for Member 5's DEOC dashboard header."""
        total = len(_IN_MEMORY_REPORTS)
        pending = sum(1 for r in _IN_MEMORY_REPORTS if r["review_status"] == "PENDING_REVIEW")
        approved = sum(1 for r in _IN_MEMORY_REPORTS if r["review_status"] == "VERIFIED_APPROVED")
        rejected = sum(1 for r in _IN_MEMORY_REPORTS if r["review_status"] == "REJECTED")
        return {
            "total_reports": total,
            "pending_review": pending,
            "verified_approved": approved,
            "rejected": rejected,
            "verification_rate_pct": round((approved / total * 100) if total > 0 else 0, 1),
        }

    def get_geojson_feature_collection(
        self,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Export crowdsourced hazard reports as an RFC 7946 compliant GeoJSON FeatureCollection.
        Compatible with QGIS, ArcGIS, MapLibre, Leaflet, and Member 5 GIS dashboards.
        """
        reports = self.list_reports(status=status)
        if channel:
            reports = [r for r in reports if r.get("channel", "").lower() == channel.lower()]
        if severity:
            reports = [r for r in reports if r.get("severity", "").upper() == severity.upper()]

        features = []
        for rep in reports:
            lat = rep.get("lat")
            lng = rep.get("lng")
            if lat is None or lng is None:
                continue

            features.append({
                "type": "Feature",
                "id": rep.get("id"),
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(float(lng), 6), round(float(lat), 6)],  # RFC 7946: [lng, lat]
                },
                "properties": {
                    "id": rep.get("id"),
                    "tracking_id": rep.get("tracking_id"),
                    "classification": rep.get("classification"),
                    "hazard_type": rep.get("hazard_type"),
                    "severity": rep.get("severity"),
                    "assessed_severity": rep.get("assessed_severity", rep.get("severity")),
                    "confidence_pct": rep.get("confidence_pct"),
                    "review_status": rep.get("review_status"),
                    "verified": rep.get("verified", False),
                    "channel": rep.get("channel", "WhatsApp"),
                    "sender_name": rep.get("sender_name"),
                    "sender_username": rep.get("sender_username"),
                    "sender_phone": rep.get("sender_phone"),
                    "telegram_chat_id": rep.get("telegram_chat_id"),
                    "image_url": rep.get("image_url"),
                    "location_str": rep.get("location_str"),
                    "raw_notes": rep.get("raw_notes"),
                    "assigned_unit": rep.get("assigned_unit"),
                    "reviewed_by": rep.get("reviewed_by"),
                    "deoc_notes": rep.get("deoc_notes"),
                    "submitted_at": rep.get("submitted_at"),
                    "google_maps_url": f"https://maps.google.com/?q={lat},{lng}",
                    "osm_url": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=16/{lat}/{lng}",
                },
            })

        return {
            "type": "FeatureCollection",
            "metadata": {
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "total_features": len(features),
                "crs": "urn:ogc:def:crs:OGC:1.3:CRS84",
                "source": "SafeSlope-NER Real-Time Citizen Telemetry & GIS Feed",
                "corridor": "Mizoram NH-54 & Champhai-Serchhip Corridor",
            },
            "features": features,
        }

    def get_corridor_zones_geojson(self) -> Dict[str, Any]:
        """
        GeoJSON layers for monitored mountain corridors and high-risk slope sections in Mizoram.
        Provides spatial reference context on the live map.
        """
        return {
            "type": "FeatureCollection",
            "metadata": {
                "name": "Mizoram Critical Mountain Corridors",
                "authority": "Mizoram DDMA & SafeSlope-NER",
            },
            "features": [
                {
                    "type": "Feature",
                    "id": "CORRIDOR-NH54",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [92.7176, 23.7271],  # Aizawl
                            [92.8350, 23.5100],  # Baktawng
                            [92.8540, 23.3150],  # Chhiahtlang / Serchhip
                            [92.8480, 23.1800],  # Keitum
                            [92.7300, 22.8800],  # Lunglei
                        ],
                    },
                    "properties": {
                        "name": "National Highway 54 (Aizawl - Serchhip - Lunglei)",
                        "corridor_id": "NH-54-MZ",
                        "risk_level": "HIGH",
                        "critical_km": "km 32 to km 68 (Chhiahtlang Sector)",
                        "soil_type": "Sedimentary Shale & Weathered Sandstone",
                    },
                },
                {
                    "type": "Feature",
                    "id": "ZONE-SERCHHIP",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [92.8300, 23.2900],
                            [92.8800, 23.2900],
                            [92.8800, 23.3400],
                            [92.8300, 23.3400],
                            [92.8300, 23.2900],
                        ]],
                    },
                    "properties": {
                        "name": "Serchhip Mountain Cut Hazard Zone",
                        "risk_level": "CRITICAL",
                        "active_faults": "Mat Fault Zone",
                        "primary_hazard": "Debris Flows & Slope Slumps",
                    },
                },
                {
                    "type": "Feature",
                    "id": "ZONE-CHAMPHAI",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [93.2800, 23.4400],
                            [93.3600, 23.4400],
                            [93.3600, 23.5100],
                            [93.2800, 23.5100],
                            [93.2800, 23.4400],
                        ]],
                    },
                    "properties": {
                        "name": "Champhai Ridge Fracture Corridor",
                        "risk_level": "HIGH",
                        "active_faults": "Indo-Burma Wedge Transverse Shear",
                        "primary_hazard": "Road Tension Cracks & Boulders",
                    },
                },
            ],
        }


# Global Singleton Queue Service
queue_service = VerificationQueueService()
