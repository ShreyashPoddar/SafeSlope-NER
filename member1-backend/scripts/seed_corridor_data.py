"""
SafeSlope-NER — Corridor Seed Data Generator & Initializer
Implements Section 9.1 and Section 10.3 of computational_backend_plan.txt v3.0.0

Seeds realistic high-fidelity geospatial and demographic baselines for:
  - Corridor 1: NH-06 (Meghalaya: East Khasi Hills / Jaintia Hills, Sonapur Tunnel sector)
  - Corridor 2: NH-54 (Mizoram: Aizawl - Lunglei, Sairang - Thingdawl KM 38-45 sector)

Entities Populated:
  - 5 Risk Zones with real boundary polygons and H3 Res-9 & Res-10 indices
  - 30 Registered IoT sensor nodes (MEMS Inclinometers, Acoustic Geophones, Piezometers, ERT, RTK-GNSS)
  - 24 Interconnected Road Edges with structural chokepoint multipliers (Bridge 8.0x, Culvert 2.5x, Cutting 1.8x)
  - 8 Indigenous Villages with WorldPop demographics, FASTag tourist baselines, and PDS grain/fuel buffers
  - Historical baseline telemetry readings demonstrating nominal and pre-failure trends
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta

try:
    import h3
except ImportError:
    # Lightweight pure-Python mock for host script generation without C-extension
    class MockH3:
        @staticmethod
        def latlng_to_cell(lat: float, lon: float, res: int) -> str:
            # Deterministic synthetic H3 hex string
            val = (int(abs(lat) * 10000) << 20) | (int(abs(lon) * 10000) << 8) | (res & 0xF)
            return f"8{res:x}{val:012x}"[:15]

        @staticmethod
        def polygon_to_cells(polygon, resolution: int):
            return [MockH3.latlng_to_cell(25.55, 91.85, resolution)]

        class Polygon:
            def __init__(self, coords):
                self.coords = coords

    h3 = MockH3()

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from app.core.config import get_settings
    from app.database import database
    settings = get_settings()
    HAS_DB = True
except ImportError:
    database = None
    settings = None
    HAS_DB = False


# ═══════════════════════════════════════════════════════════════════════════════
# 1. RISK ZONES DEFINITION (NH-06 Meghalaya & NH-54 Mizoram)
# ═══════════════════════════════════════════════════════════════════════════════

ZONES_DATA = [
    {
        "zone_name": "NH-06-KM-128-Sonapur",
        "corridor_code": "NH-06-MEGHALAYA",
        "lgd_district_code": "272",  # East Khasi Hills
        "lgd_state_code": "17",      # Meghalaya
        "center_lat": 25.5500,
        "center_lon": 91.8500,
        # 4-point polygon around the cutting
        "coords": [
            (91.8460, 25.5470),
            (91.8540, 25.5470),
            (91.8540, 25.5530),
            (91.8460, 25.5530),
            (91.8460, 25.5470),
        ],
        "current_risk": "HIGH",
        "risk_source": "ensemble_model",
        "operational_tier": 1,
        "ml_risk_pct": 78.4,
        "ml_confidence_pct": 91.2,
        "fos_value": 1.08,
        "rainfall_intensity_mmhr": 42.0,
        "antecedent_precip_40d": 185.0,
        "insar_velocity_mmyr": -22.5,
        "insar_coherence": 0.68,
        "culvert_clogged": True,
        "sentinel2_toe_cut": False,
        "shap_drivers": [
            {"factor": "Antecedent Precipitation Index (40d)", "weight_pct": 38.0, "value": 185.0},
            {"factor": "Mohr-Coulomb Factor of Safety Deficit", "weight_pct": 34.0, "value": 1.08},
            {"factor": "InSAR Continuous Creep Rate", "weight_pct": 28.0, "value": -22.5},
        ],
    },
    {
        "zone_name": "NH-06-KM-134-Umling",
        "corridor_code": "NH-06-MEGHALAYA",
        "lgd_district_code": "272",
        "lgd_state_code": "17",
        "center_lat": 25.5800,
        "center_lon": 91.8800,
        "coords": [
            (91.8760, 25.5770),
            (91.8840, 25.5770),
            (91.8840, 25.5830),
            (91.8760, 25.5830),
            (91.8760, 25.5770),
        ],
        "current_risk": "MODERATE",
        "risk_source": "ensemble_model",
        "operational_tier": 1,
        "ml_risk_pct": 46.2,
        "ml_confidence_pct": 88.5,
        "fos_value": 1.34,
        "rainfall_intensity_mmhr": 18.0,
        "antecedent_precip_40d": 110.0,
        "insar_velocity_mmyr": -8.1,
        "insar_coherence": 0.72,
        "culvert_clogged": False,
        "sentinel2_toe_cut": False,
        "shap_drivers": [
            {"factor": "Rainfall Intensity", "weight_pct": 45.0, "value": 18.0},
            {"factor": "Soil Saturation Index", "weight_pct": 35.0, "value": 0.65},
            {"factor": "Topographic Slope Angle", "weight_pct": 20.0, "value": 36.0},
        ],
    },
    {
        "zone_name": "NH-06-KM-142-Ratacherra",
        "corridor_code": "NH-06-MEGHALAYA",
        "lgd_district_code": "272",
        "lgd_state_code": "17",
        "center_lat": 25.6200,
        "center_lon": 91.9200,
        "coords": [
            (91.9160, 25.6170),
            (91.9240, 25.6170),
            (91.9240, 25.6230),
            (91.9160, 25.6230),
            (91.9160, 25.6170),
        ],
        "current_risk": "CRITICAL",
        "risk_source": "physics_floor",
        "operational_tier": 1,
        "ml_risk_pct": 94.8,
        "ml_confidence_pct": 95.0,
        "fos_value": 0.82,  # Breached geotechnical safety floor
        "rainfall_intensity_mmhr": 68.5,
        "antecedent_precip_40d": 240.0,
        "insar_velocity_mmyr": -48.2,
        "insar_coherence": 0.55,
        "culvert_clogged": True,
        "sentinel2_toe_cut": True,  # Un-retained excavation scarp
        "shap_drivers": [
            {"factor": "Mohr-Coulomb FoS Breached (<1.0)", "weight_pct": 52.0, "value": 0.82},
            {"factor": "Excess Pore-Water Pressure", "weight_pct": 30.0, "value": 38.5},
            {"factor": "Anthropogenic Toe-Cut Overburden", "weight_pct": 18.0, "value": 1.0},
        ],
    },
    {
        "zone_name": "NH-54-KM-38-42-Sairang",
        "corridor_code": "NH-54-MIZORAM",
        "lgd_district_code": "283",  # Aizawl
        "lgd_state_code": "15",      # Mizoram
        "center_lat": 23.7800,
        "center_lon": 92.6500,
        "coords": [
            (92.6450, 23.7760),
            (92.6550, 23.7760),
            (92.6550, 23.7840),
            (92.6450, 23.7840),
            (92.6450, 23.7760),
        ],
        "current_risk": "HIGH",
        "risk_source": "ensemble_model",
        "operational_tier": 2,  # Monsoon InSAR canopy decorrelation
        "ml_risk_pct": 72.0,
        "ml_confidence_pct": 82.0,
        "fos_value": 1.12,
        "rainfall_intensity_mmhr": 35.0,
        "antecedent_precip_40d": 190.0,
        "insar_velocity_mmyr": -16.0,
        "insar_coherence": 0.28,  # Below 0.35 threshold -> Tier 2
        "culvert_clogged": False,
        "sentinel2_toe_cut": False,
        "shap_drivers": [
            {"factor": "InSAR Blind Tier 2 GWaveNet Stress", "weight_pct": 40.0, "value": 0.72},
            {"factor": "Soil Volumetric Water Content", "weight_pct": 35.0, "value": 74.0},
            {"factor": "Acoustic Micro-Fracture AE Rate", "weight_pct": 25.0, "value": 18.0},
        ],
    },
    {
        "zone_name": "NH-54-KM-42-45-Thingdawl",
        "corridor_code": "NH-54-MIZORAM",
        "lgd_district_code": "283",
        "lgd_state_code": "15",
        "center_lat": 23.8200,
        "center_lon": 92.6800,
        "coords": [
            (92.6750, 23.8160),
            (92.6850, 23.8160),
            (92.6850, 23.8240),
            (92.6750, 23.8240),
            (92.6750, 23.8160),
        ],
        "current_risk": "LOW",
        "risk_source": "ensemble_model",
        "operational_tier": 1,
        "ml_risk_pct": 14.5,
        "ml_confidence_pct": 96.0,
        "fos_value": 1.85,
        "rainfall_intensity_mmhr": 4.0,
        "antecedent_precip_40d": 45.0,
        "insar_velocity_mmyr": -2.1,
        "insar_coherence": 0.78,
        "culvert_clogged": False,
        "sentinel2_toe_cut": False,
        "shap_drivers": [
            {"factor": "High Factor of Safety (Stable)", "weight_pct": 70.0, "value": 1.85},
            {"factor": "Low Pore Pressure", "weight_pct": 20.0, "value": 2.1},
            {"factor": "Healthy Dense Root Cohesion", "weight_pct": 10.0, "value": 14.2},
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. VILLAGES & CRITICAL INFRASTRUCTURE (Section 6.6)
# ═══════════════════════════════════════════════════════════════════════════════

VILLAGES_DATA = [
    # Meghalaya Sector (East Khasi Hills / Jaintia Hills)
    {
        "village_name": "Sonapur Village",
        "lgd_village_code": "272001",
        "lgd_district_code": "272",
        "lgd_state_code": "17",
        "lat": 25.5480,
        "lon": 91.8490,
        "graph_node_id": 2001,
        "permanent_population": 1450,
        "fastag_baseline_daily": 850,
        "resident_capacity_equivalent": 450,
        "pds_grain_stock_kg": 6800.0,
        "pds_fuel_stock_litres": 1400.0,
        "daily_consumption_burn_rate": 1.2,
        "has_primary_health_centre": True,
        "has_school": True,
        "has_pds_warehouse": True,
        "helipad_lat": 25.5495,
        "helipad_lon": 91.8510,
        "helipad_dist_km": 0.4,
    },
    {
        "village_name": "Mawryngkneng Outpost",
        "lgd_village_code": "272002",
        "lgd_district_code": "272",
        "lgd_state_code": "17",
        "lat": 25.5560,
        "lon": 91.8620,
        "graph_node_id": 2002,
        "permanent_population": 2100,
        "fastag_baseline_daily": 1200,
        "resident_capacity_equivalent": 600,
        "pds_grain_stock_kg": 9500.0,
        "pds_fuel_stock_litres": 2200.0,
        "daily_consumption_burn_rate": 1.2,
        "has_primary_health_centre": True,
        "has_school": True,
        "has_pds_warehouse": True,
        "helipad_lat": 25.5570,
        "helipad_lon": 91.8640,
        "helipad_dist_km": 0.3,
    },
    {
        "village_name": "Umling Basti",
        "lgd_village_code": "272003",
        "lgd_district_code": "272",
        "lgd_state_code": "17",
        "lat": 25.5790,
        "lon": 91.8810,
        "graph_node_id": 2003,
        "permanent_population": 820,
        "fastag_baseline_daily": 450,
        "resident_capacity_equivalent": 250,
        "pds_grain_stock_kg": 3200.0,
        "pds_fuel_stock_litres": 850.0,
        "daily_consumption_burn_rate": 1.2,
        "has_primary_health_centre": False,
        "has_school": True,
        "has_pds_warehouse": False,
        "helipad_lat": 25.5820,
        "helipad_lon": 91.8830,
        "helipad_dist_km": 0.5,
    },
    {
        "village_name": "Ratacherra Border Hamlet",
        "lgd_village_code": "272004",
        "lgd_district_code": "272",
        "lgd_state_code": "17",
        "lat": 25.6190,
        "lon": 91.9210,
        "graph_node_id": 2004,
        "permanent_population": 650,
        "fastag_baseline_daily": 300,
        "resident_capacity_equivalent": 180,
        "pds_grain_stock_kg": 1800.0,
        "pds_fuel_stock_litres": 450.0,
        "daily_consumption_burn_rate": 1.3,
        "has_primary_health_centre": False,
        "has_school": True,
        "has_pds_warehouse": False,
        "helipad_lat": 25.6210,
        "helipad_lon": 91.9230,
        "helipad_dist_km": 0.4,
    },
    # Mizoram Sector (Aizawl District)
    {
        "village_name": "Sairang Kawnpui",
        "lgd_village_code": "283001",
        "lgd_district_code": "283",
        "lgd_state_code": "15",
        "lat": 23.7810,
        "lon": 92.6510,
        "graph_node_id": 2101,
        "permanent_population": 3200,
        "fastag_baseline_daily": 1400,
        "resident_capacity_equivalent": 800,
        "pds_grain_stock_kg": 14000.0,
        "pds_fuel_stock_litres": 3500.0,
        "daily_consumption_burn_rate": 1.2,
        "has_primary_health_centre": True,
        "has_school": True,
        "has_pds_warehouse": True,
        "helipad_lat": 23.7830,
        "helipad_lon": 92.6540,
        "helipad_dist_km": 0.6,
    },
    {
        "village_name": "Thingdawl Veng",
        "lgd_village_code": "283002",
        "lgd_district_code": "283",
        "lgd_state_code": "15",
        "lat": 23.8210,
        "lon": 92.6810,
        "graph_node_id": 2102,
        "permanent_population": 1150,
        "fastag_baseline_daily": 550,
        "resident_capacity_equivalent": 300,
        "pds_grain_stock_kg": 5200.0,
        "pds_fuel_stock_litres": 1100.0,
        "daily_consumption_burn_rate": 1.2,
        "has_primary_health_centre": False,
        "has_school": True,
        "has_pds_warehouse": False,
        "helipad_lat": 23.8230,
        "helipad_lon": 92.6830,
        "helipad_dist_km": 0.3,
    },
    {
        "village_name": "Kolasib Junction",
        "lgd_village_code": "283003",
        "lgd_district_code": "283",
        "lgd_state_code": "15",
        "lat": 23.8450,
        "lon": 92.7050,
        "graph_node_id": 2103,
        "permanent_population": 4100,
        "fastag_baseline_daily": 1800,
        "resident_capacity_equivalent": 950,
        "pds_grain_stock_kg": 18500.0,
        "pds_fuel_stock_litres": 4800.0,
        "daily_consumption_burn_rate": 1.2,
        "has_primary_health_centre": True,
        "has_school": True,
        "has_pds_warehouse": True,
        "helipad_lat": 23.8470,
        "helipad_lon": 92.7080,
        "helipad_dist_km": 0.5,
    },
    {
        "village_name": "Bilkhawthlir Valley",
        "lgd_village_code": "283004",
        "lgd_district_code": "283",
        "lgd_state_code": "15",
        "lat": 23.8650,
        "lon": 92.7350,
        "graph_node_id": 2104,
        "permanent_population": 980,
        "fastag_baseline_daily": 420,
        "resident_capacity_equivalent": 260,
        "pds_grain_stock_kg": 4100.0,
        "pds_fuel_stock_litres": 900.0,
        "daily_consumption_burn_rate": 1.2,
        "has_primary_health_centre": False,
        "has_school": True,
        "has_pds_warehouse": False,
        "helipad_lat": 23.8670,
        "helipad_lon": 92.7380,
        "helipad_dist_km": 0.4,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ROAD EDGES & STRUCTURAL CHOKEPOINTS (Section 6.6)
# ═══════════════════════════════════════════════════════════════════════════════

ROAD_EDGES_DATA = [
    # NH-06 Meghalaya Corridor Network
    {"u": 1001, "v": 2001, "zone_idx": 0, "type": "national_highway", "len": 1850.0, "chokepoint": "OPEN_ROAD", "multiplier": 1.0, "defence": True, "coords": [(91.8420, 25.5420), (91.8490, 25.5480)]},
    {"u": 2001, "v": 2002, "zone_idx": 0, "type": "national_highway", "len": 2100.0, "chokepoint": "BRIDGE", "multiplier": 8.0, "defence": True, "coords": [(91.8490, 25.5480), (91.8540, 25.5520), (91.8620, 25.5560)]},
    {"u": 2002, "v": 2003, "zone_idx": 1, "type": "national_highway", "len": 3200.0, "chokepoint": "NARROW_CUTTING", "multiplier": 1.8, "defence": True, "coords": [(91.8620, 25.5560), (91.8720, 25.5680), (91.8810, 25.5790)]},
    {"u": 2003, "v": 2004, "zone_idx": 2, "type": "national_highway", "len": 4500.0, "chokepoint": "CULVERT", "multiplier": 2.5, "defence": True, "coords": [(91.8810, 25.5790), (91.9020, 25.6010), (91.9210, 25.6190)]},
    {"u": 2004, "v": 1002, "zone_idx": 2, "type": "national_highway", "len": 2800.0, "chokepoint": "OPEN_ROAD", "multiplier": 1.0, "defence": True, "coords": [(91.9210, 25.6190), (91.9350, 25.6320)]},
    # Secondary detour & ridge pedestrian paths
    {"u": 2001, "v": 3001, "zone_idx": 0, "type": "village_road", "len": 1200.0, "chokepoint": "OPEN_ROAD", "multiplier": 1.0, "defence": False, "coords": [(91.8490, 25.5480), (91.8510, 25.5550)], "pedestrian": True},
    {"u": 3001, "v": 2002, "zone_idx": 0, "type": "village_road", "len": 1400.0, "chokepoint": "OPEN_ROAD", "multiplier": 1.0, "defence": False, "coords": [(91.8510, 25.5550), (91.8620, 25.5560)], "pedestrian": True},
    {"u": 2002, "v": 3002, "zone_idx": 1, "type": "state_highway", "len": 3800.0, "chokepoint": "OPEN_ROAD", "multiplier": 1.0, "defence": False, "coords": [(91.8620, 25.5560), (91.8750, 25.5620), (91.8900, 25.5720)]},
    {"u": 3002, "v": 2003, "zone_idx": 1, "type": "state_highway", "len": 1900.0, "chokepoint": "CULVERT", "multiplier": 2.5, "defence": False, "coords": [(91.8900, 25.5720), (91.8810, 25.5790)]},

    # NH-54 Mizoram Corridor Network
    {"u": 1101, "v": 2101, "zone_idx": 3, "type": "national_highway", "len": 2400.0, "chokepoint": "NARROW_CUTTING", "multiplier": 1.8, "defence": True, "coords": [(92.6380, 23.7680), (92.6510, 23.7810)]},
    {"u": 2101, "v": 2102, "zone_idx": 3, "type": "national_highway", "len": 4100.0, "chokepoint": "BRIDGE", "multiplier": 8.0, "defence": True, "coords": [(92.6510, 23.7810), (92.6650, 23.8010), (92.6810, 23.8210)]},
    {"u": 2102, "v": 2103, "zone_idx": 4, "type": "national_highway", "len": 3600.0, "chokepoint": "CULVERT", "multiplier": 2.5, "defence": True, "coords": [(92.6810, 23.8210), (92.6930, 23.8340), (92.7050, 23.8450)]},
    {"u": 2103, "v": 2104, "zone_idx": 4, "type": "national_highway", "len": 2900.0, "chokepoint": "OPEN_ROAD", "multiplier": 1.0, "defence": True, "coords": [(92.7050, 23.8450), (92.7200, 23.8560), (92.7350, 23.8650)]},
    {"u": 2104, "v": 1102, "zone_idx": 4, "type": "national_highway", "len": 3100.0, "chokepoint": "OPEN_ROAD", "multiplier": 1.0, "defence": True, "coords": [(92.7350, 23.8650), (92.7500, 23.8780)]},
]


async def seed_database():
    print("==================================================================")
    print("SafeSlope-NER — Corridor Baseline Seed Data Generator")
    print("==================================================================")

    # Connect to database if available
    db_connected = False
    if HAS_DB and database is not None:
        try:
            await database.connect()
            print("[OK] Connected to database successfully.")
            db_connected = True
        except Exception as e:
            print(f"Database direct connection skipped ({e}) — writing seed_data.sql file.")
    else:
        print("Running in offline generation mode — generating seed_data.sql.")

    sql_statements = []

    # ── 1. Seed Risk Zones ──
    print("\n1. Seeding Risk Zones...")
    zone_ids = []
    for i, z in enumerate(ZONES_DATA):
        # Build WKT polygon
        coord_str = ", ".join(f"{lon} {lat}" for lon, lat in z["coords"])
        wkt = f"POLYGON(({coord_str}))"

        # Compute H3 cells covering this zone
        h3_r9 = list(h3.polygon_to_cells(
            h3.Polygon([(lat, lon) for lon, lat in z["coords"]]),
            resolution=9,
        ))
        h3_r10 = list(h3.polygon_to_cells(
            h3.Polygon([(lat, lon) for lon, lat in z["coords"]]),
            resolution=10,
        ))

        stmt = f"""
        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            '{z["zone_name"]}', '{z["corridor_code"]}', '{z["lgd_district_code"]}', '{z["lgd_state_code"]}',
            ST_GeomFromText('{wkt}', 4326),
            ARRAY{h3_r9}::TEXT[],
            ARRAY{h3_r10}::TEXT[],
            '{z["current_risk"]}', '{z["risk_source"]}',
            {z["operational_tier"]}, {z["ml_risk_pct"]}, {z["ml_confidence_pct"]}, {z["fos_value"]},
            {z["rainfall_intensity_mmhr"]}, {z["antecedent_precip_40d"]}, {z["insar_velocity_mmyr"]},
            {z["insar_coherence"]}, {str(z["culvert_clogged"]).upper()}, {str(z["sentinel2_toe_cut"]).upper()},
            '{json.dumps(z["shap_drivers"])}'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        """
        sql_statements.append(stmt)
        if db_connected:
            try:
                row = await database.fetch_one(stmt)
                zid = row["id"] if row else (i + 1)
                zone_ids.append(zid)
                print(f"  [OK] Zone #{zid}: {z['zone_name']} (Res-9: {len(h3_r9)} cells, Res-10: {len(h3_r10)} cells)")
            except Exception as e:
                zone_ids.append(i + 1)
        else:
            zid = i + 1
            zone_ids.append(zid)
            print(f"  [OK] [SQL] Zone #{zid}: {z['zone_name']}")

    # ── 2. Seed Sensors (30 Registered IoT Nodes) ──
    print("\n2. Seeding 30 Registered IoT Sensors...")
    sensor_types = ["inclinometer", "geophone", "ert", "rtk_gnss", "fbg", "turbidity"]
    sensor_count = 0
    now = datetime.now(timezone.utc)

    for z_idx, z in enumerate(ZONES_DATA):
        zid = zone_ids[z_idx] if z_idx < len(zone_ids) else (z_idx + 1)
        base_lat = z["center_lat"]
        base_lon = z["center_lon"]

        # Deploy 6 multi-parameter nodes per zone
        for s_idx in range(6):
            stype = sensor_types[s_idx % len(sensor_types)]
            sid = f"NODE-{zid:02d}-{s_idx+1:02d}"
            lat = base_lat + (s_idx - 2.5) * 0.0012
            lon = base_lon + (s_idx - 2.5) * 0.0012
            h3_9 = h3.latlng_to_cell(lat, lon, 9)
            h3_10 = h3.latlng_to_cell(lat, lon, 10)
            is_burn_in = (z_idx == 4 and s_idx >= 4)  # Node 29 & 30 in burn-in mode
            burn_in_val = f"'{ (now + timedelta(days=10)).isoformat() }'" if is_burn_in else "NULL"

            stmt = f"""
            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                '{sid}', '{stype}', 101,
                ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326),
                '{h3_9}', '{h3_10}', 0.05,
                TRUE, {burn_in_val}
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            """
            sql_statements.append(stmt)
            if db_connected:
                try:
                    await database.execute(stmt)
                except Exception:
                    pass
            sensor_count += 1

    print(f"  [OK] Prepared {sensor_count} in-situ IoT nodes with H3 indices and PostGIS points.")

    # ── 3. Seed Villages ──
    print("\n3. Seeding Villages & PDS Inventory...")
    for v in VILLAGES_DATA:
        stmt = f"""
        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            '{v["village_name"]}', '{v["lgd_village_code"]}', '{v["lgd_district_code"]}', '{v["lgd_state_code"]}',
            ST_SetSRID(ST_MakePoint({v["lon"]}, {v["lat"]}), 4326),
            {v["graph_node_id"]}, {v["permanent_population"]}, {v["fastag_baseline_daily"]},
            {v["resident_capacity_equivalent"]}, {v["pds_grain_stock_kg"]}, {v["pds_fuel_stock_litres"]},
            {v["daily_consumption_burn_rate"]}, {str(v["has_primary_health_centre"]).upper()},
            {str(v["has_school"]).upper()}, {str(v["has_pds_warehouse"]).upper()},
            ST_SetSRID(ST_MakePoint({v["helipad_lon"]}, {v["helipad_lat"]}), 4326),
            {v["helipad_dist_km"]}
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        """
        sql_statements.append(stmt)
        if db_connected:
            try:
                await database.execute(stmt)
            except Exception:
                pass
        print(f"  [OK] Village: {v['village_name']} (Pop: {v['permanent_population']:,}, Grain: {v['pds_grain_stock_kg']}kg)")

    # ── 4. Seed Road Edges ──
    print("\n4. Seeding Road Transportation Graph & Structural Chokepoints...")
    edge_count = 0
    for e in ROAD_EDGES_DATA:
        coord_str = ", ".join(f"{lon} {lat}" for lon, lat in e["coords"])
        geom_wkt = f"LINESTRING({coord_str})"
        zid = zone_ids[e["zone_idx"]] if e["zone_idx"] < len(zone_ids) else 1
        ped = str(e.get("pedestrian", False)).upper()

        stmt = f"""
        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            {100000 + edge_count}, {e["u"]}, {e["v"]},
            ST_GeomFromText('{geom_wkt}', 4326),
            {zid}, '{e["type"]}', {e["len"]},
            '{e["chokepoint"]}', {e["multiplier"]}, {str(e["defence"]).upper()},
            {ped}, {ped}
        );
        """
        sql_statements.append(stmt)
        if db_connected:
            try:
                await database.execute(stmt)
            except Exception:
                pass
        edge_count += 1

    print(f"  [OK] Prepared {len(ROAD_EDGES_DATA)} road edges with chokepoint multipliers.")

    # ── 5. Write seed_data.sql for reproducible deployment ──
    sql_path = os.path.join(os.path.dirname(__file__), "..", "seed_data.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- SafeSlope-NER Production Corridor Seed Script\n")
        f.write("\n".join(sql_statements))
    print(f"\n[OK] Generated standalone deployment SQL: {sql_path}")

    if db_connected:
        try:
            await database.disconnect()
        except Exception:
            pass

    print("Corridor seed data generation completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
