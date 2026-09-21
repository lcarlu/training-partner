export type Sport = 'running' | 'cycling' | 'swimming' | 'strength';

export const SPORTS: Sport[] = ['running', 'cycling', 'swimming', 'strength'];

export type SportFilter = Sport | 'all';

export type TrainingPhase = 'base' | 'build' | 'peak' | 'taper' | 'race_week' | 'post';

export interface Activity {
  id: string;
  sport: Sport;
  name: string;
  startTime: string; // ISO 8601
  durationSeconds: number;
  distanceMeters: number | null;
  avgHeartRate: number | null;
  maxHeartRate: number | null;
  avgPaceSecPerKm: number | null;
  elevationGainMeters: number | null;
  calories: number | null;
  trainingEffectAerobic: number | null;
  trainingEffectAnaerobic: number | null;
}

export interface ActivityListResponse {
  items: Activity[];
  total: number;
}

export interface DailyWellness {
  date: string; // YYYY-MM-DD
  restingHeartRate: number | null;
  /** Raw Garmin status string (e.g. "BALANCED"/"UNBALANCED"/"LOW") -- not yet verified against
   * live data, so kept generic rather than a guessed literal union. */
  hrvStatus: string | null;
  hrvValueMs: number | null;
  bodyBatteryMax: number | null;
  bodyBatteryMin: number | null;
  stressAvg: number | null;
  sleepScore: number | null;
  sleepDurationSeconds: number | null;
  vo2max: number | null;
  trainingReadinessScore: number | null;
  trainingStatus: string | null;
}

export interface WeeklyVolumePoint {
  weekStart: string; // YYYY-MM-DD
  bySport: Partial<Record<Sport, number>>; // minutes
}

export type RecommendationSeverity = 'info' | 'warning' | 'alert';

export interface Recommendation {
  id: string;
  severity: RecommendationSeverity;
  title: string;
  detail: string;
}

export interface DashboardSummary {
  raceDate: string;
  daysUntilRace: number;
  phase: TrainingPhase;
  weeklyVolume: WeeklyVolumePoint[];
  recentWellness: DailyWellness[];
  todayWellness: DailyWellness | null;
  recommendations: Recommendation[];
  lastSyncAt: string | null;
}

export interface JournalEntry {
  id: string;
  date: string;
  sport: Sport;
  plannedNotes: string | null;
  actualNotes: string | null;
  rpe: number | null;
  mood: number | null;
  linkedActivityId: string | null;
}

export type JournalEntryInput = Omit<JournalEntry, 'id'>;

export interface TrainingPlanPhaseBounds {
  phase: TrainingPhase;
  start: string;
  end: string;
}

export interface TrainingPlan {
  raceDate: string;
  targetTimeSeconds: number | null;
  phases: TrainingPlanPhaseBounds[];
}

export interface SyncSummary {
  startedAt: string;
  finishedAt: string;
  counts: Record<string, number>;
}
