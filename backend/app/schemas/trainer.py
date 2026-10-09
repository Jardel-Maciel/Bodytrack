import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.workout import WorkoutExerciseCreate, WorkoutExerciseRead


# ---------------- convites / vínculos ----------------

class InviteCreate(BaseModel):
    student_label: Optional[str] = Field(default=None, max_length=120)


class InviteRead(BaseModel):
    link_id: uuid.UUID
    invite_code: str
    invite_expires_at: datetime
    student_label: Optional[str]


class AcceptInvite(BaseModel):
    code: str = Field(min_length=4, max_length=16)
    share_photos: bool = False
    share_progress: bool = False


class ConsentUpdate(BaseModel):
    share_photos: Optional[bool] = None
    share_progress: Optional[bool] = None


class StudentSummary(BaseModel):
    """Uma linha da lista de alunos do personal."""

    link_id: uuid.UUID
    status: str                          # "pending" | "active"
    display_name: str
    invite_code: Optional[str]           # só enquanto pendente
    invite_expires_at: Optional[datetime]
    share_photos: bool
    share_progress: bool
    project_name: Optional[str]
    last_session_date: Optional[date]    # só se o aluno compartilha a evolução
    photos_count: Optional[int]          # só se o aluno compartilha as fotos


class MyTrainerLink(BaseModel):
    """Visão do ALUNO sobre um vínculo com um personal."""

    link_id: uuid.UUID
    trainer_name: str
    status: str
    share_photos: bool
    share_progress: bool
    accepted_at: Optional[datetime]


# ---------------- treinos montados pelo personal ----------------

class TrainerExerciseIn(WorkoutExerciseCreate):
    """Exercício no editor do personal. `id` presente = edita o existente; ausente = cria."""

    id: Optional[uuid.UUID] = None


class TrainerWorkoutIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    muscle_group: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
    exercises: list[TrainerExerciseIn] = Field(default_factory=list)


class TrainerWorkoutRead(ORMModel):
    id: uuid.UUID
    name: str
    muscle_group: Optional[str]
    notes: Optional[str]
    created_by_trainer_id: Optional[uuid.UUID]
    editable: bool = False               # True = foi este personal que montou
    exercises: list[WorkoutExerciseRead]   # inclui catalog_id (imagem de demonstração)


# ---------------- evolução ----------------

class WeightPoint(BaseModel):
    date: date
    weight_kg: float


class RecentSession(BaseModel):
    session_id: uuid.UUID
    date: date
    workout_name: str
    sets_count: int
    total_volume_kg: float


class StudentProgress(BaseModel):
    project_name: Optional[str]
    initial_weight_kg: Optional[float]
    weights: list[WeightPoint]
    latest_measurement_date: Optional[date]
    latest_waist_cm: Optional[float]
    sessions_last_30_days: int
    recent_sessions: list[RecentSession]
