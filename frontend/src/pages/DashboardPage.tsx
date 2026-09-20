import { useCallback, useEffect, useState } from 'react';
import { api } from '../client/endpoints';
import type { DashboardSummary } from '../client/types';
import { useSportFilter } from '../context/SportFilterContext';
import { useSync } from '../hooks/useSync';
import { WeeklyVolumeChart } from '../components/charts/WeeklyVolumeChart';
import { TrainingLoadChart } from '../components/charts/TrainingLoadChart';
import { RecoveryChart } from '../components/charts/RecoveryChart';
import { VO2maxTrend } from '../components/charts/VO2maxTrend';
import { RecommendationList } from '../components/RecommendationList';
import { StatTile } from '../components/StatTile';

const PHASE_LABELS: Record<string, string> = {
  base: 'Base',
  build: 'Développement',
  peak: 'Spécifique',
  taper: 'Affûtage',
  race_week: 'Semaine de course',
  post: 'Post-course',
};

export function DashboardPage() {
  const { sport } = useSportFilter();
  const { syncing, error: syncError, lastSync, runSync } = useSync();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const loadSummary = useCallback(async () => {
    setLoading(true);
    const data = await api.dashboardSummary(sport);
    setSummary(data);
    setLoading(false);
  }, [sport]);

  // Refresh Garmin data then rebuild the dashboard whenever the page is opened.
  useEffect(() => {
    (async () => {
      await runSync();
      await loadSummary();
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!loading) loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sport]);

  const handleManualRefresh = async () => {
    await runSync();
    await loadSummary();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>Dashboard</h1>
          <p className="secondary" style={{ margin: 0 }}>
            {lastSync
              ? `Dernière synchro : ${new Date(lastSync.finishedAt).toLocaleString('fr-FR')}`
              : 'Synchronisation en cours...'}
          </p>
        </div>
        <button
          type="button"
          onClick={handleManualRefresh}
          disabled={syncing}
          style={{
            padding: '0.6rem 1rem',
            borderRadius: 8,
            border: 'none',
            background: 'var(--series-1)',
            color: 'white',
            fontWeight: 600,
            cursor: syncing ? 'not-allowed' : 'pointer',
            opacity: syncing ? 0.7 : 1,
          }}
        >
          {syncing ? 'Synchronisation…' : 'Refresh'}
        </button>
      </div>

      {syncError && (
        <div className="card" style={{ borderColor: 'var(--status-critical)' }}>
          Erreur de synchronisation : {syncError}
        </div>
      )}

      {!summary || loading ? (
        <p className="muted">Chargement du dashboard…</p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <StatTile
              label="Marathon"
              value={`J-${summary.daysUntilRace}`}
              sub={new Date(summary.raceDate).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              })}
            />
            <StatTile label="Phase" value={PHASE_LABELS[summary.phase] ?? summary.phase} />
            <StatTile
              label="Training readiness"
              value={summary.todayWellness?.trainingReadinessScore?.toString() ?? '—'}
            />
            <StatTile
              label="Body Battery"
              value={summary.todayWellness?.bodyBatteryMax?.toString() ?? '—'}
            />
            <StatTile
              label="Sommeil"
              value={
                summary.todayWellness?.sleepScore != null
                  ? `${summary.todayWellness.sleepScore}/100`
                  : '—'
              }
            />
            <StatTile
              label="HRV"
              value={
                summary.todayWellness?.hrvValueMs != null
                  ? `${summary.todayWellness.hrvValueMs} ms`
                  : '—'
              }
              sub={summary.todayWellness?.hrvStatus ?? undefined}
            />
          </div>

          <section className="card">
            <h2>Recommandations</h2>
            <RecommendationList recommendations={summary.recommendations} />
          </section>

          <section className="card">
            <h2>Volume hebdomadaire</h2>
            <WeeklyVolumeChart data={summary.weeklyVolume} />
          </section>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            <section className="card">
              <h2>Training readiness</h2>
              <TrainingLoadChart data={summary.recentWellness} />
            </section>
            <section className="card">
              <h2>Récupération</h2>
              <RecoveryChart data={summary.recentWellness} />
            </section>
          </div>

          <section className="card">
            <h2>VO2max</h2>
            <VO2maxTrend data={summary.recentWellness} />
          </section>
        </>
      )}
    </div>
  );
}
