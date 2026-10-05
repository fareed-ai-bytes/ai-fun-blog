import { keepPreviousData, useQuery } from '@tanstack/react-query';

import { getPost, listFeed, listMyPosts } from '../../api/posts';
import { queryKeys } from '../../api/queryKeys';

export function useFeed(page: number, author?: string) {
  return useQuery({
    queryKey: queryKeys.feed(page, author),
    queryFn: () => listFeed({ page, author }),
    placeholderData: keepPreviousData,
  });
}

export function usePost(slug: string) {
  return useQuery({ queryKey: queryKeys.post(slug), queryFn: () => getPost(slug) });
}

export function useMyPosts(page: number) {
  return useQuery({
    queryKey: queryKeys.myPosts(page),
    queryFn: () => listMyPosts(page),
    placeholderData: keepPreviousData,
  });
}
