def _create_workout(client, project_id, headers):
    payload = {
        "name": "Treino A",
        "muscle_group": "Peito e tríceps",
        "exercises": [
            {"name": "Supino reto", "order": 0, "target_sets": 3, "target_reps": "8-10"},
            {"name": "Tríceps corda", "order": 1, "target_sets": 3, "target_reps": "10-12"},
        ],
    }
    return client.post(f"/api/v1/projects/{project_id}/workouts", json=payload, headers=headers)


def test_create_workout_with_exercises(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    resp = _create_workout(client, project.id, auth_headers(user))
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Treino A"
    assert len(body["exercises"]) == 2


def test_log_session_and_compute_volume(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    workout = _create_workout(client, project.id, headers).json()
    supino_id = workout["exercises"][0]["id"]

    session_payload = {
        "date": "2026-09-18",
        "sets": [
            {"workout_exercise_id": supino_id, "set_number": 1, "reps": 10, "load_kg": 50},
            {"workout_exercise_id": supino_id, "set_number": 2, "reps": 10, "load_kg": 50},
            {"workout_exercise_id": supino_id, "set_number": 3, "reps": 8, "load_kg": 55},
        ],
    }
    resp = client.post(
        f"/api/v1/projects/{project.id}/workouts/{workout['id']}/sessions",
        json=session_payload,
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    # volume = (10*50) + (10*50) + (8*55) = 500 + 500 + 440 = 1440
    assert body["total_volume_kg"] == 1440


def test_exercise_progress_compares_last_two_sessions(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    workout = _create_workout(client, project.id, headers).json()
    supino_id = workout["exercises"][0]["id"]
    sessions_url = f"/api/v1/projects/{project.id}/workouts/{workout['id']}/sessions"

    client.post(
        sessions_url,
        json={
            "date": "2026-09-01",
            "sets": [{"workout_exercise_id": supino_id, "set_number": 1, "reps": 8, "load_kg": 55}],
        },
        headers=headers,
    )
    client.post(
        sessions_url,
        json={
            "date": "2026-09-08",
            "sets": [{"workout_exercise_id": supino_id, "set_number": 1, "reps": 8, "load_kg": 60}],
        },
        headers=headers,
    )

    resp = client.get(
        f"/api/v1/projects/{project.id}/workouts/{workout['id']}/exercises/{supino_id}/progress",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["last_session"]["best_set_load_kg"] == 60
    assert body["previous_session"]["best_set_load_kg"] == 55
    assert body["load_delta_kg"] == 5


def test_cannot_log_set_for_exercise_from_another_workout(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    workout_a = _create_workout(client, project.id, headers).json()
    resp_b = client.post(
        f"/api/v1/projects/{project.id}/workouts",
        json={"name": "Treino B", "exercises": [{"name": "Agachamento"}]},
        headers=headers,
    )
    exercise_from_b = resp_b.json()["exercises"][0]["id"]

    resp = client.post(
        f"/api/v1/projects/{project.id}/workouts/{workout_a['id']}/sessions",
        json={
            "date": "2026-09-18",
            "sets": [{"workout_exercise_id": exercise_from_b, "set_number": 1, "reps": 10, "load_kg": 40}],
        },
        headers=headers,
    )
    assert resp.status_code == 400


def test_workout_isolated_by_user(client, make_user, make_project, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    resp = _create_workout(client, project_a.id, auth_headers(user_b))
    assert resp.status_code == 404
