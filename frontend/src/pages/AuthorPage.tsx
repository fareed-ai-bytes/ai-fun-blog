import { useParams, useSearchParams } from 'react-router';

import { PostList } from '../features/posts/PostList';
import { useFeed } from '../features/posts/queries';
import { pageFromSearch } from '../lib/format';

/** FR-14: one author's published posts (GET /posts?author=). */
export function AuthorPage() {
  const { username = '' } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const page = pageFromSearch(searchParams.get('page'));
  const feed = useFeed(page, username);
  const displayName = feed.data?.items[0]?.author.display_name;

  return (
    <section>
      <h1 className="text-3xl font-semibold">{displayName ?? `@${username}`}</h1>
      {displayName && <p className="mt-1 text-muted">@{username}</p>}
      <div className="mt-8">
        <PostList
          data={feed.data}
          isPending={feed.isPending}
          error={feed.error}
          onRetry={() => void feed.refetch()}
          onPageChange={(next) => {
            setSearchParams({ page: String(next) });
            window.scrollTo({ top: 0 });
          }}
          emptyMessage={`@${username} hasn't published any posts yet.`}
        />
      </div>
    </section>
  );
}
