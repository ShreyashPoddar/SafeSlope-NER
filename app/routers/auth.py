import os
from fastapi import APIRouter, HTTPException, Depends
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.models.schemas import GoogleLoginPayload
from app.database import database
from app.auth import create_session_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")


@router.post("/google")
async def google_login(payload: GoogleLoginPayload):
    """
    The dashboard sends the ID token it got from Google's "Sign in with
    Google" button here. We verify it's genuinely from Google and meant
    for this app, then look up (or create) the user, and hand back a
    session token the dashboard uses on every request after this.
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID is not configured on the server",
        )

    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.id_token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_sub = idinfo["sub"]
    email = idinfo["email"]
    name = idinfo.get("name", "")

    user = await database.fetch_one(
        "SELECT * FROM users WHERE google_sub = :sub", {"sub": google_sub}
    )
    if not user:
        user = await database.fetch_one(
            """INSERT INTO users (google_sub, email, name)
               VALUES (:sub, :email, :name)
               RETURNING id, google_sub, email, name, role""",
            {"sub": google_sub, "email": email, "name": name},
        )

    token = create_session_token(dict(user))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"email": user["email"], "name": user["name"], "role": user["role"]},
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Lets the dashboard check who's currently logged in / whether the session is still valid."""
    return current_user
