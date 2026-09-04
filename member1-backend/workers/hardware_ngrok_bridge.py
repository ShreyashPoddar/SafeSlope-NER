"""
SafeSlope-NER — Live Hardware Ngrok Telemetry Bridge Worker
Streams real-time physical sensor data from the hardware gateway into the computational backend.

Polls:
  - Source: https://unknown-remold-lavish.ngrok-free.dev/telemetry
  - Interval: 5 seconds (configurable via HARDWARE_POLL_INTERVAL_SECONDS)
  - Features: Automatic dedup, PostGIS coordinate alignment, TimescaleDB hypertable insert,
              Redis feature store cache, and immediate Geotechnical Physics Engine evaluation.
"""
from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import get_settings
from app.database import database
from app.redis_client import get_redis
try:
    from app.services.physics_engine import mohr_coulomb_fos, van_genuchten_ptf
except ImportError:
    import math
    from dataclasses import dataclass

    @dataclass
    class VGResult:
        psi_m_kpa: float
        S_r: float

    @dataclass
    class FoSResult:
        fos: float
        status: str

    def van_genuchten_ptf(
        theta_measured: float,
        theta_r: float = 0.05,
        theta_s: float = 0.45,
        alpha_vg: float = 0.03,
        n_vg: float = 1.4,
    ) -> VGResult:
        S_e = max(0.01, min(0.99, (theta_measured - theta_r) / max(0.01, (theta_s - theta_r))))
        m = 1.0 - 1.0 / n_vg
        psi = (1.0 / alpha_vg) * ((S_e ** (-1.0 / m) - 1.0) ** (1.0 / n_vg))
        return VGResult(psi_m_kpa=psi, S_r=S_e)

    def mohr_coulomb_fos(
        c_prime_kpa: float,
        c_r_kpa: float,
        gamma_sat_kNm3: float,
        gamma_w_kNm3: float,
        z_m: float,
        beta_deg: float,
        u_w_kpa: float,
        phi_prime_deg: float,
        phi_b_deg: float,
        psi_m_kpa: float,
        S_r: float,
    ) -> FoSResult:
        beta = math.radians(beta_deg)
        phi = math.radians(phi_prime_deg)
        sigma = gamma_sat_kNm3 * z_m * (math.cos(beta) ** 2)
        tau_d = gamma_sat_kNm3 * z_m * math.sin(beta) * math.cos(beta)
        tau_f = (c_prime_kpa + c_r_kpa) + (sigma - u_w_kpa) * math.tan(phi)
        fos = max(0.01, tau_f / max(0.1, tau_d))
        return FoSResult(fos=fos, status="STABLE" if fos >= 1.3 else ("MARGINAL" if fos >= 1.0 else "UNSTABLE"))

logger = logging.getLogger("HardwareBridge")
settings = get_settings()

_bridge_task: Optional[asyncio.Task] = None
_running: bool = False
_last_processed_id: int = 0
_bridge_stats = {
    "status": "STOPPED",
    "last_poll_time": None,
    "last_success_time": None,
    "packets_ingested": 0,
    "last_packet_summary": None,
    "error_count": 0,
    "last_error": None,
}


def _fetch_ngrok_telemetry_sync(endpoint_url: str) -> list[dict[str, Any]]:
    """Fetches telemetry records from the live ngrok hardware endpoint using standard urllib."""
    ctx = ssl.create_default_context()
    headers = {
        "ngrok-skip-browser-warning": "true",
        "User-Agent": "SafeSlope-Computational-Backend/3.0",
        "Accept": "application/json",
    }
    req = urllib.request.Request(endpoint_url, headers=headers)
    with urllib.request.urlopen(req, timeout=6.0, context=ctx) as resp:
        if resp.status == 200:
            content = resp.read().decode("utf-8", errors="replace")
            return json.loads(content)
        else:
            raise RuntimeError(f"Hardware endpoint returned HTTP {resp.status}")


async def poll_hardware_telemetry_once() -> int:
    """
    Polls the hardware endpoint once, processes new records, and updates the physics state.
    Returns the count of newly ingested records.
    """
    global _last_processed_id, _bridge_stats
    _bridge_stats["last_poll_time"] = datetime.now(timezone.utc).isoformat()
    endpoint = f"{settings.HARDWARE_BRIDGE_URL}/telemetry"

    # Fetch in thread pool to prevent blocking the async event loop
    loop = asyncio.get_running_loop()
    try:
        records = await loop.run_in_executor(None, _fetch_ngrok_telemetry_sync, endpoint)
    except Exception as exc:
        _bridge_stats["error_count"] += 1
        _bridge_stats["last_error"] = str(exc)
        logger.warning("Hardware ngrok bridge poll failed: %s", exc)
        return 0

    if not records:
        return 0

    # Ensure records are sorted by ID ascending so we process in chronological order
    records_sorted = sorted(records, key=lambda r: r.get("id", 0))
    new_records = [r for r in records_sorted if r.get("id", 0) > _last_processed_id]

    if not new_records:
        return 0

    ingested_count = 0
    now_utc = datetime.now(timezone.utc)

    for r in new_records:
        rec_id = r.get("id", 0)
        sensor_id = str(r.get("sensor_id") or "sensor_042")
        lat = float(r.get("lat") or 23.7271)
        lon = float(r.get("lng") or 92.9376)
        pitch = float(r.get("pitch_deg") if r.get("pitch_deg") is not None else 0.0)
        roll = float(r.get("roll_deg") if r.get("roll_deg") is not None else 0.0)
        tilt_vel = float(r.get("angular_shift_rate_deg_per_sec") or 0.0) * 60.0  # deg/min
        vwc = float(r.get("soil_moisture_pct") if r.get("soil_moisture_pct") is not None else (r.get("soil_moisture") or 35.0))
        pore_pressure = float(r.get("pore_pressure_kpa") if r.get("pore_pressure_kpa") is not None else 5.0)
        brittle_trip = bool(r.get("tripwire_flag"))
        vibration_rms = float(r.get("vibration_rms_g") or 0.0)
        rec_time_str = r.get("received_at")
        try:
            recorded_at = datetime.fromisoformat(rec_time_str) if rec_time_str else now_utc
        except Exception:
            recorded_at = now_utc

        # ── 1. Register Sensor in Database (if needed) ──
        try:
            await database.execute(
                """
                INSERT INTO sensors (
                    sensor_id, sensor_type, gateway_id, location, active_status
                ) VALUES (
                    :sid, 'inclinometer', 101,
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                    TRUE
                ) ON CONFLICT (sensor_id) DO NOTHING
                """,
                {"sid": sensor_id, "lon": lon, "lat": lat},
            )
        except Exception:
            pass

        # ── 2. Insert into TimescaleDB Hypertable ──
        try:
            await database.execute(
                """
                INSERT INTO telemetry_readings (
                    sensor_id, recorded_at, pitch, roll, tilt_velocity,
                    vwc_pct, pore_pressure, rms_vibration, brittle_trip,
                    ax, ay, az, wx, wy, wz
                ) VALUES (
                    :sid, :rec_at, :pitch, :roll, :tilt_vel,
                    :vwc, :pore, :rms, :brittle,
                    :ax, :ay, :az, :wx, :wy, :wz
                )
                """,
                {
                    "sid": sensor_id,
                    "rec_at": recorded_at,
                    "pitch": pitch,
                    "roll": roll,
                    "tilt_vel": tilt_vel,
                    "vwc": vwc,
                    "pore": pore_pressure,
                    "rms": vibration_rms,
                    "brittle": brittle_trip,
                    "ax": r.get("accelerometer_x"),
                    "ay": r.get("accelerometer_y"),
                    "az": r.get("accelerometer_z"),
                    "wx": r.get("gyro_x"),
                    "wy": r.get("gyro_y"),
                    "wz": r.get("gyro_z"),
                },
            )
        except Exception:
            pass

        # ── 3. Cache in Redis Feature Store ──
        try:
            r_client = await get_redis()
            feature_dict = {
                "sensor_id": sensor_id,
                "pitch": str(pitch),
                "roll": str(roll),
                "vwc_pct": str(vwc),
                "pore_pressure": str(pore_pressure),
                "brittle_trip": "1" if brittle_trip else "0",
                "timestamp": recorded_at.isoformat(),
            }
            await r_client.hset(f"telemetry:{sensor_id}:latest", mapping=feature_dict)
            await r_client.expire(f"telemetry:{sensor_id}:latest", 86400)
        except Exception:
            pass

        # ── 4. Evaluate Geotechnical Physics Engine ──
        vg = van_genuchten_ptf(
            theta_measured=vwc / 100.0 if vwc > 1.0 else 0.35,
            theta_r=0.05,
            theta_s=0.45,
            alpha_vg=0.03,
            n_vg=1.4,
        )
        fos_res = mohr_coulomb_fos(
            c_prime_kpa=10.0,
            c_r_kpa=0.0,
            gamma_sat_kNm3=19.0,
            gamma_w_kNm3=9.81,
            z_m=3.5,
            beta_deg=35.0,
            u_w_kpa=pore_pressure,
            phi_prime_deg=32.0,
            phi_b_deg=15.0,
            psi_m_kpa=vg.psi_m_kpa,
            S_r=vg.S_r,
        )

        # Update tracking
        _last_processed_id = max(_last_processed_id, rec_id)
        ingested_count += 1

        summary = {
            "id": rec_id,
            "sensor_id": sensor_id,
            "pitch_deg": pitch,
            "roll_deg": roll,
            "pore_pressure_kpa": pore_pressure,
            "vwc_pct": vwc,
            "brittle_trip": brittle_trip,
            "computed_fos": round(fos_res.fos, 3),
            "safety_verdict": "CRITICAL" if fos_res.fos < 1.0 or brittle_trip else "NORMAL",
            "ingested_at": now_utc.isoformat(),
        }
        _bridge_stats["last_packet_summary"] = summary
        logger.info(
            "Ingested live hardware packet #%d from %s | Pitch: %.1f° | Pore: %.1f kPa | FoS: %.2f (%s)",
            rec_id, sensor_id, pitch, pore_pressure, fos_res.fos, summary["safety_verdict"],
        )

    _bridge_stats["packets_ingested"] += ingested_count
    _bridge_stats["last_success_time"] = now_utc.isoformat()
    return ingested_count


async def _bridge_loop():
    """Background polling loop executing every interval seconds."""
    global _running, _bridge_stats
    _running = True
    _bridge_stats["status"] = "STREAMING"
    interval = settings.HARDWARE_POLL_INTERVAL_SECONDS
    logger.info("Hardware Ngrok Bridge loop started (Interval: %.1fs, URL: %s)", interval, settings.HARDWARE_BRIDGE_URL)

    while _running:
        try:
            await poll_hardware_telemetry_once()
        except Exception as e:
            logger.error("Unexpected error in hardware bridge loop: %s", e)
        await asyncio.sleep(interval)

    _bridge_stats["status"] = "STOPPED"
    logger.info("Hardware Ngrok Bridge loop stopped.")


def start_hardware_bridge():
    """Starts the hardware bridge worker in the background."""
    global _bridge_task, _running
    if not settings.HARDWARE_BRIDGE_ENABLED:
        logger.info("Hardware bridge is disabled in configuration.")
        return
    if _bridge_task is None or _bridge_task.done():
        _running = True
        _bridge_task = asyncio.create_task(_bridge_loop())
        logger.info("Spawned background task for live hardware bridge.")


def stop_hardware_bridge():
    """Stops the hardware bridge worker."""
    global _running, _bridge_task
    _running = False
    if _bridge_task and not _bridge_task.done():
        _bridge_task.cancel()
        logger.info("Cancelled hardware bridge background task.")


def get_bridge_status() -> dict[str, Any]:
    """Returns real-time health metrics of the hardware bridge."""
    return {
        **_bridge_stats,
        "endpoint_url": settings.HARDWARE_BRIDGE_URL,
        "poll_interval_s": settings.HARDWARE_POLL_INTERVAL_SECONDS,
        "last_processed_id": _last_processed_id,
        "is_active": _running,
    }
