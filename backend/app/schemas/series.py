from datetime import date

from pydantic import BaseModel

VALID_METRICS = (
    "weight_kg",
    "water_liters",
    "sleep_hours",
    "steps",
    "waist_cm",
    "abdomen_cm",
    "hip_cm",
    "training_frequency",
)
VALID_PERIODS = ("7d", "30d", "90d", "project")


class SeriesPoint(BaseModel):
    date: date
    value: float


class Series(BaseModel):
    metric: str
    period: str
    points: list[SeriesPoint]
