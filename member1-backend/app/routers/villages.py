from fastapi import APIRouter, Depends
from app.models.schemas import IsolationResult, VillagePayload
from app.database import database
from app.auth import verify_api_key, get_current_user

router = APIRouter(tags=["villages"])


@router.post("/villages", dependencies=[Depends(verify_api_key)])
async def create_village(payload: VillagePayload):
    """Register a village so Member 3's isolation twin has real data to link to."""
    query = """
        INSERT INTO villages (village_name, location, population)
        VALUES (:village_name, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :population)
        RETURNING id
    """
    row = await database.fetch_one(query, payload.model_dump())
    return {"id": row["id"], "village_name": payload.village_name}


@router.get("/villages", dependencies=[Depends(get_current_user)])
async def list_villages():
    rows = await database.fetch_all(
        "SELECT id, village_name, population FROM villages ORDER BY id"
    )
    return [dict(r) for r in rows]


@router.post("/isolation-result", dependencies=[Depends(verify_api_key)])
async def receive_isolation_result(result: IsolationResult):
    """
    Member 3 posts here after the NetworkX graph traversal determines
    which villages a failed zone cuts off.

    TODO once Member 3's payload includes specific village IDs (not just
    a count): insert one row per affected village into isolation_events.
    """
    return {
        "status": "received",
        "zone_id": result.zone_id,
        "isolated_villages": result.isolated_villages,
        "affected_population": result.affected_population,
    }


@router.get("/villages/isolated", dependencies=[Depends(get_current_user)])
async def get_isolated_villages():
    query = """
        SELECT v.village_name, v.population, ie.zone_id, ie.detected_at
        FROM isolation_events ie
        JOIN villages v ON v.id = ie.village_id
        ORDER BY ie.detected_at DESC
    """
    rows = await database.fetch_all(query)
    return [dict(r) for r in rows]
