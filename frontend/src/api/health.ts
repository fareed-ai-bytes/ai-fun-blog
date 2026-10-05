import { apiRequest } from './client';

export interface HealthStatus {
  status: string;
}

export function getHealth(): Promise<HealthStatus> {
  return apiRequest<HealthStatus>('/api/v1/health');
}
