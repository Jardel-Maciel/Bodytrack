"""
Fotos de evolução — dado sensível por natureza (ver seção de
privacidade). O modelo guarda apenas o CAMINHO/URL do arquivo, nunca o
binário no banco; o storage real fica atrás de app/services/storage,
que hoje grava em disco local e amanhã pode virar S3/R2 sem migrar
esta tabela.
"""
import enum
import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class PhotoAngle(str, enum.Enum):
    FRONT = "front"
    SIDE = "side"
    BACK = "back"


class ProgressPhoto(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "progress_photos"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    angle: Mapped[PhotoAngle] = mapped_column(Enum(PhotoAngle, name="photo_angle"), nullable=False)

    # Caminho relativo dentro do storage configurado — nunca uma URL
    # pública direta, pois o acesso é sempre mediado por um endpoint
    # autenticado que confere se o usuário é o dono da foto.
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    is_private: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="photos")
