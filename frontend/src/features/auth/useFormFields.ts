import { useState } from 'react';
import type { ChangeEvent, FocusEvent } from 'react';

import type { Validator } from './validation';
import { validateAll } from './validation';

/** Minimal form state: values, validate on blur and on submit, merge server field errors. */
export function useFormFields<K extends string>(
  initial: Record<K, string>,
  rules: Partial<Record<K, Validator>>,
) {
  const [values, setValues] = useState(initial);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const bind = (name: K) => ({
    name,
    value: values[name],
    error: errors[name],
    onChange: (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setValues((current) => ({ ...current, [name]: event.target.value })),
    onBlur: (event: FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const message = rules[name]?.(event.target.value);
      setErrors((current) => {
        const rest = Object.fromEntries(Object.entries(current).filter(([key]) => key !== name));
        return message ? { ...rest, [name]: message } : rest;
      });
    },
  });

  /** Runs every rule; returns true when the form may be submitted. */
  const validate = (): boolean => {
    const found = validateAll(values, rules as Record<string, Validator>);
    setErrors(found);
    return Object.keys(found).length === 0;
  };

  return { values, setValues, errors, setErrors, bind, validate };
}
