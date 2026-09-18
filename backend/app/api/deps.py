"""
Dependencies compartilhadas pelos endpoints da API.

Na Etapa 3, `get_current_user_id` lia um header temporário (X-User-Id).
Agora que a Etapa 4 implementou login de verdade, a mesma função passa
a decodificar um JWT — e, como prometido no comentário original, nenhum
endpoint de negócio (projects, checkins, measurements, workouts...)
precisou mudar uma linha: eles só dependem de "me dê o UUID do usuário
atual", nunca de COMO isso é descoberto.
"""
import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import InvalidTokenError, decode_access_token
from app.db.session import get_db
from app.models.user import User

# HTTPBearer (em vez do fluxo OAuth2PasswordBearer padrão do FastAPI)
# porque o frontend faz login via JSON, não via formulário — o
# Swagger UI ainda ganha um botão "Authorize" para colar o token puro.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado."
        )
    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado."
        )

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado."
        )
    return user


def get_current_user_id(current_user: User = Depends(get_current_user)) -> uuid.UUID:
    return current_user.id
