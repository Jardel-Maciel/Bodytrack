"""
Metas — sempre definidas pelo usuário, nunca sugeridas como promessa de
resultado (ver seção 34 do briefing: nada de "você vai perder X kg").
"""
import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class GoalType(str, enum.Enum):
    WEIGHT = "weight"
    WAIST = "waist"
    TRAINING_FREQUENCY = "training_frequency"   # treinos/semana
    WATER = "water"                             # L/dia
    SLEEP = "sleep"                             # horas/noite
    STEPS = "steps"                             # passos/dia
    STRENGTH = "strength"                       # carga alvo num exercício


class Goal(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "goals"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[GoalType] = mapped_column(Enum(GoalType, name="goal_type"), nullable=False)

    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    # Usado só quando type == STRENGTH, ex.: "Supino reto"
    target_exercise_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    achieved: Mapped[bool] = mapped_column(default=False, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="goals")
