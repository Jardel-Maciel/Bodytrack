def test_checkin_upsert_creates_then_updates_same_day(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)
    base_url = f"/api/v1/projects/{project.id}/checkins"

    payload = {"project_id": str(project.id), "date": "2026-09-18", "weight_kg": 100, "water_liters": 2.0}
    resp = client.post(base_url, json=payload, headers=headers)
    assert resp.status_code == 201
    checkin_id = resp.json()["id"]

    # Reenviar no MESMO dia deve ATUALIZAR o registro existente, não criar um segundo.
    payload["weight_kg"] = 99.5
    resp = client.post(base_url, json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["id"] == checkin_id
    assert resp.json()["weight_kg"] == 99.5

    resp = client.get(base_url, headers=headers)
    assert len(resp.json()) == 1


def test_checkin_requires_owned_project(client, make_user, make_project, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    payload = {"project_id": str(project_a.id), "date": "2026-09-18", "weight_kg": 90}
    resp = client.post(
        f"/api/v1/projects/{project_a.id}/checkins", json=payload, headers=auth_headers(user_b)
    )
    assert resp.status_code == 404


def test_checkin_date_range_filter(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)
    base_url = f"/api/v1/projects/{project.id}/checkins"

    for d in ["2026-01-01", "2026-01-10", "2026-02-01"]:
        client.post(base_url, json={"project_id": str(project.id), "date": d}, headers=headers)

    resp = client.get(base_url, params={"start": "2026-01-01", "end": "2026-01-31"}, headers=headers)
    assert [c["date"] for c in resp.json()] == ["2026-01-01", "2026-01-10"]
