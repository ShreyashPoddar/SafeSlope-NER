from fastapi import APIRouter, Depends
from app.models.schemas import ReportPayload
from app.database import database
from app.auth import verify_api_key, get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", dependencies=[Depends(verify_api_key)])
async def receive_report(payload: ReportPayload):
    query = """
        INSERT INTO reports (location, classification, confidence_pct, image_url, verified)
        VALUES (ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :classification, :confidence_pct, :image_url, TRUE)
    """
    await database.execute(query, payload.model_dump())
    return {"status": "received", "classification": payload.classification}


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_reports():
    query = """
        SELECT id, classification, confidence_pct, image_url, verified, submitted_at
        FROM reports
        ORDER BY submitted_at DESC
        LIMIT 50
    """
    rows = await database.fetch_all(query)
    return [dict(r) for r in rows]
