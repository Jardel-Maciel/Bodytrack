import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.achievement import AchievementRead
from app.services import achievement_service
from app.services.project_service import ProjectNotFoundError

router = APIRouter()


@router.get("", response_model=list[AchievementRead])
def list_achievements(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[AchievementRead]:
    try:
        return achievement_service.list_achievements(db, project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")
