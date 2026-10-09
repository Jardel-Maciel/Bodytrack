from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import MarkRead, NotificationList
from app.services import notification_service

router = APIRouter()


@router.get("", response_model=NotificationList)
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    return {
        "items": notification_service.list_for_user(db, user.id),
        "unread_count": notification_service.unread_count(db, user.id),
    }


@router.post("/read")
def mark_read(payload: MarkRead, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    return {"unread_count": notification_service.mark_read(db, user.id, payload.ids)}
