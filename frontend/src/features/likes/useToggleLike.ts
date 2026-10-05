import { useMutation, useQueryClient } from '@tanstack/react-query';

import { likePost, unlikePost } from '../../api/likes';
import { queryKeys } from '../../api/queryKeys';
import type { PostDetail } from '../../api/types';

/** Optimistic like toggle: update the cached post at once, roll back on error (design.md). */
export function useToggleLike(slug: string) {
  const queryClient = useQueryClient();
  const key = queryKeys.post(slug);

  return useMutation({
    mutationFn: ({ postId, like }: { postId: string; like: boolean }) =>
      like ? likePost(postId) : unlikePost(postId),
    onMutate: async ({ like }) => {
      await queryClient.cancelQueries({ queryKey: key });
      const previous = queryClient.getQueryData<PostDetail>(key);
      if (previous) {
        queryClient.setQueryData<PostDetail>(key, {
          ...previous,
          liked_by_me: like,
          like_count: Math.max(0, previous.like_count + (like ? 1 : -1)),
        });
      }
      return { previous };
    },
    onError: (_error, _vars, context) => {
      if (context?.previous) queryClient.setQueryData(key, context.previous);
    },
    onSuccess: (state) => {
      queryClient.setQueryData<PostDetail>(key, (current) =>
        current ? { ...current, ...state } : current,
      );
      void queryClient.invalidateQueries({ queryKey: queryKeys.feedAll });
    },
  });
}
