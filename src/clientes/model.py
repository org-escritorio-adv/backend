from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome_razao_social = Column(String, nullable=False)
    cpf_cnpj = Column(String, unique=True, nullable=False)
    telefone = Column(String)
    email = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    autorizacao_busca = Column(Boolean, default=False)
    data_autorizacao_busca = Column(DateTime, nullable=True)

    processos = relationship("Processo", back_populates="cliente")
