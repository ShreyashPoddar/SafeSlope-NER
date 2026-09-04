"""
SafeSlope-NER — FastAPI Application Entry Point
Registers all routers as per Section 12 (Codebase Directory Structure)
"""
import asyncio
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import database
from app.redis_client import get_redis, close_redis
from app.routers import telemetry, risk, reports, villages, auth, network_twin, tiles, governance, simulation

# Add workers/ to path for APScheduler meteo ingestion worker
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from workers.meteo_ingestion import start_meteo_worker, stop_meteo_worker
from workers.hardware_ngrok_bridge import start_hardware_bridge, stop_hardware_bridge


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            await database.connect()
            print("✓ Connected to TimescaleDB (PostgreSQL + PostGIS + pgvector)")
            break
        except Exception as exc:
            if attempt == max_attempts:
                raise
            print(f"  TimescaleDB not ready (attempt {attempt}/{max_attempts}): {exc}")
            await asyncio.sleep(2)

    # Verify Redis feature store is reachable
    try:
        r = await get_redis()
        await r.ping()
        print("✓ Redis feature store connected")
    except Exception as exc:
        print(f"  Warning: Redis unavailable — feature store will degrade: {exc}")

    # Start meteo ingestion worker (Section 6.1 — every 15 minutes)
    try:
        start_meteo_worker()
        print("✓ Meteo ingestion worker started (15-min interval)")
    except Exception as exc:
        print(f"  Warning: Meteo worker failed to start: {exc}")

    # Start live hardware ngrok bridge worker (polls every 5s)
    try:
        start_hardware_bridge()
        print("✓ Live hardware ngrok bridge worker started")
    except Exception as exc:
        print(f"  Warning: Live hardware bridge failed to start: {exc}")

    yield


    # ── Shutdown ─────────────────────────────────────────────────────────────
    stop_hardware_bridge()
    stop_meteo_worker()
    await database.disconnect()
    await close_redis()
    print("SafeSlope-NER API shutdown complete.")


app = FastAPI(
    title="SafeSlope-NER API",
    description=(
        "Operational multi-tiered AI Decision Support System for MDoNER "
        "(SIH26001) — landslide early warning, HITL governance, and "
        "kinematic runout modeling for North Eastern India road corridors."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

# Permissive CORS for hackathon — tighten allow_origins before production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def read_root():
    return {
        "status": "SafeSlope-NER API running",
        "version": "3.0.0",
        "plan": "computational_backend_plan.txt v3.0.0",
    }


@app.get("/health", tags=["health"])
async def health_check():
    try:
        await database.fetch_one("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False

    try:
        r = await get_redis()
        await r.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    return {
        "database": "ok" if db_ok else "degraded",
        "redis": "ok" if redis_ok else "degraded",
        "overall": "ok" if (db_ok and redis_ok) else "degraded",
    }


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(risk.router)
app.include_router(reports.router)
app.include_router(villages.router)
app.include_router(network_twin.router)
app.include_router(tiles.router)
app.include_router(governance.router)
app.include_router(simulation.router)
