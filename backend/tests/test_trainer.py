"""
Área do personal. Foco: isolamento (um personal nunca vê aluno que não é dele) e
consentimento (sem aceite / sem permissão do aluno, nada de fotos ou evolução).
"""
import io
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.trainer_link import TrainerStudentLink
from tests.test_photos import _tiny_png_bytes

API = "/api/v1"


@pytest.fixture()
def make_trainer(make_user, db_session):
    def _make(email="personal@example.com"):
        user = make_user(email=email)
        user.role = "trainer"
        db_session.commit()
        return user
    return _make


@pytest.fixture()
def linked(client, make_user, make_trainer, make_project, auth_headers):
    """Personal + aluno (com projeto) já vinculados. Aluno NÃO compartilha nada por padrão."""

    def _make(share_photos=False, share_progress=False, trainer_email="personal@example.com", student_email="aluno@example.com"):
        trainer = make_trainer(trainer_email)
        student = make_user(email=student_email)
        project = make_project(student)
        invite = client.post(f"{API}/trainer/invites", json={"student_label": "João"}, headers=auth_headers(trainer)).json()
        resp = client.post(
            f"{API}/trainer-links/accept",
            json={"code": invite["invite_code"], "share_photos": share_photos, "share_progress": share_progress},
            headers=auth_headers(student),
        )
        assert resp.status_code == 201, resp.text
        return trainer, student, project, invite["link_id"]
    return _make


def _workout_payload(**over):
    payload = {
        "name": "Treino A — Peito",
        "muscle_group": "Peito",
        "exercises": [
            {"name": "Supino reto", "target_sets": 4, "target_reps": "8-10", "rest_seconds": 90},
            {"name": "Tríceps corda", "target_sets": 3, "target_reps": "12"},
        ],
    }
    payload.update(over)
    return payload


# ------------------------------------------------------------------ papéis

def test_register_as_trainer_and_default_is_student(client):
    base = {"email": "a@x.com", "password": "senha12345", "name": "A"}
    assert client.post(f"{API}/auth/register", json=base).json()["role"] == "student"
    resp = client.post(f"{API}/auth/register", json={**base, "email": "b@x.com", "role": "trainer"})
    assert resp.json()["role"] == "trainer"


def test_user_can_switch_role_but_null_does_not_erase_it(client, make_user, auth_headers):
    user = make_user()
    h = auth_headers(user)
    assert client.patch(f"{API}/auth/me", json={"role": "trainer"}, headers=h).json()["role"] == "trainer"
    assert client.patch(f"{API}/auth/me", json={"role": None}, headers=h).json()["role"] == "trainer"
    assert client.patch(f"{API}/auth/me", json={"role": "admin"}, headers=h).status_code == 422


def test_student_cannot_use_trainer_routes(client, make_user, auth_headers):
    student = make_user()
    assert client.get(f"{API}/trainer/students", headers=auth_headers(student)).status_code == 403
    assert client.post(f"{API}/trainer/invites", json={}, headers=auth_headers(student)).status_code == 403
    assert client.get(f"{API}/trainer/students").status_code == 401


# ------------------------------------------------------------------ convites

def test_invite_flow_and_student_list(client, linked, auth_headers):
    trainer, student, _project, link_id = linked()
    rows = client.get(f"{API}/trainer/students", headers=auth_headers(trainer)).json()
    assert len(rows) == 1
    assert rows[0]["status"] == "active"
    assert rows[0]["display_name"] == student.name
    assert rows[0]["invite_code"] is None
    mine = client.get(f"{API}/trainer-links", headers=auth_headers(student)).json()
    assert mine[0]["trainer_name"] == trainer.name and mine[0]["link_id"] == link_id


def test_pending_invite_is_listed_with_code(client, make_trainer, auth_headers):
    trainer = make_trainer()
    invite = client.post(f"{API}/trainer/invites", json={"student_label": "Maria"}, headers=auth_headers(trainer)).json()
    assert len(invite["invite_code"]) == 8
    row = client.get(f"{API}/trainer/students", headers=auth_headers(trainer)).json()[0]
    assert row["status"] == "pending" and row["display_name"] == "Maria" and row["invite_code"] == invite["invite_code"]


def test_trainer_can_have_many_students(client, make_user, make_trainer, make_project, auth_headers):
    trainer = make_trainer()
    for i in range(5):
        student = make_user(email=f"aluno{i}@example.com")
        make_project(student)
        code = client.post(f"{API}/trainer/invites", json={}, headers=auth_headers(trainer)).json()["invite_code"]
        assert client.post(f"{API}/trainer-links/accept", json={"code": code}, headers=auth_headers(student)).status_code == 201
    rows = client.get(f"{API}/trainer/students", headers=auth_headers(trainer)).json()
    assert len(rows) == 5 and all(r["status"] == "active" for r in rows)


def test_invite_is_single_use_and_code_is_case_insensitive(client, make_user, make_trainer, auth_headers):
    trainer = make_trainer()
    code = client.post(f"{API}/trainer/invites", json={}, headers=auth_headers(trainer)).json()["invite_code"]
    s1, s2 = make_user(email="s1@x.com"), make_user(email="s2@x.com")
    assert client.post(f"{API}/trainer-links/accept", json={"code": code.lower()}, headers=auth_headers(s1)).status_code == 201
    assert client.post(f"{API}/trainer-links/accept", json={"code": code}, headers=auth_headers(s2)).status_code == 404


def test_invalid_expired_and_own_invites_are_rejected(client, make_user, make_trainer, auth_headers, db_session):
    trainer = make_trainer()
    student = make_user(email="s@x.com")
    assert client.post(f"{API}/trainer-links/accept", json={"code": "ZZZZZZZZ"}, headers=auth_headers(student)).status_code == 404

    invite = client.post(f"{API}/trainer/invites", json={}, headers=auth_headers(trainer)).json()
    assert client.post(f"{API}/trainer-links/accept", json={"code": invite["invite_code"]}, headers=auth_headers(trainer)).status_code == 400

    link = db_session.get(TrainerStudentLink, uuid.UUID(invite["link_id"]))
    link.invite_expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.commit()
    assert client.post(f"{API}/trainer-links/accept", json={"code": invite["invite_code"]}, headers=auth_headers(student)).status_code == 404
    assert client.get(f"{API}/trainer/students", headers=auth_headers(trainer)).json() == []  # vencido some da lista


def test_cannot_link_twice_to_same_trainer(client, linked, auth_headers):
    trainer, student, *_ = linked()
    code = client.post(f"{API}/trainer/invites", json={}, headers=auth_headers(trainer)).json()["invite_code"]
    assert client.post(f"{API}/trainer-links/accept", json={"code": code}, headers=auth_headers(student)).status_code == 409


# ------------------------------------------------------------------ isolamento

def test_other_trainer_cannot_touch_my_student(client, linked, make_trainer, auth_headers):
    _t, _s, _p, link_id = linked()
    intruder = make_trainer("intruso@example.com")
    h = auth_headers(intruder)
    for method, path, body in [
        ("get", f"/trainer/students/{link_id}/workouts", None),
        ("post", f"/trainer/students/{link_id}/workouts", _workout_payload()),
        ("get", f"/trainer/students/{link_id}/photos", None),
        ("get", f"/trainer/students/{link_id}/progress", None),
        ("delete", f"/trainer/students/{link_id}", None),
    ]:
        kwargs = {"json": body} if body else {}
        assert getattr(client, method)(f"{API}{path}", headers=h, **kwargs).status_code == 404, path


# ------------------------------------------------------------------ treinos

def test_trainer_builds_workout_in_student_project_and_student_sees_it(client, linked, auth_headers):
    trainer, student, project, link_id = linked()
    resp = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=auth_headers(trainer))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["editable"] is True and len(body["exercises"]) == 2
    assert body["exercises"][0]["catalog_id"] == "Barbell_Bench_Press_-_Medium_Grip"  # imagem de demonstração

    # o aluno enxerga o treino nas telas que já existiam
    seen = client.get(f"{API}/projects/{project.id}/workouts", headers=auth_headers(student)).json()
    assert [w["name"] for w in seen] == ["Treino A — Peito"]
    assert seen[0]["created_by_trainer_id"] == str(trainer.id)


def test_cannot_create_workout_when_student_has_no_project(client, make_user, make_trainer, auth_headers):
    trainer, student = make_trainer(), make_user(email="semprojeto@x.com")
    code = client.post(f"{API}/trainer/invites", json={}, headers=auth_headers(trainer)).json()["invite_code"]
    link_id = client.post(f"{API}/trainer-links/accept", json={"code": code}, headers=auth_headers(student)).json()["link_id"]
    resp = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=auth_headers(trainer))
    assert resp.status_code == 409


def test_update_keeps_exercise_ids_and_reorders(client, linked, auth_headers):
    trainer, _s, _p, link_id = linked()
    h = auth_headers(trainer)
    w = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=h).json()
    supino, triceps = w["exercises"]

    payload = {
        "name": "Treino A — Peito e tríceps",
        "exercises": [
            {"id": triceps["id"], "name": "Tríceps corda", "target_sets": 4},
            {"id": supino["id"], "name": "Supino reto", "target_sets": 5, "target_reps": "6-8"},
            {"name": "Crucifixo reto com halteres", "target_sets": 3},
        ],
    }
    resp = client.put(f"{API}/trainer/students/{link_id}/workouts/{w['id']}", json=payload, headers=h)
    assert resp.status_code == 200, resp.text
    exercises = resp.json()["exercises"]
    assert [e["name"] for e in exercises] == ["Tríceps corda", "Supino reto", "Crucifixo reto com halteres"]
    assert {e["id"] for e in exercises[:2]} == {supino["id"], triceps["id"]}  # mesmos IDs = histórico preservado
    assert exercises[1]["target_sets"] == 5


def test_cannot_remove_exercise_that_has_logged_sets(client, linked, auth_headers):
    trainer, student, project, link_id = linked()
    h = auth_headers(trainer)
    w = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=h).json()
    supino, triceps = w["exercises"]

    client.post(
        f"{API}/projects/{project.id}/workouts/{w['id']}/sessions",
        json={"date": "2026-10-01", "sets": [{"workout_exercise_id": supino["id"], "set_number": 1, "reps": 10, "load_kg": 40}]},
        headers=auth_headers(student),
    )
    only_triceps = {"name": w["name"], "exercises": [{"id": triceps["id"], "name": "Tríceps corda"}]}
    resp = client.put(f"{API}/trainer/students/{link_id}/workouts/{w['id']}", json=only_triceps, headers=h)
    assert resp.status_code == 409 and "Supino reto" in resp.json()["detail"]

    # exercício SEM histórico pode sair normalmente
    only_supino = {"name": w["name"], "exercises": [{"id": supino["id"], "name": "Supino reto"}]}
    assert client.put(f"{API}/trainer/students/{link_id}/workouts/{w['id']}", json=only_supino, headers=h).status_code == 200


def test_delete_workout_archives_when_student_has_history(client, linked, auth_headers):
    trainer, student, project, link_id = linked()
    h = auth_headers(trainer)
    clean = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(name="Sem uso"), headers=h).json()
    used = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(name="Usado"), headers=h).json()
    client.post(
        f"{API}/projects/{project.id}/workouts/{used['id']}/sessions",
        json={"date": "2026-10-01", "sets": [{"workout_exercise_id": used["exercises"][0]["id"], "set_number": 1, "reps": 8, "load_kg": 30}]},
        headers=auth_headers(student),
    )
    assert client.delete(f"{API}/trainer/students/{link_id}/workouts/{clean['id']}", headers=h).json() == {"result": "deleted"}
    assert client.delete(f"{API}/trainer/students/{link_id}/workouts/{used['id']}", headers=h).json() == {"result": "archived"}
    names = [w["name"] for w in client.get(f"{API}/projects/{project.id}/workouts", headers=auth_headers(student)).json()]
    assert names == []  # arquivado sai da lista ativa, mas o histórico de sessões continua no banco


def test_trainer_cannot_edit_workout_the_student_made_and_only_sees_it_with_consent(client, linked, auth_headers):
    trainer, student, project, link_id = linked(share_progress=False)
    own = client.post(
        f"{API}/projects/{project.id}/workouts", json={"name": "Meu treino", "exercises": [{"name": "Corrida"}]},
        headers=auth_headers(student),
    ).json()
    h = auth_headers(trainer)
    assert client.get(f"{API}/trainer/students/{link_id}/workouts", headers=h).json() == []

    client.patch(f"{API}/trainer-links/{link_id}", json={"share_progress": True}, headers=auth_headers(student))
    listed = client.get(f"{API}/trainer/students/{link_id}/workouts", headers=h).json()
    assert [(w["name"], w["editable"]) for w in listed] == [("Meu treino", False)]

    resp = client.put(f"{API}/trainer/students/{link_id}/workouts/{own['id']}", json={"name": "Hackeado", "exercises": []}, headers=h)
    assert resp.status_code == 404
    assert client.delete(f"{API}/trainer/students/{link_id}/workouts/{own['id']}", headers=h).status_code == 404


# ------------------------------------------------------------------ fotos e evolução

def _upload_photo(client, student, project, auth_headers, tmp_path, monkeypatch, angle="front", day="2026-09-18"):
    from app.core.config import settings
    monkeypatch.setattr(settings, "STORAGE_LOCAL_PATH", str(tmp_path))
    files = {"file": ("f.png", io.BytesIO(_tiny_png_bytes()), "image/png")}
    resp = client.post(
        f"{API}/projects/{project.id}/photos", data={"angle": angle, "date": day}, files=files, headers=auth_headers(student)
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_photos_require_student_consent_and_follow_changes(client, linked, auth_headers, tmp_path, monkeypatch):
    trainer, student, project, link_id = linked(share_photos=False)
    photo_id = _upload_photo(client, student, project, auth_headers, tmp_path, monkeypatch)
    th = auth_headers(trainer)

    assert client.get(f"{API}/trainer/students/{link_id}/photos", headers=th).status_code == 403
    assert client.get(f"{API}/trainer/students/{link_id}/photos/{photo_id}/file", headers=th).status_code == 403

    client.patch(f"{API}/trainer-links/{link_id}", json={"share_photos": True}, headers=auth_headers(student))
    photos = client.get(f"{API}/trainer/students/{link_id}/photos", headers=th)
    assert photos.status_code == 200 and [p["id"] for p in photos.json()] == [photo_id]
    file_resp = client.get(f"{API}/trainer/students/{link_id}/photos/{photo_id}/file", headers=th)
    assert file_resp.status_code == 200 and file_resp.content == _tiny_png_bytes()
    assert "no-store" in file_resp.headers["cache-control"]

    # o aluno retira a permissão -> acesso some imediatamente
    client.patch(f"{API}/trainer-links/{link_id}", json={"share_photos": False}, headers=auth_headers(student))
    assert client.get(f"{API}/trainer/students/{link_id}/photos/{photo_id}/file", headers=th).status_code == 403


def test_trainer_cannot_fetch_photo_of_someone_elses_student(client, linked, make_user, make_project, auth_headers, tmp_path, monkeypatch):
    trainer, _student, _project, link_id = linked(share_photos=True)
    stranger = make_user(email="estranho@example.com")
    stranger_photo = _upload_photo(client, stranger, make_project(stranger), auth_headers, tmp_path, monkeypatch)
    resp = client.get(f"{API}/trainer/students/{link_id}/photos/{stranger_photo}/file", headers=auth_headers(trainer))
    assert resp.status_code == 404


def test_progress_requires_consent_and_summarizes(client, linked, auth_headers):
    trainer, student, project, link_id = linked(share_progress=False)
    th = auth_headers(trainer)
    assert client.get(f"{API}/trainer/students/{link_id}/progress", headers=th).status_code == 403

    client.patch(f"{API}/trainer-links/{link_id}", json={"share_progress": True}, headers=auth_headers(student))
    w = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=th).json()
    today = datetime.now(timezone.utc).date().isoformat()
    client.post(
        f"{API}/projects/{project.id}/workouts/{w['id']}/sessions",
        json={"date": today, "sets": [
            {"workout_exercise_id": w["exercises"][0]["id"], "set_number": 1, "reps": 10, "load_kg": 50},
            {"workout_exercise_id": w["exercises"][0]["id"], "set_number": 2, "reps": 8, "load_kg": 55},
        ]},
        headers=auth_headers(student),
    )
    prog = client.get(f"{API}/trainer/students/{link_id}/progress", headers=th).json()
    assert prog["sessions_last_30_days"] == 1
    assert prog["recent_sessions"][0]["workout_name"] == "Treino A — Peito"
    assert prog["recent_sessions"][0]["total_volume_kg"] == 940  # 10*50 + 8*55


# ------------------------------------------------------------------ encerrar vínculo

def test_student_revokes_link_trainer_loses_access_but_keeps_workouts_with_student(client, linked, auth_headers):
    trainer, student, project, link_id = linked()
    th = auth_headers(trainer)
    client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=th)

    assert client.delete(f"{API}/trainer-links/{link_id}", headers=auth_headers(student)).status_code == 204
    assert client.get(f"{API}/trainer/students/{link_id}/workouts", headers=th).status_code == 404
    assert client.get(f"{API}/trainer/students", headers=th).json() == []
    assert client.get(f"{API}/trainer-links", headers=auth_headers(student)).json() == []
    still_there = client.get(f"{API}/projects/{project.id}/workouts", headers=auth_headers(student)).json()
    assert len(still_there) == 1  # o aluno fica com o treino


def test_trainer_removes_student_and_cancels_pending_invite(client, linked, make_trainer, auth_headers):
    trainer, student, _p, link_id = linked()
    th = auth_headers(trainer)
    pending = client.post(f"{API}/trainer/invites", json={"student_label": "Ana"}, headers=th).json()

    assert client.delete(f"{API}/trainer/students/{link_id}", headers=th).status_code == 204
    assert client.delete(f"{API}/trainer/students/{pending['link_id']}", headers=th).status_code == 204
    assert client.get(f"{API}/trainer/students", headers=th).json() == []
    assert client.post(f"{API}/trainer-links/accept", json={"code": pending["invite_code"]}, headers=auth_headers(student)).status_code == 404
    assert client.delete(f"{API}/trainer/students/{link_id}", headers=auth_headers(make_trainer("outro@x.com"))).status_code == 404


def test_student_cannot_change_someone_elses_link(client, linked, make_user, auth_headers):
    _t, _s, _p, link_id = linked()
    other = make_user(email="outro@x.com")
    assert client.patch(f"{API}/trainer-links/{link_id}", json={"share_photos": True}, headers=auth_headers(other)).status_code == 404
    assert client.delete(f"{API}/trainer-links/{link_id}", headers=auth_headers(other)).status_code == 404


def test_progress_includes_weights_and_measurement(client, linked, auth_headers):
    trainer, student, project, link_id = linked(share_progress=True)
    sh = auth_headers(student)
    for day, kg in (("2026-10-01", 90.0), ("2026-10-08", 89.2)):
        r = client.post(
            f"{API}/projects/{project.id}/checkins",
            json={"project_id": str(project.id), "date": day, "weight_kg": kg}, headers=sh,
        )
        assert r.status_code == 201, r.text
    prog = client.get(f"{API}/trainer/students/{link_id}/progress", headers=auth_headers(trainer)).json()
    assert [(w["date"], w["weight_kg"]) for w in prog["weights"]] == [("2026-10-01", 90.0), ("2026-10-08", 89.2)]  # ordem cronológica
    assert prog["project_name"] == project.name
