from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UsuarioBase(BaseModel):
    nome: str
    email: str
    perfil: str = "advogado"


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    oab: str | None = None
    perfil: str | None = None


class UsuarioMeUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    oab: str | None = None


class Usuario(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    email: str
    perfil: str = "advogado"
    telefone: str | None = None
    oab: str | None = None
    status: str | None = "Ativo"
    avatar: str | None = None
    permissoes: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
