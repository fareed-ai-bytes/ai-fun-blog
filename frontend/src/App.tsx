import { useEffect, useState } from 'react';

import { getHealth } from './api/health';

type ApiState = { kind: 'loading' } | { kind: 'ok'; status: string } | { kind: 'error' };

// Placeholder screen for T-001: proves the SPA reaches the API through the Vite proxy.
// Replaced by the router + app shell in T-010 (which also brings TanStack Query).
export default function App() {
  const [state, setState] = useState<ApiState>({ kind: 'loading' });

  useEffect(() => {
    getHealth()
      .then((health) => setState({ kind: 'ok', status: health.status }))
      .catch(() => setState({ kind: 'error' }));
  }, []);

  return (
    <main className="mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-semibold text-ink">Blog Platform</h1>
      <p className="mt-2 text-muted">Scaffold is running. The feed arrives in a later task.</p>
      <p className="mt-8 rounded-md border border-line p-4" data-testid="api-health">
        API health: {state.kind === 'loading' && <span className="text-muted">checking…</span>}
        {state.kind === 'ok' && <span className="font-medium text-success">{state.status}</span>}
        {state.kind === 'error' && <span className="font-medium text-danger">unreachable</span>}
      </p>
    </main>
  );
}
