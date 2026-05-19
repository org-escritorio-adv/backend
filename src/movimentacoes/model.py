from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(DateTime, nullable=False)
    descricao = Column(Text, nullable=False)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=False)

    processo = relationship("Processo", back_populates="movimentacoes")
