from typing import Optional


def resolve_risk(
    physics_risk: Optional[str], ml_risk_pct: Optional[float]
) -> tuple[str, str]:
    """
    The core architectural idea from the project doc: the physics
    safety floor always wins if it says HIGH, regardless of what
    the ML model thinks. Otherwise, fall back to the ML score.
    """
    if physics_risk == "HIGH":
        return "HIGH", "physics_floor"

    if ml_risk_pct is not None:
        if ml_risk_pct >= 70:
            return "HIGH", "ml_model"
        if ml_risk_pct >= 40:
            return "MODERATE", "ml_model"
        return "LOW", "ml_model"

    return "LOW", "default"
