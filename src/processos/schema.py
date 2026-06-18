from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.movimentacoes.schema import Movimentacao


class PrazoEmbutido(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    data_limite: datetime
    status: str
    created_at: datetime | None = None


class ProcessoBase(BaseModel):
    numero_cnj: str = Field(..., description="Número único CNJ de 20 dígitos (ex: 0001234-56.2023.8.26.0000)")
    tribunal: str
    partes: str | None = None
    data_abertura: datetime | None = None
    status: str = "ativo"
    favorito: bool = False
    cliente_id: int | None = None
    advogado_id: int | None = None


class ProcessoCreate(ProcessoBase):
    pass


class ProcessoUpdate(BaseModel):
    numero_cnj: str | None = None
    tribunal: str | None = None
    partes: str | None = None
    data_abertura: datetime | None = None
    status: str | None = None
    favorito: bool | None = None
    cliente_id: int | None = None
    advogado_id: int | None = None


class Processo(ProcessoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    movimentacoes: list[Movimentacao] = []
    prazos: list[PrazoEmbutido] = []


class DocumentoProcessoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    processo_id: int
    nome_original: str
    tamanho: int | None = None
    criado_em: datetime | None = None
