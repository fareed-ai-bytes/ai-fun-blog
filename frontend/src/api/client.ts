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
    this.name = 'ApiError';
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

export type QueryParams = Record<string, string | number | undefined | null>;

export function withQuery(path: string, params: QueryParams): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  let response: Response;
  try {
    response = await fetch(path, { ...init, headers, credentials: 'include' });
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', 'Could not reach the server. Check your connection.');
  }

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

export function jsonBody(value: unknown): RequestInit {
  return { body: JSON.stringify(value) };
}

/** Field → message map from a 422 (`details: [{field, message}]`) or 409 (`details: {field}`). */
export function fieldErrors(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError)) return {};
  const { details } = error;
  const result: Record<string, string> = {};
  if (Array.isArray(details)) {
    for (const item of details as unknown[]) {
      if (typeof item === 'object' && item !== null && 'field' in item && 'message' in item) {
        const field = String(item.field);
        if (field && !(field in result)) result[field] = String(item.message);
      }
    }
  } else if (typeof details === 'object' && details !== null && 'field' in details) {
    result[String(details.field)] = error.message;
  }
  return result;
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}
