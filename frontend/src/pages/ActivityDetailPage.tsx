import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../client/endpoints';
import type { Activity } from '../client/types';
import { StatTile } from '../components/StatTile';

export function ActivityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activity, setActivity] = useState<Activity | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api
      .activity(id)
      .then((a) => setActivity(a ?? null))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className="muted">Chargement…</p>;
  if (!activity) return <p>Activité introuvable. <Link to="/activities">Retour</Link></p>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Link to="/activities" className="muted">
        ← Activités
      </Link>
      <h1>{activity.name}</h1>
      <p className="secondary">
        {new Date(activity.startTime).toLocaleString('fr-FR')} · {activity.sport}
      </p>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <StatTile label="Durée" value={`${Math.round(activity.durationSeconds / 60)} min`} />
        <StatTile
          label="Distance"
          value={activity.distanceMeters ? `${(activity.distanceMeters / 1000).toFixed(2)} km` : '—'}
        />
        <StatTile label="FC moyenne" value={activity.avgHeartRate?.toString() ?? '—'} />
        <StatTile label="FC max" value={activity.maxHeartRate?.toString() ?? '—'} />
        <StatTile
          label="Allure moyenne"
          value={
            activity.avgPaceSecPerKm
              ? `${Math.floor(activity.avgPaceSecPerKm / 60)}:${(activity.avgPaceSecPerKm % 60).toString().padStart(2, '0')} /km`
              : '—'
          }
        />
        <StatTile label="Dénivelé" value={activity.elevationGainMeters != null ? `${activity.elevationGainMeters} m` : '—'} />
        <StatTile label="Calories" value={activity.calories?.toString() ?? '—'} />
      </div>
    </div>
  );
}
