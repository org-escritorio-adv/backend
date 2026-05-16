from datetime import date
from typing import List
from pydantic import BaseModel, Field

class Movement(BaseModel):
    date: date
    description: str

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

    # TO DO: revisar a modelagem
    client_id: int      # Aponta para o ID do Cliente
    tribunal_id: int     # Aponta para o ID do Tribunal
    advogado_id: int     # Aponta para o ID do Usuário (Advogado)

class ProcessCreate(BaseModel):
    number: str
    court: str
    parts: str
    start_date: date
    status: str


class ProcessUpdate(BaseModel):
    """PATCH: só os enviados são aplicados."""

    number: str | None = None
    court: str | None = None
    parts: str | None = None
    start_date: date | None = None
    status: str | None = None
    favorite: bool | None = None
    movements: List[Movement] | None = None
