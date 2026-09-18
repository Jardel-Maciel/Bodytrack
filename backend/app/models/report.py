"""
Relatório semanal — snapshot calculado e "congelado" ao final de cada
semana (peso inicial/final da semana, treinos feitos, médias etc.).
Guardamos o resultado já calculado (JSON) em vez de recalcular sempre
em tempo real: assim o relatório de "semana 4" não muda retroativamente
se o usuário editar um registro antigo depois, e fica rápido de exibir
no histórico de relatórios.
"""
import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class WeeklyReport(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "weekly_reports"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Estrutura livre, validada pelo schema Pydantic `WeeklyReportSummary`
    # (Etapa 11): peso_inicio, peso_fim, treinos, agua_media, sono_medio,
    # adesao_alimentar_pct, passos_media, destaques[]
    summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    project: Mapped["Project"] = relationship(back_populates="weekly_reports")
