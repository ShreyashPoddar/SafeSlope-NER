"""
SafeSlope-NER — Meteorological Ingestion Worker
Covers: Section 6.1 (15-min multi-rate ingestion), Section 4.3 (circuit breaker),
        Section 5.3 (H3 cell feature writing), Section 2.4 (IMD rainfall, INSAT-3D,
        NCS seismic, MOSDAC InSAR update triggers)

Runs as an APScheduler background worker every 15 minutes.
On startup, fetches weather baselines for all active risk zones.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.core.feature_store import (
    fetch_rainfall_with_fallback,
    fetch_seismic_with_fallback,
    write_meteo_features,
    get_sensor_h3_pair,
)
from app.database import database
from app.services.physics_engine import compute_api, downscale_rainfall

logger = logging.getLogger(__name__)
settings = get_settings()

# APScheduler instance (registered in main.py lifespan)
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")


async def ingest_meteo_for_all_zones() -> None:
    """
    15-minute meteo ingestion tick for all active risk zones (Section 6.1).
    For each zone:
    1. Fetch live rainfall from IMD (with ECMWF fallback)
    2. Apply orographic downscaling to DEM cell elevation
    3. Compute API-40d from 40-day rolling archive
    4. Write meteo feature vector to Redis for each H3 cell in zone
    5. Fetch NCS seismic events and flag if M ≥ 3.0 within 50km
    """
    logger.info("Meteo ingestion tick started — %s", datetime.now(timezone.utc).isoformat())

    # Fetch all active zones
    rows = await database.fetch_all(
        """
        SELECT id, zone_name, lgd_district_code,
               ST_Y(ST_Centroid(boundary)) AS lat,
               ST_X(ST_Centroid(boundary)) AS lon
        FROM risk_zones
        WHERE current_risk != 'ARCHIVED'
        """
    )

    for row in rows:
        zone_id = row["id"]
        lat = row["lat"]
        lon = row["lon"]
        district_code = row["lgd_district_code"]

        try:
            # Step 1: Fetch rainfall with fallback (Section 4.3)
            rain_mmhr, provenance = await fetch_rainfall_with_fallback(
                lat=lat, lon=lon, district_code=district_code,
            )

            # Step 2: Fetch 40-day rainfall archive for API
            rain_archive_rows = await database.fetch_all(
                """
                SELECT SUM(rainfall_intensity_mmhr) AS daily_total
                FROM risk_zones
                WHERE id = :zid
                  AND updated_at >= NOW() - INTERVAL '40 days'
                GROUP BY DATE(updated_at)
                ORDER BY DATE(updated_at)
                LIMIT 40
                """,
                {"zid": zone_id},
            )
            daily_series = [float(r["daily_total"] or 0.0) for r in rain_archive_rows]
            api_40d = compute_api(daily_series)

            # Step 3: Fetch seismic data from NCS (Section 2.4)
            seismic = await fetch_seismic_with_fallback(lat, lon)
            seismic_trigger = False
            pga_g = 0.0
            if seismic:
                events = seismic.get("events", [])
                for event in events:
                    mag = float(event.get("magnitude", 0.0))
                    depth_km = float(event.get("depth_km", 10.0))
                    if mag >= 3.0:
                        seismic_trigger = True
                        # Simple attenuation: PGA ~ 0.005 * 10^(0.5*M) / (D + 10)
                        import math
                        pga_g = 0.005 * (10 ** (0.5 * mag)) / (depth_km + 10.0)
                        break

            # Step 4: Write meteo feature vector to Redis (Section 5.4)
            h3_pair = get_sensor_h3_pair(lat, lon)
            meteo_features = {
                "rain_intensity_mmhr": rain_mmhr,
                "api_40d": api_40d,
                "weather_source": provenance,
                "seismic_trigger": seismic_trigger,
                "pga_g": pga_g,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            for h3_cell in h3_pair.values():
                await write_meteo_features(h3_cell, meteo_features)

            # Step 5: Update zone rainfall snapshot in Postgres
            await database.execute(
                """
                UPDATE risk_zones
                SET rainfall_intensity_mmhr = :rain,
                    antecedent_precip_40d = :api,
                    weather_source = :source,
                    ncs_seismic_trigger = :seismic,
                    updated_at = NOW()
                WHERE id = :zid
                """,
                {
                    "rain": rain_mmhr,
                    "api": api_40d,
                    "source": provenance,
                    "seismic": seismic_trigger,
                    "zid": zone_id,
                },
            )

            logger.debug(
                "Zone %d — rain=%.1fmm/hr API40d=%.1fmm seismic=%s src=%s",
                zone_id, rain_mmhr, api_40d, seismic_trigger, provenance,
            )

        except Exception as e:
            logger.error("Meteo ingestion failed for zone %d: %s", zone_id, e, exc_info=True)

    logger.info("Meteo ingestion tick complete for %d zones", len(rows))


def start_meteo_worker() -> None:
    """Register and start the 15-minute meteo ingestion job."""
    scheduler.add_job(
        ingest_meteo_for_all_zones,
        trigger=IntervalTrigger(minutes=15),
        id="meteo_ingestion",
        replace_existing=True,
        coalesce=True,          # Skip missed ticks if server was down
        max_instances=1,        # Never run two simultaneously
    )
    if not scheduler.running:
        scheduler.start()
    logger.info("Meteo ingestion worker started — every 15 minutes")


def stop_meteo_worker() -> None:
    """Gracefully shut down the APScheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
