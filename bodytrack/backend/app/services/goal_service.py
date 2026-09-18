import uuid
from typing import Any, Sequence

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.repositories import goal_repository as repo
from app.services.project_service import get_project_or_404


class GoalNotFoundError(Exception):
    pass


def create_goal(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, data: dict[str, Any]) -> Goal:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    return repo.create(db, project_id=project_id, data=data)


def list_goals(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> Sequence[Goal]:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    return repo.list_for_project(db, project_id=project_id)


def update_goal(
    db: Session, *, goal_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID, data: dict[str, Any]
) -> Goal:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    goal = repo.get_owned(db, goal_id=goal_id, project_id=project_id)
    if goal is None:
        raise GoalNotFoundError()
    return repo.update(db, goal=goal, data=data)


def delete_goal(db: Session, *, goal_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    goal = repo.get_owned(db, goal_id=goal_id, project_id=project_id)
    if goal is None:
        raise GoalNotFoundError()
    repo.delete(db, goal=goal)
