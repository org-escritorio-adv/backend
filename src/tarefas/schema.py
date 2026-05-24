from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TarefaBase(BaseModel):
    titulo: str
    descricao: str | None = None
    processo_id: int | None = None
    responsavel_id: int | None = None
    status: str = "aberta"


class TarefaCreate(TarefaBase):
    pass


class TarefaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    status: str | None = None
    processo_id: int | None = None
    responsavel_id: int | None = None


class Tarefa(TarefaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
