import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class WorkoutExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    order: int = 0
    target_sets: Optional[int] = Field(default=None, ge=1, le=20)
    target_reps: Optional[str] = Field(default=None, max_length=20)
    rest_seconds: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None


class WorkoutExerciseRead(ORMModel, WorkoutExerciseCreate):
    id: uuid.UUID


class WorkoutCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    muscle_group: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
    exercises: list[WorkoutExerciseCreate] = Field(default_factory=list)


class WorkoutRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    muscle_group: Optional[str]
    notes: Optional[str]
    is_active: bool
    exercises: list[WorkoutExerciseRead]


class ExerciseSetCreate(BaseModel):
    workout_exercise_id: uuid.UUID
    set_number: int = Field(ge=1)
    reps: int = Field(ge=1)
    load_kg: float = Field(ge=0)


class ExerciseSetRead(ORMModel, ExerciseSetCreate):
    id: uuid.UUID


class WorkoutSessionCreate(BaseModel):
    date: date
    notes: Optional[str] = None
    sets: list[ExerciseSetCreate] = Field(min_length=1)


class WorkoutSessionRead(ORMModel):
    id: uuid.UUID
    workout_id: uuid.UUID
    date: date
    notes: Optional[str]
    sets: list[ExerciseSetRead]
    total_volume_kg: float


class ExerciseProgressPoint(BaseModel):
    session_id: uuid.UUID
    session_date: date
    best_set_load_kg: float
    best_set_reps: int
    total_volume_kg: float


class ExerciseProgress(BaseModel):
    """
    'Última sessão x sessão atual', conforme pedido no briefing: para
    cada sessão em que o exercício foi feito, guardamos a MELHOR série
    (maior carga) e o volume total daquela sessão; `load_delta_kg`
    compara a última sessão com a penúltima.
    """

    workout_exercise_id: uuid.UUID
    exercise_name: str
    history: list[ExerciseProgressPoint]
    last_session: Optional[ExerciseProgressPoint]
    previous_session: Optional[ExerciseProgressPoint]
    load_delta_kg: Optional[float]
