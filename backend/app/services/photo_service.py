import uuid
from datetime import date as date_
from typing import Optional, Sequence

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.photo import PhotoAngle, ProgressPhoto
from app.repositories import photo_repository as repo
from app.schemas.photo import PhotoComparison
from app.services import storage_service
from app.services.project_service import get_project_or_404


class PhotoNotFoundError(Exception):
    pass


def upload_photo(
    db: Session,
    *,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    angle: PhotoAngle,
    photo_date: date_,
    week_number: Optional[int],
    file: UploadFile,
) -> ProgressPhoto:
    get_project_or_404(db, project_id=project_id, user_id=user_id)

    # Salva o arquivo primeiro; só grava a linha no banco se o arquivo
    # foi salvo com sucesso (evita registro "órfão" apontando para um
    # arquivo que não existe).
    file_path = storage_service.save_photo(file, project_id=project_id)

    photo = ProgressPhoto(
        project_id=project_id,
        date=photo_date,
        week_number=week_number,
        angle=angle,
        file_path=file_path,
    )
    return repo.create(db, photo=photo)


def list_photos(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> Sequence[ProgressPhoto]:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    return repo.list_for_project(db, project_id=project_id)


def get_photo_or_404(
    db: Session, *, photo_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> ProgressPhoto:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    photo = repo.get_owned(db, photo_id=photo_id, project_id=project_id)
    if photo is None:
        raise PhotoNotFoundError()
    return photo


def delete_photo(db: Session, *, photo_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    photo = get_photo_or_404(db, photo_id=photo_id, project_id=project_id, user_id=user_id)
    storage_service.delete_photo_file(photo.file_path)
    repo.delete(db, photo=photo)


def compare_weeks(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, week_a: int, week_b: int
) -> PhotoComparison:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    photos_a = repo.list_by_week(db, project_id=project_id, week_number=week_a)
    photos_b = repo.list_by_week(db, project_id=project_id, week_number=week_b)
    return PhotoComparison(week_a=week_a, week_b=week_b, photos_a=list(photos_a), photos_b=list(photos_b))
