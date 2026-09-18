import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.measurement import (
    MeasurementCreate,
    MeasurementProgress,
    MeasurementRead,
)
from app.services import measurement_service
from app.services.measurement_service import MeasurementNotFoundError
from app.services.project_service import ProjectNotFoundError

router = APIRouter()


@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def upsert_measurement(
    project_id: uuid.UUID,
    payload: MeasurementCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> MeasurementRead:
    if payload.project_id != project_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "project_id do payload não confere com a URL.")
    try:
        return measurement_service.upsert_measurement(
            db, project_id=project_id, user_id=user_id, data=payload.model_dump(exclude={"project_id"})
        )
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("", response_model=list[MeasurementRead])
def list_measurements(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[MeasurementRead]:
    try:
        return list(measurement_service.list_measurements(db, project_id=project_id, user_id=user_id))
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("/progress", response_model=MeasurementProgress)
def get_progress(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> MeasurementProgress:
    try:
        return measurement_service.get_progress(db, project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(
    project_id: uuid.UUID,
    measurement_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    try:
        measurement_service.delete_measurement(
            db, measurement_id=measurement_id, project_id=project_id, user_id=user_id
        )
    except (ProjectNotFoundError, MeasurementNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Medida não encontrada")
