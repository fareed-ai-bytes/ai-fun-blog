// Client-side checks mirror the API rules for fast feedback; the server stays the authority.

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const USERNAME = /^[a-z0-9_]{3,30}$/;

export type Validator = (value: string) => string | undefined;

export const validators: Record<string, Validator> = {
  email: (v) => (EMAIL.test(v.trim()) ? undefined : 'Enter a valid email address'),
  username: (v) =>
    USERNAME.test(v.trim().toLowerCase())
      ? undefined
      : '3–30 characters: letters, digits and underscores only',
  display_name: (v) => {
    const length = v.trim().length;
    return length >= 1 && length <= 60 ? undefined : 'Enter a name (up to 60 characters)';
  },
  password: (v) =>
    v.length >= 8 && v.length <= 128 ? undefined : 'Use at least 8 characters (up to 128)',
  required: (v) => (v.trim() ? undefined : 'Required'),
};

export function validateAll(
  values: Record<string, string>,
  rules: Record<string, Validator>,
): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const [field, rule] of Object.entries(rules)) {
    const message = rule(values[field] ?? '');
    if (message) errors[field] = message;
  }
  return errors;
}
