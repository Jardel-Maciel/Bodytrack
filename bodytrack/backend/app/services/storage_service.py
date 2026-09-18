"""
Abstração de armazenamento de arquivo (hoje só fotos de progresso).

Só existe UMA implementação agora (disco local, dentro de
`backend/storage/photos/`), mas o resto do código nunca importa
`pathlib` ou fala de "disco" diretamente — sempre passa por
`save_photo`/`read_photo`/`delete_photo_file`. Trocar para um object
storage (S3, Cloudflare R2, etc.) em produção é reescrever só este
arquivo, sem tocar em repository/service/endpoint de fotos.
"""
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

_ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


class InvalidPhotoError(Exception):
    pass


def _storage_root() -> Path:
    root = Path(settings.STORAGE_LOCAL_PATH)
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_photo(file: UploadFile, *, project_id: uuid.UUID) -> str:
    """Valida, salva em disco e devolve o caminho RELATIVO (o que fica em `progress_photos.file_path`)."""
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise InvalidPhotoError("Formato não suportado. Envie uma imagem JPEG, PNG ou WEBP.")

    contents = file.file.read()
    max_bytes = settings.MAX_PHOTO_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise InvalidPhotoError(f"Imagem maior que {settings.MAX_PHOTO_SIZE_MB}MB.")

    ext = _ALLOWED_CONTENT_TYPES[file.content_type]
    relative_path = f"{project_id}/{uuid.uuid4()}.{ext}"

    full_path = _storage_root() / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(contents)

    return relative_path


def read_photo(file_path: str) -> bytes:
    full_path = _storage_root() / file_path
    if not full_path.exists():
        raise FileNotFoundError(file_path)
    return full_path.read_bytes()


def delete_photo_file(file_path: str) -> None:
    full_path = _storage_root() / file_path
    if full_path.exists():
        full_path.unlink()


def content_type_for(file_path: str) -> str:
    ext = file_path.rsplit(".", 1)[-1].lower()
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(
        ext, "application/octet-stream"
    )
