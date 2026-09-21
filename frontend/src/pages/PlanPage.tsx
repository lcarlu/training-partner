import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { api } from '../client/endpoints';
import type { TrainingPlan } from '../client/types';

const PHASE_LABELS: Record<string, string> = {
  base: 'Base',
  build: 'Développement',
  peak: 'Spécifique',
  taper: 'Affûtage',
  race_week: 'Semaine de course',
  post: 'Post-course',
};

function secondsToHms(seconds: number | null): string {
  if (seconds == null) return '';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}:${m.toString().padStart(2, '0')}`;
}

function hmsToSeconds(value: string): number | null {
  const match = /^(\d+):(\d{1,2})$/.exec(value.trim());
  if (!match) return null;
  return Number(match[1]) * 3600 + Number(match[2]) * 60;
}

export function PlanPage() {
  const [plan, setPlan] = useState<TrainingPlan | null>(null);
  const [raceDate, setRaceDate] = useState('');
  const [targetTime, setTargetTime] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.plan().then((p) => {
      setPlan(p);
      setRaceDate(p.raceDate);
      setTargetTime(secondsToHms(p.targetTimeSeconds));
    });
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!plan) return;
    setSaving(true);
    const updated = await api.planUpdate({
      ...plan,
      raceDate,
      targetTimeSeconds: hmsToSeconds(targetTime),
    });
    setPlan(updated);
    setSaving(false);
  };

  if (!plan) return <p className="muted">Chargement…</p>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <h1>Plan marathon</h1>

      <form onSubmit={handleSubmit} className="card" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <label>
          Date de course
          <br />
          <input type="date" value={raceDate} onChange={(e) => setRaceDate(e.target.value)} required />
        </label>
        <label>
          Objectif (h:mm)
          <br />
          <input
            type="text"
            placeholder="3:30"
            value={targetTime}
            onChange={(e) => setTargetTime(e.target.value)}
          />
        </label>
        <button type="submit" disabled={saving}>
          {saving ? 'Enregistrement…' : 'Enregistrer'}
        </button>
      </form>

      <section className="card">
        <h2>Timeline des phases</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {plan.phases.map((p) => (
            <div key={p.phase} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  background: 'var(--series-1)',
                  flexShrink: 0,
                }}
              />
              <div style={{ minWidth: 110, fontWeight: 600 }}>{PHASE_LABELS[p.phase] ?? p.phase}</div>
              <div className="secondary">
                {new Date(p.start).toLocaleDateString('fr-FR')} → {new Date(p.end).toLocaleDateString('fr-FR')}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
