/**
 * SafeSlope-NER — Telemetry API
 */
import { apiRequest } from './client';

export interface SensorHealth {
  sensor_id: string;
  active_status: boolean;
  is_burn_in_mode: boolean;
  last_seen: string | null;
  battery_v: number | null;
  battery_soc_pct: number | null;
  rssi_dbm: number | null;
  last_risk_level: string | null;
}

export interface TelemetryReading {
  recorded_at: string;
  pitch: number | null;
  roll: number | null;
  tilt_velocity: number | null;
  vwc_pct: number | null;
  pore_pressure: number | null;
  ae_count: number | null;
  vpp_mv: number | null;
  brittle_trip: boolean | null;
  battery_v: number | null;
  rssi_dbm: number | null;
  snr_db: number | null;
  is_backfilled: boolean;
  data_provenance: string;
}

export interface SensorHistoryResponse {
  sensor_id: string;
  readings: TelemetryReading[];
}

export async function getSensorHealth(): Promise<SensorHealth[]> {
  return apiRequest<SensorHealth[]>('/telemetry/sensor-health');
}

export async function getSensorHistory(
  sensorId: string,
  limit = 50
): Promise<SensorHistoryResponse> {
  return apiRequest<SensorHistoryResponse>(`/telemetry/${encodeURIComponent(sensorId)}?limit=${limit}`);
}

export async function triggerHardwareSync(): Promise<unknown> {
  return apiRequest('/telemetry/hardware-bridge/sync-now', { method: 'POST' });
}

export async function getHardwareBridgeStatus(): Promise<unknown> {
  return apiRequest('/telemetry/hardware-bridge/status');
}
