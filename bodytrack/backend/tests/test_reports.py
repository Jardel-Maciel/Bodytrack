def test_generate_weekly_report(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    for d, w in [("2026-01-01", 100), ("2026-01-03", 99)]:
        client.post(
            f"/api/v1/projects/{project.id}/checkins",
            json={
                "project_id": str(project.id),
                "date": d,
                "weight_kg": w,
                "water_liters": 3,
                "followed_diet": True,
                "hit_protein_goal": False,
            },
            headers=headers,
        )

    resp = client.post(
        f"/api/v1/projects/{project.id}/reports/generate", json={"week_number": 1}, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["summary"]["weight_start_kg"] == 100
    assert body["summary"]["weight_end_kg"] == 99
    assert body["summary"]["days_registered"] == 2
    # 2 True/False registrados de cada campo -> 2 True em 4 flags = 50%
    assert body["summary"]["diet_adherence_pct"] == 50.0


def test_export_json_and_csv(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    client.post(
        f"/api/v1/projects/{project.id}/checkins",
        json={"project_id": str(project.id), "date": "2026-01-01", "weight_kg": 100},
        headers=headers,
    )

    resp = client.get(
        f"/api/v1/projects/{project.id}/reports/export", params={"format": "json"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["checkins"][0]["weight_kg"] == 100

    resp = client.get(
        f"/api/v1/projects/{project.id}/reports/export", params={"format": "csv"}, headers=headers
    )
    assert resp.status_code == 200
    assert "checkin,2026-01-01,weight_kg,100" in resp.text


def test_report_pdf_download(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    resp = client.post(
        f"/api/v1/projects/{project.id}/reports/generate", json={"week_number": 1}, headers=headers
    )
    report_id = resp.json()["id"]

    resp = client.get(f"/api/v1/projects/{project.id}/reports/{report_id}/pdf", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"


def test_report_isolated_by_user(client, make_user, make_project, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    resp = client.post(
        f"/api/v1/projects/{project_a.id}/reports/generate",
        json={"week_number": 1},
        headers=auth_headers(user_b),
    )
    assert resp.status_code == 404
