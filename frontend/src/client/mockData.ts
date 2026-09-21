import type {
  Activity,
  DailyWellness,
  DashboardSummary,
  JournalEntry,
  JournalEntryInput,
  Recommendation,
  Sport,
  SportFilter,
  SyncSummary,
  TrainingPlan,
  TrainingPhase,
  WeeklyVolumePoint,
} from './types';
import { SPORTS } from './types';

const RACE_DATE = '2027-04-11';

function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function daysBetween(from: Date, to: Date): number {
  return Math.round((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24));
}

// Mirrors the thresholds in backend/app/domain/phase.py::compute_phase.
export function computePhase(today: Date, raceDate: string): { phase: TrainingPhase; daysUntilRace: number } {
  const race = new Date(`${raceDate}T00:00:00`);
  const daysUntilRace = daysBetween(today, race);
  const weeksUntilRace = daysUntilRace / 7;
  const phase: TrainingPhase =
    daysUntilRace < 0
      ? 'post'
      : weeksUntilRace <= 1
        ? 'race_week'
        : weeksUntilRace <= 3
          ? 'taper'
          : weeksUntilRace <= 16
            ? 'peak'
            : weeksUntilRace <= 32
              ? 'build'
              : 'base';
  return { phase, daysUntilRace };
}

function addWeeks(d: Date, weeks: number): Date {
  const out = new Date(d);
  out.setDate(out.getDate() + Math.round(weeks * 7));
  return out;
}

function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const rand = seededRandom(42);

function buildWeeklyVolume(): WeeklyVolumePoint[] {
  const points: WeeklyVolumePoint[] = [];
  const now = new Date();
  for (let i = 11; i >= 0; i--) {
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - now.getDay() - i * 7);
    const base = 120 + (11 - i) * 6;
    points.push({
      weekStart: isoDate(weekStart),
      bySport: {
        running: Math.round(base + rand() * 40),
        cycling: Math.round(30 + rand() * 60),
        swimming: Math.round(rand() * 30),
        strength: Math.round(20 + rand() * 20),
      },
    });
  }
  return points;
}

function buildWellness(days: number): DailyWellness[] {
  const out: DailyWellness[] = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(now.getDate() - i);
    out.push({
      date: isoDate(d),
      restingHeartRate: Math.round(46 + rand() * 6),
      hrvStatus: rand() > 0.7 ? 'unbalanced' : 'balanced',
      hrvValueMs: Math.round(55 + rand() * 25),
      bodyBatteryMax: Math.round(70 + rand() * 30),
      bodyBatteryMin: Math.round(10 + rand() * 30),
      stressAvg: Math.round(15 + rand() * 30),
      sleepScore: Math.round(55 + rand() * 40),
      sleepDurationSeconds: Math.round((6 + rand() * 2) * 3600),
      vo2max: Math.round(48 + rand() * 4),
      trainingReadinessScore: Math.round(40 + rand() * 55),
      trainingStatus: ['PRODUCTIVE', 'MAINTAINING', 'RECOVERY', 'PEAKING'][Math.floor(rand() * 4)],
    });
  }
  return out;
}

const MOCK_WELLNESS = buildWellness(60);
const MOCK_WEEKLY_VOLUME = buildWeeklyVolume();

const SPORT_ACTIVITY_NAMES: Record<Sport, string[]> = {
  running: ['Sortie longue', 'Footing facile', 'Fractionné 10x400m', 'Seuil 20min', 'Récupération active'],
  cycling: ['Sortie route', 'Home trainer Zwift', 'Sortie endurance'],
  swimming: ['Séance technique', "Endurance piscine"],
  strength: ['Renfort bas du corps', 'Gainage & mobilité'],
};

function buildActivities(count: number): Activity[] {
  const out: Activity[] = [];
  const now = new Date();
  for (let i = 0; i < count; i++) {
    const sport = SPORTS[Math.floor(rand() * SPORTS.length)];
    const names = SPORT_ACTIVITY_NAMES[sport];
    const start = new Date(now);
    start.setDate(now.getDate() - i * 2 - Math.floor(rand() * 2));
    const durationMin = sport === 'strength' ? 30 + rand() * 30 : 30 + rand() * 90;
    const distanceKm = sport === 'strength' ? null : (durationMin / 60) * (sport === 'running' ? 10.5 : sport === 'cycling' ? 28 : 2.5);
    out.push({
      id: `mock-${i}`,
      sport,
      name: names[Math.floor(rand() * names.length)],
      startTime: start.toISOString(),
      durationSeconds: Math.round(durationMin * 60),
      distanceMeters: distanceKm ? Math.round(distanceKm * 1000) : null,
      avgHeartRate: sport === 'strength' ? null : Math.round(130 + rand() * 30),
      maxHeartRate: sport === 'strength' ? null : Math.round(160 + rand() * 25),
      avgPaceSecPerKm: sport === 'running' ? Math.round(270 + rand() * 60) : null,
      elevationGainMeters: sport === 'strength' ? null : Math.round(rand() * 300),
      calories: Math.round(durationMin * (sport === 'strength' ? 6 : 10)),
      trainingEffectAerobic: sport === 'strength' ? null : Math.round((2 + rand() * 3) * 10) / 10,
      trainingEffectAnaerobic: sport === 'strength' ? null : Math.round(rand() * 20) / 10,
    });
  }
  return out;
}

const MOCK_ACTIVITIES = buildActivities(40);

function buildRecommendations(phase: TrainingPhase): Recommendation[] {
  const recs: Recommendation[] = [
    {
      id: 'rec-phase',
      severity: 'info',
      title: `Phase actuelle : ${phase}`,
      detail: "Continue de suivre la progression de volume prévue pour cette phase.",
    },
  ];
  const recentHrv = MOCK_WELLNESS.slice(-7);
  const lowHrvDays = recentHrv.filter((w) => w.hrvStatus === 'unbalanced').length;
  if (lowHrvDays >= 3) {
    recs.push({
      id: 'rec-hrv',
      severity: 'warning',
      title: 'HRV instable sur les 7 derniers jours',
      detail: `${lowHrvDays} jours en "unbalanced" — envisage une semaine allégée ou une journée de récupération active.`,
    });
  }
  const lastStatus = MOCK_WELLNESS[MOCK_WELLNESS.length - 1]?.trainingStatus;
  if (lastStatus === 'RECOVERY') {
    recs.push({
      id: 'rec-status',
      severity: 'alert',
      title: 'Training status Garmin : Recovery',
      detail: 'Privilégie une séance facile ou du repos avant la prochaine séance de qualité.',
    });
  }
  return recs;
}

let journalStore: JournalEntry[] = [
  {
    id: 'j-1',
    date: isoDate(new Date()),
    sport: 'running',
    plannedNotes: 'Sortie longue 25km en endurance fondamentale',
    actualNotes: null,
    rpe: null,
    mood: null,
    linkedActivityId: null,
  },
];

// Mirrors backend/app/domain/phase.py::compute_phase_bounds (same thresholds/arbitrary display
// bounds for Base's start and Post's end).
function buildPhaseTimeline(raceDate: string): TrainingPlan['phases'] {
  const race = new Date(`${raceDate}T00:00:00`);
  const bound = (weeks: number) => isoDate(addWeeks(race, -weeks));
  return [
    { phase: 'base', start: bound(52), end: bound(32) },
    { phase: 'build', start: bound(32), end: bound(16) },
    { phase: 'peak', start: bound(16), end: bound(3) },
    { phase: 'taper', start: bound(3), end: bound(1) },
    { phase: 'race_week', start: bound(1), end: isoDate(race) },
    { phase: 'post', start: isoDate(race), end: isoDate(addWeeks(race, 4)) },
  ];
}

let planStore: TrainingPlan = {
  raceDate: RACE_DATE,
  targetTimeSeconds: 3 * 3600 + 30 * 60,
  phases: buildPhaseTimeline(RACE_DATE),
};

export const mockApi = {
  sync(): Promise<SyncSummary> {
    const now = new Date().toISOString();
    return Promise.resolve({
      startedAt: now,
      finishedAt: now,
      counts: { activities: 3, wellness: 1, body_composition: 1 },
    });
  },

  dashboardSummary(sport: SportFilter): Promise<DashboardSummary> {
    const { phase, daysUntilRace } = computePhase(new Date(), planStore.raceDate);
    const weeklyVolume =
      sport === 'all'
        ? MOCK_WEEKLY_VOLUME
        : MOCK_WEEKLY_VOLUME.map((p) => ({
            weekStart: p.weekStart,
            bySport: { [sport]: p.bySport[sport] ?? 0 },
          }));
    return Promise.resolve({
      raceDate: planStore.raceDate,
      daysUntilRace,
      phase,
      weeklyVolume,
      recentWellness: MOCK_WELLNESS.slice(-30),
      todayWellness: MOCK_WELLNESS[MOCK_WELLNESS.length - 1] ?? null,
      recommendations: buildRecommendations(phase),
      lastSyncAt: new Date().toISOString(),
    });
  },

  activities(params: { sport?: SportFilter; from?: string; to?: string; limit?: number }): Promise<{
    items: Activity[];
    total: number;
  }> {
    let items = MOCK_ACTIVITIES;
    if (params.sport && params.sport !== 'all') {
      items = items.filter((a) => a.sport === params.sport);
    }
    const total = items.length;
    if (params.limit) items = items.slice(0, params.limit);
    return Promise.resolve({ items, total });
  },

  activity(id: string): Promise<Activity | undefined> {
    return Promise.resolve(MOCK_ACTIVITIES.find((a) => a.id === id));
  },

  wellness(): Promise<DailyWellness[]> {
    return Promise.resolve(MOCK_WELLNESS);
  },

  journalList(): Promise<JournalEntry[]> {
    return Promise.resolve(journalStore);
  },

  journalCreate(input: JournalEntryInput): Promise<JournalEntry> {
    const entry: JournalEntry = { ...input, id: `j-${Date.now()}` };
    journalStore = [entry, ...journalStore];
    return Promise.resolve(entry);
  },

  journalUpdate(id: string, input: JournalEntryInput): Promise<JournalEntry> {
    journalStore = journalStore.map((e) => (e.id === id ? { ...input, id } : e));
    return Promise.resolve({ ...input, id });
  },

  journalDelete(id: string): Promise<void> {
    journalStore = journalStore.filter((e) => e.id !== id);
    return Promise.resolve();
  },

  plan(): Promise<TrainingPlan> {
    return Promise.resolve(planStore);
  },

  planUpdate(input: TrainingPlan): Promise<TrainingPlan> {
    planStore = { ...input, phases: buildPhaseTimeline(input.raceDate) };
    return Promise.resolve(planStore);
  },
};
