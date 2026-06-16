"""add autorizacao_busca to clientes

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-15

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS garante que a migration é idempotente:
    # no banco existente adiciona as colunas; num banco fresh criado pelo 0001
    # elas já existem e o comando vira no-op.
    op.execute("""
        ALTER TABLE clientes
            ADD COLUMN IF NOT EXISTS autorizacao_busca      BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS data_autorizacao_busca TIMESTAMP;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE clientes DROP COLUMN IF EXISTS data_autorizacao_busca;")
    op.execute("ALTER TABLE clientes DROP COLUMN IF EXISTS autorizacao_busca;")
