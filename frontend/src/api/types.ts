// Mirrors the API schemas in docs/architecture.md (snake_case end to end).
// Replaced by types generated from OpenAPI in T-087.

export interface Me {
  id: string;
  email: string;
  username: string;
  display_name: string;
}

export interface Author {
  username: string;
  display_name: string;
}

export type PostStatus = 'draft' | 'published';

export interface PostSummary {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  status: PostStatus;
  author: Author;
  published_at: string | null;
  updated_at: string;
  like_count: number;
  comment_count: number;
}

export interface PostDetail extends PostSummary {
  body_md: string;
  liked_by_me: boolean;
  is_owner: boolean;
}

export interface LikeState {
  like_count: number;
  liked_by_me: boolean;
}

export interface Comment {
  id: string;
  body: string;
  author: Author;
  created_at: string;
  can_delete: boolean;
}

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

export interface RegisterInput {
  email: string;
  username: string;
  display_name: string;
  password: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface PostInput {
  title: string;
  body_md: string;
  status?: PostStatus;
}

export type PostChanges = Partial<PostInput>;
