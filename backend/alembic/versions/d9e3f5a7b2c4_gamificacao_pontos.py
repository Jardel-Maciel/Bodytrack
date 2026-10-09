"""gamificação: point_events

Revision ID: d9e3f5a7b2c4
Revises: c8d2e4f6a1b3
Create Date: 2026-10-09 18:00:00.000000

Migração ADITIVA: só cria a tabela de pontos. Ninguém ganha pontos retroativos.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d9e3f5a7b2c4"
down_revision: Union[str, None] = "c8d2e4f6a1b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "point_events",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "kind", "day", name="uq_point_event_user_kind_day"),
    )
    op.create_index(op.f("ix_point_events_user_id"), "point_events", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_point_events_user_id"), table_name="point_events")
    op.drop_table("point_events")
