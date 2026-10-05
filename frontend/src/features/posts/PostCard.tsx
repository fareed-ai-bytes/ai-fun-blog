import { Link } from 'react-router';

import type { PostSummary } from '../../api/types';
import { formatDate, pluralise } from '../../lib/format';

export function PostCard({ post }: { post: PostSummary }) {
  return (
    <article className="border-b border-line pb-6 last:border-b-0">
      <h2 className="text-xl font-semibold leading-snug">
        <Link to={`/p/${post.slug}`} className="hover:text-primary">
          {post.title}
        </Link>
      </h2>
      {post.excerpt && <p className="mt-2 text-ink/80">{post.excerpt}</p>}
      <p className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
        <Link to={`/u/${post.author.username}`} className="font-medium hover:text-primary">
          {post.author.display_name}
        </Link>
        <time dateTime={post.published_at ?? undefined}>{formatDate(post.published_at)}</time>
        <span aria-label={pluralise(post.like_count, 'like')}>♥ {post.like_count}</span>
        <span aria-label={pluralise(post.comment_count, 'comment')}>💬 {post.comment_count}</span>
      </p>
    </article>
  );
}
