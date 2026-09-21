def test_get_plan_creates_default(client):
    resp = client.get("/api/plan")
    assert resp.status_code == 200
    body = resp.json()
    assert body["raceDate"] == "2027-04-11"
    assert body["phase"] in {"base", "build", "peak", "taper", "race_week", "post"}
    assert body["weeksToRace"] > 0
    assert len(body["phases"]) == 6
    assert {p["phase"] for p in body["phases"]} == {
        "base",
        "build",
        "peak",
        "taper",
        "race_week",
        "post",
    }
    # phases should be contiguous and end at the race date
    race_week = next(p for p in body["phases"] if p["phase"] == "race_week")
    assert race_week["end"] == "2027-04-11"


def test_update_plan(client):
    resp = client.post(
        "/api/plan",
        json={"name": "Marathon de Paris", "raceDate": "2027-04-11", "targetTimeSeconds": 12600},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Marathon de Paris"
    assert body["targetTimeSeconds"] == 12600

    # the update should persist as the new "current" plan
    get_resp = client.get("/api/plan")
    assert get_resp.json()["name"] == "Marathon de Paris"
