import type { ReactNode } from 'react';

import { errorMessage } from '../api/client';
import { Button } from './Button';

// Loading / empty / error states required on every data view (design.md).

function Bar({ className }: { className: string }) {
  return <div className={`animate-pulse rounded bg-slate-200 ${className}`} />;
}

export function PostListSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div aria-busy="true" aria-label="Loading posts" className="space-y-8">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="space-y-3">
          <Bar className="h-6 w-2/3" />
          <Bar className="h-4 w-full" />
          <Bar className="h-4 w-5/6" />
          <Bar className="h-3 w-1/3" />
        </div>
      ))}
    </div>
  );
}

export function PostSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading post" className="space-y-4">
      <Bar className="h-9 w-3/4" />
      <Bar className="h-4 w-1/3" />
      <div className="space-y-3 pt-4">
        {Array.from({ length: 6 }, (_, i) => (
          <Bar key={i} className="h-4 w-full" />
        ))}
      </div>
    </div>
  );
}

export function InlineLoading({ label = 'Loading…' }: { label?: string }) {
  return (
    <p aria-busy="true" className="py-4 text-sm text-muted">
      {label}
    </p>
  );
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  return (
    <div role="alert" className="rounded-md border border-red-200 bg-red-50 p-4">
      <p className="font-medium text-danger">Couldn't load this.</p>
      <p className="mt-1 text-sm text-ink">{errorMessage(error)}</p>
      {onRetry && (
        <Button variant="secondary" className="mt-3" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}

export function EmptyState({ message, action }: { message: string; action?: ReactNode }) {
  return (
    <div className="rounded-md border border-dashed border-line p-8 text-center">
      <p className="text-muted">{message}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
