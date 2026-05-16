from pydantic import BaseModel
from datetime import date

class ClientBase(BaseModel):
    nome_razao_social: str
    cpf_cnpj: str
    telefone: str | None = None
    email: str | None = None

class ClientCreate(ClientBase):
    pass #Herda de Client Base

class ClientUpdate(BaseModel):
    nome_razao_social: str | None = None
    cpf_cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None

class Client(ClientBase):
    id: int
    created_at: date
    updated_at: date
