from app.api.schemas.activity import ActivityRead


def _base_kwargs(**overrides):
    kwargs = {
        "id": "a1",
        "sport": "running",
        "name": "Sortie longue",
        "start_time": "2026-06-01T08:00:00",
        "duration_s": 3600,
        "distance_m": 10000,
        "avg_hr": 150,
        "max_hr": 170,
        "calories": 700,
        "elevation_gain_m": 50,
        "training_effect_aerobic": 3.0,
        "training_effect_anaerobic": 1.0,
    }
    kwargs.update(overrides)
    return kwargs


def test_avg_pace_computed_from_duration_and_distance():
    activity = ActivityRead(**_base_kwargs())
    body = activity.model_dump(by_alias=True)
    assert body["avgPaceSecPerKm"] == 360  # 3600s / 10km


def test_avg_pace_is_none_without_distance():
    activity = ActivityRead(**_base_kwargs(distance_m=None))
    body = activity.model_dump(by_alias=True)
    assert body["avgPaceSecPerKm"] is None


def test_activities_list_endpoint_returns_items_and_total(client):
    resp = client.get("/api/activities")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"items": [], "total": 0}
