import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.workout import (
    ExerciseProgress,
    WorkoutCreate,
    WorkoutRead,
    WorkoutSessionCreate,
    WorkoutSessionRead,
)
from app.services import workout_service
from app.services.project_service import ProjectNotFoundError
from app.services.workout_service import (
    ExerciseNotFoundError,
    InvalidExerciseForWorkoutError,
    WorkoutNotFoundError,
)

router = APIRouter()


@router.post("", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(
    project_id: uuid.UUID,
    payload: WorkoutCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> WorkoutRead:
    try:
        return workout_service.create_workout(
            db, project_id=project_id, user_id=user_id, data=payload.model_dump()
        )
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("", response_model=list[WorkoutRead])
def list_workouts(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[WorkoutRead]:
    try:
        return list(workout_service.list_workouts(db, project_id=project_id, user_id=user_id))
    except ProjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado")


@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(
    project_id: uuid.UUID,
    workout_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> WorkoutRead:
    try:
        return workout_service.get_workout_or_404(
            db, workout_id=workout_id, project_id=project_id, user_id=user_id
        )
    except (ProjectNotFoundError, WorkoutNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Treino não encontrado")


@router.post(
    "/{workout_id}/sessions", response_model=WorkoutSessionRead, status_code=status.HTTP_201_CREATED
)
def log_session(
    project_id: uuid.UUID,
    workout_id: uuid.UUID,
    payload: WorkoutSessionCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> WorkoutSessionRead:
    try:
        return workout_service.log_session(
            db, workout_id=workout_id, project_id=project_id, user_id=user_id, data=payload.model_dump()
        )
    except (ProjectNotFoundError, WorkoutNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Treino não encontrado")
    except InvalidExerciseForWorkoutError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Uma das séries referencia um exercício que não pertence a este treino."
        )


@router.get("/{workout_id}/sessions", response_model=list[WorkoutSessionRead])
def list_sessions(
    project_id: uuid.UUID,
    workout_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> list[WorkoutSessionRead]:
    try:
        return list(
            workout_service.list_sessions(
                db, workout_id=workout_id, project_id=project_id, user_id=user_id
            )
        )
    except (ProjectNotFoundError, WorkoutNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Treino não encontrado")


@router.get("/{workout_id}/exercises/{exercise_id}/progress", response_model=ExerciseProgress)
def get_exercise_progress(
    project_id: uuid.UUID,
    workout_id: uuid.UUID,
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> ExerciseProgress:
    try:
        return workout_service.get_exercise_progress(
            db,
            workout_id=workout_id,
            exercise_id=exercise_id,
            project_id=project_id,
            user_id=user_id,
        )
    except (ProjectNotFoundError, WorkoutNotFoundError, ExerciseNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Treino ou exercício não encontrado")
