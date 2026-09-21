import { useCallback, useState } from 'react';
import { api } from '../client/endpoints';
import type { SyncSummary } from '../client/types';

interface UseSyncResult {
  syncing: boolean;
  error: string | null;
  lastSync: SyncSummary | null;
  runSync: () => Promise<void>;
}

export function useSync(): UseSyncResult {
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<SyncSummary | null>(null);

  const runSync = useCallback(async () => {
    setSyncing(true);
    setError(null);
    try {
      const summary = await api.sync();
      setLastSync(summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Échec de la synchronisation');
    } finally {
      setSyncing(false);
    }
  }, []);

  return { syncing, error, lastSync, runSync };
}
