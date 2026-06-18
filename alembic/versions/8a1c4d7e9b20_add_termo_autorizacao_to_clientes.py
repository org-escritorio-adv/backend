"""add termo autorizacao to clientes

Revision ID: 8a1c4d7e9b20
Revises: 7b9c4d2e1a6f
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op


revision: str = "8a1c4d7e9b20"
down_revision: Union[str, None] = "7b9c4d2e1a6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE clientes "
        "ADD COLUMN IF NOT EXISTS termo_autorizacao_arquivo VARCHAR"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE clientes DROP COLUMN IF EXISTS termo_autorizacao_arquivo")
