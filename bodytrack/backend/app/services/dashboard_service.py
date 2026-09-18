"""
Agregação de dados para a tela "Início".

Nenhum cálculo aqui é sofisticado de propósito — são só as contas que
qualquer planilha faria (dias decorridos, % do período, streak de dias
consecutivos). A parte que importa é reunir tudo num único lugar
testável, em vez de espalhar essa lógica pelo frontend.
"""
import uuid
from datetime import date as date_
from datetime import timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.checkin import DailyCheckin
from app.models.measurement import BodyMeasurement
from app.models.project import Project
from app.models.user import User
from app.models.workout import Workout, WorkoutSession
from app.schemas.dashboard import DashboardSummary
from app.services.project_service import get_project_or_404


def _week_of_project(project: Project, today: date_) -> int:
    days_elapsed = (today - project.start_date).days
    return max(1, days_elapsed // 7 + 1)


def _total_weeks(project: Project) -> int:
    total_days = (project.end_date - project.start_date).days
    return max(1, round(total_days / 7))


def _percent_complete(project: Project, today: date_) -> float:
    total_days = (project.end_date - project.start_date).days or 1
    elapsed = min(max((today - project.start_date).days, 0), total_days)
    return round(elapsed / total_days * 100, 1)


def _compute_streak(db: Session, project_id: uuid.UUID) -> int:
    """
    Dias consecutivos com check-in, contando a partir do registro mais
    recente (não necessariamente hoje — se o usuário não abriu o app
    hoje ainda, o streak de ontem continua valendo até a meia-noite).
    """
    dates = db.scalars(
        select(DailyCheckin.date)
        .where(DailyCheckin.project_id == project_id)
        .order_by(DailyCheckin.date.desc())
    ).all()
    if not dates:
        return 0

    dates_set = set(dates)
    streak = 0
    cursor = dates[0]
    while cursor in dates_set:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _consistency_pct(db: Session, project_id: uuid.UUID, today: date_, window_days: int = 7) -> float:
    start = today - timedelta(days=window_days - 1)
    count = (
        db.scalar(
            select(func.count(DailyCheckin.id)).where(
                DailyCheckin.project_id == project_id,
                DailyCheckin.date >= start,
                DailyCheckin.date <= today,
            )
        )
        or 0
    )
    return round(min(count, window_days) / window_days * 100, 1)


def get_dashboard(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, today: Optional[date_] = None
) -> DashboardSummary:
    project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    today = today or date_.today()

    first_checkin = db.scalars(
        select(DailyCheckin)
        .where(DailyCheckin.project_id == project_id)
        .order_by(DailyCheckin.date)
    ).first()
    latest_checkin = db.scalars(
        select(DailyCheckin)
        .where(DailyCheckin.project_id == project_id)
        .order_by(DailyCheckin.date.desc())
    ).first()
    latest_measurement = db.scalars(
        select(BodyMeasurement)
        .where(BodyMeasurement.project_id == project_id)
        .order_by(BodyMeasurement.date.desc())
    ).first()

    initial_weight = project.initial_weight_kg or (first_checkin.weight_kg if first_checkin else None)
    current_weight = (latest_checkin.weight_kg if latest_checkin else None) or initial_weight
    weight_variation = (
        round(current_weight - initial_weight, 2)
        if initial_weight is not None and current_weight is not None
        else None
    )

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    workouts_this_week = (
        db.scalar(
            select(func.count(WorkoutSession.id))
            .join(Workout, WorkoutSession.workout_id == Workout.id)
            .where(
                Workout.project_id == project_id,
                WorkoutSession.date >= week_start,
                WorkoutSession.date <= week_end,
            )
        )
        or 0
    )

    user = db.get(User, user_id)
    bmi = None
    if current_weight and user and user.height_cm:
        height_m = user.height_cm / 100
        bmi = round(current_weight / (height_m**2), 1)

    is_today_checkin = bool(latest_checkin and latest_checkin.date == today)

    return DashboardSummary(
        project_name=project.name,
        day_of_project=(today - project.start_date).days + 1,
        week_of_project=_week_of_project(project, today),
        total_weeks=_total_weeks(project),
        percent_complete=_percent_complete(project, today),
        days_remaining=max((project.end_date - today).days, 0),
        streak_days=_compute_streak(db, project_id),
        consistency_pct_last_7_days=_consistency_pct(db, project_id, today),
        last_checkin_date=latest_checkin.date if latest_checkin else None,
        initial_weight_kg=initial_weight,
        current_weight_kg=current_weight,
        weight_variation_kg=weight_variation,
        bmi=bmi,
        waist_cm=latest_measurement.waist_cm if latest_measurement else None,
        abdomen_cm=latest_measurement.abdomen_cm if latest_measurement else None,
        hip_cm=latest_measurement.hip_cm if latest_measurement else None,
        water_liters_today=latest_checkin.water_liters if is_today_checkin else None,
        sleep_hours_last_night=latest_checkin.sleep_hours if is_today_checkin else None,
        steps_today=latest_checkin.steps if is_today_checkin else None,
        workouts_this_week=workouts_this_week,
    )
