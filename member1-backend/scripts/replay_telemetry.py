"""
SafeSlope-NER — LoRa Telemetry Replay & Demonstration Tool
Implements Section 3.1, Section 3.2, and Section 10.4 of computational_backend_plan.txt v3.0.0

Generates canonical 20-byte LoRa packets in C-struct format:
  Struct: '<HHhhBBHHHHbBH'
Signs with HMAC-SHA256 and streams to POST /telemetry/binary-batch
to simulate real-time sensor mesh telemetry on road cuttings.
"""
from __future__ import annotations

import hashlib
import hmac
import struct
import time
from datetime import datetime, timezone

try:
    import crcmod
    _crc16_func = crcmod.predefined.mkCrcFun("crc-ccitt-false")
    def compute_crc16(data: bytes) -> int:
        return _crc16_func(data)
except ImportError:
    def compute_crc16(data: bytes) -> int:
        # Pure Python CRC-16-CCITT (polynomial 0x1021, init 0xFFFF)
        crc = 0xFFFF
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc
FRAME_FORMAT = "<HHhhBBHHHHbBH"  # 20 bytes exact


def create_binary_telemetry_frame(
    node_id: int,
    epoch_offset_s: int,
    pitch_deg: float,
    roll_deg: float,
    vwc_pct: int,
    battery_v: float,
    pore_pressure_kpa: float,
    ae_count: int = 0,
    vpp_mv: int = 0,
    temp_c: int = 24,
    brittle_trip: bool = False,
    power_mode: int = 1,
) -> bytes:
    """Encodes sensor metrics into the exact 20-byte LoRa binary packet."""
    pitch_raw = int(pitch_deg * 100)
    roll_raw = int(roll_deg * 100)
    battery_v_raw = int((battery_v - 2.0) * 100)
    pore_raw = int(pore_pressure_kpa * 10)

    # Status flags bit-field
    status_byte = 0
    if brittle_trip:
        status_byte |= 0b00000001
    status_byte |= (power_mode & 0b11) << 2

    # Pack 18 bytes (excluding CRC)
    partial = struct.pack(
        "<HHhhBBHHHbB",
        node_id,
        epoch_offset_s,
        pitch_raw,
        roll_raw,
        vwc_pct,
        battery_v_raw,
        pore_raw,
        ae_count,
        vpp_mv,
        temp_c,
        status_byte,
    )

    # Compute CRC-16-CCITT over the first 18 bytes
    crc_val = compute_crc16(partial)

    # Full 20-byte frame
    return partial + struct.pack("<H", crc_val)


def main():
    print("==================================================================")
    print("SafeSlope-NER — LoRa Telemetry Binary Packet Replay Generator")
    print("==================================================================")
    
    gateway_id = 101
    frame_count = 5
    gateway_epoch = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")
    secret_key = "change-this-gateway-hmac-secret"

    # Gateway header (4 bytes): gateway_id (uint16) + frame_count (uint16)
    header = struct.pack("<HH", gateway_id, frame_count)

    frames_bytes = b""
    for i in range(frame_count):
        f = create_binary_telemetry_frame(
            node_id=1001 + i,
            epoch_offset_s=120 + i * 10,
            pitch_deg=2.4 + (i * 0.3),
            roll_deg=0.8,
            vwc_pct=65,
            battery_v=3.65,
            pore_pressure_kpa=18.4,
            ae_count=12,
            vpp_mv=45,
            temp_c=22,
            brittle_trip=(i == 4),  # Node 5 triggers brittle tripwire!
        )
        frames_bytes += f

    full_payload = header + frames_bytes
    assert len(full_payload) == 4 + (frame_count * 20)

    # Compute HMAC-SHA256 signature
    sig = hmac.new(secret_key.encode(), full_payload, hashlib.sha256).hexdigest()

    print(f"Constructed batch payload: {len(full_payload)} bytes ({frame_count} frames)")
    print(f"X-Signature-SHA256: {sig}")
    print(f"X-Gateway-Epoch:    {gateway_epoch}")
    print("\nPayload is ready for transmission to POST /telemetry/binary-batch.")


if __name__ == "__main__":
    main()
