import { Link, useSearchParams } from 'react-router';

import { errorMessage } from '../api/client';
import type { PostSummary } from '../api/types';
import { Button, buttonClass } from '../components/Button';
import { ConfirmButton } from '../components/ConfirmButton';
import { Pagination } from '../components/Pagination';
import { StatusBadge } from '../components/StatusBadge';
import { EmptyState, ErrorState, PostListSkeleton } from '../components/states';
import { useDeletePost, useUpdatePost } from '../features/posts/mutations';
import { useMyPosts } from '../features/posts/queries';
import { formatDate, pageFromSearch } from '../lib/format';

export function MyPostsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = pageFromSearch(searchParams.get('page'));
  const posts = useMyPosts(page);

  return (
    <section>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">My posts</h1>
        <Link to="/write" className={buttonClass('primary')}>
          Write
        </Link>
      </div>
      {posts.isPending ? (
        <PostListSkeleton />
      ) : posts.error || !posts.data ? (
        <ErrorState error={posts.error} onRetry={() => void posts.refetch()} />
      ) : posts.data.items.length === 0 ? (
        <EmptyState
          message="You haven't written anything yet."
          action={
            <Link to="/write" className={buttonClass('primary')}>
              Write your first post
            </Link>
          }
        />
      ) : (
        <>
          <ul className="divide-y divide-line rounded-md border border-line">
            {posts.data.items.map((post) => (
              <MyPostRow key={post.id} post={post} />
            ))}
          </ul>
          <Pagination
            page={posts.data.page}
            pageSize={posts.data.page_size}
            total={posts.data.total}
            onChange={(next) => setSearchParams({ page: String(next) })}
          />
        </>
      )}
    </section>
  );
}

function MyPostRow({ post }: { post: PostSummary }) {
  const update = useUpdatePost();
  const remove = useDeletePost();
  const published = post.status === 'published';
  const error = update.error ?? remove.error;

  return (
    <li className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <StatusBadge status={post.status} />
          <Link to={`/p/${post.slug}`} className="truncate font-medium hover:text-primary">
            {post.title}
          </Link>
        </div>
        <p className="mt-1 text-sm text-muted">
          Updated {formatDate(post.updated_at)} · ♥ {post.like_count} · 💬 {post.comment_count}
        </p>
        {error && (
          <p role="alert" className="mt-1 text-sm text-danger">
            {errorMessage(error)}
          </p>
        )}
      </div>
      <div className="flex shrink-0 flex-wrap items-center gap-2">
        <Link to={`/edit/${post.slug}`} className={buttonClass('secondary')}>
          Edit
        </Link>
        <Button
          variant="secondary"
          disabled={update.isPending}
          onClick={() =>
            update.mutate({ id: post.id, changes: { status: published ? 'draft' : 'published' } })
          }
        >
          {published ? 'Unpublish' : 'Publish'}
        </Button>
        <ConfirmButton
          label="Delete"
          confirmLabel="Yes, delete"
          question="Delete this post?"
          pending={remove.isPending}
          onConfirm={() => remove.mutate({ id: post.id, slug: post.slug })}
        />
      </div>
    </li>
  );
}
