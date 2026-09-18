from datetime import date
from typing import Optional

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """
    Tudo que a tela 'Início' precisa para responder, de cara, "como
    estou evoluindo?" — um único endpoint agrega dados que vêm de
    Project, DailyCheckin, BodyMeasurement e WorkoutSession, pra o
    frontend não precisar orquestrar 5 chamadas para montar uma tela.
    """

    project_name: str
    day_of_project: int
    week_of_project: int
    total_weeks: int
    percent_complete: float
    days_remaining: int

    streak_days: int
    consistency_pct_last_7_days: float
    last_checkin_date: Optional[date]

    initial_weight_kg: Optional[float]
    current_weight_kg: Optional[float]
    weight_variation_kg: Optional[float]
    bmi: Optional[float]

    waist_cm: Optional[float]
    abdomen_cm: Optional[float]
    hip_cm: Optional[float]

    water_liters_today: Optional[float]
    sleep_hours_last_night: Optional[float]
    steps_today: Optional[int]
    workouts_this_week: int
