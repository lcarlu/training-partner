def test_journal_crud_roundtrip(client):
    create_resp = client.post(
        "/api/journal",
        json={
            "date": "2026-06-01",
            "sport": "running",
            "plannedNotes": "10km facile",
            "actualNotes": None,
            "rpe": None,
            "mood": None,
            "linkedActivityId": None,
        },
    )
    assert create_resp.status_code == 201
    entry = create_resp.json()
    assert entry["date"] == "2026-06-01"
    entry_id = entry["id"]

    list_resp = client.get("/api/journal")
    assert list_resp.status_code == 200
    assert any(e["id"] == entry_id for e in list_resp.json())

    update_resp = client.put(
        f"/api/journal/{entry_id}",
        json={
            "date": "2026-06-01",
            "sport": "running",
            "plannedNotes": "10km facile",
            "actualNotes": "fait, RAS",
            "rpe": 4,
            "mood": 4,
            "linkedActivityId": None,
        },
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["actualNotes"] == "fait, RAS"

    delete_resp = client.delete(f"/api/journal/{entry_id}")
    assert delete_resp.status_code == 204

    get_after_delete = client.get("/api/journal")
    assert not any(e["id"] == entry_id for e in get_after_delete.json())


def test_update_unknown_journal_entry_404s(client):
    resp = client.put(
        "/api/journal/does-not-exist",
        json={"date": "2026-06-01", "sport": "running"},
    )
    assert resp.status_code == 404
