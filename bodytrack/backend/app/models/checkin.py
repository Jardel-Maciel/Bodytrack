"""
Check-in diário — o coração do app: 1 registro por dia por projeto.

Reúne peso, água, sono, energia, humor, passos, treino e os campos
simples de adesão alimentar (checkboxes), como pedido: nada de contagem
de calorias complexa no MVP.
"""
import uuid
from datetime import date, time
from typing import Optional

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, SmallInteger, Text, Time, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class DailyCheckin(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "daily_checkins"
    __table_args__ = (
        # Um único check-in por dia por projeto — evita duplicidade e
        # simplifica muito os cálculos de streak/consistência.
        UniqueConstraint("project_id", "date", name="uq_checkin_project_date"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Peso do dia (também poderia vir de body_measurements, mas manter
    # aqui permite registrar peso sem abrir a tela de medidas completas)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Água
    water_liters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Sono
    sleep_start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    sleep_end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_quality: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)  # 1..5

    # Atividade
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    trained_today: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Bem-estar subjetivo
    energy_level: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)  # 1..5
    mood_level: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)    # 1..5

    # Alimentação — simples e funcional, conforme especificado
    followed_diet: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    hit_protein_goal: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    avoided_ultraprocessed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    portion_control: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="checkins")
