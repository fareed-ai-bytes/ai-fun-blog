import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useLocation } from 'react-router';

import { errorMessage, fieldErrors } from '../../api/client';
import { createComment, deleteComment, listComments } from '../../api/comments';
import { queryKeys } from '../../api/queryKeys';
import type { Comment, Me, PostDetail } from '../../api/types';
import { Button } from '../../components/Button';
import { ConfirmButton } from '../../components/ConfirmButton';
import { Pagination } from '../../components/Pagination';
import { EmptyState, ErrorState, InlineLoading } from '../../components/states';
import { formatDate } from '../../lib/format';

const MAX_LENGTH = 2000;

function useRefreshAfterCommentChange(post: PostDetail) {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.commentsAll(post.id) });
    void queryClient.invalidateQueries({ queryKey: queryKeys.post(post.slug) });
    void queryClient.invalidateQueries({ queryKey: queryKeys.feedAll });
  };
}

export function Comments({ post, me }: { post: PostDetail; me: Me | null | undefined }) {
  const [page, setPage] = useState(1);
  const comments = useQuery({
    queryKey: queryKeys.comments(post.id, page),
    queryFn: () => listComments(post.id, page),
    placeholderData: keepPreviousData,
  });

  return (
    <section aria-labelledby="comments-heading" className="mt-10">
      <h2 id="comments-heading" className="text-xl font-semibold">
        Comments
      </h2>
      {post.status === 'published' && <CommentForm post={post} me={me} />}
      <div className="mt-6">
        {comments.isPending ? (
          <InlineLoading label="Loading comments…" />
        ) : comments.error || !comments.data ? (
          <ErrorState error={comments.error} onRetry={() => void comments.refetch()} />
        ) : comments.data.items.length === 0 ? (
          <EmptyState message="No comments yet." />
        ) : (
          <>
            <ul className="divide-y divide-line">
              {comments.data.items.map((comment) => (
                <CommentItem key={comment.id} comment={comment} post={post} />
              ))}
            </ul>
            <Pagination
              label="Comment pages"
              page={comments.data.page}
              pageSize={comments.data.page_size}
              total={comments.data.total}
              onChange={setPage}
            />
          </>
        )}
      </div>
    </section>
  );
}

function CommentForm({ post, me }: { post: PostDetail; me: Me | null | undefined }) {
  const location = useLocation();
  const [body, setBody] = useState('');
  const [localError, setLocalError] = useState<string>();
  const refresh = useRefreshAfterCommentChange(post);
  const create = useMutation({
    mutationFn: (text: string) => createComment(post.id, text),
    onSuccess: () => {
      setBody('');
      refresh();
    },
  });

  if (!me) {
    return (
      <p className="mt-4 text-sm">
        <Link to="/login" state={{ from: location }} className="font-medium text-primary">
          Log in to comment
        </Link>
      </p>
    );
  }

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    const text = body.trim();
    if (!text) return setLocalError('Write a comment first');
    if (text.length > MAX_LENGTH) return setLocalError(`Keep it under ${MAX_LENGTH} characters`);
    setLocalError(undefined);
    create.mutate(text);
  };

  const error =
    localError ??
    (create.error ? (fieldErrors(create.error).body ?? errorMessage(create.error)) : undefined);
  return (
    <form noValidate onSubmit={onSubmit} className="mt-4 space-y-2">
      <label htmlFor="comment-body" className="sr-only">
        Add a comment
      </label>
      <textarea
        id="comment-body"
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={3}
        placeholder="Add a comment…"
        aria-invalid={error ? true : undefined}
        className={
          'block w-full rounded-md border px-3 py-2 text-sm outline-none ' +
          'focus:border-primary focus:ring-2 focus:ring-primary/30 ' +
          (error ? 'border-danger' : 'border-line')
        }
      />
      <div className="flex items-center justify-between gap-3">
        <span className={`text-xs ${body.length > MAX_LENGTH ? 'text-danger' : 'text-muted'}`}>
          {body.length}/{MAX_LENGTH}
        </span>
        <Button type="submit" disabled={create.isPending}>
          {create.isPending ? 'Posting…' : 'Comment'}
        </Button>
      </div>
      {error && (
        <p role="alert" className="text-sm text-danger">
          {error}
        </p>
      )}
    </form>
  );
}

function CommentItem({ comment, post }: { comment: Comment; post: PostDetail }) {
  const refresh = useRefreshAfterCommentChange(post);
  const remove = useMutation({ mutationFn: () => deleteComment(comment.id), onSuccess: refresh });
  return (
    <li className="py-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm">
          <Link to={`/u/${comment.author.username}`} className="font-semibold hover:text-primary">
            {comment.author.display_name}
          </Link>{' '}
          <time dateTime={comment.created_at} className="text-muted">
            {formatDate(comment.created_at)}
          </time>
        </p>
        {comment.can_delete && (
          <ConfirmButton
            label="Delete"
            confirmLabel="Yes, delete"
            question="Delete this comment?"
            pending={remove.isPending}
            onConfirm={() => remove.mutate()}
          />
        )}
      </div>
      <p className="mt-1 whitespace-pre-wrap break-words">{comment.body}</p>
      {remove.isError && (
        <p role="alert" className="mt-1 text-sm text-danger">
          {errorMessage(remove.error)}
        </p>
      )}
    </li>
  );
}
