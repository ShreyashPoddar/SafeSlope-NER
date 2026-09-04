from typing import Optional, Dict, Any, List
from pydantic import BaseModel



# --- Member 4 (IoT hardware) sends this ---
class TelemetryPayload(BaseModel):
    sensor_id: str
    lat: float
    lng: float
    tilt_delta: float
    soil_moisture: float
    risk_state: Optional[str] = None
    trigger_cause: Optional[str] = None
    pitch_deg: Optional[float] = None
    roll_deg: Optional[float] = None
    pore_pressure_kpa: Optional[float] = None
    packet_sequence_id: Optional[int] = None
    mpu_ok: Optional[bool] = None


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


# --- Landslide Algorithm Integration Payload ---
class LandslideAlgorithmPayload(BaseModel):
    zone_id: Optional[int] = 1
    zone_name: str = "Champhai - Serchhip Corridor (NH-54)"
    risk_pct: Optional[float] = None
    predicted_probability: Optional[float] = None
    confidence_pct: float = 85.0
    confidence: Optional[float] = None
    model_version: Optional[str] = "xgboost-landslide-v2"
    source_model: Optional[str] = None
    corridor_id: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rainfall_mm_24h: Optional[float] = None
    soil_moisture_pct: Optional[float] = None
    slope_tilt_deg: Optional[float] = None
    pore_pressure_kpa: Optional[float] = None
    trigger_features: Optional[Dict[str, Any]] = None
    force_notify: Optional[bool] = False



# --- Dynamic Threshold Settings ---
class ThresholdSettingsPayload(BaseModel):
    advisory_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    min_confidence: Optional[float] = None
    auto_notify_on_breach: Optional[bool] = None
    cooldown_minutes: Optional[int] = None
    enabled_channels: Optional[list[str]] = None
    target_audience: Optional[str] = None


# --- Area Directory Community Subscriber ---
class SubscriberPayload(BaseModel):
    phone: str
    name: str = "Corridor Resident"
    zone_name: str = "Champhai - Serchhip Corridor (NH-54)"
    village: Optional[str] = "Serchhip"
    role: str = "citizen"  # "citizen", "aapda_mitra", "village_head", "transport", "deoc"
    channel: str = "whatsapp"  # "whatsapp", "sms", "telegram"
    lang: str = "lus"  # "lus", "as", "kha", "mni", "bn", "en"
    lat: Optional[float] = None
    lng: Optional[float] = None
    telegram_chat_id: Optional[int] = None


# --- Notification Settings Payload for Emergency Broadcast ---
class NotificationSettingsPayload(BaseModel):
    channels: list[str] = ["whatsapp", "sms", "telegram", "cap", "siren"]
    target_audience: str = "all_in_area"  # "all_in_area", "volunteers_only", "full_blast"
    selected_languages: Optional[list[str]] = ["lus", "as", "kha", "mni", "bn", "en"]
    include_bypass: bool = True
    custom_instructions: Optional[str] = None
    urgency: str = "Immediate"
    severity: str = "Severe"
    siren_relay_enabled: bool = True

