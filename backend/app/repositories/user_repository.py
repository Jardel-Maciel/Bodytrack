from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email))


def create(db: Session, *, email: str, hashed_password: str, name: str, **extra) -> User:
    user = User(email=email, hashed_password=hashed_password, name=name, **extra)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, *, user: User, data: dict) -> User:
    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
