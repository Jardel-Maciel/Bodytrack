def test_first_checkin_unlocks_achievement(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    client.post(
        f"/api/v1/projects/{project.id}/checkins",
        json={"project_id": str(project.id), "date": "2026-09-18"},
        headers=headers,
    )

    resp = client.get(f"/api/v1/projects/{project.id}/achievements", headers=headers)
    assert resp.status_code == 200
    codes = {a["code"] for a in resp.json()}
    assert "first_checkin" in codes


def test_achievements_isolated_by_user(client, make_user, make_project, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    resp = client.get(f"/api/v1/projects/{project_a.id}/achievements", headers=auth_headers(user_b))
    assert resp.status_code == 404
