from datetime import date

from pydantic import BaseModel


class UsuarioBase(BaseModel):
    nome: str
    email: str
    perfil: str = "advogado"


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    perfil: str | None = None


class Usuario(UsuarioBase):
    id: int
    created_at: date
    updated_at: date
