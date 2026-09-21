from datetime import date, timedelta

from app.domain.entities import Phase, PhaseInfo, Severity, WellnessDay
from app.domain.recommendations import generate_recommendations


def _wellness_day(day: date, **overrides) -> WellnessDay:
    base = {
        "day": day,
        "resting_hr": 50,
        "hrv_status": "BALANCED",
        "hrv_last_night_avg": 60.0,
        "body_battery_min": 20,
        "body_battery_max": 90,
        "stress_avg": 30,
        "sleep_score": 80,
        "sleep_duration_s": 27000.0,
        "vo2max_running": 50.0,
        "vo2max_cycling": None,
        "training_readiness_score": 75,
        "training_status": "PRODUCTIVE",
    }
    base.update(overrides)
    return WellnessDay(**base)


def _phase_info(phase: Phase = Phase.BUILD, weeks_to_race: float = 20.0) -> PhaseInfo:
    return PhaseInfo(phase=phase, weeks_to_race=weeks_to_race, race_date=date(2027, 4, 11))


def test_always_includes_phase_banner():
    recs = generate_recommendations(_phase_info(), recent_wellness=[], weekly_volume_km=[])
    assert len(recs) == 1
    assert recs[0].severity == Severity.INFO


def test_flags_risky_training_status():
    today = date(2026, 6, 1)
    days = [
        _wellness_day(today - timedelta(days=i), training_status="OVERREACHING")
        for i in range(3, -1, -1)
    ]
    recs = generate_recommendations(_phase_info(), recent_wellness=days, weekly_volume_km=[])
    assert any(r.severity == Severity.WARNING and "Overreaching" in r.title for r in recs)


def test_flags_low_hrv():
    today = date(2026, 6, 1)
    days = [_wellness_day(today - timedelta(days=i), hrv_status="LOW") for i in range(3, -1, -1)]
    recs = generate_recommendations(_phase_info(), recent_wellness=days, weekly_volume_km=[])
    assert any("HRV" in r.title for r in recs)


def test_flags_low_readiness_as_alert():
    today = date(2026, 6, 1)
    days = [
        _wellness_day(today - timedelta(days=i), training_readiness_score=20)
        for i in range(3, -1, -1)
    ]
    recs = generate_recommendations(_phase_info(), recent_wellness=days, weekly_volume_km=[])
    alert = next(r for r in recs if "readiness" in r.title.lower())
    assert alert.severity == Severity.ALERT


def test_flags_rapid_volume_increase():
    recs = generate_recommendations(
        _phase_info(), recent_wellness=[], weekly_volume_km=[20.0, 35.0]
    )
    assert any("volume" in r.title.lower() for r in recs)


def test_base_phase_encourages_building_volume_when_flat():
    recs = generate_recommendations(
        _phase_info(phase=Phase.BASE, weeks_to_race=40.0),
        recent_wellness=[],
        weekly_volume_km=[30.0, 28.0],
    )
    assert any("Base" in r.title for r in recs)
