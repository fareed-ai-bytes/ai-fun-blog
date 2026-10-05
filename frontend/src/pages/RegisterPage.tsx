import type { FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router';

import { errorMessage, fieldErrors } from '../api/client';
import { Button } from '../components/Button';
import { TextField } from '../components/TextField';
import { returnPath } from '../features/auth/returnTo';
import { useRegister } from '../features/auth/useAuthMutations';
import { useFormFields } from '../features/auth/useFormFields';
import { useMe } from '../features/auth/useMe';
import { validators } from '../features/auth/validation';

export function RegisterPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { data: me } = useMe();
  const register = useRegister();
  const form = useFormFields(
    { email: '', username: '', display_name: '', password: '' },
    {
      email: validators.email,
      username: validators.username,
      display_name: validators.display_name,
      password: validators.password,
    },
  );

  if (me) return <Navigate to={returnPath(location.state)} replace />;

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!form.validate()) return;
    register.mutate(form.values, {
      onSuccess: () => void navigate(returnPath(location.state), { replace: true }),
      onError: (error) => form.setErrors(fieldErrors(error)),
    });
  };

  const formError =
    register.isError && Object.keys(fieldErrors(register.error)).length === 0
      ? errorMessage(register.error)
      : undefined;

  return (
    <section className="mx-auto max-w-sm">
      <h1 className="text-2xl font-semibold">Create your account</h1>
      <form noValidate onSubmit={onSubmit} className="mt-6 space-y-4">
        {formError && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-danger">
            {formError}
          </p>
        )}
        <TextField label="Email" type="email" autoComplete="email" {...form.bind('email')} />
        <TextField
          label="Username"
          autoComplete="username"
          hint="Lowercase letters, digits and underscores; shown on your posts."
          {...form.bind('username')}
        />
        <TextField label="Display name" autoComplete="name" {...form.bind('display_name')} />
        <TextField
          label="Password"
          type="password"
          autoComplete="new-password"
          hint="At least 8 characters."
          {...form.bind('password')}
        />
        <Button type="submit" className="w-full" disabled={register.isPending}>
          {register.isPending ? 'Creating account…' : 'Sign up'}
        </Button>
      </form>
      <p className="mt-4 text-sm text-muted">
        Already have an account?{' '}
        <Link to="/login" state={location.state} className="font-medium text-primary">
          Log in
        </Link>
      </p>
    </section>
  );
}
