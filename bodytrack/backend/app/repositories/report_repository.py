import uuid
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import WeeklyReport


def get_by_week(db: Session, *, project_id: uuid.UUID, week_number: int) -> Optional[WeeklyReport]:
    stmt = select(WeeklyReport).where(
        WeeklyReport.project_id == project_id, WeeklyReport.week_number == week_number
    )
    return db.scalars(stmt).first()


def upsert(
    db: Session, *, project_id: uuid.UUID, week_number: int, data: dict[str, Any]
) -> WeeklyReport:
    existing = get_by_week(db, project_id=project_id, week_number=week_number)
    if existing is not None:
        existing.start_date = data["start_date"]
        existing.end_date = data["end_date"]
        existing.summary = data["summary"]
        db.commit()
        db.refresh(existing)
        return existing

    report = WeeklyReport(project_id=project_id, week_number=week_number, **data)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_for_project(db: Session, *, project_id: uuid.UUID) -> Sequence[WeeklyReport]:
    stmt = (
        select(WeeklyReport)
        .where(WeeklyReport.project_id == project_id)
        .order_by(WeeklyReport.week_number)
    )
    return db.scalars(stmt).all()


def get_owned(db: Session, *, report_id: uuid.UUID, project_id: uuid.UUID) -> Optional[WeeklyReport]:
    stmt = select(WeeklyReport).where(
        WeeklyReport.id == report_id, WeeklyReport.project_id == project_id
    )
    return db.scalars(stmt).first()
