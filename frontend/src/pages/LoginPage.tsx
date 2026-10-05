import type { FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router';

import { errorMessage, fieldErrors } from '../api/client';
import { Button } from '../components/Button';
import { TextField } from '../components/TextField';
import { returnPath } from '../features/auth/returnTo';
import { useLogin } from '../features/auth/useAuthMutations';
import { useFormFields } from '../features/auth/useFormFields';
import { useMe } from '../features/auth/useMe';
import { validators } from '../features/auth/validation';

export function LoginPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { data: me } = useMe();
  const login = useLogin();
  const form = useFormFields(
    { email: '', password: '' },
    { email: validators.email, password: validators.required },
  );

  if (me) return <Navigate to={returnPath(location.state)} replace />;

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!form.validate()) return;
    login.mutate(form.values, {
      onSuccess: () => void navigate(returnPath(location.state), { replace: true }),
      onError: (error) => form.setErrors(fieldErrors(error)),
    });
  };

  const formError =
    login.isError && Object.keys(fieldErrors(login.error)).length === 0
      ? errorMessage(login.error)
      : undefined;

  return (
    <section className="mx-auto max-w-sm">
      <h1 className="text-2xl font-semibold">Log in</h1>
      <form noValidate onSubmit={onSubmit} className="mt-6 space-y-4">
        {formError && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-danger">
            {formError}
          </p>
        )}
        <TextField label="Email" type="email" autoComplete="email" {...form.bind('email')} />
        <TextField
          label="Password"
          type="password"
          autoComplete="current-password"
          {...form.bind('password')}
        />
        <Button type="submit" className="w-full" disabled={login.isPending}>
          {login.isPending ? 'Logging in…' : 'Log in'}
        </Button>
      </form>
      <p className="mt-4 text-sm text-muted">
        No account?{' '}
        <Link to="/register" state={location.state} className="font-medium text-primary">
          Sign up
        </Link>
      </p>
    </section>
  );
}
