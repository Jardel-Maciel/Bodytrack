import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import ChatUnread, MessageCreate, MessageRead
from app.services import chat_service
from app.services.chat_service import (
    ChatLinkNotFoundError, EmptyMessageError, MessageTooLongError, RateLimitedError,
)

router = APIRouter()


def _link(link_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return chat_service.get_link_for_participant(db, user_id=user.id, link_id=link_id)
    except ChatLinkNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversa não encontrada.")


def _view(message, user_id) -> dict:
    return {
        "id": message.id, "sender_id": message.sender_id, "body": message.body,
        "created_at": message.created_at, "mine": message.sender_id == user_id,
    }


@router.get("/unread", response_model=ChatUnread)
def unread(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    by_link = chat_service.unread_by_link(db, user_id=user.id)
    return {"total": sum(by_link.values()), "by_link": by_link}


@router.get("/{link_id}/messages", response_model=list[MessageRead])
def list_messages(link=Depends(_link), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [_view(m, user.id) for m in chat_service.list_messages(db, link=link, user_id=user.id)]


@router.post("/{link_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: MessageCreate, link=Depends(_link),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    try:
        return _view(chat_service.send(db, link=link, user_id=user.id, body=payload.body), user.id)
    except EmptyMessageError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Mensagem vazia.")
    except MessageTooLongError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Mensagem muito longa (máx. 2000 caracteres).")
    except RateLimitedError:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Muitas mensagens em pouco tempo. Aguarde um instante.")
