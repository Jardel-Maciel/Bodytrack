import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.services import goal_service
from app.services.goal_service import GoalNotFoundError
from app.services.project_service import ProjectNotFoundError

router = APIRouter()


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    project_id: uuid.UUID,
    payload: GoalCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> GoalRead:
    try:
        return goal_service.create_goal(db, project_id=project_id, user_id=user_id, data=payload.model_dump())
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("", response_model=list[GoalRead])
def list_goals(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[GoalRead]:
    try:
        return list(goal_service.list_goals(db, project_id=project_id, user_id=user_id))
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    project_id: uuid.UUID,
    goal_id: uuid.UUID,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> GoalRead:
    try:
        return goal_service.update_goal(
            db, goal_id=goal_id, project_id=project_id, user_id=user_id, data=payload.model_dump(exclude_unset=True)
        )
    except (ProjectNotFoundError, GoalNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meta não encontrada")


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    project_id: uuid.UUID,
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    try:
        goal_service.delete_goal(db, goal_id=goal_id, project_id=project_id, user_id=user_id)
    except (ProjectNotFoundError, GoalNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meta não encontrada")
