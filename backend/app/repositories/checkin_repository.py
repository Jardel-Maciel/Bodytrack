import uuid
from datetime import date as date_
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.checkin import DailyCheckin


def create(db: Session, *, project_id: uuid.UUID, data: dict[str, Any]) -> DailyCheckin:
    checkin = DailyCheckin(project_id=project_id, **data)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


def get_by_date(db: Session, *, project_id: uuid.UUID, on_date: date_) -> Optional[DailyCheckin]:
    stmt = select(DailyCheckin).where(
        DailyCheckin.project_id == project_id, DailyCheckin.date == on_date
    )
    return db.scalars(stmt).first()


def get_owned(
    db: Session, *, checkin_id: uuid.UUID, project_id: uuid.UUID
) -> Optional[DailyCheckin]:
    stmt = select(DailyCheckin).where(
        DailyCheckin.id == checkin_id, DailyCheckin.project_id == project_id
    )
    return db.scalars(stmt).first()


def list_for_project(
    db: Session,
    *,
    project_id: uuid.UUID,
    start: Optional[date_] = None,
    end: Optional[date_] = None,
) -> Sequence[DailyCheckin]:
    stmt = select(DailyCheckin).where(DailyCheckin.project_id == project_id)
    if start is not None:
        stmt = stmt.where(DailyCheckin.date >= start)
    if end is not None:
        stmt = stmt.where(DailyCheckin.date <= end)
    return db.scalars(stmt.order_by(DailyCheckin.date)).all()


def update(db: Session, *, checkin: DailyCheckin, data: dict[str, Any]) -> DailyCheckin:
    for field, value in data.items():
        setattr(checkin, field, value)
    db.commit()
    db.refresh(checkin)
    return checkin


def delete(db: Session, *, checkin: DailyCheckin) -> None:
    db.delete(checkin)
    db.commit()
