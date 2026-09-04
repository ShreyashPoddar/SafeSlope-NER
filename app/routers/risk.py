import json
from fastapi import APIRouter, Depends
from app.models.schemas import RulesResult, MLResult, RiskZonePayload, LandslideAlgorithmPayload
from app.database import database
from app.redis_client import redis_client
from app.services.risk_engine import resolve_risk
from app.services.threshold_engine import evaluate_landslide_algorithm_prediction
from app.auth import verify_api_key, get_current_user

router = APIRouter(tags=["risk"])

CACHE_KEY = "risk_state_all"


@router.post("/risk-zones", dependencies=[Depends(verify_api_key)])
async def create_risk_zone(payload: RiskZonePayload):
    """Register a zone (e.g. a road segment) so Members 2 and 3 have a
    real zone_id to post their results against — the seed data only
    covers zone_1 and zone_2."""
    query = """
        INSERT INTO risk_zones (zone_name)
        VALUES (:zone_name)
        RETURNING id, zone_name, current_risk
    """
    row = await database.fetch_one(query, payload.model_dump())
    await _refresh_cache()
    return dict(row)


@router.get("/risk-zones", dependencies=[Depends(get_current_user)])
async def list_risk_zones():
    rows = await database.fetch_all(
        "SELECT id, zone_name, current_risk, ml_risk_pct, ml_confidence_pct FROM risk_zones ORDER BY id"
    )
    return [dict(r) for r in rows]


@router.post("/rules-result", dependencies=[Depends(verify_api_key)])
async def receive_rules_result(result: RulesResult):
    """Member 2 posts here after evaluating the physics threshold."""
    await _update_zone(result.zone_id, physics_risk=result.risk_level)
    return {"status": "ok"}


@router.post("/ml-result", dependencies=[Depends(verify_api_key)])
async def receive_ml_result(result: MLResult):
    """Member 3 posts here after their XGBoost model scores a zone."""
    await _update_zone(
        result.zone_id,
        ml_risk_pct=result.ml_risk_pct,
        confidence=result.confidence_pct,
    )
    return {"status": "ok"}


@router.post("/api/algorithm/landslide-risk")
@router.post("/algorithm/landslide-risk")
async def receive_algorithm_landslide_prediction(payload: LandslideAlgorithmPayload):
    """
    Standard ingestion endpoint for the upcoming main git landslide risk prediction algorithm.
    Evaluates the prediction against dynamic thresholds (Advisory, Warning, Critical),
    dynamically calculates geotechnical Factor of Safety and spatial isolation metrics,
    and automatically triggers the area emergency broadcast cascade upon breach.
    """
    features = {}
    # Merge nested trigger features if supplied
    if payload.trigger_features:
        features.update(payload.trigger_features)

    if payload.rainfall_mm_24h is not None:
        features["rainfall_mm_24h"] = payload.rainfall_mm_24h
    if payload.soil_moisture_pct is not None:
        features["soil_moisture_pct"] = payload.soil_moisture_pct
    if payload.slope_tilt_deg is not None:
        features["slope_tilt_deg"] = payload.slope_tilt_deg
    if payload.pore_pressure_kpa is not None:
        features["pore_pressure_kpa"] = payload.pore_pressure_kpa

    # Resolve risk probability (accepts 0-1 probability or 0-100 percentage)
    raw_prob = payload.risk_pct if payload.risk_pct is not None else payload.predicted_probability
    if raw_prob is None:
        raw_prob = 75.0  # Safe default if pure features are sent

    # Resolve confidence (accepts 0-1 or 0-100)
    raw_conf = payload.confidence if payload.confidence is not None else payload.confidence_pct
    if raw_conf is not None and raw_conf <= 1.0:
        raw_conf *= 100.0

    eval_result = await evaluate_landslide_algorithm_prediction(
        zone_id=payload.zone_id or 1,
        zone_name=payload.corridor_id or payload.zone_name,
        risk_pct=raw_prob,
        confidence_pct=raw_conf if raw_conf is not None else 85.0,
        model_version=payload.source_model or payload.model_version or "xgboost-landslide-v2",
        features=features,
        force_notify=payload.force_notify or False,
        lat=payload.latitude,
        lng=payload.longitude,
    )
    return eval_result




async def _update_zone(
    zone_id: int,
    physics_risk: str | None = None,
    ml_risk_pct: float | None = None,
    confidence: float | None = None,
):
    row = await database.fetch_one(
        "SELECT * FROM risk_zones WHERE id = :id", {"id": zone_id}
    )
    if not row:
        return

    final_risk, source = resolve_risk(
        physics_risk,
        ml_risk_pct if ml_risk_pct is not None else row["ml_risk_pct"],
    )

    await database.execute(
        """UPDATE risk_zones
           SET current_risk = :risk, risk_source = :source,
               ml_risk_pct = COALESCE(:ml_pct, ml_risk_pct),
               ml_confidence_pct = COALESCE(:confidence, ml_confidence_pct),
               updated_at = now()
           WHERE id = :id""",
        {
            "risk": final_risk,
            "source": source,
            "ml_pct": ml_risk_pct,
            "confidence": confidence,
            "id": zone_id,
        },
    )

    await _refresh_cache()

    # --- Member 6 Cross-Team Touchpoint: Automated Comms Trigger ---
    if final_risk in ["HIGH", "CRITICAL"]:
        try:
            from app.comms.dispatcher import alert_dispatcher
            await alert_dispatcher.evaluate_risk_trigger(
                zone_id=zone_id,
                zone_name=row["zone_name"],
                risk_level=final_risk,
                source=source,
            )
        except Exception:
            pass


async def _refresh_cache():
    rows = await database.fetch_all("SELECT * FROM risk_zones")
    state = {r["zone_name"]: dict(r) for r in rows}
    try:
        redis_client.set(CACHE_KEY, json.dumps(state, default=str), ex=300)
    except Exception:
        pass  # cache write failed — Postgres still has the real data


@router.get("/risk-state", dependencies=[Depends(get_current_user)])
async def get_risk_state():
    """Member 5's dashboard polls this. Redis first, Postgres fallback."""
    try:
        cached = redis_client.get(CACHE_KEY)
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Redis unreachable — fall through to Postgres

    rows = await database.fetch_all("SELECT * FROM risk_zones")
    state = {r["zone_name"]: dict(r) for r in rows}
    await _refresh_cache()
    return state
