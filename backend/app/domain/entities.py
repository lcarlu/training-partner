from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class Sport(StrEnum):
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    STRENGTH = "strength"
    OTHER = "other"


class Phase(StrEnum):
    BASE = "base"
    BUILD = "build"
    PEAK = "peak"
    TAPER = "taper"
    RACE_WEEK = "race_week"
    POST = "post"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"


@dataclass(frozen=True, slots=True)
class Activity:
    id: str
    sport: Sport
    name: str
    start_time: datetime
    duration_s: float
    distance_m: float | None
    avg_hr: int | None
    max_hr: int | None
    calories: float | None
    elevation_gain_m: float | None
    training_effect_aerobic: float | None
    training_effect_anaerobic: float | None


@dataclass(frozen=True, slots=True)
class WellnessDay:
    day: date
    resting_hr: int | None
    hrv_status: str | None
    hrv_last_night_avg: float | None
    body_battery_min: int | None
    body_battery_max: int | None
    stress_avg: int | None
    sleep_score: int | None
    sleep_duration_s: float | None
    vo2max_running: float | None
    vo2max_cycling: float | None
    training_readiness_score: int | None
    training_status: str | None


@dataclass(frozen=True, slots=True)
class PhaseInfo:
    phase: Phase
    weeks_to_race: float
    race_date: date


@dataclass(frozen=True, slots=True)
class PhaseBounds:
    phase: Phase
    start: date
    end: date


@dataclass(frozen=True, slots=True)
class Recommendation:
    severity: Severity
    title: str
    detail: str


@dataclass(frozen=True, slots=True)
class JournalEntry:
    id: str | None
    day: date
    sport: Sport
    planned_notes: str | None
    actual_notes: str | None
    rpe: int | None
    mood: int | None
    linked_activity_id: str | None


@dataclass(frozen=True, slots=True)
class TrainingPlan:
    id: str | None
    name: str
    race_date: date
    target_time_seconds: int | None
