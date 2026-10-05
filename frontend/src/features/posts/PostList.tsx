import type { ReactNode } from 'react';

import type { Page, PostSummary } from '../../api/types';
import { Pagination } from '../../components/Pagination';
import { EmptyState, ErrorState, PostListSkeleton } from '../../components/states';
import { PostCard } from './PostCard';

interface PostListProps {
  data: Page<PostSummary> | undefined;
  isPending: boolean;
  error: unknown;
  onRetry: () => void;
  onPageChange: (page: number) => void;
  emptyMessage: string;
  emptyAction?: ReactNode;
}

/** Feed-style list with loading, error, empty and paginated states. */
export function PostList(props: PostListProps) {
  const { data, isPending, error, onRetry, onPageChange, emptyMessage, emptyAction } = props;
  if (isPending) return <PostListSkeleton />;
  if (error || !data) return <ErrorState error={error} onRetry={onRetry} />;
  if (data.items.length === 0) return <EmptyState message={emptyMessage} action={emptyAction} />;
  return (
    <>
      <div className="space-y-6">
        {data.items.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
      <Pagination
        page={data.page}
        pageSize={data.page_size}
        total={data.total}
        onChange={onPageChange}
      />
    </>
  );
}
