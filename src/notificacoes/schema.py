from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificacaoBase(BaseModel):
    tipo: str = "geral"
    titulo: str
    mensagem: str
    link: str | None = None
    usuario_id: int | None = None


class NotificacaoCreate(NotificacaoBase):
    pass


class Notificacao(NotificacaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lida: bool
    created_at: datetime | None = None