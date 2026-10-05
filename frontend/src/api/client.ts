// Single fetch wrapper for the whole app (architecture.md: frontend/src/api/client.ts).
// Always sends the auth cookie; turns the error envelope into a typed ApiError.

export interface ErrorEnvelope {
  error: { code: string; message: string; details: unknown };
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown;

  constructor(status: number, code: string, message: string, details: unknown = null) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function isErrorEnvelope(value: unknown): value is ErrorEnvelope {
  if (typeof value !== 'object' || value === null || !('error' in value)) return false;
  const inner: unknown = value.error;
  return typeof inner === 'object' && inner !== null && 'code' in inner && 'message' in inner;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  const response = await fetch(path, { ...init, headers, credentials: 'include' });

  if (response.status === 204) return undefined as T;
  const body: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    if (isErrorEnvelope(body)) {
      const { code, message, details } = body.error;
      throw new ApiError(response.status, code, message, details);
    }
    throw new ApiError(response.status, 'HTTP_ERROR', `Request failed (${response.status})`);
  }
  return body as T;
}
