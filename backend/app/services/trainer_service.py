"""
Regras da área do personal.

Princípio central: o personal NUNCA acessa dados de um aluno "por ID do aluno".
Toda operação começa em `get_active_link(trainer_id, link_id)`, que só devolve
um vínculo se (a) pertence a este personal e (b) está ATIVO. Dali em diante,
quem decide o que ele pode ver são as permissões dadas pelo aluno
(`share_photos`, `share_progress`). Sem vínculo/permissão -> erro -> 404/403.
"""
import secrets
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.checkin import DailyCheckin
from app.models.measurement import BodyMeasurement
from app.models.photo import ProgressPhoto
from app.models.project import Project, ProjectStatus
from app.models.trainer_link import LINK_ACTIVE, LINK_PENDING, LINK_REVOKED, TrainerStudentLink
from app.models.user import User
from app.models.workout import Workout, WorkoutExercise, WorkoutSession
from app.services.notification_service import notify

INVITE_TTL_DAYS = 14
# Sem 0/O/1/I/L: o aluno digita o código à mão, então evitamos caracteres que se confundem.
_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


class LinkNotFoundError(Exception): ...
class InviteInvalidError(Exception): ...
class InviteOwnError(Exception): ...
class AlreadyLinkedError(Exception): ...
class PermissionNotGrantedError(Exception): ...
class StudentHasNoProjectError(Exception): ...
class WorkoutNotFoundError(Exception): ...
class ExerciseNotInWorkoutError(Exception): ...
class ExerciseHasHistoryError(Exception):
    def __init__(self, exercise_name: str):
        super().__init__(exercise_name)
        self.exercise_name = exercise_name


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _name(db: Session, user_id: uuid.UUID) -> str:
    user = db.get(User, user_id)
    return user.name if user else "Alguém"


def _as_aware(value: datetime) -> datetime:
    # SQLite (testes) devolve datetime sem fuso; Postgres devolve com fuso.
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------- vínculos

def create_invite(db: Session, *, trainer_id: uuid.UUID, student_label: Optional[str]) -> TrainerStudentLink:
    link = TrainerStudentLink(
        trainer_id=trainer_id,
        student_label=(student_label or "").strip() or None,
        invite_code=_unique_code(db),
        invite_expires_at=_now() + timedelta(days=INVITE_TTL_DAYS),
        status=LINK_PENDING,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def _unique_code(db: Session) -> str:
    for _ in range(10):
        code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(8))
        if db.scalar(select(TrainerStudentLink.id).where(TrainerStudentLink.invite_code == code)) is None:
            return code
    raise RuntimeError("Não foi possível gerar um código de convite único.")


def accept_invite(
    db: Session, *, student: User, code: str, share_photos: bool, share_progress: bool
) -> TrainerStudentLink:
    normalized = "".join(ch for ch in code.upper() if ch.isalnum())
    link = db.scalar(select(TrainerStudentLink).where(TrainerStudentLink.invite_code == normalized))
    # Mesma resposta para "não existe", "já usado", "expirado" e "revogado": não ajuda quem tenta adivinhar.
    if (
        link is None
        or link.status != LINK_PENDING
        or _as_aware(link.invite_expires_at) < _now()
    ):
        raise InviteInvalidError()
    if link.trainer_id == student.id:
        raise InviteOwnError()

    already = db.scalar(
        select(TrainerStudentLink.id).where(
            TrainerStudentLink.trainer_id == link.trainer_id,
            TrainerStudentLink.student_id == student.id,
            TrainerStudentLink.status == LINK_ACTIVE,
        )
    )
    if already is not None:
        raise AlreadyLinkedError()

    link.student_id = student.id
    link.status = LINK_ACTIVE
    link.share_photos = share_photos
    link.share_progress = share_progress
    link.accepted_at = _now()
    notify(
        db, user_id=link.trainer_id, kind="link_accepted",
        title=f"{student.name} aceitou seu convite",
        body="Agora você já pode montar treinos para este aluno.", link_path=f"/alunos/{link.id}",
    )
    db.commit()
    db.refresh(link)
    return link


def get_active_link(db: Session, *, trainer_id: uuid.UUID, link_id: uuid.UUID) -> TrainerStudentLink:
    link = db.get(TrainerStudentLink, link_id)
    if link is None or link.trainer_id != trainer_id or link.status != LINK_ACTIVE or link.student_id is None:
        raise LinkNotFoundError()
    return link


def end_link_as_trainer(db: Session, *, trainer_id: uuid.UUID, link_id: uuid.UUID) -> None:
    link = db.get(TrainerStudentLink, link_id)
    if link is None or link.trainer_id != trainer_id or link.status == LINK_REVOKED:
        raise LinkNotFoundError()
    was_active = link.status == LINK_ACTIVE and link.student_id is not None
    link.status = LINK_REVOKED
    if was_active:
        notify(
            db, user_id=link.student_id, kind="link_ended",
            title=f"{_name(db, trainer_id)} encerrou o acompanhamento",
            body="Os treinos que ele montou continuam com você.", link_path="/perfil",
        )
    db.commit()


def list_student_links(db: Session, *, trainer_id: uuid.UUID) -> list[dict]:
    links = db.scalars(
        select(TrainerStudentLink)
        .where(TrainerStudentLink.trainer_id == trainer_id, TrainerStudentLink.status != LINK_REVOKED)
        .order_by(TrainerStudentLink.created_at)
    ).all()
    now = _now()
    rows = []
    for link in links:
        if link.status == LINK_PENDING and _as_aware(link.invite_expires_at) < now:
            continue  # convite vencido some da lista
        student = db.get(User, link.student_id) if link.student_id else None
        project = _student_project(db, link.student_id) if link.student_id else None
        last_session = photos_count = None
        if link.status == LINK_ACTIVE and project is not None:
            if link.share_progress:
                last_session = _last_session_date(db, project.id)
            if link.share_photos:
                photos_count = db.scalar(
                    select(func.count()).select_from(ProgressPhoto).join(Project)
                    .where(Project.user_id == link.student_id)
                ) or 0
        rows.append(
            {
                "link_id": link.id,
                "status": link.status,
                "display_name": student.name if student else (link.student_label or "Convite pendente"),
                "invite_code": link.invite_code if link.status == LINK_PENDING else None,
                "invite_expires_at": link.invite_expires_at if link.status == LINK_PENDING else None,
                "share_photos": link.share_photos,
                "share_progress": link.share_progress,
                "project_name": project.name if project else None,
                "last_session_date": last_session,
                "photos_count": photos_count,
            }
        )
    return rows


# ------- lado do aluno

def list_my_trainers(db: Session, *, student_id: uuid.UUID) -> list[dict]:
    links = db.scalars(
        select(TrainerStudentLink)
        .where(TrainerStudentLink.student_id == student_id, TrainerStudentLink.status == LINK_ACTIVE)
        .order_by(TrainerStudentLink.accepted_at)
    ).all()
    return [
        {
            "link_id": l.id,
            "trainer_name": db.get(User, l.trainer_id).name,
            "status": l.status,
            "share_photos": l.share_photos,
            "share_progress": l.share_progress,
            "accepted_at": l.accepted_at,
        }
        for l in links
    ]


def _get_my_link(db: Session, *, student_id: uuid.UUID, link_id: uuid.UUID) -> TrainerStudentLink:
    link = db.get(TrainerStudentLink, link_id)
    if link is None or link.student_id != student_id or link.status != LINK_ACTIVE:
        raise LinkNotFoundError()
    return link


def update_consent(
    db: Session, *, student_id: uuid.UUID, link_id: uuid.UUID,
    share_photos: Optional[bool], share_progress: Optional[bool],
) -> TrainerStudentLink:
    link = _get_my_link(db, student_id=student_id, link_id=link_id)
    before = (link.share_photos, link.share_progress)
    if share_photos is not None:
        link.share_photos = share_photos
    if share_progress is not None:
        link.share_progress = share_progress
    if before != (link.share_photos, link.share_progress):
        yes_no = lambda v: "sim" if v else "não"
        notify(
            db, user_id=link.trainer_id, kind="consent_changed",
            title=f"{_name(db, student_id)} atualizou o que compartilha com você",
            body=f"Fotos: {yes_no(link.share_photos)} · Evolução: {yes_no(link.share_progress)}",
            link_path=f"/alunos/{link.id}",
        )
    db.commit()
    db.refresh(link)
    return link


def end_link_as_student(db: Session, *, student_id: uuid.UUID, link_id: uuid.UUID) -> None:
    link = _get_my_link(db, student_id=student_id, link_id=link_id)
    link.status = LINK_REVOKED
    notify(
        db, user_id=link.trainer_id, kind="link_ended",
        title=f"{_name(db, student_id)} encerrou o acompanhamento", link_path="/alunos",
    )
    db.commit()


# ---------------------------------------------------------------- dados do aluno

def _student_project(db: Session, student_id: uuid.UUID) -> Optional[Project]:
    """Projeto em que o personal trabalha: o ativo mais recente do aluno."""
    return db.scalars(
        select(Project)
        .where(Project.user_id == student_id, Project.status == ProjectStatus.ACTIVE)
        .order_by(Project.created_at.desc())
    ).first()


def _last_session_date(db: Session, project_id: uuid.UUID) -> Optional[date]:
    return db.scalar(
        select(func.max(WorkoutSession.date)).join(Workout).where(Workout.project_id == project_id)
    )


def _require_project(db: Session, link: TrainerStudentLink) -> Project:
    project = _student_project(db, link.student_id)
    if project is None:
        raise StudentHasNoProjectError()
    return project


# ---------------------------------------------------------------- treinos

def _workout_view(workout: Workout, trainer_id: uuid.UUID) -> Workout:
    workout.editable = workout.created_by_trainer_id == trainer_id  # type: ignore[attr-defined]
    return workout


def list_workouts(db: Session, *, link: TrainerStudentLink) -> Sequence[Workout]:
    project = _student_project(db, link.student_id)
    if project is None:
        return []
    stmt = (
        select(Workout)
        .where(Workout.project_id == project.id, Workout.is_active.is_(True))
        .options(selectinload(Workout.exercises))
        .order_by(Workout.created_at)
    )
    workouts = db.scalars(stmt).all()
    # Treinos que o PRÓPRIO aluno criou só aparecem se ele compartilha a evolução.
    visible = [w for w in workouts if w.created_by_trainer_id == link.trainer_id or link.share_progress]
    return [_workout_view(w, link.trainer_id) for w in visible]


def _get_editable_workout(db: Session, *, link: TrainerStudentLink, workout_id: uuid.UUID) -> Workout:
    project = _student_project(db, link.student_id)
    workout = db.scalars(
        select(Workout)
        .where(Workout.id == workout_id, Workout.project_id == (project.id if project else None))
        .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
    ).first()
    # Só edita o que ELE montou: o treino que o aluno criou por conta própria não é mexido.
    if workout is None or workout.created_by_trainer_id != link.trainer_id:
        raise WorkoutNotFoundError()
    return workout


def create_workout(db: Session, *, link: TrainerStudentLink, data: dict) -> Workout:
    project = _require_project(db, link)
    exercises = data.pop("exercises", [])
    workout = Workout(
        project_id=project.id, created_by_trainer_id=link.trainer_id,
        name=data["name"], muscle_group=data.get("muscle_group"), notes=data.get("notes"),
    )
    for index, ex in enumerate(exercises):
        ex.pop("id", None)
        ex["order"] = index
        workout.exercises.append(WorkoutExercise(**ex))
    db.add(workout)
    notify(
        db, user_id=link.student_id, kind="workout_new",
        title=f"{_name(db, link.trainer_id)} montou um treino novo para você",
        body=workout.name, link_path="/treino",
    )
    db.commit()
    db.refresh(workout)
    return _workout_view(workout, link.trainer_id)


def update_workout(db: Session, *, link: TrainerStudentLink, workout_id: uuid.UUID, data: dict) -> Workout:
    workout = _get_editable_workout(db, link=link, workout_id=workout_id)
    incoming = data.pop("exercises", [])

    existing = {e.id: e for e in workout.exercises}
    incoming_ids = {ex["id"] for ex in incoming if ex.get("id")}
    if not incoming_ids <= existing.keys():
        raise ExerciseNotInWorkoutError()

    # Não apaga exercício que o aluno já executou: perderia o histórico de cargas dele.
    for ex_id, exercise in existing.items():
        if ex_id not in incoming_ids and exercise.sets:
            raise ExerciseHasHistoryError(exercise.name)
    for ex_id, exercise in existing.items():
        if ex_id not in incoming_ids:
            workout.exercises.remove(exercise)

    workout.name = data["name"]
    workout.muscle_group = data.get("muscle_group")
    workout.notes = data.get("notes")
    for index, ex in enumerate(incoming):
        ex_id = ex.pop("id", None)
        ex["order"] = index
        if ex_id:
            target = existing[ex_id]
            for field, value in ex.items():
                setattr(target, field, value)
        else:
            workout.exercises.append(WorkoutExercise(**ex))
    notify(
        db, user_id=link.student_id, kind="workout_updated",
        title=f"{_name(db, link.trainer_id)} atualizou o treino \"{workout.name}\"",
        body="Confira as mudanças antes do próximo treino.", link_path="/treino",
    )
    db.commit()
    db.refresh(workout)
    return _workout_view(workout, link.trainer_id)


def delete_workout(db: Session, *, link: TrainerStudentLink, workout_id: uuid.UUID) -> str:
    """Devolve "deleted" ou "archived". Com sessões registradas, só arquiva (preserva o histórico do aluno)."""
    workout = _get_editable_workout(db, link=link, workout_id=workout_id)
    has_history = db.scalar(
        select(func.count()).select_from(WorkoutSession).where(WorkoutSession.workout_id == workout.id)
    )
    notify(
        db, user_id=link.student_id, kind="workout_removed",
        title=f"{_name(db, link.trainer_id)} removeu o treino \"{workout.name}\"", link_path="/treino",
    )
    if has_history:
        workout.is_active = False
        db.commit()
        return "archived"
    db.delete(workout)
    db.commit()
    return "deleted"


# ---------------------------------------------------------------- evolução e fotos

def _require(link: TrainerStudentLink, *, photos: bool = False, progress: bool = False) -> None:
    if (photos and not link.share_photos) or (progress and not link.share_progress):
        raise PermissionNotGrantedError()


def get_progress(db: Session, *, link: TrainerStudentLink) -> dict:
    _require(link, progress=True)
    project = _student_project(db, link.student_id)
    if project is None:
        return {
            "project_name": None, "initial_weight_kg": None, "weights": [],
            "latest_measurement_date": None, "latest_waist_cm": None,
            "sessions_last_30_days": 0, "recent_sessions": [],
        }

    weights = db.execute(
        select(DailyCheckin.date, DailyCheckin.weight_kg)
        .where(DailyCheckin.project_id == project.id, DailyCheckin.weight_kg.is_not(None))
        .order_by(DailyCheckin.date.desc()).limit(60)
    ).all()
    measurement = db.scalars(
        select(BodyMeasurement).where(BodyMeasurement.project_id == project.id)
        .order_by(BodyMeasurement.date.desc())
    ).first()

    sessions = db.scalars(
        select(WorkoutSession).join(Workout)
        .where(Workout.project_id == project.id)
        .options(selectinload(WorkoutSession.sets), selectinload(WorkoutSession.workout))
        .order_by(WorkoutSession.date.desc(), WorkoutSession.created_at.desc()).limit(15)
    ).all()
    since = date.today() - timedelta(days=30)
    last_30 = db.scalar(
        select(func.count()).select_from(WorkoutSession).join(Workout)
        .where(Workout.project_id == project.id, WorkoutSession.date >= since)
    ) or 0

    return {
        "project_name": project.name,
        "initial_weight_kg": project.initial_weight_kg,
        "weights": [{"date": d, "weight_kg": w} for d, w in reversed(weights)],
        "latest_measurement_date": measurement.date if measurement else None,
        "latest_waist_cm": measurement.waist_cm if measurement else None,
        "sessions_last_30_days": last_30,
        "recent_sessions": [
            {
                "session_id": s.id, "date": s.date, "workout_name": s.workout.name,
                "sets_count": len(s.sets), "total_volume_kg": s.total_volume_kg,
            }
            for s in sessions
        ],
    }


def list_photos(db: Session, *, link: TrainerStudentLink) -> Sequence[ProgressPhoto]:
    _require(link, photos=True)
    return db.scalars(
        select(ProgressPhoto).join(Project)
        .where(Project.user_id == link.student_id)
        .order_by(ProgressPhoto.date, ProgressPhoto.created_at)
    ).all()


def get_photo(db: Session, *, link: TrainerStudentLink, photo_id: uuid.UUID) -> ProgressPhoto:
    _require(link, photos=True)
    photo = db.scalars(
        select(ProgressPhoto).join(Project)
        .where(ProgressPhoto.id == photo_id, Project.user_id == link.student_id)
    ).first()
    if photo is None:
        raise LinkNotFoundError()
    return photo
