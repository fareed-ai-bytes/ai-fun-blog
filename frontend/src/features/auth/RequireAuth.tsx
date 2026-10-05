import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router';

import { ErrorState, InlineLoading } from '../../components/states';
import { useMe } from './useMe';

/** UX guard only — the API enforces auth. Sends anonymous users to /login and back. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const location = useLocation();
  const me = useMe();
  if (me.isPending) return <InlineLoading />;
  if (me.error) return <ErrorState error={me.error} onRetry={() => void me.refetch()} />;
  if (!me.data) return <Navigate to="/login" state={{ from: location }} replace />;
  return <>{children}</>;
}
