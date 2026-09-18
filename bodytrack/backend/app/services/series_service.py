"""
Dados de série temporal para os gráficos de evolução (Etapa 10).

Um único endpoint (`GET /projects/{id}/series?metric=...&period=...`)
serve todos os ~9 gráficos pedidos no briefing: o `metric` escolhe a
coluna/origem, o `period` escolhe a janela de tempo. Isso evita criar
um endpoint por gráfico.
"""
import uuid
from datetime import date as date_
from datetime import timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.checkin import DailyCheckin
from app.models.measurement import BodyMeasurement
from app.models.project import Project
from app.models.workout import Workout, WorkoutSession
from app.schemas.series import Series, SeriesPoint
from app.services.project_service import get_project_or_404

_CHECKIN_METRICS = {
    "weight_kg": DailyCheckin.weight_kg,
    "water_liters": DailyCheckin.water_liters,
    "sleep_hours": DailyCheckin.sleep_hours,
    "steps": DailyCheckin.steps,
}
_MEASUREMENT_METRICS = {
    "waist_cm": BodyMeasurement.waist_cm,
    "abdomen_cm": BodyMeasurement.abdomen_cm,
    "hip_cm": BodyMeasurement.hip_cm,
}


class InvalidMetricError(Exception):
    pass


class InvalidPeriodError(Exception):
    pass


def _period_start(period: str, project: Project, today: date_) -> Optional[date_]:
    if period == "7d":
        return today - timedelta(days=6)
    if period == "30d":
        return today - timedelta(days=29)
    if period == "90d":
        return today - timedelta(days=89)
    if period == "project":
        return project.start_date
    raise InvalidPeriodError()


def get_series(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, metric: str, period: str
) -> Series:
    project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    today = date_.today()
    start = _period_start(period, project, today)

    if metric == "training_frequency":
        return _training_frequency_series(db, project_id=project_id, start=start, today=today, period=period)

    if metric in _CHECKIN_METRICS:
        column = _CHECKIN_METRICS[metric]
        stmt = (
            select(DailyCheckin.date, column)
            .where(DailyCheckin.project_id == project_id, DailyCheckin.date >= start, column.isnot(None))
            .order_by(DailyCheckin.date)
        )
    elif metric in _MEASUREMENT_METRICS:
        column = _MEASUREMENT_METRICS[metric]
        stmt = (
            select(BodyMeasurement.date, column)
            .where(
                BodyMeasurement.project_id == project_id,
                BodyMeasurement.date >= start,
                column.isnot(None),
            )
            .order_by(BodyMeasurement.date)
        )
    else:
        raise InvalidMetricError()

    rows = db.execute(stmt).all()
    points = [SeriesPoint(date=row[0], value=row[1]) for row in rows]
    return Series(metric=metric, period=period, points=points)


def _training_frequency_series(
    db: Session, *, project_id: uuid.UUID, start: Optional[date_], today: date_, period: str
) -> Series:
    """Uma sessão de treino conta como 1 ponto na semana em que ocorreu (semana começando na segunda-feira)."""
    stmt = (
        select(WorkoutSession.date)
        .join(Workout, WorkoutSession.workout_id == Workout.id)
        .where(Workout.project_id == project_id, WorkoutSession.date >= start, WorkoutSession.date <= today)
    )
    dates = db.scalars(stmt).all()

    weekly_counts: dict[date_, int] = {}
    for d in dates:
        week_start = d - timedelta(days=d.weekday())
        weekly_counts[week_start] = weekly_counts.get(week_start, 0) + 1

    points = [SeriesPoint(date=k, value=v) for k, v in sorted(weekly_counts.items())]
    return Series(metric="training_frequency", period=period, points=points)
