import type { PostStatus } from '../api/types';

/** Text + colour, never colour alone (design.md). */
export function StatusBadge({ status }: { status: PostStatus }) {
  const published = status === 'published';
  return (
    <span
      className={
        'inline-block rounded-full px-2 py-0.5 text-xs font-semibold ' +
        (published ? 'bg-green-100 text-success' : 'bg-amber-100 text-warn')
      }
    >
      {published ? 'Published' : 'Draft'}
    </span>
  );
}
