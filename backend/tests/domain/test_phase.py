from datetime import date

from app.domain.entities import Phase
from app.domain.phase import compute_phase, compute_phase_bounds


def test_base_phase_far_from_race():
    info = compute_phase(race_date=date(2027, 4, 11), today=date(2026, 1, 1))
    assert info.phase == Phase.BASE
    assert info.weeks_to_race > 32


def test_build_phase():
    info = compute_phase(race_date=date(2027, 4, 11), today=date(2026, 10, 1))
    assert info.phase == Phase.BUILD


def test_peak_phase():
    info = compute_phase(race_date=date(2027, 4, 11), today=date(2027, 1, 15))
    assert info.phase == Phase.PEAK


def test_taper_phase():
    info = compute_phase(race_date=date(2027, 4, 11), today=date(2027, 3, 25))
    assert info.phase == Phase.TAPER


def test_race_week():
    info = compute_phase(race_date=date(2027, 4, 11), today=date(2027, 4, 10))
    assert info.phase == Phase.RACE_WEEK


def test_post_race():
    info = compute_phase(race_date=date(2027, 4, 11), today=date(2027, 4, 20))
    assert info.phase == Phase.POST
    assert info.weeks_to_race < 0


def test_phase_bounds_are_contiguous_and_ordered():
    race_date = date(2027, 4, 11)
    bounds = compute_phase_bounds(race_date)
    assert [b.phase for b in bounds] == [
        Phase.BASE,
        Phase.BUILD,
        Phase.PEAK,
        Phase.TAPER,
        Phase.RACE_WEEK,
        Phase.POST,
    ]
    for earlier, later in zip(bounds, bounds[1:], strict=False):
        assert earlier.end == later.start
    assert bounds[0].start < bounds[0].end
    assert bounds[-2].end == race_date  # race_week ends on race day
    assert bounds[-1].start == race_date  # post starts on race day
