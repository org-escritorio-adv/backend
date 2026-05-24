from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PrazoBase(BaseModel):
    titulo: str
    data_limite: datetime
    processo_id: int
    status: str = "pendente"


class PrazoCreate(PrazoBase):
    pass


class PrazoUpdate(BaseModel):
    titulo: str | None = None
    data_limite: datetime | None = None
    status: str | None = None


class Prazo(PrazoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime | None = None
