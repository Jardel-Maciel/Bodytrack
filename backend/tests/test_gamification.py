"""Gamificação: login/acesso, meta de água, treino, trava anti-duplicidade, janela de datas e níveis."""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.goal import Goal, GoalType
from app.models.point_event import PointEvent
from app.services import gamification_service as gam

API = "/api/v1"
HOJE = date(2026, 10, 9)


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    """Congela o 'hoje' do app para os testes não dependerem do relógio."""
    state = {"day": HOJE}
    monkeypatch.setattr(gam, "today", lambda: state["day"])
    return state


@pytest.fixture()
def ctx(client, make_user, make_project, auth_headers):
    user = make_user()
    project = make_project(user)
    return user, project, auth_headers(user)


def _summary(client, headers):
    return client.get(f"{API}/gamification/summary", headers=headers).json()


def _checkin(client, project, headers, day=HOJE, **fields):
    payload = {"project_id": str(project.id), "date": day.isoformat(), **fields}
    r = client.post(f"{API}/projects/{project.id}/checkins", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def _session(client, project, headers, day=HOJE):
    w = client.post(
        f"{API}/projects/{project.id}/workouts", json={"name": "A", "exercises": [{"name": "Supino reto"}]}, headers=headers
    ).json()
    r = client.post(
        f"{API}/projects/{project.id}/workouts/{w['id']}/sessions",
        json={"date": day.isoformat(), "sets": [{"workout_exercise_id": w["exercises"][0]["id"], "set_number": 1, "reps": 8, "load_kg": 40}]},
        headers=headers,
    )
    assert r.status_code == 201, r.text


# ------------------------------------------------------------------ acesso / login

def test_login_gives_points_once_per_day(client, make_user, fixed_today):
    make_user()
    creds = {"email": "user@example.com", "password": "senha12345"}
    for _ in range(3):  # entrar e sair várias vezes no mesmo dia
        token = client.post(f"{API}/auth/login", json=creds).json()["access_token"]
    s = _summary(client, {"Authorization": f"Bearer {token}"})
    assert s["total_points"] == 5 and s["today"]["login"]["done"] is True

    fixed_today["day"] = HOJE + timedelta(days=1)  # virou o dia
    token = client.post(f"{API}/auth/login", json=creds).json()["access_token"]
    assert _summary(client, {"Authorization": f"Bearer {token}"})["total_points"] == 10


def test_opening_the_app_while_logged_in_counts_as_the_days_access(client, ctx):
    _user, _project, h = ctx  # nunca fez login: só tem o token (como um PWA que ficou logado)
    assert client.get(f"{API}/auth/me", headers=h).status_code == 200
    client.get(f"{API}/auth/me", headers=h)
    assert _summary(client, h)["total_points"] == 5


# ------------------------------------------------------------------ água

def test_water_goal_default_and_custom_goal(client, ctx, db_session):
    _user, project, h = ctx
    _checkin(client, project, h, water_liters=2.0)
    assert _summary(client, h)["today"]["water"]["done"] is False  # padrão: 2,5 L

    _checkin(client, project, h, water_liters=2.5)
    s = _summary(client, h)
    assert s["today"]["water"]["done"] is True and s["today"]["water"]["goal_liters"] == 2.5

    _checkin(client, project, h, water_liters=4.0)  # editar de novo não pontua em dobro
    assert _summary(client, h)["points_today"] == 10

    db_session.add(Goal(project_id=project.id, type=GoalType.WATER, target_value=3.5))
    db_session.commit()
    s = _summary(client, h)
    assert s["today"]["water"]["goal_liters"] == 3.5


def test_custom_water_goal_is_respected(client, ctx, db_session):
    _user, project, h = ctx
    db_session.add(Goal(project_id=project.id, type=GoalType.WATER, target_value=3.0))
    db_session.commit()
    _checkin(client, project, h, water_liters=2.8)
    assert _summary(client, h)["today"]["water"]["done"] is False
    _checkin(client, project, h, water_liters=3.0)
    assert _summary(client, h)["today"]["water"]["done"] is True


# ------------------------------------------------------------------ treino

def test_workout_points_from_session_or_checkin_only_once_a_day(client, ctx):
    _user, project, h = ctx
    _session(client, project, h)
    assert _summary(client, h)["today"]["workout"]["done"] is True
    _checkin(client, project, h, trained_today=True)   # mesmo dia, outra origem
    _session(client, project, h)                        # segunda sessão
    s = _summary(client, h)
    assert s["points_today"] == 15 and len(s["recent"]) == 1


def test_workout_points_from_checkin_trained_today(client, ctx):
    _user, project, h = ctx
    _checkin(client, project, h, trained_today=False)
    assert _summary(client, h)["today"]["workout"]["done"] is False
    _checkin(client, project, h, trained_today=True)
    assert _summary(client, h)["total_points"] == 15


def test_full_day_adds_up(client, ctx):
    _user, project, h = ctx
    client.get(f"{API}/auth/me", headers=h)
    _checkin(client, project, h, water_liters=3.0, trained_today=True)
    s = _summary(client, h)
    assert s["total_points"] == s["points_today"] == 5 + 10 + 15
    assert [d["points"] for d in s["last_7_days"]] == [0, 0, 0, 0, 0, 0, 30]
    assert s["last_7_days"][-1]["day"] == HOJE.isoformat()


# ------------------------------------------------------------------ janela de datas

def test_only_recent_days_score(client, ctx):
    _user, project, h = ctx
    _checkin(client, project, h, day=HOJE - timedelta(days=8), trained_today=True)   # velho demais
    assert _summary(client, h)["total_points"] == 0
    _checkin(client, project, h, day=HOJE - timedelta(days=7), trained_today=True)   # limite da janela
    assert _summary(client, h)["total_points"] == 15
    _checkin(client, project, h, day=HOJE + timedelta(days=1), trained_today=True)   # futuro
    assert _summary(client, h)["total_points"] == 15


def test_offline_checkin_synced_days_later_still_scores_for_its_own_day(client, ctx):
    _user, project, h = ctx
    _checkin(client, project, h, day=HOJE - timedelta(days=3), water_liters=3.0)
    s = _summary(client, h)
    assert s["total_points"] == 10 and s["points_today"] == 0  # pontos caem no dia certo, não em hoje
    assert s["recent"][0]["day"] == (HOJE - timedelta(days=3)).isoformat()


# ------------------------------------------------------------------ robustez

def test_database_blocks_duplicate_events(client, ctx, db_session):
    user, _project, _h = ctx
    assert gam._award(db_session, user_id=user.id, kind="login", day=HOJE) is True
    assert gam._award(db_session, user_id=user.id, kind="login", day=HOJE) is False
    db_session.add(PointEvent(user_id=user.id, kind="login", day=HOJE, points=5))  # burlando o "if"
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_gamification_failure_never_breaks_the_checkin(client, ctx, monkeypatch):
    _user, project, h = ctx

    def boom(*a, **k):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(gam, "_award", boom)
    _checkin(client, project, h, water_liters=3.0, trained_today=True)  # continua 201
    assert client.get(f"{API}/auth/me", headers=h).status_code == 200   # e abrir o app também
    assert len(client.get(f"{API}/projects/{project.id}/checkins", headers=h).json()) == 1


def test_users_do_not_see_each_others_points(client, ctx, make_user, auth_headers):
    _user, project, h = ctx
    _checkin(client, project, h, trained_today=True)
    other = auth_headers(make_user(email="outro@x.com"))
    assert _summary(client, other)["total_points"] == 0
    assert client.get(f"{API}/gamification/summary").status_code == 401


def test_summary_for_brand_new_user_without_project(client, make_user, auth_headers):
    s = _summary(client, auth_headers(make_user()))
    assert s["total_points"] == 0 and s["level"] == 1 and s["level_title"] == "Iniciante"
    assert s["today"]["water"]["goal_liters"] is None and s["rules"] == {"login": 5, "water": 10, "workout": 15}


# ------------------------------------------------------------------ níveis e fuso

@pytest.mark.parametrize(
    "total, level, to_next",
    [(0, 1, 50), (49, 1, 1), (50, 2, 150), (199, 2, 1), (200, 3, 250), (450, 4, 350), (4050, 10, 950)],
)
def test_level_thresholds(total, level, to_next):
    info = gam.level_info(total)
    assert info["level"] == level and info["points_to_next"] == to_next
    assert info["points_in_level"] + info["points_to_next"] == info["level_size"]


def test_level_titles_cap_at_the_last_one():
    assert gam.level_info(10**6)["level_title"] == "Lenda"
    assert gam.level_info(0)["level_title"] == "Iniciante"


def test_real_today_uses_the_app_timezone(monkeypatch):
    monkeypatch.undo()  # volta a função real (o autouse trocou por uma fixa)
    assert gam.today() == datetime.now(ZoneInfo("America/Sao_Paulo")).date()
