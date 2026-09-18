def test_measurement_progress_compares_first_and_last(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)
    base_url = f"/api/v1/projects/{project.id}/measurements"

    client.post(
        base_url,
        json={"project_id": str(project.id), "date": "2026-01-01", "waist_cm": 124, "hip_cm": 110},
        headers=headers,
    )
    client.post(
        base_url,
        # abdomen_cm só aparece na segunda medida — não deve quebrar o cálculo
        json={"project_id": str(project.id), "date": "2026-02-01", "waist_cm": 118, "abdomen_cm": 100},
        headers=headers,
    )

    resp = client.get(f"{base_url}/progress", headers=headers)
    assert resp.status_code == 200
    by_field = {f["field"]: f for f in resp.json()["fields"]}

    assert by_field["waist_cm"]["initial_value"] == 124
    assert by_field["waist_cm"]["current_value"] == 118
    assert by_field["waist_cm"]["variation"] == -6

    # hip só existe na primeira medida, abdomen só na segunda — sem par completo, sem variação.
    assert by_field["hip_cm"]["variation"] is None
    assert by_field["abdomen_cm"]["variation"] is None


def test_measurement_isolated_by_user(client, make_user, make_project, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    resp = client.post(
        f"/api/v1/projects/{project_a.id}/measurements",
        json={"project_id": str(project_a.id), "date": "2026-01-01", "waist_cm": 120},
        headers=auth_headers(user_b),
    )
    assert resp.status_code == 404
