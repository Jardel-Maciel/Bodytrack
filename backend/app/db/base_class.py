"""
Base declarativa do SQLAlchemy + mixins reutilizados por todos os modelos.

Decisões de design (explicadas no README/arquitetura):

- IDs são UUID (não inteiros autoincrementais). Isso facilita a futura
  sincronização offline-first entre dispositivos: um registro criado no
  celular sem internet já nasce com um ID globalmente único, sem
  depender do servidor para gerar a sequência.
- Usamos o tipo `sqlalchemy.Uuid` (agnóstico de banco), não o
  `postgresql.UUID` específico do dialeto. Roda em produção sobre
  Postgres normalmente, mas também permite testes automatizados (Etapa
  13) contra SQLite em memória, sem precisar subir um Postgres real
  só para rodar a suíte de testes.
- Todo modelo tem created_at/updated_at — necessário para PWA offline
  (resolver conflitos por "quem mudou por último") e para os relatórios
  de evolução ao longo do tempo.
- TimestampMixin e UUIDMixin são compostos nos modelos concretos.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
