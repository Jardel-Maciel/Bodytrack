"""
Camada de acesso a dados para Project — só sabe falar SQLAlchemy, não
conhece regra de negócio nem HTTP. Isso é o que permite testar a
lógica de negócio (app/services/project_service.py) com um banco
fake/em memória sem duplicar consultas espalhadas pelos endpoints.
"""
import uuid
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


def create(db: Session, *, user_id: uuid.UUID, data: dict[str, Any]) -> Project:
    project = Project(user_id=user_id, **data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_for_user(db: Session, *, user_id: uuid.UUID) -> Sequence[Project]:
    stmt = select(Project).where(Project.user_id == user_id).order_by(Project.start_date.desc())
    return db.scalars(stmt).all()


def get_owned(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Project]:
    """
    Busca o projeto JÁ filtrando pelo dono. Não existe um `get_by_id`
    sem o filtro de user_id em nenhum lugar do código — é assim que a
    regra "usuário jamais acessa dado de outro usuário" vira estrutural
    em vez de depender de alguém lembrar de checar depois.
    """
    stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
    return db.scalars(stmt).first()


def update(db: Session, *, project: Project, data: dict[str, Any]) -> Project:
    for field, value in data.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, *, project: Project) -> None:
    db.delete(project)
    db.commit()
