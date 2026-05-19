from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Prazo(Base):
    __tablename__ = "prazos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    data_limite = Column(DateTime, nullable=False)
    status = Column(String, default="pendente")
    processo_id = Column(Integer, ForeignKey("processos.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    processo = relationship("Processo", back_populates="prazos")
