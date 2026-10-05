import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { likePost, unlikePost } from '../../api/likes';
import { ApiError } from '../../api/client';
import { queryKeys } from '../../api/queryKeys';
import type { LikeState, Me, PostDetail } from '../../api/types';
import { LikeButton } from './LikeButton';

vi.mock('../../api/likes', () => ({ likePost: vi.fn(), unlikePost: vi.fn() }));

const me: Me = { id: 'u2', email: 'bob@example.com', username: 'bob', display_name: 'Bob' };

const basePost: PostDetail = {
  id: 'p1',
  slug: 'hello',
  title: 'Hello',
  excerpt: '',
  status: 'published',
  author: { username: 'alice', display_name: 'Alice' },
  published_at: '2026-10-01T10:00:00Z',
  updated_at: '2026-10-01T10:00:00Z',
  like_count: 3,
  comment_count: 0,
  body_md: 'Hi',
  liked_by_me: false,
  is_owner: false,
};

/** Renders the button from the query cache, like PostPage does, so optimistic updates show. */
function renderLikeButton(post: PostDetail, viewer: Me | null) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  queryClient.setQueryData(queryKeys.post(post.slug), post);
  function Harness() {
    const { data } = useQuery({
      queryKey: queryKeys.post(post.slug),
      queryFn: () => Promise.resolve(post),
      staleTime: Infinity,
    });
    return data ? <LikeButton post={data} me={viewer} /> : null;
  }
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <Harness />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

describe('LikeButton', () => {
  beforeEach(() => {
    vi.mocked(likePost).mockReset();
    vi.mocked(unlikePost).mockReset();
  });

  it('asks anonymous users to log in instead of showing a dead button', () => {
    renderLikeButton(basePost, null);
    expect(screen.getByRole('link', { name: 'Log in to like' })).toBeTruthy();
    expect(screen.queryByRole('button')).toBeNull();
  });

  it('shows only the count on your own post (BR-03)', () => {
    renderLikeButton({ ...basePost, is_owner: true }, me);
    expect(screen.queryByRole('button')).toBeNull();
    expect(screen.getByText(/3 likes/)).toBeTruthy();
  });

  it('updates optimistically, then keeps the server value', async () => {
    const server = deferred<LikeState>();
    vi.mocked(likePost).mockReturnValue(server.promise);
    renderLikeButton(basePost, me);

    const button = screen.getByRole('button', { name: 'Like this post' });
    expect(button.getAttribute('aria-pressed')).toBe('false');
    fireEvent.click(button);

    // Before the server answers, the UI already shows the new state.
    await waitFor(() => expect(screen.getByTestId('like-count').textContent).toBe('4'));
    expect(screen.getByRole('button').getAttribute('aria-pressed')).toBe('true');
    expect(likePost).toHaveBeenCalledWith('p1');

    server.resolve({ like_count: 4, liked_by_me: true });
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Unlike this post' })).toBeTruthy(),
    );
  });

  it('rolls back when the server rejects the like', async () => {
    const server = deferred<LikeState>();
    vi.mocked(likePost).mockReturnValue(server.promise);
    renderLikeButton(basePost, me);

    fireEvent.click(screen.getByRole('button', { name: 'Like this post' }));
    await waitFor(() => expect(screen.getByTestId('like-count').textContent).toBe('4'));

    server.reject(new ApiError(404, 'POST_NOT_FOUND', 'Post not found'));
    await waitFor(() => expect(screen.getByTestId('like-count').textContent).toBe('3'));
    expect(screen.getByRole('button').getAttribute('aria-pressed')).toBe('false');
    expect(screen.getByRole('alert').textContent).toBe('Post not found');
  });

  it('unlikes when already liked', async () => {
    vi.mocked(unlikePost).mockResolvedValue({ like_count: 2, liked_by_me: false });
    renderLikeButton({ ...basePost, liked_by_me: true }, me);

    fireEvent.click(screen.getByRole('button', { name: 'Unlike this post' }));
    await waitFor(() => expect(screen.getByTestId('like-count').textContent).toBe('2'));
    expect(unlikePost).toHaveBeenCalledWith('p1');
  });
});
