import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.photo import PhotoAngle
from app.schemas.photo import PhotoComparison, PhotoRead
from app.services import photo_service, storage_service
from app.services.photo_service import PhotoNotFoundError
from app.services.project_service import ProjectNotFoundError
from app.services.storage_service import InvalidPhotoError

router = APIRouter()


@router.post("", response_model=PhotoRead, status_code=status.HTTP_201_CREATED)
def upload_photo(
    project_id: uuid.UUID,
    angle: PhotoAngle = Form(...),
    photo_date: date = Form(..., alias="date"),
    week_number: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> PhotoRead:
    try:
        return photo_service.upload_photo(
            db,
            project_id=project_id,
            user_id=user_id,
            angle=angle,
            photo_date=photo_date,
            week_number=week_number,
            file=file,
        )
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")
    except InvalidPhotoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


@router.get("", response_model=list[PhotoRead])
def list_photos(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[PhotoRead]:
    try:
        return list(photo_service.list_photos(db, project_id=project_id, user_id=user_id))
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("/compare", response_model=PhotoComparison)
def compare_weeks(
    project_id: uuid.UUID,
    week_a: int = Query(..., ge=1),
    week_b: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> PhotoComparison:
    try:
        return photo_service.compare_weeks(db, project_id=project_id, user_id=user_id, week_a=week_a, week_b=week_b)
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("/{photo_id}/file")
def get_photo_file(
    project_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> Response:
    """
    Serve o binário da foto. Deliberadamente NÃO é uma URL pública: só
    responde depois de confirmar (via get_photo_or_404) que a foto
    pertence a um projeto do usuário autenticado — é isso que impede
    alguém de adivinhar/compartilhar um link direto para a foto de
    outra pessoa.
    """
    try:
        photo = photo_service.get_photo_or_404(db, photo_id=photo_id, project_id=project_id, user_id=user_id)
        content = storage_service.read_photo(photo.file_path)
    except (ProjectNotFoundError, PhotoNotFoundError, FileNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto não encontrada")
    return Response(content=content, media_type=storage_service.content_type_for(photo.file_path))


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    project_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    try:
        photo_service.delete_photo(db, photo_id=photo_id, project_id=project_id, user_id=user_id)
    except (ProjectNotFoundError, PhotoNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto não encontrada")
