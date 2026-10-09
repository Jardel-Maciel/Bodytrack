"""
Vínculo entre um personal (trainer) e um aluno (student).

Fluxo, sempre com CONSENTIMENTO do aluno:

1. O personal cria um convite  -> linha com status "pending", `invite_code`
   gerado e `student_id` ainda vazio.
2. O aluno digita o código no app e escolhe o que compartilha
   (`share_photos`, `share_progress`) -> status "active" e `student_id` preenchido.
3. Aluno OU personal podem encerrar a qualquer momento -> status "revoked".
   O personal perde o acesso na hora; os treinos que ele montou continuam com o aluno.

Tudo que o personal acessa de um aluno passa por UMA linha "active" desta
tabela: sem vínculo ativo (ou sem a permissão específica), a API responde 404/403.
Status é String (e não Enum do Postgres) para facilitar evolução futura sem
migração de tipo.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, UUIDMixin

LINK_PENDING = "pending"
LINK_ACTIVE = "active"
LINK_REVOKED = "revoked"


class TrainerStudentLink(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "trainer_student_links"

    trainer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )
    # Como o personal chama o aluno enquanto o convite não foi aceito (ex.: "João da academia").
    student_label: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    invite_code: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    invite_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(10), default=LINK_PENDING, nullable=False, index=True)

    # Permissões dadas PELO ALUNO (padrão: nada compartilhado até ele aceitar e escolher).
    share_photos: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    share_progress: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
