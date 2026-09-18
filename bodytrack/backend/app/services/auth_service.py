from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(
    db: Session, *, email: str, password: str, name: str, birth_date=None, height_cm=None
) -> User:
    if user_repository.get_by_email(db, email):
        raise EmailAlreadyRegisteredError()
    return user_repository.create(
        db,
        email=email,
        hashed_password=hash_password(password),
        name=name,
        birth_date=birth_date,
        height_cm=height_cm,
    )


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    # Mesma mensagem de erro para "e-mail não existe" e "senha errada" —
    # de propósito, para não revelar a um atacante quais e-mails estão
    # cadastrados na base.
    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()
    return user
