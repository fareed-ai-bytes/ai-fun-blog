import { useId, useState } from 'react';
import type { SyntheticEvent } from 'react';

import { errorMessage, fieldErrors } from '../../api/client';
import type { PostStatus } from '../../api/types';
import { Button } from '../../components/Button';
import { Markdown } from '../../components/Markdown';
import { StatusBadge } from '../../components/StatusBadge';
import { TextField } from '../../components/TextField';

export interface EditorValues {
  title: string;
  body_md: string;
}

interface PostEditorProps {
  initial: EditorValues;
  /** Current status of an existing post; undefined when writing a new one. */
  status?: PostStatus;
  pending: boolean;
  error: unknown;
  onSave: (values: EditorValues, status: PostStatus) => void;
}

function validate(values: EditorValues): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!values.title.trim()) errors.title = 'Give your post a title';
  else if (values.title.length > 200) errors.title = 'Keep the title under 200 characters';
  if (!values.body_md.trim()) errors.body_md = 'Write something first';
  else if (values.body_md.length > 50_000)
    errors.body_md = 'Posts are limited to 50,000 characters';
  return errors;
}

/** Title + Markdown textarea with Write/Preview tabs (no WYSIWYG — out of scope). */
export function PostEditor({ initial, status, pending, error, onSave }: PostEditorProps) {
  const [values, setValues] = useState(initial);
  const [tab, setTab] = useState<'write' | 'preview'>('write');
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const bodyId = useId();
  const errors = { ...fieldErrors(error), ...localErrors };
  const formError =
    error && Object.keys(fieldErrors(error)).length === 0 ? errorMessage(error) : undefined;

  const submit = (nextStatus: PostStatus) => (event?: SyntheticEvent) => {
    event?.preventDefault();
    const found = validate(values);
    setLocalErrors(found);
    if (Object.keys(found).length === 0) onSave(values, nextStatus);
  };

  const published = status === 'published';
  return (
    <form noValidate onSubmit={submit(status ?? 'draft')} className="space-y-5">
      {status && (
        <p>
          <StatusBadge status={status} />
        </p>
      )}
      {formError && (
        <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-danger">
          {formError}
        </p>
      )}
      <TextField
        label="Title"
        value={values.title}
        error={errors.title}
        maxLength={200}
        onChange={(e) => setValues({ ...values, title: e.target.value })}
      />

      <div>
        <div role="tablist" aria-label="Editor mode" className="flex gap-1 border-b border-line">
          {(['write', 'preview'] as const).map((name) => (
            <button
              key={name}
              type="button"
              role="tab"
              aria-selected={tab === name}
              aria-controls={bodyId}
              onClick={() => setTab(name)}
              className={
                '-mb-px border-b-2 px-4 py-2 text-sm font-medium capitalize ' +
                (tab === name ? 'border-primary text-primary' : 'border-transparent text-muted')
              }
            >
              {name}
            </button>
          ))}
        </div>
        <div id={bodyId} role="tabpanel" className="pt-3">
          {tab === 'write' ? (
            <>
              <label htmlFor={`${bodyId}-body`} className="sr-only">
                Body (Markdown)
              </label>
              <textarea
                id={`${bodyId}-body`}
                value={values.body_md}
                onChange={(e) => setValues({ ...values, body_md: e.target.value })}
                rows={18}
                placeholder="Write in Markdown: # Heading, **bold**, - lists, [links](https://…)"
                aria-invalid={errors.body_md ? true : undefined}
                className={
                  'block w-full rounded-md border px-3 py-2 font-mono text-sm outline-none ' +
                  'focus:border-primary focus:ring-2 focus:ring-primary/30 ' +
                  (errors.body_md ? 'border-danger' : 'border-line')
                }
              />
            </>
          ) : (
            <div className="min-h-64 rounded-md border border-line p-4">
              {values.body_md.trim() ? (
                <Markdown>{values.body_md}</Markdown>
              ) : (
                <p className="text-muted">Nothing to preview yet.</p>
              )}
            </div>
          )}
          {errors.body_md && (
            <p role="alert" className="mt-1 text-sm text-danger">
              {errors.body_md}
            </p>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        {published ? (
          <>
            <Button type="submit" disabled={pending}>
              Save changes
            </Button>
            <Button variant="secondary" disabled={pending} onClick={submit('draft')}>
              Unpublish
            </Button>
          </>
        ) : (
          <>
            <Button variant="secondary" type="submit" disabled={pending}>
              Save draft
            </Button>
            <Button disabled={pending} onClick={submit('published')}>
              Publish
            </Button>
          </>
        )}
      </div>
    </form>
  );
}
