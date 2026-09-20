import { apiClient } from './apiClient';
import { mockApi } from './mockData';
import type {
  Activity,
  ActivityListResponse,
  DailyWellness,
  DashboardSummary,
  JournalEntry,
  JournalEntryInput,
  SportFilter,
  SyncSummary,
  TrainingPlan,
} from './types';

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

export const api = {
  sync: (): Promise<SyncSummary> =>
    USE_MOCKS ? mockApi.sync() : apiClient.post<SyncSummary>('/api/sync/refresh'),

  dashboardSummary: (sport: SportFilter): Promise<DashboardSummary> => {
    if (USE_MOCKS) return mockApi.dashboardSummary(sport);
    const qs = sport === 'all' ? '' : `?sport=${sport}`;
    return apiClient.get<DashboardSummary>(`/api/dashboard/summary${qs}`);
  },

  activities: (params: {
    sport?: SportFilter;
    from?: string;
    to?: string;
    limit?: number;
  }): Promise<ActivityListResponse> => {
    if (USE_MOCKS) return mockApi.activities(params);
    const qs = new URLSearchParams();
    if (params.sport && params.sport !== 'all') qs.set('sport', params.sport);
    if (params.from) qs.set('from', params.from);
    if (params.to) qs.set('to', params.to);
    if (params.limit) qs.set('limit', String(params.limit));
    return apiClient.get<ActivityListResponse>(`/api/activities?${qs.toString()}`);
  },

  activity: (id: string): Promise<Activity | undefined> =>
    USE_MOCKS ? mockApi.activity(id) : apiClient.get<Activity>(`/api/activities/${id}`),

  wellness: (): Promise<DailyWellness[]> =>
    USE_MOCKS ? mockApi.wellness() : apiClient.get<DailyWellness[]>('/api/wellness/daily'),

  journalList: (): Promise<JournalEntry[]> =>
    USE_MOCKS ? mockApi.journalList() : apiClient.get<JournalEntry[]>('/api/journal'),

  journalCreate: (input: JournalEntryInput): Promise<JournalEntry> =>
    USE_MOCKS ? mockApi.journalCreate(input) : apiClient.post<JournalEntry>('/api/journal', input),

  journalUpdate: (id: string, input: JournalEntryInput): Promise<JournalEntry> =>
    USE_MOCKS
      ? mockApi.journalUpdate(id, input)
      : apiClient.put<JournalEntry>(`/api/journal/${id}`, input),

  journalDelete: (id: string): Promise<void> =>
    USE_MOCKS ? mockApi.journalDelete(id) : apiClient.delete<void>(`/api/journal/${id}`),

  plan: (): Promise<TrainingPlan> =>
    USE_MOCKS ? mockApi.plan() : apiClient.get<TrainingPlan>('/api/plan'),

  planUpdate: (input: TrainingPlan): Promise<TrainingPlan> =>
    USE_MOCKS ? mockApi.planUpdate(input) : apiClient.post<TrainingPlan>('/api/plan', input),
};
