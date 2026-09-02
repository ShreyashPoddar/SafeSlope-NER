from fastapi import APIRouter, Depends
from app.models.schemas import TelemetryPayload
from app.database import database
from app.auth import verify_api_key

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/", dependencies=[Depends(verify_api_key)])
async def receive_telemetry(payload: TelemetryPayload):
    # Keep the sensor's known location up to date (PostGIS point)
    upsert_sensor = """
        INSERT INTO sensors (sensor_id, location)
        VALUES (:sensor_id, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
        ON CONFLICT (sensor_id) DO UPDATE SET location = EXCLUDED.location
    """
    await database.execute(
        upsert_sensor, payload.model_dump(include={"sensor_id", "lat", "lng"})
    )

    # Store the actual reading
    insert_reading = """
        INSERT INTO telemetry_readings (sensor_id, tilt_delta, soil_moisture)
        VALUES (:sensor_id, :tilt_delta, :soil_moisture)
    """
    await database.execute(
        insert_reading, payload.model_dump(exclude={"lat", "lng"})
    )

    return {"status": "received", "sensor_id": payload.sensor_id}


@router.get("/sensors")
async def list_sensors():
    """Note: this is registered before /{sensor_id} on purpose — a static
    path must come before a dynamic one, or FastAPI would treat the word
    "sensors" as a sensor_id and this would never get hit."""
    rows = await database.fetch_all("SELECT id, sensor_id FROM sensors ORDER BY id")
    return [dict(r) for r in rows]


@router.get("/{sensor_id}")
async def get_sensor_history(sensor_id: str):
    query = """
        SELECT tilt_delta, soil_moisture, recorded_at
        FROM telemetry_readings
        WHERE sensor_id = :sensor_id
        ORDER BY recorded_at DESC
        LIMIT 20
    """
    rows = await database.fetch_all(query, {"sensor_id": sensor_id})
    return {"sensor_id": sensor_id, "readings": [dict(r) for r in rows]}
