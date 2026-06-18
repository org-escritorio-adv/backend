"""Adiciona telefone e foto_url a advogados

Revision ID: 9c2f1ab34d70
Revises: 8a1c4d7e9b20
Create Date: 2026-06-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9c2f1ab34d70'
down_revision: Union[str, None] = '8a1c4d7e9b20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('advogados', sa.Column('telefone', sa.String(), nullable=True))
    op.add_column('advogados', sa.Column('foto_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('advogados', 'foto_url')
    op.drop_column('advogados', 'telefone')
