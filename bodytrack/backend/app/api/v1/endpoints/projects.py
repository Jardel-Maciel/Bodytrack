"""
Endpoints de Project.

Todos dependem de `get_current_user_id` (app/api/deps.py) — hoje
resolvido via header temporário, JWT a partir da Etapa 4 — e nunca
recebem `user_id` do cliente: o dono do projeto é sempre quem está
autenticado, nunca um campo do payload (evita que alguém tente criar
ou ler um projeto "em nome" de outro usuário só editando o JSON).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import project_service
from app.services.project_service import ProjectNotFoundError

router = APIRouter()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> ProjectRead:
    return project_service.create_project(db, user_id=user_id, data=payload.model_dump())


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[ProjectRead]:
    return list(project_service.list_projects(db, user_id=user_id))


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> ProjectRead:
    try:
        return project_service.get_project_or_404(db, project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado")


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> ProjectRead:
    try:
        return project_service.update_project(
            db, project_id=project_id, user_id=user_id, data=payload.model_dump(exclude_unset=True)
        )
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    try:
        project_service.delete_project(db, project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado")
