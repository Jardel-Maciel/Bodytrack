import uuid
from typing import Any, Sequence

from sqlalchemy.orm import Session

from app.models.workout import Workout, WorkoutSession
from app.repositories import workout_repository as repo
from app.schemas.workout import ExerciseProgress, ExerciseProgressPoint
from app.services.project_service import get_project_or_404


class WorkoutNotFoundError(Exception):
    pass


class ExerciseNotFoundError(Exception):
    pass


class InvalidExerciseForWorkoutError(Exception):
    """Uma série referencia um workout_exercise_id que não pertence a este workout."""


def _ensure_project_ownership(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    get_project_or_404(db, project_id=project_id, user_id=user_id)


def create_workout(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, data: dict[str, Any]
) -> Workout:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    return repo.create_workout(db, project_id=project_id, data=data)


def list_workouts(db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> Sequence[Workout]:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    return repo.list_for_project(db, project_id=project_id)


def get_workout_or_404(
    db: Session, *, workout_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> Workout:
    _ensure_project_ownership(db, project_id=project_id, user_id=user_id)
    workout = repo.get_owned(db, workout_id=workout_id, project_id=project_id)
    if workout is None:
        raise WorkoutNotFoundError()
    return workout


def log_session(
    db: Session,
    *,
    workout_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict[str, Any],
) -> WorkoutSession:
    workout = get_workout_or_404(db, workout_id=workout_id, project_id=project_id, user_id=user_id)

    valid_exercise_ids = {exercise.id for exercise in workout.exercises}
    for set_data in data["sets"]:
        if set_data["workout_exercise_id"] not in valid_exercise_ids:
            raise InvalidExerciseForWorkoutError()

    return repo.create_session(db, workout_id=workout_id, data=data)


def list_sessions(
    db: Session, *, workout_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> Sequence[WorkoutSession]:
    get_workout_or_404(db, workout_id=workout_id, project_id=project_id, user_id=user_id)
    return repo.list_sessions(db, workout_id=workout_id)


def get_exercise_progress(
    db: Session,
    *,
    workout_id: uuid.UUID,
    exercise_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
) -> ExerciseProgress:
    workout = get_workout_or_404(db, workout_id=workout_id, project_id=project_id, user_id=user_id)
    exercise = next((e for e in workout.exercises if e.id == exercise_id), None)
    if exercise is None:
        raise ExerciseNotFoundError()

    sets = repo.get_exercise_history(db, workout_exercise_id=exercise_id)

    sessions_by_id: dict[uuid.UUID, list] = {}
    dates_by_id: dict[uuid.UUID, Any] = {}
    for s in sets:
        sessions_by_id.setdefault(s.session_id, []).append(s)
        dates_by_id[s.session_id] = s.session.date

    history: list[ExerciseProgressPoint] = []
    for session_id in sorted(sessions_by_id, key=lambda sid: dates_by_id[sid]):
        session_sets = sessions_by_id[session_id]
        best = max(session_sets, key=lambda s: s.load_kg)
        volume = sum(s.reps * s.load_kg for s in session_sets)
        history.append(
            ExerciseProgressPoint(
                session_id=session_id,
                session_date=dates_by_id[session_id],
                best_set_load_kg=best.load_kg,
                best_set_reps=best.reps,
                total_volume_kg=volume,
            )
        )

    last_session = history[-1] if history else None
    previous_session = history[-2] if len(history) >= 2 else None
    load_delta_kg = None
    if last_session and previous_session:
        load_delta_kg = round(last_session.best_set_load_kg - previous_session.best_set_load_kg, 2)

    return ExerciseProgress(
        workout_exercise_id=exercise_id,
        exercise_name=exercise.name,
        history=history,
        last_session=last_session,
        previous_session=previous_session,
        load_delta_kg=load_delta_kg,
    )
