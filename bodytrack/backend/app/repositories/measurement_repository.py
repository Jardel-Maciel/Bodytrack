import uuid
from datetime import date as date_
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement


def create(db: Session, *, project_id: uuid.UUID, data: dict[str, Any]) -> BodyMeasurement:
    measurement = BodyMeasurement(project_id=project_id, **data)
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


def get_by_date(
    db: Session, *, project_id: uuid.UUID, on_date: date_
) -> Optional[BodyMeasurement]:
    stmt = select(BodyMeasurement).where(
        BodyMeasurement.project_id == project_id, BodyMeasurement.date == on_date
    )
    return db.scalars(stmt).first()


def get_owned(
    db: Session, *, measurement_id: uuid.UUID, project_id: uuid.UUID
) -> Optional[BodyMeasurement]:
    stmt = select(BodyMeasurement).where(
        BodyMeasurement.id == measurement_id, BodyMeasurement.project_id == project_id
    )
    return db.scalars(stmt).first()


def list_for_project(db: Session, *, project_id: uuid.UUID) -> Sequence[BodyMeasurement]:
    stmt = (
        select(BodyMeasurement)
        .where(BodyMeasurement.project_id == project_id)
        .order_by(BodyMeasurement.date)
    )
    return db.scalars(stmt).all()


def first_and_last(
    db: Session, *, project_id: uuid.UUID
) -> tuple[Optional[BodyMeasurement], Optional[BodyMeasurement]]:
    all_rows = list_for_project(db, project_id=project_id)
    if not all_rows:
        return None, None
    return all_rows[0], all_rows[-1]


def update(db: Session, *, measurement: BodyMeasurement, data: dict[str, Any]) -> BodyMeasurement:
    for field, value in data.items():
        setattr(measurement, field, value)
    db.commit()
    db.refresh(measurement)
    return measurement


def delete(db: Session, *, measurement: BodyMeasurement) -> None:
    db.delete(measurement)
    db.commit()
