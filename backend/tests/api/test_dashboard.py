def test_dashboard_summary_works_before_any_sync(client):
    """The dbt marts don't exist yet (no sync has run) -- WarehouseReader should degrade to
    empty results rather than error, and the dashboard should still return a phase + banner
    recommendation from the plan alone."""
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["phase"] in {"base", "build", "peak", "taper", "race_week", "post"}
    assert body["todayWellness"] is None
    assert body["weeklyVolume"] == []
    assert body["recentWellness"] == []
    assert body["lastSyncAt"] is None
    assert len(body["recommendations"]) >= 1
    assert body["recommendations"][0]["id"] == "0"
    assert isinstance(body["daysUntilRace"], int)


def test_dashboard_summary_accepts_sport_filter(client):
    resp = client.get("/api/dashboard/summary", params={"sport": "running"})
    assert resp.status_code == 200
    assert resp.json()["weeklyVolume"] == []
