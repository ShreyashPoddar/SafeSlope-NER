/**
 * SafeSlope-NER — Villages & Isolation API
 */
import { apiRequest } from './client';

export interface Village {
  id: number;
  village_name: string;
  population: number;
}

export interface IsolatedVillage {
  village_name: string;
  population: number;
  zone_id: number;
  detected_at: string;
}

export async function getVillages(): Promise<Village[]> {
  return apiRequest<Village[]>('/villages');
}

export async function getIsolatedVillages(): Promise<IsolatedVillage[]> {
  return apiRequest<IsolatedVillage[]>('/villages/isolated');
}
