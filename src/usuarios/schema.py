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
    perfil: str | None = None


class Usuario(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None
