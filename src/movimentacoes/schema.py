from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MovimentacaoBase(BaseModel):
    data: datetime
    descricao: str
    processo_id: int


class MovimentacaoCreate(MovimentacaoBase):
    pass


class MovimentacaoUpdate(BaseModel):
    data: datetime | None = None
    descricao: str | None = None
    processo_id: int | None = None


class Movimentacao(MovimentacaoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
