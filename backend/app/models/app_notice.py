"""
Aviso dentro do app (o "sininho"), gerado por eventos da área do personal:
treino novo/atualizado/removido, convite aceito, permissões alteradas, vínculo encerrado.

Não confundir com `Notification` (models/notification.py), que guarda as
PREFERÊNCIAS de lembrete do usuário (check-in, água...). Aqui é o histórico de
avisos que o usuário recebe e marca como lidos.

Avisos iguais e ainda NÃO lidos são agrupados (o texto é atualizado em vez de
criar outro), para o personal salvar o mesmo treino 5 vezes não gerar 5 avisos.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class AppNotice(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "app_notices"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    link_path: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # rota do app a abrir ao tocar
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def at(self) -> datetime:
        """Quando o aviso aconteceu (atualizado a cada agrupamento)."""
        return self.updated_at
