from pydantic import BaseModel
from typing import Optional
from datetime import date

class LeadSiteBase(BaseModel):
    nome: str
    email: str
    telefone: str
    mensagem: str
    status: str = "Novo" 

class LeadSiteCreate(LeadSiteBase):
    pass

class LeadSiteUpdate(BaseModel):
    status: str | None = None #  atualizar o status do lead

class LeadSite(LeadSiteBase):
    id: int
    criado_em: date
    atualizado_em: date