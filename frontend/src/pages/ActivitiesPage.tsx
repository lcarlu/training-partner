import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../client/endpoints';
import type { Activity } from '../client/types';
import { useSportFilter } from '../context/SportFilterContext';

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.round((seconds % 3600) / 60);
  return h > 0 ? `${h}h${m.toString().padStart(2, '0')}` : `${m}min`;
}

function formatDistance(meters: number | null): string {
  if (meters == null) return '—';
  return `${(meters / 1000).toFixed(1)} km`;
}

const PAGE_SIZE = 15;

export function ActivitiesPage() {
  const { sport } = useSportFilter();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setPage(0);
  }, [sport]);

  useEffect(() => {
    setLoading(true);
    api
      .activities({ sport, limit: PAGE_SIZE * (page + 1) })
      .then((res) => {
        setActivities(res.items.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE));
        setTotal(res.total);
      })
      .finally(() => setLoading(false));
  }, [sport, page]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h1>Activités</h1>
      {loading ? (
        <p className="muted">Chargement…</p>
      ) : (
        <>
          <div className="card" style={{ padding: 0, overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--gridline)' }}>
                  <th style={{ padding: '0.75rem' }}>Date</th>
                  <th style={{ padding: '0.75rem' }}>Sport</th>
                  <th style={{ padding: '0.75rem' }}>Nom</th>
                  <th style={{ padding: '0.75rem' }}>Durée</th>
                  <th style={{ padding: '0.75rem' }}>Distance</th>
                  <th style={{ padding: '0.75rem' }}>FC moy.</th>
                </tr>
              </thead>
              <tbody>
                {activities.map((a) => (
                  <tr key={a.id} style={{ borderBottom: '1px solid var(--gridline)' }}>
                    <td style={{ padding: '0.75rem' }}>
                      {new Date(a.startTime).toLocaleDateString('fr-FR')}
                    </td>
                    <td style={{ padding: '0.75rem' }}>{a.sport}</td>
                    <td style={{ padding: '0.75rem' }}>
                      <Link to={`/activities/${a.id}`}>{a.name}</Link>
                    </td>
                    <td style={{ padding: '0.75rem' }}>{formatDuration(a.durationSeconds)}</td>
                    <td style={{ padding: '0.75rem' }}>{formatDistance(a.distanceMeters)}</td>
                    <td style={{ padding: '0.75rem' }}>{a.avgHeartRate ?? '—'}</td>
                  </tr>
                ))}
                {activities.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ padding: '1rem', textAlign: 'center' }} className="muted">
                      Aucune activité.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button type="button" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
              Précédent
            </button>
            <span className="muted">
              Page {page + 1} / {totalPages}
            </span>
            <button
              type="button"
              disabled={page + 1 >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Suivant
            </button>
          </div>
        </>
      )}
    </div>
  );
}
