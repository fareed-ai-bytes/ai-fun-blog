import { apiRequest, jsonBody, withQuery } from './client';
import type { Comment, Page } from './types';

export function listComments(postId: string, page: number): Promise<Page<Comment>> {
  return apiRequest<Page<Comment>>(withQuery(`/api/v1/posts/${postId}/comments`, { page }));
}

export function createComment(postId: string, body: string): Promise<Comment> {
  return apiRequest<Comment>(`/api/v1/posts/${postId}/comments`, {
    method: 'POST',
    ...jsonBody({ body }),
  });
}

export function deleteComment(commentId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/comments/${commentId}`, { method: 'DELETE' });
}
