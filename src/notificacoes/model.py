from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func

from src.database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    # tipo livre para categorizar a notificação (ex: "sincronizacao_falha",
    # "nova_movimentacao", "prazo"). Útil para o front escolher ícone/cor.
    tipo = Column(String, nullable=False, default="geral")
    titulo = Column(String, nullable=False)
    mensagem = Column(Text, nullable=False)
    # link opcional para onde a notificação deve levar ao ser clicada
    # (ex: "/app/processos" ou um id de processo).
    link = Column(String, nullable=True)
    lida = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())