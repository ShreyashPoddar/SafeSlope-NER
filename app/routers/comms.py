"""
ResiliNER / SafeSlope-NER - Comms & Bot Router
Member 6: Communications & Bot Developer

Endpoints:
- POST /api/comms/webhook/whatsapp (Twilio & Meta WhatsApp inbound webhook)
- GET  /api/comms/webhook/whatsapp (Meta webhook verification challenge)
- POST /api/comms/classify (Upload image for instant CV hazard tagging)
- GET  /api/comms/queue (DEOC human-in-the-loop verification queue for Member 5)
- POST /api/comms/queue/{report_id}/action (DEOC officer Approve/Reject)
- GET  /api/comms/queue/stats (Verification metrics summary)
- GET  /api/comms/cap (List NDMA SACHET CAP alerts)
- GET  /api/comms/cap/{identifier}.xml (ITU-T X.1303 / NDMA SACHET CAP XML feed)
- GET  /api/comms/cap/{identifier}.json (CAP JSON feed)
- POST /api/comms/broadcast/trigger (Emergency broadcast dispatcher)
- GET  /api/comms/samples/{sample_key} (Curated test image assets)
- GET  /api/comms/stream (SSE real-time incident feed for Member 5's GIS map)
- POST /api/comms/simulate/message (Browser-based WhatsApp Simulator bridge)
- GET  /api/comms/outbox (Recent outbound messages log)
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, Response, Form, File, UploadFile, Query, HTTPException, status
from fastapi.responses import PlainTextResponse, StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel

from app.comms.vernacular import SUPPORTED_LANGUAGES, get_text
from app.comms.classifier import classify_field_photo
from app.comms.queue_service import queue_service
from app.comms.cap_engine import cap_registry, CAPAlert
from app.comms.bot_engine import bot_engine
from app.comms.dispatcher import alert_dispatcher
from app.comms.twilio_client import comms_client
from app.comms.event_stream import broadcaster
from app.comms.sample_media import build_sample_assets, SAMPLES_DIR, SAMPLE_GENERATORS

router = APIRouter(prefix="/api/comms", tags=["comms"])


# --- Pydantic Schemas ---
class ReviewActionPayload(BaseModel):
    action: str  # "APPROVE" or "REJECT"
    officer_name: Optional[str] = "DEOC Duty Officer"
    deoc_notes: Optional[str] = None
    adjusted_severity: Optional[str] = None
    assigned_unit: Optional[str] = None
    notify_citizen: Optional[bool] = True


class BroadcastTriggerPayload(BaseModel):
    zone_name: str = "Champhai - Serchhip Corridor (NH-54)"
    risk_level: str = "HIGH"
    source: str = "physics_floor"
    isolation_data: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None


class SimulatorMessagePayload(BaseModel):
    from_phone: str = "+919436122880"
    body: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    image_base64: Optional[str] = None
    sample_key: Optional[str] = None
    sender_name: Optional[str] = None
    sender_username: Optional[str] = None
    channel: Optional[str] = None
    telegram_chat_id: Optional[int] = None


# -------------------------------------------------------------------
# 1. WhatsApp Webhook (Twilio & Meta Format)
# -------------------------------------------------------------------
@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: Optional[str] = Form(None),
    Body: Optional[str] = Form(None),
    Latitude: Optional[float] = Form(None),
    Longitude: Optional[float] = Form(None),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None),
):
    """
    Twilio & Meta Inbound WhatsApp Webhook.
    Handles incoming messages, photos, and location coordinates.
    """
    from_phone = From or "+919436100000"
    body_text = Body or ""
    media_url = MediaUrl0

    is_meta_request = False
    # Handle JSON format if request is application/json (e.g. Meta Cloud API)
    if request.headers.get("content-type", "").startswith("application/json"):
        is_meta_request = True
        try:
            json_body = await request.json()
            # Parse Meta Cloud API structure if present
            entries = json_body.get("entry", [])
            if entries:
                changes = entries[0].get("changes", [])
                if changes:
                    value = changes[0].get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        msg = messages[0]
                        from_phone = msg.get("from", from_phone)
                        msg_type = msg.get("type", "text")
                        if msg_type == "text":
                            body_text = msg.get("text", {}).get("body", "")
                        elif msg_type == "location":
                            loc = msg.get("location", {})
                            Latitude = loc.get("latitude")
                            Longitude = loc.get("longitude")
                        elif msg_type == "image":
                            body_text = msg.get("image", {}).get("caption", "")
        except Exception:
            pass

    # Process through bot state engine
    bot_res = await bot_engine.process_incoming_message(
        from_phone=from_phone,
        body_text=body_text,
        lat=Latitude,
        lng=Longitude,
        media_url=media_url,
    )

    # If inbound is from Meta WhatsApp Cloud API, dispatch outbound reply via Meta Graph API
    if is_meta_request and comms_client.is_meta_live:
        comms_client.send_whatsapp(
            to_phone=from_phone,
            body=bot_res["reply"],
            preferred_provider="META_WHATSAPP",
        )
        return JSONResponse({"status": "ok", "delivered": True, "reply": bot_res["reply"]})

    # Return TwiML XML so Twilio speaks natively
    reply_escaped = (
        bot_res["reply"]
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    twiml_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_escaped}</Message>
</Response>"""

    return Response(content=twiml_xml, media_type="application/xml")


@router.get("/webhook/whatsapp")
def verify_meta_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """Verification challenge for Meta WhatsApp Cloud API setup."""
    from app.comms.twilio_client import get_meta_credentials
    _, _, expected_token = get_meta_credentials()
    if not expected_token:
        expected_token = "safeslope_secret_verify_token_2026"
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return PlainTextResponse(content=hub_challenge or "verified")
    return PlainTextResponse(content="Verification failed", status_code=403)


# -------------------------------------------------------------------
# 2. AI Field Media Classification Endpoint
# -------------------------------------------------------------------
@router.post("/classify")
async def classify_media(file: Optional[UploadFile] = File(None)):
    """Upload a field photo directly to run MobileNet / CV classification."""
    if not file:
        raise HTTPException(status_code=400, detail="No media file provided")

    contents = await file.read()
    res = classify_field_photo(contents)
    return res


# -------------------------------------------------------------------
# 3. DEOC Human-in-the-Loop Verification Queue (Member 5 Integration)
# -------------------------------------------------------------------
@router.get("/queue")
def list_verification_queue(status: Optional[str] = Query(None)):
    """List crowdsourced reports awaiting DEOC verification."""
    return queue_service.list_reports(status=status)


@router.get("/queue/stats")
def get_queue_statistics():
    """Summary metrics for Member 5's dashboard header."""
    return queue_service.get_stats() if hasattr(queue_service, "get_stats") else queue_service.get_queue_stats()


@router.post("/queue/{report_id}/action")
async def review_report_action(report_id: int, payload: ReviewActionPayload):
    """
    DEOC officer reviews and approves or rejects a crowdsourced report.
    Approved reports feed into the live verified GIS layer.
    """
    res = await queue_service.review_report(
        report_id=report_id,
        action=payload.action,
        officer_name=payload.officer_name or "DEOC Duty Officer",
        deoc_notes=payload.deoc_notes,
        adjusted_severity=payload.adjusted_severity,
        assigned_unit=payload.assigned_unit,
        notify_citizen=True if payload.notify_citizen is None else payload.notify_citizen,
    )
    if not res:
        raise HTTPException(status_code=404, detail="Report not found in queue")
    return res


# -------------------------------------------------------------------
# 4. National Alerting Protocol (CAP) Compliance Endpoints
# -------------------------------------------------------------------
@router.get("/cap")
def list_cap_alerts():
    """List active NDMA SACHET CAP alerts."""
    alerts = cap_registry.list_all()
    return [a.to_dict() for a in alerts]


@router.get("/cap/{identifier}.xml")
def get_cap_alert_xml(identifier: str):
    """Retrieve official ITU-T X.1303 / NDMA SACHET CAP v1.2 XML string."""
    alert = cap_registry.get(identifier)
    if not alert:
        raise HTTPException(status_code=404, detail="CAP Alert not found")
    return Response(content=alert.to_xml(), media_type="application/xml")


@router.get("/cap/{identifier}.json")
def get_cap_alert_json(identifier: str):
    """Retrieve CAP Alert JSON."""
    alert = cap_registry.get(identifier)
    if not alert:
        raise HTTPException(status_code=404, detail="CAP Alert not found")
    return alert.to_dict()


@router.post("/broadcast/trigger")
async def trigger_emergency_broadcast(payload: BroadcastTriggerPayload):
    """
    Manual or automated trigger for an emergency broadcast.
    Generates CAP alert and delivers localized WhatsApp/SMS/Telegram warnings to area subscribers.
    """
    res = await alert_dispatcher.evaluate_risk_trigger(
        zone_id=1,
        zone_name=payload.zone_name,
        risk_level=payload.risk_level,
        source=payload.source,
        isolation_data=payload.isolation_data,
        force_broadcast=True,
        notification_settings=payload.notification_settings,
    )
    return res or {"status": "No broadcast dispatched"}


@router.get("/broadcast/history")
def get_broadcast_history(limit: int = 20):
    """Retrieve recent emergency broadcast dispatch records."""
    return alert_dispatcher.list_dispatches(limit=limit)


# -------------------------------------------------------------------
# 4b. Landslide Risk Threshold Management & Area Directory Endpoints
# -------------------------------------------------------------------
@router.get("/thresholds")
def get_risk_thresholds():
    """Get active algorithm threshold settings and recent evaluation logs."""
    from app.services.threshold_engine import get_threshold_settings, get_recent_evaluations
    return {
        "settings": get_threshold_settings().model_dump(),
        "recent_evaluations": get_recent_evaluations(limit=10),
    }


@router.post("/thresholds")
def update_risk_thresholds(payload: Dict[str, Any]):
    """Dynamically adjust landslide risk algorithm thresholds."""
    from app.services.threshold_engine import update_threshold_settings
    updated = update_threshold_settings(payload)
    return {
        "status": "updated",
        "settings": updated.model_dump(),
    }


@router.get("/subscribers")
def list_community_subscribers(
    zone_name: Optional[str] = Query(None, description="Filter by corridor or zone"),
    village: Optional[str] = Query(None, description="Filter by village"),
    role: Optional[str] = Query(None, description="Filter by role (e.g. citizen, aapda_mitra, village_head)"),
):
    """
    List community members in the area notification directory.
    Solves lack of cellular tracking infrastructure by maintaining geocoded contacts.
    """
    return alert_dispatcher.list_subscribers(zone_name=zone_name, village=village, role=role)


@router.post("/subscribers")
def register_community_subscriber(payload: Dict[str, Any]):
    """
    Register or update a community member in the corridor broadcast directory.
    """
    if "phone" not in payload:
        raise HTTPException(status_code=400, detail="phone is required")
    sub = alert_dispatcher.register_subscriber(
        phone=payload["phone"],
        name=payload.get("name", "Corridor Resident"),
        zone_name=payload.get("zone_name", "Champhai - Serchhip Corridor (NH-54)"),
        village=payload.get("village", "Serchhip"),
        role=payload.get("role", "citizen"),
        channel=payload.get("channel", "whatsapp"),
        lang=payload.get("lang", "lus"),
        lat=payload.get("lat"),
        lng=payload.get("lng"),
        telegram_chat_id=payload.get("telegram_chat_id"),
        notes=payload.get("notes"),
    )
    return {"status": "registered", "subscriber": sub}



# -------------------------------------------------------------------
# 5. Sample Media Endpoints for Zero-Asset Demos & Testing
# -------------------------------------------------------------------
@router.get("/samples")
def list_sample_assets():
    """List available pre-generated hazard images."""
    paths = build_sample_assets()
    result = []
    for key, (fname, _, title) in SAMPLE_GENERATORS.items():
        result.append({
            "key": key,
            "title": title,
            "filename": fname,
            "url": f"/api/comms/samples/{key}",
        })
    return result


@router.get("/samples/{sample_key}")
def get_sample_image(sample_key: str):
    """Serve a sample hazard JPEG file directly."""
    build_sample_assets()
    if sample_key not in SAMPLE_GENERATORS:
        sample_key = "crack"
    fname, _, _ = SAMPLE_GENERATORS[sample_key]
    filepath = os.path.join(SAMPLES_DIR, fname)
    return FileResponse(filepath, media_type="image/jpeg")


# -------------------------------------------------------------------
# 6. Real-time Event Stream (SSE for Member 5's GIS Dashboard)
# -------------------------------------------------------------------
@router.get("/stream")
async def comms_event_stream():
    """Server-Sent Events (SSE) feed for live dashboard updates."""
    return StreamingResponse(
        broadcaster.subscribe(),
        media_type="text/event-stream",
    )


# -------------------------------------------------------------------
# 7. Real-Time Geospatial Live Feeds & GeoJSON Layers (RFC 7946)
# -------------------------------------------------------------------
@router.get("/geospatial/geojson")
@router.get("/geojson")
def get_geospatial_geojson_feed(
    status: Optional[str] = Query(None, description="Filter by review status (e.g. PENDING_REVIEW, VERIFIED_APPROVED)"),
    channel: Optional[str] = Query(None, description="Filter by reporting channel (e.g. Telegram Bot, WhatsApp)"),
    severity: Optional[str] = Query(None, description="Filter by severity (e.g. CRITICAL, HIGH, MODERATE, LOW)"),
):
    """
    RFC 7946 GeoJSON FeatureCollection stream for crowdsourced hazard locations.
    Directly ingestible by QGIS, ArcGIS, MapLibre, Leaflet, and Member 5 GIS Dashboard.
    """
    feed = queue_service.get_geojson_feature_collection(
        status=status,
        channel=channel,
        severity=severity,
    )
    return JSONResponse(content=feed, media_type="application/geo+json")


@router.get("/geospatial/zones")
def get_geospatial_corridor_zones():
    """
    GeoJSON layers representing monitored mountain transport corridors and hazard zones in Mizoram.
    """
    zones = queue_service.get_corridor_zones_geojson()
    return JSONResponse(content=zones, media_type="application/geo+json")


@router.get("/geospatial/feed")
def get_geospatial_summary_feed():
    """
    Live summary telemetry feed of all geospatial hazard coordinates with quick statistics.
    """
    geojson = queue_service.get_geojson_feature_collection()
    stats = queue_service.get_queue_stats()
    return {
        "status": "online",
        "protocol": "RFC 7946 GeoJSON",
        "live_features_count": geojson["metadata"]["total_features"],
        "stats": stats,
        "geojson_endpoint": "/api/comms/geospatial/geojson",
        "zones_endpoint": "/api/comms/geospatial/zones",
        "stream_endpoint": "/api/comms/stream",
    }


# -------------------------------------------------------------------
# 8. Interactive WhatsApp Simulator Bridge (Day 4 Demo Ready)
# -------------------------------------------------------------------
@router.post("/simulate/message")
async def simulate_whatsapp_message(payload: SimulatorMessagePayload):
    """
    Web Simulator endpoint: Allows interacting with the bot directly from
    the in-browser demo phone without needing cellular data or Twilio SMS balance.
    """
    # If a sample key was provided, load its sample image
    img_b64 = payload.image_base64
    if payload.sample_key and not img_b64:
        from app.comms.sample_media import get_sample_base64
        img_b64 = get_sample_base64(payload.sample_key)

    res = await bot_engine.process_incoming_message(
        from_phone=payload.from_phone,
        body_text=payload.body,
        lat=payload.lat,
        lng=payload.lng,
        image_base64=img_b64,
        sender_name=payload.sender_name,
        sender_username=payload.sender_username,
        channel=payload.channel,
        telegram_chat_id=payload.telegram_chat_id,
    )
    return res


@router.get("/outbox")
def get_comms_outbox(limit: int = 25):
    """View recent outgoing SMS / WhatsApp messages for verification."""
    return comms_client.get_recent_outbox(limit=limit)


@router.get("/languages")
def get_supported_languages():
    """List 6 supported North East regional languages."""
    return SUPPORTED_LANGUAGES


# -------------------------------------------------------------------
# 9. Live Demo Messaging Bridge (Telegram & Twilio Phone Testing)
# -------------------------------------------------------------------
class LiveDemoTestMessagePayload(BaseModel):
    target_type: str = "telegram"  # "telegram", "whatsapp", "sms"
    destination: str  # chat_id for telegram, phone number for whatsapp/sms
    zone_name: Optional[str] = "Champhai - Serchhip Corridor (NH-54)"
    custom_text: Optional[str] = None


@router.get("/live-demo/status")
def get_live_demo_status():
    """Returns the live connection status of Telegram and Twilio comms gateways."""
    from app.comms.telegram_bot import get_token, get_api_base
    import requests

    tg_token = get_token()
    tg_status = {"configured": bool(tg_token), "status": "OFFLINE", "bot_username": None}
    if tg_token:
        try:
            r = requests.get(f"{get_api_base()}/getMe", timeout=3)
            data = r.json()
            if data.get("ok"):
                tg_status["status"] = "LIVE_CONNECTED"
                tg_status["bot_username"] = data.get("result", {}).get("username")
                tg_status["bot_name"] = data.get("result", {}).get("first_name")
        except Exception:
            tg_status["status"] = "CONFIGURED_UNREACHABLE"

    twilio_configured = comms_client.is_twilio_live
    whatsapp_live = comms_client.is_live
    return {
        "telegram": tg_status,
        "whatsapp": {
            "configured": whatsapp_live,
            "provider": comms_client.active_provider,
            "meta_whatsapp": {
                "configured": comms_client.is_meta_live,
                "phone_number_id": comms_client.meta_phone_id if comms_client.is_meta_live else None,
            },
            "twilio": {
                "configured": twilio_configured,
                "whatsapp_number": comms_client.twilio_whatsapp_number,
            },
        },
        "twilio": {
            "configured": comms_client.is_live,
            "mode": comms_client.active_provider,
            "whatsapp_number": comms_client.twilio_whatsapp_number,
        },
        "registered_subscribers": len(alert_dispatcher.subscribers),
        "active_telegram_chats": list(alert_dispatcher.active_telegram_chat_ids),
    }


@router.post("/live-demo/test-message")
def send_live_demo_test_message(payload: LiveDemoTestMessagePayload):
    """
    Sends an instant live test alert directly to a real phone / Telegram chat
    for audience presentations and live demonstrations.
    """
    target = payload.target_type.lower()
    dest = payload.destination.strip()

    if target == "telegram":
        from app.comms.telegram_bot import send_direct_test_alert
        try:
            chat_id = int(dest)
        except ValueError:
            return JSONResponse(status_code=400, content={"error": "Telegram destination must be a numeric Chat ID"})
        
        res = send_direct_test_alert(chat_id=chat_id, message_text=payload.custom_text)
        return res

    elif target in ["whatsapp", "sms"]:
        if payload.custom_text:
            text = payload.custom_text
        else:
            from app.services.risk_calculator import calculate_complete_risk_profile
            calc = calculate_complete_risk_profile(zone_name=payload.zone_name)
            iso = calc["isolation_metrics"]
            text = (
                f"🚨 *SAFESLOPE-NER DYNAMIC ALERT*\n"
                f"Corridor: {payload.zone_name}\n"
                f"Factor of Safety: {calc['factor_of_safety']:.2f} ({'SHEAR FAILURE CRITICAL' if calc['is_physics_failure'] else 'UNSTABLE'})\n"
                f"Failure Prob: {calc['calculated_risk_pct']:.1f}% | Evac Window: {calc['evacuation_window_hours']} hrs\n"
                f"Runout Radius: {calc['impact_radius_km']} km | Pop at Risk: {iso['affected_population']:,}\n"
                f"Road Blockage: {iso['facilities_cut_off'][0]}\n"
                f"Designated Bypass: {iso['designated_bypass']}\n"
                f"Nearest Safe Shelter: {iso['nearest_shelter']} (Cap: {iso['nearest_shelter_capacity']})"
            )
        if target == "whatsapp":
            res = comms_client.send_whatsapp(to_phone=dest, body=text)
        else:
            res = comms_client.send_sms(to_phone=dest, body=text)
        return res

    else:
        return JSONResponse(status_code=400, content={"error": f"Unsupported target_type: {target}"})

