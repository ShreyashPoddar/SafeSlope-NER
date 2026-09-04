/**
 * SafeSlope-NER — Central API Client
 * Uses native fetch with Bearer token interceptor.
 * In dev: requests go to /api/* which Vite proxies to http://localhost:8000
 * In production: set VITE_API_BASE_URL=https://your-backend.com
 */

const BASE_URL: string = (import.meta.env.VITE_API_BASE_URL as string) || '/api';

export const TOKEN_KEY = 'safeslope_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  /** If true, skip attaching the Authorization header */
  anonymous?: boolean;
};

export async function apiRequest<T = unknown>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, headers = {}, anonymous = false } = options;

  const allHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (!anonymous) {
    const token = getToken();
    if (token) {
      allHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  const url = path.startsWith('http') ? path : `${BASE_URL}${path}`;

  const res = await fetch(url, {
    method,
    headers: allHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const errJson = await res.json();
      detail = (errJson as { detail?: string })?.detail ?? detail;
    } catch {
      // ignore parse error
    }
    if (res.status === 401) {
      clearToken();
    }
    throw new ApiError(res.status, detail);
  }

  // Some endpoints return 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}
