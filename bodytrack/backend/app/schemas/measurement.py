import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema

_FIELDS = (
    "weight_kg",
    "neck_cm",
    "shoulders_cm",
    "chest_cm",
    "arm_right_cm",
    "arm_left_cm",
    "waist_cm",
    "abdomen_cm",
    "hip_cm",
    "thigh_right_cm",
    "thigh_left_cm",
    "calf_right_cm",
    "calf_left_cm",
)


class MeasurementBase(BaseModel):
    date: date
    # Todos opcionais, conforme pedido: "não obrigar o usuário a
    # preencher todas as medidas, permitir registrar só as disponíveis".
    weight_kg: Optional[float] = Field(default=None, gt=0)
    neck_cm: Optional[float] = Field(default=None, gt=0)
    shoulders_cm: Optional[float] = Field(default=None, gt=0)
    chest_cm: Optional[float] = Field(default=None, gt=0)
    arm_right_cm: Optional[float] = Field(default=None, gt=0)
    arm_left_cm: Optional[float] = Field(default=None, gt=0)
    waist_cm: Optional[float] = Field(default=None, gt=0)
    abdomen_cm: Optional[float] = Field(default=None, gt=0)
    hip_cm: Optional[float] = Field(default=None, gt=0)
    thigh_right_cm: Optional[float] = Field(default=None, gt=0)
    thigh_left_cm: Optional[float] = Field(default=None, gt=0)
    calf_right_cm: Optional[float] = Field(default=None, gt=0)
    calf_left_cm: Optional[float] = Field(default=None, gt=0)


class MeasurementCreate(MeasurementBase):
    project_id: uuid.UUID


class MeasurementUpdate(BaseModel):
    weight_kg: Optional[float] = Field(default=None, gt=0)
    neck_cm: Optional[float] = Field(default=None, gt=0)
    shoulders_cm: Optional[float] = Field(default=None, gt=0)
    chest_cm: Optional[float] = Field(default=None, gt=0)
    arm_right_cm: Optional[float] = Field(default=None, gt=0)
    arm_left_cm: Optional[float] = Field(default=None, gt=0)
    waist_cm: Optional[float] = Field(default=None, gt=0)
    abdomen_cm: Optional[float] = Field(default=None, gt=0)
    hip_cm: Optional[float] = Field(default=None, gt=0)
    thigh_right_cm: Optional[float] = Field(default=None, gt=0)
    thigh_left_cm: Optional[float] = Field(default=None, gt=0)
    calf_right_cm: Optional[float] = Field(default=None, gt=0)
    calf_left_cm: Optional[float] = Field(default=None, gt=0)


class MeasurementRead(MeasurementBase, TimestampedSchema):
    project_id: uuid.UUID


class MeasurementFieldProgress(BaseModel):
    """Comparação inicial x atual de UM campo de medida (ex.: cintura)."""

    field: str
    initial_value: Optional[float]
    current_value: Optional[float]
    variation: Optional[float]
    variation_pct: Optional[float]


class MeasurementProgress(BaseModel):
    """Resumo de evolução de todas as medidas, usado na tela de Medidas."""

    fields: list[MeasurementFieldProgress]
