from datetime import date
from typing import List

from pydantic import BaseModel, Field

from src.movimentacoes.schema import Movement


class Process(BaseModel):
    id: int
    created_at: date
    updated_at: date
    number: str = Field(..., description="Formato CNJ com 20 digitos")
    court: str
    parts: str
    start_date: date
    status: str
    favorite: bool = False
    movements: List[Movement] = []
    client_id: int
    tribunal_id: int
    advogado_id: int


class ProcessCreate(BaseModel):
    number: str
    court: str
    parts: str
    start_date: date
    status: str


class ProcessUpdate(BaseModel):
    number: str | None = None
    court: str | None = None
    parts: str | None = None
    start_date: date | None = None
    status: str | None = None
    favorite: bool | None = None
    movements: List[Movement] | None = None
