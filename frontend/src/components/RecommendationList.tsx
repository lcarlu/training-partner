import type { Recommendation, RecommendationSeverity } from '../client/types';

const SEVERITY_STYLE: Record<RecommendationSeverity, { color: string; icon: string; label: string }> = {
  info: { color: 'var(--status-good)', icon: '✓', label: 'Info' },
  warning: { color: 'var(--status-warning)', icon: '!', label: 'Attention' },
  alert: { color: 'var(--status-critical)', icon: '⛔', label: 'Alerte' },
};

interface Props {
  recommendations: Recommendation[];
}

export function RecommendationList({ recommendations }: Props) {
  if (recommendations.length === 0) {
    return <p className="muted">Aucune recommandation pour le moment.</p>;
  }

  return (
    <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {recommendations.map((rec) => {
        const style = SEVERITY_STYLE[rec.severity];
        return (
          <li
            key={rec.id}
            style={{
              display: 'flex',
              gap: '0.75rem',
              alignItems: 'flex-start',
              borderLeft: `3px solid ${style.color}`,
              paddingLeft: '0.75rem',
            }}
          >
            <span
              aria-label={style.label}
              title={style.label}
              style={{ color: style.color, fontWeight: 700, minWidth: '1.5rem' }}
            >
              {style.icon}
            </span>
            <div>
              <div style={{ fontWeight: 600 }}>{rec.title}</div>
              <div className="secondary" style={{ fontSize: '0.9rem' }}>
                {rec.detail}
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
