import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.series import VALID_METRICS, VALID_PERIODS, Series
from app.services import series_service
from app.services.project_service import ProjectNotFoundError
from app.services.series_service import InvalidMetricError, InvalidPeriodError

router = APIRouter()


@router.get("", response_model=Series)
def get_series(
    project_id: uuid.UUID,
    metric: str = Query(..., description=f"Um de: {', '.join(VALID_METRICS)}"),
    period: str = Query("30d", description=f"Um de: {', '.join(VALID_PERIODS)}"),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> Series:
    try:
        return series_service.get_series(db, project_id=project_id, user_id=user_id, metric=metric, period=period)
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")
    except InvalidMetricError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"metric inválida. Use um de: {', '.join(VALID_METRICS)}")
    except InvalidPeriodError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"period inválido. Use um de: {', '.join(VALID_PERIODS)}")
