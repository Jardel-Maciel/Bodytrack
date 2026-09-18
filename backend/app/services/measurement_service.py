import uuid
from typing import Any, Sequence

from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement
from app.repositories import measurement_repository as repo
from app.schemas.measurement import _FIELDS, MeasurementFieldProgress, MeasurementProgress
from app.services.project_service import get_project_or_404


class MeasurementNotFoundError(Exception):
    pass


def _ensure_project_ownership(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    get_project_or_404(db, project_id=project_id, user_id=user_id)


def upsert_measurement(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, data: dict[str, Any]
) -> BodyMeasurement:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    existing = repo.get_by_date(db, project_id=project_id, on_date=data["date"])
    if existing is not None:
        data_without_date = {k: v for k, v in data.items() if k != "date"}
        return repo.update(db, measurement=existing, data=data_without_date)
    return repo.create(db, project_id=project_id, data=data)


def list_measurements(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID
) -> Sequence[BodyMeasurement]:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    return repo.list_for_project(db, project_id=project_id)


def get_measurement_or_404(
    db: Session, *, measurement_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> BodyMeasurement:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    measurement = repo.get_owned(db, measurement_id=measurement_id, project_id=project_id)
    if measurement is None:
        raise MeasurementNotFoundError()
    return measurement


def delete_measurement(
    db: Session, *, measurement_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    measurement = get_measurement_or_404(
        db, measurement_id=measurement_id, project_id=project_id, user_id=user_id
    )
    repo.delete(db, measurement=measurement)


def get_progress(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> MeasurementProgress:
    """
    Compara a PRIMEIRA medida registrada com a MAIS RECENTE, campo a
    campo. Um campo só entra na comparação se tiver valor tanto na
    primeira quanto na última medida — não assumimos que toda medida
    tem todos os campos preenchidos (ver Etapa 8 do briefing: "não
    obrigar a preencher todas as medidas").
    """
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    first, last = repo.first_and_last(db, project_id=project_id)

    fields: list[MeasurementFieldProgress] = []
    for field_name in _FIELDS:
        initial = getattr(first, field_name, None) if first else None
        current = getattr(last, field_name, None) if last else None
        variation = None
        variation_pct = None
        if initial is not None and current is not None:
            variation = round(current - initial, 2)
            variation_pct = round((variation / initial) * 100, 2) if initial != 0 else None
        fields.append(
            MeasurementFieldProgress(
                field=field_name,
                initial_value=initial,
                current_value=current,
                variation=variation,
                variation_pct=variation_pct,
            )
        )
    return MeasurementProgress(fields=fields)
