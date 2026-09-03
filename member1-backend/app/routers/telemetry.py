"""
SafeSlope-NER — Telemetry Router
Implements the complete 11-step binary ingestion pipeline from Section 3 of
computational_backend_plan.txt, covering:
  - Section 3.1: 20-byte binary wire protocol struct unpacking
  - Section 3.2: LoRa concentrator gateway binary batch endpoint
  - Section 3.3: Epoch anchoring (TrueTimestamp = GatewayEpoch + NodeOffset)
  - Section 3.4: HMAC-SHA256 verification, CRC-16 check, range clamping, deduplication
  - Section 3.5: Dead-Letter Queue (DLQ) quarantine for corrupted frames
  - Section 4.2: Out-of-order backfill detection (suppresses retroactive alarms)
  - Section 8.5: Every accepted frame appended to the cryptographic audit ledger
"""
from __future__ import annotations

import json
import struct
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, status

from app.auth import require_gateway_hmac, verify_api_key, get_current_user
from app.core.config import get_settings
from app.database import database
from app.models.schemas import (
    BatchIngestionResponse,
    BinaryTelemetryFrame,
    RejectionReason,
    SensorHealthResponse,
    TelemetryPayload,
)
from app.redis_client import get_redis

settings = get_settings()
router = APIRouter(prefix="/telemetry", tags=["telemetry"])

# ─────────────────────────────────────────────────────────────────────────────
# CRC-16-CCITT calculator (Section 3.1)
# ─────────────────────────────────────────────────────────────────────────────
_crc16 = crcmod.predefined.mkCrcFun("crc-ccitt-false")

# ─────────────────────────────────────────────────────────────────────────────
# Wire protocol constants (Section 3.1)
# ─────────────────────────────────────────────────────────────────────────────
FRAME_FORMAT = "<HHhhBBHHHbBH"   # 20 bytes exact (Section 3.1)
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)   # Equals 20 bytes exactly
GATEWAY_HEADER_FORMAT = "<HH"     # gateway_id (2B) + frame_count (2B)
GATEWAY_HEADER_SIZE = struct.calcsize(GATEWAY_HEADER_FORMAT)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Quarantine a bad frame into the DLQ (Section 3.5)
# ═══════════════════════════════════════════════════════════════════════════════
async def _quarantine_frame(
    raw_frame: bytes,
    reason: RejectionReason,
    gateway_id: Optional[int],
    source_ip: Optional[str],
    node_id_raw: Optional[int] = None,
) -> None:
    await database.execute(
        """
        INSERT INTO quarantine_telemetry
            (raw_payload, rejection_reason, gateway_id, source_ip, node_id_raw)
        VALUES (:payload, :reason, :gw, :ip, :nid)
        """,
        {
            "payload": raw_frame,
            "reason": reason.value,
            "gw": gateway_id,
            "ip": source_ip,
            "nid": node_id_raw,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Append a record to the SHA-256 audit ledger (Section 8.5)
# ═══════════════════════════════════════════════════════════════════════════════
async def _append_audit(payload_type: str, payload_data: dict) -> str:
    import hashlib
    last = await database.fetch_one(
        "SELECT block_hash FROM audit_ledger ORDER BY id DESC LIMIT 1"
    )
    prev_hash = last["block_hash"] if last else "0" * 64
    ts = datetime.now(timezone.utc).isoformat()
    content = f"{prev_hash}|{ts}|{payload_type}|{json.dumps(payload_data, sort_keys=True, default=str)}"
    block_hash = hashlib.sha256(content.encode()).hexdigest()
    await database.execute(
        """
        INSERT INTO audit_ledger (previous_hash, block_hash, payload_type, payload_data)
        VALUES (:ph, :bh, :pt, :pd)
        """,
        {
            "ph": prev_hash,
            "bh": block_hash,
            "pt": payload_type,
            "pd": json.dumps(payload_data, default=str),
        },
    )
    return block_hash


# ═══════════════════════════════════════════════════════════════════════════════
# POST /telemetry/binary-batch
# Sections 3.1, 3.2, 3.3, 3.4, 3.5, 4.2, 8.5
# ═══════════════════════════════════════════════════════════════════════════════
@router.post(
    "/binary-batch",
    response_model=BatchIngestionResponse,
    summary="LoRa Gateway Binary Batch Endpoint (Section 3.2)",
    description="""
    Accepts a raw binary payload from LoRa concentrator gateways (SX1302/SX1303).

    Payload structure:
    - 4-byte gateway header: [gateway_id uint16][frame_count uint16]
    - N × 20-byte telemetry frames in '<HHhhBBHHHHbBH' format

    Security: requires valid HMAC-SHA256 in X-Signature-SHA256 header.
    Target: < 0.5 ms per frame (Section 11 SLA).
    """,
)
async def receive_binary_batch(
    request: Request,
    raw_body: bytes = Depends(require_gateway_hmac),  # Step 1 & 3: HMAC verified
    x_gateway_epoch: str = Header(
        ...,
        description="UTC ISO-8601 timestamp of gateway's last NTP sync (Section 3.3)"
    ),
) -> BatchIngestionResponse:
    t_start = time.perf_counter()
    source_ip = request.client.host if request.client else "unknown"

    # ── Parse gateway epoch anchor (Section 3.3) ──────────────────────────────
    try:
        gateway_epoch = datetime.fromisoformat(x_gateway_epoch.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Gateway-Epoch must be ISO-8601 UTC (e.g. 2026-09-04T00:00:00Z)",
        )

    # ── Parse 4-byte gateway header (Section 3.2) ────────────────────────────
    if len(raw_body) < GATEWAY_HEADER_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payload too short — minimum {GATEWAY_HEADER_SIZE} bytes for gateway header",
        )

    gateway_id, frame_count_declared = struct.unpack_from(GATEWAY_HEADER_FORMAT, raw_body, 0)
    frame_data = raw_body[GATEWAY_HEADER_SIZE:]

    # Validate declared vs actual frame count
    actual_frame_count = len(frame_data) // FRAME_SIZE
    if actual_frame_count != frame_count_declared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Frame count mismatch: header declares {frame_count_declared} frames "
                f"but payload contains {actual_frame_count} complete frames "
                f"({len(frame_data)} bytes / {FRAME_SIZE} bytes per frame)"
            ),
        )

    redis = await get_redis()
    now_utc = datetime.now(timezone.utc)

    # Counters for response
    accepted = quarantined = deduplicated = backfilled = 0
    backfill_alarms_suppressed = 0
    audit_batch: list[dict] = []

    # ── Process each 20-byte frame (Section 3.1) ─────────────────────────────
    for i in range(frame_count_declared):
        offset = i * FRAME_SIZE
        raw_frame = frame_data[offset : offset + FRAME_SIZE]

        if len(raw_frame) != FRAME_SIZE:
            await _quarantine_frame(raw_frame, RejectionReason.MALFORMED_FRAME, gateway_id, source_ip)
            quarantined += 1
            continue

        # Step 4: Unpack binary frame
        (
            node_id,
            epoch_offset_s,
            pitch_raw,
            roll_raw,
            vwc_pct,
            battery_v_raw,
            pore_pressure_raw,
            ae_count,
            vpp_mv,
            temp_c,
            status_flags_raw,
            crc16_received,
        ) = struct.unpack(FRAME_FORMAT, raw_frame)

        # Step 5: CRC-16 check (Section 3.1) — verify bytes 0..17
        crc16_computed = _crc16(raw_frame[:18])
        if crc16_computed != crc16_received:
            await _quarantine_frame(
                raw_frame, RejectionReason.CRC_FAIL, gateway_id, source_ip, node_id
            )
            quarantined += 1
            continue

        # Step 6: Schema & range clamping (Section 3.4 anti-poisoning)
        pitch_deg = pitch_raw / 100.0
        roll_deg = roll_raw / 100.0
        battery_v = (battery_v_raw / 100.0) + 2.0
        pore_pressure_kpa = pore_pressure_raw / 10.0

        range_ok = (
            -90.0 <= pitch_deg <= 90.0
            and -90.0 <= roll_deg <= 90.0
            and 0 <= vwc_pct <= 100
            and 1.8 <= battery_v <= 4.55
        )
        if not range_ok:
            await _quarantine_frame(
                raw_frame, RejectionReason.SCHEMA_RANGE, gateway_id, source_ip, node_id
            )
            quarantined += 1
            continue

        # Step 7: Epoch anchoring (Section 3.3)
        # TrueTimestamp = GatewayHourlySyncEpoch + NodeEpochOffset
        true_timestamp = gateway_epoch + timedelta(seconds=epoch_offset_s)

        # Flag for clock resync if offset > 3600s (Section 3.3)
        if epoch_offset_s > settings.MAX_EPOCH_OFFSET_SECONDS:
            await redis.setex(f"clock_resync:{node_id}", 86400, "1")

        # Step 8: Deduplication (Section 3.4)
        # Redis key TTL 120s: SET telemetry:dedup:{node_id}:{sequence_id} EX 120 NX
        # sequence_id keyed by epoch_offset_s and ae_count
        seq_id = (epoch_offset_s << 16) | (ae_count & 0xFFFF)
        dedup_key = f"telemetry:dedup:{node_id}:{seq_id}"
        was_new = await redis.set(dedup_key, "1", ex=settings.DEDUP_TTL_SECONDS, nx=True)
        if not was_new:
            deduplicated += 1
            continue

        # Step 9: Backfill detection (Section 4.2)
        # Packets older than 5 min are historical — must NEVER trigger live actuations
        age_seconds = (now_utc - true_timestamp).total_seconds()
        is_backfilled = age_seconds > settings.BACKFILL_THRESHOLD_SECONDS
        if is_backfilled:
            backfilled += 1
            backfill_alarms_suppressed += 1

        # Step 10: Decode status flags byte (Section 3.1)
        brittle_trip = bool(status_flags_raw & 0b00000001)
        solar_active = bool(status_flags_raw & 0b00000010)
        power_mode = (status_flags_raw >> 2) & 0b11
        consensus_flag = bool(status_flags_raw & 0b00010000)

        # Step 11: Insert into telemetry_readings
        await database.execute(
            """
            INSERT INTO telemetry_readings (
                sensor_id, recorded_at, received_at, is_backfilled,
                pitch, roll, vwc_pct, pore_pressure,
                ae_count, vpp_mv, brittle_trip,
                battery_v, internal_temp_c,
                solar_active, consensus_flag, power_mode,
                sequence_id, data_provenance
            ) VALUES (
                :sensor_id, :recorded_at, NOW(), :is_backfilled,
                :pitch, :roll, :vwc_pct, :pore_pressure,
                :ae_count, :vpp_mv, :brittle_trip,
                :battery_v, :internal_temp_c,
                :solar_active, :consensus_flag, :power_mode,
                :sequence_id, 'DIRECT'
            )
            """,
            {
                "sensor_id": str(node_id),
                "recorded_at": true_timestamp,
                "is_backfilled": is_backfilled,
                "pitch": pitch_deg,
                "roll": roll_deg,
                "vwc_pct": float(vwc_pct),
                "pore_pressure": pore_pressure_kpa,
                "ae_count": ae_count,
                "vpp_mv": vpp_mv,
                "brittle_trip": brittle_trip,
                "battery_v": battery_v,
                "internal_temp_c": float(temp_c),
                "solar_active": solar_active,
                "consensus_flag": consensus_flag,
                "power_mode": power_mode,
                "sequence_id": seq_id,
            },
        )

        # Audit batch accumulate (write as single batch event for efficiency)
        audit_batch.append({
            "node_id": node_id,
            "recorded_at": true_timestamp.isoformat(),
            "pitch": pitch_deg,
            "vwc_pct": vwc_pct,
            "brittle_trip": brittle_trip,
            "is_backfilled": is_backfilled,
        })

        accepted += 1

    # Write batch audit entry (Section 8.5) — one ledger block per batch
    if audit_batch:
        await _append_audit(
            "TELEMETRY",
            {
                "gateway_id": gateway_id,
                "frames_accepted": accepted,
                "frames_quarantined": quarantined,
                "sample": audit_batch[:3],   # Include first 3 frames as evidence
            },
        )

    elapsed_ms = (time.perf_counter() - t_start) * 1000

    return BatchIngestionResponse(
        gateway_id=gateway_id,
        frames_received=frame_count_declared,
        frames_accepted=accepted,
        frames_quarantined=quarantined,
        frames_deduplicated=deduplicated,
        frames_backfilled=backfilled,
        backfill_alarms_suppressed=backfill_alarms_suppressed,
        processing_ms=round(elapsed_ms, 3),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# POST /telemetry/ — JSON fallback (backward compatible, kept for dev testing)
# ═══════════════════════════════════════════════════════════════════════════════
@router.post("/", summary="JSON Telemetry Fallback (Development / HTTP sensors)")
async def receive_telemetry(
    payload: TelemetryPayload,
    _: None = Depends(verify_api_key),
):
    """
    JSON telemetry ingestion — kept for sensors that cannot use binary LoRa protocol.
    For production LoRa deployments, use POST /telemetry/binary-batch.
    """
    await database.execute(
        """
        INSERT INTO telemetry_readings (
            sensor_id, recorded_at,
            pitch, roll, tilt_velocity,
            vwc_pct, pore_pressure, matric_suction,
            apparent_resistivity, ae_count, vpp_mv, brittle_trip,
            delta_x_mm, delta_y_mm, delta_z_mm,
            battery_v, battery_soc_pct, solar_vpv, internal_temp_c,
            rssi_dbm, snr_db, sequence_id, edge_anomaly_score,
            fbg_micro_strain, fbg_load_kn,
            ax, ay, az, wx, wy, wz, rms_vibration,
            data_provenance
        ) VALUES (
            :sensor_id, :recorded_at,
            :pitch, :roll, :tilt_velocity,
            :vwc_pct, :pore_pressure, :matric_suction,
            :apparent_resistivity, :ae_count, :vpp_mv, :brittle_trip,
            :delta_x_mm, :delta_y_mm, :delta_z_mm,
            :battery_v, :battery_soc_pct, :solar_vpv, :internal_temp_c,
            :rssi_dbm, :snr_db, :sequence_id, :edge_anomaly_score,
            :fbg_micro_strain, :fbg_load_kn,
            :ax, :ay, :az, :wx, :wy, :wz, :rms_vibration,
            'DIRECT'
        )
        """,
        payload.model_dump(),
    )
    return {"status": "received", "sensor_id": payload.sensor_id}


# ═══════════════════════════════════════════════════════════════════════════════
# GET /telemetry/sensors — Sensor registry list
# ═══════════════════════════════════════════════════════════════════════════════
@router.get(
    "/sensors",
    summary="List all registered sensors with burn-in status",
    dependencies=[Depends(get_current_user)],
)
async def list_sensors():
    rows = await database.fetch_all(
        """
        SELECT
            s.id, s.sensor_id, s.sensor_type, s.gateway_id,
            s.active_status,
            s.burn_in_expires_at,
            (s.burn_in_expires_at IS NOT NULL AND s.burn_in_expires_at > NOW()) AS is_burn_in_mode,
            s.created_at
        FROM sensors s
        ORDER BY s.id
        """
    )
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# GET /telemetry/sensor-health — Hardware health dashboard (Section 2.1)
# ═══════════════════════════════════════════════════════════════════════════════
@router.get(
    "/sensor-health",
    summary="Per-sensor health: last_seen, battery, RSSI, burn-in status",
    dependencies=[Depends(get_current_user)],
)
async def get_sensor_health():
    rows = await database.fetch_all(
        """
        SELECT
            s.sensor_id,
            s.active_status,
            (s.burn_in_expires_at IS NOT NULL AND s.burn_in_expires_at > NOW()) AS is_burn_in_mode,
            r.recorded_at AS last_seen,
            r.battery_v,
            r.battery_soc_pct,
            r.rssi_dbm,
            rz.current_risk AS last_risk_level
        FROM sensors s
        LEFT JOIN LATERAL (
            SELECT recorded_at, battery_v, battery_soc_pct, rssi_dbm
            FROM telemetry_readings
            WHERE sensor_id = s.sensor_id
            ORDER BY recorded_at DESC
            LIMIT 1
        ) r ON TRUE
        LEFT JOIN risk_zones rz ON rz.h3_r10_cells @> ARRAY[s.corridor_h3_r10]
        ORDER BY s.sensor_id
        """
    )
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# GET /telemetry/quarantine — DLQ forensics (Section 3.5)
# ═══════════════════════════════════════════════════════════════════════════════
@router.get(
    "/quarantine",
    summary="Dead-Letter Queue — corrupted/rejected frames (Section 3.5)",
    dependencies=[Depends(get_current_user)],
)
async def list_quarantine(limit: int = 50, gateway_id: Optional[int] = None):
    base_query = """
        SELECT id, rejection_reason, gateway_id, source_ip, node_id_raw, received_at
        FROM quarantine_telemetry
        {where}
        ORDER BY received_at DESC
        LIMIT :limit
    """
    where = "WHERE gateway_id = :gw" if gateway_id else ""
    rows = await database.fetch_all(
        base_query.format(where=where),
        {"limit": limit, "gw": gateway_id},
    )
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# GET /telemetry/hardware-bridge/status & POST /sync-now
# ═══════════════════════════════════════════════════════════════════════════════
@router.get(
    "/hardware-bridge/status",
    summary="Get live hardware ngrok bridge status & metrics",
)
async def hardware_bridge_status():
    from workers.hardware_ngrok_bridge import get_bridge_status
    return get_bridge_status()


@router.post(
    "/hardware-bridge/sync-now",
    summary="Trigger immediate poll from live ngrok hardware endpoint",
)
async def hardware_bridge_sync_now():
    from workers.hardware_ngrok_bridge import poll_hardware_telemetry_once, get_bridge_status
    count = await poll_hardware_telemetry_once()
    status = get_bridge_status()
    return {
        "status": "SYNC_EXECUTED",
        "new_records_ingested": count,
        "bridge_metrics": status,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GET /telemetry/{sensor_id} — Historical readings
# ═══════════════════════════════════════════════════════════════════════════════
@router.get(
    "/{sensor_id}",
    summary="Last N telemetry readings for a sensor",
    dependencies=[Depends(get_current_user)],
)
async def get_sensor_history(sensor_id: str, limit: int = 50):
    rows = await database.fetch_all(
        """
        SELECT
            recorded_at, pitch, roll, tilt_velocity,
            vwc_pct, pore_pressure, ae_count, vpp_mv, brittle_trip,
            battery_v, rssi_dbm, snr_db, is_backfilled, data_provenance
        FROM telemetry_readings
        WHERE sensor_id = :sensor_id
        ORDER BY recorded_at DESC
        LIMIT :limit
        """,
        {"sensor_id": sensor_id, "limit": limit},
    )
    return {"sensor_id": sensor_id, "readings": [dict(r) for r in rows]}
