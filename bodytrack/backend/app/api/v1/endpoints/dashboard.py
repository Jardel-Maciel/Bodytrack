import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service
from app.services.project_service import ProjectNotFoundError

router = APIRouter()


@router.get("", response_model=DashboardSummary)
def get_dashboard(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> DashboardSummary:
    try:
        return dashboard_service.get_dashboard(db, project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")
