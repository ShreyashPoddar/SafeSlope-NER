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
    location GEOMETRY(Point, 4326),
    classification TEXT,
    confidence_pct FLOAT,
    image_url TEXT,
    verified BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP DEFAULT now()
);

-- seed data so /risk-state returns something real on first run
INSERT INTO risk_zones (zone_name, current_risk, ml_risk_pct, ml_confidence_pct)
VALUES ('zone_1', 'LOW', 12, 60), ('zone_2', 'MODERATE', 55, 68);
