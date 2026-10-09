"""
Gamificação: pontos por constância.

Regras (valores em POINTS; cada uma vale UMA vez por dia):
  login    +5   primeiro acesso do dia (login OU abrir o app já logado — o PWA fica logado por dias)
  water    +10  bateu a meta de água do dia (meta do projeto; se não houver, DEFAULT_WATER_GOAL_L)
  workout  +15  treinou no dia (sessão de treino registrada OU check-in com "treinei hoje")

Decisões importantes:
- Sem ranking entre usuários (o briefing do projeto pede "sem competição").
- O "dia" é o do fuso APP_TIMEZONE (padrão São Paulo), não UTC.
- Só pontua dia entre hoje e BACKDATE_DAYS atrás: dá folga para check-in feito offline e
  sincronizado depois, mas não deixa lançar um mês de treinos retroativos para ganhar pontos.
- Pontuar é "melhor esforço": se algo aqui falhar, o check-in/treino/login que o originou
  NÃO pode falhar junto (ver _safe).
"""
import logging
import math
import uuid
from datetime import date, datetime, timedelta
from functools import wraps
from typing import Any, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.checkin import DailyCheckin
from app.models.goal import Goal, GoalType
from app.models.point_event import PointEvent
from app.models.project import Project, ProjectStatus

logger = logging.getLogger(__name__)

POINTS = {"login": 5, "water": 10, "workout": 15}
DEFAULT_WATER_GOAL_L = 2.5
BACKDATE_DAYS = 7
LEVEL_TITLES = ["Iniciante", "Aprendiz", "Constante", "Dedicado", "Focado",
                "Persistente", "Atleta", "Veterano", "Mestre", "Lenda"]


def today() -> date:
    """Hoje no fuso do app. Função separada para os testes conseguirem fixar o dia."""
    return datetime.now(ZoneInfo(settings.APP_TIMEZONE)).date()


def _safe(fn):
    """Gamificação nunca derruba a operação principal (que já foi gravada antes de chegar aqui)."""
    @wraps(fn)
    def wrapper(db: Session, *args: Any, **kwargs: Any):
        try:
            return fn(db, *args, **kwargs)
        except Exception:  # noqa: BLE001 - melhor esforço, mas registra para investigar
            logger.exception("Falha ao registrar pontos (%s)", fn.__name__)
            db.rollback()
            return None
    return wrapper


def _award(db: Session, *, user_id: uuid.UUID, kind: str, day: date) -> bool:
    """Dá os pontos de `kind` para `day` se ainda não deu. Devolve True se ganhou agora."""
    now = today()
    if day > now or day < now - timedelta(days=BACKDATE_DAYS):
        return False
    already = db.scalar(
        select(PointEvent.id).where(PointEvent.user_id == user_id, PointEvent.kind == kind, PointEvent.day == day)
    )
    if already is not None:
        return False
    db.add(PointEvent(user_id=user_id, kind=kind, day=day, points=POINTS[kind]))
    try:
        db.commit()
    except IntegrityError:  # outra requisição ganhou no mesmo instante: a trava do banco vale
        db.rollback()
        return False
    return True


# ------------------------------------------------------------------ gatilhos

@_safe
def record_access(db: Session, user_id: uuid.UUID) -> bool:
    return _award(db, user_id=user_id, kind="login", day=today())


def water_goal_liters(db: Session, project_id: uuid.UUID) -> float:
    goal = db.scalars(
        select(Goal).where(Goal.project_id == project_id, Goal.type == GoalType.WATER)
        .order_by(Goal.created_at.desc())
    ).first()
    return goal.target_value if goal and goal.target_value > 0 else DEFAULT_WATER_GOAL_L


@_safe
def on_checkin(db: Session, user_id: uuid.UUID, checkin: DailyCheckin) -> None:
    if checkin.water_liters is not None and checkin.water_liters >= water_goal_liters(db, checkin.project_id):
        _award(db, user_id=user_id, kind="water", day=checkin.date)
    if checkin.trained_today:
        _award(db, user_id=user_id, kind="workout", day=checkin.date)


@_safe
def on_session(db: Session, user_id: uuid.UUID, session_date: date) -> None:
    _award(db, user_id=user_id, kind="workout", day=session_date)


# ------------------------------------------------------------------ níveis

def level_info(total: int) -> dict:
    """Nível = floor(sqrt(total/50)) + 1  ->  níveis em 0, 50, 200, 450, 800, 1250... pontos."""
    level = int(math.sqrt(total / 50)) + 1
    start, nxt = 50 * (level - 1) ** 2, 50 * level ** 2
    return {
        "level": level,
        "level_title": LEVEL_TITLES[min(level, len(LEVEL_TITLES)) - 1],
        "points_in_level": total - start,
        "level_size": nxt - start,
        "points_to_next": nxt - total,
    }


# ------------------------------------------------------------------ resumo

def get_summary(db: Session, user_id: uuid.UUID) -> dict:
    now = today()
    total = db.scalar(select(func.coalesce(func.sum(PointEvent.points), 0)).where(PointEvent.user_id == user_id)) or 0

    week_start = now - timedelta(days=6)
    events = db.scalars(
        select(PointEvent).where(PointEvent.user_id == user_id, PointEvent.day >= week_start)
        .order_by(PointEvent.day.desc(), PointEvent.created_at.desc())
    ).all()
    by_day: dict[date, int] = {}
    for e in events:
        by_day[e.day] = by_day.get(e.day, 0) + e.points
    done_today = {e.kind for e in events if e.day == now}

    project = db.scalars(
        select(Project).where(Project.user_id == user_id, Project.status == ProjectStatus.ACTIVE)
        .order_by(Project.created_at.desc())
    ).first()
    liters_today = goal_liters = None
    if project is not None:
        goal_liters = water_goal_liters(db, project.id)
        checkin = db.scalars(
            select(DailyCheckin).where(DailyCheckin.project_id == project.id, DailyCheckin.date == now)
        ).first()
        liters_today = checkin.water_liters if checkin else None

    recent = db.scalars(
        select(PointEvent).where(PointEvent.user_id == user_id)
        .order_by(PointEvent.day.desc(), PointEvent.created_at.desc()).limit(15)
    ).all()

    return {
        "total_points": total,
        **level_info(total),
        "points_today": by_day.get(now, 0),
        "today": {
            "date": now,
            "login": {"done": "login" in done_today, "points": POINTS["login"]},
            "water": {"done": "water" in done_today, "points": POINTS["water"],
                      "liters": liters_today, "goal_liters": goal_liters},
            "workout": {"done": "workout" in done_today, "points": POINTS["workout"]},
        },
        "last_7_days": [
            {"day": d, "points": by_day.get(d, 0)}
            for d in (week_start + timedelta(days=i) for i in range(7))
        ],
        "recent": [{"kind": e.kind, "day": e.day, "points": e.points} for e in recent],
        "rules": POINTS,
    }
