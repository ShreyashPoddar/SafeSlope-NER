import os
import time
import asyncio
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv(override=True)

from app.comms.bot_engine import bot_engine


def get_token() -> str:
    """Retrieve Telegram Bot Token dynamically from environment."""
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()


def get_api_base() -> str:
    """Construct Telegram API Base URL."""
    return f"https://api.telegram.org/bot{get_token()}"


def get_updates(offset: int = None) -> list:
    url = f"{get_api_base()}/getUpdates"
    params = {"timeout": 20}
    if offset:
        params["offset"] = offset
    try:
        resp = requests.get(url, params=params, timeout=25)
        if resp.status_code == 200:
            return resp.json().get("result", [])
    except Exception as e:
        print(f"Polling error: {e}")
    return []


def send_message(chat_id: int, text: str, reply_markup: Optional[dict] = None):
    """Send message to a Telegram chat, optionally with custom keyboard."""
    url = f"{get_api_base()}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        r = requests.post(url, json=payload, timeout=2.5)
        if r.status_code != 200:
            # Fallback to plain text if Telegram rejects markdown
            payload.pop("parse_mode", None)
            requests.post(url, json=payload, timeout=2.5)
    except Exception:
        payload.pop("parse_mode", None)
        try:
            requests.post(url, json=payload, timeout=2.5)
        except Exception:
            pass


def send_assessment_notification(
    chat_id: int,
    report: Dict[str, Any],
    action: str,
    notes: Optional[str] = None,
    officer_name: str = "DEOC Duty Officer",
    assigned_unit: Optional[str] = None,
):
    """
    Sends real-time assessment feedback directly to the citizen on Telegram
    when an officer reviews their submission on localhost.
    """
    tracking_id = report.get("tracking_id", "SLOPE-REPORT")
    hazard = report.get("classification", "Slope Hazard")
    status_emoji = "✅ *VERIFIED & APPROVED*" if action.upper() == "APPROVE" else "❌ *REPORT REJECTED*"

    msg_lines = [
        "🛡️ *DISTRICT EMERGENCY OPERATION CENTER (DEOC)*",
        f"Incident Assessment Update for: `{tracking_id}`",
        "",
        f"Status: {status_emoji}",
        f"Hazard Category: *{hazard}*",
        f"Reviewed By: *{officer_name}*",
    ]

    if assigned_unit:
        msg_lines.append(f"🚒 Response Unit: *{assigned_unit}*")

    if notes:
        msg_lines.append(f"📋 Officer Remarks: _{notes}_")

    if action.upper() == "APPROVE":
        msg_lines.append("\nYour report is now live on the verified District GIS map. Thank you for safeguarding our hill corridors!")
    else:
        msg_lines.append("\nThis report could not be verified by field telemetry or was duplicate. Thank you for remaining vigilant.")

    full_text = "\n".join(msg_lines)
    send_message(chat_id, full_text)
    print(f"[Telegram Notification] Delivered assessment update to chat {chat_id} for {tracking_id}")


def download_telegram_file(file_id: str) -> bytes:
    """Download photo or document bytes directly from Telegram servers."""
    token = get_token()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured in environment")

    info_url = f"{get_api_base()}/getFile?file_id={file_id}"
    res = requests.get(info_url, timeout=12).json()
    if not res.get("ok"):
        raise RuntimeError(f"Telegram getFile error: {res.get('description', 'Unknown')}")

    file_path = res["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    resp = requests.get(download_url, timeout=25)
    resp.raise_for_status()
    return resp.content


def _build_telegram_keyboard(session_state: str) -> Optional[dict]:
    """Provides thumb-friendly mobile buttons for the citizen in Telegram."""
    if session_state == "AWAITING_LOCATION":
        return {
            "keyboard": [
                [{"text": "📍 Tap Here to Share Exact GPS Pin", "request_location": True}],
                [{"text": "0️⃣ Main Menu"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
    elif session_state == "AWAITING_HAZARD_TYPE":
        return {
            "keyboard": [
                [{"text": "1️⃣ Road Tension Crack"}, {"text": "2️⃣ Surface Rockfall"}],
                [{"text": "3️⃣ Landslide Scar / Mudflow"}, {"text": "4️⃣ Blocked Culvert"}],
                [{"text": "5️⃣ Other Slope Hazard"}, {"text": "0️⃣ Main Menu"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
    elif session_state == "AWAITING_PHOTO":
        return {
            "keyboard": [
                [{"text": "📸 Attach Photo via Camera/Gallery"}],
                [{"text": "📍 Skip to Location"}, {"text": "0️⃣ Main Menu"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
    elif session_state == "MENU":
        return {
            "keyboard": [
                [{"text": "1️⃣ Report Slope Hazard 📸"}, {"text": "2️⃣ Safe Shelters & Routes ⛺"}],
                [{"text": "3️⃣ Emergency SOS 🆘"}, {"text": "4️⃣ Language Selection 🌐"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False,
        }
    return None


async def handle_message(msg: dict):
    chat_id = msg["chat"]["id"]
    from_user = msg.get("from", {})
    user_id = from_user.get("id", chat_id)
    username = from_user.get("username", "")
    first_name = from_user.get("first_name", "")
    last_name = from_user.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip() or username or f"Telegram User {user_id}"
    user_identifier = f"tg_{user_id}"
    phone_display = f"@{username}" if username else f"TG: {full_name} ({user_id})"

    raw_text = msg.get("text", "")
    caption = msg.get("caption", "")
    text = (raw_text or caption or "").strip()

    # Normalize button text choices
    if "Report Slope Hazard" in text or text.startswith("1️⃣"):
        text = "1"
    elif "Safe Shelters" in text or text.startswith("2️⃣"):
        text = "2"
    elif "Emergency SOS" in text or text.startswith("3️⃣"):
        text = "3"
    elif "Language" in text or text.startswith("4️⃣"):
        text = "4"
    elif "Main Menu" in text or text.startswith("0️⃣"):
        text = "0"
    elif "Skip to Location" in text:
        text = "skip"

    lat = None
    lng = None
    media_bytes = None

    # 1. Check for Location pin
    if "location" in msg:
        loc = msg["location"]
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        text = "GPS Location Pin"

    # 2. Check for Photo
    if "photo" in msg and len(msg["photo"]) > 0:
        # Highest resolution photo is last in list
        best_photo = msg["photo"][-1]
        try:
            media_bytes = download_telegram_file(best_photo["file_id"])
            if not text:
                text = caption or "Photo attached from mobile camera"
        except Exception as err:
            print(f"⚠️ Error downloading Telegram photo: {err}")

    # 3. Check for Document image
    if not media_bytes and "document" in msg:
        doc = msg["document"]
        mime = doc.get("mime_type", "")
        if mime.startswith("image/"):
            try:
                media_bytes = download_telegram_file(doc["file_id"])
                if not text:
                    text = caption or "Document image attached"
            except Exception as err:
                print(f"⚠️ Error downloading Telegram document image: {err}")

    if media_bytes:
        print(f"[Telegram Photo] Received photo from {phone_display}! Running MobileNetV3 CV Classifier...")
    elif lat and lng:
        print(f"[Telegram GPS] Received GPS pin from {phone_display}: {lat:.4f}N, {lng:.4f}E")
    else:
        print(f"[Telegram Msg] Received message from {phone_display}: '{text}'")

    # Process through Member 6 Bot State Engine with full metadata
    reply_obj = await bot_engine.process_incoming_message(
        from_phone=user_identifier,
        body_text=text,
        lat=lat,
        lng=lng,
        media_bytes=media_bytes,
        sender_name=full_name,
        sender_username=username,
        channel="Telegram Bot",
        telegram_chat_id=chat_id,
        chat_id=chat_id,
    )

    # Build smart interactive keyboard based on next conversational state
    kb = _build_telegram_keyboard(reply_obj.get("session_state", "MENU"))
    send_message(chat_id, reply_obj["reply"], reply_markup=kb)
    print(f"[Telegram Reply] Sent reply to {phone_display} (State: {reply_obj.get('session_state')})")

    # Automatically register chat into live emergency broadcast directory
    try:
        from app.comms.dispatcher import alert_dispatcher
        alert_dispatcher.register_telegram_chat(chat_id=chat_id, name=full_name)
    except Exception:
        pass



def run_telegram_poller():
    token = get_token()
    if not token:
        print("=" * 65)
        print("100% FREE TELEGRAM BOT BRIDGE")
        print("=" * 65)
        print("TELEGRAM_BOT_TOKEN not found in .env")
        print("=" * 65)
        return

    # Verify Token with getMe
    try:
        me_resp = requests.get(f"{get_api_base()}/getMe", timeout=8)
        me_data = me_resp.json()
        if not me_data.get("ok"):
            print("=" * 65)
            print("❌ TELEGRAM AUTHENTICATION FAILED")
            print(f"Reason: {me_data.get('description', 'Unauthorized')}")
            print("=" * 65)
            return
        bot_info = me_data.get("result", {})
        bot_username = bot_info.get("username", "UnknownBot")
        bot_name = bot_info.get("first_name", "SafeSlope")
    except Exception as e:
        print(f"❌ Failed to reach Telegram API: {e}")
        return

    print("=" * 65)
    print(f"✅ SafeSlope-NER: Connected to Telegram as @{bot_username} ({bot_name})!")
    print(f"👉 You can message @{bot_username} on your phone to test live!")
    print("Real-time submissions will appear instantly on localhost dashboard.")
    print("Press Ctrl+C to stop.")
    print("=" * 65)

    last_offset = None
    while True:
        try:
            updates = get_updates(last_offset)
            for upd in updates:
                last_offset = upd["update_id"] + 1
                if "message" in upd:
                    asyncio.run(handle_message(upd["message"]))
        except KeyboardInterrupt:
            print("\nStopped Telegram poller.")
            break
        except Exception as exc:
            time.sleep(2)


def broadcast_telegram_alert(
    chat_ids: list[int],
    message_text: str,
) -> Dict[str, Any]:
    """
    Broadcast emergency warning to registered Telegram chats / channels.
    Falls back to simulated delivery if no bot token is set.
    """
    token = get_token()
    dispatched = 0
    failed = 0

    if not token or os.environ.get("TESTING"):
        # High-fidelity simulated Telegram delivery
        print(f"[Telegram Simulated Broadcast] Delivered to {len(chat_ids)} chats")
        return {
            "channel": "TELEGRAM",
            "total": len(chat_ids),
            "dispatched": len(chat_ids),
            "failed": 0,
            "provider": "SIMULATED_TELEGRAM",
        }

    for cid in chat_ids:
        try:
            send_message(cid, message_text)
            dispatched += 1
        except Exception:
            failed += 1

    return {
        "channel": "TELEGRAM",
        "total": len(chat_ids),
        "dispatched": dispatched,
        "failed": failed,
        "provider": "LIVE_TELEGRAM",
    }


def send_direct_test_alert(chat_id: int, message_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Direct test dispatch to a specific Telegram chat ID for live demos and verification.
    """
    token = get_token()
    if not token or os.environ.get("TESTING"):
        return {
            "status": "DELIVERED (SIMULATED)",
            "chat_id": chat_id,
            "provider": "SIMULATED_TELEGRAM",
            "message": message_text or "SafeSlope Test Alert",
        }

    alert_body = message_text or (
        "🚨 *SAFESLOPE-NER LIVE DEMO BROADCAST TEST*\n\n"
        "📍 *Corridor*: Champhai - Serchhip NH-54 (km 42.4)\n"
        "⚠️ *Status*: WARNING THRESHOLD BREACHED (78.5% Risk)\n"
        "🔬 *Geotech Physics*: Factor of Safety = 1.12 (Marginally Stable)\n"
        "⏱️ *Evacuation Window*: 4.5 hours\n"
        "🏘️ *Affected Area*: Chhiahtlang & Keitum cut-off expected\n"
        "🛣️ *Designated Bypass*: Keitum-Chhiahtlang Rural Link R-4\n"
        "⛺ *Safe Shelter*: Chhiahtlang Community Disaster Hall\n\n"
        "📞 *Helpline*: DEOC 1077 / Mizoram SEOC 112\n"
        "_This is a live system demonstration broadcast from Member 6 Communications Console._"
    )

    url = f"{get_api_base()}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": alert_body,
        "parse_mode": "Markdown",
    }
    try:
        r = requests.post(url, json=payload, timeout=5.0)
        res_data = r.json()
        if r.status_code == 200 and res_data.get("ok"):
            return {
                "status": "DELIVERED",
                "chat_id": chat_id,
                "provider": "LIVE_TELEGRAM",
                "message_id": res_data.get("result", {}).get("message_id"),
            }
        else:
            return {
                "status": "FAILED",
                "chat_id": chat_id,
                "error": res_data.get("description", "Unknown Telegram error"),
            }
    except Exception as exc:
        return {
            "status": "ERROR",
            "chat_id": chat_id,
            "error": str(exc),
        }


async def start_telegram_background_poller():
    """Asynchronous background poller designed to run inside FastAPI startup."""
    token = get_token()
    if not token:
        print("ℹ️ Telegram poller skipped: TELEGRAM_BOT_TOKEN not set in .env")
        return

    api_base = get_api_base()
    try:
        loop = asyncio.get_running_loop()
        me_resp = await loop.run_in_executor(None, lambda: requests.get(f"{api_base}/getMe", timeout=8).json())
        if not me_resp.get("ok"):
            print(f"⚠️ Telegram Bot disabled: {me_resp.get('description')}")
            return
        bot_info = me_resp.get("result", {})
        bot_username = bot_info.get("username", "UnknownBot")
        print(f"🤖 SafeSlope Telegram Bot LIVE in background as @{bot_username}!")
    except Exception as e:
        print(f"⚠️ Telegram background startup error: {e}")
        return

    last_offset = None
    while True:
        try:
            updates = await loop.run_in_executor(None, lambda: get_updates(last_offset))
            for upd in updates:
                last_offset = upd["update_id"] + 1
                if "message" in upd:
                    await handle_message(upd["message"])
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(2)


if __name__ == "__main__":
    run_telegram_poller()

