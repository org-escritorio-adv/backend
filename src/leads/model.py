from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from src.database import Base


class LeadSite(Base):
    __tablename__ = "leads_site"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String)
    mensagem = Column(Text)
    status = Column(String, default="Novo")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
