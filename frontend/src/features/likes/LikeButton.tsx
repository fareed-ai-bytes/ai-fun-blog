import { Link, useLocation } from 'react-router';

import { errorMessage } from '../../api/client';
import type { Me, PostDetail } from '../../api/types';
import { pluralise } from '../../lib/format';
import { useToggleLike } from './useToggleLike';

interface LikeButtonProps {
  post: PostDetail;
  me: Me | null | undefined;
}

/** Anonymous → "Log in to like"; own post → count only (BR-03); others → toggle. */
export function LikeButton({ post, me }: LikeButtonProps) {
  const location = useLocation();
  const toggle = useToggleLike(post.slug);
  const count = pluralise(post.like_count, 'like');

  if (!me) {
    return (
      <span className="inline-flex items-center gap-3 text-sm">
        <span className="text-muted">♥ {count}</span>
        <Link to="/login" state={{ from: location }} className="font-medium text-primary">
          Log in to like
        </Link>
      </span>
    );
  }

  if (post.is_owner) {
    return <span className="text-sm text-muted">♥ {count}</span>;
  }

  const liked = post.liked_by_me;
  return (
    <span className="inline-flex items-center gap-3">
      <button
        type="button"
        aria-pressed={liked}
        aria-label={liked ? 'Unlike this post' : 'Like this post'}
        onClick={() => toggle.mutate({ postId: post.id, like: !liked })}
        className={
          'inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-semibold ' +
          'transition-colors focus-visible:outline-2 focus-visible:outline-accent ' +
          (liked
            ? 'border-accent bg-accent text-white hover:bg-rose-700'
            : 'border-line bg-white text-accent hover:bg-rose-50')
        }
      >
        <span aria-hidden="true">{liked ? '♥' : '♡'}</span>
        <span data-testid="like-count">{post.like_count}</span>
      </button>
      {toggle.isError && (
        <span role="alert" className="text-sm text-danger">
          {errorMessage(toggle.error)}
        </span>
      )}
    </span>
  );
}
