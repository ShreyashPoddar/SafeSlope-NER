import os
from fastapi import Header, HTTPException, status

# Every other member's service authenticates to your gateway with this
# shared key, sent as a header: X-API-Key: <value>
# Set a real value via the SERVICE_API_KEY env var — do not ship the
# default in anything beyond local dev.
API_KEY = os.environ.get("SERVICE_API_KEY", "dev-only-change-me")


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
