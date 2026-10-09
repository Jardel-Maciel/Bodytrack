import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from app.schemas.common import ORMModel


class NotificationRead(ORMModel):
    id: uuid.UUID
    kind: str
    title: str
    body: Optional[str]
    link_path: Optional[str]
    at: datetime
    read_at: Optional[datetime] = Field(default=None, exclude=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def read(self) -> bool:
        return self.read_at is not None


class NotificationList(BaseModel):
    items: list[NotificationRead]
    unread_count: int


class MarkRead(BaseModel):
    ids: Optional[list[uuid.UUID]] = None  # None = marcar todos


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class MessageRead(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    created_at: datetime
    mine: bool


class ChatUnread(BaseModel):
    total: int
    by_link: dict[str, int]
