from typing import Optional

from pydantic import BaseModel


class ExerciseCatalogItem(BaseModel):
    """Um exercício do catálogo, pronto para o frontend (autocomplete + modal de demonstração)."""

    id: str
    name: str
    aliases: list[str]
    primary_muscles: list[str]
    secondary_muscles: list[str]
    equipment: str
    image_count: int
    video_url: Optional[str] = None  # vídeo em loop (mp4); None = mostra as imagens
