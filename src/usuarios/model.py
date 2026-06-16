from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func

from src.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(String, unique=True, index=True, nullable=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False, default="keycloak")
    telefone = Column(String, nullable=True)
    oab = Column(String, nullable=True)
    perfil = Column(
        Enum("admin", "advogado", "estagiario", name="perfil_enum"),
        default="advogado",
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
