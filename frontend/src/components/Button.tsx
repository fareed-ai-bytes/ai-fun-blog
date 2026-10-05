import type { ButtonHTMLAttributes } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-semibold ' +
  'transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 ' +
  'focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-50';

const VARIANTS: Record<ButtonVariant, string> = {
  primary: 'bg-primary text-white hover:bg-blue-700',
  secondary: 'border border-line bg-white text-ink hover:bg-slate-50',
  danger: 'bg-danger text-white hover:bg-red-700',
  ghost: 'text-ink hover:bg-slate-100',
};

/** Classes for anything that should look like a button (also used on <Link>). */
export function buttonClass(variant: ButtonVariant = 'primary', extra = ''): string {
  return `${BASE} ${VARIANTS[variant]} ${extra}`.trim();
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export function Button({ variant = 'primary', className = '', type, ...props }: ButtonProps) {
  return <button type={type ?? 'button'} className={buttonClass(variant, className)} {...props} />;
}
