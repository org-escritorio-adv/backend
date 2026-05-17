from datetime import date

from pydantic import BaseModel


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
    id: int
    criado_em: date
    atualizado_em: date
