"""add permissoes override column to usuarios

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-17
"""
from alembic import op

revision: str = "0004"
down_revision: str = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS permissoes JSONB;")


def downgrade() -> None:
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS permissoes;")
