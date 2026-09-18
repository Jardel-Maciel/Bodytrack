"""
Testes do domínio Project (Etapa 3, atualizado na Etapa 4 para usar
JWT real via `auth_headers` em vez do header temporário X-User-Id).

O teste mais importante do arquivo inteiro é
`test_user_b_cannot_access_user_a_project` — ele prova a regra da
Etapa 28 do briefing ("um usuário jamais poderá acessar dados de
outro usuário") no caso mais básico do sistema. Toda nova etapa que
adicionar um recurso preso a Project (check-ins, medidas, fotos,
treinos) ganha um teste equivalente.
"""


def _payload(**overrides):
    base = {
        "name": "Minha Transformação",
        "start_date": "2026-09-18",
        "end_date": "2027-01-08",
        "initial_weight_kg": 127,
    }
    base.update(overrides)
    return base


def test_create_and_list_project(client, make_user, auth_headers):
    user = make_user()
    headers = auth_headers(user)

    resp = client.post("/api/v1/projects", json=_payload(), headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Minha Transformação"
    assert body["status"] == "active"

    resp = client.get("/api/v1/projects", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_end_date_before_start_date_is_rejected(client, make_user, auth_headers):
    user = make_user()
    headers = auth_headers(user)

    resp = client.post(
        "/api/v1/projects",
        json=_payload(start_date="2026-09-18", end_date="2026-01-01"),
        headers=headers,
    )
    assert resp.status_code == 422


def test_user_b_cannot_access_user_a_project(client, make_user, auth_headers):
    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")

    resp = client.post("/api/v1/projects", json=_payload(), headers=auth_headers(user_a))
    project_id = resp.json()["id"]

    headers_b = auth_headers(user_b)

    # Usuário B não vê o projeto de A na própria listagem.
    resp = client.get("/api/v1/projects", headers=headers_b)
    assert resp.json() == []

    # Usuário B não consegue buscar diretamente pelo ID (404, não 403 —
    # não revelamos nem que o projeto existe).
    resp = client.get(f"/api/v1/projects/{project_id}", headers=headers_b)
    assert resp.status_code == 404

    # Nem editar...
    resp = client.patch(
        f"/api/v1/projects/{project_id}", json={"name": "Invasão"}, headers=headers_b
    )
    assert resp.status_code == 404

    # ...nem excluir.
    resp = client.delete(f"/api/v1/projects/{project_id}", headers=headers_b)
    assert resp.status_code == 404

    # O dono de fato continua enxergando o próprio projeto normalmente.
    resp = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers(user_a))
    assert resp.status_code == 200
