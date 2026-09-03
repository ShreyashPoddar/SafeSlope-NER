-- ============================================================================================
-- SafeSlope-NER PRODUCTION DATABASE SCHEMA (v3.0.0)
-- PostgreSQL 16 + PostGIS 3.4 + TimescaleDB + pgvector
-- Implements full 11-table schema from Section 9.1 of computational_backend_plan.txt
-- ============================================================================================

-- ─────────────────────────────────────────────
-- EXTENSIONS
-- ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- for text search on reports

-- ============================================================================================
-- TABLE 1: SENSORS — Hardware Registry
-- Covers: Section 2.1 (all sensor types), Section 7.2 (burn-in protocol), Section 3.3 (gateway)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS sensors (
    id               SERIAL PRIMARY KEY,
    sensor_id        TEXT UNIQUE NOT NULL,
    sensor_type      TEXT NOT NULL CHECK (sensor_type IN (
                         'inclinometer',   -- MPU6050/ADXL345 tilt + IMU
                         'geophone',       -- Piezoelectric bedrock acoustic emission
                         'ert',            -- Electrical Resistivity Tomography probes
                         'rtk_gnss',       -- u-blox ZED-F9P translational tripwire
                         'fbg',            -- Fiber Bragg Grating strain + load cell
                         'turbidity',      -- Spring water NTU optical sensor
                         'event_camera',   -- Neuromorphic DVS gantry camera
                         'das_fiber',      -- Distributed Acoustic Sensing interrogator
                         'gnss_r',         -- GNSS-Reflectometry soil moisture
                         'infrasound'      -- Tripartite infrasound pressure array
                     )),
    gateway_id       INT,                   -- LoRa concentrator gateway serving this node
    location         GEOMETRY(Point, 4326) NOT NULL,
    corridor_h3_r9   TEXT,                 -- H3 Resolution-9 cell index (watershed scale)
    corridor_h3_r10  TEXT,                 -- H3 Resolution-10 cell index (road cutting scale)
    installation_angle_offset FLOAT DEFAULT 0.0,  -- Hardware mounting tilt compensation
    firmware_version TEXT DEFAULT 'v1.0.0-esp32s3',
    active_status    BOOLEAN DEFAULT TRUE,
    -- Day-Zero Cold-Start Protocol (Section 7.2): ML disabled until burn-in expires
    burn_in_expires_at TIMESTAMPTZ,        -- NULL means fully commissioned
    -- Node power characterisation
    nominal_vbat_min FLOAT DEFAULT 2.8,   -- LiFePO4 cutoff voltage (V)
    nominal_vbat_max FLOAT DEFAULT 4.55,   -- Fully charged voltage (V)
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_sensors_location   ON sensors USING GIST(location);
CREATE INDEX idx_sensors_h3_r9      ON sensors (corridor_h3_r9);
CREATE INDEX idx_sensors_h3_r10     ON sensors (corridor_h3_r10);
CREATE INDEX idx_sensors_gateway    ON sensors (gateway_id);

-- ============================================================================================
-- TABLE 2: TELEMETRY_READINGS — TimescaleDB Hypertable (All 20-byte wire protocol fields)
-- Covers: Section 2.1 (all 19 raw/derived sensor signals), Section 3.1 (wire protocol fields),
--         Section 4.2 (backfill flag), Section 7.1 (tilt velocity for creep rate)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS telemetry_readings (
    id                   BIGSERIAL,
    sensor_id            TEXT REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    recorded_at          TIMESTAMPTZ NOT NULL,            -- True anchored timestamp (§3.3)
    received_at          TIMESTAMPTZ DEFAULT NOW(),       -- Server receipt time
    is_backfilled        BOOLEAN DEFAULT FALSE,           -- Packet older than 5 min (§4.2)

    -- ── Tilt & Kinematics (MPU6050 / ADXL345) ──────────────────────────────────────────
    pitch                FLOAT,                           -- deg, Kalman-filtered inclination
    roll                 FLOAT,                           -- deg, complementary-filtered roll
    tilt_velocity        FLOAT,                           -- deg/min, creep rate dθ/dt
    ax                   FLOAT,                           -- g, raw tri-axial acceleration X
    ay                   FLOAT,                           -- g, raw tri-axial acceleration Y
    az                   FLOAT,                           -- g, raw tri-axial acceleration Z
    wx                   FLOAT,                           -- deg/s, angular velocity X
    wy                   FLOAT,                           -- deg/s, angular velocity Y
    wz                   FLOAT,                           -- deg/s, angular velocity Z
    rms_vibration        FLOAT,                           -- g, RMS vibration amplitude

    -- ── RTK-GNSS Translational Slide Tripwire (u-blox ZED-F9P) ────────────────────────
    delta_x_mm           FLOAT,                           -- mm, eastward displacement
    delta_y_mm           FLOAT,                           -- mm, northward displacement
    delta_z_mm           FLOAT,                           -- mm, vertical displacement

    -- ── Hydrological & Subsurface Stress ────────────────────────────────────────────────
    vwc_pct              FLOAT,                           -- %, volumetric water content θ
    pore_pressure        FLOAT,                           -- kPa, positive pore-water pressure u_w
    matric_suction       FLOAT,                           -- kPa, negative pressure ψ_m (capillary)
    saturation_index     FLOAT,                           -- 0-1, S_r void fraction occupied by water

    -- ── Electrical Resistivity (ERT slip-surface profiling) ─────────────────────────────
    apparent_resistivity FLOAT,                           -- Ω·m, Wenner/Schlumberger electrode array

    -- ── Fiber Bragg Grating Strain (rock bolts & retaining wall anchors) ────────────────
    fbg_micro_strain     FLOAT,                           -- με, optical strain reading
    fbg_load_kn          FLOAT,                           -- kN, anchor tensile load

    -- ── Acoustic Emission / Geophone Micro-fracture Detection ───────────────────────────
    ae_count             INT,                             -- events/s, brittle rock micro-fracture rate
    vpp_mv               INT,                             -- mV, peak energy of stress-wave burst
    brittle_trip         BOOLEAN DEFAULT FALSE,           -- hardware interrupt flag (bit 0 of status)

    -- ── Power Circuit & Hardware Health ─────────────────────────────────────────────────
    battery_v            FLOAT,                           -- V, terminal voltage (2.0–4.55V)
    battery_soc_pct      FLOAT,                           -- %, state of charge estimate
    solar_vpv            FLOAT,                           -- V, photovoltaic harvesting voltage
    internal_temp_c      FLOAT,                           -- °C, on-chip thermal sensor

    -- ── LoRa Link Quality & Telemetry Diagnostics ───────────────────────────────────────
    rssi_dbm             FLOAT,                           -- dBm, received signal strength indicator
    snr_db               FLOAT,                           -- dB, signal-to-noise ratio
    sequence_id          BIGINT,                          -- Transmission counter for deduplication
    power_mode           SMALLINT,                        -- 0=DeepSleep 1=Normal 2=Burst 3=Fault
    solar_active         BOOLEAN DEFAULT FALSE,           -- Bit 1 of status flags
    consensus_flag       BOOLEAN DEFAULT FALSE,           -- Bit 4: k-out-of-n neighbour verified
    edge_anomaly_score   FLOAT,                           -- 0.0–1.0, TinyML on-board anomaly score
    data_provenance      TEXT DEFAULT 'DIRECT'            -- DIRECT / KRIGING_IMPUTED / SYNTHETIC
);

-- Convert to TimescaleDB hypertable — 7-day chunks (Section 9.2)
SELECT create_hypertable(
    'telemetry_readings', 'recorded_at',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- TimescaleDB Compression (Section 9.2): compress chunks older than 14 days
ALTER TABLE telemetry_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby   = 'recorded_at DESC'
);
SELECT add_compression_policy('telemetry_readings', INTERVAL '14 days');

-- Data retention: keep 365 days of raw telemetry
SELECT add_retention_policy('telemetry_readings', INTERVAL '365 days');

CREATE INDEX idx_telemetry_sensor_time ON telemetry_readings (sensor_id, recorded_at DESC);
CREATE INDEX idx_telemetry_backfilled  ON telemetry_readings (is_backfilled, recorded_at DESC);

-- ============================================================================================
-- TABLE 3: QUARANTINE_TELEMETRY — Dead-Letter Queue (DLQ) Storage
-- Covers: Section 3.5 (DLQ quarantine), Section 3.4 (CRC fail / schema violation packets)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS quarantine_telemetry (
    id               BIGSERIAL PRIMARY KEY,
    raw_payload      BYTEA,                               -- raw 20-byte binary frame
    rejection_reason TEXT NOT NULL CHECK (rejection_reason IN (
                         'CRC_FAIL',                      -- CRC-16-CCITT mismatch
                         'HMAC_FAIL',                     -- Gateway HMAC-SHA256 mismatch
                         'SCHEMA_RANGE',                  -- Physical value out of bounds
                         'REPLAY_DUPLICATE',              -- Sequence ID seen within 120s
                         'MALFORMED_FRAME',               -- Frame length ≠ 20 bytes
                         'POISONING_ATTEMPT'              -- Executable strings in text fields
                     )),
    gateway_id       INT,
    source_ip        TEXT,
    node_id_raw      INT,                                 -- Raw node_id before validation
    received_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_quarantine_time   ON quarantine_telemetry (received_at DESC);
CREATE INDEX idx_quarantine_reason ON quarantine_telemetry (rejection_reason);

-- ============================================================================================
-- TABLE 4: RISK_ZONES — Spatial Corridor Sectors with LGD Scoping
-- Covers: Section 5.3 (H3 corridor masking), Section 8.1 (LGD district codes),
--         Section 6.3 (ensemble outputs), Section 6.4 (SHAP drivers, conformal confidence)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS risk_zones (
    id                        SERIAL PRIMARY KEY,
    zone_name                 TEXT UNIQUE NOT NULL,
    corridor_code             TEXT NOT NULL,              -- e.g. 'NH-54-KM-38-45'
    lgd_district_code         TEXT NOT NULL,              -- Census LGD code e.g. '272' (East Khasi Hills)
    lgd_state_code            TEXT,                       -- e.g. '17' (Meghalaya)
    boundary                  GEOMETRY(Polygon, 4326) NOT NULL,
    h3_r9_cells               TEXT[],                     -- H3 Resolution-9 cells covering this zone
    h3_r10_cells              TEXT[],                     -- H3 Resolution-10 cells covering this zone

    -- Current risk state
    current_risk              TEXT DEFAULT 'LOW' CHECK (current_risk IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    risk_source               TEXT DEFAULT 'ensemble_model' CHECK (risk_source IN (
                                  'physics_floor',        -- Mohr-Coulomb FoS hard override
                                  'ensemble_model',       -- ML stacking meta-learner
                                  'expert_override',      -- Manual DEOC operator override
                                  'edge_tripwire',        -- Direct hardware brittle_trip
                                  'burn_in_physics'       -- Physics-only during 14-day burn-in
                              )),
    operational_tier          SMALLINT DEFAULT 1 CHECK (operational_tier BETWEEN 1 AND 4),

    -- ML ensemble outputs (Section 6.3 / 6.4)
    ml_risk_pct               FLOAT,                      -- % failure probability from stacking meta-learner
    ml_confidence_pct         FLOAT,                      -- % conformal prediction confidence
    shap_drivers              JSONB,                      -- Top-3 SHAP factors + weights

    -- Physics outputs (Section 6.2)
    fos_value                 FLOAT,                      -- Mohr-Coulomb Factor of Safety
    rainfall_intensity_mmhr   FLOAT,                      -- Instantaneous I (mm/hr)
    antecedent_precip_40d     FLOAT,                      -- API-40d (mm)
    insar_velocity_mmyr       FLOAT,                      -- InSAR v_LOS (mm/year)
    insar_coherence           FLOAT,                      -- γ interferometric coherence (0–1)

    -- Governance
    culvert_clogged           BOOLEAN DEFAULT FALSE,       -- CVI-triggered threshold penalty
    sentinel2_toe_cut         BOOLEAN DEFAULT FALSE,       -- Fresh road-cut excavation detected
    ncs_seismic_trigger       BOOLEAN DEFAULT FALSE,       -- NCS earthquake M≥3.0 nearby

    -- Provenance
    weather_source            TEXT DEFAULT 'IMD_DIRECT',   -- IMD_DIRECT / ECMWF_BACKUP / LOCAL_OROGRAPHIC_ESTIMATE
    updated_at                TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_risk_zones_boundary      ON risk_zones USING GIST(boundary);
CREATE INDEX idx_risk_zones_lgd           ON risk_zones (lgd_district_code);
CREATE INDEX idx_risk_zones_current_risk  ON risk_zones (current_risk);
CREATE INDEX idx_risk_zones_tier          ON risk_zones (operational_tier);

-- ============================================================================================
-- TABLE 5: ROAD_EDGES — Transportation Graph with Chokepoint Multipliers
-- Covers: Section 6.6 (isolation twin, structural multipliers), Section 2.8 (strategic defence),
--         Section 2.7 (culvert vulnerability index)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS road_edges (
    id                           SERIAL PRIMARY KEY,
    osm_id                       BIGINT,                  -- OpenStreetMap way ID
    u_node                       BIGINT NOT NULL,         -- Origin graph node ID
    v_node                       BIGINT NOT NULL,         -- Destination graph node ID
    geometry                     GEOMETRY(LineString, 4326) NOT NULL,
    associated_zone_id           INT REFERENCES risk_zones(id) ON DELETE SET NULL,
    highway_type                 TEXT NOT NULL,           -- 'national_highway' / 'state_highway' / 'village_road'
    length_m                     FLOAT NOT NULL,

    -- Chokepoint classification & structural clearance multipliers (Section 6.6)
    chokepoint_type              TEXT DEFAULT 'OPEN_ROAD' CHECK (chokepoint_type IN (
                                     'OPEN_ROAD',          -- baseline 1.0×
                                     'NARROW_CUTTING',     -- 1.8× clearance multiplier
                                     'CULVERT',            -- 2.5× clearance multiplier
                                     'BRIDGE'              -- 8.0× clearance multiplier
                                 )),
    structural_duration_multiplier FLOAT DEFAULT 1.0,     -- Actual multiplier value
    is_severed                   BOOLEAN DEFAULT FALSE,   -- Runtime: edge cut by debris runout polygon
    is_strategic_defence         BOOLEAN DEFAULT FALSE,   -- BRO / LAC priority corridor (§2.8)

    -- Culvert Vulnerability Index (Section 2.7): clogged culvert penalty
    culvert_vulnerability_index  FLOAT DEFAULT 0.0,       -- 0.0 (clear) to 1.0 (fully blocked)
    last_patrol_inspection       TIMESTAMPTZ,             -- Last Aapda Mitra / citizen report time

    -- Pedestrian accessibility for evacuation pathfinding (Section 2.9)
    pedestrian_accessible        BOOLEAN DEFAULT FALSE,   -- Ridge-line pedestrian escape route
    avoids_drainage_gully        BOOLEAN DEFAULT FALSE,   -- True = safe from debris funneling

    updated_at                   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_road_edges_geom          ON road_edges USING GIST(geometry);
CREATE INDEX idx_road_edges_uv            ON road_edges (u_node, v_node);
CREATE INDEX idx_road_edges_severed       ON road_edges (is_severed);
CREATE INDEX idx_road_edges_defence       ON road_edges (is_strategic_defence);

-- ============================================================================================
-- TABLE 6: VILLAGES & CRITICAL FACILITIES — Demographics with LGD Scoping & PDS Inventory
-- Covers: Section 6.6 (WorldPop integration, PDS depletion formula), Section 2.9 (field ops)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS villages (
    id                           SERIAL PRIMARY KEY,
    village_name                 TEXT NOT NULL,
    lgd_village_code             TEXT UNIQUE,             -- Official LGD village code
    lgd_district_code            TEXT NOT NULL,
    lgd_state_code               TEXT,
    location                     GEOMETRY(Point, 4326) NOT NULL,
    graph_node_id                BIGINT,                  -- OSM node ID in the road graph

    -- Demographics
    permanent_population         INT NOT NULL,            -- WorldPop census resident count
    -- FASTag tourist/transit scaling formula (Section 6.6):
    -- P_total = permanent_population × (1 + (FASTag_actual - FASTag_baseline) / capacity)
    fastag_baseline_daily        INT DEFAULT 0,           -- Historical average vehicle throughput
    resident_capacity_equivalent INT DEFAULT 1,          -- Normalisation denominator

    -- PDS Inventory (Section 6.6 depletion formula)
    pds_grain_stock_kg           FLOAT DEFAULT 5000.0,
    pds_fuel_stock_litres        FLOAT DEFAULT 1200.0,
    pds_medical_units            FLOAT DEFAULT 500.0,
    daily_consumption_burn_rate  FLOAT DEFAULT 1.2,       -- kg or L per person per day

    -- Critical facilities
    has_primary_health_centre    BOOLEAN DEFAULT FALSE,
    has_school                   BOOLEAN DEFAULT TRUE,
    has_pds_warehouse            BOOLEAN DEFAULT FALSE,
    nearest_helipad_location     GEOMETRY(Point, 4326),   -- Air-drop supply and medevac point
    nearest_helipad_dist_km      FLOAT,

    created_at                   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_villages_location    ON villages USING GIST(location);
CREATE INDEX idx_villages_lgd         ON villages (lgd_district_code);
CREATE INDEX idx_villages_graph_node  ON villages (graph_node_id);

-- ============================================================================================
-- TABLE 7: ISOLATION_EVENTS — Road Network Severance & Cascading Impact Logs
-- Covers: Section 6.6 (twin outputs), Section 2.9 (PDS stockout → airdrop escalation)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS isolation_events (
    id                           SERIAL PRIMARY KEY,
    zone_id                      INT REFERENCES risk_zones(id) ON DELETE SET NULL,
    trigger_source               TEXT DEFAULT 'fno_runout', -- fno_runout / flow_r / manual
    severed_edge_ids             INT[],                   -- Road edges removed from graph
    isolated_village_ids         INT[],                   -- Village IDs cut off from network

    -- Population impact (Section 6.6)
    permanent_pop_affected       INT NOT NULL DEFAULT 0,
    transient_pop_affected       INT DEFAULT 0,           -- Tourists + truckers via FASTag
    total_pop_isolated           INT NOT NULL DEFAULT 0,
    estimated_blockage_days      FLOAT NOT NULL,

    -- PDS depletion tracking (Section 6.6):
    -- DaysToDepletion = Stock / (BurnRate × total_pop_isolated)
    pds_stockout_horizon_days    FLOAT NOT NULL DEFAULT 0,
    airdrop_priority_level       TEXT DEFAULT 'NONE' CHECK (airdrop_priority_level IN (
                                     'NONE',              -- Clearance before stockout
                                     'SCHEDULED',         -- Air-drop within 72 hours
                                     'URGENT',            -- Air-drop within 24 hours
                                     'CRITICAL'           -- Immediate military helicopter dispatch
                                 )),

    -- LDOF (Landslide-Dammed Lake Outburst Flood) risk
    ldof_risk_detected           BOOLEAN DEFAULT FALSE,
    ldof_breach_time_hrs         FLOAT,                   -- Estimated dam-breach timeframe
    ldof_flood_height_m          FLOAT,                   -- Downstream peak surge wave height

    -- UAV waypoints export
    drone_kml_url                TEXT,                    -- .kml mission file for volunteer drone operators

    detected_at                  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_isolation_zone_time  ON isolation_events (zone_id, detected_at DESC);
CREATE INDEX idx_isolation_priority   ON isolation_events (airdrop_priority_level);

-- ============================================================================================
-- TABLE 8: REPORTS — Crowdsourced Citizen & Patrol Feeds (WhatsApp + Aapda Mitra)
-- Covers: Section 2.9 (WhatsApp bot, YOLOv11-Seg, SAM-2 metric crack measurement),
--         Section 2.7 (Culvert Vulnerability Index)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS reports (
    id                           SERIAL PRIMARY KEY,
    report_uuid                  UUID DEFAULT gen_random_uuid(),
    submitter_phone              TEXT,                    -- E.164 format or hashed for privacy
    submitter_role               TEXT DEFAULT 'CITIZEN' CHECK (submitter_role IN (
                                     'CITIZEN', 'AAPDA_MITRA', 'HIGHWAY_PATROL', 'BRO_ENGINEER'
                                 )),
    location                     GEOMETRY(Point, 4326) NOT NULL,
    image_url                    TEXT,                    -- Object storage URL

    -- YOLOv11-Seg + SAM-2 computer vision outputs (Section 2.9)
    ai_classification            TEXT CHECK (ai_classification IN (
                                     'Rockfall', 'Tension_Crack', 'Debris_Slump',
                                     'Blocked_Culvert', 'Scarp_Formation', 'Normal'
                                 )),
    ai_confidence_pct            FLOAT,
    crack_width_cm               FLOAT,                  -- EXIF back-projected metric width
    crack_length_m               FLOAT,                  -- EXIF back-projected metric length
    debris_volume_estimate_m3    FLOAT,                  -- Coarse DoD volume estimate

    -- Culvert Vulnerability Index update (Section 2.7)
    nearest_road_edge_id         INT REFERENCES road_edges(id) ON DELETE SET NULL,
    cvi_delta                    FLOAT DEFAULT 0.0,      -- CVI increment from this report

    -- Aapda Mitra verification workflow (Section 2.9)
    aapda_mitra_dispatched       BOOLEAN DEFAULT FALSE,
    volunteer_id                 TEXT,
    verified_by_volunteer        BOOLEAN DEFAULT FALSE,
    verification_comment         TEXT,
    verified_at                  TIMESTAMPTZ,

    submitted_at                 TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_reports_location   ON reports USING GIST(location);
CREATE INDEX idx_reports_class      ON reports (ai_classification);
CREATE INDEX idx_reports_submitted  ON reports (submitted_at DESC);

-- ============================================================================================
-- TABLE 9: SOP_EVACUATION_ORDERS — HITL Administrative Governance
-- Covers: Section 8.2 (DMA 2005 §34 HITL workflow), Section 6.7 (CAP XML, LoRa barrier,
--         SCADA grid islanding, sunset gating), Section 8.1 (LGD district scoping)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS sop_evacuation_orders (
    id                           SERIAL PRIMARY KEY,
    order_uuid                   UUID DEFAULT gen_random_uuid(),
    zone_id                      INT REFERENCES risk_zones(id) ON DELETE SET NULL,
    isolation_event_id           INT REFERENCES isolation_events(id) ON DELETE SET NULL,
    lgd_district_code            TEXT NOT NULL,
    lgd_state_code               TEXT,

    -- Risk context at time of generation
    risk_pct_at_generation       FLOAT,
    confidence_pct_at_generation FLOAT,
    fos_at_generation            FLOAT,
    affected_population          INT,
    detour_route_description     TEXT,

    -- HITL DM Authorization (Section 8.2)
    -- Step 1: System generates → dm_authorized = FALSE
    -- Step 2: DM reviews 3D terrain profile on dashboard
    -- Step 3: DM enters 6-digit PIN → dm_authorized = TRUE
    dm_authorized                BOOLEAN DEFAULT FALSE,
    authorized_by                TEXT,                   -- DM name / designation
    authorized_by_email          TEXT,                   -- JWT sub email
    authorized_at                TIMESTAMPTZ,
    dm_pin_hash                  TEXT,                   -- Bcrypt hash of 6-digit PIN

    -- Documents
    order_pdf_url                TEXT,                   -- ReportLab / WeasyPrint generated PDF
    rag_source_chunks            TEXT[],                 -- pgvector chunks used by LLM

    -- CAP XML dissemination (Section 8.4)
    cap_alert_xml                TEXT,                   -- ITU-T X.1303 CAP XML payload
    cap_xsd_validated            BOOLEAN DEFAULT FALSE,  -- lxml XSD validation passed
    cap_dispatched_at            TIMESTAMPTZ,

    -- Actuation flags (Section 6.7)
    sunset_gating_triggered      BOOLEAN DEFAULT FALSE,  -- Daytime travel restriction issued
    lora_barrier_actuated        BOOLEAN DEFAULT FALSE,  -- Sub-GHz LoRa → boom barriers + VMS
    scada_grid_islanded          BOOLEAN DEFAULT FALSE,  -- Modbus-TCP 11kV/33kV breaker opened
    whatsapp_broadcast_sent      BOOLEAN DEFAULT FALSE,  -- Multi-language broadcast dispatched
    nec_interstate_notified      BOOLEAN DEFAULT FALSE,  -- NEC multi-state gateway notified
    gsi_nlfc_exported            BOOLEAN DEFAULT FALSE,  -- GSI Bhusanket LANDSLIP format exported

    generated_at                 TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_sop_zone_time      ON sop_evacuation_orders (zone_id, generated_at DESC);
CREATE INDEX idx_sop_authorized     ON sop_evacuation_orders (dm_authorized, authorized_at);
CREATE INDEX idx_sop_lgd            ON sop_evacuation_orders (lgd_district_code);

-- ============================================================================================
-- TABLE 10: AUDIT_LEDGER — Cryptographic SHA-256 State Chain
-- Covers: Section 8.5 (immutable hash chain), Section 2.10 (post-disaster judicial record)
-- Formula: H_n = SHA-256(H_{n-1} || Timestamp || PayloadType || JSON(PayloadData))
-- ============================================================================================
CREATE TABLE IF NOT EXISTS audit_ledger (
    id                           BIGSERIAL PRIMARY KEY,
    previous_hash                TEXT NOT NULL,           -- H_{n-1} SHA-256 hex digest
    block_hash                   TEXT NOT NULL UNIQUE,    -- H_n SHA-256 hex digest
    payload_type                 TEXT NOT NULL CHECK (payload_type IN (
                                     'TELEMETRY',         -- Raw sensor frame ingested
                                     'RISK_SCORE',        -- ML ensemble risk assessment
                                     'SOP_ORDER',         -- Evacuation order drafted
                                     'DM_AUTHORIZATION',  -- District Magistrate sign-off
                                     'BARRIER_ACTUATION', -- LoRa boom barrier triggered
                                     'SCADA_TRIP',        -- 11kV/33kV circuit breaker opened
                                     'CAP_DISPATCH',      -- CAP XML cell-broadcast sent
                                     'VOLUNTEER_VERIFY',  -- Aapda Mitra field verification
                                     'SYSTEM_EVENT'       -- Tier change, cold-start, drift alert
                                 )),
    payload_data                 JSONB NOT NULL,          -- Full event payload
    created_at                   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_created      ON audit_ledger (created_at DESC);
CREATE INDEX idx_audit_hash         ON audit_ledger (block_hash);
CREATE INDEX idx_audit_type         ON audit_ledger (payload_type);

-- ============================================================================================
-- TABLE 11: DISASTER_MANUAL_CHUNKS — RAG Vector Store
-- Covers: Section 5.6 (on-premise RAG pipeline), Section 6.7 (LLM SOP generation)
-- ============================================================================================
CREATE TABLE IF NOT EXISTS disaster_manual_chunks (
    id                           SERIAL PRIMARY KEY,
    state                        TEXT NOT NULL,           -- 'Meghalaya' / 'Assam' / 'Manipur' etc.
    document_title               TEXT NOT NULL,           -- e.g. 'Meghalaya SDMA Flood SOP 2022'
    document_section             TEXT,                    -- Chapter/Section identifier
    chunk_content                TEXT NOT NULL,
    chunk_index                  INT,                     -- Position within document
    embedding                    vector(384),             -- sentence-transformers/all-MiniLM-L6-v2
    created_at                   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_rag_state          ON disaster_manual_chunks (state);
CREATE INDEX idx_rag_embedding      ON disaster_manual_chunks USING ivfflat (embedding vector_cosine_ops)
                                    WITH (lists = 100);

-- ============================================================================================
-- STORED PROCEDURE: Dynamic Mapbox Vector Tile (MVT) Generator
-- Covers: Section 5.5, Section 9.3
-- Returns binary .pbf Protocol Buffer tile for the React dashboard
-- Target: < 25ms delivery latency
-- ============================================================================================
CREATE OR REPLACE FUNCTION get_risk_zone_mvt(z integer, x integer, y integer)
RETURNS bytea AS $$
DECLARE
    tile_envelope geometry;
    mvt_output    bytea;
BEGIN
    tile_envelope := ST_TileEnvelope(z, x, y);
    SELECT ST_AsMVT(q, 'risk_zones', 4096, 'mvt_geom') INTO mvt_output
    FROM (
        SELECT
            rz.id,
            rz.zone_name,
            rz.corridor_code,
            rz.lgd_district_code,
            rz.current_risk,
            rz.operational_tier,
            rz.ml_risk_pct,
            rz.ml_confidence_pct,
            rz.fos_value,
            rz.weather_source,
            rz.culvert_clogged,
            rz.sentinel2_toe_cut,
            rz.shap_drivers,
            ST_AsMVTGeom(
                ST_Transform(rz.boundary, 3857),
                tile_envelope, 4096, 64, TRUE
            ) AS mvt_geom
        FROM risk_zones rz
        WHERE rz.boundary && ST_Transform(tile_envelope, 4326)
          AND ST_Intersects(rz.boundary, ST_Transform(tile_envelope, 4326))
    ) q
    WHERE q.mvt_geom IS NOT NULL;
    RETURN COALESCE(mvt_output, ''::bytea);
END;
$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;

-- Road edges MVT (for dashboard graph overlay)
CREATE OR REPLACE FUNCTION get_road_edges_mvt(z integer, x integer, y integer)
RETURNS bytea AS $$
DECLARE
    tile_envelope geometry;
    mvt_output    bytea;
BEGIN
    tile_envelope := ST_TileEnvelope(z, x, y);
    SELECT ST_AsMVT(q, 'road_edges', 4096, 'mvt_geom') INTO mvt_output
    FROM (
        SELECT
            re.id,
            re.highway_type,
            re.chokepoint_type,
            re.structural_duration_multiplier,
            re.is_severed,
            re.is_strategic_defence,
            re.culvert_vulnerability_index,
            ST_AsMVTGeom(
                ST_Transform(re.geometry, 3857),
                tile_envelope, 4096, 64, TRUE
            ) AS mvt_geom
        FROM road_edges re
        WHERE re.geometry && ST_Transform(tile_envelope, 4326)
    ) q
    WHERE q.mvt_geom IS NOT NULL;
    RETURN COALESCE(mvt_output, ''::bytea);
END;
$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;
-- SafeSlope-NER Production Corridor Seed Script

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-06-KM-128-Sonapur', 'NH-06-MEGHALAYA', '272', '17',
            ST_GeomFromText('POLYGON((91.846 25.547, 91.854 25.547, 91.854 25.553, 91.846 25.553, 91.846 25.547))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'HIGH', 'ensemble_model',
            1, 78.4, 91.2, 1.08,
            42.0, 185.0, -22.5,
            0.68, TRUE, FALSE,
            '[{"factor": "Antecedent Precipitation Index (40d)", "weight_pct": 38.0, "value": 185.0}, {"factor": "Mohr-Coulomb Factor of Safety Deficit", "weight_pct": 34.0, "value": 1.08}, {"factor": "InSAR Continuous Creep Rate", "weight_pct": 28.0, "value": -22.5}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-06-KM-134-Umling', 'NH-06-MEGHALAYA', '272', '17',
            ST_GeomFromText('POLYGON((91.876 25.577, 91.884 25.577, 91.884 25.583, 91.876 25.583, 91.876 25.577))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'MODERATE', 'ensemble_model',
            1, 46.2, 88.5, 1.34,
            18.0, 110.0, -8.1,
            0.72, FALSE, FALSE,
            '[{"factor": "Rainfall Intensity", "weight_pct": 45.0, "value": 18.0}, {"factor": "Soil Saturation Index", "weight_pct": 35.0, "value": 0.65}, {"factor": "Topographic Slope Angle", "weight_pct": 20.0, "value": 36.0}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-06-KM-142-Ratacherra', 'NH-06-MEGHALAYA', '272', '17',
            ST_GeomFromText('POLYGON((91.916 25.617, 91.924 25.617, 91.924 25.623, 91.916 25.623, 91.916 25.617))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'CRITICAL', 'physics_floor',
            1, 94.8, 95.0, 0.82,
            68.5, 240.0, -48.2,
            0.55, TRUE, TRUE,
            '[{"factor": "Mohr-Coulomb FoS Breached (<1.0)", "weight_pct": 52.0, "value": 0.82}, {"factor": "Excess Pore-Water Pressure", "weight_pct": 30.0, "value": 38.5}, {"factor": "Anthropogenic Toe-Cut Overburden", "weight_pct": 18.0, "value": 1.0}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-54-KM-38-42-Sairang', 'NH-54-MIZORAM', '283', '15',
            ST_GeomFromText('POLYGON((92.645 23.776, 92.655 23.776, 92.655 23.784, 92.645 23.784, 92.645 23.776))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'HIGH', 'ensemble_model',
            2, 72.0, 82.0, 1.12,
            35.0, 190.0, -16.0,
            0.28, FALSE, FALSE,
            '[{"factor": "InSAR Blind Tier 2 GWaveNet Stress", "weight_pct": 40.0, "value": 0.72}, {"factor": "Soil Volumetric Water Content", "weight_pct": 35.0, "value": 74.0}, {"factor": "Acoustic Micro-Fracture AE Rate", "weight_pct": 25.0, "value": 18.0}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-54-KM-42-45-Thingdawl', 'NH-54-MIZORAM', '283', '15',
            ST_GeomFromText('POLYGON((92.675 23.816, 92.685 23.816, 92.685 23.824, 92.675 23.824, 92.675 23.816))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'LOW', 'ensemble_model',
            1, 14.5, 96.0, 1.85,
            4.0, 45.0, -2.1,
            0.78, FALSE, FALSE,
            '[{"factor": "High Factor of Safety (Stable)", "weight_pct": 70.0, "value": 1.85}, {"factor": "Low Pore Pressure", "weight_pct": 20.0, "value": 2.1}, {"factor": "Healthy Dense Root Cohesion", "weight_pct": 10.0, "value": 14.2}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(91.847, 25.547), 4326),
                '89003e5ee3c609', '8a003e5ee3c60a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(91.84819999999999, 25.5482), 4326),
                '89003e5fa3d109', '8a003e5fa3d10a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(91.84939999999999, 25.549400000000002), 4326),
                '89003e6e63dd09', '8a003e6e63dd0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(91.8506, 25.5506), 4326),
                '89003e6f23ea09', '8a003e6f23ea0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(91.8518, 25.5518), 4326),
                '89003e6fe3f609', '8a003e6fe3f60a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(91.853, 25.553), 4326),
                '89003e6ea40209', '8a003e6ea4020a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(91.877, 25.576999999999998), 4326),
                '89003e7f94f209', '8a003e7f94f20a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(91.87819999999999, 25.5782), 4326),
                '89003e7e64fd09', '8a003e7e64fd0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(91.87939999999999, 25.5794), 4326),
                '89003e7f250909', '8a003e7f25090a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(91.8806, 25.580599999999997), 4326),
                '89003e7fd51609', '8a003e7fd5160a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(91.8818, 25.581799999999998), 4326),
                '89003e7e952209', '8a003e7e95220a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(91.883, 25.583), 4326),
                '89003e7f552e09', '8a003e7f552e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(91.917, 25.617), 4326),
                '89003e8ea68209', '8a003e8ea6820a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(91.9182, 25.6182), 4326),
                '89003e8f668e09', '8a003e8f668e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(91.9194, 25.619400000000002), 4326),
                '89003e8e269a09', '8a003e8e269a0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(91.92060000000001, 25.6206), 4326),
                '89003e8ee6a609', '8a003e8ee6a60a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(91.9218, 25.6218), 4326),
                '89003e8fa6b209', '8a003e8fa6b20a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(91.923, 25.623), 4326),
                '89003e8e66be09', '8a003e8e66be0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(92.647, 23.777), 4326),
                '89003a0ea30609', '8a003a0ea3060a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(92.6482, 23.778200000000002), 4326),
                '89003a0f631209', '8a003a0f63120a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(92.6494, 23.779400000000003), 4326),
                '89003a0e231e09', '8a003a0e231e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(92.65060000000001, 23.7806), 4326),
                '89003a0ee32a09', '8a003a0ee32a0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(92.65180000000001, 23.7818), 4326),
                '89003a0fa33609', '8a003a0fa3360a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(92.653, 23.783), 4326),
                '89003a1e634209', '8a003a1e63420a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(92.677, 23.817), 4326),
                '89003a2fa43209', '8a003a2fa4320a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(92.6782, 23.8182), 4326),
                '89003a2e643e09', '8a003a2e643e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(92.6794, 23.8194), 4326),
                '89003a2f244a09', '8a003a2f244a0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(92.68060000000001, 23.8206), 4326),
                '89003a2fe45609', '8a003a2fe4560a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(92.68180000000001, 23.8218), 4326),
                '89003a2ea46209', '8a003a2ea4620a', 0.05,
                TRUE, '2026-09-13T19:36:36.765697+00:00'
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(92.683, 23.823), 4326),
                '89003a2f646e09', '8a003a2f646e0a', 0.05,
                TRUE, '2026-09-13T19:36:36.765697+00:00'
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Sonapur Village', '272001', '272', '17',
            ST_SetSRID(ST_MakePoint(91.849, 25.548), 4326),
            2001, 1450, 850,
            450, 6800.0, 1400.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(91.851, 25.5495), 4326),
            0.4
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Mawryngkneng Outpost', '272002', '272', '17',
            ST_SetSRID(ST_MakePoint(91.862, 25.556), 4326),
            2002, 2100, 1200,
            600, 9500.0, 2200.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(91.864, 25.557), 4326),
            0.3
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Umling Basti', '272003', '272', '17',
            ST_SetSRID(ST_MakePoint(91.881, 25.579), 4326),
            2003, 820, 450,
            250, 3200.0, 850.0,
            1.2, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(91.883, 25.582), 4326),
            0.5
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Ratacherra Border Hamlet', '272004', '272', '17',
            ST_SetSRID(ST_MakePoint(91.921, 25.619), 4326),
            2004, 650, 300,
            180, 1800.0, 450.0,
            1.3, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(91.923, 25.621), 4326),
            0.4
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Sairang Kawnpui', '283001', '283', '15',
            ST_SetSRID(ST_MakePoint(92.651, 23.781), 4326),
            2101, 3200, 1400,
            800, 14000.0, 3500.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(92.654, 23.783), 4326),
            0.6
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Thingdawl Veng', '283002', '283', '15',
            ST_SetSRID(ST_MakePoint(92.681, 23.821), 4326),
            2102, 1150, 550,
            300, 5200.0, 1100.0,
            1.2, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(92.683, 23.823), 4326),
            0.3
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Kolasib Junction', '283003', '283', '15',
            ST_SetSRID(ST_MakePoint(92.705, 23.845), 4326),
            2103, 4100, 1800,
            950, 18500.0, 4800.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(92.708, 23.847), 4326),
            0.5
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Bilkhawthlir Valley', '283004', '283', '15',
            ST_SetSRID(ST_MakePoint(92.735, 23.865), 4326),
            2104, 980, 420,
            260, 4100.0, 900.0,
            1.2, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(92.738, 23.867), 4326),
            0.4
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100000, 1001, 2001,
            ST_GeomFromText('LINESTRING(91.842 25.542, 91.849 25.548)', 4326),
            1, 'national_highway', 1850.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100001, 2001, 2002,
            ST_GeomFromText('LINESTRING(91.849 25.548, 91.854 25.552, 91.862 25.556)', 4326),
            1, 'national_highway', 2100.0,
            'BRIDGE', 8.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100002, 2002, 2003,
            ST_GeomFromText('LINESTRING(91.862 25.556, 91.872 25.568, 91.881 25.579)', 4326),
            2, 'national_highway', 3200.0,
            'NARROW_CUTTING', 1.8, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100003, 2003, 2004,
            ST_GeomFromText('LINESTRING(91.881 25.579, 91.902 25.601, 91.921 25.619)', 4326),
            3, 'national_highway', 4500.0,
            'CULVERT', 2.5, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100004, 2004, 1002,
            ST_GeomFromText('LINESTRING(91.921 25.619, 91.935 25.632)', 4326),
            3, 'national_highway', 2800.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100005, 2001, 3001,
            ST_GeomFromText('LINESTRING(91.849 25.548, 91.851 25.555)', 4326),
            1, 'village_road', 1200.0,
            'OPEN_ROAD', 1.0, FALSE,
            TRUE, TRUE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100006, 3001, 2002,
            ST_GeomFromText('LINESTRING(91.851 25.555, 91.862 25.556)', 4326),
            1, 'village_road', 1400.0,
            'OPEN_ROAD', 1.0, FALSE,
            TRUE, TRUE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100007, 2002, 3002,
            ST_GeomFromText('LINESTRING(91.862 25.556, 91.875 25.562, 91.89 25.572)', 4326),
            2, 'state_highway', 3800.0,
            'OPEN_ROAD', 1.0, FALSE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100008, 3002, 2003,
            ST_GeomFromText('LINESTRING(91.89 25.572, 91.881 25.579)', 4326),
            2, 'state_highway', 1900.0,
            'CULVERT', 2.5, FALSE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100009, 1101, 2101,
            ST_GeomFromText('LINESTRING(92.638 23.768, 92.651 23.781)', 4326),
            4, 'national_highway', 2400.0,
            'NARROW_CUTTING', 1.8, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100010, 2101, 2102,
            ST_GeomFromText('LINESTRING(92.651 23.781, 92.665 23.801, 92.681 23.821)', 4326),
            4, 'national_highway', 4100.0,
            'BRIDGE', 8.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100011, 2102, 2103,
            ST_GeomFromText('LINESTRING(92.681 23.821, 92.693 23.834, 92.705 23.845)', 4326),
            5, 'national_highway', 3600.0,
            'CULVERT', 2.5, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100012, 2103, 2104,
            ST_GeomFromText('LINESTRING(92.705 23.845, 92.72 23.856, 92.735 23.865)', 4326),
            5, 'national_highway', 2900.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100013, 2104, 1102,
            ST_GeomFromText('LINESTRING(92.735 23.865, 92.75 23.878)', 4326),
            5, 'national_highway', 3100.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        
-- SafeSlope-NER Disaster Manuals RAG pgvector Seed

        INSERT INTO disaster_manual_chunks (
            state, document_title, document_section, chunk_content, embedding
        ) VALUES (
            'Meghalaya', 'Meghalaya SDMA Landslide Hazard Operating Manual 2024', 'Section 12.4 — Precautionary Ridge Evacuation',
            'When predictive monitoring systems register a Factor of Safety (FoS) below 1.0 or failure probability exceeding 75%, the District Disaster Management Authority (DDMA) chaired by the Deputy Commissioner shall invoke Section 34(b) of the Disaster Management Act, 2005. Evacuation of settlements on vulnerable colluvial slopes shall strictly follow pre-identified ridgeline pedestrian tracks to avoid drainage ravines prone to debris funneling. Daytime travel gating must be enforced before 17:00 IST if overnight collapse is anticipated.', '[0.038593, 0.021557, -0.007581, -0.004718, -0.054896, 0.100322, -0.018307, -0.026203, 0.067456, -0.023905, 0.016921, 0.089532, 0.027484, -0.002366, -0.005988, -0.089491, -0.031476, -0.044931, 0.026962, -0.069864, 0.065462, -0.044206, 0.012126, -0.007918, -0.072488, -0.043175, -0.002308, -0.078552, 0.070072, -0.041066, -0.003341, 0.022627, -0.002423, 0.000417, -0.011782, -0.081238, -0.047589, -0.105180, 0.009138, 0.073720, -0.071383, 0.107641, -0.024334, 0.096438, -0.034683, -0.046897, 0.101567, -0.053287, 0.020525, 0.051818, 0.027316, -0.043052, 0.038005, -0.026968, -0.038763, 0.033476, 0.016346, 0.019733, 0.015381, -0.014476, -0.018502, -0.001197, 0.007514, 0.015447, -0.048068, -0.061708, 0.048363, 0.081028, 0.115371, -0.026291, -0.057050, 0.066599, -0.001949, 0.027316, 0.018576, 0.042407, -0.048570, -0.068489, 0.003040, 0.031314, -0.040123, 0.060191, 0.002152, -0.039497, -0.003090, 0.036394, 0.052115, -0.034802, 0.117273, 0.063662, -0.061038, -0.107790, -0.016354, -0.001748, -0.017781, 0.009719, 0.066013, -0.001485, -0.084381, 0.047246, -0.074108, -0.034543, 0.044807, -0.010519, -0.032041, 0.009582, -0.006256, -0.000887, 0.017344, -0.065410, 0.087255, 0.060939, -0.040163, 0.029894, -0.000959, -0.064383, 0.115294, 0.040388, 0.011425, -0.051192, 0.016882, 0.003456, 0.007520, 0.087623, 0.100884, 0.154021, 0.069974, -0.050605, 0.021712, -0.037322, -0.039343, -0.051560, 0.044489, -0.036532, 0.020471, -0.082926, -0.079630, -0.007937, 0.083486, 0.027646, 0.002623, 0.016276, 0.046730, -0.001492, 0.034945, -0.043496, -0.048940, 0.047822, 0.062846, -0.098356, -0.052434, 0.012905, 0.008503, 0.039572, 0.069509, -0.019024, -0.015679, -0.063105, 0.049959, 0.035152, -0.095714, 0.073440, 0.039176, 0.082139, -0.007652, 0.044259, -0.029671, -0.001872, -0.012772, 0.028806, -0.035459, 0.008848, -0.053939, 0.027044, 0.061205, -0.013860, -0.010849, 0.056910, -0.010600, -0.055439, -0.025741, 0.065882, -0.002152, -0.006697, 0.041314, -0.059966, -0.025221, -0.034875, 0.021855, 0.080255, -0.009099, 0.040246, -0.029758, 0.032821, 0.031882, 0.060663, -0.020377, 0.045836, 0.011453, 0.003191, -0.028676, -0.068603, 0.025480, -0.068766, -0.018638, 0.099081, -0.025214, -0.033761, -0.079637, 0.007041, 0.114274, -0.011732, -0.033376, -0.019378, 0.043862, 0.044336, -0.013008, 0.050253, -0.001909, 0.024833, -0.041395, -0.004263, 0.048782, 0.065949, -0.010559, 0.015038, 0.054634, -0.034527, 0.043249, 0.035646, -0.022310, 0.000751, -0.073019, -0.012672, -0.040763, -0.013217, -0.044702, -0.045501, -0.014827, -0.024879, 0.004910, 0.038332, -0.099069, -0.077166, 0.028737, -0.018672, -0.005455, -0.090574, 0.087337, -0.057272, -0.052218, 0.007921, -0.038925, -0.060947, -0.022456, 0.005373, 0.005741, 0.012198, -0.053637, -0.019842, -0.061038, 0.059103, 0.003287, -0.027087, 0.073583, -0.103279, -0.012579, 0.088547, -0.028885, -0.000128, -0.064596, -0.085439, -0.035000, 0.049288, 0.007505, -0.167882, 0.043231, 0.035486, 0.043046, 0.073942, -0.001899, -0.090743, -0.025963, 0.088830, -0.046734, -0.087360, 0.018873, -0.040006, -0.054818, -0.060504, -0.023690, 0.008735, 0.082908, -0.053245, 0.012875, -0.015998, 0.009145, -0.043734, -0.037066, -0.112703, -0.078484, 0.003375, -0.058612, -0.058023, 0.039740, 0.083932, 0.011617, -0.036096, -0.060031, -0.008556, -0.022227, -0.045060, 0.034453, 0.053333, -0.105777, -0.027976, 0.030962, 0.003550, 0.077844, -0.030364, -0.025384, 0.029162, 0.142877, -0.042654, -0.040881, 0.037116, -0.039926, 0.038952, 0.092859, 0.045086, -0.002922, -0.078977, -0.000361, 0.017146, -0.004139, -0.086410, 0.086741, 0.004974, 0.030559, 0.116821, -0.048960, -0.047861, 0.016280, 0.015166, 0.090215, -0.015387, 0.050315, 0.022168, -0.030283, -0.098637, 0.019021, -0.020748, -0.014585, -0.067556, 0.019773, -0.034813, -0.091062, -0.043770, 0.023961, -0.014840, -0.009183, 0.102124, 0.039758, 0.004456, -0.030396, -0.069431, 0.021368, -0.036527, -0.064524, 0.033503, 0.009403, -0.049985, -0.014350, -0.011227, -0.004621, -0.057079, 0.031467, 0.000246, -0.017015, -0.029804, 0.014317, 0.051913, 0.044185, -0.042912]'::vector(384)
        );
        

        INSERT INTO disaster_manual_chunks (
            state, document_title, document_section, chunk_content, embedding
        ) VALUES (
            'Meghalaya', 'Meghalaya SDMA Landslide Hazard Operating Manual 2024', 'Section 14.2 — Critical Electrical Grid Islanding',
            'In the event of an imminent mass movement breach along major highways (NH-06, SH-4), automated SCADA trip directives shall be transmitted to the MeECL (Meghalaya Energy Corporation Limited) distribution substations. Circuit breakers on 11 kV and 33 kV lines crossing the slip zone must be opened immediately to avoid fallen live conductors igniting fuel or electrocuting downstream evacuation teams and first responders.', '[-0.123988, 0.005778, 0.014555, 0.089383, 0.041903, 0.048085, 0.048420, 0.019663, -0.005442, 0.013570, -0.082254, 0.043784, -0.043446, 0.041677, -0.005592, -0.040371, 0.053461, 0.000211, -0.046949, -0.022752, -0.021110, 0.034923, 0.001841, -0.052724, 0.039553, 0.079329, -0.031558, -0.018959, -0.058922, -0.056602, -0.006708, -0.030521, -0.063560, 0.051270, 0.076689, 0.015374, -0.067001, -0.062099, 0.043236, -0.020455, -0.014349, -0.021899, -0.090807, -0.061290, 0.040287, 0.015062, 0.057073, 0.118512, 0.002331, 0.056836, 0.057389, 0.082464, 0.078233, -0.056314, 0.047947, 0.049655, -0.006080, -0.038440, -0.000494, -0.032602, 0.001695, 0.018838, 0.022323, -0.010312, 0.052107, -0.081733, -0.054457, 0.003925, -0.009738, -0.015993, 0.066206, 0.017828, -0.047099, 0.080695, -0.012297, -0.082303, 0.095623, 0.021282, 0.017886, 0.027676, -0.034277, 0.022048, 0.002447, 0.091847, 0.087252, -0.014038, 0.021988, -0.066828, 0.033240, 0.004526, -0.000696, 0.030166, -0.018477, 0.008386, -0.020876, 0.043365, 0.065203, 0.010412, 0.006017, -0.024628, 0.092250, -0.087932, 0.067604, 0.025550, 0.049422, -0.030478, -0.042076, 0.073919, 0.115523, -0.011808, 0.034496, 0.007648, -0.024191, 0.122201, 0.051990, 0.096224, -0.003742, -0.009744, -0.015934, 0.070615, -0.085069, 0.022542, -0.024669, 0.002297, -0.003559, 0.040339, -0.080137, 0.040118, -0.039925, 0.001920, 0.041913, 0.011831, -0.088718, 0.134050, 0.039289, 0.052685, 0.033729, -0.021235, -0.039658, 0.001544, 0.070874, -0.068174, 0.024096, -0.047118, -0.030586, -0.026828, -0.034145, -0.054770, 0.045062, 0.007054, -0.064551, 0.012228, -0.004998, 0.111512, -0.056079, -0.001673, 0.061764, 0.016130, -0.010383, 0.055150, 0.008479, 0.001392, -0.060449, -0.104079, 0.021029, -0.051658, -0.045361, 0.081200, 0.025368, -0.027113, 0.021847, -0.083982, 0.004521, -0.015915, 0.027107, -0.011099, 0.007251, 0.014698, 0.069169, -0.065070, -0.076311, -0.056909, -0.055129, -0.004301, 0.031139, -0.003534, -0.046123, 0.072621, 0.081797, -0.067506, 0.019647, -0.061463, 0.000161, 0.022154, -0.036858, 0.089549, -0.017967, 0.019802, -0.004781, 0.003115, 0.010079, -0.017794, -0.059619, -0.085818, -0.011947, 0.038169, -0.086271, -0.031467, 0.051133, 0.008648, 0.054051, -0.040718, -0.066889, -0.046138, 0.007205, -0.015812, 0.023851, 0.014762, 0.017276, -0.039091, 0.018967, 0.058215, 0.006044, -0.051201, 0.013830, -0.133460, 0.044214, 0.011729, -0.089446, 0.011208, -0.021413, 0.026791, -0.010256, 0.105969, 0.071101, 0.033418, -0.062972, 0.034988, 0.046818, 0.051445, -0.007365, -0.069585, -0.024676, -0.014325, -0.013064, 0.024523, -0.008350, -0.003718, -0.014819, -0.003339, -0.032890, 0.061311, -0.033198, -0.015571, -0.036667, -0.018640, -0.107438, -0.039397, 0.075155, -0.040960, 0.092036, 0.097684, -0.046275, -0.029814, 0.017229, 0.034717, -0.054229, -0.045400, -0.029864, -0.001026, 0.042973, -0.031543, -0.045484, -0.034998, 0.063211, 0.018079, 0.055564, 0.006732, 0.070255, 0.102468, -0.002731, 0.010933, -0.033390, -0.006619, 0.087630, -0.000252, 0.132990, 0.052014, -0.012799, 0.050244, 0.051981, -0.000353, -0.037947, -0.025613, -0.088441, 0.129479, 0.058047, 0.031702, -0.072761, -0.060419, -0.065141, 0.025270, 0.008859, -0.003032, -0.016082, -0.014192, -0.045576, 0.080008, 0.015028, -0.002278, -0.020048, 0.064937, 0.071240, 0.092697, -0.061216, -0.032982, -0.004784, -0.124703, 0.053661, 0.074073, 0.083586, 0.003077, -0.003554, 0.047471, 0.084351, 0.030099, -0.086614, 0.063833, 0.042499, -0.005580, 0.032357, -0.042074, -0.028855, -0.023456, -0.055949, -0.082894, -0.063629, 0.048534, 0.021404, -0.019288, 0.030586, -0.068966, -0.036966, 0.040648, 0.007166, 0.068701, 0.072020, 0.055178, 0.007580, 0.008151, -0.006824, -0.002472, -0.091499, 0.011338, 0.026159, 0.011366, -0.022353, -0.067350, -0.045848, -0.028919, 0.020526, -0.063323, 0.102556, 0.019437, 0.007098, -0.068392, 0.016246, -0.015552, -0.052000, 0.023029, 0.009605, -0.072624, -0.055871, 0.009017, 0.021811, 0.074659, -0.004989, 0.085893, 0.006219, 0.014927, 0.023897, 0.095503, 0.063020, 0.103418]'::vector(384)
        );
        

        INSERT INTO disaster_manual_chunks (
            state, document_title, document_section, chunk_content, embedding
        ) VALUES (
            'Assam', 'Assam State Disaster Management Authority (ASDMA) Inter-State Corridor SOP', 'Section 8.1 — Essential Supply Depletion & Airdrop Protocol',
            'When landslide debris severs an arterial National Highway isolating more than two revenue villages, the Block Development Officer shall assess Public Distribution System (PDS) warehouse grain and kerosene reserves. If clearance operations are projected to exceed available buffer stocks (PDS depletion horizon T_depletion < 48 hours), the State EOC shall immediately requisition Indian Air Force helicopter airdrops from Borjhar / Kumbhirgram Air Force Stations.', '[0.025152, -0.117226, 0.107258, -0.010920, -0.095599, 0.022920, 0.003986, -0.072040, -0.027047, 0.079734, -0.020530, 0.012305, -0.097270, 0.039320, 0.063667, 0.005862, -0.022501, -0.007431, -0.005317, -0.012505, -0.152449, 0.021498, -0.072167, -0.021674, 0.012295, 0.040671, 0.105577, -0.053775, -0.046918, 0.118270, -0.069427, 0.013120, -0.103270, 0.056735, 0.036135, 0.069721, 0.098129, 0.081720, 0.032435, 0.071890, 0.030660, -0.051010, 0.034050, 0.006801, -0.054656, 0.017615, -0.012515, 0.015487, 0.103866, -0.023424, -0.082586, -0.067862, -0.030665, 0.033181, 0.076938, -0.014891, -0.014554, -0.018260, 0.008334, 0.015562, -0.042580, -0.101470, -0.057618, 0.098392, 0.031870, 0.046895, 0.039880, -0.043482, 0.008872, 0.092092, -0.051509, -0.005795, -0.047899, 0.008536, 0.029713, -0.039467, -0.007700, -0.013169, -0.078267, 0.019032, 0.051754, -0.024386, 0.021037, 0.015611, -0.008084, 0.013262, 0.085872, 0.057353, -0.031986, -0.079395, 0.012643, 0.058306, -0.162915, -0.121086, -0.027674, -0.031277, 0.034624, -0.038357, -0.039925, -0.080122, -0.045714, -0.048984, -0.037543, -0.069668, -0.005404, -0.000258, 0.024582, -0.024663, 0.036145, 0.009484, -0.040031, -0.090383, -0.035285, -0.104137, 0.028214, -0.084373, 0.009183, -0.005510, 0.028017, -0.016151, 0.068392, -0.012660, 0.018999, -0.035961, 0.020052, 0.000955, -0.148646, 0.091385, -0.070546, -0.028522, 0.029726, 0.024288, -0.015370, 0.062365, -0.031439, -0.012889, 0.009745, -0.070171, -0.024366, -0.022380, -0.066473, 0.044181, 0.008475, -0.085103, -0.072769, 0.001943, 0.144259, -0.005192, -0.067597, -0.006689, -0.026005, 0.060429, 0.005818, 0.103486, 0.000129, -0.011368, 0.013819, -0.026448, 0.004473, 0.050068, 0.004650, 0.031685, -0.017235, -0.081407, -0.013984, 0.017784, -0.072213, -0.072317, -0.063969, -0.002522, -0.017165, -0.100300, 0.044656, -0.057532, 0.069328, -0.000493, -0.034486, -0.074891, 0.034614, -0.013771, 0.018847, -0.056044, 0.102327, -0.028159, 0.039175, 0.028618, -0.004115, -0.034394, -0.088073, 0.007180, -0.014667, -0.109791, -0.020518, 0.024087, 0.015968, -0.019259, 0.083354, -0.024798, 0.007344, 0.029302, 0.008067, 0.010822, -0.015341, -0.006708, -0.038790, 0.090805, 0.026682, -0.005797, 0.011959, -0.088822, 0.024623, -0.040348, -0.003732, -0.051459, -0.077744, 0.014133, 0.020975, 0.080785, 0.006923, -0.005751, 0.068303, -0.001023, -0.007660, 0.080550, -0.050851, 0.056310, 0.013001, 0.032394, -0.002907, -0.031015, 0.003469, -0.082748, 0.013094, 0.058563, -0.049814, -0.031348, -0.010413, 0.057670, -0.058962, 0.005982, 0.081629, 0.067608, -0.012106, -0.008125, -0.018479, 0.080431, -0.042989, 0.010506, 0.011749, -0.007439, -0.044546, -0.028028, -0.003070, 0.047267, -0.005085, -0.066882, -0.039473, -0.032745, 0.028540, -0.012988, -0.023968, -0.033775, 0.007502, -0.029680, -0.034075, -0.031835, 0.059037, 0.021220, -0.039076, 0.065623, -0.057214, -0.107895, -0.026693, 0.016018, 0.008444, 0.032400, 0.015364, -0.057786, -0.051444, 0.054884, -0.050879, -0.104947, 0.054804, 0.001112, 0.039730, -0.056204, 0.017711, 0.015191, 0.011595, -0.041530, 0.037245, -0.001018, -0.006243, -0.054692, 0.033927, 0.023374, 0.019997, -0.050622, -0.014746, 0.048836, -0.026430, 0.012711, -0.094764, -0.000459, 0.018064, 0.058266, 0.067558, 0.092405, 0.023370, 0.025159, 0.006363, -0.011411, 0.005237, -0.030951, -0.024550, 0.111597, 0.006326, 0.064359, 0.004133, -0.053551, 0.066221, -0.001168, 0.011210, -0.021082, 0.056824, 0.021077, -0.096792, -0.009051, -0.010036, -0.039369, -0.022988, 0.052564, -0.017222, 0.002653, -0.015679, -0.042659, 0.022144, 0.008776, 0.057975, -0.034832, 0.002633, 0.012313, 0.043471, 0.019414, -0.125257, 0.072563, 0.002045, 0.002474, 0.037137, 0.055659, 0.062416, -0.089859, -0.002658, 0.034373, 0.038893, 0.039188, -0.101512, 0.098470, -0.024380, 0.001867, 0.046439, 0.057575, 0.069606, -0.074043, 0.059961, 0.019038, -0.001917, -0.038189, -0.020301, 0.041573, -0.024912, -0.038350, -0.070621, -0.096098, -0.023613, 0.080952, -0.034445, 0.004704, -0.080958, 0.014594, -0.005728, 0.047017, 0.006649, 0.022955]'::vector(384)
        );
        

        INSERT INTO disaster_manual_chunks (
            state, document_title, document_section, chunk_content, embedding
        ) VALUES (
            'Manipur', 'Manipur SDMA Post-Noney Landslide Special Directive', 'Section 4.3 — Landslide-Dammed Lake Outburst Flood (LDOF) Alert',
            'Debris flows obstructing natural river courses (e.g., Ijai River, Barak tributaries) require immediate hydraulic hazard modeling. If a temporary landslide dam exceeds 15 meters in height, upstream backwater impoundment and piping failure timelines shall be modeled. Evacuation warnings shall be issued to all downstream settlements within a 15 km channel reach with minimum 4-hour lead time prior to anticipated dam breach.', '[0.013993, -0.059146, -0.018373, -0.024721, -0.038243, 0.034333, 0.005486, 0.041940, -0.067797, -0.034556, 0.073300, 0.029511, -0.002785, -0.021724, -0.048048, -0.067829, -0.020400, 0.045583, -0.001734, 0.026098, 0.024061, -0.061941, 0.031332, 0.029557, -0.003068, 0.009432, -0.060610, 0.073885, 0.046408, -0.032253, 0.054141, -0.019252, 0.040397, -0.003631, -0.010014, -0.035051, -0.049115, 0.003013, 0.056250, -0.074173, -0.021187, 0.005149, 0.067985, -0.056638, 0.086747, 0.044369, 0.021158, 0.085280, 0.017576, -0.031826, -0.078231, -0.124671, -0.116005, 0.068501, 0.025610, 0.043847, -0.085767, 0.058605, 0.013113, -0.058756, -0.032776, -0.039509, -0.013423, 0.054305, 0.051261, 0.029702, 0.008908, -0.117071, 0.069708, 0.096490, 0.008877, -0.013956, 0.029509, -0.000421, -0.102014, -0.014920, -0.128894, -0.001523, -0.123287, -0.074297, 0.032146, 0.023402, -0.160369, -0.052617, -0.078646, 0.006508, 0.028696, -0.010780, 0.036889, -0.024354, 0.046520, 0.031114, 0.013585, -0.011072, 0.026139, -0.099728, -0.060027, -0.029788, 0.026514, -0.073949, 0.073846, 0.001027, -0.054389, 0.016616, -0.097079, -0.020740, -0.036289, 0.018579, -0.033184, -0.026478, -0.023388, -0.011359, -0.019794, -0.068387, 0.028182, 0.012721, -0.042801, -0.056437, 0.077027, 0.049966, 0.006723, -0.108011, 0.001164, 0.039101, 0.100479, 0.059483, 0.020528, -0.100143, 0.002922, -0.059506, 0.027767, -0.030712, -0.062399, -0.158587, -0.024762, 0.007067, -0.007859, -0.080927, 0.015500, -0.079893, -0.025684, 0.006218, -0.049326, -0.028171, 0.045044, -0.003704, -0.038443, -0.002440, 0.021193, -0.093750, 0.062043, 0.057814, -0.038375, -0.021452, -0.009994, 0.028597, 0.034382, 0.110420, -0.018717, 0.073263, 0.007371, 0.041393, 0.014060, -0.050779, 0.081274, 0.094048, 0.039472, -0.090711, 0.018320, -0.001495, -0.055319, 0.023279, -0.057711, 0.019393, 0.060404, -0.148602, -0.040428, 0.015420, -0.020158, 0.062827, -0.019677, -0.013832, 0.092736, 0.056501, 0.032342, 0.014920, -0.161817, 0.116056, 0.056266, -0.063463, 0.007395, 0.021139, -0.003167, -0.020696, -0.017206, -0.013516, -0.007392, 0.047601, -0.028567, 0.039102, -0.108757, -0.026728, -0.006479, 0.098563, 0.006687, 0.060140, 0.017694, 0.005944, 0.033494, -0.007913, -0.039422, 0.019212, 0.052451, -0.017639, 0.054181, -0.021420, -0.032075, 0.006121, 0.065446, 0.093422, 0.034092, 0.023632, -0.027578, -0.002902, 0.039209, 0.008100, 0.019147, 0.064552, -0.020699, 0.027111, 0.011185, 0.013742, -0.026601, -0.066280, 0.022714, -0.019977, 0.069550, -0.005938, -0.006721, -0.061772, -0.057632, -0.099872, -0.005839, -0.007386, 0.057970, 0.040679, -0.006174, 0.013445, 0.009310, 0.002597, -0.000345, -0.003198, 0.032594, 0.000972, 0.039265, -0.044124, -0.019782, 0.034826, -0.003416, 0.048439, -0.087291, -0.010903, 0.027780, 0.031605, 0.088368, 0.001925, -0.001128, -0.065557, -0.025851, -0.004467, -0.011113, -0.058509, 0.013763, 0.027123, 0.033462, -0.052138, 0.030180, 0.054697, -0.001933, 0.035290, -0.002660, -0.015659, -0.040228, 0.042669, -0.085105, -0.031309, 0.063865, -0.110548, 0.052259, -0.033298, -0.021536, 0.032562, -0.057412, 0.028663, -0.052903, 0.027133, -0.001542, 0.035413, 0.011481, 0.021853, -0.041948, -0.067299, 0.007864, 0.011407, -0.027732, 0.058107, 0.029304, -0.114056, -0.016228, -0.059969, 0.040834, 0.006159, -0.001173, 0.021822, -0.011186, 0.052991, 0.049601, -0.016998, 0.083721, -0.001644, 0.052503, -0.042429, 0.078648, 0.008060, -0.020484, -0.013979, -0.013242, 0.028659, -0.011348, -0.037327, -0.030669, -0.057572, -0.064076, 0.020002, -0.044598, -0.053902, 0.066558, -0.061418, -0.093214, 0.028910, 0.028413, -0.030521, -0.051366, -0.030856, 0.011509, -0.047755, -0.051895, 0.089628, 0.019665, -0.015732, 0.120294, -0.050956, 0.030577, 0.011904, -0.162122, 0.012167, -0.048456, -0.056662, -0.001420, 0.042400, -0.035266, 0.062414, -0.049981, 0.010691, 0.045756, 0.033286, -0.009604, 0.008385, 0.074119, -0.004675, -0.039271, -0.063095, -0.021718, 0.041840, -0.009054, -0.029310, 0.037289, 0.108020, -0.007061, 0.018484, 0.052980, -0.041217, -0.040753, -0.058870]'::vector(384)
        );
        

        INSERT INTO disaster_manual_chunks (
            state, document_title, document_section, chunk_content, embedding
        ) VALUES (
            'National', 'NDMA National Guidelines on Management of Landslides and Snow Avalanches', 'Section 6.5 — Common Alerting Protocol Dissemination',
            'All hyper-local landslide early warning platforms shall format public alert messages according to the ITU-T X.1303 Common Alerting Protocol (CAP-v1.2). Broadcast sirens and cell-broadcast texts must be disseminated in the primary official languages of the affected sub-district (English, Hindi, and tribal vernaculars including Khasi, Garo, and Mizo).', '[0.001942, 0.007511, 0.005445, -0.074357, -0.032110, 0.075164, 0.027277, 0.018676, 0.059785, -0.020043, 0.041190, -0.030321, 0.014784, 0.003773, -0.114859, -0.028698, -0.115225, 0.108176, -0.022125, -0.061563, -0.020989, 0.056741, -0.033817, 0.027443, 0.022518, 0.004971, -0.003882, -0.089117, 0.050297, -0.080232, 0.020152, 0.031501, -0.008963, 0.022957, -0.038505, -0.027856, -0.045522, 0.086926, 0.089158, -0.019279, 0.052438, -0.030430, 0.082836, -0.037452, -0.008906, -0.001225, 0.031233, 0.043858, 0.017157, -0.045913, 0.020894, 0.098847, 0.001489, -0.078283, 0.059586, 0.018114, 0.039835, 0.009754, -0.044049, 0.028753, 0.024205, -0.050672, 0.011683, 0.045097, 0.008583, -0.067756, -0.014986, -0.085958, -0.038499, 0.034053, -0.019044, 0.021547, -0.034523, -0.008270, -0.022948, -0.059224, 0.027206, 0.083793, 0.083863, 0.014712, -0.036700, 0.068852, -0.049164, -0.019599, -0.034819, 0.058756, 0.018449, -0.080127, 0.011014, -0.020504, 0.058898, -0.113046, -0.031908, -0.043919, -0.001907, -0.028082, 0.081033, -0.018276, -0.053588, 0.022881, -0.005491, -0.013274, -0.037225, -0.025025, -0.007803, 0.101469, 0.000124, 0.014844, 0.026882, 0.109256, -0.092435, -0.016352, 0.017162, 0.035774, 0.043433, 0.064149, -0.025443, -0.036905, -0.056443, 0.015193, 0.006588, -0.094219, 0.008916, -0.079365, -0.017077, 0.000988, 0.013691, -0.032166, -0.050256, -0.036873, -0.006171, -0.031051, -0.050302, -0.000057, -0.050756, 0.019229, -0.003205, 0.044103, -0.153237, -0.034642, 0.065678, -0.006740, 0.082649, 0.068130, -0.004626, 0.037262, 0.049247, 0.087834, -0.013573, 0.035906, 0.022277, 0.017305, -0.010987, 0.013102, -0.023279, -0.114919, 0.021530, 0.051054, 0.017299, -0.016619, 0.077268, 0.042633, 0.006127, -0.039006, -0.146691, -0.020623, 0.001344, -0.009905, 0.007148, 0.057769, 0.023999, 0.051817, -0.028671, 0.057424, -0.061730, 0.022358, 0.055616, 0.060517, 0.033055, -0.003068, -0.037656, -0.023802, 0.039864, 0.098647, 0.016201, 0.016416, -0.006814, 0.032332, 0.039944, -0.041769, -0.038810, 0.039795, -0.032109, -0.032941, -0.000319, 0.042617, -0.018790, 0.001961, 0.040968, 0.047822, 0.108637, 0.029168, -0.064856, 0.006299, 0.030423, -0.018689, 0.004211, -0.065920, 0.026361, 0.018623, 0.014186, -0.023010, 0.006788, -0.003184, -0.036977, -0.061566, 0.008839, 0.037448, 0.093325, 0.013578, -0.002482, 0.043516, -0.011278, 0.009369, -0.071427, 0.042930, 0.023872, -0.009385, -0.078329, -0.019313, -0.068988, -0.050755, 0.048914, -0.076738, -0.016160, 0.083375, -0.040046, 0.050467, 0.060675, 0.057945, -0.018299, -0.035779, 0.033974, -0.073726, -0.145097, 0.055806, 0.093729, -0.064555, -0.033932, 0.047209, -0.044905, -0.043224, 0.101200, 0.085095, -0.064993, -0.035867, -0.006847, -0.041000, -0.076063, 0.082860, 0.069279, -0.078008, 0.038441, -0.020069, 0.076770, -0.090400, 0.010642, -0.119425, 0.026225, -0.032142, -0.099754, 0.027799, 0.057811, -0.071456, -0.080535, 0.054437, -0.032516, -0.036912, 0.000516, -0.035300, 0.075378, -0.024509, -0.028659, 0.133143, 0.059207, 0.013984, 0.061209, -0.017513, 0.035590, -0.057957, 0.051835, 0.060951, -0.046045, 0.055065, -0.010049, -0.052265, 0.006878, -0.017690, -0.045051, 0.093122, 0.071116, 0.049295, -0.003480, -0.016264, 0.097346, 0.017878, 0.054852, -0.044819, -0.024711, -0.071727, -0.092956, 0.019959, -0.015538, -0.063384, 0.001642, -0.020779, -0.031489, 0.030528, -0.089205, -0.018921, -0.074843, -0.001170, 0.057128, 0.147029, -0.050014, 0.031092, 0.026190, 0.056600, -0.007374, -0.021527, -0.036056, -0.027473, -0.023245, -0.060180, -0.089402, -0.027782, -0.011564, 0.007300, -0.039348, -0.064610, -0.033838, -0.017453, -0.046600, 0.089827, 0.060659, 0.016112, 0.045018, -0.018054, 0.037840, -0.032272, 0.064077, 0.051300, -0.015456, -0.017635, 0.038259, 0.006536, -0.045224, -0.019222, -0.079944, 0.032606, 0.017737, 0.010006, 0.064437, -0.057644, -0.025136, 0.047081, 0.050370, -0.023239, 0.007350, -0.021866, -0.092452, -0.111007, -0.010021, -0.014795, -0.007945, 0.047349, 0.018079, -0.054812, 0.098209, -0.035276, -0.055169, 0.000795, 0.021247, 0.014550]'::vector(384)
        );
        
