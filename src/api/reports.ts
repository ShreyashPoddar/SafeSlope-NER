/**
 * SafeSlope-NER — Reports API (Citizen Hazard Reports)
 */
import { apiRequest } from './client';

export interface ReportSubmitPayload {
  submitter_phone: string;
  submitter_role: 'citizen' | 'highway_patrol' | 'aapda_mitra';
  latitude: number;
  longitude: number;
  image_url: string;
  description?: string;
}

export interface ReportSubmitResponse {
  status: string;
  report_id: number;
  classification: string;
  confidence_pct: number;
  metric_crack_width_cm: number | null;
  aapda_mitra_alerted: boolean;
}

export interface ReportListItem {
  id: number;
  report_uuid: string;
  submitter_role: string;
  latitude: number;
  longitude: number;
  ai_classification: string;
  ai_confidence_pct: number;
  crack_width_cm: number | null;
  crack_length_m: number | null;
  cvi_delta: number;
  verified_by_volunteer: boolean;
  submitted_at: string;
}

export async function submitReport(
  payload: ReportSubmitPayload
): Promise<ReportSubmitResponse> {
  return apiRequest<ReportSubmitResponse>('/reports/', {
    method: 'POST',
    body: payload,
  });
}

export async function listReports(limit = 50): Promise<ReportListItem[]> {
  return apiRequest<ReportListItem[]>(`/reports/?limit=${limit}`);
}
