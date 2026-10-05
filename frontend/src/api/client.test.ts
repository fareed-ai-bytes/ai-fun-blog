import { describe, expect, it, vi } from 'vitest';

import { ApiError, apiRequest, fieldErrors, withQuery } from './client';

function mockFetch(status: number, body: unknown) {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(body === undefined ? null : JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

describe('apiRequest', () => {
  it('sends cookies and a JSON content type, and returns the parsed body', async () => {
    const fetchMock = mockFetch(200, { status: 'ok' });
    const result = await apiRequest<{ status: string }>('/api/v1/health', {
      method: 'POST',
      body: '{}',
    });
    expect(result).toEqual({ status: 'ok' });
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.credentials).toBe('include');
    expect(new Headers(init.headers).get('Content-Type')).toBe('application/json');
  });

  it('returns undefined for 204 No Content', async () => {
    mockFetch(204, undefined);
    await expect(apiRequest('/api/v1/auth/logout')).resolves.toBeUndefined();
  });

  it('turns the error envelope into a typed ApiError', async () => {
    mockFetch(404, { error: { code: 'POST_NOT_FOUND', message: 'Post not found', details: null } });
    const error = await apiRequest('/api/v1/posts/x').catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 404, code: 'POST_NOT_FOUND', message: 'Post not found' });
  });

  it('handles a non-envelope error body', async () => {
    mockFetch(502, { unexpected: true });
    await expect(apiRequest('/api/v1/posts')).rejects.toMatchObject({
      status: 502,
      code: 'HTTP_ERROR',
    });
  });

  it('reports network failures as NETWORK_ERROR', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    await expect(apiRequest('/api/v1/posts')).rejects.toMatchObject({
      status: 0,
      code: 'NETWORK_ERROR',
    });
  });
});

describe('fieldErrors', () => {
  it('maps 422 details to field messages', () => {
    const error = new ApiError(422, 'VALIDATION_ERROR', 'Invalid input', [
      { field: 'password', message: 'Too short' },
    ]);
    expect(fieldErrors(error)).toEqual({ password: 'Too short' });
  });

  it('maps a 409 conflict to its field', () => {
    const error = new ApiError(409, 'EMAIL_TAKEN', 'Email already used', { field: 'email' });
    expect(fieldErrors(error)).toEqual({ email: 'Email already used' });
  });

  it('returns nothing for other errors', () => {
    expect(fieldErrors(new Error('boom'))).toEqual({});
  });
});

describe('withQuery', () => {
  it('skips empty values', () => {
    expect(withQuery('/api/v1/posts', { page: 2, author: undefined, q: '' })).toBe(
      '/api/v1/posts?page=2',
    );
  });
});
