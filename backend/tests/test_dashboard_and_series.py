def test_dashboard_aggregates_project_data(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user, initial_weight_kg=127)
    headers = auth_headers(user)

    client.post(
        f"/api/v1/projects/{project.id}/checkins",
        json={"project_id": str(project.id), "date": "2026-01-01", "weight_kg": 127},
        headers=headers,
    )
    client.post(
        f"/api/v1/projects/{project.id}/checkins",
        json={"project_id": str(project.id), "date": "2026-01-08", "weight_kg": 124.5},
        headers=headers,
    )
    client.post(
        f"/api/v1/projects/{project.id}/measurements",
        json={"project_id": str(project.id), "date": "2026-01-08", "waist_cm": 118},
        headers=headers,
    )

    resp = client.get(f"/api/v1/projects/{project.id}/dashboard", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["initial_weight_kg"] == 127
    assert body["current_weight_kg"] == 124.5
    assert body["weight_variation_kg"] == -2.5
    assert body["waist_cm"] == 118
    assert body["week_of_project"] >= 1


def test_dashboard_requires_owned_project(client, make_user, make_project, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    resp = client.get(f"/api/v1/projects/{project_a.id}/dashboard", headers=auth_headers(user_b))
    assert resp.status_code == 404


def test_weight_series_returns_points_in_order(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    for d, w in [("2026-01-01", 100), ("2026-01-02", 99.5), ("2026-01-05", 98)]:
        client.post(
            f"/api/v1/projects/{project.id}/checkins",
            json={"project_id": str(project.id), "date": d, "weight_kg": w},
            headers=headers,
        )

    resp = client.get(
        f"/api/v1/projects/{project.id}/series",
        params={"metric": "weight_kg", "period": "project"},
        headers=headers,
    )
    assert resp.status_code == 200
    points = resp.json()["points"]
    assert [p["value"] for p in points] == [100, 99.5, 98]


def test_series_rejects_invalid_metric(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    resp = client.get(
        f"/api/v1/projects/{project.id}/series",
        params={"metric": "nao_existe"},
        headers=auth_headers(user),
    )
    assert resp.status_code == 400
