import io


def _tiny_png_bytes() -> bytes:
    # PNG 1x1 válido (menor arquivo possível), só para testar o upload de verdade.
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
        "de0000000c4944415478da6360606060000000050001a5f645400000000049454e44ae426082"
    )


def test_upload_list_and_fetch_photo(client, make_user, make_project, auth_headers, tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "STORAGE_LOCAL_PATH", str(tmp_path))

    user = make_user()
    project = make_project(user)
    headers = auth_headers(user)

    files = {"file": ("foto.png", io.BytesIO(_tiny_png_bytes()), "image/png")}
    data = {"angle": "front", "date": "2026-09-18", "week_number": "1"}
    resp = client.post(f"/api/v1/projects/{project.id}/photos", data=data, files=files, headers=headers)
    assert resp.status_code == 201
    photo_id = resp.json()["id"]

    resp = client.get(f"/api/v1/projects/{project.id}/photos", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.get(f"/api/v1/projects/{project.id}/photos/{photo_id}/file", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"


def test_photo_isolated_by_user(client, make_user, make_project, auth_headers, tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "STORAGE_LOCAL_PATH", str(tmp_path))

    user_a = make_user("a@example.com")
    user_b = make_user("b@example.com")
    project_a = make_project(user_a)

    files = {"file": ("foto.png", io.BytesIO(_tiny_png_bytes()), "image/png")}
    data = {"angle": "front", "date": "2026-09-18"}
    resp = client.post(
        f"/api/v1/projects/{project_a.id}/photos", data=data, files=files, headers=auth_headers(user_b)
    )
    assert resp.status_code == 404


def test_rejects_unsupported_file_type(client, make_user, make_project, auth_headers, tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "STORAGE_LOCAL_PATH", str(tmp_path))

    user = make_user()
    project = make_project(user)

    files = {"file": ("foto.txt", io.BytesIO(b"nao e uma imagem"), "text/plain")}
    data = {"angle": "front", "date": "2026-09-18"}
    resp = client.post(
        f"/api/v1/projects/{project.id}/photos", data=data, files=files, headers=auth_headers(user)
    )
    assert resp.status_code == 400
