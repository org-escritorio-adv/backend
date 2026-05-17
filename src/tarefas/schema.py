from datetime import date

from pydantic import BaseModel


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


class Tarefa(TarefaBase):
    id: int
    created_at: date
    updated_at: date
