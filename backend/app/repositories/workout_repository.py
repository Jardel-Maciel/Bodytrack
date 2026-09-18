import uuid
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout import ExerciseSet, Workout, WorkoutExercise, WorkoutSession


def create_workout(db: Session, *, project_id: uuid.UUID, data: dict[str, Any]) -> Workout:
    exercises_data = data.pop("exercises", [])
    workout = Workout(project_id=project_id, **data)
    for exercise_data in exercises_data:
        workout.exercises.append(WorkoutExercise(**exercise_data))
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


def list_for_project(db: Session, *, project_id: uuid.UUID) -> Sequence[Workout]:
    stmt = (
        select(Workout)
        .where(Workout.project_id == project_id, Workout.is_active.is_(True))
        .options(selectinload(Workout.exercises))
        .order_by(Workout.created_at)
    )
    return db.scalars(stmt).all()


def get_owned(db: Session, *, workout_id: uuid.UUID, project_id: uuid.UUID) -> Optional[Workout]:
    stmt = (
        select(Workout)
        .where(Workout.id == workout_id, Workout.project_id == project_id)
        .options(selectinload(Workout.exercises))
    )
    return db.scalars(stmt).first()


def create_session(db: Session, *, workout_id: uuid.UUID, data: dict[str, Any]) -> WorkoutSession:
    sets_data = data.pop("sets", [])
    session_obj = WorkoutSession(workout_id=workout_id, **data)
    for set_data in sets_data:
        session_obj.sets.append(ExerciseSet(**set_data))
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj


def list_sessions(db: Session, *, workout_id: uuid.UUID) -> Sequence[WorkoutSession]:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.workout_id == workout_id)
        .options(selectinload(WorkoutSession.sets))
        .order_by(WorkoutSession.date)
    )
    return db.scalars(stmt).all()


def get_exercise_history(db: Session, *, workout_exercise_id: uuid.UUID) -> Sequence[ExerciseSet]:
    stmt = (
        select(ExerciseSet)
        .join(WorkoutSession, ExerciseSet.session_id == WorkoutSession.id)
        .where(ExerciseSet.workout_exercise_id == workout_exercise_id)
        .options(selectinload(ExerciseSet.session))
        .order_by(WorkoutSession.date)
    )
    return db.scalars(stmt).all()
