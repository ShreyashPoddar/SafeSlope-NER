"""
SafeSlope-NER — Dead-Letter Queue (DLQ) Quarantine Consumer
Covers: Section 3.5 (Ingestion Backpressure & DLQ Quarantine),
        Section 3.4 (Anti-Poisoning & CRC Anomaly Tracking)

Processes quarantined packets from `quarantine_telemetry`:
  - Analyzes recurring CRC error patterns (identifying failing transmitters / RF jamming)
  - Identifies malicious payload injection attempts (POISONING_ATTEMPT)
  - Aggregates forensic health stats for network operators
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.database import database

logger = logging.getLogger(__name__)


async def get_dlq_forensics_summary(hours: int = 24) -> dict[str, Any]:
    """
    Summarizes DLQ quarantine patterns over the specified lookback window.
    Provides diagnostic metrics on node hardware faults vs RF noise vs malicious attempts.
    """
    query = """
        SELECT
            rejection_reason,
            COUNT(*) as total_count,
            COUNT(DISTINCT node_id_raw) as distinct_nodes,
            COUNT(DISTINCT gateway_id) as distinct_gateways
        FROM quarantine_telemetry
        WHERE received_at >= NOW() - (:hours || ' hours')::INTERVAL
        GROUP BY rejection_reason
        ORDER BY total_count DESC
    """
    rows = await database.fetch_all(query, {"hours": hours})
    
    breakdown = {
        r["rejection_reason"]: {
            "count": r["total_count"],
            "nodes_affected": r["distinct_nodes"],
            "gateways_involved": r["distinct_gateways"],
        }
        for r in rows
    }

    # Identify repeat offending nodes with physical sensor breakdown
    top_offenders_query = """
        SELECT node_id_raw, rejection_reason, COUNT(*) as fail_count
        FROM quarantine_telemetry
        WHERE received_at >= NOW() - (:hours || ' hours')::INTERVAL
          AND node_id_raw IS NOT NULL
        GROUP BY node_id_raw, rejection_reason
        HAVING COUNT(*) > 5
        ORDER BY fail_count DESC
        LIMIT 10
    """
    offenders = await database.fetch_all(top_offenders_query, {"hours": hours})

    return {
        "lookback_hours": hours,
        "total_quarantined": sum(r["total_count"] for r in rows),
        "reason_breakdown": breakdown,
        "failing_nodes": [dict(o) for o in offenders],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def purge_old_quarantine_records(retention_days: int = 30) -> int:
    """
    Cleans up old quarantined frames beyond judicial retention requirements.
    """
    delete_query = """
        DELETE FROM quarantine_telemetry
        WHERE received_at < NOW() - (:days || ' days')::INTERVAL
    """
    result = await database.execute(delete_query, {"days": retention_days})
    logger.info("Purged expired DLQ records older than %d days.", retention_days)
    return result
