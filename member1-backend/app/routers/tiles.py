"""
SafeSlope-NER — Dynamic Mapbox Vector Tile (MVT) Streaming Router
Implements Section 5.5 and Section 9.3 of computational_backend_plan.txt v3.0.0

Streams binary Protocol Buffer (.pbf) vector tiles directly from PostGIS:
  - Stored procedure `get_risk_zone_mvt(z, x, y)`
  - Stored procedure `get_road_edges_mvt(z, x, y)`
Delivers dynamic sub-corridor layers to the React/Deck.gl dashboard in < 25ms.
"""
from __future__ import annotations

import time
import logging
from fastapi import APIRouter, Response, HTTPException

from app.database import database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tiles", tags=["tiles"])


@router.get(
    "/risk-zones/{z}/{x}/{y}.pbf",
    summary="Dynamic Mapbox Vector Tile for Risk Zones",
    description="Streams binary .pbf vector tile of active risk corridors via ST_AsMVT.",
)
async def get_risk_zones_mvt(z: int, x: int, y: int):
    t0 = time.perf_counter()
    try:
        row = await database.fetch_one(
            "SELECT get_risk_zone_mvt(:z, :x, :y) AS mvt",
            {"z": z, "x": x, "y": y},
        )
        tile_bytes = row["mvt"] if row and row["mvt"] else b""
    except Exception as e:
        logger.error("Failed generating risk zone MVT for tile (%d, %d, %d): %s", z, x, y, e)
        tile_bytes = b""

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return Response(
        content=bytes(tile_bytes),
        media_type="application/x-protobuf",
        headers={
            "Content-Type": "application/x-protobuf",
            "Cache-Control": "public, max-age=15",
            "X-Response-Time-Ms": f"{elapsed_ms:.2f}",
        },
    )


@router.get(
    "/road-edges/{z}/{x}/{y}.pbf",
    summary="Dynamic Mapbox Vector Tile for Road Transportation Network",
    description="Streams binary .pbf vector tile of road edges, chokepoints, and severed segments.",
)
async def get_road_edges_mvt(z: int, x: int, y: int):
    t0 = time.perf_counter()
    try:
        row = await database.fetch_one(
            "SELECT get_road_edges_mvt(:z, :x, :y) AS mvt",
            {"z": z, "x": x, "y": y},
        )
        tile_bytes = row["mvt"] if row and row["mvt"] else b""
    except Exception as e:
        logger.error("Failed generating road edges MVT for tile (%d, %d, %d): %s", z, x, y, e)
        tile_bytes = b""

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return Response(
        content=bytes(tile_bytes),
        media_type="application/x-protobuf",
        headers={
            "Content-Type": "application/x-protobuf",
            "Cache-Control": "public, max-age=30",
            "X-Response-Time-Ms": f"{elapsed_ms:.2f}",
        },
    )
