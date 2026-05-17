from datetime import date

from pydantic import BaseModel


class PrazoBase(BaseModel):
    titulo: str
    data_limite: date
    processo_id: int
    status: str = "pendente"


class PrazoCreate(PrazoBase):
    pass


class PrazoUpdate(BaseModel):
    titulo: str | None = None
    data_limite: date | None = None
    status: str | None = None


class Prazo(PrazoBase):
    id: int
    created_at: date
    updated_at: date
