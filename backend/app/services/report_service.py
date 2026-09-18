"""
Relatório semanal (Etapa 11).

`generate_weekly_report` é um upsert por (project_id, week_number) —
gerar de novo a mesma semana substitui o resumo anterior, mas o
resultado nunca é recalculado "ao vivo" quando alguém só quer LER um
relatório antigo (ver comentário em app/models/report.py): o registro
fica congelado até alguém pedir para gerar aquela semana de novo.
"""
import uuid
from datetime import date as date_
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.checkin import DailyCheckin
from app.models.report import WeeklyReport
from app.models.workout import Workout, WorkoutSession
from app.repositories import measurement_repository
from app.repositories import report_repository as repo
from app.schemas.report import WeeklyReportSummary
from app.services.project_service import get_project_or_404


class ReportNotFoundError(Exception):
    pass


_DIET_FLAG_FIELDS = (
    "followed_diet",
    "hit_protein_goal",
    "avoided_ultraprocessed",
    "portion_control",
)


def _week_bounds(project, week_number: int) -> tuple[date_, date_]:
    start = project.start_date + timedelta(days=(week_number - 1) * 7)
    end = start + timedelta(days=6)
    return start, end


def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def generate_weekly_report(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, week_number: int
) -> WeeklyReport:
    project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    start, end = _week_bounds(project, week_number)

    checkins = db.scalars(
        select(DailyCheckin)
        .where(DailyCheckin.project_id == project_id, DailyCheckin.date >= start, DailyCheckin.date <= end)
        .order_by(DailyCheckin.date)
    ).all()

    measurements_in_week = [
        m
        for m in measurement_repository.list_for_project(db, project_id=project_id)
        if start <= m.date <= end
    ]

    workouts_count = len(
        db.scalars(
            select(WorkoutSession.id)
            .join(Workout, WorkoutSession.workout_id == Workout.id)
            .where(
                Workout.project_id == project_id,
                WorkoutSession.date >= start,
                WorkoutSession.date <= end,
            )
        ).all()
    )

    weights = [c.weight_kg for c in checkins if c.weight_kg is not None]
    waists = [m.waist_cm for m in measurements_in_week if m.waist_cm is not None]

    diet_flags: list[bool] = []
    for c in checkins:
        for field in _DIET_FLAG_FIELDS:
            value = getattr(c, field)
            if value is not None:
                diet_flags.append(value)

    summary = WeeklyReportSummary(
        week_number=week_number,
        start_date=start,
        end_date=end,
        days_registered=len(checkins),
        weight_start_kg=weights[0] if weights else None,
        weight_end_kg=weights[-1] if weights else None,
        weight_variation_kg=round(weights[-1] - weights[0], 2) if len(weights) >= 2 else None,
        waist_start_cm=waists[0] if waists else None,
        waist_end_cm=waists[-1] if waists else None,
        waist_variation_cm=round(waists[-1] - waists[0], 2) if len(waists) >= 2 else None,
        workouts_count=workouts_count,
        avg_water_liters=_avg([c.water_liters for c in checkins if c.water_liters is not None]),
        avg_sleep_hours=_avg([c.sleep_hours for c in checkins if c.sleep_hours is not None]),
        avg_steps=_avg([c.steps for c in checkins if c.steps is not None]),
        diet_adherence_pct=(
            round(sum(diet_flags) / len(diet_flags) * 100, 1) if diet_flags else None
        ),
    )

    return repo.upsert(
        db,
        project_id=project_id,
        week_number=week_number,
        data={"start_date": start, "end_date": end, "summary": summary.model_dump(mode="json")},
    )


def list_reports(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> list[WeeklyReport]:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    return list(repo.list_for_project(db, project_id=project_id))


def get_report_or_404(
    db: Session, *, report_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> WeeklyReport:
    get_project_or_404(db, project_id=project_id, user_id=user_id)
    report = repo.get_owned(db, report_id=report_id, project_id=project_id)
    if report is None:
        raise ReportNotFoundError()
    return report
