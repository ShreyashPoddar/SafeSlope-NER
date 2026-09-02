from typing import Optional
from pydantic import BaseModel


# --- Member 4 (IoT hardware) sends this ---
class TelemetryPayload(BaseModel):
    sensor_id: str
    lat: float
    lng: float
    tilt_delta: float
    soil_moisture: float


# --- Member 2 (Geospatial/Rules) sends this back ---
class RulesResult(BaseModel):
    zone_id: int
    risk_level: str  # "HIGH" / "MODERATE" / "LOW"
    source: str = "physics_floor"


# --- Member 3 (ML/Isolation Twin) sends these back ---
class MLResult(BaseModel):
    zone_id: int
    ml_risk_pct: float
    confidence_pct: float


class IsolationResult(BaseModel):
    zone_id: int
    isolated_villages: int
    affected_population: int
    facilities_cut_off: list[str] = []


# --- Member 6 (WhatsApp/CV) sends this ---
class ReportPayload(BaseModel):
    lat: float
    lng: float
    classification: str  # "Rockfall" / "Road Crack" / "Landslide Scars"
    confidence_pct: float
    image_url: Optional[str] = None


# --- Admin/setup: registering the real-world data other members need ---
class VillagePayload(BaseModel):
    village_name: str
    lat: float
    lng: float
    population: int


class RiskZonePayload(BaseModel):
    zone_name: str


# --- Google Sign-In: what the dashboard sends after a user logs in ---
class GoogleLoginPayload(BaseModel):
    id_token: str
