import uuid
from datetime import date
from typing import Optional

from app.models.photo import PhotoAngle
from app.schemas.common import ORMModel


class PhotoRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID
    date: date
    week_number: Optional[int]
    angle: PhotoAngle
    is_private: bool


class PhotoComparison(ORMModel):
    """Fotos de duas semanas lado a lado — base do modo 'Antes e Depois'."""

    week_a: int
    week_b: int
    photos_a: list[PhotoRead]
    photos_b: list[PhotoRead]
