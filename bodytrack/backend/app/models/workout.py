"""
Módulo de treino — 4 entidades que trabalham juntas:

Workout            "Treino A" — um MODELO/rotina (ex.: "Peito e tríceps")
WorkoutExercise     um exercício dentro dessa rotina (ex.: "Supino reto"),
                    com a meta planejada (séries/reps/carga alvo)
WorkoutSession      uma EXECUÇÃO real do treino em um dia específico
ExerciseSet         cada série realmente executada em uma sessão, para
                    um exercício específico (peso e reps reais)

Essa separação entre "modelo" (Workout/WorkoutExercise) e "execução"
(WorkoutSession/ExerciseSet) é o que permite comparar "última sessão
55kg x8" com "sessão atual 60kg x8" e montar o gráfico de evolução de
carga ao longo das semanas, sem perder o histórico quando o usuário
ajusta a rotina.
"""
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Float, ForeignKey, Integer, SmallInteger, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class Workout(UUIDMixin, TimestampMixin, Base):
    """Um modelo de treino, ex.: 'Treino A — Peito e tríceps'."""

    __tablename__ = "workouts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)          # "Treino A"
    muscle_group: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="workouts")
    exercises: Mapped[List["WorkoutExercise"]] = relationship(
        back_populates="workout", cascade="all, delete-orphan", order_by="WorkoutExercise.order"
    )
    sessions: Mapped[List["WorkoutSession"]] = relationship(
        back_populates="workout", cascade="all, delete-orphan", order_by="WorkoutSession.date"
    )


class WorkoutExercise(UUIDMixin, TimestampMixin, Base):
    """Um exercício dentro de um Workout, com a meta planejada."""

    __tablename__ = "workout_exercises"

    workout_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workouts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)   # "Supino reto"
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    target_sets: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    target_reps: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # ex.: "8-10"
    rest_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    workout: Mapped["Workout"] = relationship(back_populates="exercises")
    sets: Mapped[List["ExerciseSet"]] = relationship(
        back_populates="workout_exercise", cascade="all, delete-orphan"
    )


class WorkoutSession(UUIDMixin, TimestampMixin, Base):
    """Uma execução real de um Workout em uma data específica."""

    __tablename__ = "workout_sessions"

    workout_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workouts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Tipo explícito (Date) passado ao mapped_column: evita ambiguidade
    # do SQLAlchemy ao resolver a anotação quando o nome do atributo
    # ("date") coincide com o nome do tipo Python importado (datetime.date).
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    workout: Mapped["Workout"] = relationship(back_populates="sessions")
    sets: Mapped[List["ExerciseSet"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    @property
    def total_volume_kg(self) -> float:
        """volume = Σ (séries × repetições × carga) de todas as séries da sessão."""
        return sum((s.reps or 0) * (s.load_kg or 0) for s in self.sets)


class ExerciseSet(UUIDMixin, TimestampMixin, Base):
    """Uma série realmente executada: N repetições com determinada carga."""

    __tablename__ = "exercise_sets"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workout_sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workout_exercises.id", ondelete="CASCADE"), index=True, nullable=False
    )

    set_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    load_kg: Mapped[float] = mapped_column(Float, nullable=False)

    session: Mapped["WorkoutSession"] = relationship(back_populates="sets")
    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="sets")
