import uuid
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal


def create(db: Session, *, project_id: uuid.UUID, data: dict[str, Any]) -> Goal:
    goal = Goal(project_id=project_id, **data)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def list_for_project(db: Session, *, project_id: uuid.UUID) -> Sequence[Goal]:
    stmt = select(Goal).where(Goal.project_id == project_id)
    return db.scalars(stmt).all()


def get_owned(db: Session, *, goal_id: uuid.UUID, project_id: uuid.UUID) -> Optional[Goal]:
    stmt = select(Goal).where(Goal.id == goal_id, Goal.project_id == project_id)
    return db.scalars(stmt).first()


def update(db: Session, *, goal: Goal, data: dict[str, Any]) -> Goal:
    for field, value in data.items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


def delete(db: Session, *, goal: Goal) -> None:
    db.delete(goal)
    db.commit()
