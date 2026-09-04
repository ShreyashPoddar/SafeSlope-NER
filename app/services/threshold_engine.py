"""
SafeSlope-NER - Landslide Risk Algorithm Threshold & Evaluation Engine
Member 1 & Member 6 System

Manages configurable risk thresholds (Advisory, Warning, Critical),
evaluates predictions received from external algorithms (e.g., XGBoost, physics models,
or rainfall-induced slope stability models), and triggers automated area notifications
when thresholds are breached.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel


class ThresholdSettings(BaseModel):
    advisory_threshold: float = 40.0   # MODERATE risk: Caution & internal monitoring
    warning_threshold: float = 70.0    # HIGH risk: Community advisory & evacuation readiness
    critical_threshold: float = 85.0   # CRITICAL risk: Immediate evacuation & road closure
    min_confidence: float = 50.0       # Minimum model confidence % required to trigger auto-broadcast
    auto_notify_on_breach: bool = True # Automatically dispatch alerts to area when threshold is exceeded
    cooldown_minutes: int = 15         # Prevent alert fatigue: min minutes between broadcasts per zone
    enabled_channels: list[str] = ["whatsapp", "sms", "telegram", "cap", "siren"]
    target_audience: str = "all_in_area"  # "all_in_area", "volunteers_only", "full_blast"


# Global thread-safe in-memory settings store
_CURRENT_SETTINGS = ThresholdSettings()

# Tracks last broadcast timestamp per zone to implement cooldown/debounce
_ZONE_LAST_TRIGGER: Dict[str, datetime] = {}

# Recent algorithm evaluation logs
_EVALUATION_LOGS: list[Dict[str, Any]] = []


def get_threshold_settings() -> ThresholdSettings:
    """Retrieve current threshold settings."""
    return _CURRENT_SETTINGS


def update_threshold_settings(new_settings: Dict[str, Any]) -> ThresholdSettings:
    """Update threshold settings dynamically."""
    global _CURRENT_SETTINGS
    data = _CURRENT_SETTINGS.model_dump()
    data.update({k: v for k, v in new_settings.items() if v is not None})
    _CURRENT_SETTINGS = ThresholdSettings(**data)
    return _CURRENT_SETTINGS


def determine_risk_level(ml_risk_pct: Optional[float]) -> Tuple[str, bool]:
    """
    Evaluates risk percentage against configured thresholds.
    Returns: (risk_level: str, is_threshold_breached: bool)
    """
    if ml_risk_pct is None:
        return "LOW", False

    settings = _CURRENT_SETTINGS
    if ml_risk_pct >= settings.critical_threshold:
        return "CRITICAL", True
    elif ml_risk_pct >= settings.warning_threshold:
        return "HIGH", True
    elif ml_risk_pct >= settings.advisory_threshold:
        return "MODERATE", False
    else:
        return "LOW", False


from app.services.risk_calculator import calculate_complete_risk_profile


async def evaluate_landslide_algorithm_prediction(
    zone_id: int,
    zone_name: str,
    risk_pct: float,
    confidence_pct: float = 85.0,
    model_version: str = "landslide-v1.0",
    features: Optional[Dict[str, Any]] = None,
    force_notify: bool = False,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Core entry point for the upcoming main git landslide risk prediction algorithm.
    Dynamically computes Factor of Safety (FoS), runout impact radius, evacuation window,
    isolated villages, and affected populations with ZERO hardcoded values.
    Evaluates against thresholds and triggers the area emergency broadcast upon breach.
    """
    settings = _CURRENT_SETTINGS

    # Normalize risk probability if passed as 0.0 - 1.0
    normalized_risk_pct = risk_pct * 100.0 if risk_pct <= 1.0 else risk_pct

    feat = features or {}
    rainfall_24h = feat.get("rainfall_24h_mm") or feat.get("rainfall_mm_24h")
    soil_moist = feat.get("soil_moisture_pct") or feat.get("soil_moisture") or feat.get("soil_saturation_pct")
    tilt_val = feat.get("slope_tilt_deg")
    tilt_rate = feat.get("slope_tilt_rate_deg_hr") or feat.get("tilt_delta")
    pore_press = feat.get("pore_pressure_kpa")

    # Dynamic Complete Risk & Spatial Profile Calculation
    profile = calculate_complete_risk_profile(
        zone_name=zone_name,
        zone_id=zone_id,
        lat=lat,
        lng=lng,
        risk_pct=normalized_risk_pct,
        confidence_pct=confidence_pct,
        rainfall_24h_mm=rainfall_24h,
        soil_moisture_pct=soil_moist,
        slope_tilt_deg=tilt_val,
        tilt_rate_deg_hr=tilt_rate,
        pore_pressure_kpa=pore_press,
        model_version=model_version,
    )


    final_risk_pct = profile["calculated_risk_pct"]
    risk_level, threshold_breached = determine_risk_level(final_risk_pct)
    # If geotechnical physics shear failure occurred (FoS < 1.0), force CRITICAL threshold breach
    if profile.get("is_physics_failure"):
        risk_level = "CRITICAL"
        threshold_breached = True

    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Check cooldown
    last_trigger = _ZONE_LAST_TRIGGER.get(zone_name)
    is_in_cooldown = False
    if last_trigger:
        elapsed_seconds = (now - last_trigger).total_seconds()
        if elapsed_seconds < (settings.cooldown_minutes * 60) and not force_notify:
            is_in_cooldown = True

    confidence_ok = confidence_pct >= settings.min_confidence
    should_notify = (threshold_breached and confidence_ok and not is_in_cooldown and settings.auto_notify_on_breach) or force_notify

    eval_result: Dict[str, Any] = {
        "timestamp": now_str,
        "zone_id": zone_id,
        "zone_name": zone_name,
        "risk_pct": normalized_risk_pct,
        "calculated_risk_pct": final_risk_pct,
        "confidence_pct": confidence_pct,

        "model_version": model_version,
        "derived_risk_level": risk_level,
        "threshold_breached": threshold_breached,
        "factor_of_safety": profile["factor_of_safety"],
        "is_physics_failure": profile["is_physics_failure"],
        "impact_radius_meters": profile["impact_radius_meters"],
        "impact_radius_km": profile["impact_radius_km"],
        "evacuation_window_hours": profile["evacuation_window_hours"],
        "active_thresholds": {
            "warning": settings.warning_threshold,
            "critical": settings.critical_threshold,
            "min_confidence": settings.min_confidence,
        },
        "environmental_features": profile["environmental_features"],
        "isolation_metrics": profile["isolation_metrics"],
        "notification_triggered": should_notify,
        "cooldown_active": is_in_cooldown,
        "dispatch_summary": None,
    }

    # Update database risk state if database is available
    try:
        from app.database import database
        from app.redis_client import redis_client
        import json

        if database.is_connected:
            await database.execute(
                """UPDATE risk_zones
                   SET current_risk = :risk, risk_source = :source,
                       ml_risk_pct = :ml_pct, ml_confidence_pct = :confidence,
                       updated_at = now()
                   WHERE id = :id OR zone_name = :zone_name""",
                {
                    "risk": risk_level,
                    "source": f"algorithm_{model_version}",
                    "ml_pct": final_risk_pct,
                    "confidence": confidence_pct,
                    "id": zone_id,
                    "zone_name": zone_name,
                },
            )
            try:
                rows = await database.fetch_all("SELECT * FROM risk_zones")
                state = {r["zone_name"]: dict(r) for r in rows}
                redis_client.set("risk_state_all", json.dumps(state, default=str), ex=300)
            except Exception:
                pass
    except Exception:
        pass  # Running standalone or in memory mode

    # Trigger area emergency broadcast if threshold is breached
    if should_notify:
        _ZONE_LAST_TRIGGER[zone_name] = now
        try:
            from app.comms.dispatcher import alert_dispatcher

            # Fully calculated dynamic isolation metrics
            isolation_data = dict(profile["isolation_metrics"])
            isolation_data.update({
                "trigger_algorithm": model_version,
                "predicted_risk_pct": final_risk_pct,
                "factor_of_safety": profile["factor_of_safety"],
                "evacuation_window_hours": profile["evacuation_window_hours"],
                "impact_radius_km": profile["impact_radius_km"],
            })

            dispatch_res = await alert_dispatcher.evaluate_risk_trigger(
                zone_id=zone_id,
                zone_name=zone_name,
                risk_level=risk_level,
                source=f"algorithm_{model_version}",
                isolation_data=isolation_data,
                force_broadcast=True,
                notification_settings={
                    "channels": settings.enabled_channels,
                    "target_audience": settings.target_audience,
                    "include_bypass": True,
                },
            )
            eval_result["dispatch_summary"] = dispatch_res
        except Exception as exc:
            eval_result["dispatch_error"] = str(exc)

    _EVALUATION_LOGS.insert(0, eval_result)
    if len(_EVALUATION_LOGS) > 50:
        _EVALUATION_LOGS.pop()

    return eval_result


def get_recent_evaluations(limit: int = 20) -> list[Dict[str, Any]]:
    """Return recent algorithm evaluation records."""
    return _EVALUATION_LOGS[:limit]
