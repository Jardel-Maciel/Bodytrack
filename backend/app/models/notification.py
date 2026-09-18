"""
Notificações/lembretes configuráveis (check-in, água, medidas, fotos,
treino atrasado). No MVP isso vira notificações locais do PWA
(Notifications API do navegador); este modelo guarda a PREFERÊNCIA e o
histórico, não a entrega em si.
"""
import enum
import uuid
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Time, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class NotificationType(str, enum.Enum):
    DAILY_CHECKIN = "daily_checkin"
    WATER_REMINDER = "water_reminder"
    MEASUREMENT_REMINDER = "measurement_reminder"
    PHOTO_REMINDER = "photo_reminder"
    WORKOUT_INACTIVITY = "workout_inactivity"


class Notification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"), nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scheduled_time: Mapped[Optional[str]] = mapped_column(Time, nullable=True)
    message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="notifications")
