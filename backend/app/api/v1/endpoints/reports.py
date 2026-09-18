import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.report import WeeklyReportRead
from app.services import export_service, pdf_service, report_service
from app.services.project_service import ProjectNotFoundError, get_project_or_404
from app.services.report_service import ReportNotFoundError

router = APIRouter()


class GenerateReportRequest(BaseModel):
    week_number: int = Field(ge=1)


@router.post("/generate", response_model=WeeklyReportRead, status_code=status.HTTP_201_CREATED)
def generate_report(
    project_id: uuid.UUID,
    payload: GenerateReportRequest,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> WeeklyReportRead:
    try:
        return report_service.generate_weekly_report(
            db, project_id=project_id, user_id=user_id, week_number=payload.week_number
        )
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("", response_model=list[WeeklyReportRead])
def list_reports(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[WeeklyReportRead]:
    try:
        return report_service.list_reports(db, project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("/export")
def export_data(
    project_id: uuid.UUID,
    format: Literal["csv", "json"] = Query("json"),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> Response:
    try:
        content, media_type, filename = export_service.export_project_data(
            db, project_id=project_id, user_id=user_id, fmt=format
        )
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{report_id}/pdf")
def get_report_pdf(
    project_id: uuid.UUID,
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> Response:
    try:
        report = report_service.get_report_or_404(
            db, report_id=report_id, project_id=project_id, user_id=user_id
        )
        # get_project_or_404 já rodou dentro de get_report_or_404, mas
        # precisamos do nome do projeto para o cabeçalho do PDF.
        project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    except (ProjectNotFoundError, ReportNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Relatório não encontrado")

    pdf_bytes = pdf_service.render_weekly_report_pdf(report, project_name=project.name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="relatorio_semana_{report.week_number}.pdf"'},
    )
