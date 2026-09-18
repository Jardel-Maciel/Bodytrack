"""
Conquistas simples — sem competição entre usuários (conforme briefing).
`code` identifica a conquista (ex.: "first_workout", "7_day_streak") e o
catálogo de códigos vive no backend (services/achievements_service.py,
a ser criado na Etapa 7+), não no banco.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, UUIDMixin


class Achievement(UUIDMixin, Base):
    __tablename__ = "achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "code", name="uq_achievement_user_code"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="achievements")
