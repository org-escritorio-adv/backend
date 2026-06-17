"""Cria tabela advogados

Revision ID: dce522dbdfd4
Revises: 0004
Create Date: 2026-06-17 21:56:01.128861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'dce522dbdfd4'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('advogados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('cargo', sa.String(), nullable=False),
        sa.Column('especialidade', sa.String(), nullable=True),
        sa.Column('oab', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_advogados_id'), 'advogados', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_advogados_id'), table_name='advogados')
    op.drop_table('advogados')

