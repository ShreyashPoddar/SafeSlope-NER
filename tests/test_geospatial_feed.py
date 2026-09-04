import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.comms.queue_service import queue_service

client = TestClient(app)


def test_geospatial_geojson_endpoint_rfc7946():
    """Verify GET /api/comms/geospatial/geojson conforms to RFC 7946 GeoJSON specification."""
    resp = client.get("/api/comms/geospatial/geojson")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/geo+json")

    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert "metadata" in data
    assert isinstance(data["features"], list)
    assert data["metadata"]["total_features"] == len(data["features"])

    if len(data["features"]) > 0:
        feat = data["features"][0]
        assert feat["type"] == "Feature"
        assert "geometry" in feat
        assert feat["geometry"]["type"] == "Point"
        # GeoJSON coordinates MUST be [longitude, latitude]
        coords = feat["geometry"]["coordinates"]
        assert len(coords) == 2
        lng, lat = coords[0], coords[1]
        assert isinstance(lng, (int, float))
        assert isinstance(lat, (int, float))
        assert -180 <= lng <= 180
        assert -90 <= lat <= 90

        # Check required properties
        props = feat["properties"]
        assert "tracking_id" in props
        assert "classification" in props
        assert "severity" in props
        assert "confidence_pct" in props
        assert "review_status" in props
        assert "google_maps_url" in props
        assert "osm_url" in props


def test_geospatial_geojson_filtering():
    """Verify status, channel, and severity query filters on the GeoJSON feed."""
    # Filter by status
    resp_pending = client.get("/api/comms/geospatial/geojson?status=PENDING_REVIEW")
    assert resp_pending.status_code == 200
    for f in resp_pending.json()["features"]:
        assert f["properties"]["review_status"] == "PENDING_REVIEW"

    # Filter by channel
    resp_tg = client.get("/api/comms/geospatial/geojson?channel=Telegram%20Bot")
    assert resp_tg.status_code == 200
    for f in resp_tg.json()["features"]:
        assert f["properties"]["channel"].lower() == "telegram bot"


def test_geospatial_corridor_zones():
    """Verify GET /api/comms/geospatial/zones returns valid mountain corridor geometries."""
    resp = client.get("/api/comms/geospatial/zones")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/geo+json")

    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 2

    # Check NH-54 corridor line
    nh54 = next((f for f in data["features"] if f["id"] == "CORRIDOR-NH54"), None)
    assert nh54 is not None
    assert nh54["geometry"]["type"] == "LineString"
    assert len(nh54["geometry"]["coordinates"]) >= 3


def test_geospatial_summary_feed():
    """Verify GET /api/comms/geospatial/feed provides quick telemetry summary."""
    resp = client.get("/api/comms/geospatial/feed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert "live_features_count" in data
    assert "stats" in data
    assert data["geojson_endpoint"] == "/api/comms/geospatial/geojson"
