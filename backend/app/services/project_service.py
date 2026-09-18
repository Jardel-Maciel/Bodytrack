"""
Regras de negócio de Project. O endpoint HTTP não decide "o que
acontece quando o projeto não existe" — ele só traduz a exceção de
domínio (`ProjectNotFoundError`) para um status HTTP. Isso mantém a
regra de negócio testável sem precisar simular uma requisição HTTP.
"""
import uuid
from typing import Any, Sequence

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories import project_repository as repo


class ProjectNotFoundError(Exception):
    """Levantada quando o projeto não existe OU não pertence ao usuário atual.

    De propósito, os dois casos são indistinguíveis para quem chama a
    API: devolver 404 em ambos (em vez de 403 para "existe mas não é
    seu") evita vazar a existência de projetos de outros usuários.
    """


def create_project(db: Session, *, user_id: uuid.UUID, data: dict[str, Any]) -> Project:
    return repo.create(db, user_id=user_id, data=data)


def list_projects(db: Session, *, user_id: uuid.UUID) -> Sequence[Project]:
    return repo.list_for_user(db, user_id=user_id)


def get_project_or_404(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    project = repo.get_owned(db, project_id=project_id, user_id=user_id)
    if project is None:
        raise ProjectNotFoundError()
    return project


def update_project(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, data: dict[str, Any]
) -> Project:
    project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    return repo.update(db, project=project, data=data)


def delete_project(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    repo.delete(db, project=project)
