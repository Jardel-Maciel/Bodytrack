"""
Regras de negócio do check-in diário.

O ponto central aqui é `upsert_checkin`: a tela "Check-in de hoje" do
frontend sempre manda "salvar o check-in de hoje", sem se importar se
já existe um ou não — então o service decide por ela (criar na
primeira vez do dia, atualizar se o usuário reabrir a tela e mudar
algo). Isso também é o que a constraint `UNIQUE(project_id, date)` do
banco garante no nível de dado: nunca existem dois check-ins para o
mesmo dia do mesmo projeto.
"""
import uuid
from datetime import date as date_
from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.models.checkin import DailyCheckin
from app.repositories import checkin_repository as repo
from app.services.project_service import ProjectNotFoundError, get_project_or_404


class CheckinNotFoundError(Exception):
    pass


def _ensure_project_ownership(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    # Reaproveita a regra de "o projeto existe e é meu" já provada no
    # domínio de Project — evita duplicar essa checagem em todo domínio
    # novo que penduramos em Project (checkins, measurements, workouts...).
    get_project_or_404(db, project_id=project_id, user_id=user_id)


def upsert_checkin(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, data: dict[str, Any]
) -> DailyCheckin:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)

    existing = repo.get_by_date(db, project_id=project_id, on_date=data["date"])
    if existing is not None:
        data_without_date = {k: v for k, v in data.items() if k != "date"}
        return repo.update(db, checkin=existing, data=data_without_date)
    return repo.create(db, project_id=project_id, data=data)


def list_checkins(
    db: Session,
    *,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    start: Optional[date_] = None,
    end: Optional[date_] = None,
) -> Sequence[DailyCheckin]:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    return repo.list_for_project(db, project_id=project_id, start=start, end=end)


def get_checkin_or_404(
    db: Session, *, checkin_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> DailyCheckin:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    checkin = repo.get_owned(db, checkin_id=checkin_id, project_id=project_id)
    if checkin is None:
        raise CheckinNotFoundError()
    return checkin


def delete_checkin(
    db: Session, *, checkin_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    checkin = get_checkin_or_404(db, checkin_id=checkin_id, project_id=project_id, user_id=user_id)
    repo.delete(db, checkin=checkin)
