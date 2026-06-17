"""Cria tabela notificacoes

Revision ID: 7b9c4d2e1a6f
Revises: dce522dbdfd4
Create Date: 2026-06-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b9c4d2e1a6f"
down_revision: Union[str, None] = "dce522dbdfd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notificacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("tipo", sa.String(), nullable=False, server_default="geral"),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("lida", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notificacoes_id"), "notificacoes", ["id"], unique=False)
    op.create_index(op.f("ix_notificacoes_usuario_id"), "notificacoes", ["usuario_id"], unique=False)
    op.create_index(op.f("ix_notificacoes_created_at"), "notificacoes", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notificacoes_created_at"), table_name="notificacoes")
    op.drop_index(op.f("ix_notificacoes_usuario_id"), table_name="notificacoes")
    op.drop_index(op.f("ix_notificacoes_id"), table_name="notificacoes")
    op.drop_table("notificacoes")
