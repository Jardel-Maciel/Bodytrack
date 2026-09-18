"""
Conquistas simples (Etapa 13 do briefing original), sem competição
entre usuários — só marcos da própria jornada.

Simplificação assumida: como as conquistas são avaliadas "quando a
tela de conquistas é aberta" (não há um job em segundo plano), elas só
enxergam os dados do projeto que está sendo consultado, mesmo a tabela
`achievements` sendo por usuário. Para um usuário com um único projeto
ativo por vez (o caso de uso do MVP), isso é equivalente a olhar tudo;
vale revisitar se o produto ganhar múltiplos projetos simultâneos.
"""
import uuid
from datetime import date as date_

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.achievement import Achievement
from app.models.checkin import DailyCheckin
from app.models.photo import ProgressPhoto
from app.models.workout import Workout, WorkoutSession
from app.repositories import workout_repository
from app.schemas.achievement import AchievementRead
from app.services.dashboard_service import _compute_streak, _week_of_project
from app.services.project_service import get_project_or_404

CATALOG = {
    "first_checkin": "Primeiro check-in registrado",
    "streak_7": "7 dias de consistência",
    "days_30": "30 dias registrados",
    "first_workout": "Primeiro treino registrado",
    "workouts_10": "10 treinos concluídos",
    "first_pr": "Primeiro recorde pessoal (PR)",
    "weeks_4": "4 semanas completas",
    "water_100l": "100 litros de água registrados",
    "first_photo_comparison": "Primeiro comparativo de fotos",
}


def _has_any_pr(db: Session, *, project_id: uuid.UUID) -> bool:
    """Verdadeiro se, em algum exercício, uma sessão bateu a melhor carga de todas as sessões anteriores."""
    for workout in workout_repository.list_for_project(db, project_id=project_id):
        for exercise in workout.exercises:
            sets = workout_repository.get_exercise_history(db, workout_exercise_id=exercise.id)
            sessions: dict[uuid.UUID, list[float]] = {}
            dates: dict[uuid.UUID, date_] = {}
            for s in sets:
                sessions.setdefault(s.session_id, []).append(s.load_kg)
                dates[s.session_id] = s.session.date

            ordered_session_ids = sorted(sessions, key=lambda sid: dates[sid])
            best_so_far: float | None = None
            for session_id in ordered_session_ids:
                session_best = max(sessions[session_id])
                if best_so_far is not None and session_best > best_so_far:
                    return True
                best_so_far = session_best if best_so_far is None else max(best_so_far, session_best)
    return False


def check_and_unlock(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    already_unlocked = set(
        db.scalars(select(Achievement.code).where(Achievement.user_id == user_id)).all()
    )

    def unlock(code: str) -> None:
        if code not in already_unlocked:
            db.add(Achievement(user_id=user_id, code=code))
            already_unlocked.add(code)

    checkins_count = (
        db.scalar(select(func.count(DailyCheckin.id)).where(DailyCheckin.project_id == project_id)) or 0
    )
    if checkins_count >= 1:
        unlock("first_checkin")
    if checkins_count >= 30:
        unlock("days_30")
    if _compute_streak(db, project_id) >= 7:
        unlock("streak_7")

    sessions_count = (
        db.scalar(
            select(func.count(WorkoutSession.id))
            .join(Workout, WorkoutSession.workout_id == Workout.id)
            .where(Workout.project_id == project_id)
        )
        or 0
    )
    if sessions_count >= 1:
        unlock("first_workout")
    if sessions_count >= 10:
        unlock("workouts_10")

    water_total = (
        db.scalar(select(func.sum(DailyCheckin.water_liters)).where(DailyCheckin.project_id == project_id)) or 0
    )
    if water_total >= 100:
        unlock("water_100l")

    weeks_with_photos = (
        db.scalar(
            select(func.count(func.distinct(ProgressPhoto.week_number))).where(
                ProgressPhoto.project_id == project_id, ProgressPhoto.week_number.isnot(None)
            )
        )
        or 0
    )
    if weeks_with_photos >= 2:
        unlock("first_photo_comparison")

    if _week_of_project(project, date_.today()) >= 4:
        unlock("weeks_4")

    if _has_any_pr(db, project_id=project_id):
        unlock("first_pr")

    db.commit()


def list_achievements(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> list[AchievementRead]:
    check_and_unlock(db, project_id=project_id, user_id=user_id)
    rows = db.scalars(
        select(Achievement).where(Achievement.user_id == user_id).order_by(Achievement.unlocked_at)
    ).all()
    return [
        AchievementRead(code=a.code, label=CATALOG.get(a.code, a.code), unlocked_at=a.unlocked_at)
        for a in rows
    ]
