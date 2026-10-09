"""Lado do ALUNO: aceitar convite, ver seus personais, ajustar o que compartilha e encerrar o vínculo."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trainer import AcceptInvite, ConsentUpdate, MyTrainerLink
from app.services import trainer_service
from app.services.trainer_service import (
    AlreadyLinkedError,
    InviteInvalidError,
    InviteOwnError,
    LinkNotFoundError,
)

router = APIRouter()


def _as_view(db: Session, link) -> dict:
    return next(l for l in trainer_service.list_my_trainers(db, student_id=link.student_id) if l["link_id"] == link.id)


@router.get("", response_model=list[MyTrainerLink])
def my_trainers(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    return trainer_service.list_my_trainers(db, student_id=user.id)


@router.post("/accept", response_model=MyTrainerLink, status_code=status.HTTP_201_CREATED)
def accept_invite(payload: AcceptInvite, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    try:
        link = trainer_service.accept_invite(
            db, student=user, code=payload.code,
            share_photos=payload.share_photos, share_progress=payload.share_progress,
        )
    except InviteInvalidError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Código inválido, já usado ou vencido.")
    except InviteOwnError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Você não pode aceitar o seu próprio convite.")
    except AlreadyLinkedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Você já está vinculado a este personal.")
    return _as_view(db, link)


@router.patch("/{link_id}", response_model=MyTrainerLink)
def update_consent(
    link_id: uuid.UUID, payload: ConsentUpdate,
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
) -> dict:
    try:
        link = trainer_service.update_consent(
            db, student_id=user.id, link_id=link_id,
            share_photos=payload.share_photos, share_progress=payload.share_progress,
        )
    except LinkNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vínculo não encontrado.")
    return _as_view(db, link)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def end_link(link_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    try:
        trainer_service.end_link_as_student(db, student_id=user.id, link_id=link_id)
    except LinkNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vínculo não encontrado.")
