"""
Geração de PDF do relatório semanal, usando reportlab. Deliberadamente
simples (uma tabela) — a Etapa 14 pode evoluir o layout depois; o que
importa aqui é o usuário conseguir baixar e guardar o relatório.
"""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.report import WeeklyReport

_LABELS = {
    "days_registered": "Dias registrados",
    "weight_start_kg": "Peso inicial (kg)",
    "weight_end_kg": "Peso final (kg)",
    "weight_variation_kg": "Variação de peso (kg)",
    "waist_start_cm": "Cintura inicial (cm)",
    "waist_end_cm": "Cintura final (cm)",
    "waist_variation_cm": "Variação de cintura (cm)",
    "workouts_count": "Treinos realizados",
    "avg_water_liters": "Água média (L/dia)",
    "avg_sleep_hours": "Sono médio (h/noite)",
    "avg_steps": "Passos médios/dia",
    "diet_adherence_pct": "Adesão alimentar (%)",
}


def render_weekly_report_pdf(report: WeeklyReport, project_name: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=f"Relatório semanal — {project_name}")
    styles = getSampleStyleSheet()
    summary = report.summary

    elements = [
        Paragraph(f"{project_name}", styles["Title"]),
        Paragraph(f"Relatório da Semana {report.week_number}", styles["Heading2"]),
        Paragraph(f"{report.start_date.isoformat()} a {report.end_date.isoformat()}", styles["Normal"]),
        Spacer(1, 16),
    ]

    rows = [["Métrica", "Valor"]]
    for key, label in _LABELS.items():
        value = summary.get(key)
        rows.append([label, "—" if value is None else str(value)])

    table = Table(rows, colWidths=[260, 180])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2233")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F4F8")]),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 24))
    elements.append(
        Paragraph(
            "Este relatório apenas registra e apresenta a evolução dos dados inseridos pelo "
            "usuário. Não constitui diagnóstico médico, nutricional ou de treinamento, e não "
            "substitui acompanhamento profissional.",
            styles["Italic"],
        )
    )

    doc.build(elements)
    return buffer.getvalue()
