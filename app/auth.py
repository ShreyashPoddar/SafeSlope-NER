import os
import time
import jwt
from fastapi import Header, HTTPException, status

# --- Machine-to-machine: Members 2/4/6's services calling your gateway ---
# Sent as a header: X-API-Key: <value>
API_KEY = os.environ.get("SERVICE_API_KEY", "dev-only-change-me")


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


# --- Human sessions: a DDMA official logged into Member 5's dashboard ---
# After /auth/google succeeds, the dashboard sends this back on every
# request as: Authorization: Bearer <session token>
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-change-me-too")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = 60 * 60 * 12  # 12 hours


def create_session_token(user: dict) -> str:
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
        "exp": int(time.time()) + JWT_EXPIRY_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    token = authorization.removeprefix("Bearer ")
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

