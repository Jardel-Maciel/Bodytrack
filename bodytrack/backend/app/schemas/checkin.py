import uuid
from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema


class CheckinBase(BaseModel):
    date: date
    weight_kg: Optional[float] = Field(default=None, gt=0)
    water_liters: Optional[float] = Field(default=None, ge=0)
    sleep_start: Optional[time] = None
    sleep_end: Optional[time] = None
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=5)
    steps: Optional[int] = Field(default=None, ge=0)
    trained_today: bool = False
    energy_level: Optional[int] = Field(default=None, ge=1, le=5)
    mood_level: Optional[int] = Field(default=None, ge=1, le=5)
    followed_diet: Optional[bool] = None
    hit_protein_goal: Optional[bool] = None
    avoided_ultraprocessed: Optional[bool] = None
    portion_control: Optional[bool] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class CheckinCreate(CheckinBase):
    project_id: uuid.UUID


class CheckinUpdate(BaseModel):
    """PATCH parcial — todos os campos exceto `date`/`project_id`, que identificam o registro."""

    weight_kg: Optional[float] = Field(default=None, gt=0)
    water_liters: Optional[float] = Field(default=None, ge=0)
    sleep_start: Optional[time] = None
    sleep_end: Optional[time] = None
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=5)
    steps: Optional[int] = Field(default=None, ge=0)
    trained_today: Optional[bool] = None
    energy_level: Optional[int] = Field(default=None, ge=1, le=5)
    mood_level: Optional[int] = Field(default=None, ge=1, le=5)
    followed_diet: Optional[bool] = None
    hit_protein_goal: Optional[bool] = None
    avoided_ultraprocessed: Optional[bool] = None
    portion_control: Optional[bool] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class CheckinRead(CheckinBase, TimestampedSchema):
    project_id: uuid.UUID
