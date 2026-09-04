"""
SafeSlope-NER — Core Configuration
Section 5.2 (dual-profile deployment), Section 3.4 (HMAC security),
Section 7.1-7.2 (hysteresis / burn-in constants), Section 5.3 (H3 spatial)
"""
from __future__ import annotations
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Runtime Profile ──────────────────────────────────────────────────────
    # laptop-workstation-cpu  → Ollama + Redis Streams + ONNX FP16
    # cloud-production-gpu    → vLLM + Redpanda + TensorRT
    RUNTIME_PROFILE: str = "laptop-workstation-cpu"

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://resiliner_user:resiliner_pass@db:5432/resiliner"

    # ─── Redis Feature Store & Deduplication ──────────────────────────────────
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_MAXMEM_MB: int = 2048

    # ─── Security & Authentication ────────────────────────────────────────────
    SERVICE_API_KEY: str = "dev-only-change-me"
    JWT_SECRET: str = "dev-only-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_SECONDS: int = 43200  # 12 hours
    GOOGLE_CLIENT_ID: str = "your-google-client-id.apps.googleusercontent.com"
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # HMAC-SHA256 gateway authentication key (Section 3.4)
    # All LoRa concentrator gateways must sign binary payloads with this secret.
    GATEWAY_HMAC_SECRET: str = "change-this-gateway-hmac-secret"
    HMAC_TOLERANCE_SECONDS: int = 300  # Replay window: reject payloads older than 5 min

    # DM PIN hashing (Section 8.2) — bcrypt rounds
    DM_PIN_BCRYPT_ROUNDS: int = 12

    # ─── Live Hardware Bridge (Member-2 / Ngrok Endpoint) ─────────────────────
    HARDWARE_BRIDGE_URL: str = "https://unknown-remold-lavish.ngrok-free.dev"
    HARDWARE_BRIDGE_ENABLED: bool = True
    HARDWARE_POLL_INTERVAL_SECONDS: float = 5.0

    # ─── LLM / RAG Configuration ──────────────────────────────────────────────
    # Laptop profile: Ollama with 4-bit quantized 3B model (~4.8 GB VRAM)
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    # Cloud profile: vLLM with full 8B instruct model (16-24 GB VRAM)
    VLLM_BASE_URL: str = "http://vllm:8001"
    LLM_MODEL_NAME: str = "llama3.2:3b"          # Override to llama3:8b-instruct-q4_K_M on cloud
    LLM_TIMEOUT_SECONDS: int = 120
    RAG_TOP_K_CHUNKS: int = 5
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"   # sentence-transformers, 384 dims

    # ─── Spatial / H3 Parameters (Section 5.3) ────────────────────────────────
    # Resolution 9 (~105m radius): Watershed hydrological accumulation
    H3_RESOLUTION_COARSE: int = 9
    # Resolution 10 (~40m radius): Road cuttings, retaining walls, sensor clusters
    H3_RESOLUTION_FINE: int = 10
    # 800m corridor buffer — cuts active compute from 224M → <60k cells (99.97% reduction)
    CORRIDOR_BUFFER_M: float = 800.0
    UTM_CRS: str = "EPSG:32646"  # UTM Zone 46N — canonical NE India grid

    # ─── Physics Engine Constants (Section 6.2) ────────────────────────────────
    # Empirical rainfall threshold coefficients: I_crit = A * D^(-B)
    RAINFALL_THRESHOLD_A: float = 5.8294
    RAINFALL_THRESHOLD_B: float = 0.4141
    # Culvert clogged penalty: I_crit_adjusted = I_crit * CVI_PENALTY
    CVI_THRESHOLD_PENALTY: float = 0.70          # 30% reduction when culvert blocked
    # Root cohesion parameters for jhum fallow decay c_r(t) = c0 * exp(-κ * t)
    JHUM_ROOT_COHESION_C0_KPA: float = 15.0
    JHUM_DECAY_KAPPA: float = 0.065              # Calibrated for 18-36 month fallow cycle
    # Antecedent Precipitation Index decay factor
    API_DECAY_DELTA: float = 0.88                # Range 0.85–0.92 (Section 6.1)
    API_WINDOW_DAYS: int = 40

    # ─── Anti-"Cry Wolf" Hysteresis (Section 7.1) ──────────────────────────────
    # Emergency warning requires sustained breach for N seconds
    HYSTERESIS_SECONDS: int = 8
    # Minimum creep rate to qualify as plastic deformation
    DEFORMATION_RATE_DEG_PER_MIN: float = 0.05
    # Transient shock threshold (rejected if returned to baseline < 3s)
    TRANSIENT_SPIKE_DEG: float = 3.0
    TRANSIENT_SPIKE_MAX_SEC: float = 3.0

    # ─── Spatial k-out-of-n Consensus (Section 2.5) ────────────────────────────
    CONSENSUS_MIN_NODES: int = 2                 # Min adjacent nodes to confirm
    CONSENSUS_WINDOW_SEC: int = 5                # Time window for concurrent detection
    CONSENSUS_RADIUS_M: float = 150.0            # Spatial cluster radius

    # ─── Day-Zero Cold-Start (Section 7.2) ─────────────────────────────────────
    BURN_IN_DAYS: int = 14                       # Physics-only mode duration

    # ─── Backfill Detection (Section 4.2) ──────────────────────────────────────
    # Packets older than this are backfilled — never trigger live actuations
    BACKFILL_THRESHOLD_SECONDS: int = 300        # 5 minutes

    # ─── Clock Drift / Epoch Anchoring (Section 3.3) ───────────────────────────
    MAX_EPOCH_OFFSET_SECONDS: int = 3600         # Flag for clock resync if exceeded

    # ─── Redis Deduplication TTL (Section 3.4) ─────────────────────────────────
    DEDUP_TTL_SECONDS: int = 120

    # ─── Tier Thresholds (Section 7.4) ─────────────────────────────────────────
    INSAR_COHERENCE_TIER1_MIN: float = 0.35      # Below this → Tier 2 (InSAR blind)
    IOT_ONLINE_TIER3_MIN_FRACTION: float = 0.30  # Below this → Tier 3 (degraded IoT)

    # ─── Event-Delta Compute Thresholds (Section 6.3) ──────────────────────────
    # Only run full inference if features changed beyond these deltas
    DELTA_RAIN_1H_MM: float = 2.5
    DELTA_VWC_PCT: float = 4.0
    DELTA_TILT_DEG: float = 0.2

    # ─── Drift Detection (Section 7.5) ─────────────────────────────────────────
    DRIFT_PSI_THRESHOLD: float = 0.20            # Trigger recalibration if PSI > 0.2
    DRIFT_WASSERSTEIN_THRESHOLD: float = 0.15

    # ─── Model Paths (Section 6.3) ─────────────────────────────────────────────
    CATBOOST_SO_PATH: str = "models/compiled/catboost.so"
    LGBM_SO_PATH: str = "models/compiled/lgbm.so"
    XGB_SO_PATH: str = "models/compiled/xgb.so"
    FNO_MODEL_PATH: str = "models/fno/fno_voellmy.pt"
    GWAVENET_MODEL_PATH: str = "models/gwavenet.pt"
    PINN_MODEL_PATH: str = "models/pinn.pt"
    YOLO_MODEL_PATH: str = "models/yolov11-seg.pt"

    # ─── External Government APIs (Section 4.3) ────────────────────────────────
    IMD_API_BASE: str = "https://api.imd.gov.in/rainfall"
    MOSDAC_API_BASE: str = "https://mosdac.gov.in/api"
    NCS_API_BASE: str = "https://seismo.gov.in/api/recent"
    ECMWF_BACKUP_API: str = "https://api.open-meteo.com/v1"
    CIRCUIT_BREAKER_FAIL_MAX: int = 3
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 60     # Seconds before half-open retry

    # ─── Satellite Earth Observation & Remote Sensing APIs (Section 2.2) ───────
    # Google Earth Engine (GEE)
    GEE_SERVICE_ACCOUNT: str = ""
    GEE_SERVICE_ACCOUNT_KEY_PATH: str = "credentials/gee-key.json"
    GEE_PROJECT_ID: str = ""

    # Copernicus Data Space Ecosystem (CDSE) / Sentinel Hub
    CDSE_CLIENT_ID: str = ""
    CDSE_CLIENT_SECRET: str = ""
    SENTINEL_HUB_CLIENT_ID: str = ""
    SENTINEL_HUB_CLIENT_SECRET: str = ""
    SENTINEL_HUB_INSTANCE_ID: str = ""

    # NASA Earthdata & Alaska Satellite Facility (ASF DAAC)
    EARTHDATA_USERNAME: str = ""
    EARTHDATA_PASSWORD: str = ""
    EARTHDATA_BEARER_TOKEN: str = ""

    # ISRO MOSDAC & Bhuvan
    MOSDAC_USER_EMAIL: str = ""
    MOSDAC_API_TOKEN: str = ""
    BHUVAN_API_TOKEN: str = ""

    # Planet Labs (PlanetScope & SkySat)
    PLANET_API_KEY: str = ""

    # OpenTopography (Global DEM Subsetting)
    OPENTOPOGRAPHY_API_KEY: str = ""

    # ─── Actuation SLA (Section 11) ────────────────────────────────────────────
    LORA_BARRIER_SLA_MS: int = 1500             # < 1.5s to physical barrier drop
    SCADA_TRIP_SLA_MS: int = 250                # < 250ms to circuit breaker open
    FEATURE_STORE_SLA_MS: float = 1.0           # < 1.0ms Redis pipeline read
    MVT_TILE_SLA_MS: int = 30                   # < 30ms vector tile delivery
    FNO_RUNOUT_SLA_MS: int = 50                 # < 50ms runout contour generation
    GRAPH_CUT_SLA_MS: int = 20                  # < 20ms Rustworkx isolation traversal

    # ─── Simulation Harness (Section 10.3) ─────────────────────────────────────
    SIMULATION_DURATION_SECONDS: int = 45
    SIMULATION_SCENARIOS: list[str] = [
        "2022_manipur_noney_landslide",
        "nh06_cloudburst_sector_4",
        "nh54_km42_debris_flow",
    ]

    @property
    def is_laptop_profile(self) -> bool:
        return self.RUNTIME_PROFILE == "laptop-workstation-cpu"

    @property
    def is_cloud_profile(self) -> bool:
        return self.RUNTIME_PROFILE == "cloud-production-gpu"

    @property
    def llm_base_url(self) -> str:
        return self.OLLAMA_BASE_URL if self.is_laptop_profile else self.VLLM_BASE_URL


@lru_cache()
def get_settings() -> Settings:
    return Settings()
