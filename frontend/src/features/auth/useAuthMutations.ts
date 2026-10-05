import { useMutation, useQueryClient } from '@tanstack/react-query';

import { login, logout, register } from '../../api/auth';
import { queryKeys } from '../../api/queryKeys';
import type { Me } from '../../api/types';

function useOnAuthChange() {
  const queryClient = useQueryClient();
  return (me: Me | null) => {
    queryClient.setQueryData(queryKeys.me, me);
    // Personalised fields (is_owner, liked_by_me, can_delete) change with the user.
    void queryClient.invalidateQueries({ predicate: (q) => q.queryKey[0] !== 'me' });
  };
}

export function useLogin() {
  const onAuthChange = useOnAuthChange();
  return useMutation({ mutationFn: login, onSuccess: onAuthChange });
}

export function useRegister() {
  const onAuthChange = useOnAuthChange();
  return useMutation({ mutationFn: register, onSuccess: onAuthChange });
}

export function useLogout() {
  const onAuthChange = useOnAuthChange();
  return useMutation({ mutationFn: logout, onSuccess: () => onAuthChange(null) });
}
