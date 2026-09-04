import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.database import database
from app.routers import telemetry, risk, reports, villages, auth, comms

app = FastAPI(title="ResiliNER API - SafeSlope-NER")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_telegram_task = None

@app.on_event("startup")
async def startup():
    global _telegram_task
    # Attempt Postgres connection with gentle retry; keep API alive if running standalone
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            await asyncio.wait_for(database.connect(), timeout=0.5)
            print("Connected to Postgres database.")
            break
        except Exception as exc:
            if attempt == max_attempts:
                print(f"Notice: Running in local memory/cache mode ({exc})")
                break
            await asyncio.sleep(0.2)

    # Launch free Telegram Bot poller in background if token exists (disabled in test mode)
    if not os.environ.get("TESTING"):
        try:
            from app.comms.telegram_bot import start_telegram_background_poller
            _telegram_task = asyncio.create_task(start_telegram_background_poller())
        except Exception as e:
            print(f"Notice: Telegram background poller not started ({e})")


@app.on_event("shutdown")
async def shutdown():
    global _telegram_task
    if _telegram_task:
        _telegram_task.cancel()
    try:
        if database.is_connected:
            await database.disconnect()
    except Exception:
        pass


from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse


@app.get("/")
def read_root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/demo", status_code=307)
    return {
        "status": "ResiliNER API running",
        "member_6_comms": "Active",
        "demo_console": "/demo",
        "docs": "/docs",
    }


@app.get("/demo", response_class=HTMLResponse)
def get_demo_page():
    """Serves the Member 6 Day 4 Live Demo Console & WhatsApp Web Simulator."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "demo", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SafeSlope Demo Console</h1><p>Demo index.html not found</p>"


@app.get("/mobile", response_class=HTMLResponse)
@app.get("/demo/mobile", response_class=HTMLResponse)
def get_mobile_page():
    """Serves the zero-install smartphone interface for real phone camera & GPS testing."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "demo", "mobile.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SafeSlope Mobile</h1><p>mobile.html not found</p>"


# Mount static uploads directory for citizen field photos
from fastapi.staticfiles import StaticFiles
from app.comms.media_handler import ensure_upload_dir

upload_dir = ensure_upload_dir()
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")



app.include_router(telemetry.router)
app.include_router(risk.router)
app.include_router(reports.router)
app.include_router(villages.router)
app.include_router(auth.router)
app.include_router(comms.router)

