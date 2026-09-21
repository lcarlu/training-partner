from datetime import date, timedelta

from app.domain.entities import Phase, PhaseBounds, PhaseInfo

_BASE_WEEKS_THRESHOLD = 32
_BUILD_WEEKS_THRESHOLD = 16
_TAPER_WEEKS_THRESHOLD = 3
_RACE_WEEK_THRESHOLD = 1

_DISPLAY_BASE_START_WEEKS = 52
"""Arbitrary display-only start for the Base phase timeline (Base itself has no real start --
training can begin whenever) so `compute_phase_bounds` returns a bounded range."""
_DISPLAY_POST_END_WEEKS = 4
"""Arbitrary display-only end for the Post phase timeline, same reasoning."""


def compute_phase(race_date: date, today: date) -> PhaseInfo:
    weeks_to_race = (race_date - today).days / 7

    if weeks_to_race < 0:
        phase = Phase.POST
    elif weeks_to_race <= _RACE_WEEK_THRESHOLD:
        phase = Phase.RACE_WEEK
    elif weeks_to_race <= _TAPER_WEEKS_THRESHOLD:
        phase = Phase.TAPER
    elif weeks_to_race <= _BUILD_WEEKS_THRESHOLD:
        phase = Phase.PEAK
    elif weeks_to_race <= _BASE_WEEKS_THRESHOLD:
        phase = Phase.BUILD
    else:
        phase = Phase.BASE

    return PhaseInfo(phase=phase, weeks_to_race=round(weeks_to_race, 1), race_date=race_date)


def compute_phase_bounds(race_date: date) -> list[PhaseBounds]:
    """Calendar date ranges for each phase, from the same thresholds as `compute_phase`.
    Base's start and Post's end are arbitrary display bounds (see module docstrings above) --
    there's no real "training block length" concept here, just a countdown to race day."""

    def weeks_before(weeks: float) -> date:
        return race_date - timedelta(days=round(weeks * 7))

    def weeks_after(weeks: float) -> date:
        return race_date + timedelta(days=round(weeks * 7))

    return [
        PhaseBounds(
            phase=Phase.BASE,
            start=weeks_before(_DISPLAY_BASE_START_WEEKS),
            end=weeks_before(_BASE_WEEKS_THRESHOLD),
        ),
        PhaseBounds(
            phase=Phase.BUILD,
            start=weeks_before(_BASE_WEEKS_THRESHOLD),
            end=weeks_before(_BUILD_WEEKS_THRESHOLD),
        ),
        PhaseBounds(
            phase=Phase.PEAK,
            start=weeks_before(_BUILD_WEEKS_THRESHOLD),
            end=weeks_before(_TAPER_WEEKS_THRESHOLD),
        ),
        PhaseBounds(
            phase=Phase.TAPER,
            start=weeks_before(_TAPER_WEEKS_THRESHOLD),
            end=weeks_before(_RACE_WEEK_THRESHOLD),
        ),
        PhaseBounds(
            phase=Phase.RACE_WEEK,
            start=weeks_before(_RACE_WEEK_THRESHOLD),
            end=race_date,
        ),
        PhaseBounds(
            phase=Phase.POST,
            start=race_date,
            end=weeks_after(_DISPLAY_POST_END_WEEKS),
        ),
    ]
