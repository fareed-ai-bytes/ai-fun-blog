import type { Location } from 'react-router';

/** Where to send the user after login/register: the page they came from (design.md). */
export function returnPath(state: unknown): string {
  if (typeof state === 'object' && state !== null && 'from' in state) {
    const from = state.from as Partial<Location> | undefined;
    const path = `${from?.pathname ?? '/'}${from?.search ?? ''}`;
    // Only in-app relative paths; never back to the auth pages themselves.
    if (path.startsWith('/') && !path.startsWith('//') && !/^\/(login|register)/.test(path)) {
      return path;
    }
  }
  return '/';
}
