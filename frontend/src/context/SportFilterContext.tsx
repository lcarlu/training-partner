import { createContext, useContext, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import type { SportFilter } from '../client/types';

interface SportFilterContextValue {
  sport: SportFilter;
  setSport: (sport: SportFilter) => void;
}

const SportFilterContext = createContext<SportFilterContextValue | null>(null);

export function SportFilterProvider({ children }: { children: ReactNode }) {
  const [sport, setSport] = useState<SportFilter>('all');
  const value = useMemo(() => ({ sport, setSport }), [sport]);
  return <SportFilterContext.Provider value={value}>{children}</SportFilterContext.Provider>;
}

export function useSportFilter(): SportFilterContextValue {
  const ctx = useContext(SportFilterContext);
  if (!ctx) throw new Error('useSportFilter must be used within SportFilterProvider');
  return ctx;
}
