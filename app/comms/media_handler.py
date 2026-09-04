"""
ResiliNER / SafeSlope-NER - Field Media Ingestion & Storage Handler
Member 6: Communications & Bot Developer

Downloads and caches incoming WhatsApp media attachments (from Twilio / Meta),
saves them to local storage (app/static/uploads/), and exposes public URLs for Member 5's 3D GIS feed.
"""

import os
import io
import time
import uuid
from typing import Tuple, Optional
import requests
from PIL import Image

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))


def ensure_upload_dir() -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


def download_media_bytes(
    media_url: str,
    auth_user: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> bytes:
    """
    Download raw bytes from a remote URL.
    Supports Twilio Basic Auth if configured.
    """
    # Check if credentials in environment if targeting Twilio API
    if not auth_user and "api.twilio.com" in media_url:
        auth_user = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    auth = (auth_user, auth_token) if (auth_user and auth_token) else None

    # Handle local relative sample URLs (e.g. /api/comms/samples/rockfall)
    if media_url.startswith("/api/comms/samples/"):
        sample_key = media_url.split("/")[-1]
        from app.comms.sample_media import SAMPLE_GENERATORS, SAMPLES_DIR, ensure_samples_dir
        ensure_samples_dir()
        if sample_key in SAMPLE_GENERATORS:
            fname, gen_fn, _ = SAMPLE_GENERATORS[sample_key]
            path = os.path.join(SAMPLES_DIR, fname)
            if not os.path.exists(path):
                gen_fn().save(path, "JPEG")
            with open(path, "rb") as f:
                return f.read()

    headers = {
        "User-Agent": "ResiliNER-SafeSlope/1.0",
    }
    resp = requests.get(media_url, auth=auth, headers=headers, timeout=12)
    resp.raise_for_status()
    return resp.content


def save_media_file(
    content: bytes,
    filename_prefix: str = "field_report",
) -> Tuple[str, str]:
    """
    Saves image bytes to app/static/uploads/ and returns:
    (local_file_path, public_relative_url)
    """
    ensure_upload_dir()
    unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"
    filename = f"{filename_prefix}_{unique_id}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        pil_img = Image.open(io.BytesIO(content))
        # Ensure RGB format for JPEG
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        pil_img.save(filepath, "JPEG", quality=85)
    except Exception:
        # Fallback to direct binary write
        with open(filepath, "wb") as f:
            f.write(content)

    public_url = f"/uploads/{filename}"
    return filepath, public_url
