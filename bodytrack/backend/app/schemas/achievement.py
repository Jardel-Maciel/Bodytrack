from datetime import datetime

from pydantic import BaseModel


class AchievementRead(BaseModel):
    code: str
    label: str
    unlocked_at: datetime
