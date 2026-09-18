"""
Segurança: hash de senha (Etapa 3) + emissão/verificação de JWT (Etapa 4).

Como o JWT funciona aqui, resumidamente: `create_access_token` empacota
o ID do usuário e uma data de expiração num payload, assina esse
payload com `SECRET_KEY` usando HMAC-SHA256 (HS256) e devolve uma
string em 3 partes (header.payload.assinatura). Qualquer um pode LER o
payload (é só base64, não é criptografado), mas ninguém sem a
SECRET_KEY consegue FORJAR uma assinatura válida — é isso que permite
ao backend confiar no token sem consultar o banco a cada requisição
(além de checar se o usuário ainda existe, que fazemos por segurança
extra em `get_current_user`).
"""
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# Usamos a biblioteca `bcrypt` diretamente (em vez de `passlib`, mais
# comum em tutoriais). Motivo prático: no momento em que este projeto
# foi criado, a combinação passlib 1.7 + bcrypt 4/5 tem um bug conhecido
# de compatibilidade (passlib faz um autoteste interno que quebra com
# versões recentes do bcrypt). Chamar o bcrypt direto é só duas funções
# e remove essa dependência frágil.
#
# bcrypt trunca silenciosamente segredos maiores que 72 bytes — por
# isso cortamos explicitamente, para não depender desse comportamento
# implícito da biblioteca.
_MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.checkpw(truncated, hashed_password.encode("utf-8"))


class InvalidTokenError(Exception):
    """Token ausente, malformado, expirado ou assinado com outra chave."""


def create_access_token(subject: uuid.UUID, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise InvalidTokenError("Token sem 'sub'")
        return uuid.UUID(subject)
    except (JWTError, ValueError) as exc:
        raise InvalidTokenError(str(exc)) from exc
