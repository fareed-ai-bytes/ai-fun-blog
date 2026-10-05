import { useNavigate, useParams } from 'react-router';

import { ApiError } from '../api/client';
import type { PostDetail, PostStatus } from '../api/types';
import { ErrorState, PostSkeleton } from '../components/states';
import { useCreatePost, useUpdatePost } from '../features/posts/mutations';
import type { EditorValues } from '../features/posts/PostEditor';
import { PostEditor } from '../features/posts/PostEditor';
import { usePost } from '../features/posts/queries';
import { NotFoundPage } from './NotFoundPage';

/** After saving: published → the public post; draft → My posts (demo path in KICKOFF.md). */
function useAfterSave() {
  const navigate = useNavigate();
  return (post: PostDetail) =>
    void navigate(post.status === 'published' ? `/p/${post.slug}` : '/me/posts');
}

export function WritePage() {
  const create = useCreatePost();
  const afterSave = useAfterSave();
  return (
    <section>
      <h1 className="mb-6 text-2xl font-semibold">Write a post</h1>
      <PostEditor
        initial={{ title: '', body_md: '' }}
        pending={create.isPending}
        error={create.error}
        onSave={(values: EditorValues, status: PostStatus) =>
          create.mutate({ ...values, status }, { onSuccess: afterSave })
        }
      />
    </section>
  );
}

export function EditPage() {
  const { slug = '' } = useParams();
  const post = usePost(slug);
  const update = useUpdatePost();
  const afterSave = useAfterSave();

  if (post.isPending) return <PostSkeleton />;
  if (post.error instanceof ApiError && post.error.status === 404) return <NotFoundPage />;
  if (post.error || !post.data) {
    return <ErrorState error={post.error} onRetry={() => void post.refetch()} />;
  }
  if (!post.data.is_owner) return <NotFoundPage />;

  const current = post.data;
  return (
    <section>
      <h1 className="mb-6 text-2xl font-semibold">Edit post</h1>
      <PostEditor
        key={current.id}
        initial={{ title: current.title, body_md: current.body_md }}
        status={current.status}
        pending={update.isPending}
        error={update.error}
        onSave={(values, status) =>
          update.mutate(
            { id: current.id, changes: { ...values, status } },
            { onSuccess: afterSave },
          )
        }
      />
    </section>
  );
}
