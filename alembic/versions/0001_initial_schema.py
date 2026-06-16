"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-15

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE perfil_enum AS ENUM ('admin', 'advogado', 'estagiario');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id          SERIAL PRIMARY KEY,
            nome        VARCHAR NOT NULL,
            email       VARCHAR NOT NULL,
            senha_hash  VARCHAR NOT NULL,
            perfil      perfil_enum NOT NULL DEFAULT 'advogado',
            created_at  TIMESTAMPTZ DEFAULT now(),
            updated_at  TIMESTAMPTZ
        );
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_email ON usuarios (email);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_usuarios_id    ON usuarios (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_usuarios_email ON usuarios (email);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id                    SERIAL PRIMARY KEY,
            nome_razao_social     VARCHAR NOT NULL,
            cpf_cnpj              VARCHAR NOT NULL,
            telefone              VARCHAR,
            email                 VARCHAR,
            created_at            TIMESTAMPTZ DEFAULT now(),
            updated_at            TIMESTAMPTZ,
            autorizacao_busca     BOOLEAN DEFAULT FALSE,
            data_autorizacao_busca TIMESTAMP
        );
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_clientes_cpf_cnpj ON clientes (cpf_cnpj);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_clientes_id ON clientes (id);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS processos (
            id          SERIAL PRIMARY KEY,
            numero_cnj  VARCHAR(25) NOT NULL,
            tribunal    VARCHAR,
            partes      TEXT,
            data_abertura TIMESTAMP,
            status      VARCHAR DEFAULT 'ativo',
            favorito    BOOLEAN DEFAULT FALSE,
            cliente_id  INTEGER REFERENCES clientes(id),
            advogado_id INTEGER REFERENCES usuarios(id),
            created_at  TIMESTAMPTZ DEFAULT now(),
            updated_at  TIMESTAMPTZ
        );
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_processos_numero_cnj ON processos (numero_cnj);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_processos_id         ON processos (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_processos_numero_cnj ON processos (numero_cnj);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id          SERIAL PRIMARY KEY,
            data        TIMESTAMP NOT NULL,
            descricao   TEXT NOT NULL,
            processo_id INTEGER NOT NULL REFERENCES processos(id)
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_movimentacoes_id ON movimentacoes (id);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id             SERIAL PRIMARY KEY,
            titulo         VARCHAR NOT NULL,
            descricao      TEXT,
            status         VARCHAR DEFAULT 'aberta',
            processo_id    INTEGER REFERENCES processos(id),
            responsavel_id INTEGER REFERENCES usuarios(id),
            created_at     TIMESTAMPTZ DEFAULT now(),
            updated_at     TIMESTAMPTZ
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_tarefas_id ON tarefas (id);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS prazos (
            id          SERIAL PRIMARY KEY,
            titulo      VARCHAR NOT NULL,
            data_limite TIMESTAMP NOT NULL,
            status      VARCHAR DEFAULT 'pendente',
            processo_id INTEGER REFERENCES processos(id),
            created_at  TIMESTAMPTZ DEFAULT now()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_prazos_id ON prazos (id);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS leads_site (
            id           SERIAL PRIMARY KEY,
            nome         VARCHAR NOT NULL,
            email        VARCHAR NOT NULL,
            telefone     VARCHAR,
            mensagem     TEXT,
            status       VARCHAR DEFAULT 'Novo',
            criado_em    TIMESTAMPTZ DEFAULT now(),
            atualizado_em TIMESTAMPTZ
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_leads_site_id ON leads_site (id);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id          VARCHAR PRIMARY KEY,
            email       VARCHAR NOT NULL,
            token       VARCHAR(6) NOT NULL,
            expires_at  TIMESTAMPTZ NOT NULL,
            created_at  TIMESTAMPTZ DEFAULT now()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_email ON password_reset_tokens (email);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS password_reset_tokens;")
    op.execute("DROP TABLE IF EXISTS leads_site;")
    op.execute("DROP TABLE IF EXISTS prazos;")
    op.execute("DROP TABLE IF EXISTS tarefas;")
    op.execute("DROP TABLE IF EXISTS movimentacoes;")
    op.execute("DROP TABLE IF EXISTS processos;")
    op.execute("DROP TABLE IF EXISTS clientes;")
    op.execute("DROP TABLE IF EXISTS usuarios;")
    op.execute("DROP TYPE IF EXISTS perfil_enum;")
