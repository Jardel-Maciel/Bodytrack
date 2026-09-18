"""
Infraestrutura de testes.

Usamos SQLite em memória em vez do Postgres real: como os modelos usam
`sqlalchemy.Uuid` (agnóstico de dialeto, ver app/db/base_class.py), o
mesmo schema roda em ambos. Isso deixa a suíte de testes rápida e sem
dependência externa — nenhum docker/Postgres precisa estar no ar para
rodar `pytest`.
"""
import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.project import Project
from app.models.user import User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def make_user(db_session):
    """Factory para criar usuários de teste diretamente no banco (bypassa /auth/register)."""

    def _make(email: str = "user@example.com", password: str = "senha12345") -> User:
        user = User(email=email, hashed_password=hash_password(password), name="Usuário de Teste")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make


@pytest.fixture()
def auth_headers():
    """Gera o header Authorization: Bearer <token> para um usuário de teste."""

    def _headers(user: User) -> dict:
        token = create_access_token(subject=user.id)
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture()
def make_project(db_session):
    """Factory para criar um projeto de teste direto no banco, sem passar pela API."""

    def _make(user: User, **overrides) -> Project:
        data = dict(
            user_id=user.id,
            name="Projeto de Teste",
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 12, 31),
            initial_weight_kg=100,
        )
        data.update(overrides)
        project = Project(**data)
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        return project

    return _make
