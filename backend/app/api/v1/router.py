"""
Router agregador da v1 da API. Cada domínio ganha seu próprio arquivo
em app/api/v1/endpoints/ e é incluído aqui. Manter tudo versionado sob
/api/v1 evita quebrar o app quando surgirem mudanças incompatíveis no
futuro (ex.: quando o produto virar multiusuário "de verdade").
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    achievements,
    auth,
    checkins,
    dashboard,
    goals,
    measurements,
    photos,
    projects,
    reports,
    series,
    workouts,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])

# Recursos aninhados em /projects/{project_id}/... — cada um pertence a
# um projeto específico, nunca são acessados soltos.
api_router.include_router(checkins.router, prefix="/projects/{project_id}/checkins", tags=["checkins"])
api_router.include_router(
    measurements.router, prefix="/projects/{project_id}/measurements", tags=["measurements"]
)
api_router.include_router(workouts.router, prefix="/projects/{project_id}/workouts", tags=["workouts"])
api_router.include_router(goals.router, prefix="/projects/{project_id}/goals", tags=["goals"])
api_router.include_router(dashboard.router, prefix="/projects/{project_id}/dashboard", tags=["dashboard"])
api_router.include_router(series.router, prefix="/projects/{project_id}/series", tags=["series"])
api_router.include_router(photos.router, prefix="/projects/{project_id}/photos", tags=["photos"])
api_router.include_router(reports.router, prefix="/projects/{project_id}/reports", tags=["reports"])
api_router.include_router(
    achievements.router, prefix="/projects/{project_id}/achievements", tags=["achievements"]
)
