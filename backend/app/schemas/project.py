from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.models.project import ProjectStatus
from app.schemas.common import TimestampedSchema


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    goal_description: Optional[str] = None
    start_date: date
    end_date: date
    initial_weight_kg: Optional[float] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date deve ser posterior a start_date")
        return self


class ProjectCreate(ProjectBase):
    """Payload de criação — status sempre nasce ACTIVE, não é escolhido pelo cliente."""


class ProjectUpdate(BaseModel):
    """
    Todos os campos opcionais: PATCH parcial. `exclude_unset=True` no
    endpoint garante que campos omitidos não sobrescrevem o valor atual.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    goal_description: Optional[str] = None
    end_date: Optional[date] = None
    status: Optional[ProjectStatus] = None


class ProjectRead(ProjectBase, TimestampedSchema):
    status: ProjectStatus
