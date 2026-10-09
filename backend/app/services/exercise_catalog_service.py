"""
Catálogo de exercícios com imagens de demonstração.

Como funciona o vínculo "exercício do treino" -> "imagem":

`WorkoutExercise.name` é texto livre (a pessoa digita "Supino reto",
"supino inclinado halter", "Puxada frontal"...). Em vez de obrigar uma
migração/FK, o vínculo é feito PELO NOME, na hora de ler:

    "Supino Reto!"  --normaliza-->  "supino reto"  --procura-->  entrada do catálogo

Assim, treinos que já existem em produção ganham imagem automaticamente,
sem alterar o banco. A busca é propositalmente CONSERVADORA: mostrar a
imagem errada de um exercício é pior do que não mostrar imagem nenhuma,
então só devolvemos algo quando a confiança é alta.

Ordem de tentativas (da mais para a menos confiável):
1. Nome/apelido idêntico depois de normalizar (sem acento, minúsculo, sem pontuação).
2. Mesmas palavras em outra ordem, ignorando "de/com/na/no/..."
   ("barra supino reto com" == "supino reto com barra").
3. Parecido o bastante (difflib, similaridade >= 0,90) — pega erros de
   digitação como "supino retto" ou "agachameto".

As imagens em si ficam em frontend/public/exercises/<id>/<n>.webp.
O dataset de origem (free-exercise-db) é de domínio público (Unlicense).
"""
import json
import re
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CATALOG_PATH = _DATA_DIR / "exercise_catalog.json"
# Vídeos próprios (opcionais): {"<catalog_id>": "/exercise-videos/<arquivo>.mp4" ou URL https}.
# Fica num arquivo À PARTE do catálogo para não ser apagado quando o catálogo é regerado.
_VIDEOS_PATH = _DATA_DIR / "exercise_videos.json"

# Palavras de ligação que não distinguem um exercício do outro.
_STOPWORDS = frozenset({"de", "da", "do", "das", "dos", "com", "na", "no", "nas", "nos", "em", "e", "a", "o", "para", "pra"})

_FUZZY_THRESHOLD = 0.90
_MIN_FUZZY_LENGTH = 6  # textos muito curtos geram falsos positivos no fuzzy


def normalize(text: str) -> str:
    """'  Supino  Reto (Barra)! ' -> 'supino reto barra'."""
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = without_accents.lower()
    cleaned = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(cleaned.split())


def _token_key(normalized: str) -> frozenset[str]:
    return frozenset(t for t in normalized.split() if t not in _STOPWORDS)


@lru_cache(maxsize=1)
def _load() -> tuple[list[dict], dict[str, dict], dict[frozenset, dict]]:
    """Lê o JSON uma única vez e monta os índices de busca."""
    items: list[dict] = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    videos: dict[str, str] = (
        json.loads(_VIDEOS_PATH.read_text(encoding="utf-8")) if _VIDEOS_PATH.exists() else {}
    )
    for item in items:
        item["video_url"] = videos.get(item["id"])  # None = ainda sem vídeo próprio
    by_text: dict[str, dict] = {}
    by_tokens: dict[frozenset, dict] = {}
    for item in items:
        for label in [item["name"], *item.get("aliases", [])]:
            norm = normalize(label)
            by_text.setdefault(norm, item)          # o primeiro dono de um texto vence
            by_tokens.setdefault(_token_key(norm), item)
    return items, by_text, by_tokens


def list_catalog() -> list[dict]:
    return _load()[0]


def get_by_id(catalog_id: str) -> Optional[dict]:
    return next((i for i in _load()[0] if i["id"] == catalog_id), None)


def find_by_name(name: str) -> Optional[dict]:
    """Devolve a entrada do catálogo que corresponde ao nome digitado, ou None."""
    _, by_text, by_tokens = _load()
    norm = normalize(name or "")
    if not norm:
        return None

    if norm in by_text:
        return by_text[norm]

    tokens = _token_key(norm)
    if tokens and tokens in by_tokens:
        return by_tokens[tokens]

    if len(norm) >= _MIN_FUZZY_LENGTH:
        best_item, best_score = None, 0.0
        for label, item in by_text.items():
            if len(label) < _MIN_FUZZY_LENGTH:
                continue
            score = SequenceMatcher(None, norm, label).ratio()
            if score > best_score:
                best_item, best_score = item, score
        if best_item is not None and best_score >= _FUZZY_THRESHOLD:
            return best_item

    return None
