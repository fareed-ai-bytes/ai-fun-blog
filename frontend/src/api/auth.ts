import { ApiError, apiRequest, jsonBody } from './client';
import type { LoginInput, Me, RegisterInput } from './types';

/** The current user, or null when not logged in (401 is an expected answer here). */
export async function getMe(): Promise<Me | null> {
  try {
    return await apiRequest<Me>('/api/v1/auth/me');
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null;
    throw error;
  }
}

export function register(input: RegisterInput): Promise<Me> {
  return apiRequest<Me>('/api/v1/auth/register', { method: 'POST', ...jsonBody(input) });
}

export function login(input: LoginInput): Promise<Me> {
  return apiRequest<Me>('/api/v1/auth/login', { method: 'POST', ...jsonBody(input) });
}

export function logout(): Promise<void> {
  return apiRequest<void>('/api/v1/auth/logout', { method: 'POST' });
}
