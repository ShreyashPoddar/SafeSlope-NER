"""
SafeSlope-NER — Authentication & RBAC
Covers: Section 3.4 (HMAC-SHA256 gateway authentication),
        Section 8.3 (RBAC: Public / Volunteer / Operator / Magistrate),
        Section 8.2 (DM PIN hash for HITL authorization)
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, Request, status

from app.core.config import get_settings

settings = get_settings()

# ─────────────────────────────────────────────────────────────────────────────
# API KEY — Machine-to-machine (Members 2/3/4/6 services)
# ─────────────────────────────────────────────────────────────────────────────
API_KEY = settings.SERVICE_API_KEY


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


# ─────────────────────────────────────────────────────────────────────────────
# JWT SESSION — Human dashboard users (Member 5's React frontend)
# ─────────────────────────────────────────────────────────────────────────────

def create_session_token(user: dict) -> str:
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
        "exp": int(time.time()) + settings.JWT_EXPIRY_SECONDS,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    token = authorization.removeprefix("Bearer ")
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )


# ─────────────────────────────────────────────────────────────────────────────
# ROLE-BASED ACCESS CONTROL (Section 8.3)
# Roles: ROLE_PUBLIC < ROLE_VOLUNTEER < ROLE_OPERATOR < ROLE_MAGISTRATE
# ─────────────────────────────────────────────────────────────────────────────

ROLE_HIERARCHY = {
    "ROLE_PUBLIC": 0,
    "ROLE_VOLUNTEER": 1,
    "ROLE_OPERATOR": 2,
    "ROLE_MAGISTRATE": 3,
}


def _require_role(minimum_role: str):
    async def dependency(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role", "ROLE_PUBLIC")
        if ROLE_HIERARCHY.get(user_role, 0) < ROLE_HIERARCHY.get(minimum_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' is insufficient. Required: {minimum_role}",
            )
        return user
    return dependency


# Reusable role-gated dependencies
require_role_volunteer   = _require_role("ROLE_VOLUNTEER")
require_role_operator    = _require_role("ROLE_OPERATOR")
require_role_magistrate  = _require_role("ROLE_MAGISTRATE")


# ─────────────────────────────────────────────────────────────────────────────
# HMAC-SHA256 GATEWAY AUTHENTICATION (Section 3.4)
# All LoRa concentrator gateways sign their binary payloads with the
# shared GATEWAY_HMAC_SECRET using HMAC-SHA256.
# Header name: X-Signature-SHA256
# ─────────────────────────────────────────────────────────────────────────────

def verify_gateway_hmac(raw_body: bytes, x_signature_sha256: str) -> bool:
    """
    Verifies HMAC-SHA256 signature over raw binary payload.
    Returns True on match, False on mismatch.
    Unsigned / mismatched requests must be rejected with HTTP 401 (Section 3.4).
    """
    expected_sig = hmac.new(
        settings.GATEWAY_HMAC_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_sig, x_signature_sha256.lower().replace("sha256=", ""))


async def require_gateway_hmac(
    request: Request,
    x_signature_sha256: str = Header(..., description="HMAC-SHA256 over raw binary payload"),
) -> bytes:
    """
    FastAPI dependency — reads raw body and validates HMAC signature.
    Returns raw bytes for downstream binary parsing.
    """
    raw_body = await request.body()
    if not verify_gateway_hmac(raw_body, x_signature_sha256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="HMAC-SHA256 signature mismatch — unauthorized gateway",
        )
    return raw_body


# ─────────────────────────────────────────────────────────────────────────────
# DM PIN HASH (Section 8.2 — HITL Authorization)
# The District Magistrate's 6-digit PIN is stored as a bcrypt hash.
# ─────────────────────────────────────────────────────────────────────────────

def hash_dm_pin(pin: str) -> str:
    """Bcrypt hash of a 6-digit DM authorization PIN."""
    return bcrypt.hashpw(
        pin.encode(),
        bcrypt.gensalt(rounds=settings.DM_PIN_BCRYPT_ROUNDS),
    ).decode()


def verify_dm_pin(pin: str, stored_hash: str) -> bool:
    """Verify a DM PIN against its bcrypt hash."""
    return bcrypt.checkpw(pin.encode(), stored_hash.encode())
