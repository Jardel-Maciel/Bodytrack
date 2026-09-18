"""
Usuário da plataforma.

Mesmo sendo um app "de uso pessoal" hoje, o modelo já nasce
multi-tenant: cada linha de dado sensível (check-in, medida, foto...)
tem uma FK direta ou indireta até `User.id`, e toda query no backend
filtra por esse dono. Isso é o que permite, no futuro, abrir o mesmo
banco para vários usuários sem reescrever nada — só remover a suposição
implícita de "sou o único usuário".
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Unidades preferidas — hoje só kg/cm/L são usados, mas já
    # deixamos o campo para não travar o produto no futuro (ex.: lb)
    unit_weight: Mapped[str] = mapped_column(String(10), default="kg", nullable=False)
    unit_length: Mapped[str] = mapped_column(String(10), default="cm", nullable=False)
    unit_volume: Mapped[str] = mapped_column(String(10), default="L", nullable=False)

    projects: Mapped[List["Project"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[List["Achievement"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
