"""
Engine e sessão do SQLAlchemy.

`get_db` é a dependency do FastAPI usada em todos os endpoints: garante
que cada requisição tem sua própria sessão e que ela é sempre fechada,
mesmo em caso de erro.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # evita erros de "conexão morta" após idle longo
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
