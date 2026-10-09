"""Chat personal <-> aluno. Só existe dentro de um vínculo ATIVO e só os dois participantes acessam."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.trainer_link import LINK_ACTIVE, TrainerStudentLink
from app.models.trainer_message import TrainerMessage

MAX_BODY = 2000
MAX_PER_MINUTE = 20
HISTORY_LIMIT = 100


class ChatLinkNotFoundError(Exception): ...
class EmptyMessageError(Exception): ...
class MessageTooLongError(Exception): ...
class RateLimitedError(Exception): ...


def get_link_for_participant(db: Session, *, user_id: uuid.UUID, link_id: uuid.UUID) -> TrainerStudentLink:
    link = db.get(TrainerStudentLink, link_id)
    if link is None or link.status != LINK_ACTIVE or user_id not in (link.trainer_id, link.student_id):
        raise ChatLinkNotFoundError()
    return link


def list_messages(db: Session, *, link: TrainerStudentLink, user_id: uuid.UUID) -> Sequence[TrainerMessage]:
    """Últimas mensagens em ordem cronológica. Abrir a conversa marca como lidas as que vieram do outro lado."""
    db.execute(
        update(TrainerMessage)
        .where(TrainerMessage.link_id == link.id, TrainerMessage.sender_id != user_id, TrainerMessage.read_at.is_(None))
        .values(read_at=datetime.now(timezone.utc))
    )
    db.commit()
    newest_first = db.scalars(
        select(TrainerMessage).where(TrainerMessage.link_id == link.id)
        .order_by(TrainerMessage.created_at.desc(), TrainerMessage.id).limit(HISTORY_LIMIT)
    ).all()
    return list(reversed(newest_first))


def send(db: Session, *, link: TrainerStudentLink, user_id: uuid.UUID, body: str) -> TrainerMessage:
    text = (body or "").strip()
    if not text:
        raise EmptyMessageError()
    if len(text) > MAX_BODY:
        raise MessageTooLongError()
    recent = db.scalar(
        select(func.count()).select_from(TrainerMessage).where(
            TrainerMessage.sender_id == user_id,
            TrainerMessage.created_at > datetime.now(timezone.utc) - timedelta(minutes=1),
        )
    ) or 0
    if recent >= MAX_PER_MINUTE:
        raise RateLimitedError()
    # Horário gravado aqui (microssegundos) e não pelo default do banco: duas mensagens no mesmo
    # instante empatariam e a ordem da conversa ficaria aleatória.
    message = TrainerMessage(link_id=link.id, sender_id=user_id, body=text, created_at=datetime.now(timezone.utc))
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def unread_by_link(db: Session, *, user_id: uuid.UUID) -> dict[str, int]:
    """Mensagens não lidas por conversa (só vínculos ativos dos quais o usuário participa)."""
    rows = db.execute(
        select(TrainerMessage.link_id, func.count())
        .join(TrainerStudentLink, TrainerStudentLink.id == TrainerMessage.link_id)
        .where(
            TrainerStudentLink.status == LINK_ACTIVE,
            (TrainerStudentLink.trainer_id == user_id) | (TrainerStudentLink.student_id == user_id),
            TrainerMessage.sender_id != user_id,
            TrainerMessage.read_at.is_(None),
        )
        .group_by(TrainerMessage.link_id)
    ).all()
    return {str(link_id): count for link_id, count in rows}
