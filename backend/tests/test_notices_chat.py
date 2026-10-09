"""Avisos (sininho) e chat entre personal e aluno."""
from tests.test_trainer import API, _workout_payload, linked, make_trainer  # noqa: F401  (fixtures reutilizadas)


def _notices(client, user, auth_headers):
    return client.get(f"{API}/notifications", headers=auth_headers(user)).json()


# ------------------------------------------------------------------ avisos

def test_trainer_actions_notify_the_student(client, linked, auth_headers):
    trainer, student, _p, link_id = linked()
    th = auth_headers(trainer)
    w = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=th).json()

    data = _notices(client, student, auth_headers)
    assert data["unread_count"] == 1
    n = data["items"][0]
    assert n["kind"] == "workout_new" and n["link_path"] == "/treino" and n["read"] is False
    assert trainer.name in n["title"] and n["body"] == "Treino A — Peito"

    client.put(f"{API}/trainer/students/{link_id}/workouts/{w['id']}", json=_workout_payload(name="Treino A v2"), headers=th)
    kinds = sorted(i["kind"] for i in _notices(client, student, auth_headers)["items"])
    assert kinds == ["workout_new", "workout_updated"]

    client.delete(f"{API}/trainer/students/{link_id}/workouts/{w['id']}", headers=th)
    assert "workout_removed" in [i["kind"] for i in _notices(client, student, auth_headers)["items"]]


def test_repeated_unread_notices_are_grouped(client, linked, auth_headers):
    trainer, student, _p, link_id = linked()
    th = auth_headers(trainer)
    w = client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=th).json()
    for i in range(4):
        client.put(f"{API}/trainer/students/{link_id}/workouts/{w['id']}", json=_workout_payload(name=f"v{i}"), headers=th)
    items = [i for i in _notices(client, student, auth_headers)["items"] if i["kind"] == "workout_updated"]
    assert len(items) == 1 and "v3" in items[0]["title"]  # 4 edições, 1 aviso (o mais recente)


def test_student_actions_notify_the_trainer(client, make_user, make_trainer, make_project, auth_headers):
    trainer, student = make_trainer(), make_user(email="aluno@example.com")
    make_project(student)
    code = client.post(f"{API}/trainer/invites", json={}, headers=auth_headers(trainer)).json()["invite_code"]
    link_id = client.post(f"{API}/trainer-links/accept", json={"code": code}, headers=auth_headers(student)).json()["link_id"]
    first = _notices(client, trainer, auth_headers)["items"][0]
    assert first["kind"] == "link_accepted" and first["link_path"] == f"/alunos/{link_id}"

    client.patch(f"{API}/trainer-links/{link_id}", json={"share_photos": True}, headers=auth_headers(student))
    client.patch(f"{API}/trainer-links/{link_id}", json={"share_photos": True}, headers=auth_headers(student))  # sem mudança: sem aviso novo
    consent = [i for i in _notices(client, trainer, auth_headers)["items"] if i["kind"] == "consent_changed"]
    assert len(consent) == 1 and "Fotos: sim" in consent[0]["body"]

    client.delete(f"{API}/trainer-links/{link_id}", headers=auth_headers(student))
    assert "link_ended" in [i["kind"] for i in _notices(client, trainer, auth_headers)["items"]]


def test_trainer_removing_student_notifies_student_but_cancelling_invite_does_not(client, linked, auth_headers):
    trainer, student, _p, link_id = linked()
    th = auth_headers(trainer)
    pending = client.post(f"{API}/trainer/invites", json={}, headers=th).json()
    client.delete(f"{API}/trainer/students/{pending['link_id']}", headers=th)
    assert _notices(client, student, auth_headers)["items"] == []
    client.delete(f"{API}/trainer/students/{link_id}", headers=th)
    assert [i["kind"] for i in _notices(client, student, auth_headers)["items"]] == ["link_ended"]


def test_mark_read_only_touches_own_notices(client, linked, make_user, auth_headers):
    trainer, student, _p, link_id = linked()
    client.post(f"{API}/trainer/students/{link_id}/workouts", json=_workout_payload(), headers=auth_headers(trainer))
    other = make_user(email="outro@x.com")
    assert client.post(f"{API}/notifications/read", json={}, headers=auth_headers(other)).json() == {"unread_count": 0}
    assert _notices(client, student, auth_headers)["unread_count"] == 1  # o do aluno não foi afetado

    item_id = _notices(client, student, auth_headers)["items"][0]["id"]
    assert client.post(f"{API}/notifications/read", json={"ids": [item_id]}, headers=auth_headers(student)).json() == {"unread_count": 0}
    assert _notices(client, student, auth_headers)["items"][0]["read"] is True
    assert client.get(f"{API}/notifications").status_code == 401


# ------------------------------------------------------------------ chat

def test_chat_roundtrip_and_unread_counts(client, linked, auth_headers):
    trainer, student, _p, link_id = linked()
    th, sh = auth_headers(trainer), auth_headers(student)

    sent = client.post(f"{API}/chat/{link_id}/messages", json={"body": "  Bom dia! Como foi o treino?  "}, headers=th)
    assert sent.status_code == 201 and sent.json()["mine"] is True and sent.json()["body"] == "Bom dia! Como foi o treino?"
    client.post(f"{API}/chat/{link_id}/messages", json={"body": "Segunda série ficou pesada"}, headers=th)

    assert client.get(f"{API}/chat/unread", headers=sh).json() == {"total": 2, "by_link": {link_id: 2}}
    assert client.get(f"{API}/chat/unread", headers=th).json()["total"] == 0  # quem enviou não tem "não lida"

    msgs = client.get(f"{API}/chat/{link_id}/messages", headers=sh).json()
    assert [m["body"] for m in msgs] == ["Bom dia! Como foi o treino?", "Segunda série ficou pesada"]
    assert [m["mine"] for m in msgs] == [False, False]
    assert client.get(f"{API}/chat/unread", headers=sh).json()["total"] == 0  # abrir a conversa marca como lida

    client.post(f"{API}/chat/{link_id}/messages", json={"body": "Foi ótimo, subi a carga!"}, headers=sh)
    assert client.get(f"{API}/chat/unread", headers=th).json()["by_link"] == {link_id: 1}
    assert client.get(f"{API}/chat/{link_id}/messages", headers=th).json()[-1]["mine"] is False


def test_chat_is_private_to_the_two_participants(client, linked, make_trainer, make_user, auth_headers):
    _t, _s, _p, link_id = linked()
    for outsider in (make_trainer("intruso@x.com"), make_user(email="curioso@x.com")):
        h = auth_headers(outsider)
        assert client.get(f"{API}/chat/{link_id}/messages", headers=h).status_code == 404
        assert client.post(f"{API}/chat/{link_id}/messages", json={"body": "oi"}, headers=h).status_code == 404
    assert client.get(f"{API}/chat/{link_id}/messages").status_code == 401


def test_chat_closes_when_link_is_revoked(client, linked, auth_headers):
    trainer, student, _p, link_id = linked()
    client.post(f"{API}/chat/{link_id}/messages", json={"body": "oi"}, headers=auth_headers(trainer))
    client.delete(f"{API}/trainer-links/{link_id}", headers=auth_headers(student))
    for user in (trainer, student):
        assert client.get(f"{API}/chat/{link_id}/messages", headers=auth_headers(user)).status_code == 404
        assert client.post(f"{API}/chat/{link_id}/messages", json={"body": "oi"}, headers=auth_headers(user)).status_code == 404
    assert client.get(f"{API}/chat/unread", headers=auth_headers(student)).json()["total"] == 0


def test_chat_validates_and_rate_limits(client, linked, auth_headers):
    trainer, _s, _p, link_id = linked()
    th = auth_headers(trainer)
    assert client.post(f"{API}/chat/{link_id}/messages", json={"body": "   "}, headers=th).status_code == 422
    assert client.post(f"{API}/chat/{link_id}/messages", json={"body": "x" * 2001}, headers=th).status_code == 422
    codes = [client.post(f"{API}/chat/{link_id}/messages", json={"body": f"m{i}"}, headers=th).status_code for i in range(22)]
    assert codes.count(201) == 20 and codes[-1] == 429
