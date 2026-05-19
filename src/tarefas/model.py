from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    status = Column(String, default="aberta")
    processo_id = Column(Integer, ForeignKey("processos.id"))
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    processo = relationship("Processo", back_populates="tarefas")
