from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.gamification import GamificationSummary
from app.services import gamification_service

router = APIRouter()


@router.get("/summary", response_model=GamificationSummary)
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    return gamification_service.get_summary(db, user.id)
