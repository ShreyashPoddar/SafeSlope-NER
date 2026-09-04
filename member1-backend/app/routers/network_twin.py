"""
SafeSlope-NER — Transportation Network & Isolation Digital Twin Router
Exposes endpoints for road graph severance, demographic impact analysis,
and emergency supply logistics.
"""
from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth import get_current_user, require_role_operator
from app.database import database
from app.models.schemas import IsolationResult
from app.services.fno_runout import simulate_runout
from app.services.isolation_twin import evaluate_isolation_impact, generate_uav_mission_kml

router = APIRouter(prefix="/network", tags=["network-twin"])


@router.post("/simulate-impact/{zone_id}", response_model=IsolationResult)
async def trigger_runout_and_isolation(
    zone_id: int,
    volume_m3: float = 15000.0,
    _: dict = Depends(require_role_operator),
):
    """
    Executes the coupled FNO Kinematic Runout + Isolation Twin pipeline for a zone.
    Determines severed road edges, isolated population, and PDS depletion timeline.
    """
    zone = await database.fetch_one(
        """
        SELECT id, zone_name,
               ST_Y(ST_Centroid(boundary)) AS lat,
               ST_X(ST_Centroid(boundary)) AS lon
        FROM risk_zones WHERE id = :id
        """,
        {"id": zone_id},
    )
    if not zone:
        raise HTTPException(status_code=404, detail=f"Risk zone {zone_id} not found")

    # Step 1: Kinematic Debris Runout
    runout_res = await simulate_runout(
        zone_id=zone_id,
        source_lat=zone["lat"],
        source_lon=zone["lon"],
        estimated_volume_m3=volume_m3,
    )

    # Step 2: Isolation Twin Severance Traversal
    isolation_res = await evaluate_isolation_impact(
        zone_id=zone_id,
        runout_poly_90=runout_res["shapely_p90"],
        debris_volume_m3=volume_m3,
    )

    return isolation_res


@router.get("/isolation-events", summary="List historical network isolation events")
async def list_isolation_events(limit: int = 20, _: dict = Depends(get_current_user)):
    rows = await database.fetch_all(
        """
        SELECT ie.*, rz.zone_name, rz.lgd_district_code
        FROM isolation_events ie
        LEFT JOIN risk_zones rz ON rz.id = ie.zone_id
        ORDER BY ie.detected_at DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )
    return [dict(r) for r in rows]


@router.get("/uav-mission/{event_id}.kml", summary="Download UAV Drone Mission Waypoint KML")
async def download_uav_mission_kml(event_id: int):
    event = await database.fetch_one(
        "SELECT * FROM isolation_events WHERE id = :id", {"id": event_id}
    )
    if not event:
        raise HTTPException(status_code=404, detail="Isolation event not found")

    kml_content = generate_uav_mission_kml(
        isolated_villages=[],
        debris_center_lat=25.55,
        debris_center_lon=91.85,
    )
    return Response(content=kml_content, media_type="application/vnd.google-earth.kml+xml")
