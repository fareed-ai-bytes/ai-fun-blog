import { apiRequest, jsonBody, withQuery } from './client';
import type { Page, PostChanges, PostDetail, PostInput, PostSummary } from './types';

export interface FeedParams {
  page: number;
  author?: string;
}

export function listFeed({ page, author }: FeedParams): Promise<Page<PostSummary>> {
  return apiRequest<Page<PostSummary>>(withQuery('/api/v1/posts', { page, author }));
}

export function getPost(slug: string): Promise<PostDetail> {
  return apiRequest<PostDetail>(`/api/v1/posts/${encodeURIComponent(slug)}`);
}

export function listMyPosts(page: number): Promise<Page<PostSummary>> {
  return apiRequest<Page<PostSummary>>(withQuery('/api/v1/me/posts', { page }));
}

export function createPost(input: PostInput): Promise<PostDetail> {
  return apiRequest<PostDetail>('/api/v1/posts', { method: 'POST', ...jsonBody(input) });
}

export function updatePost(id: string, changes: PostChanges): Promise<PostDetail> {
  return apiRequest<PostDetail>(`/api/v1/posts/${id}`, { method: 'PATCH', ...jsonBody(changes) });
}

export function deletePost(id: string): Promise<void> {
  return apiRequest<void>(`/api/v1/posts/${id}`, { method: 'DELETE' });
}
