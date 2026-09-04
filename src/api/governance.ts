/**
 * SafeSlope-NER — Governance API (Evacuation Orders & Audit Ledger)
 */
import { apiRequest } from './client';

export interface DraftOrderPayload {
  zone_id: number;
  lgd_district_code: string;
  affected_population: number;
  detour_route_description?: string;
  sunset_gating_check?: boolean;
  isolation_event_id?: number;
  lgd_state_code?: string;
}

export interface AuthorizeOrderPayload {
  order_id: number;
  authorized_by: string;
  dm_pin: string;
}

export interface AuthorizeOrderResponse {
  status: string;
  order_id: number;
  authorized_by: string;
  lora_barrier_dropped: boolean;
  scada_grid_islanded: boolean;
  cap_dispatched: boolean;
  total_execution_ms: number;
  audit_ledger_status: string;
}

export interface AuditBlock {
  id: number;
  previous_hash: string;
  block_hash: string;
  payload_type: string;
  payload_data: string;
  created_at: string;
}

export async function draftEvacuationOrder(
  payload: DraftOrderPayload
): Promise<unknown> {
  return apiRequest('/governance/orders/draft', {
    method: 'POST',
    body: payload,
  });
}

export async function authorizeEvacuationOrder(
  payload: AuthorizeOrderPayload
): Promise<AuthorizeOrderResponse> {
  return apiRequest<AuthorizeOrderResponse>('/governance/orders/authorize', {
    method: 'POST',
    body: payload,
  });
}

export async function getAuditBlocks(limit = 25): Promise<AuditBlock[]> {
  return apiRequest<AuditBlock[]>(`/governance/audit-ledger/blocks?limit=${limit}`);
}

export async function verifyAuditLedger(): Promise<unknown> {
  return apiRequest('/governance/audit-ledger/verify');
}
