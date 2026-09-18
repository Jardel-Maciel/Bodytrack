def test_create_and_update_goal(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    resp = client.post(
        f"/api/v1/projects/{project.id}/goals",
        json={"type": "waist", "target_value": 100},
        headers=headers,
    )
    assert resp.status_code == 201
    goal_id = resp.json()["id"]
    assert resp.json()["achieved"] is False

    resp = client.patch(
        f"/api/v1/projects/{project.id}/goals/{goal_id}", json={"achieved": True}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["achieved"] is True


def test_goal_isolated_by_user(client, make_user, make_project, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    resp = client.post(
        f"/api/v1/projects/{project_a.id}/goals",
        json={"type": "weight", "target_value": 90},
        headers=auth_headers(user_b),
    )
    assert resp.status_code == 404
