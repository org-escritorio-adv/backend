from datetime import date

from pydantic import BaseModel


class ClientBase(BaseModel):
    nome_razao_social: str
    cpf_cnpj: str
    telefone: str | None = None
    email: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nome_razao_social: str | None = None
    cpf_cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None


class Client(ClientBase):
    id: int
    created_at: date
    updated_at: date
