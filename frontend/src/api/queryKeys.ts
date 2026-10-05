// One place for TanStack Query keys so invalidation stays consistent.
export const queryKeys = {
  me: ['me'] as const,
  feedAll: ['feed'] as const,
  feed: (page: number, author?: string) => ['feed', { page, author: author ?? null }] as const,
  postAll: ['post'] as const,
  post: (slug: string) => ['post', slug] as const,
  myPostsAll: ['myPosts'] as const,
  myPosts: (page: number) => ['myPosts', page] as const,
  comments: (postId: string, page: number) => ['comments', postId, page] as const,
  commentsAll: (postId: string) => ['comments', postId] as const,
};
