import { useState } from 'react';

import { Button } from './Button';

interface ConfirmButtonProps {
  label: string;
  confirmLabel: string;
  question: string;
  onConfirm: () => void;
  pending?: boolean;
}

/** Inline confirm for destructive actions (design.md): Delete → "Delete? Yes / Cancel". */
export function ConfirmButton({
  label,
  confirmLabel,
  question,
  onConfirm,
  pending,
}: ConfirmButtonProps) {
  const [asking, setAsking] = useState(false);
  if (!asking) {
    return (
      <Button variant="ghost" className="text-danger" onClick={() => setAsking(true)}>
        {label}
      </Button>
    );
  }
  return (
    <span role="group" aria-label={question} className="inline-flex items-center gap-2">
      <span className="text-sm text-ink">{question}</span>
      <Button
        variant="danger"
        disabled={pending}
        onClick={() => {
          onConfirm();
          setAsking(false);
        }}
      >
        {confirmLabel}
      </Button>
      <Button variant="secondary" onClick={() => setAsking(false)}>
        Cancel
      </Button>
    </span>
  );
}
