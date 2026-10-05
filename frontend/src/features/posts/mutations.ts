import { useMutation, useQueryClient } from '@tanstack/react-query';

import { createPost, deletePost, updatePost } from '../../api/posts';
import { queryKeys } from '../../api/queryKeys';
import type { PostChanges, PostDetail } from '../../api/types';

function useInvalidatePostLists() {
  const queryClient = useQueryClient();
  return (post?: PostDetail) => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.feedAll });
    void queryClient.invalidateQueries({ queryKey: queryKeys.myPostsAll });
    if (post) queryClient.setQueryData(queryKeys.post(post.slug), post);
  };
}

export function useCreatePost() {
  const invalidate = useInvalidatePostLists();
  return useMutation({ mutationFn: createPost, onSuccess: invalidate });
}

export function useUpdatePost() {
  const invalidate = useInvalidatePostLists();
  return useMutation({
    mutationFn: ({ id, changes }: { id: string; changes: PostChanges }) => updatePost(id, changes),
    onSuccess: invalidate,
  });
}

export function useDeletePost() {
  const queryClient = useQueryClient();
  const invalidate = useInvalidatePostLists();
  return useMutation({
    mutationFn: ({ id }: { id: string; slug: string }) => deletePost(id),
    onSuccess: (_result, { slug }) => {
      queryClient.removeQueries({ queryKey: queryKeys.post(slug) });
      invalidate();
    },
  });
}
