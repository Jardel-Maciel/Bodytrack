import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.schemas.common import ORMModel


class WeeklyReportSummary(BaseModel):
    """
    O JSON congelado dentro de `weekly_reports.summary`. Linguagem
    deliberadamente descritiva ("foi observado", "variação registrada")
    em vez de prescritiva — o app relata o que os dados mostram, nunca
    diagnostica ou promete resultado (Etapa 9 e 16 do briefing).
    """

    week_number: int
    start_date: date
    end_date: date
    days_registered: int

    weight_start_kg: Optional[float]
    weight_end_kg: Optional[float]
    weight_variation_kg: Optional[float]

    waist_start_cm: Optional[float]
    waist_end_cm: Optional[float]
    waist_variation_cm: Optional[float]

    workouts_count: int
    avg_water_liters: Optional[float]
    avg_sleep_hours: Optional[float]
    avg_steps: Optional[float]
    diet_adherence_pct: Optional[float]


class WeeklyReportRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID
    week_number: int
    start_date: date
    end_date: date
    summary: dict
