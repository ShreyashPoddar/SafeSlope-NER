import os
import requests
from fastapi import APIRouter, HTTPException, Depends
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.models.schemas import GoogleLoginPayload, GitHubLoginPayload
from app.database import database
from app.auth import create_session_token, get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/google")
async def google_login(payload: GoogleLoginPayload):
    """
    The dashboard sends the ID token it got from Google's "Sign in with
    Google" button here. We verify it's genuinely from Google and meant
    for this app, then look up (or create) the user, and hand back a
    session token the dashboard uses on every request after this.
    """
    google_client_id = settings.GOOGLE_CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")
    if not google_client_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID is not configured on the server",
        )

    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.id_token, google_requests.Request(), google_client_id
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


@router.post("/github")
async def github_login(payload: GitHubLoginPayload):
    """
    Exchanges the GitHub temporary authorization code for an access token,
    fetches user profile from GitHub API, and creates or fetches the user
    in the database, returning a session JWT.
    """
    client_id = settings.GITHUB_CLIENT_ID or os.environ.get("GITHUB_CLIENT_ID", "")
    client_secret = settings.GITHUB_CLIENT_SECRET or os.environ.get("GITHUB_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET is not configured on the server",
        )

    # 1. Exchange temporary code for an access token
    token_url = "https://github.com/login/oauth/access_token"
    token_response = requests.post(
        token_url,
        headers={"Accept": "application/json"},
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": payload.code,
        },
        timeout=10,
    )
    if token_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to exchange GitHub authorization code")

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        error_desc = token_data.get("error_description", "Invalid GitHub authorization code")
        raise HTTPException(status_code=401, detail=error_desc)

    # 2. Fetch user profile from GitHub API
    user_response = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=10,
    )
    if user_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to fetch user profile from GitHub")

    gh_user = user_response.json()
    gh_id = str(gh_user["id"])
    email = gh_user.get("email") or f"{gh_user.get('login', gh_id)}@users.noreply.github.com"
    name = gh_user.get("name") or gh_user.get("login", "GitHub User")
    gh_sub = f"gh_{gh_id}"

    # 3. Look up or create user in database
    user = await database.fetch_one(
        "SELECT * FROM users WHERE google_sub = :sub OR email = :email",
        {"sub": gh_sub, "email": email},
    )
    if not user:
        user = await database.fetch_one(
            """INSERT INTO users (google_sub, email, name)
               VALUES (:sub, :email, :name)
               RETURNING id, google_sub, email, name, role""",
            {"sub": gh_sub, "email": email, "name": name},
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

