import { SPORTS } from '../client/types';
import type { SportFilter } from '../client/types';

const LABELS: Record<SportFilter, string> = {
  all: 'Tous',
  running: 'Course à pied',
  cycling: 'Vélo',
  swimming: 'Natation',
  strength: 'Renforcement',
};

interface Props {
  value: SportFilter;
  onChange: (sport: SportFilter) => void;
}

export function SportSelector({ value, onChange }: Props) {
  const options: SportFilter[] = ['all', ...SPORTS];
  return (
    <select
      aria-label="Filtrer par sport"
      value={value}
      onChange={(e) => onChange(e.target.value as SportFilter)}
      style={{
        padding: '0.4rem 0.6rem',
        borderRadius: 8,
        border: '1px solid var(--border)',
        background: 'var(--surface-card)',
        color: 'var(--text-primary)',
      }}
    >
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {LABELS[opt]}
        </option>
      ))}
    </select>
  );
}
