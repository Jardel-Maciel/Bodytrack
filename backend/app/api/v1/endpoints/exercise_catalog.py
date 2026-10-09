from fastapi import APIRouter, Depends, Response

from app.api.deps import get_current_user_id
from app.schemas.exercise_catalog import ExerciseCatalogItem
from app.services import exercise_catalog_service

router = APIRouter()


@router.get("", response_model=list[ExerciseCatalogItem])
def list_exercise_catalog(
    response: Response,
    _user_id=Depends(get_current_user_id),
) -> list[dict]:
    """
    Catálogo completo (~90 itens, poucos KB). O frontend busca uma vez e usa
    para o autocomplete do formulário de treino e para o modal de demonstração.
    O conteúdo só muda quando o app é atualizado, então pode ficar em cache.
    """
    response.headers["Cache-Control"] = "private, max-age=3600"
    return exercise_catalog_service.list_catalog()
