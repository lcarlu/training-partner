interface Props {
  label: string;
  value: string;
  sub?: string;
}

export function StatTile({ label, value, sub }: Props) {
  return (
    <div className="card" style={{ flex: '1 1 140px' }}>
      <div className="muted" style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
        {label}
      </div>
      <div style={{ fontSize: '1.8rem', fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>{value}</div>
      {sub && (
        <div className="secondary" style={{ fontSize: '0.85rem' }}>
          {sub}
        </div>
      )}
    </div>
  );
}
