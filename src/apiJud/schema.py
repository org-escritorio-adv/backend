from typing import Any
from pydantic import BaseModel


# ── Requests ──────────────────────────────────────────────────────────────────

class DataJudConsultaRequest(BaseModel):
    numero_processo: str
    tribunal: str = "api_publica_tjdft"


class DataJudImportarRequest(BaseModel):
    numero_processo: str
    tribunal: str = "tjdft"
    cliente_id: int | None = None
    advogado_id: int | None = None


# ── Payload bruto do DataJud (ElasticSearch _source) ─────────────────────────

class DataJudProcesso(BaseModel):
    numeroProcesso: str
    tribunal: str | None = None
    grau: str | None = None
    dataAjuizamento: str | None = None
    dataHoraUltimaAtualizacao: str | None = None
    classe: dict[str, Any] | None = None
    assuntos: list[dict[str, Any]] = []
    orgaoJulgador: dict[str, Any] | None = None
    partes: list[dict[str, Any]] = []
    movimentos: list[dict[str, Any]] = []
    nivelSigilo: int | None = None


# ── Responses ─────────────────────────────────────────────────────────────────

class DataJudConsultaResponse(BaseModel):
    numero_processo: str
    tribunal: str
    total: int
    processos: list[DataJudProcesso] = []


class DataJudImportarResponse(BaseModel):
    processo_id: int
    numero_cnj: str
    tribunal: str | None
    data_abertura: str | None
    movimentacoes_importadas: int


class DataJudSincronizarResponse(BaseModel):
    total_processos: int
    sincronizados_com_sucesso: int
    falhas: int
    ultima_sincronizacao: str


# compatibilidade com imports antigos
JusbrasilConsultaRequest = DataJudConsultaRequest
JusbrasilConsultaResponse = DataJudConsultaResponse