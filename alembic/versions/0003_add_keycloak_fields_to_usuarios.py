"""add keycloak fields to usuarios

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-15
"""
from alembic import op

revision: str = "0003"
down_revision: str = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS keycloak_id VARCHAR UNIQUE;")
    op.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefone VARCHAR;")
    op.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS oab VARCHAR;")
    op.execute("CREATE INDEX IF NOT EXISTS ix_usuarios_keycloak_id ON usuarios (keycloak_id);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_usuarios_keycloak_id;")
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS oab;")
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS telefone;")
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS keycloak_id;")
