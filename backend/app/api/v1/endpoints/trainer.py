"""Área do personal. Prefixo: /trainer. Todas as rotas exigem papel "trainer"."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_trainer
from app.db.session import get_db
from app.models.trainer_link import TrainerStudentLink
from app.models.user import User
from app.schemas.photo import PhotoRead
from app.schemas.trainer import (
    InviteCreate,
    InviteRead,
    StudentProgress,
    StudentSummary,
    TrainerWorkoutIn,
    TrainerWorkoutRead,
)
from app.services import storage_service, trainer_service
from app.services.trainer_service import (
    ExerciseHasHistoryError,
    ExerciseNotInWorkoutError,
    LinkNotFoundError,
    PermissionNotGrantedError,
    StudentHasNoProjectError,
    WorkoutNotFoundError,
)

router = APIRouter()


def get_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db),
    trainer: User = Depends(require_trainer),
) -> TrainerStudentLink:
    """Porta de entrada de TODA rota por aluno: só passa com vínculo ativo deste personal."""
    try:
        return trainer_service.get_active_link(db, trainer_id=trainer.id, link_id=link_id)
    except LinkNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")


def _forbidden(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, detail)


# ---------------- alunos ----------------

@router.post("/invites", response_model=InviteRead, status_code=status.HTTP_201_CREATED)
def create_invite(
    payload: InviteCreate, db: Session = Depends(get_db), trainer: User = Depends(require_trainer)
) -> InviteRead:
    link = trainer_service.create_invite(db, trainer_id=trainer.id, student_label=payload.student_label)
    return InviteRead(
        link_id=link.id, invite_code=link.invite_code,
        invite_expires_at=link.invite_expires_at, student_label=link.student_label,
    )


@router.get("/students", response_model=list[StudentSummary])
def list_students(db: Session = Depends(get_db), trainer: User = Depends(require_trainer)) -> list[dict]:
    return trainer_service.list_student_links(db, trainer_id=trainer.id)


@router.delete("/students/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_student(
    link_id: uuid.UUID, db: Session = Depends(get_db), trainer: User = Depends(require_trainer)
) -> None:
    """Encerra o vínculo (ou cancela um convite pendente). Os treinos já montados ficam com o aluno."""
    try:
        trainer_service.end_link_as_trainer(db, trainer_id=trainer.id, link_id=link_id)
    except LinkNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")


# ---------------- treinos do aluno ----------------

@router.get("/students/{link_id}/workouts", response_model=list[TrainerWorkoutRead])
def list_workouts(link: TrainerStudentLink = Depends(get_link), db: Session = Depends(get_db)):
    return trainer_service.list_workouts(db, link=link)


@router.post("/students/{link_id}/workouts", response_model=TrainerWorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(
    payload: TrainerWorkoutIn, link: TrainerStudentLink = Depends(get_link), db: Session = Depends(get_db)
):
    try:
        return trainer_service.create_workout(db, link=link, data=payload.model_dump())
    except StudentHasNoProjectError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Este aluno ainda não tem um projeto ativo. Peça para ele concluir o início no app.",
        )


@router.put("/students/{link_id}/workouts/{workout_id}", response_model=TrainerWorkoutRead)
def update_workout(
    workout_id: uuid.UUID, payload: TrainerWorkoutIn,
    link: TrainerStudentLink = Depends(get_link), db: Session = Depends(get_db),
):
    try:
        return trainer_service.update_workout(db, link=link, workout_id=workout_id, data=payload.model_dump())
    except WorkoutNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Treino não encontrado (ou não foi montado por você).")
    except ExerciseNotInWorkoutError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Exercício não pertence a este treino.")
    except ExerciseHasHistoryError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f'O aluno já registrou séries em "{exc.exercise_name}". Mantenha o exercício ou crie um treino novo.',
        )


@router.delete("/students/{link_id}/workouts/{workout_id}")
def delete_workout(
    workout_id: uuid.UUID, link: TrainerStudentLink = Depends(get_link), db: Session = Depends(get_db)
) -> dict:
    try:
        outcome = trainer_service.delete_workout(db, link=link, workout_id=workout_id)
    except WorkoutNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Treino não encontrado (ou não foi montado por você).")
    return {"result": outcome}  # "deleted" ou "archived" (quando o aluno já tem histórico nele)


# ---------------- evolução e fotos (dependem do consentimento do aluno) ----------------

@router.get("/students/{link_id}/progress", response_model=StudentProgress)
def get_progress(link: TrainerStudentLink = Depends(get_link), db: Session = Depends(get_db)) -> dict:
    try:
        return trainer_service.get_progress(db, link=link)
    except PermissionNotGrantedError:
        raise _forbidden("O aluno não compartilhou a evolução com você.")


@router.get("/students/{link_id}/photos", response_model=list[PhotoRead])
def list_photos(link: TrainerStudentLink = Depends(get_link), db: Session = Depends(get_db)):
    try:
        return list(trainer_service.list_photos(db, link=link))
    except PermissionNotGrantedError:
        raise _forbidden("O aluno não compartilhou as fotos com você.")


@router.get("/students/{link_id}/photos/{photo_id}/file")
def get_photo_file(
    photo_id: uuid.UUID, link: TrainerStudentLink = Depends(get_link), db: Session = Depends(get_db)
) -> Response:
    try:
        photo = trainer_service.get_photo(db, link=link, photo_id=photo_id)
        content = storage_service.read_photo(photo.file_path)
    except PermissionNotGrantedError:
        raise _forbidden("O aluno não compartilhou as fotos com você.")
    except (LinkNotFoundError, FileNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto não encontrada.")
    response = Response(content=content, media_type=storage_service.content_type_for(photo.file_path))
    response.headers["Cache-Control"] = "private, no-store"  # foto sensível: nada de cache compartilhado
    return response
