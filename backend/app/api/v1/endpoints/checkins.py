"""
Check-ins de um projeto — rotas aninhadas em /projects/{project_id}/checkins.

`POST` é sempre um upsert (ver checkin_service.upsert_checkin): a tela
"Check-in de hoje" do frontend não precisa saber se já existe um
registro para hoje, ela só manda salvar.
"""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.checkin import CheckinCreate, CheckinRead, CheckinUpdate
from app.services import checkin_service
from app.services.checkin_service import CheckinNotFoundError
from app.services.project_service import ProjectNotFoundError

router = APIRouter()


@router.post("", response_model=CheckinRead, status_code=status.HTTP_201_CREATED)
def upsert_checkin(
    project_id: uuid.UUID,
    payload: CheckinCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> CheckinRead:
    if payload.project_id != project_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "project_id do payload não confere com a URL.")
    try:
        return checkin_service.upsert_checkin(
            db,
            project_id=project_id,
            user_id=user_id,
            data=payload.model_dump(exclude={"project_id"}),
        )
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("", response_model=list[CheckinRead])
def list_checkins(
    project_id: uuid.UUID,
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[CheckinRead]:
    try:
        return list(
            checkin_service.list_checkins(
                db, project_id=project_id, user_id=user_id, start=start, end=end
            )
        )
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("/{checkin_id}", response_model=CheckinRead)
def get_checkin(
    project_id: uuid.UUID,
    checkin_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> CheckinRead:
    try:
        return checkin_service.get_checkin_or_404(
            db, checkin_id=checkin_id, project_id=project_id, user_id=user_id
        )
    except (ProjectNotFoundError, CheckinNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Check-in não encontrado")


@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkin(
    project_id: uuid.UUID,
    checkin_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    try:
        checkin_service.delete_checkin(
            db, checkin_id=checkin_id, project_id=project_id, user_id=user_id
        )
    except (ProjectNotFoundError, CheckinNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Check-in não encontrado")
