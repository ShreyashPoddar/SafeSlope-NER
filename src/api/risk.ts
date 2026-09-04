/**
 * SafeSlope-NER — Risk Zones API
 */
import { apiRequest } from './client';

export interface RiskZoneBackend {
  id: number;
  zone_name: string;
  corridor_code: string;
  lgd_district_code: string;
  current_risk: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | null;
  operational_tier: number | null;
  ml_risk_pct: number | null;
  ml_confidence_pct: number | null;
  fos_value: number | null;
  shap_drivers: string | null;
  weather_source: string | null;
  updated_at: string | null;
}

export interface RiskStateEntry {
  id: number;
  zone_name: string;
  current_risk: string | null;
  operational_tier: number | null;
  ml_risk_pct: number | null;
  ml_confidence_pct: number | null;
  fos_value: number | null;
  updated_at: string | null;
}

export async function getRiskZones(): Promise<RiskZoneBackend[]> {
  return apiRequest<RiskZoneBackend[]>('/risk-zones');
}

export async function getRiskState(): Promise<Record<string, RiskStateEntry>> {
  return apiRequest<Record<string, RiskStateEntry>>('/risk-state');
}

export async function getRiskZone(zoneId: number): Promise<unknown> {
  return apiRequest(`/risk-zones/${zoneId}`);
}
