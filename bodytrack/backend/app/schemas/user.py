from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import TimestampedSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=120)
    birth_date: Optional[date] = None
    height_cm: Optional[float] = Field(default=None, gt=0)


class UserRead(TimestampedSchema):
    """Nunca inclui `hashed_password` — isso jamais sai da API."""

    email: str
    name: str
    birth_date: Optional[date] = None
    height_cm: Optional[float] = None
    unit_weight: str
    unit_length: str
    unit_volume: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    birth_date: Optional[date] = None
    height_cm: Optional[float] = Field(default=None, gt=0)
