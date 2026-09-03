"""
SafeSlope-NER — Pydantic v2 Data Models & API Schemas
Covers all wire protocol fields (Section 3.1), risk assessment (6.3/6.4),
governance orders (Section 8), isolation twin (6.6), and simulation (10.3)
"""
from __future__ import annotations

import struct
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskSource(str, Enum):
    PHYSICS_FLOOR = "physics_floor"
    ENSEMBLE_MODEL = "ensemble_model"
    EXPERT_OVERRIDE = "expert_override"
    EDGE_TRIPWIRE = "edge_tripwire"
    BURN_IN_PHYSICS = "burn_in_physics"


class OperationalTier(int, Enum):
    """Hierarchical Model Degradation Matrix (Section 7.4)"""
    TIER1_FULL_ENSEMBLE = 1       # InSAR coherence ≥ 0.35, edge nodes online
    TIER2_INSAR_BLIND = 2         # Monsoon decorrelation γ < 0.35
    TIER3_DEGRADED_IOT = 3        # Battery cutoff / radio jamming
    TIER4_PHYSICS_ONLY = 4        # Complete telecom blackout


class SensorType(str, Enum):
    INCLINOMETER = "inclinometer"
    GEOPHONE = "geophone"
    ERT = "ert"
    RTK_GNSS = "rtk_gnss"
    FBG = "fbg"
    TURBIDITY = "turbidity"
    EVENT_CAMERA = "event_camera"
    DAS_FIBER = "das_fiber"
    GNSS_R = "gnss_r"
    INFRASOUND = "infrasound"


class PowerMode(int, Enum):
    """Status flags bits 2-3 (Section 3.1)"""
    DEEP_SLEEP = 0    # VWC < 40% — poll every 1 hour
    NORMAL = 1        # VWC 40-70% — poll every 5 min
    BURST = 2         # VWC ≥ 85% or sudden acceleration — continuous streaming
    FAULT = 3         # Hardware fault state


class ReportClassification(str, Enum):
    ROCKFALL = "Rockfall"
    TENSION_CRACK = "Tension_Crack"
    DEBRIS_SLUMP = "Debris_Slump"
    BLOCKED_CULVERT = "Blocked_Culvert"
    SCARP_FORMATION = "Scarp_Formation"
    NORMAL = "Normal"


class AirdropPriority(str, Enum):
    NONE = "NONE"
    SCHEDULED = "SCHEDULED"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class ChokepointType(str, Enum):
    OPEN_ROAD = "OPEN_ROAD"           # 1.0× structural clearance multiplier
    NARROW_CUTTING = "NARROW_CUTTING"  # 1.8×
    CULVERT = "CULVERT"               # 2.5×
    BRIDGE = "BRIDGE"                 # 8.0×


class AuditPayloadType(str, Enum):
    TELEMETRY = "TELEMETRY"
    RISK_SCORE = "RISK_SCORE"
    SOP_ORDER = "SOP_ORDER"
    DM_AUTHORIZATION = "DM_AUTHORIZATION"
    BARRIER_ACTUATION = "BARRIER_ACTUATION"
    SCADA_TRIP = "SCADA_TRIP"
    CAP_DISPATCH = "CAP_DISPATCH"
    VOLUNTEER_VERIFY = "VOLUNTEER_VERIFY"
    SYSTEM_EVENT = "SYSTEM_EVENT"


class RejectionReason(str, Enum):
    CRC_FAIL = "CRC_FAIL"
    HMAC_FAIL = "HMAC_FAIL"
    SCHEMA_RANGE = "SCHEMA_RANGE"
    REPLAY_DUPLICATE = "REPLAY_DUPLICATE"
    MALFORMED_FRAME = "MALFORMED_FRAME"
    POISONING_ATTEMPT = "POISONING_ATTEMPT"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3.1 — 20-BYTE BINARY WIRE PROTOCOL
# Struct format: '<HHhhBBHHHbBH' = 20 bytes exactly
# ═══════════════════════════════════════════════════════════════════════════════

FRAME_FORMAT = "<HHhhBBHHHbBH"  # Section 3.1 canonical spec (20 bytes)
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)  # Equals 20 bytes exactly


class StatusFlags(BaseModel):
    """Decoded status flags byte — Bit-field from Section 3.1"""
    model_config = ConfigDict(frozen=True)

    brittle_shear_trip: bool = False    # Bit 0 — hardware interrupt tripped
    solar_harvesting_active: bool = False  # Bit 1 — panel charging
    power_mode: PowerMode = PowerMode.NORMAL  # Bits 2-3 — duty cycle state
    consensus_flag: bool = False        # Bit 4 — k-out-of-n neighbour verified
    reserved: int = 0                   # Bits 5-7

    @classmethod
    def from_byte(cls, raw_byte: int) -> "StatusFlags":
        bit0 = bool(raw_byte & 0b00000001)
        bit1 = bool(raw_byte & 0b00000010)
        bits23 = (raw_byte >> 2) & 0b11
        bit4 = bool(raw_byte & 0b00010000)
        bits57 = (raw_byte >> 5) & 0b111
        return cls(
            brittle_shear_trip=bit0,
            solar_harvesting_active=bit1,
            power_mode=PowerMode(bits23),
            consensus_flag=bit4,
            reserved=bits57,
        )


class BinaryTelemetryFrame(BaseModel):
    """
    Decoded 20-byte LoRa binary frame (Section 3.1).
    All physical range validations enforce the anti-poisoning clamping spec.
    """
    model_config = ConfigDict(frozen=True)

    # Header
    node_id: int = Field(..., ge=0, le=65535,
                         description="uint16 — supports up to 65,535 registered edge nodes")
    epoch_offset_s: int = Field(..., ge=0, le=65535,
                                description="uint16 — seconds since gateway hourly sync epoch")

    # Tilt (int16 scaled by 100 → ±90.00°)
    pitch_raw: int = Field(..., ge=-9000, le=9000)
    roll_raw: int = Field(..., ge=-9000, le=9000)

    # Hydrology
    vwc_pct: int = Field(..., ge=0, le=100, description="uint8 — volumetric water content %")

    # Battery: V_actual = (raw_value / 100) + 2.0  → range 2.00V to 4.55V (Section 3.1)
    battery_v_raw: int = Field(..., ge=0, le=255,
                               description="uint8 — scaled: V = (raw/100) + 2.0")

    # Pore pressure (uint16 scaled by 10 → 0.0 to 6553.5 kPa)
    pore_pressure_raw: int = Field(..., ge=0, le=65535)

    # Acoustic emission
    ae_count: int = Field(..., ge=0, le=65535, description="uint16 — events/s micro-fracture rate")
    vpp_mv: int = Field(..., ge=0, le=65535, description="uint16 — peak signal energy mV")


    # Temperature (int8 — signed, -40°C to +85°C)
    temp_c: int = Field(..., ge=-40, le=85, description="int8 — ESP32-S3 on-chip thermal")

    # Status flags bitfield
    status_flags_raw: int = Field(..., ge=0, le=255)

    # CRC-16-CCITT checksum
    crc16: int = Field(..., ge=0, le=65535)

    # Computed after decoding (not in wire format)
    gateway_id: Optional[int] = None
    gateway_epoch_utc: Optional[datetime] = None
    true_timestamp: Optional[datetime] = None
    is_backfilled: bool = False

    @property
    def pitch_deg(self) -> float:
        return self.pitch_raw / 100.0

    @property
    def roll_deg(self) -> float:
        return self.roll_raw / 100.0

    @property
    def battery_v(self) -> float:
        return (self.battery_v_raw / 100.0) + 2.0

    @property
    def pore_pressure_kpa(self) -> float:
        return self.pore_pressure_raw / 10.0

    @property
    def status(self) -> StatusFlags:
        return StatusFlags.from_byte(self.status_flags_raw)

    @field_validator("battery_v_raw")
    @classmethod
    def validate_battery(cls, v: int) -> int:
        # Anti-poisoning: reject if decoded voltage is outside [1.8, 4.55]V (Section 3.4)
        actual_v = (v / 100.0) + 2.0
        if actual_v < 1.8 or actual_v > 4.55:
            raise ValueError(f"Battery voltage {actual_v:.2f}V out of physical range [1.8, 4.55]V")
        return v


class BinaryTelemetryBatch(BaseModel):
    """
    LoRa Concentrator Gateway binary batch (Section 3.2).
    4-byte gateway header + N × 20-byte frames.
    """
    gateway_id: int = Field(..., ge=0, le=65535)
    frame_count: int = Field(..., ge=1, le=500,
                             description="uint16 — max 500 frames per batch")
    gateway_epoch_utc: datetime = Field(...,
        description="Gateway's anchored NTP/GPS epoch — used to compute true timestamps")
    frames: list[BinaryTelemetryFrame]
    gateway_hmac: str = Field(..., description="X-Signature-SHA256 from request header")

    @model_validator(mode="after")
    def validate_frame_count(self) -> "BinaryTelemetryBatch":
        if len(self.frames) != self.frame_count:
            raise ValueError(
                f"frame_count header={self.frame_count} but {len(self.frames)} frames decoded"
            )
        return self


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY — JSON Fallback (Full field set from Section 2.1)
# ═══════════════════════════════════════════════════════════════════════════════

class TelemetryPayload(BaseModel):
    """JSON telemetry payload — used when binary wire is not available (HTTP fallback)."""
    sensor_id: str
    recorded_at: datetime

    # Tilt & IMU
    pitch: Optional[float] = Field(None, ge=-90.0, le=90.0)
    roll: Optional[float] = Field(None, ge=-90.0, le=90.0)
    tilt_velocity: Optional[float] = None
    ax: Optional[float] = Field(None, ge=-20.0, le=20.0)
    ay: Optional[float] = Field(None, ge=-20.0, le=20.0)
    az: Optional[float] = Field(None, ge=-20.0, le=20.0)
    wx: Optional[float] = None
    wy: Optional[float] = None
    wz: Optional[float] = None
    rms_vibration: Optional[float] = Field(None, ge=0.0)

    # RTK-GNSS
    delta_x_mm: Optional[float] = None
    delta_y_mm: Optional[float] = None
    delta_z_mm: Optional[float] = None

    # Hydrology
    vwc_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    pore_pressure: Optional[float] = Field(None, ge=0.0, le=7000.0)
    matric_suction: Optional[float] = None
    saturation_index: Optional[float] = Field(None, ge=0.0, le=1.0)

    # ERT
    apparent_resistivity: Optional[float] = Field(None, ge=0.0)

    # FBG
    fbg_micro_strain: Optional[float] = None
    fbg_load_kn: Optional[float] = None

    # Acoustic emission / geophone
    ae_count: Optional[int] = Field(None, ge=0)
    vpp_mv: Optional[int] = Field(None, ge=0)
    brittle_trip: bool = False

    # Power health
    battery_v: Optional[float] = Field(None, ge=1.8, le=4.55)
    battery_soc_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    solar_vpv: Optional[float] = Field(None, ge=0.0)
    internal_temp_c: Optional[float] = Field(None, ge=-40.0, le=85.0)

    # LoRa link quality
    rssi_dbm: Optional[float] = Field(None, ge=-130.0, le=0.0)
    snr_db: Optional[float] = Field(None, ge=-25.0, le=15.0)
    sequence_id: Optional[int] = Field(None, ge=0)
    edge_anomaly_score: Optional[float] = Field(None, ge=0.0, le=1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# SENSOR REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class SensorCreate(BaseModel):
    sensor_id: str = Field(..., min_length=3, max_length=64)
    sensor_type: SensorType
    gateway_id: Optional[int] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-90.0, le=180.0)
    installation_angle_offset: float = Field(0.0, ge=-5.0, le=5.0)
    firmware_version: str = "v1.0.0-esp32s3"
    burn_in_expires_at: Optional[datetime] = None


class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sensor_id: str
    sensor_type: str
    gateway_id: Optional[int]
    latitude: float
    longitude: float
    active_status: bool
    burn_in_expires_at: Optional[datetime]
    is_burn_in_mode: bool
    created_at: datetime


class SensorHealthResponse(BaseModel):
    sensor_id: str
    last_seen: Optional[datetime]
    battery_v: Optional[float]
    battery_soc_pct: Optional[float]
    rssi_dbm: Optional[float]
    active_status: bool
    is_burn_in_mode: bool
    last_risk_level: Optional[str]


# ═══════════════════════════════════════════════════════════════════════════════
# SHAP EXPLAINABILITY (Section 6.4)
# ═══════════════════════════════════════════════════════════════════════════════

class ShapDriver(BaseModel):
    """Top physical driver from TreeSHAP attribution (Section 6.4)."""
    factor: str            # Human-readable name e.g. '72h Antecedent Precipitation'
    feature_key: str       # Machine key e.g. 'api_40d'
    weight_pct: float      # Shapley attribution percentage
    value: Optional[float] = None  # Actual feature value


# ═══════════════════════════════════════════════════════════════════════════════
# RISK ASSESSMENT (Sections 6.2, 6.3, 6.4, 7.4)
# ═══════════════════════════════════════════════════════════════════════════════

class PhysicsResult(BaseModel):
    """Raw geotechnical physics outputs (Section 6.2)."""
    fos: float                          # Modified Mohr-Coulomb Factor of Safety
    fos_safe: bool                      # fos >= 1.0
    psi_m_kpa: Optional[float] = None  # Matric suction (kPa)
    k_sat_ms: Optional[float] = None   # Saturated hydraulic conductivity (m/s)
    root_cohesion_kpa: float = 0.0     # Dynamic jhum c_r(t) (kPa)
    rainfall_threshold_exceeded: bool = False
    rainfall_margin_pct: float = 0.0
    deformation_status: str = "MONITORING"  # SHOCK / SUSTAINED_PLASTIC / MONITORING


class RiskAssessmentResponse(BaseModel):
    """Full risk assessment response from the 7-stage pipeline (Sections 6.2–6.4)."""
    zone_id: int
    zone_name: str
    lgd_district_code: str

    # Primary risk metrics
    risk_pct: float = Field(..., ge=0.0, le=100.0)
    confidence_pct: float = Field(..., ge=0.0, le=100.0)
    status: RiskLevel
    risk_source: RiskSource

    # Physics
    physics: PhysicsResult

    # ML ensemble (None during burn-in or Tier 4)
    top_drivers: list[ShapDriver] = []
    base_model_probs: Optional[dict[str, float]] = None  # catboost/lgbm/xgb/tabnet probs

    # Operational state
    tier_mode: OperationalTier
    is_burn_in_mode: bool = False
    weather_source: str = "IMD_DIRECT"
    data_provenance: str = "DIRECT"

    # Deterministic safety overrides triggered (Section 6.3)
    seismic_override: bool = False
    toe_cut_override: bool = False
    brittle_trip_override: bool = False

    assessed_at: datetime


class RiskZoneCreate(BaseModel):
    zone_name: str
    corridor_code: str
    lgd_district_code: str
    lgd_state_code: Optional[str] = None
    boundary_geojson: dict          # GeoJSON Polygon


class RiskZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    zone_name: str
    corridor_code: str
    lgd_district_code: str
    current_risk: str
    operational_tier: int
    ml_risk_pct: Optional[float]
    ml_confidence_pct: Optional[float]
    fos_value: Optional[float]
    shap_drivers: Optional[dict]
    weather_source: str
    updated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# ROAD NETWORK & ISOLATION TWIN (Section 6.6, 2.9)
# ═══════════════════════════════════════════════════════════════════════════════

class RoadEdgeCreate(BaseModel):
    osm_id: Optional[int] = None
    u_node: int
    v_node: int
    geometry_geojson: dict          # GeoJSON LineString
    associated_zone_id: Optional[int] = None
    highway_type: str
    length_m: float = Field(..., gt=0.0)
    chokepoint_type: ChokepointType = ChokepointType.OPEN_ROAD
    is_strategic_defence: bool = False
    culvert_vulnerability_index: float = Field(0.0, ge=0.0, le=1.0)
    pedestrian_accessible: bool = False


class IsolationResult(BaseModel):
    """
    Isolation-Impact Twin output (Section 6.6).
    Converts geotechnical failure into human-impact metrics.
    """
    zone_id: int
    trigger_source: str
    severed_edge_ids: list[int]
    isolated_village_ids: list[int]
    isolated_village_names: list[str]

    # Population (WorldPop + FASTag scaling)
    permanent_pop_affected: int
    transient_pop_affected: int
    total_pop_isolated: int
    estimated_blockage_days: float

    # PDS depletion tracking (Section 6.6)
    pds_stockout_horizon_days: float
    airdrop_priority_level: AirdropPriority
    critical_facilities: list[str]  # e.g. ["Primary Health Centre — Nongstoin", "School — Mawryngkneng"]

    # LDOF risk (Section 2.10)
    ldof_risk_detected: bool = False
    ldof_breach_time_hrs: Optional[float] = None
    ldof_flood_height_m: Optional[float] = None

    # Summary narrative
    summary: str  # e.g. "Slope failure at KM 42 (NH-54). 6 villages, ~2,400 people isolated for 4 days."

    computed_at: datetime


class VillageCreate(BaseModel):
    village_name: str
    lgd_village_code: Optional[str] = None
    lgd_district_code: str
    lgd_state_code: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-90.0, le=180.0)
    graph_node_id: Optional[int] = None
    permanent_population: int = Field(..., gt=0)
    fastag_baseline_daily: int = 0
    pds_grain_stock_kg: float = 5000.0
    pds_fuel_stock_litres: float = 1200.0
    daily_consumption_burn_rate: float = 1.2
    has_primary_health_centre: bool = False
    has_school: bool = True
    has_pds_warehouse: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# CITIZEN REPORTS & COMPUTER VISION (Sections 2.9, 2.7)
# ═══════════════════════════════════════════════════════════════════════════════

class ReportCreate(BaseModel):
    submitter_phone: Optional[str] = None
    submitter_role: str = "CITIZEN"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-90.0, le=180.0)
    image_url: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    report_uuid: str
    location_lat: float
    location_lng: float
    ai_classification: Optional[str]
    ai_confidence_pct: Optional[float]
    crack_width_cm: Optional[float]
    crack_length_m: Optional[float]
    nearest_road_edge_id: Optional[int]
    cvi_delta: float
    aapda_mitra_dispatched: bool
    verified_by_volunteer: bool
    submitted_at: datetime


class VisionResult(BaseModel):
    """YOLOv11-Seg + SAM-2 outputs (Section 2.9)"""
    classification: ReportClassification
    confidence_pct: float
    crack_width_cm: Optional[float] = None
    crack_length_m: Optional[float] = None
    debris_volume_estimate_m3: Optional[float] = None
    bounding_box: Optional[list[float]] = None  # [x1, y1, x2, y2] normalized


# ═══════════════════════════════════════════════════════════════════════════════
# ADMINISTRATIVE GOVERNANCE — HITL (Sections 8.1–8.5)
# ═══════════════════════════════════════════════════════════════════════════════

class EvacuationOrderCreate(BaseModel):
    """
    Operator creates an evacuation order proposal (ROLE_OPERATOR).
    DM authorizes it separately (ROLE_MAGISTRATE).
    DMA 2005 Section 34 HITL requirement.
    """
    zone_id: int
    lgd_district_code: str
    lgd_state_code: Optional[str] = None
    isolation_event_id: Optional[int] = None
    affected_population: int
    detour_route_description: Optional[str] = None
    # Sunset gating flag (Section 6.7 / 2.8):
    # If predicted failure overlaps 18:00–06:00 IST, system adds daytime restriction clause
    sunset_gating_check: bool = True


class EvacuationOrderAuthorize(BaseModel):
    """
    District Magistrate / DDMA Chairman authorization (ROLE_MAGISTRATE).
    Requires 6-digit PIN — Section 8.2 HITL workflow step 3.
    """
    order_id: int
    dm_pin: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    authorized_by: str  # DM name / official designation


class SopOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_uuid: str
    zone_id: int
    lgd_district_code: str
    affected_population: int
    dm_authorized: bool
    authorized_by: Optional[str]
    authorized_at: Optional[datetime]
    order_pdf_url: Optional[str]
    cap_alert_xml: Optional[str]
    cap_xsd_validated: bool
    sunset_gating_triggered: bool
    lora_barrier_actuated: bool
    scada_grid_islanded: bool
    whatsapp_broadcast_sent: bool
    generated_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LEDGER (Section 8.5)
# ═══════════════════════════════════════════════════════════════════════════════

class AuditLedgerEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    previous_hash: str
    block_hash: str
    payload_type: str
    payload_data: dict[str, Any]
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULATION HARNESS (Section 10.3)
# 1-Click Crisis Disaster Simulation (45-second deterministic replay)
# ═══════════════════════════════════════════════════════════════════════════════

class SimulationTriggerRequest(BaseModel):
    scenario: str = Field(
        "nh54_km42_debris_flow",
        description="Scenario key — see config SIMULATION_SCENARIOS"
    )
    # Allow partial simulation for testing individual stages
    run_up_to_stage: int = Field(7, ge=1, le=7)


class SimulationStageResult(BaseModel):
    stage: int
    stage_name: str
    elapsed_ms: float
    outputs: dict[str, Any]
    success: bool
    error: Optional[str] = None


class SimulationStatusResponse(BaseModel):
    scenario: str
    total_elapsed_ms: float
    stages: list[SimulationStageResult]
    final_risk_pct: Optional[float]
    final_status: Optional[str]
    total_pop_isolated: Optional[int]
    pds_stockout_days: Optional[float]
    evacuation_order_generated: bool
    audit_trail_length: int
    success: bool


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY & INGESTION RESPONSES
# ═══════════════════════════════════════════════════════════════════════════════

class BatchIngestionResponse(BaseModel):
    gateway_id: int
    frames_received: int
    frames_accepted: int
    frames_quarantined: int
    frames_deduplicated: int
    frames_backfilled: int
    backfill_alarms_suppressed: int
    processing_ms: float


class QuarantineEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rejection_reason: str
    gateway_id: Optional[int]
    source_ip: Optional[str]
    node_id_raw: Optional[int]
    received_at: datetime
