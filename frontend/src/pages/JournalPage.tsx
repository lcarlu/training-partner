import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { api } from '../client/endpoints';
import type { JournalEntry, JournalEntryInput, Sport } from '../client/types';
import { SPORTS } from '../client/types';

const EMPTY_FORM: JournalEntryInput = {
  date: new Date().toISOString().slice(0, 10),
  sport: 'running',
  plannedNotes: '',
  actualNotes: '',
  rpe: null,
  mood: null,
  linkedActivityId: null,
};

export function JournalPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<JournalEntryInput>(EMPTY_FORM);

  const load = () => {
    setLoading(true);
    api
      .journalList()
      .then(setEntries)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const startEdit = (entry: JournalEntry) => {
    setEditingId(entry.id);
    const { id: _id, ...rest } = entry;
    void _id;
    setForm(rest);
  };

  const resetForm = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (editingId) {
      await api.journalUpdate(editingId, form);
    } else {
      await api.journalCreate(form);
    }
    resetForm();
    load();
  };

  const handleDelete = async (id: string) => {
    await api.journalDelete(id);
    if (editingId === id) resetForm();
    load();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <h1>Journal d'entraînement</h1>

      <form onSubmit={handleSubmit} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <h2>{editingId ? "Modifier l'entrée" : 'Nouvelle entrée'}</h2>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <label>
            Date
            <br />
            <input
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              required
            />
          </label>
          <label>
            Sport
            <br />
            <select
              value={form.sport}
              onChange={(e) => setForm({ ...form, sport: e.target.value as Sport })}
            >
              {SPORTS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label>
            RPE (1-10)
            <br />
            <input
              type="number"
              min={1}
              max={10}
              value={form.rpe ?? ''}
              onChange={(e) => setForm({ ...form, rpe: e.target.value ? Number(e.target.value) : null })}
            />
          </label>
          <label>
            Humeur (1-5)
            <br />
            <input
              type="number"
              min={1}
              max={5}
              value={form.mood ?? ''}
              onChange={(e) => setForm({ ...form, mood: e.target.value ? Number(e.target.value) : null })}
            />
          </label>
        </div>
        <label>
          Prévu
          <br />
          <textarea
            value={form.plannedNotes ?? ''}
            onChange={(e) => setForm({ ...form, plannedNotes: e.target.value })}
            rows={2}
            style={{ width: '100%' }}
          />
        </label>
        <label>
          Réalisé
          <br />
          <textarea
            value={form.actualNotes ?? ''}
            onChange={(e) => setForm({ ...form, actualNotes: e.target.value })}
            rows={2}
            style={{ width: '100%' }}
          />
        </label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button type="submit">{editingId ? 'Enregistrer' : 'Ajouter'}</button>
          {editingId && (
            <button type="button" onClick={resetForm}>
              Annuler
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p className="muted">Chargement…</p>
      ) : (
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {entries.map((entry) => (
            <li key={entry.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
              <div>
                <div style={{ fontWeight: 600 }}>
                  {entry.date} {entry.sport && `· ${entry.sport}`} {entry.rpe && `· RPE ${entry.rpe}`}
                </div>
                {entry.plannedNotes && <div className="secondary">Prévu : {entry.plannedNotes}</div>}
                {entry.actualNotes && <div className="secondary">Réalisé : {entry.actualNotes}</div>}
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                <button type="button" onClick={() => startEdit(entry)}>
                  Éditer
                </button>
                <button type="button" onClick={() => handleDelete(entry.id)}>
                  Supprimer
                </button>
              </div>
            </li>
          ))}
          {entries.length === 0 && <p className="muted">Aucune entrée pour le moment.</p>}
        </ul>
      )}
    </div>
  );
}
