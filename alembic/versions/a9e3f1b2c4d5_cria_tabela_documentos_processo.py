"""cria tabela documentos_processo

Revision ID: a9e3f1b2c4d5
Revises: 8a1c4d7e9b20
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a9e3f1b2c4d5"
down_revision: Union[str, None] = "8a1c4d7e9b20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documentos_processo",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("processo_id", sa.Integer(), sa.ForeignKey("processos.id"), nullable=False, index=True),
        sa.Column("nome_original", sa.String(), nullable=False),
        sa.Column("nome_salvo", sa.String(), nullable=False),
        sa.Column("tamanho", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("documentos_processo")
