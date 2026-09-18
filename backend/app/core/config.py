"""
Configuração central da aplicação.

Usamos pydantic-settings para carregar variáveis de ambiente de forma
tipada e validada. Nenhum segredo fica hard-coded no código: tudo vem
do .env (que nunca deve ser commitado — veja .env.example).
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Aplicação
    APP_NAME: str = "BodyTrack API"
    ENV: str = "development"
    DEBUG: bool = True

    # Banco de dados
    DATABASE_URL: str = "postgresql+psycopg2://bodytrack:bodytrack@localhost:5432/bodytrack"

    # Segurança / JWT
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24          # 1 dia
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30    # 30 dias

    # CORS — origens do frontend autorizadas a chamar a API
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Armazenamento de fotos
    # "local" grava em disco (backend/storage/photos); em produção trocar
    # por um provedor de object storage (S3, R2, Spaces) sem mudar o
    # restante do código — ver app/services/storage_service.py
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_PATH: str = "storage/photos"
    MAX_PHOTO_SIZE_MB: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Cache simples: lê o .env uma única vez por processo."""
    return Settings()


settings = get_settings()
