"""
ResiliNER / SafeSlope-NER - WhatsApp & SMS Multi-Gateway Client
Member 6: Communications & Bot Developer

Supports:
1. Meta WhatsApp Cloud API (v19.0 / v20.0 official Graph API)
2. Twilio WhatsApp & SMS API
3. High-Fidelity Local Simulation Mode (zero-cost offline hackathon demo)

Features dynamic environment hot-reloading (load_dotenv(override=True))
so newly added API keys in .env take effect immediately without server restarts.
"""

import os
import re
import time
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv

# Initial load of .env
load_dotenv()


def reload_env_credentials():
    """Reloads .env file from disk to pick up newly added API credentials."""
    try:
        load_dotenv(override=True)
    except Exception:
        pass


def get_meta_credentials() -> tuple[str, str, str]:
    """Returns (meta_token, phone_number_id, verify_token) fresh from environment."""
    reload_env_credentials()
    token = (
        os.environ.get("META_WHATSAPP_TOKEN")
        or os.environ.get("META_WA_TOKEN")
        or ""
    ).strip()
    phone_id = (
        os.environ.get("META_WHATSAPP_PHONE_ID")
        or os.environ.get("META_PHONE_NUMBER_ID")
        or ""
    ).strip()
    verify_token = os.environ.get("META_VERIFY_TOKEN", "safeslope_secret_verify_token_2026").strip()
    return token, phone_id, verify_token


def get_twilio_credentials() -> tuple[str, str, str, str]:
    """Returns (account_sid, auth_token, whatsapp_from, sms_from) fresh from environment."""
    reload_env_credentials()
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
    token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    wa_from = os.environ.get("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886").strip()
    sms_from = os.environ.get("TWILIO_PHONE_NUMBER", wa_from.replace("whatsapp:", "")).strip()
    return sid, token, wa_from, sms_from


def normalize_phone_number(raw_phone: str) -> tuple[str, str, str]:
    """
    Normalizes a phone string into:
    (clean_digits, e164_str, twilio_recipient)
    e.g. '6351525923' -> ('916351525923', '+916351525923', 'whatsapp:+916351525923')
    """
    clean = raw_phone.replace("whatsapp:", "").strip()
    digits = re.sub(r"[^\d]", "", clean)
    # If 10 digits starting with 6, 7, 8, 9, assume India (+91)
    if len(digits) == 10 and digits[0] in "6789":
        digits = f"91{digits}"
    e164 = f"+{digits}"
    wa_recipient = f"whatsapp:{e164}"
    return digits, e164, wa_recipient


# Backwards compatibility module attributes
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
META_WA_TOKEN = os.environ.get("META_WA_TOKEN", "")
META_PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID", "")
META_WHATSAPP_TOKEN = os.environ.get("META_WHATSAPP_TOKEN", "")
META_WHATSAPP_PHONE_ID = os.environ.get("META_WHATSAPP_PHONE_ID", "")


def __getattr__(name: str):
    """Dynamic module-level attribute lookup to allow hot-reloading of .env variables."""
    reload_env_credentials()
    if name in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_NUMBER", "TWILIO_PHONE_NUMBER"):
        return os.environ.get(name, "")
    if name in ("META_WHATSAPP_TOKEN", "META_WA_TOKEN"):
        return os.environ.get("META_WHATSAPP_TOKEN") or os.environ.get("META_WA_TOKEN") or ""
    if name in ("META_WHATSAPP_PHONE_ID", "META_PHONE_NUMBER_ID"):
        return os.environ.get("META_WHATSAPP_PHONE_ID") or os.environ.get("META_PHONE_NUMBER_ID") or ""
    if name == "META_VERIFY_TOKEN":
        return os.environ.get("META_VERIFY_TOKEN", "safeslope_secret_verify_token_2026")
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


class CommsGatewayClient:
    """
    Manages dispatching outbound WhatsApp & SMS messages across Meta Cloud API,
    Twilio REST API, and Local Simulation Mode.
    """

    def __init__(self):
        self.outbox_history: List[Dict[str, Any]] = []

    @property
    def is_meta_live(self) -> bool:
        token, phone_id, _ = get_meta_credentials()
        return bool(
            token
            and phone_id
            and not token.lower().startswith("change-")
            and not token.lower().startswith("your_")
            and not phone_id.lower().startswith("change-")
            and not phone_id.lower().startswith("your_")
        )

    @property
    def is_twilio_live(self) -> bool:
        sid, token, _, _ = get_twilio_credentials()
        return bool(
            sid
            and token
            and not sid.lower().startswith("change-")
            and not sid.lower().startswith("ac_xxxx")
            and not token.lower().startswith("change-")
        )

    @property
    def is_live(self) -> bool:
        """True if either Meta WhatsApp or Twilio is configured with valid credentials."""
        return self.is_meta_live or self.is_twilio_live

    @property
    def active_provider(self) -> str:
        """Returns the primary active outbound WhatsApp provider name."""
        if self.is_meta_live:
            return "META_WHATSAPP"
        if self.is_twilio_live:
            return "TWILIO"
        return "SIMULATED"

    @property
    def twilio_whatsapp_number(self) -> str:
        _, _, wa_from, _ = get_twilio_credentials()
        return wa_from

    @property
    def meta_phone_id(self) -> str:
        _, phone_id, _ = get_meta_credentials()
        return phone_id

    def send_whatsapp(
        self,
        to_phone: str,
        body: str,
        media_url: Optional[str] = None,
        send_via_api: bool = True,
        preferred_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message via Meta Cloud API or Twilio WhatsApp.
        Automatically normalizes phone numbers for both providers.
        Falls back to high-fidelity simulation mode if no live credentials are active.
        """
        clean_digits, clean_e164, twilio_recipient = normalize_phone_number(to_phone)

        record: Dict[str, Any] = {
            "id": f"msg_{int(time.time() * 1000)}_{len(self.outbox_history) + 1}",
            "to": twilio_recipient,
            "recipient_digits": clean_digits,
            "body": body,
            "media_url": media_url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "QUEUED",
            "provider": self.active_provider,
        }

        # Check provider selection
        meta_token, meta_phone_id, _ = get_meta_credentials()
        twilio_sid, twilio_token, twilio_from, _ = get_twilio_credentials()

        use_meta = False
        use_twilio = False

        if preferred_provider:
            pref = preferred_provider.upper()
            if pref in ("META", "META_WHATSAPP", "CLOUD_API") and self.is_meta_live:
                use_meta = True
            elif pref in ("TWILIO", "TWILIO_WHATSAPP") and self.is_twilio_live:
                use_twilio = True

        if not use_meta and not use_twilio:
            if self.is_meta_live:
                use_meta = True
            elif self.is_twilio_live:
                use_twilio = True

        # --- 1. Dispatch via Meta WhatsApp Cloud API ---
        if use_meta and send_via_api:
            record["provider"] = "META_WHATSAPP"
            try:
                url = f"https://graph.facebook.com/v19.0/{meta_phone_id}/messages"
                headers = {
                    "Authorization": f"Bearer {meta_token}",
                    "Content-Type": "application/json",
                }
                if media_url:
                    payload = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": clean_digits,
                        "type": "image",
                        "image": {
                            "link": media_url,
                            "caption": body,
                        },
                    }
                else:
                    payload = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": clean_digits,
                        "type": "text",
                        "text": {
                            "preview_url": False,
                            "body": body,
                        },
                    }

                resp = requests.post(url, json=payload, headers=headers, timeout=8)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    record["status"] = "SENT"
                    messages = data.get("messages", [])
                    if messages:
                        record["message_id"] = messages[0].get("id")
                    record["response"] = data
                else:
                    err_json = {}
                    try:
                        err_json = resp.json()
                    except Exception:
                        pass
                    err_code = err_json.get("error", {}).get("code")
                    # If error is 131047 (Re-engagement / 24-hour window limit), retry with Meta pre-approved hello_world template
                    if err_code == 131047:
                        tmpl_payload = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": clean_digits,
                            "type": "template",
                            "template": {
                                "name": "hello_world",
                                "language": {"code": "en_US"},
                            },
                        }
                        tmpl_resp = requests.post(url, json=tmpl_payload, headers=headers, timeout=8)
                        if tmpl_resp.status_code in (200, 201):
                            tmpl_data = tmpl_resp.json()
                            record["status"] = "SENT (TEMPLATE_FALLBACK)"
                            record["note"] = "Delivered via Meta hello_world template (24h customer window not open yet). Reply 'Hi' from phone to enable full text alerts."
                            messages = tmpl_data.get("messages", [])
                            if messages:
                                record["message_id"] = messages[0].get("id")
                        else:
                            record["status"] = "FAILED"
                            record["error"] = tmpl_resp.text
                    else:
                        record["status"] = "FAILED"
                        record["error"] = resp.text
            except Exception as e:
                record["status"] = "ERROR"
                record["error"] = str(e)

        # --- 2. Dispatch via Twilio REST API ---
        elif use_twilio and send_via_api:
            record["provider"] = "TWILIO"
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
                payload = {
                    "From": twilio_from if twilio_from.startswith("whatsapp:") else f"whatsapp:{twilio_from}",
                    "To": twilio_recipient,
                    "Body": body,
                }
                if media_url:
                    payload["MediaUrl"] = media_url

                resp = requests.post(
                    url,
                    data=payload,
                    auth=(twilio_sid, twilio_token),
                    timeout=8,
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    record["status"] = data.get("status", "SENT").upper()
                    record["sid"] = data.get("sid")
                else:
                    record["status"] = "FAILED"
                    record["error"] = resp.text
            except Exception as e:
                record["status"] = "ERROR"
                record["error"] = str(e)

        # --- 3. Offline / Simulation Mode ---
        else:
            record["provider"] = "SIMULATED"
            record["status"] = "DELIVERED (SIMULATED)"

        self.outbox_history.append(record)
        if len(self.outbox_history) > 100:
            self.outbox_history.pop(0)

        return record

    def send_sms(
        self,
        to_phone: str,
        body: str,
        send_via_api: bool = True,
    ) -> Dict[str, Any]:
        """
        Send a cellular SMS message (e.g. for non-smartphone 2G handsets).
        Falls back to simulation mode if live Twilio credentials are not set.
        """
        _, clean_phone, _ = normalize_phone_number(to_phone)

        record: Dict[str, Any] = {
            "id": f"sms_{int(time.time() * 1000)}_{len(self.outbox_history) + 1}",
            "to": clean_phone,
            "body": body,
            "channel": "SMS",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "QUEUED",
            "provider": "TWILIO_SMS" if self.is_twilio_live else "SIMULATED_SMS",
        }

        twilio_sid, twilio_token, _, sms_from = get_twilio_credentials()

        if self.is_twilio_live and send_via_api:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
                payload = {
                    "From": sms_from,
                    "To": clean_phone,
                    "Body": body,
                }
                resp = requests.post(
                    url,
                    data=payload,
                    auth=(twilio_sid, twilio_token),
                    timeout=8,
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    record["status"] = data.get("status", "SENT").upper()
                    record["sid"] = data.get("sid")
                else:
                    record["status"] = "FAILED"
                    record["error"] = resp.text
            except Exception as e:
                record["status"] = "ERROR"
                record["error"] = str(e)
        else:
            record["status"] = "DELIVERED (SIMULATED SMS)"

        self.outbox_history.append(record)
        if len(self.outbox_history) > 100:
            self.outbox_history.pop(0)

        return record

    def broadcast_alert(
        self,
        subscribers: List[Dict[str, Any]],
        message_by_lang: Dict[str, str],
        default_lang: str = "en",
        channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Dispatch geofenced alert in subscriber's selected regional language and channel."""
        active_channels = channels or ["whatsapp", "sms"]
        dispatched_wa = 0
        dispatched_sms = 0
        failed = 0

        for sub in subscribers:
            phone = sub.get("phone", "")
            if not phone:
                continue
            lang = sub.get("lang", default_lang)
            text = message_by_lang.get(lang, message_by_lang.get(default_lang, ""))
            preferred_channel = sub.get("channel", "whatsapp")

            # Dispatch WhatsApp if channel is active and subscriber prefers or is general
            if "whatsapp" in active_channels and preferred_channel in ["whatsapp", "any"]:
                res_wa = self.send_whatsapp(to_phone=phone, body=text)
                if "ERROR" in res_wa.get("status", "") or "FAILED" in res_wa.get("status", ""):
                    failed += 1
                else:
                    dispatched_wa += 1

            # Dispatch SMS if SMS channel is enabled
            if "sms" in active_channels and (preferred_channel in ["sms", "any"] or "whatsapp" not in active_channels):
                res_sms = self.send_sms(to_phone=phone, body=text)
                if "ERROR" in res_sms.get("status", "") or "FAILED" in res_sms.get("status", ""):
                    failed += 1
                else:
                    dispatched_sms += 1

        total_dispatched = dispatched_wa + dispatched_sms
        return {
            "total_recipients": len(subscribers),
            "dispatched": total_dispatched,
            "dispatched_whatsapp": dispatched_wa,
            "dispatched_sms": dispatched_sms,
            "failed": failed,
            "provider": self.active_provider,
        }

    def get_recent_outbox(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.outbox_history[-limit:]


# Global Singleton Client
comms_client = CommsGatewayClient()
