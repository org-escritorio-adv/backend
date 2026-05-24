from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LeadSiteBase(BaseModel):
    nome: str
    email: str
    telefone: str | None = None
    mensagem: str | None = None
    status: str = "Novo"


class LeadSiteCreate(LeadSiteBase):
    pass


class LeadSiteUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    mensagem: str | None = None
    status: str | None = None


class LeadSite(LeadSiteBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None
