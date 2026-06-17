from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Processo(Base):
    __tablename__ = "processos"

    id = Column(Integer, primary_key=True, index=True)
    numero_cnj = Column(String(25), unique=True, nullable=False, index=True)
    tribunal = Column(String)
    partes = Column(Text)
    data_abertura = Column(DateTime)
    status = Column(String, default="ativo")
    favorito = Column(Boolean, default=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    advogado_id = Column(Integer, ForeignKey("usuarios.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cliente = relationship("Cliente", back_populates="processos")
    movimentacoes = relationship(
        "Movimentacao", back_populates="processo", cascade="all, delete-orphan"
    )
    tarefas = relationship("Tarefa", back_populates="processo", cascade="all, delete-orphan")
    prazos = relationship("Prazo", back_populates="processo", cascade="all, delete-orphan")
