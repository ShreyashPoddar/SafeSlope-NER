import json
from fastapi import APIRouter, Depends
from app.models.schemas import RulesResult, MLResult, RiskZonePayload
from app.database import database
from app.redis_client import redis_client
from app.services.risk_engine import resolve_risk
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
