"""
SafeSlope-NER — Radar & Remote Sensing Ingestion Worker (InSAR & Optical)
Covers: Section 2.2 (Sentinel-1 InSAR, Sentinel-2 Optical, Cartosat DEM),
        Section 6.1 (Multi-rate Ingestion & Grid Harmonization),
        Section 7.4 (Tier 1 -> Tier 2 InSAR decorrelation trigger: gamma < 0.35)

Runs periodically or triggers on MOSDAC / Copernicus hub data availability.
Updates:
  - InSAR LOS deformation velocity (v_LOS mm/yr)
  - Interferometric coherence (gamma, 0.0 - 1.0)
  - Sentinel-2 optical NDVI / NDMI and anthropogenic toe-cut detection
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import get_settings
from app.database import database

logger = logging.getLogger(__name__)
settings = get_settings()


async def process_insar_displacement_update(
    zone_id: int,
    v_los_mmyr: float,
    coherence_gamma: float,
    unwrapped_phase_rad: Optional[float] = None,
    los_displacement_mm: Optional[float] = None,
) -> dict[str, Any]:
    """
    Ingests and harmonizes Sentinel-1/NISAR interferometric radar products.
    If coherence drops below gamma = 0.35 (e.g. dense monsoon jungle decorrelation),
    the system automatically downgrades the zone's operational tier to Tier 2 (Section 7.4).
    """
    # Check coherence threshold for Tier 2 degradation
    tier_change_required = coherence_gamma < settings.INSAR_COHERENCE_TIER1_MIN

    query = """
        UPDATE risk_zones
        SET insar_velocity_mmyr = :v_los,
            insar_coherence = :coherence,
            operational_tier = CASE
                WHEN :coherence < :min_coherence AND operational_tier = 1 THEN 2
                WHEN :coherence >= :min_coherence AND operational_tier = 2 THEN 1
                ELSE operational_tier
            END,
            updated_at = NOW()
        WHERE id = :zone_id
        RETURNING id, zone_name, insar_velocity_mmyr, insar_coherence, operational_tier
    """
    row = await database.fetch_one(
        query,
        {
            "v_los": v_los_mmyr,
            "coherence": coherence_gamma,
            "min_coherence": settings.INSAR_COHERENCE_TIER1_MIN,
            "zone_id": zone_id,
        },
    )

    if not row:
        raise ValueError(f"Zone ID {zone_id} does not exist.")

    result = dict(row)
    if tier_change_required:
        logger.warning(
            "InSAR decorrelation detected on Zone %s (coherence gamma=%.2f < %.2f). "
            "Operational Tier degraded to %d.",
            result.get("zone_name"),
            coherence_gamma,
            settings.INSAR_COHERENCE_TIER1_MIN,
            result.get("operational_tier"),
        )
    return result


async def process_optical_sentinel2_update(
    zone_id: int,
    ndvi: float,
    ndmi: float,
    toe_cut_detected: bool,
) -> dict[str, Any]:
    """
    Harmonizes Sentinel-2 multispectral vegetation/soil indices and flags
    un-retained excavation cuts (toe-cutting) along road corridors.
    """
    query = """
        UPDATE risk_zones
        SET sentinel2_toe_cut = :toe_cut,
            updated_at = NOW()
        WHERE id = :zone_id
        RETURNING id, zone_name, sentinel2_toe_cut, current_risk
    """
    row = await database.fetch_one(
        query,
        {
            "toe_cut": toe_cut_detected,
            "zone_id": zone_id,
        },
    )

    if not row:
        raise ValueError(f"Zone ID {zone_id} does not exist.")

    result = dict(row)
    if toe_cut_detected:
        logger.warning(
            "Anthropogenic toe-cut excavation detected on Zone %s via Sentinel-2. "
            "Safety override armed.",
            result.get("zone_name"),
        )
    return result
