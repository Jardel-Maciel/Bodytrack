"""
Peças reutilizadas pelos demais schemas Pydantic.

`ORMModel` liga o Pydantic ao SQLAlchemy: com `from_attributes=True`,
um endpoint pode devolver diretamente um objeto ORM (`Project`, por
exemplo) que o FastAPI serializa lendo os atributos do objeto, sem
precisar converter manualmente para dict.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(ORMModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
