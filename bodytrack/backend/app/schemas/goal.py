import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.models.goal import GoalType
from app.schemas.common import ORMModel


class GoalCreate(BaseModel):
    type: GoalType
    target_value: float = Field(gt=0)
    # Só usado quando type == "strength", ex.: "Supino reto".
    target_exercise_name: Optional[str] = Field(default=None, max_length=150)


class GoalUpdate(BaseModel):
    target_value: Optional[float] = Field(default=None, gt=0)
    achieved: Optional[bool] = None


class GoalRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID
    type: GoalType
    target_value: float
    target_exercise_name: Optional[str]
    achieved: bool
