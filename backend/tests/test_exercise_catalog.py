import json
from collections import defaultdict
from pathlib import Path

import pytest

from app.services import exercise_catalog_service as catalog

PUBLIC_EXERCISES_DIR = Path(__file__).resolve().parents[2] / "frontend" / "public" / "exercises"


# ---------- integridade do catálogo ----------

def test_catalog_has_no_ambiguous_labels():
    """Nenhum nome/apelido (normalizado) pode apontar para dois exercícios diferentes."""
    owners = defaultdict(set)
    for item in catalog.list_catalog():
        for label in [item["name"], *item["aliases"]]:
            owners[catalog.normalize(label)].add(item["id"])
    conflicts = {label: ids for label, ids in owners.items() if len(ids) > 1}
    assert not conflicts, f"Apelidos ambíguos: {conflicts}"


def test_catalog_ids_are_unique():
    ids = [i["id"] for i in catalog.list_catalog()]
    assert len(ids) == len(set(ids))


def test_every_catalog_entry_has_its_image_files():
    """Se o JSON promete N imagens, os arquivos .webp precisam existir no frontend."""
    for item in catalog.list_catalog():
        assert item["image_count"] >= 1
        for n in range(item["image_count"]):
            assert (PUBLIC_EXERCISES_DIR / item["id"] / f"{n}.webp").exists(), f"{item['id']}/{n}.webp"


# ---------- busca por nome ----------

@pytest.mark.parametrize(
    "typed, expected_name",
    [
        ("Supino reto", "Supino reto com barra"),
        ("supino RETO", "Supino reto com barra"),
        ("  Supino   reto  ", "Supino reto com barra"),
        ("Tríceps corda", "Tríceps corda"),
        ("triceps corda", "Tríceps corda"),
        ("Rosca Scott", "Rosca Scott"),
        ("rosca scott", "Rosca Scott"),
        ("Puxada frontal", "Puxada frontal aberta"),
        ("Cadeira extensora", "Cadeira extensora"),
        ("extensora", "Cadeira extensora"),
        ("Leg Press", "Leg press 45°"),
        ("Levantamento terra", "Levantamento terra"),
        ("Remada serrote", "Remada unilateral com halter"),
        ("Elevação lateral", "Elevação lateral"),
        ("barra supino reto com", "Supino reto com barra"),   # ordem diferente das palavras
        ("Supino retto", "Supino reto com barra"),            # erro de digitação
        ("Agachameto livre", "Agachamento livre com barra"),  # erro de digitação
        ("Agachamento búlgaro", "Agachamento búlgaro"),
    ],
)
def test_find_by_name_matches(typed, expected_name):
    found = catalog.find_by_name(typed)
    assert found is not None, typed
    assert found["name"] == expected_name


@pytest.mark.parametrize(
    "typed",
    ["", "   ", "xyz", "Treino de cardio", "Corrida na esteira", "Alongamento", "Supino de gato", "ab"],
)
def test_find_by_name_does_not_guess(typed):
    """Sem confiança alta, não mostramos imagem (melhor nada do que a imagem errada)."""
    assert catalog.find_by_name(typed) is None


def test_normalize_strips_accents_and_punctuation():
    assert catalog.normalize("  Tríceps  (Corda)! ") == "triceps corda"


# ---------- API ----------

def test_catalog_endpoint_requires_auth(client):
    assert client.get("/api/v1/exercise-catalog").status_code == 401


def test_catalog_endpoint_lists_items(client, make_user, auth_headers):
    user = make_user()
    resp = client.get("/api/v1/exercise-catalog", headers=auth_headers(user))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == len(catalog.list_catalog()) >= 80
    first = body[0]
    assert {"id", "name", "aliases", "primary_muscles", "secondary_muscles", "equipment", "image_count", "video_url"} <= first.keys()
    assert "max-age" in resp.headers["cache-control"]


def test_workout_exercises_expose_catalog_id(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    payload = {
        "name": "Treino A",
        "exercises": [
            {"name": "Supino reto", "order": 0},
            {"name": "Exercício inventado do João", "order": 1},
        ],
    }
    resp = client.post(f"/api/v1/projects/{project.id}/workouts", json=payload, headers=auth_headers(user))
    assert resp.status_code == 201
    exercises = resp.json()["exercises"]
    assert exercises[0]["catalog_id"] == "Barbell_Bench_Press_-_Medium_Grip"
    assert exercises[1]["catalog_id"] is None

    # também aparece ao listar/ler o treino (caminho usado pela tela de Treino)
    listed = client.get(f"/api/v1/projects/{project.id}/workouts", headers=auth_headers(user)).json()
    assert listed[0]["exercises"][0]["catalog_id"] == "Barbell_Bench_Press_-_Medium_Grip"


def test_video_url_defaults_to_none_and_local_videos_exist():
    """Sem vídeo cadastrado = None. Se o vídeo é local (/exercise-videos/...), o arquivo precisa existir."""
    videos_dir = PUBLIC_EXERCISES_DIR.parent / "exercise-videos"
    for item in catalog.list_catalog():
        url = item["video_url"]
        if url is None:
            continue
        assert url.startswith(("https://", "/exercise-videos/")), f"{item['id']}: {url}"
        if url.startswith("/exercise-videos/"):
            assert (videos_dir / url.removeprefix("/exercise-videos/")).exists(), url
