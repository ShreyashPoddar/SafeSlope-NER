"""
ResiliNER / SafeSlope-NER - Conversational Bot Engine
Member 6: Communications & Bot Developer

Stateful two-way WhatsApp / Twilio conversational bot supporting:
- 6 North East regional languages (Assamese, Khasi, Mizo, Manipuri, Bengali, English)
- Inbound field hazard reporting workflow (Aapda Mitra volunteers & local citizens)
- Integrated Computer Vision AI classification of attached hazard photos
- Human-in-the-loop governance (routing to DEOC verification queue)
- Safe evacuation shelters & dynamic isolation twin bypass routes
"""

import time
import re
from typing import Dict, Any, Optional, Tuple
from app.comms.vernacular import (
    get_text,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
)
from app.comms.classifier import classify_field_photo
from app.comms.queue_service import queue_service
from app.comms.twilio_client import comms_client

# In-memory conversational session store: phone_number -> session dict
_USER_SESSIONS: Dict[str, Dict[str, Any]] = {}

HAZARD_MENU_CHOICES = {
    "1": ("Road Tension Crack", "HIGH"),
    "2": ("Surface Rockfall", "CRITICAL"),
    "3": ("Landslide Scar / Mudflow", "CRITICAL"),
    "4": ("Blocked Culvert / Drainage Failure", "MODERATE"),
    "5": ("Other Slope Hazard", "MODERATE"),
}

LANG_MENU_CHOICES = {
    "1": "en",
    "2": "as",
    "3": "kha",
    "4": "lus",
    "5": "mni",
    "6": "bn",
}


class ConversationalBotEngine:
    """Manages conversational state machine for citizen WhatsApp interaction."""

    def get_or_create_session(self, phone: str) -> Dict[str, Any]:
        cleaned_phone = phone.replace("whatsapp:", "").strip()
        if cleaned_phone not in _USER_SESSIONS:
            _USER_SESSIONS[cleaned_phone] = {
                "phone": cleaned_phone,
                "lang": DEFAULT_LANGUAGE,
                "state": "MENU",
                "in_progress_report": {},
                "last_active": time.time(),
            }
        session = _USER_SESSIONS[cleaned_phone]
        session["last_active"] = time.time()
        return session

    async def process_incoming_message(
        self,
        from_phone: str,
        body_text: str = "",
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        media_url: Optional[str] = None,
        media_bytes: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        sender_name: Optional[str] = None,
        sender_username: Optional[str] = None,
        channel: Optional[str] = None,
        telegram_chat_id: Optional[Any] = None,
        chat_id: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Process an inbound message from WhatsApp (Twilio/Meta), Telegram, or Web Simulator.
        Returns the bot's response message and metadata.
        """
        session = self.get_or_create_session(from_phone)
        text = (body_text or "").strip()
        lang = session["lang"]
        state = session["state"]

        # Cache metadata into session report
        if sender_name:
            session["in_progress_report"]["sender_name"] = sender_name
        if sender_username:
            session["in_progress_report"]["sender_username"] = sender_username
        if channel:
            session["in_progress_report"]["channel"] = channel
        elif from_phone.startswith("tg_"):
            session["in_progress_report"]["channel"] = "Telegram Bot"
        t_id = telegram_chat_id or chat_id
        if t_id:
            session["in_progress_report"]["telegram_chat_id"] = t_id

        # Universal resets
        normalized = text.lower()
        if normalized in ["hi", "hello", "menu", "start", "/start", "chibai", "help", "0"]:
            session["state"] = "MENU"
            session["in_progress_report"] = {}
            reply = f"{get_text('welcome_banner', lang)}\n\n{get_text('menu_prompt', lang)}"
            return self._finalize_reply(session, reply)

        if normalized in ["sos", "emergency", "police", "ambulance", "112", "1077"]:
            reply = get_text("sos_prompt", lang)
            return self._finalize_reply(session, reply)

        # Smart Direct Media Ingestion:
        # If user directly sends a photo while in MENU or starting up
        image_target = media_bytes or image_base64 or media_url
        if image_target and state in ["MENU", "AWAITING_HAZARD_TYPE"]:
            session["state"] = "AWAITING_PHOTO"
            state = "AWAITING_PHOTO"

        # -------------------------------------------------------------
        # STATE: MENU
        # -------------------------------------------------------------
        if state == "MENU":
            if text == "1":
                # Start hazard report
                session["state"] = "AWAITING_HAZARD_TYPE"
                session["in_progress_report"] = {}
                reply = get_text("report_step1_hazard", lang)
                return self._finalize_reply(session, reply)

            elif text == "2":
                # Shelters & Bypass Routes
                reply = f"{get_text('shelter_title', lang)}\n\n{get_text('shelter_default', lang)}"
                return self._finalize_reply(session, reply)

            elif text == "3":
                # DEOC SOS Hotlines
                reply = get_text("sos_prompt", lang)
                return self._finalize_reply(session, reply)

            elif text == "4":
                # Language Selection
                session["state"] = "AWAITING_LANG"
                reply = get_text("lang_select_prompt", lang)
                return self._finalize_reply(session, reply)

            elif lat and lng:
                # Direct location drop
                session["state"] = "AWAITING_PHOTO"
                session["in_progress_report"]["lat"] = lat
                session["in_progress_report"]["lng"] = lng
                reply = f"📍 Location pin received ({lat:.4f}°N, {lng:.4f}°E).\n\n{get_text('report_step2_photo', lang)}"
                return self._finalize_reply(session, reply)

            else:
                # Invalid choice
                reply = (
                    "⚠️ Invalid selection.\n\n"
                    f"{get_text('menu_prompt', lang)}"
                )
                return self._finalize_reply(session, reply)

        # -------------------------------------------------------------
        # STATE: AWAITING_LANG
        # -------------------------------------------------------------
        elif state == "AWAITING_LANG":
            if text in LANG_MENU_CHOICES:
                new_lang = LANG_MENU_CHOICES[text]
                session["lang"] = new_lang
                session["state"] = "MENU"
                lang_meta = SUPPORTED_LANGUAGES[new_lang]
                reply = (
                    f"{get_text('lang_updated', new_lang)}\n\n"
                    f"{get_text('menu_prompt', new_lang)}"
                )
                return self._finalize_reply(session, reply)
            else:
                reply = get_text("lang_select_prompt", lang)
                return self._finalize_reply(session, reply)

        # -------------------------------------------------------------
        # STATE: AWAITING_HAZARD_TYPE
        # -------------------------------------------------------------
        elif state == "AWAITING_HAZARD_TYPE":
            if text in HAZARD_MENU_CHOICES:
                hazard_name, default_sev = HAZARD_MENU_CHOICES[text]
                session["in_progress_report"]["hazard_type"] = hazard_name
                session["in_progress_report"]["default_severity"] = default_sev
                session["state"] = "AWAITING_PHOTO"
                reply = get_text("report_step2_photo", lang)
                return self._finalize_reply(session, reply)
            else:
                reply = (
                    "⚠️ Please choose a valid hazard number (1-5):\n\n"
                    f"{get_text('report_step1_hazard', lang)}"
                )
                return self._finalize_reply(session, reply)

        # -------------------------------------------------------------
        # STATE: AWAITING_PHOTO
        # -------------------------------------------------------------
        elif state == "AWAITING_PHOTO":
            # Check if photo is attached (via URL, raw bytes, or base64)
            image_target = media_bytes or image_base64 or media_url

            if image_target:
                # Run AI Computer Vision Classifier & Save Media
                saved_public_url = "/api/comms/samples/rockfall"
                try:
                    from app.comms.media_handler import download_media_bytes, save_media_file

                    if isinstance(image_target, bytes):
                        raw_bytes = image_target
                    elif isinstance(image_target, str) and image_target.startswith("data:image"):
                        import base64
                        raw_bytes = base64.b64decode(image_target.split(",", 1)[1])
                    elif isinstance(image_target, str) and (image_target.startswith("http") or image_target.startswith("/api")):
                        raw_bytes = download_media_bytes(image_target)
                    elif isinstance(image_target, str) and os.path.exists(image_target):
                        with open(image_target, "rb") as f:
                            raw_bytes = f.read()
                    else:
                        raw_bytes = b""

                    if raw_bytes:
                        local_path, saved_public_url = save_media_file(raw_bytes, filename_prefix="citizen_report")
                        cv_result = classify_field_photo(local_path)
                    else:
                        cv_result = classify_field_photo(image_target)

                    session["in_progress_report"]["classification"] = cv_result["tag"]
                    session["in_progress_report"]["confidence_pct"] = cv_result["confidence_pct"]
                    session["in_progress_report"]["severity"] = cv_result["severity"]
                    session["in_progress_report"]["image_url"] = saved_public_url
                    session["in_progress_report"]["ai_analyzed"] = True
                    session["in_progress_report"]["cv_details"] = cv_result
                    if text and text not in ["skip", "no", "phah lo", "skip photo", "next", "Photo attached", "Photo attached from mobile camera"]:
                        session["in_progress_report"]["raw_notes"] = text
                except Exception as e:
                    haz = session["in_progress_report"].get("hazard_type", "Road Hazard")
                    session["in_progress_report"]["classification"] = haz
                    session["in_progress_report"]["confidence_pct"] = 72.0
                    session["in_progress_report"]["severity"] = "HIGH"
                    session["in_progress_report"]["image_url"] = saved_public_url
            elif normalized in ["skip", "no", "phah lo", "skip photo", "next"]:
                haz = session["in_progress_report"].get("hazard_type", "Road Hazard")
                session["in_progress_report"]["classification"] = haz
                session["in_progress_report"]["confidence_pct"] = 65.0
                session["in_progress_report"]["severity"] = session["in_progress_report"].get("default_severity", "MODERATE")
                session["in_progress_report"]["image_url"] = None
                session["in_progress_report"]["ai_analyzed"] = False
            else:
                haz = session["in_progress_report"].get("hazard_type", "Road Hazard")
                session["in_progress_report"]["classification"] = haz
                session["in_progress_report"]["confidence_pct"] = 65.0
                session["in_progress_report"]["severity"] = session["in_progress_report"].get("default_severity", "MODERATE")
                session["in_progress_report"]["raw_notes"] = text

            session["state"] = "AWAITING_LOCATION"
            # If location was already captured earlier, ingest immediately
            if session["in_progress_report"].get("lat") and session["in_progress_report"].get("lng"):
                lat = session["in_progress_report"]["lat"]
                lng = session["in_progress_report"]["lng"]
                return await self._ingest_and_confirm(session, lat, lng, None, lang, from_phone)

            reply = get_text("report_step3_location", lang)
            return self._finalize_reply(session, reply)

        # -------------------------------------------------------------
        # STATE: AWAITING_LOCATION
        # -------------------------------------------------------------
        elif state == "AWAITING_LOCATION":
            return await self._ingest_and_confirm(session, lat, lng, text, lang, from_phone)

        # Fallback
        session["state"] = "MENU"
        reply = get_text("menu_prompt", lang)
        return self._finalize_reply(session, reply)

    async def _ingest_and_confirm(
        self,
        session: Dict[str, Any],
        lat: Optional[float],
        lng: Optional[float],
        text: Optional[str],
        lang: str,
        from_phone: str,
    ) -> Dict[str, Any]:
        """Ingests field report into DEOC queue and returns confirmation receipt."""
        rep = session["in_progress_report"]
        report_lat = lat or rep.get("lat") or 23.3102
        report_lng = lng or rep.get("lng") or 92.8524
        location_str = f"GPS: {report_lat:.4f}°N, {report_lng:.4f}°E"

        if text and not lat:
            location_str = text
            coords_match = re.search(r"(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)", text)
            if coords_match:
                try:
                    report_lat = float(coords_match.group(1))
                    report_lng = float(coords_match.group(2))
                except ValueError:
                    pass

        # Ingest into verification queue with full metadata
        final_report = await queue_service.ingest_report(
            hazard_type=rep.get("hazard_type", rep.get("classification", "Road Hazard")),
            classification=rep.get("classification", "Surface Rockfall"),
            confidence_pct=rep.get("confidence_pct", 78.5),
            severity=rep.get("severity", "HIGH"),
            lat=report_lat,
            lng=report_lng,
            sender_phone=from_phone,
            sender_name=rep.get("sender_name"),
            sender_username=rep.get("sender_username"),
            channel=rep.get("channel", "Telegram Bot" if from_phone.startswith("tg_") else "WhatsApp"),
            telegram_chat_id=rep.get("telegram_chat_id"),
            image_url=rep.get("image_url"),
            location_str=location_str,
            raw_notes=rep.get("raw_notes", text if text and not lat else f"Field report via {rep.get('channel', 'comms')} from {from_phone}"),
            cv_details=rep.get("cv_details"),
        )

        # Reset session to MENU
        session["state"] = "MENU"
        session["in_progress_report"] = {}

        # Deliver confirmation receipt
        conf_body = get_text(
            "report_confirm_body",
            lang,
            tracking_id=final_report["tracking_id"],
            classification=final_report["classification"],
            confidence=final_report["confidence_pct"],
            location_str=location_str,
            timestamp=final_report["submitted_at"],
        )
        reply = f"{get_text('report_confirm_title', lang)}\n\n{conf_body}\n\n{get_text('menu_prompt', lang)}"
        return self._finalize_reply(session, reply, extra_meta={"report": final_report})

    def _finalize_reply(
        self,
        session: Dict[str, Any],
        reply_text: str,
        extra_meta: Optional[Dict[str, Any]] = None,
        send_outbound_api: bool = False,
    ) -> Dict[str, Any]:
        """Format the reply and record outbox history."""
        comms_client.send_whatsapp(
            to_phone=session["phone"],
            body=reply_text,
            send_via_api=send_outbound_api,
        )

        response_payload = {
            "to": session["phone"],
            "reply": reply_text,
            "session_state": session["state"],
            "language": session["lang"],
        }
        if extra_meta:
            response_payload.update(extra_meta)
        return response_payload


# Global Singleton Bot Engine
bot_engine = ConversationalBotEngine()
