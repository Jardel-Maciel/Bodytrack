"""
Livro-razão de pontos da gamificação: UMA linha por ponto ganho.

A restrição única (user_id, kind, day) é a trava central do sistema: cada tipo
de ponto só pode ser ganho UMA vez por usuário por dia. É o banco que garante
isso (e não só um "if" no código), então nem duas requisições simultâneas nem o
reenvio de um check-in offline conseguem pontuar em dobro.

O total de pontos NÃO é guardado: é a soma das linhas. Assim nunca fica
dessincronizado e dá para ajustar as regras sem migrar dados.
"""
import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class PointEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "point_events"
    __table_args__ = (UniqueConstraint("user_id", "kind", "day", name="uq_point_event_user_kind_day"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # "login" | "water" | "workout"
    day: Mapped[date] = mapped_column(Date, nullable=False)        # dia a que o ponto se refere (fuso do app)
    points: Mapped[int] = mapped_column(Integer, nullable=False)   # valor na época (mudar a regra não altera o passado)
