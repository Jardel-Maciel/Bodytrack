"""
Importa TODOS os modelos em um único lugar.

O Alembic (migrations) inspeciona `Base.metadata` para gerar as
migrations automaticamente — se um modelo novo não for importado aqui,
o autogenerate do Alembic simplesmente não o vê. Este módulo não é
usado pela aplicação em si, apenas pelo Alembic (`env.py` importa
`app.db.base`).
"""
from app.db.base_class import Base  # noqa: F401

from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.checkin import DailyCheckin  # noqa: F401
from app.models.measurement import BodyMeasurement  # noqa: F401
from app.models.photo import ProgressPhoto  # noqa: F401
from app.models.workout import (  # noqa: F401
    Workout,
    WorkoutExercise,
    WorkoutSession,
    ExerciseSet,
)
from app.models.goal import Goal  # noqa: F401
from app.models.achievement import Achievement  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.report import WeeklyReport  # noqa: F401
