"""
ResiliNER / SafeSlope-NER - Cross-Team Alert Dispatcher & Area Community Notification Engine
Member 6: Communications & Bot Developer

Integrates with:
- Member 1 (Lead): Automatic risk threshold triggers (physics floor vs ML / landslide algorithm)
- Member 3 (ML & Analytics): Pulls Isolation Twin metrics (isolated villages, cut-off highways, bypass routes)
- Member 5 (Full-Stack Dashboard): Live broadcast event feeds and GeoJSON streams

Area Notification Architecture (Solving lack of cellular tracking infrastructure):
In mountain corridors where telecom towers cannot actively track citizen locations, this system
maintains a geocoded Community Broadcast Directory of residents, Aapda Mitra disaster volunteers,
Village Council Presidents (VCPs), and transport operators. It executes a multi-tiered cascade:
1. Targeted Direct Alerts (WhatsApp & Cellular SMS) to everyone mapped to the affected corridor/village.
2. Village Amplifier Cascade: Instant alerts to Aapda Mitra and Village Heads to sound village sirens & church bells.
3. Multi-Channel Dispatch: WhatsApp, SMS (2G feature phones), Telegram, and NDMA SACHET CAP v1.2 Protocol.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import re

from app.comms.vernacular import get_text, SUPPORTED_LANGUAGES
from app.comms.cap_engine import CAPAlert, cap_registry
from app.comms.twilio_client import comms_client, normalize_phone_number
from app.comms.event_stream import broadcaster


# Pre-seeded community directory across key mountain corridors in Mizoram & North East
_INITIAL_COMMUNITY_SUBSCRIBERS: List[Dict[str, Any]] = [
    # --- Champhai - Serchhip Corridor (NH-54) ---
    {
        "phone": "+916351525923",
        "name": "Live Test Director",
        "role": "citizen",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "village": "Serchhip",
        "channel": "whatsapp",
        "lang": "en",
        "lat": 23.3150,
        "lng": 92.8540,
        "notes": "Verified Live WhatsApp Test Recipient (6351525923)",
        "telegram_chat_id": None,
    },
    {
        "phone": "+919436122880",
        "name": "Lalremruata",
        "role": "aapda_mitra",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "village": "Chhiahtlang",
        "channel": "whatsapp",
        "lang": "lus",
        "lat": 23.2840,
        "lng": 92.8460,
        "notes": "Aapda Mitra Team Leader (Controls community village siren & PA horn)",
        "telegram_chat_id": 987654321,
    },
    {
        "phone": "+919862044812",
        "name": "C. Vanlalpeka",
        "role": "village_head",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "village": "Serchhip",
        "channel": "sms",
        "lang": "lus",
        "lat": 23.3150,
        "lng": 92.8540,
        "notes": "Village Council President (VCP) - Sounds church warning bells",
        "telegram_chat_id": None,
    },
    {
        "phone": "+919436199123",
        "name": "Lalrinawma Colney",
        "role": "citizen",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "village": "Keitum",
        "channel": "whatsapp",
        "lang": "lus",
        "lat": 23.2380,
        "lng": 92.8710,
        "notes": "Resident on landslide-prone slope slope sector km 42",
        "telegram_chat_id": 987654322,
    },
    {
        "phone": "+919856123456",
        "name": "Yumnam Tomba",
        "role": "transport",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "village": "Baktawng",
        "channel": "whatsapp",
        "lang": "mni",
        "lat": 23.4120,
        "lng": 92.8930,
        "notes": "Mizoram Maxi-Cab Transport Union Representative",
        "telegram_chat_id": None,
    },
    {
        "phone": "+919435012345",
        "name": "Anirban Das",
        "role": "citizen",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "village": "Chhiahtlang",
        "channel": "sms",
        "lang": "bn",
        "lat": 23.2820,
        "lng": 92.8430,
        "notes": "Corridor merchant & supply truck operator",
        "telegram_chat_id": None,
    },
    # --- Aizawl South Mountain Slopes ---
    {
        "phone": "+919402177309",
        "name": "Bipul Kalita",
        "role": "aapda_mitra",
        "zone_name": "Aizawl South Mountain Slopes",
        "village": "Thingsulthliah",
        "channel": "whatsapp",
        "lang": "as",
        "lat": 23.6820,
        "lng": 92.8830,
        "notes": "Border Roads Org (BRO) Field Safety Marshal",
        "telegram_chat_id": 987654323,
    },
    {
        "phone": "+919774011223",
        "name": "Bantei Marbaniang",
        "role": "citizen",
        "zone_name": "Aizawl South Mountain Slopes",
        "village": "Aizawl South",
        "channel": "whatsapp",
        "lang": "kha",
        "lat": 23.7120,
        "lng": 92.7150,
        "notes": "PWD Assistant Engineer & resident",
        "telegram_chat_id": None,
    },
    {
        "phone": "+919863334455",
        "name": "K. Lalbiakzuala",
        "role": "village_head",
        "zone_name": "Aizawl South Mountain Slopes",
        "village": "Thingsulthliah",
        "channel": "sms",
        "lang": "lus",
        "lat": 23.6850,
        "lng": 92.8800,
        "notes": "Thingsulthliah VCP - Controls Community Public Address System",
        "telegram_chat_id": None,
    },
    # --- Lunglei Hill Cut Corridor ---
    {
        "phone": "+919862112233",
        "name": "Zonunsanga",
        "role": "aapda_mitra",
        "zone_name": "Lunglei Hill Cut Corridor",
        "village": "Zobawk",
        "channel": "whatsapp",
        "lang": "lus",
        "lat": 22.8620,
        "lng": 92.7530,
        "notes": "Aapda Mitra Disaster Volunteer",
        "telegram_chat_id": 987654324,
    },
    {
        "phone": "+919100000001",
        "name": "DEOC Duty Liaison",
        "role": "deoc",
        "zone_name": "Champhai - Serchhip Corridor (NH-54)",
        "village": "Serchhip",
        "channel": "any",
        "lang": "en",
        "lat": 23.3150,
        "lng": 92.8540,
        "notes": "District Emergency Operation Center Central Liaison",
        "telegram_chat_id": 987654325,
    },
]

_DISPATCH_LOGS: List[Dict[str, Any]] = []


class AlertDispatcher:
    """
    Dispatches geofenced, multilingual alerts and NDMA SACHET CAP broadcasts.
    Resolves the absence of cellular tracking infrastructure by maintaining an
    area-referenced Community Broadcast Directory and tiered amplifier network.
    """

    def __init__(self):
        self.subscribers: List[Dict[str, Any]] = list(_INITIAL_COMMUNITY_SUBSCRIBERS)
        self.active_telegram_chat_ids: set[int] = set()

    def register_telegram_chat(self, chat_id: int, name: str = "Telegram User"):
        """Records a live Telegram chat ID for broadcast distribution."""
        self.active_telegram_chat_ids.add(chat_id)
        # Also register as subscriber
        self.register_subscriber(
            phone=f"tg_{chat_id}",
            name=name,
            role="citizen",
            channel="telegram",
            telegram_chat_id=chat_id,
            notes="Live registered Telegram Bot user",
        )

    def register_subscriber(
        self,
        phone: str,
        name: str = "Corridor Resident",
        zone_name: str = "Champhai - Serchhip Corridor (NH-54)",
        village: Optional[str] = "Serchhip",
        role: str = "citizen",
        channel: str = "whatsapp",
        lang: str = "lus",
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        telegram_chat_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register or update a community member in the area alert directory."""
        if telegram_chat_id:
            self.active_telegram_chat_ids.add(telegram_chat_id)

        if phone.startswith("tg_"):
            clean_phone = phone
        else:
            _, clean_phone, _ = normalize_phone_number(phone)

        existing = next((s for s in self.subscribers if s["phone"] == clean_phone), None)
        if existing:
            existing.update({
                "name": name,
                "zone_name": zone_name,
                "village": village or existing.get("village", "Serchhip"),
                "role": role,
                "channel": channel,
                "lang": lang,
                "lat": lat if lat is not None else existing.get("lat"),
                "lng": lng if lng is not None else existing.get("lng"),
                "telegram_chat_id": telegram_chat_id or existing.get("telegram_chat_id"),
                "notes": notes or existing.get("notes"),
            })
            return existing

        new_sub = {
            "phone": clean_phone,
            "name": name,
            "zone_name": zone_name,
            "village": village or "Serchhip",
            "role": role,
            "channel": channel,
            "lang": lang,
            "lat": lat,
            "lng": lng,
            "telegram_chat_id": telegram_chat_id,
            "notes": notes or "Registered Community Member",
        }
        self.subscribers.append(new_sub)
        return new_sub

    def list_subscribers(
        self,
        zone_name: Optional[str] = None,
        village: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List registered community members with optional area filters."""
        res = self.subscribers
        if zone_name:
            res = [s for s in res if zone_name.lower() in s.get("zone_name", "").lower()]
        if village:
            res = [s for s in res if village.lower() in s.get("village", "").lower()]
        if role:
            res = [s for s in res if s.get("role") == role]
        return res

    def get_subscribers_for_area(
        self,
        zone_name: str,
        village: Optional[str] = None,
        audience_filter: str = "all_in_area",
    ) -> List[Dict[str, Any]]:
        """
        Geotargeted Area Lookup:
        Finds everyone registered in the target corridor/zone and applies audience filtering.
        If a specific village has very few subscribers, cascades to village heads and Aapda Mitra
        for the entire corridor so no community is left unwarned.
        """
        clean_zone = zone_name.strip().lower()

        # Match subscribers belonging to this corridor/zone
        matched = []
        for s in self.subscribers:
            s_zone = s.get("zone_name", "").strip().lower()
            if s_zone == clean_zone or clean_zone in s_zone or s_zone in clean_zone:
                matched.append(s)
            elif any(k in s_zone and k in clean_zone for k in ["serchhip", "champhai", "aizawl", "lunglei", "nh-54"]):
                matched.append(s)

        if not matched:
            matched = list(self.subscribers)

        # Apply Audience Filtering
        if audience_filter == "volunteers_only":
            filtered = [s for s in matched if s.get("role") in ["aapda_mitra", "village_head", "deoc"]]
            return filtered if filtered else matched
        elif audience_filter == "all_in_area":
            return matched
        else:
            return list(self.subscribers)

    async def evaluate_risk_trigger(
        self,
        zone_id: int,
        zone_name: str,
        risk_level: str,
        source: str,
        isolation_data: Optional[Dict[str, Any]] = None,
        force_broadcast: bool = False,
        notification_settings: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Main Cross-Team Alert Trigger & Broadcast Engine.
        Executes when the landslide prediction algorithm or physics floor clears the threshold.
        Applies dynamically calculated isolation metrics, area targeting, and multi-channel cascade.
        """
        if risk_level not in ["HIGH", "CRITICAL"] and not force_broadcast:
            return None

        settings = notification_settings or {}
        active_channels = settings.get("channels", ["whatsapp", "sms", "telegram", "cap", "siren"])
        target_audience = settings.get("target_audience", "all_in_area")
        selected_languages = settings.get("selected_languages") or list(SUPPORTED_LANGUAGES.keys())
        custom_instructions = settings.get("custom_instructions")
        urgency = settings.get("urgency", "Immediate")
        severity = settings.get("severity", "Severe" if risk_level == "HIGH" else "Extreme")

        # Dynamically calculate isolation metrics if not supplied
        if not isolation_data:
            from app.services.risk_calculator import calculate_complete_risk_profile
            calc_prof = calculate_complete_risk_profile(
                zone_name=zone_name,
                zone_id=zone_id,
            )
            iso_info = dict(calc_prof["isolation_metrics"])
            iso_info.update({
                "factor_of_safety": calc_prof["factor_of_safety"],
                "evacuation_window_hours": calc_prof["evacuation_window_hours"],
                "impact_radius_km": calc_prof["impact_radius_km"],
                "predicted_risk_pct": calc_prof["calculated_risk_pct"],
            })
        else:
            iso_info = isolation_data

        v_count = iso_info.get("isolated_villages", 1)
        p_count = iso_info.get("affected_population", 0)
        roads = iso_info.get("facilities_cut_off", [f"{zone_name} Corridor"])
        bypass_route = iso_info.get("designated_bypass", "Designated Emergency Bypass Road")
        fos_val = iso_info.get("factor_of_safety")
        evac_hrs = iso_info.get("evacuation_window_hours")

        fos_str = f"FoS {fos_val:.2f} (Unstable) | " if fos_val is not None else ""
        evac_str = f"Evac Window: {evac_hrs}h | " if evac_hrs is not None else ""
        cut_off_summary = f"{fos_str}{evac_str}{v_count} villages, {p_count} people cut-off expected. Impending block: {roads[0]}."

        # 1. Generate standard ITU-T X.1303 / NDMA SACHET CAP Alert
        cap_alert = CAPAlert(
            zone_name=zone_name,
            severity=severity,
            urgency=urgency,
            certainty="Likely" if "algorithm" in source or "ml" in source else "Observed",
            isolation_data=iso_info,
        )
        cap_registry.register(cap_alert)

        # 2. Compile Multilingual Emergency Messages in requested regional languages
        messages_by_lang: Dict[str, str] = {}
        for lang_code in selected_languages:
            base_msg = get_text(
                "alert_broadcast_high",
                lang=lang_code,
                zone_name=zone_name,
                trigger_source=source.replace("_", " ").title(),
                isolation_summary=cut_off_summary,
                bypass_route=bypass_route,
            )
            if custom_instructions:
                base_msg += f"\n\n📢 DEOC Directive: {custom_instructions}"
            messages_by_lang[lang_code] = base_msg

        # 3. Find Targeted Community Contacts for this Affected Corridor/Area
        targeted_subscribers = self.get_subscribers_for_area(
            zone_name=zone_name,
            audience_filter=target_audience,
        )

        # 4. Multi-Channel Cascade Delivery:
        # A) WhatsApp & Cellular SMS
        comms_res = comms_client.broadcast_alert(
            subscribers=targeted_subscribers,
            message_by_lang=messages_by_lang,
            default_lang="lus" if "lus" in messages_by_lang else "en",
            channels=[c for c in active_channels if c in ["whatsapp", "sms"]],
        )

        # B) Telegram Broadcast (including live registered chats)
        telegram_dispatched = 0
        if "telegram" in active_channels:
            from app.comms.telegram_bot import broadcast_telegram_alert
            chat_ids = [
                s["telegram_chat_id"]
                for s in targeted_subscribers
                if s.get("telegram_chat_id") is not None
            ]
            for cid in self.active_telegram_chat_ids:
                if cid not in chat_ids:
                    chat_ids.append(cid)
            if not chat_ids:
                chat_ids = [987654321, 987654322]
            
            tg_text = f"🚨 *EMERGENCY ALERT: {zone_name}*\n\n" + messages_by_lang.get("en", "")
            tg_res = broadcast_telegram_alert(chat_ids=chat_ids, message_text=tg_text)
            telegram_dispatched = tg_res.get("dispatched", 0)


        # C) Community Siren / Village PA Horns
        siren_activated = "siren" in active_channels
        village_horns_count = sum(1 for s in targeted_subscribers if s.get("role") in ["aapda_mitra", "village_head"])

        # Compile Targeted Villages and Roles reached
        villages_reached = list(set(s.get("village", "General Area") for s in targeted_subscribers))
        roles_reached = list(set(s.get("role", "citizen") for s in targeted_subscribers))

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        total_deliveries = comms_res["dispatched"] + telegram_dispatched

        dispatch_record = {
            "dispatch_id": f"DISP-{now_str[:10]}-{cap_alert.identifier[-6:]}",
            "cap_identifier": cap_alert.identifier,
            "zone_name": zone_name,
            "risk_level": risk_level,
            "source": source,
            "urgency": urgency,
            "severity": severity,
            "recipients_count": len(targeted_subscribers),
            "successful_deliveries": total_deliveries,
            "breakdown": {
                "whatsapp": comms_res.get("dispatched_whatsapp", 0),
                "sms": comms_res.get("dispatched_sms", 0),
                "telegram": telegram_dispatched,
                "cap_published": "cap" in active_channels,
                "village_sirens_activated": siren_activated,
                "siren_stations_triggered": village_horns_count if siren_activated else 0,
            },
            "targeted_villages": villages_reached,
            "roles_reached": roles_reached,
            "channels_used": active_channels,
            "isolation_metrics": iso_info,
            "dispatched_at": now_str,
            "sample_message_en": messages_by_lang.get("en", ""),
            "sample_message_mizo": messages_by_lang.get("lus", ""),
        }

        _DISPATCH_LOGS.insert(0, dispatch_record)
        if len(_DISPATCH_LOGS) > 100:
            _DISPATCH_LOGS.pop()

        # 5. Broadcast live event to Member 5's GIS stream
        broadcaster.publish_nowait("ALERT_BROADCAST_DISPATCHED", dispatch_record)

        return dispatch_record

    def list_dispatches(self, limit: int = 20) -> List[Dict[str, Any]]:
        return _DISPATCH_LOGS[:limit]


# Global Singleton Dispatcher
alert_dispatcher = AlertDispatcher()
