import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.app_notice import AppNotice


def notify(
    db: Session, *, user_id: uuid.UUID, kind: str, title: str,
    body: Optional[str] = None, link_path: Optional[str] = None,
) -> None:
    """
    Cria um aviso SEM fazer commit: quem chama commita junto com a ação que o
    gerou (se a ação falhar, o aviso não existe; se der certo, os dois existem).
    Aviso igual (mesmo tipo e destino) ainda não lido é atualizado, não duplicado.
    """
    existing = db.scalars(
        select(AppNotice).where(
            AppNotice.user_id == user_id, AppNotice.kind == kind,
            AppNotice.link_path == link_path, AppNotice.read_at.is_(None),
        )
    ).first()
    if existing:
        existing.title, existing.body = title[:200], (body or "")[:400] or None
        existing.updated_at = datetime.now(timezone.utc)
        return
    db.add(AppNotice(
        user_id=user_id, kind=kind, title=title[:200],
        body=(body or "")[:400] or None, link_path=link_path,
    ))


def list_for_user(db: Session, user_id: uuid.UUID, limit: int = 50) -> Sequence[AppNotice]:
    return db.scalars(
        select(AppNotice).where(AppNotice.user_id == user_id)
        .order_by(AppNotice.updated_at.desc()).limit(limit)
    ).all()


def unread_count(db: Session, user_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count()).select_from(AppNotice)
        .where(AppNotice.user_id == user_id, AppNotice.read_at.is_(None))
    ) or 0


def mark_read(db: Session, user_id: uuid.UUID, ids: Optional[list[uuid.UUID]] = None) -> int:
    """Marca como lidos (os `ids` informados, ou todos). Só mexe nos avisos DESTE usuário."""
    stmt = update(AppNotice).where(AppNotice.user_id == user_id, AppNotice.read_at.is_(None))
    if ids is not None:
        stmt = stmt.where(AppNotice.id.in_(ids))
    db.execute(stmt.values(read_at=datetime.now(timezone.utc)))
    db.commit()
    return unread_count(db, user_id)
