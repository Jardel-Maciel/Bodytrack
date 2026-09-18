"""
Ponto de entrada da API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# IMPORTANTE: importa todos os modelos ANTES de qualquer rota rodar uma
# query. Modelos como User.notifications ou User.achievements referenciam
# a classe relacionada por STRING (relationship("Notification")), e o
# SQLAlchemy só resolve essa string quando a classe correspondente já foi
# importada em algum lugar do processo. Endpoints como /auth ou /projects
# nunca importam app.models.notification diretamente (não existe endpoint
# de notificações ainda) — sem esta linha, o primeiro request que tocasse
# o mapper de User quebraria com "failed to locate a name ('Notification')".
# Os testes (tests/conftest.py) não pegam esse bug porque importam
# `app.db.base` diretamente; rodando `uvicorn app.main:app` puro, sem essa
# linha, o processo real quebra. app/db/base.py é exatamente o módulo que
# centraliza a importação de todos os modelos (ver seu comentário).
import app.db.base  # noqa: F401,E402

from app.api.v1.router import api_router  # noqa: E402

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="API do BodyTrack — acompanhamento de recomposição corporal.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}
