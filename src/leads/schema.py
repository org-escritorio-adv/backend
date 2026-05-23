from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeadSiteBase(BaseModel):
    nome: str
    email: str
    telefone: str
    mensagem: str
    status: str = "Novo"


class LeadSiteCreate(LeadSiteBase):
    pass


class LeadSiteUpdate(BaseModel):
    status: str | None = None


class LeadSite(LeadSiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
    atualizado_em: datetime | None = None
