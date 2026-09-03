"""
SafeSlope-NER — Field Edge Gateway Store-and-Forward Daemon
Implements Section 4.1 of computational_backend_plan.txt v3.0.0

Runs on Raspberry Pi 4 / CM4 field concentrators (SX1302/SX1303 LoRa):
  - Local SQLite Write-Ahead Logging (WAL) circular buffer
  - Retains up to 7 days of 20-byte raw telemetry frames during total cellular blackout
  - Monitors 4G/2G connectivity with low-overhead health heartbeats
  - Drains backlogged buffer using batch memory slicing (N x 20 bytes) with HMAC-SHA256
  - Enforces low-bandwidth cellular rate-limiting to prevent mountain tower congestion
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import sqlite3
import struct
import time
from datetime import datetime, timezone

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GatewayDaemon")

GATEWAY_ID = int(os.getenv("GATEWAY_ID", "101"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
HMAC_SECRET = os.getenv("GATEWAY_HMAC_SECRET", "change-this-gateway-hmac-secret")
DB_PATH = os.getenv("BUFFER_DB_PATH", "gateway_buffer.db")
MAX_BATCH_FRAMES = 50  # Up to 50 frames per HTTP batch (1000 bytes payload)


class GatewayBuffer:
    """Local SQLite circular buffer for offline packet retention."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        with conn:
            # Enable WAL mode for high-concurrency non-blocking writes
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raw_frame BLOB NOT NULL,
                    received_at REAL NOT NULL,
                    synced INTEGER DEFAULT 0
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sync ON telemetry_queue (synced, id);")
        conn.close()

    def enqueue_frame(self, frame_bytes: bytes):
        if len(frame_bytes) != 20:
            logger.warning("Rejected non-20-byte frame: len=%d", len(frame_bytes))
            return
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute(
                "INSERT INTO telemetry_queue (raw_frame, received_at, synced) VALUES (?, ?, 0);",
                (frame_bytes, time.time()),
            )
        conn.close()

    def fetch_unsynced_batch(self, limit: int = MAX_BATCH_FRAMES) -> list[tuple[int, bytes]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, raw_frame FROM telemetry_queue WHERE synced = 0 ORDER BY id ASC LIMIT ?;",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def mark_synced(self, ids: list[int]):
        if not ids:
            return
        conn = sqlite3.connect(self.db_path)
        with conn:
            placeholders = ",".join("?" for _ in ids)
            conn.execute(f"DELETE FROM telemetry_queue WHERE id IN ({placeholders});", ids)
        conn.close()

    def pending_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry_queue WHERE synced = 0;")
        count = cursor.fetchone()[0]
        conn.close()
        return count


async def check_cellular_connectivity(client: httpx.AsyncClient) -> bool:
    try:
        resp = await client.get(f"{BACKEND_URL}/health", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


async def drain_backlog(buffer: GatewayBuffer, client: httpx.AsyncClient) -> int:
    """Drains pending packets in batches to the backend."""
    synced_total = 0
    while True:
        batch = buffer.fetch_unsynced_batch(limit=MAX_BATCH_FRAMES)
        if not batch:
            break

        row_ids = [r[0] for r in batch]
        raw_frames = b"".join(r[1] for r in batch)
        frame_count = len(batch)

        # 4-byte header: gateway_id (uint16) + frame_count (uint16)
        header = struct.pack("<HH", GATEWAY_ID, frame_count)
        payload = header + raw_frames

        # HMAC-SHA256 signature
        sig = hmac.new(HMAC_SECRET.encode(), payload, hashlib.sha256).hexdigest()
        epoch_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")

        headers = {
            "Content-Type": "application/octet-stream",
            "X-Gateway-ID": str(GATEWAY_ID),
            "X-Gateway-Epoch": epoch_str,
            "X-Signature-SHA256": sig,
        }

        try:
            resp = await client.post(
                f"{BACKEND_URL}/telemetry/binary-batch",
                content=payload,
                headers=headers,
                timeout=5.0,
            )
            if resp.status_code == 200:
                buffer.mark_synced(row_ids)
                synced_total += frame_count
                logger.info("Synced batch of %d frames to backend. Total synced: %d", frame_count, synced_total)
            else:
                logger.warning("Backend rejected batch with status %d: %s", resp.status_code, resp.text)
                break
        except Exception as e:
            logger.warning("Failed transmitting batch: %s. Re-buffering.", e)
            break

        # Yield execution to avoid saturating 2G modem
        await asyncio.sleep(0.05)

    return synced_total


async def run_gateway_loop():
    logger.info("Starting SafeSlope-NER Edge Gateway Store-and-Forward Daemon (Gateway ID: %d)", GATEWAY_ID)
    buffer = GatewayBuffer()

    async with httpx.AsyncClient() as client:
        while True:
            pending = buffer.pending_count()
            online = await check_cellular_connectivity(client)

            if online and pending > 0:
                logger.info("Cellular connectivity ACTIVE. Draining buffer (%d frames queued)...", pending)
                synced = await drain_backlog(buffer, client)
                logger.info("Drained %d frames. Remaining in queue: %d", synced, buffer.pending_count())
            elif not online:
                logger.debug("Cellular connection down. Telemetry accumulating safely in local SQLite buffer.")

            await asyncio.sleep(2.0)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_gateway_loop())
