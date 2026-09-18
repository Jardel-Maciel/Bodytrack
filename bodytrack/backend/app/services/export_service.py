"""
Exportação de dados brutos (Etapa 30 do briefing: "o usuário deve
conseguir exportar seu histórico" em CSV/JSON). Formato de saída do CSV
é "longo" (uma linha por campo) de propósito: check-ins e medidas têm
colunas diferentes, e um único arquivo em formato longo evita ter que
gerar dois CSVs (ou lidar com colunas vazias) para representar os dois.
"""
import csv
import io
import json
import uuid
from typing import Literal

from sqlalchemy.orm import Session

from app.models.checkin import DailyCheckin
from app.models.measurement import BodyMeasurement
from app.repositories import checkin_repository, measurement_repository
from app.services.project_service import get_project_or_404

_CHECKIN_FIELDS = (
    "weight_kg",
    "water_liters",
    "sleep_hours",
    "sleep_quality",
    "steps",
    "trained_today",
    "energy_level",
    "mood_level",
    "followed_diet",
    "hit_protein_goal",
    "avoided_ultraprocessed",
    "portion_control",
    "notes",
)

_MEASUREMENT_FIELDS = (
    "weight_kg",
    "neck_cm",
    "shoulders_cm",
    "chest_cm",
    "arm_right_cm",
    "arm_left_cm",
    "waist_cm",
    "abdomen_cm",
    "hip_cm",
    "thigh_right_cm",
    "thigh_left_cm",
    "calf_right_cm",
    "calf_left_cm",
)


def _checkin_dict(c: DailyCheckin) -> dict:
    return {"date": c.date.isoformat(), **{f: getattr(c, f) for f in _CHECKIN_FIELDS}}


def _measurement_dict(m: BodyMeasurement) -> dict:
    return {"date": m.date.isoformat(), **{f: getattr(m, f) for f in _MEASUREMENT_FIELDS}}


def export_project_data(
    db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID, fmt: Literal["csv", "json"]
) -> tuple[bytes, str, str]:
    project = get_project_or_404(db, project_id=project_id, user_id=user_id)
    checkins = [_checkin_dict(c) for c in checkin_repository.list_for_project(db, project_id=project_id)]
    measurements = [
        _measurement_dict(m) for m in measurement_repository.list_for_project(db, project_id=project_id)
    ]

    if fmt == "json":
        payload = {"project": project.name, "checkins": checkins, "measurements": measurements}
        content = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        return content, "application/json", "bodytrack_export.json"

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["tipo", "data", "campo", "valor"])
    for row in checkins:
        date_value = row["date"]
        for field, value in row.items():
            if field != "date":
                writer.writerow(["checkin", date_value, field, value])
    for row in measurements:
        date_value = row["date"]
        for field, value in row.items():
            if field != "date":
                writer.writerow(["measurement", date_value, field, value])

    return buffer.getvalue().encode("utf-8"), "text/csv", "bodytrack_export.csv"
