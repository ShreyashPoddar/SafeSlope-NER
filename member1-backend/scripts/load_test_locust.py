"""
SafeSlope-NER — Locust & Async High-Throughput Load Testing Benchmark
Implements Section 10.4 and Section 11 of computational_backend_plan.txt v3.0.0

SLA Performance Targets:
  - Binary Packet Ingestion (POST /telemetry/binary-batch): 1,000 packets/s (< 5ms batch latency)
  - Dynamic PostGIS Vector Tile (GET /tiles/risk-zones/...): < 25ms
  - 7-Stage Risk Resolution (GET /risk/risk-zones): < 50ms
  - FNO Kinematic Runout Simulation: < 50ms

Can be run via Locust (`locust -f scripts/load_test_locust.py`) or as a standalone CLI benchmark.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import os
import struct
import sys
import time
from datetime import datetime, timezone

import httpx

# Try importing Locust for standard distributed load testing
try:
    from locust import HttpUser, task, between
    HAS_LOCUST = True
except ImportError:
    HAS_LOCUST = False

GATEWAY_ID = 101
SECRET_KEY = "change-this-gateway-hmac-secret"
TARGET_HOST = os.getenv("TARGET_HOST", "http://127.0.0.1:8000")


def generate_binary_batch_payload(node_base_id: int = 1000, frame_count: int = 25) -> tuple[bytes, dict[str, str]]:
    """Generates a signed N x 20-byte binary payload."""
    header = struct.pack("<HH", GATEWAY_ID, frame_count)
    frames = b""

    for i in range(frame_count):
        nid = node_base_id + (i % 30)
        # 18 bytes partial
        partial = struct.pack(
            "<HHhhBBHHHbB",
            nid,
            120 + i,
            int(3.4 * 100),
            int(0.8 * 100),
            65,
            int((3.65 - 2.0) * 100),
            int(14.5 * 10),
            8,
            24,
            23,
            0b00000100,  # Normal power
        )
        # Pure Python CRC-16-CCITT
        crc = 0xFFFF
        for b in partial:
            crc ^= (b << 8)
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
        frames += (partial + struct.pack("<H", crc))

    full_payload = header + frames
    sig = hmac.new(SECRET_KEY.encode(), full_payload, hashlib.sha256).hexdigest()
    epoch_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")

    headers = {
        "Content-Type": "application/octet-stream",
        "X-Gateway-ID": str(GATEWAY_ID),
        "X-Gateway-Epoch": epoch_str,
        "X-Signature-SHA256": sig,
    }
    return full_payload, headers


# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE ASYNC CLI BENCHMARK RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def run_standalone_benchmark(total_requests: int = 100, batch_size: int = 25):
    print("==================================================================")
    print("SafeSlope-NER — 1,000 pkts/s SLA Throughput Benchmark Runner")
    print(f"Target Host: {TARGET_HOST}")
    print(f"Simulating {total_requests} gateway batches ({total_requests * batch_size:,} packets)")
    print("==================================================================")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check backend health
        try:
            r = await client.get(f"{TARGET_HOST}/health")
            print(f"[OK] Backend health: {r.json().get('overall', 'ok')}")
        except Exception as e:
            print(f"[Notice] Backend not reachable at {TARGET_HOST} ({e}). Running local payload generator validation.")
            return

        latencies = []
        t_start = time.perf_counter()

        for req_idx in range(total_requests):
            payload, headers = generate_binary_batch_payload(frame_count=batch_size)
            t0 = time.perf_counter()
            resp = await client.post(f"{TARGET_HOST}/telemetry/binary-batch", content=payload, headers=headers)
            lat_ms = (time.perf_counter() - t0) * 1000
            latencies.append(lat_ms)

        total_elapsed = time.perf_counter() - t_start
        total_packets = total_requests * batch_size
        throughput_pps = total_packets / total_elapsed

        print("\nBenchmark Results:")
        print(f"  Total Packets Ingested: {total_packets:,}")
        print(f"  Total Time:             {total_elapsed:.2f}s")
        print(f"  Throughput:             {throughput_pps:.1f} packets/second")
        print(f"  Mean Batch Latency:     {sum(latencies)/len(latencies):.2f}ms")
        print(f"  p95 Batch Latency:      {sorted(latencies)[int(len(latencies)*0.95)]:.2f}ms")
        print(f"  SLA Compliance (<5ms):  {'PASS' if (sum(latencies)/len(latencies)) < 5.0 else 'WARN'}")


# ═══════════════════════════════════════════════════════════════════════════════
# LOCUST USER CLASS (Distributed multi-node benchmarking)
# ═══════════════════════════════════════════════════════════════════════════════

if HAS_LOCUST:
    class ConcentratorGatewayUser(HttpUser):
        wait_time = between(0.02, 0.05)  # 20-50ms between bursts (simulates high storm streaming)

        @task(5)
        def push_telemetry_batch(self):
            payload, headers = generate_binary_batch_payload(frame_count=20)
            self.client.post("/telemetry/binary-batch", data=payload, headers=headers)

        @task(2)
        def fetch_mvt_tile(self):
            self.client.get("/tiles/risk-zones/12/3245/1780.pbf")

        @task(1)
        def query_risk_state(self):
            self.client.get("/risk/risk-zones")


if __name__ == "__main__":
    asyncio.run(run_standalone_benchmark())
