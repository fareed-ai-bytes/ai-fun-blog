import { Link, useParams } from 'react-router';

import { ApiError } from '../api/client';
import { buttonClass } from '../components/Button';
import { Markdown } from '../components/Markdown';
import { StatusBadge } from '../components/StatusBadge';
import { ErrorState, PostSkeleton } from '../components/states';
import { useMe } from '../features/auth/useMe';
import { Comments } from '../features/comments/Comments';
import { LikeButton } from '../features/likes/LikeButton';
import { usePost } from '../features/posts/queries';
import { formatDate, pluralise } from '../lib/format';
import { NotFoundPage } from './NotFoundPage';

export function PostPage() {
  const { slug = '' } = useParams();
  const post = usePost(slug);
  const { data: me } = useMe();

  if (post.isPending) return <PostSkeleton />;
  if (post.error instanceof ApiError && post.error.status === 404) return <NotFoundPage />;
  if (post.error || !post.data) {
    return <ErrorState error={post.error} onRetry={() => void post.refetch()} />;
  }

  const data = post.data;
  return (
    <article>
      <header className="mb-8">
        {data.status === 'draft' && (
          <p className="mb-3">
            <StatusBadge status="draft" />{' '}
            <span className="text-sm text-muted">Only you can see this draft.</span>
          </p>
        )}
        <h1 className="text-4xl font-semibold leading-tight">{data.title}</h1>
        <p className="mt-3 flex flex-wrap items-center gap-x-3 text-sm text-muted">
          <Link to={`/u/${data.author.username}`} className="font-medium hover:text-primary">
            {data.author.display_name}
          </Link>
          {data.published_at && (
            <time dateTime={data.published_at}>{formatDate(data.published_at)}</time>
          )}
        </p>
        {data.is_owner && (
          <Link to={`/edit/${data.slug}`} className={buttonClass('secondary', 'mt-4')}>
            Edit
          </Link>
        )}
      </header>

      <Markdown>{data.body_md}</Markdown>

      <footer className="mt-10 flex flex-wrap items-center gap-4 border-t border-line pt-6">
        <LikeButton post={data} me={me} />
        <span className="text-sm text-muted">{pluralise(data.comment_count, 'comment')}</span>
      </footer>

      <Comments post={data} me={me} />
    </article>
  );
}
