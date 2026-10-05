import { apiRequest } from './client';
import type { LikeState } from './types';

export function likePost(postId: string): Promise<LikeState> {
  return apiRequest<LikeState>(`/api/v1/posts/${postId}/like`, { method: 'PUT' });
}

export function unlikePost(postId: string): Promise<LikeState> {
  return apiRequest<LikeState>(`/api/v1/posts/${postId}/like`, { method: 'DELETE' });
}
