from datetime import date
from typing import Optional

from pydantic import BaseModel


class TodayGoal(BaseModel):
    done: bool
    points: int


class TodayWater(TodayGoal):
    liters: Optional[float]
    goal_liters: Optional[float]


class TodayStatus(BaseModel):
    date: date
    login: TodayGoal
    water: TodayWater
    workout: TodayGoal


class DayPoints(BaseModel):
    day: date
    points: int


class PointEventRead(BaseModel):
    kind: str
    day: date
    points: int


class GamificationSummary(BaseModel):
    total_points: int
    level: int
    level_title: str
    points_in_level: int
    level_size: int
    points_to_next: int
    points_today: int
    today: TodayStatus
    last_7_days: list[DayPoints]
    recent: list[PointEventRead]
    rules: dict[str, int]
