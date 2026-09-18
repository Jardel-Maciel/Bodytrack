def test_register_login_and_me(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "nova@example.com", "password": "senha12345", "name": "Nova Usuária"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "nova@example.com"
    assert "hashed_password" not in body

    resp = client.post(
        "/api/v1/auth/login", json={"email": "nova@example.com", "password": "senha12345"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "nova@example.com"


def test_cannot_register_same_email_twice(client):
    payload = {"email": "dup@example.com", "password": "senha12345", "name": "Dup"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_with_wrong_password_fails(client, make_user):
    make_user(email="user@example.com", password="senhacerta")
    resp = client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "senhaerrada"}
    )
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/api/v1/projects")
    assert resp.status_code == 401


def test_protected_route_rejects_garbage_token(client):
    resp = client.get(
        "/api/v1/projects", headers={"Authorization": "Bearer isto-nao-e-um-jwt-valido"}
    )
    assert resp.status_code == 401
