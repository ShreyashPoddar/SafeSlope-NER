import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.models.schemas import GoogleLoginPayload
from app.database import database
from app.auth import create_session_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.environ.get(
    "GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback"
)


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


@router.get("/github/login")
async def github_login():
    """
    Visiting this endpoint in a browser sends you to GitHub's own login/
    consent page. This is the button the dashboard's "Sign in with GitHub"
    would link to.
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GITHUB_CLIENT_ID is not configured on the server",
        )
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        "&scope=read:user user:email"
    )
    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(code: str):
    """
    GitHub redirects back here with a one-time code after someone approves
    the login. We exchange that code for an access token, fetch their
    profile, create/find the user, and hand back a session token — same
    shape as the Google flow.
    """
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth is not configured on the server",
        )

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="GitHub login failed")

        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        gh_user = user_resp.json()

        email = gh_user.get("email")
        if not email:
            email_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails = email_resp.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = (
                primary["email"]
                if primary
                else f"{gh_user['id']}@users.noreply.github.com"
            )

    github_id = str(gh_user["id"])
    name = gh_user.get("name") or gh_user.get("login")

    user = await database.fetch_one(
        "SELECT * FROM users WHERE github_id = :gid", {"gid": github_id}
    )
    if not user:
        user = await database.fetch_one(
            """INSERT INTO users (github_id, email, name)
               VALUES (:gid, :email, :name)
               RETURNING id, github_id, email, name, role""",
            {"gid": github_id, "email": email, "name": name},
        )

    token = create_session_token(dict(user))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"email": user["email"], "name": user["name"], "role": user["role"]},
    }
