import { useQuery } from '@tanstack/react-query';

import { getMe } from '../../api/auth';
import { queryKeys } from '../../api/queryKeys';

/** Drives every auth-aware piece of UI. `data` is null when logged out. */
export function useMe() {
  return useQuery({ queryKey: queryKeys.me, queryFn: getMe, staleTime: 60_000 });
}
