/**
 * SafeSlope-NER — Auth API
 * Handles demo login (role-based), token management, and session restore.
 */
import { apiRequest, setToken, clearToken, getToken } from './client';
import type { UserProfile } from '../types/dashboard';

export interface DemoLoginPayload {
  portal_type: 'user' | 'admin';
  persona: 'resident' | 'tourist' | 'head_admin' | 'role_admin';
  sub_role?: string;
  email?: string;
  name?: string;
  district?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    email: string;
    name: string;
    role: string;
    sub_role?: string;
    persona?: string;
    portal_type?: string;
    district_or_corridor?: string;
  };
}

export async function demoLogin(payload: DemoLoginPayload): Promise<LoginResponse> {
  const res = await apiRequest<LoginResponse>('/auth/demo-login', {
    method: 'POST',
    body: payload,
    anonymous: true,
  });
  setToken(res.access_token);
  return res;
}

export async function getMe(): Promise<LoginResponse['user'] | null> {
  const token = getToken();
  if (!token) return null;
  try {
    return await apiRequest<LoginResponse['user']>('/auth/me');
  } catch {
    clearToken();
    return null;
  }
}

export function logout(): void {
  clearToken();
}

/** Map backend user response to frontend UserProfile shape */
export function mapToUserProfile(user: LoginResponse['user']): UserProfile {
  const initials = (user.name ?? 'U')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return {
    name: user.name,
    email: user.email,
    portalType: (user.portal_type as UserProfile['portalType']) ?? 'user',
    persona: (user.persona as UserProfile['persona']) ?? 'resident',
    subRole: user.sub_role,
    districtOrCorridor: user.district_or_corridor ?? 'NER Corridor',
    initials,
  };
}
