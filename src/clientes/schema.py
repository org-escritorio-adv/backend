from datetime import datetime

from pydantic import BaseModel, ConfigDict

class ClientBase(BaseModel):
    """Campos comuns de entrada e saída da API."""

    nome_razao_social: str
    cpf_cnpj: str
    telefone: str | None = None
    email: str | None = None
    autorizacao_busca: bool = False
    data_autorizacao_busca: datetime | None = None


class ClientCreate(ClientBase):
    """Body do POST — herda todos os campos obrigatórios de ClientBase."""
    pass


class ClientUpdate(BaseModel):
    """Body do PATCH — todos opcionais (atualização parcial)."""
    nome_razao_social: str | None = None
    cpf_cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None
    autorizacao_busca: bool | None = None
    data_autorizacao_busca: datetime | None = None


class Client(ClientBase):
    """Resposta da API — lê atributos do ORM Cliente."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    termo_autorizacao_arquivo: str | None = None


class AutorizacaoResponse(BaseModel):
    """Resposta do endpoint de registro de autorização."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    autorizacao_busca: bool
    data_autorizacao_busca: datetime | None
    termo_autorizacao_arquivo: str | None
