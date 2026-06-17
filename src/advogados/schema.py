from pydantic import BaseModel, ConfigDict
from typing import Optional

class AdvogadoBase(BaseModel):
    nome: str
    cargo: str
    especialidade: Optional[str] = None
    oab: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None

class AdvogadoCreate(AdvogadoBase):
    pass

class AdvogadoUpdate(AdvogadoBase):
    nome: Optional[str] = None
    cargo: Optional[str] = None

class Advogado(AdvogadoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
