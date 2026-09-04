from fastapi import APIRouter, Depends
from app.models.schemas import ReportPayload
from app.database import database
from app.auth import verify_api_key, get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", dependencies=[Depends(verify_api_key)])
async def receive_report(payload: ReportPayload):
    # Enqueue in Member 6 verification queue & live event feed
    from app.comms.queue_service import queue_service
    rep = await queue_service.ingest_report(
        hazard_type=payload.classification,
        classification=payload.classification,
        confidence_pct=payload.confidence_pct,
        severity="HIGH",
        lat=payload.lat,
        lng=payload.lng,
        image_url=payload.image_url,
    )
    return {"status": "received", "classification": payload.classification, "tracking_id": rep["tracking_id"]}


@router.get("/", dependencies=[Depends(get_current_user)])
async def list_reports():
    try:
        query = """
            SELECT id, classification, confidence_pct, image_url, verified, submitted_at
            FROM reports
            ORDER BY submitted_at DESC
            LIMIT 50
        """
        rows = await database.fetch_all(query)
        if rows:
            return [dict(r) for r in rows]
    except Exception:
        pass
    
    from app.comms.queue_service import queue_service
    return queue_service.list_reports()
