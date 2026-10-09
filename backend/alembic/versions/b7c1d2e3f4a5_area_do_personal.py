"""area do personal: users.role, workouts.created_by_trainer_id, trainer_student_links

Revision ID: b7c1d2e3f4a5
Revises: e81eacaaf09c
Create Date: 2026-10-08 12:00:00.000000

Migração ADITIVA (só adiciona coisas; não altera nem apaga dados existentes):
- users.role: NOT NULL com server_default 'student' -> todo usuário atual vira aluno.
- workouts.created_by_trainer_id: nullable -> treinos atuais ficam como estão.
- trainer_student_links: tabela nova.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7c1d2e3f4a5"
down_revision: Union[str, None] = "e81eacaaf09c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=20), server_default="student", nullable=False))

    op.add_column("workouts", sa.Column("created_by_trainer_id", sa.Uuid(), nullable=True))
    op.create_index(op.f("ix_workouts_created_by_trainer_id"), "workouts", ["created_by_trainer_id"], unique=False)
    op.create_foreign_key(
        "fk_workouts_created_by_trainer_id_users",
        "workouts", "users", ["created_by_trainer_id"], ["id"], ondelete="SET NULL",
    )

    op.create_table(
        "trainer_student_links",
        sa.Column("trainer_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=True),
        sa.Column("student_label", sa.String(length=120), nullable=True),
        sa.Column("invite_code", sa.String(length=16), nullable=False),
        sa.Column("invite_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("share_photos", sa.Boolean(), nullable=False),
        sa.Column("share_progress", sa.Boolean(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trainer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trainer_student_links_trainer_id"), "trainer_student_links", ["trainer_id"], unique=False)
    op.create_index(op.f("ix_trainer_student_links_student_id"), "trainer_student_links", ["student_id"], unique=False)
    op.create_index(op.f("ix_trainer_student_links_invite_code"), "trainer_student_links", ["invite_code"], unique=True)
    op.create_index(op.f("ix_trainer_student_links_status"), "trainer_student_links", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trainer_student_links_status"), table_name="trainer_student_links")
    op.drop_index(op.f("ix_trainer_student_links_invite_code"), table_name="trainer_student_links")
    op.drop_index(op.f("ix_trainer_student_links_student_id"), table_name="trainer_student_links")
    op.drop_index(op.f("ix_trainer_student_links_trainer_id"), table_name="trainer_student_links")
    op.drop_table("trainer_student_links")

    op.drop_constraint("fk_workouts_created_by_trainer_id_users", "workouts", type_="foreignkey")
    op.drop_index(op.f("ix_workouts_created_by_trainer_id"), table_name="workouts")
    op.drop_column("workouts", "created_by_trainer_id")

    op.drop_column("users", "role")
