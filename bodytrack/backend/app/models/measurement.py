"""
Medidas corporais — todas opcionais, o usuário preenche só o que mediu.
"""
import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Date, Float, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class BodyMeasurement(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "body_measurements"
    __table_args__ = (
        UniqueConstraint("project_id", "date", name="uq_measurement_project_date"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    neck_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    shoulders_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    chest_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    arm_right_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    arm_left_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    abdomen_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hip_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    thigh_right_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    thigh_left_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calf_right_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calf_left_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="measurements")
