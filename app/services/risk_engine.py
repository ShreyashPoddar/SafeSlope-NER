from typing import Optional, Dict, Any
from app.services.threshold_engine import determine_risk_level
from app.services.risk_calculator import calculate_factor_of_safety, calculate_failure_probability


def resolve_risk(
    physics_risk: Optional[str] = None,
    ml_risk_pct: Optional[float] = None,
    features: Optional[Dict[str, Any]] = None,
) -> tuple[str, str]:
    """
    Dynamic risk resolution:
    1. Physics safety floor always wins if it evaluates or reports HIGH or CRITICAL.
    2. If raw sensor features are provided, dynamically computes Factor of Safety (FoS).
       If FoS < 1.0 (imminent slope failure), forces CRITICAL physics override.
    3. Evaluates ML prediction percentage against dynamic configurable thresholds.
    """
    # 1. Direct physics override from upstream rules or sensor thresholding
    if physics_risk in ["HIGH", "CRITICAL"]:
        return physics_risk, "physics_floor"

    # 2. Dynamic geotechnical FoS calculation if sensor features are provided
    if features:
        slope_angle = features.get("slope_tilt_deg") or features.get("pitch_deg") or 35.0
        soil_moisture = features.get("soil_moisture_pct") or features.get("soil_moisture")
        pore_pressure = features.get("pore_pressure_kpa")
        fos = calculate_factor_of_safety(
            slope_angle_deg=slope_angle,
            soil_moisture_pct=soil_moisture,
            pore_pressure_kpa=pore_pressure,
        )
        if fos < 1.0:
            return "CRITICAL", "physics_fos_shear_failure"
        elif fos < 1.2 and physics_risk != "LOW":
            return "HIGH", "physics_fos_marginal_stability"

    # 3. Dynamic ML prediction evaluation
    if ml_risk_pct is not None:
        risk_level, _ = determine_risk_level(ml_risk_pct)
        return risk_level, "ml_model"

    return "LOW", "default"

