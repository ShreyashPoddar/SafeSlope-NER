CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    sensor_id TEXT UNIQUE NOT NULL,
    location GEOMETRY(Point, 4326)
);

CREATE TABLE telemetry_readings (
    id SERIAL PRIMARY KEY,
    sensor_id TEXT REFERENCES sensors(sensor_id),
    tilt_delta FLOAT,
    soil_moisture FLOAT,
    risk_state TEXT,
    trigger_cause TEXT,
    pitch_deg FLOAT,
    roll_deg FLOAT,
    pore_pressure_kpa FLOAT,
    packet_sequence_id INT,
    mpu_ok BOOLEAN,
    recorded_at TIMESTAMP DEFAULT now()
);

CREATE TABLE risk_zones (
    id SERIAL PRIMARY KEY,
    zone_name TEXT UNIQUE,
    boundary GEOMETRY(Polygon, 4326),
    current_risk TEXT DEFAULT 'LOW',
    risk_source TEXT,
    ml_risk_pct FLOAT DEFAULT 0,
    ml_confidence_pct FLOAT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE villages (
    id SERIAL PRIMARY KEY,
    village_name TEXT,
    location GEOMETRY(Point, 4326),
    population INT
);

CREATE TABLE isolation_events (
    id SERIAL PRIMARY KEY,
    zone_id INT REFERENCES risk_zones(id),
    village_id INT REFERENCES villages(id),
    detected_at TIMESTAMP DEFAULT now()
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    tracking_id TEXT,
    sender_phone TEXT,
    hazard_type TEXT,
    location GEOMETRY(Point, 4326),
    classification TEXT,
    confidence_pct FLOAT,
    image_url TEXT,
    review_status TEXT DEFAULT 'PENDING_REVIEW',
    verified BOOLEAN DEFAULT FALSE,
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    deoc_notes TEXT,
    submitted_at TIMESTAMP DEFAULT now()
);

-- People who've signed in with Google — DDMA officials using the dashboard
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_sub TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'viewer',  -- 'viewer' or 'admin'
    created_at TIMESTAMP DEFAULT now()
);

-- seed data so /risk-state returns something real on first run
INSERT INTO risk_zones (zone_name, current_risk, ml_risk_pct, ml_confidence_pct)
VALUES ('zone_1', 'LOW', 12, 60), ('zone_2', 'MODERATE', 55, 68);
