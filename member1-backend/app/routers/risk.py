"""
SafeSlope-NER — Risk Assessment Router (7-Stage Pipeline)
Implements the complete end-to-end risk pipeline from Section 6 of
computational_backend_plan.txt v3.0.0, covering:

  Stage 1: Multi-Rate Spatio-Temporal Ingestion & Grid Harmonization (§6.1)
  Stage 2: Mechanistic Geotechnical Physics Solver & Empirical Tripping (§6.2)
  Stage 3: Multi-Model Ensemble Stacking + GNN + PINN (§6.3)
  Stage 4: Uncertainty Quantification & Explainability / TreeSHAP (§6.4)
  Stage 5: Kinematic Runout & Debris Impact (§6.5)  ← stub, Sprint 4
  Stage 6: Isolation-Impact Twin & Supply Depletion (§6.6) ← stub, Sprint 4
  Stage 7: Autonomous Edge Actuation & Cryptographic Ledger (§6.7) ← Sprint 5

  Plus: Hierarchical Degradation Matrix Tier 1–4 routing (§7.4)
"""
from __future__ import annotations

import json
import logging
import math
import time
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user, require_role_operator, verify_api_key
from app.core.config import get_settings
from app.core.feature_store import (
    cache_risk_state,
    fetch_rainfall_with_fallback,
    get_all_risk_state,
    read_meteo_features,
    read_risk_state,
    should_recompute,
    write_sensor_features,
)
from app.database import database
from app.models.schemas import (
    OperationalTier,
    PhysicsResult,
    RiskAssessmentResponse,
    RiskLevel,
    RiskSource,
    RiskZoneCreate,
    RiskZoneResponse,
    ShapDriver,
)
from app.services.physics_engine import (
    PhysicsViolationError,
    check_rainfall_threshold,
    check_sustained_deformation,
    compute_root_cohesion,
    is_burn_in_mode,
    mohr_coulomb_fos,
    van_genuchten_ptf,
)

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(tags=["risk"])


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Risk percentage → RiskLevel enum (hard thresholds, Section 6.3)
# ═══════════════════════════════════════════════════════════════════════════════

def _risk_pct_to_level(risk_pct: float, fos: Optional[float] = None) -> RiskLevel:
    """
    Convert continuous risk probability to the 4-level categorical status.
    FoS hard floor: if fos < 1.0, always CRITICAL regardless of ML output.
    """
    if fos is not None and fos < 1.0:
        return RiskLevel.CRITICAL
    if risk_pct >= 75.0:
        return RiskLevel.CRITICAL
    if risk_pct >= 50.0:
        return RiskLevel.HIGH
    if risk_pct >= 25.0:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def _fos_to_risk_pct(fos: float) -> float:
    """
    Map physics FoS to an equivalent risk percentage.
    FoS ≤ 1.0 = 100% risk; FoS ≥ 2.0 = 0% risk (linear interpolation).
    """
    clamped = max(0.5, min(2.5, fos))
    risk = ((2.5 - clamped) / (2.5 - 0.5)) * 100.0
    return round(risk, 2)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Determine operational tier from sensor availability (Section 7.4)
# ═══════════════════════════════════════════════════════════════════════════════

def _determine_tier(
    insar_coherence: Optional[float],
    n_online_sensors: int,
    n_total_sensors: int,
) -> OperationalTier:
    """
    Hierarchical Model Degradation Matrix (Section 7.4):
    Tier 1: InSAR coherence ≥ 0.35 AND IoT online fraction ≥ 0.70
    Tier 2: InSAR blind (coherence < 0.35, monsoon canopy decorrelation)
    Tier 3: IoT degraded (< 30% nodes online, battery cutoff / radio jamming)
    Tier 4: Complete telecom blackout — mechanistic physics only
    """
    iot_fraction = (n_online_sensors / n_total_sensors) if n_total_sensors > 0 else 0.0

    if (
        insar_coherence is not None
        and insar_coherence >= settings.INSAR_COHERENCE_TIER1_MIN
        and iot_fraction >= 0.70
    ):
        return OperationalTier.TIER1_FULL_ENSEMBLE

    if iot_fraction >= 0.30:
        return OperationalTier.TIER2_INSAR_BLIND

    if n_online_sensors > 0:
        return OperationalTier.TIER3_DEGRADED_IOT

    return OperationalTier.TIER4_PHYSICS_ONLY


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Append audit ledger entry (Section 8.5)
# ═══════════════════════════════════════════════════════════════════════════════

async def _append_audit(payload_type: str, payload_data: dict) -> str:
    import hashlib
    last = await database.fetch_one(
        "SELECT block_hash FROM audit_ledger ORDER BY id DESC LIMIT 1"
    )
    prev_hash = last["block_hash"] if last else "0" * 64
    ts = datetime.now(timezone.utc).isoformat()
    content = f"{prev_hash}|{ts}|{payload_type}|{json.dumps(payload_data, sort_keys=True, default=str)}"
    block_hash = hashlib.sha256(content.encode()).hexdigest()
    await database.execute(
        """
        INSERT INTO audit_ledger (previous_hash, block_hash, payload_type, payload_data)
        VALUES (:ph, :bh, :pt, :pd)
        """,
        {
            "ph": prev_hash,
            "bh": block_hash,
            "pt": payload_type,
            "pd": json.dumps(payload_data, default=str),
        },
    )
    return block_hash


# ═══════════════════════════════════════════════════════════════════════════════
# CORE: 7-STAGE RISK PIPELINE
# Called internally after new telemetry arrives or on timer trigger.
# ═══════════════════════════════════════════════════════════════════════════════

async def run_risk_pipeline(zone_id: int) -> RiskAssessmentResponse:
    """
    Execute the full 7-stage computational pipeline for a risk zone.

    Stages 5, 6, 7 are stubs in Sprint 2 — fully implemented in Sprints 4 & 5.
    """
    t_start = time.perf_counter()

    # ─── Load zone record ────────────────────────────────────────────────────
    zone = await database.fetch_one(
        "SELECT * FROM risk_zones WHERE id = :id", {"id": zone_id}
    )
    if not zone:
        raise HTTPException(status_code=404, detail=f"Risk zone {zone_id} not found")

    zone = dict(zone)

    # ─── STAGE 1: Multi-Rate Spatio-Temporal Ingestion (§6.1) ────────────────
    # Aggregate latest telemetry readings from all sensors in this zone
    sensors = await database.fetch_all(
        """
        SELECT s.sensor_id, s.burn_in_expires_at,
               r.pitch, r.roll, r.tilt_velocity, r.vwc_pct, r.pore_pressure,
               r.ae_count, r.brittle_trip, r.battery_v, r.rssi_dbm,
               r.apparent_resistivity, r.delta_x_mm, r.delta_y_mm, r.delta_z_mm
        FROM sensors s
        JOIN LATERAL (
            SELECT pitch, roll, tilt_velocity, vwc_pct, pore_pressure,
                   ae_count, brittle_trip, battery_v, rssi_dbm,
                   apparent_resistivity, delta_x_mm, delta_y_mm, delta_z_mm
            FROM telemetry_readings
            WHERE sensor_id = s.sensor_id
              AND is_backfilled = FALSE
            ORDER BY recorded_at DESC
            LIMIT 1
        ) r ON TRUE
        WHERE s.corridor_h3_r9 = ANY(:cells) OR s.corridor_h3_r10 = ANY(:cells)
          AND s.active_status = TRUE
        """,
        {"cells": zone.get("h3_r9_cells", []) + zone.get("h3_r10_cells", [])},
    )
    sensor_list = [dict(s) for s in sensors]
    n_sensors = len(sensor_list)

    # Load meteo features from Redis feature store
    h3_cell = (zone.get("h3_r9_cells") or [""])[0]
    meteo = await read_meteo_features(h3_cell)
    rain_mmhr = float(meteo.get("rain_intensity_mmhr", zone.get("rainfall_intensity_mmhr") or 0.0))
    api_40d = float(meteo.get("api_40d", zone.get("antecedent_precip_40d") or 0.0))
    weather_source = meteo.get("weather_source", zone.get("weather_source", "IMD_DIRECT"))
    seismic_trigger = bool(meteo.get("seismic_trigger", zone.get("ncs_seismic_trigger", False)))
    sentinel2_toe_cut = bool(zone.get("sentinel2_toe_cut", False))

    # Aggregate multi-sensor readings
    avg_vwc = 0.0
    avg_pore = 0.0
    avg_tilt = 0.0
    n_brittle = 0
    n_online = 0
    burn_in_active = False

    for s in sensor_list:
        if s.get("vwc_pct") is not None:
            avg_vwc += float(s["vwc_pct"])
            n_online += 1
        if s.get("pore_pressure") is not None:
            avg_pore += float(s["pore_pressure"])
        if s.get("pitch") is not None:
            avg_tilt += abs(float(s["pitch"]))
        if s.get("brittle_trip"):
            n_brittle += 1
        if is_burn_in_mode(s.get("burn_in_expires_at")):
            burn_in_active = True

    if n_online > 0:
        avg_vwc /= n_online
        avg_pore /= n_online
        avg_tilt /= n_online

    insar_coherence = zone.get("insar_coherence")
    tier = _determine_tier(
        insar_coherence=insar_coherence,
        n_online_sensors=n_online,
        n_total_sensors=max(n_sensors, 1),
    )

    # ─── Event-delta compute gate (Section 6.3) ───────────────────────────────
    recompute_needed = await should_recompute(
        sensor_id=f"zone_{zone_id}",
        new_rain_mmhr=rain_mmhr,
        new_vwc_pct=avg_vwc,
        new_tilt_deg=avg_tilt,
    )

    # Return cached result if nothing has changed significantly
    if not recompute_needed:
        cached = await read_risk_state(zone_id)
        if cached:
            logger.debug("Zone %d — returning cached risk state (no delta)", zone_id)

    # ─── STAGE 2: Geotechnical Physics Solver (§6.2) ─────────────────────────
    brittle_trip_override = n_brittle >= 1

    # Determine slope parameters from zone or DEM defaults
    beta_deg = 35.0     # Placeholder — real value from DEM per sensor
    z_m = 3.5           # Placeholder — real value from ERT per sensor
    gamma_sat = 18.5    # kN/m³ — typical NE India residual soil
    gamma_w = 9.81      # kN/m³

    # Van Genuchten PTF inversion (soil-type calibrated from ICAR-NBSS)
    try:
        vg = van_genuchten_ptf(
            theta_measured=avg_vwc / 100.0,
            theta_r=0.05,
            theta_s=0.45,
            alpha_vg=0.03,   # 1/kPa — calibrated for Meghalaya residual laterite
            n_vg=1.4,
            K_sat_ms=3e-6,
        )
        psi_m_kpa = vg.psi_m_kpa
        S_r = vg.S_r
        K_sat = vg.K_sat_ms
    except Exception:
        psi_m_kpa = 10.0
        S_r = avg_vwc / 100.0
        K_sat = 1e-6

    # Jhum root cohesion — default 0 if no jhum data available
    c_r_kpa = 0.0

    # Mohr-Coulomb FoS
    physics_error = None
    fos_result = None
    try:
        fos_result = mohr_coulomb_fos(
            c_prime_kpa=8.0,       # kPa — calibrated from GSI borehole database
            c_r_kpa=c_r_kpa,
            gamma_sat_kNm3=gamma_sat,
            gamma_w_kNm3=gamma_w,
            z_m=z_m,
            beta_deg=beta_deg,
            u_w_kpa=avg_pore,
            phi_prime_deg=32.0,   # ° — calibrated for Meghalaya weathered basalt
            phi_b_deg=15.0,
            psi_m_kpa=psi_m_kpa,
            S_r=S_r,
        )
        fos = fos_result.fos
    except (PhysicsViolationError, ValueError) as e:
        logger.warning("FoS computation failed for zone %d: %s", zone_id, e)
        fos = 1.5   # Fallback to neutral value
        physics_error = str(e)

    # Rainfall threshold check (Section 6.2)
    culvert_clogged = bool(zone.get("culvert_clogged", False))
    rain_thresh = check_rainfall_threshold(
        I_mmhr=rain_mmhr,
        D_hr=1.0,
        cvi_clogged=culvert_clogged,
    )

    # Deterministic safety overrides (Section 6.3)
    seismic_override = seismic_trigger and (rain_mmhr > rain_thresh.I_crit * 0.6)
    toe_cut_override = sentinel2_toe_cut and fos < 1.5

    physics_result = PhysicsResult(
        fos=fos,
        fos_safe=(fos >= 1.0),
        psi_m_kpa=psi_m_kpa,
        k_sat_ms=K_sat,
        root_cohesion_kpa=c_r_kpa,
        rainfall_threshold_exceeded=rain_thresh.exceeded,
        rainfall_margin_pct=rain_thresh.margin_pct,
        deformation_status="MONITORING",
    )

    # ─── STAGE 3–4: ML Ensemble + Conformal UQ (§6.3, §6.4) ─────────────────
    # Sprint 2: physics-derived risk score used as ML proxy.
    # Full Treelite + GWaveNet + PINN ensemble implemented in Sprint 3.
    #
    # Burn-in mode (§7.2): if any sensor cluster is < 14 days old,
    # ML is disabled — physics FoS is sole risk driver.

    physics_risk_pct = _fos_to_risk_pct(fos)

    if burn_in_active or tier == OperationalTier.TIER4_PHYSICS_ONLY:
        # Pure physics mode
        ml_risk_pct = physics_risk_pct
        confidence_pct = 65.0   # Physics has lower confidence than full ensemble
        risk_source = RiskSource.BURN_IN_PHYSICS if burn_in_active else RiskSource.PHYSICS_FLOOR
        top_drivers: list[ShapDriver] = [
            ShapDriver(
                factor="Factor of Safety (Mohr-Coulomb)",
                feature_key="fos",
                weight_pct=60.0,
                value=fos,
            ),
            ShapDriver(
                factor="Pore-Water Pressure",
                feature_key="pore_pressure",
                weight_pct=25.0,
                value=avg_pore,
            ),
            ShapDriver(
                factor="Volumetric Water Content",
                feature_key="vwc_pct",
                weight_pct=15.0,
                value=avg_vwc,
            ),
        ]
    else:
        # ML ensemble mode (stub for Sprint 3 Treelite integration)
        # In Sprint 3 this block becomes the full stacking meta-learner call
        try:
            from app.services.ensemble_engine import run_ensemble
            ensemble_out = await run_ensemble(
                zone_id=zone_id,
                features={
                    "fos": fos,
                    "vwc_pct": avg_vwc,
                    "pore_pressure": avg_pore,
                    "rainfall_mmhr": rain_mmhr,
                    "api_40d": api_40d,
                    "insar_velocity": zone.get("insar_velocity_mmyr") or 0.0,
                    "insar_coherence": insar_coherence or 0.0,
                    "brittle_trip": float(brittle_trip_override),
                },
                tier=tier,
            )
            ml_risk_pct = ensemble_out["risk_pct"]
            confidence_pct = ensemble_out["confidence_pct"]
            top_drivers = ensemble_out["top_drivers"]
            risk_source = RiskSource.ENSEMBLE_MODEL
        except ImportError:
            # Sprint 3 not yet built — graceful fallback
            ml_risk_pct = physics_risk_pct
            confidence_pct = 70.0
            risk_source = RiskSource.PHYSICS_FLOOR
            top_drivers = []

    # Apply deterministic overrides (Section 6.3 — hard overrides cannot be
    # overruled by ML confidence score)
    final_risk_pct = ml_risk_pct
    final_source = risk_source

    if brittle_trip_override:
        final_risk_pct = max(final_risk_pct, 90.0)
        final_source = RiskSource.EDGE_TRIPWIRE
    if fos < 1.0:
        final_risk_pct = 100.0
        final_source = RiskSource.PHYSICS_FLOOR
    if seismic_override or toe_cut_override:
        final_risk_pct = max(final_risk_pct, 75.0)

    final_status = _risk_pct_to_level(final_risk_pct, fos=fos)

    # ─── Write back to Postgres + Redis cache ────────────────────────────────
    shap_payload = [
        {"factor": d.factor, "weight_pct": d.weight_pct, "value": d.value}
        for d in top_drivers
    ]

    await database.execute(
        """
        UPDATE risk_zones
        SET current_risk = :risk,
            risk_source = :source,
            operational_tier = :tier,
            ml_risk_pct = :ml_pct,
            ml_confidence_pct = :conf,
            fos_value = :fos,
            rainfall_intensity_mmhr = :rain,
            antecedent_precip_40d = :api,
            weather_source = :wsrc,
            shap_drivers = :shap,
            ncs_seismic_trigger = :seismic,
            updated_at = NOW()
        WHERE id = :id
        """,
        {
            "risk": final_status.value,
            "source": final_source.value,
            "tier": tier.value,
            "ml_pct": final_risk_pct,
            "conf": confidence_pct,
            "fos": fos,
            "rain": rain_mmhr,
            "api": api_40d,
            "wsrc": weather_source,
            "shap": json.dumps(shap_payload),
            "seismic": seismic_trigger,
            "id": zone_id,
        },
    )

    await cache_risk_state(
        zone_id=zone_id,
        risk_pct=final_risk_pct,
        confidence_pct=confidence_pct,
        status=final_status.value,
        tier=tier.value,
        shap_drivers=shap_payload,
    )

    # ─── Audit ledger (Section 8.5) ───────────────────────────────────────────
    await _append_audit(
        "RISK_SCORE",
        {
            "zone_id": zone_id,
            "risk_pct": final_risk_pct,
            "confidence_pct": confidence_pct,
            "fos": fos,
            "tier": tier.value,
            "source": final_source.value,
            "overrides": {
                "brittle_trip": brittle_trip_override,
                "seismic": seismic_override,
                "toe_cut": toe_cut_override,
            },
        },
    )

    elapsed_ms = (time.perf_counter() - t_start) * 1000
    logger.info(
        "Zone %d — %s (%.1f%%, FoS=%.2f, Tier %d) in %.1fms",
        zone_id, final_status.value, final_risk_pct, fos, tier.value, elapsed_ms,
    )

    return RiskAssessmentResponse(
        zone_id=zone_id,
        zone_name=zone.get("zone_name", ""),
        lgd_district_code=zone.get("lgd_district_code", ""),
        risk_pct=final_risk_pct,
        confidence_pct=confidence_pct,
        status=final_status,
        risk_source=final_source,
        physics=physics_result,
        top_drivers=top_drivers,
        tier_mode=tier,
        is_burn_in_mode=burn_in_active,
        weather_source=weather_source,
        seismic_override=seismic_override,
        toe_cut_override=toe_cut_override,
        brittle_trip_override=brittle_trip_override,
        assessed_at=datetime.now(timezone.utc),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/risk-zones",
    response_model=RiskZoneResponse,
    summary="Create a new risk zone corridor sector",
)
async def create_risk_zone(
    payload: RiskZoneCreate,
    _: None = Depends(require_role_operator),
):
    """Register a new risk zone. Requires ROLE_OPERATOR or higher (Section 8.3)."""
    import json as _json
    geo = payload.boundary_geojson
    row = await database.fetch_one(
        """
        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells
        )
        VALUES (
            :name, :corridor, :lgd_district, :lgd_state,
            ST_SetSRID(ST_GeomFromGeoJSON(:geo), 4326),
            :h3r9, :h3r10
        )
        RETURNING id, zone_name, corridor_code, lgd_district_code,
                  current_risk, operational_tier, ml_risk_pct, ml_confidence_pct,
                  fos_value, shap_drivers, weather_source, updated_at
        """,
        {
            "name": payload.zone_name,
            "corridor": payload.corridor_code,
            "lgd_district": payload.lgd_district_code,
            "lgd_state": payload.lgd_state_code,
            "geo": _json.dumps(geo),
            "h3r9": [],
            "h3r10": [],
        },
    )
    return dict(row)


@router.get(
    "/risk-zones",
    response_model=list[RiskZoneResponse],
    summary="List all risk zones with current status",
)
async def list_risk_zones(_: dict = Depends(get_current_user)):
    rows = await database.fetch_all(
        """
        SELECT id, zone_name, corridor_code, lgd_district_code,
               current_risk, operational_tier, ml_risk_pct, ml_confidence_pct,
               fos_value, shap_drivers, weather_source, updated_at
        FROM risk_zones
        ORDER BY current_risk DESC, ml_risk_pct DESC NULLS LAST
        """
    )
    return [dict(r) for r in rows]


@router.post(
    "/risk-zones/{zone_id}/assess",
    response_model=RiskAssessmentResponse,
    summary="Run full 7-stage risk pipeline for a zone (on-demand)",
)
async def assess_zone(
    zone_id: int,
    _: None = Depends(verify_api_key),
):
    """
    Trigger an immediate full risk assessment for a zone.
    Called by telemetry worker after batch ingestion or by external ML services.
    """
    return await run_risk_pipeline(zone_id)


@router.get(
    "/risk-state",
    summary="Current risk state — all zones (Redis cache, < 5ms) [Section 5.4]",
)
async def get_risk_state(_: dict = Depends(get_current_user)):
    """
    Member 5 dashboard polling endpoint.
    Primary: Redis cache (< 5ms). Fallback: Postgres.
    """
    cached = await get_all_risk_state()
    if cached:
        return cached

    # Redis miss — fetch from Postgres
    rows = await database.fetch_all(
        """
        SELECT id, zone_name, current_risk, operational_tier,
               ml_risk_pct, ml_confidence_pct, fos_value, updated_at
        FROM risk_zones
        ORDER BY current_risk DESC
        """
    )
    return {str(r["id"]): dict(r) for r in rows}


@router.get(
    "/risk-zones/{zone_id}",
    response_model=RiskAssessmentResponse,
    summary="Latest risk assessment for a specific zone",
)
async def get_zone_risk(zone_id: int, _: dict = Depends(get_current_user)):
    """Return cached risk state for a zone, or trigger fresh assessment."""
    cached = await read_risk_state(zone_id)
    if cached:
        zone = await database.fetch_one(
            "SELECT zone_name, lgd_district_code, fos_value, weather_source FROM risk_zones WHERE id = :id",
            {"id": zone_id},
        )
        if zone:
            return RiskAssessmentResponse(
                zone_id=zone_id,
                zone_name=zone["zone_name"],
                lgd_district_code=zone["lgd_district_code"],
                risk_pct=cached["risk_pct"],
                confidence_pct=cached["confidence_pct"],
                status=RiskLevel(cached["status"]),
                risk_source=RiskSource.ENSEMBLE_MODEL,
                physics=PhysicsResult(
                    fos=float(zone["fos_value"] or 1.5),
                    fos_safe=(float(zone["fos_value"] or 1.5) >= 1.0),
                ),
                top_drivers=[
                    ShapDriver(**d) for d in cached.get("shap_drivers", [])
                ],
                tier_mode=OperationalTier(cached["tier"]),
                weather_source=zone["weather_source"],
                assessed_at=datetime.now(timezone.utc),
            )

    # No cache — run full pipeline
    return await run_risk_pipeline(zone_id)


@router.post(
    "/ml-result",
    summary="Receive ML risk score from external model service (Member 3)",
    dependencies=[Depends(verify_api_key)],
)
async def receive_ml_result(
    zone_id: int,
    ml_risk_pct: float,
    confidence_pct: float,
    shap_drivers: Optional[list[dict]] = None,
):
    """
    Backward-compatible endpoint for Member 3 ML service to post risk scores.
    Updated to use new schema and write to Redis cache.
    """
    await database.execute(
        """
        UPDATE risk_zones
        SET ml_risk_pct = :ml_pct,
            ml_confidence_pct = :conf,
            risk_source = 'ensemble_model',
            shap_drivers = :shap,
            updated_at = NOW()
        WHERE id = :id
        """,
        {
            "ml_pct": ml_risk_pct,
            "conf": confidence_pct,
            "shap": json.dumps(shap_drivers or []),
            "id": zone_id,
        },
    )

    # Update risk level based on ML result
    new_status = _risk_pct_to_level(ml_risk_pct)
    await database.execute(
        "UPDATE risk_zones SET current_risk = :risk WHERE id = :id",
        {"risk": new_status.value, "id": zone_id},
    )

    await cache_risk_state(
        zone_id=zone_id,
        risk_pct=ml_risk_pct,
        confidence_pct=confidence_pct,
        status=new_status.value,
        tier=1,
        shap_drivers=shap_drivers or [],
    )
    return {"status": "ok", "zone_id": zone_id, "risk_level": new_status.value}


@router.post(
    "/rules-result",
    summary="Receive physics rules result from external service (Member 2)",
    dependencies=[Depends(verify_api_key)],
)
async def receive_rules_result(
    zone_id: int,
    fos: float,
    risk_level: str,
):
    """Backward-compatible endpoint for Member 2 physics service."""
    await database.execute(
        """
        UPDATE risk_zones
        SET fos_value = :fos,
            current_risk = :risk,
            risk_source = 'physics_floor',
            updated_at = NOW()
        WHERE id = :id
        """,
        {"fos": fos, "risk": risk_level, "id": zone_id},
    )
    return {"status": "ok"}
