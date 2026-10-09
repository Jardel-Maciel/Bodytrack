"""avisos (app_notices) e chat personal/aluno (trainer_messages)

Revision ID: c8d2e4f6a1b3
Revises: b7c1d2e3f4a5
Create Date: 2026-10-09 12:00:00.000000

Migração ADITIVA: só cria duas tabelas novas.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c8d2e4f6a1b3"
down_revision: Union[str, None] = "b7c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_now = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "app_notices",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.String(length=400), nullable=True),
        sa.Column("link_path", sa.String(length=200), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_now, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_now, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_app_notices_user_id"), "app_notices", ["user_id"], unique=False)

    op.create_table(
        "trainer_messages",
        sa.Column("link_id", sa.Uuid(), nullable=False),
        sa.Column("sender_id", sa.Uuid(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_now, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_now, nullable=False),
        sa.ForeignKeyConstraint(["link_id"], ["trainer_student_links.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trainer_messages_link_id"), "trainer_messages", ["link_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trainer_messages_link_id"), table_name="trainer_messages")
    op.drop_table("trainer_messages")
    op.drop_index(op.f("ix_app_notices_user_id"), table_name="app_notices")
    op.drop_table("app_notices")
