import { useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router';

import { useLogout } from '../features/auth/useAuthMutations';
import { useMe } from '../features/auth/useMe';
import { buttonClass } from './Button';

export function Header() {
  const { data: me, isPending } = useMe();
  const location = useLocation();

  return (
    <header className="border-b border-line bg-white">
      <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-4 py-3">
        <Link to="/" className="text-lg font-semibold text-ink">
          Blog Platform
        </Link>
        <nav aria-label="Account" className="flex items-center gap-2">
          {isPending ? null : me ? (
            <>
              <Link to="/write" className={buttonClass('primary')}>
                Write
              </Link>
              <AccountMenu displayName={me.display_name} username={me.username} />
            </>
          ) : (
            <>
              <Link to="/login" state={{ from: location }} className={buttonClass('ghost')}>
                Log in
              </Link>
              <Link to="/register" state={{ from: location }} className={buttonClass('primary')}>
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

function AccountMenu({ displayName, username }: { displayName: string; username: string }) {
  const menu = useRef<HTMLDetailsElement>(null);
  const navigate = useNavigate();
  const logout = useLogout();
  const close = () => menu.current?.removeAttribute('open');

  return (
    <details ref={menu} className="relative">
      <summary
        className="flex cursor-pointer list-none items-center gap-2 rounded-md px-2 py-1 hover:bg-slate-100"
        aria-label={`Account menu for ${username}`}
      >
        <span
          aria-hidden="true"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white"
        >
          {displayName.charAt(0).toUpperCase()}
        </span>
        <span className="text-sm font-medium" data-testid="header-username">
          {username}
        </span>
      </summary>
      <div className="absolute right-0 z-10 mt-2 w-44 rounded-md border border-line bg-white py-1 shadow-md">
        <Link to="/me/posts" onClick={close} className="block px-4 py-2 text-sm hover:bg-slate-50">
          My posts
        </Link>
        <Link
          to={`/u/${username}`}
          onClick={close}
          className="block px-4 py-2 text-sm hover:bg-slate-50"
        >
          My public page
        </Link>
        <button
          type="button"
          className="block w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
          disabled={logout.isPending}
          onClick={() => {
            close();
            logout.mutate(undefined, { onSuccess: () => void navigate('/') });
          }}
        >
          Log out
        </button>
      </div>
    </details>
  );
}
