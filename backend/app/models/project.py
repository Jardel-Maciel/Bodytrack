"""
Projeto de transformação (ex.: "Minha Transformação — 16 semanas").

Um usuário pode ter vários projetos ao longo do tempo (ex.: um projeto
de cutting, depois um de bulking). Praticamente todo o resto do app
(check-ins, medidas, fotos, treinos, metas) pertence a um Project, não
diretamente ao User — isso é o que permite calcular "semana 4 de 16",
comparar semana 1 x semana 16 etc. sem misturar dados de projetos
diferentes.
"""
import enum
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Enum, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"
    ARCHIVED = "archived"


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    goal_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Peso inicial é guardado explicitamente no projeto (não só inferido
    # do primeiro check-in) porque o usuário pode registrar o check-in
    # do dia 1 depois de criar o projeto, e o "peso inicial" precisa
    # ficar estável para todas as comparações de evolução.
    initial_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"), default=ProjectStatus.ACTIVE, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="projects")

    checkins: Mapped[List["DailyCheckin"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="DailyCheckin.date"
    )
    measurements: Mapped[List["BodyMeasurement"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="BodyMeasurement.date"
    )
    photos: Mapped[List["ProgressPhoto"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="ProgressPhoto.date"
    )
    workouts: Mapped[List["Workout"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    goals: Mapped[List["Goal"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    weekly_reports: Mapped[List["WeeklyReport"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
