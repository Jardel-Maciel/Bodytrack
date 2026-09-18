import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.photo import ProgressPhoto


def create(db: Session, *, photo: ProgressPhoto) -> ProgressPhoto:
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def list_for_project(db: Session, *, project_id: uuid.UUID) -> Sequence[ProgressPhoto]:
    stmt = (
        select(ProgressPhoto)
        .where(ProgressPhoto.project_id == project_id)
        .order_by(ProgressPhoto.date, ProgressPhoto.angle)
    )
    return db.scalars(stmt).all()


def list_by_week(db: Session, *, project_id: uuid.UUID, week_number: int) -> Sequence[ProgressPhoto]:
    stmt = select(ProgressPhoto).where(
        ProgressPhoto.project_id == project_id, ProgressPhoto.week_number == week_number
    )
    return db.scalars(stmt).all()


def get_owned(db: Session, *, photo_id: uuid.UUID, project_id: uuid.UUID) -> Optional[ProgressPhoto]:
    stmt = select(ProgressPhoto).where(
        ProgressPhoto.id == photo_id, ProgressPhoto.project_id == project_id
    )
    return db.scalars(stmt).first()


def delete(db: Session, *, photo: ProgressPhoto) -> None:
    db.delete(photo)
    db.commit()
