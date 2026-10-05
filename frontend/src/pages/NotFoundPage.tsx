import { Link } from 'react-router';

import { buttonClass } from '../components/Button';

/** Also shown when a draft is requested by someone other than its author (BR-01). */
export function NotFoundPage() {
  return (
    <section className="py-16 text-center">
      <h1 className="text-3xl font-semibold">Not found</h1>
      <p className="mt-2 text-muted">This page doesn't exist, or you don't have access to it.</p>
      <Link to="/" className={buttonClass('primary', 'mt-6')}>
        Back to the feed
      </Link>
    </section>
  );
}
