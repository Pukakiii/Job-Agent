// Base API client for the frontend. Pure TypeScript, no external deps.

export type ApiError = {
  status: number;
  message: string;
  detail?: unknown;
};

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: ApiError };

  const DEFAULT_BASE =
  process.env.NODE_ENV === "development"
    ? ""
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
function getBaseUrl(): string {
  const env =
    typeof process !== 'undefined'
      ? process.env.NEXT_PUBLIC_API_URL
      : undefined;
  return (env && env.trim().length > 0 ? env : DEFAULT_BASE).replace(
    /\/+$/u,
    '',
  );
}

function buildUrl(path: string): string {
  const base = getBaseUrl();
  // ensure path begins with a slash and prepend /api/v1
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${base}/api/v1${p}`;
}

async function parseJsonSafe(response: Response): Promise<unknown> {
  try {
    // Some 204 responses have no body
    if (response.status === 204) return undefined;
    const text = await response.text();
    if (!text) return undefined;
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

function extractMessageFromDetail(detail: unknown): string {
  if (!detail) return 'Unknown error';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    // fastapi validation errors are arrays of { msg, type }
    const parts: string[] = [];
    for (const item of detail) {
      if (item && typeof item === 'object') {
        const msg = (item as { msg?: unknown }).msg;
        if (typeof msg === 'string') parts.push(msg);
      }
    }
    if (parts.length > 0) return parts.join('; ');
    return JSON.stringify(detail);
  }
  if (typeof detail === 'object') {
    try {
      return JSON.stringify(detail);
    } catch {
      return 'Error';
    }
  }
  return String(detail);
}

export async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<ApiResult<T>> {
  const url = buildUrl(path);
  const baseOptions: RequestInit = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    ...options,
  };

  try {
    const res = await fetch(url, baseOptions);
    if (!res.ok) {
      const payload = await parseJsonSafe(res);
      // Backend uses { detail: string | [{ msg, type }] }
      const detail =
        payload &&
        typeof payload === 'object' &&
        'detail' in (payload as Record<string, unknown>)
          ? (payload as Record<string, unknown>).detail
          : payload;

      const message = extractMessageFromDetail(detail);
      return {
        ok: false,
        error: {
          status: res.status,
          message,
          detail,
        },
      };
    }

    // OK response
    if (res.status === 204) {
      return { ok: true, data: undefined as unknown as T };
    }

    const data = (await parseJsonSafe(res)) as T;
    return { ok: true, data };
  } catch (err) {
    // Network or other unexpected failure
    return {
      ok: false,
      error: {
        status: 0,
        message: 'Network error',
        detail:
          err instanceof Error
            ? { name: err.name, message: err.message }
            : String(err),
      },
    };
  }
}

export function get<T>(path: string): Promise<ApiResult<T>> {
  return apiRequest<T>(path, { method: 'GET' });
}

export function post<T>(path: string, body: unknown): Promise<ApiResult<T>> {
  return apiRequest<T>(path, { method: 'POST', body: JSON.stringify(body) });
}

export function put<T>(path: string, body: unknown): Promise<ApiResult<T>> {
  return apiRequest<T>(path, { method: 'PUT', body: JSON.stringify(body) });
}

export function del<T>(path: string): Promise<ApiResult<T>> {
  return apiRequest<T>(path, { method: 'DELETE' });
}
