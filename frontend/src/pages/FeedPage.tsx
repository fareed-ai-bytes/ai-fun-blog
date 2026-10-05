import { Link, useSearchParams } from 'react-router';

import { buttonClass } from '../components/Button';
import { useMe } from '../features/auth/useMe';
import { PostList } from '../features/posts/PostList';
import { useFeed } from '../features/posts/queries';
import { pageFromSearch } from '../lib/format';

export function FeedPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = pageFromSearch(searchParams.get('page'));
  const feed = useFeed(page);
  const { data: me } = useMe();

  return (
    <section>
      <h1 className="mb-8 text-3xl font-semibold">Latest posts</h1>
      <PostList
        data={feed.data}
        isPending={feed.isPending}
        error={feed.error}
        onRetry={() => void feed.refetch()}
        onPageChange={(next) => {
          setSearchParams({ page: String(next) });
          window.scrollTo({ top: 0 });
        }}
        emptyMessage="No posts have been published yet."
        emptyAction={
          <Link to={me ? '/write' : '/register'} className={buttonClass('primary')}>
            Write your first post
          </Link>
        }
      />
    </section>
  );
}
