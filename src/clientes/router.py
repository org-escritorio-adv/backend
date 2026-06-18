import base64
import os
import uuid
from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.clientes import repository, service
from src.clientes.schema import AutorizacaoResponse, Client, ClientCreate, ClientUpdate
from src.database import get_db
from src.keycloak_auth import require_roles
from src.shared.crud_factory import create_crud_router

UPLOAD_DIR = "uploads/autorizacoes"
if os.getenv("VERCEL") == "1":
    UPLOAD_DIR = "/tmp/escritorio-adv/autorizacoes"
UPLOAD_DIR = os.getenv("AUTORIZACOES_UPLOAD_DIR", UPLOAD_DIR)

EXTENSOES_PERMITIDAS = {".pdf", ".jpg", ".jpeg", ".png"}
TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10 MB


def _ensure_upload_dir() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)


class AutorizacaoRequest(BaseModel):
    declaracao: bool = False
    arquivo_base64: str | None = None
    arquivo_nome: str | None = None


router = create_crud_router(
    prefix="/clientes",
    tags=["Clientes"],
    model=Client,
    model_create=ClientCreate,
    model_update=ClientUpdate,
    resource_name="Cliente",
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=service.criar_cliente,
    atualizar=service.atualizar_cliente,
    remover=service.remover_cliente,
    roles_listar=["admin", "advogado"],
    roles_buscar=["admin", "advogado"],
    roles_criar=["admin", "advogado"],
    roles_atualizar=["admin", "advogado"],
    roles_remover=["admin"],
)


@router.post(
    "/{cliente_id}/autorizacao",
    response_model=AutorizacaoResponse,
    dependencies=[Depends(require_roles("admin", "advogado"))],
    summary="Registra autorização de busca por CPF/CNPJ (declaração ou upload base64)",
)
def registrar_autorizacao(
    cliente_id: int,
    body: AutorizacaoRequest,
    db: Session = Depends(get_db),
):
    cliente = repository.buscar_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado!")

    if not body.declaracao and not body.arquivo_base64:
        raise HTTPException(
            status_code=400,
            detail="Informe a declaração de posse ou envie o arquivo do termo.",
        )

    if body.arquivo_base64:
        _ensure_upload_dir()

        nome = body.arquivo_nome or "termo.pdf"
        ext = os.path.splitext(nome)[1].lower()
        if ext not in EXTENSOES_PERMITIDAS:
            raise HTTPException(
                status_code=422,
                detail=f"Formato não permitido. Use: {', '.join(EXTENSOES_PERMITIDAS)}",
            )

        try:
            conteudo = base64.b64decode(body.arquivo_base64)
        except Exception:
            raise HTTPException(status_code=422, detail="Arquivo base64 inválido.")

        if len(conteudo) > TAMANHO_MAXIMO:
            raise HTTPException(status_code=422, detail="Arquivo excede 10 MB.")

        # Remove arquivo anterior se existir
        if cliente.termo_autorizacao_arquivo:
            antigo = os.path.join(UPLOAD_DIR, cliente.termo_autorizacao_arquivo)
            if os.path.exists(antigo):
                os.remove(antigo)

        nome_salvo = f"{cliente_id}_{uuid.uuid4().hex}{ext}"
        with open(os.path.join(UPLOAD_DIR, nome_salvo), "wb") as f:
            f.write(conteudo)

        cliente.termo_autorizacao_arquivo = nome_salvo

    cliente.autorizacao_busca = True
    cliente.data_autorizacao_busca = datetime.utcnow()

    db.commit()
    db.refresh(cliente)
    return cliente


@router.get(
    "/{cliente_id}/autorizacao/arquivo",
    dependencies=[Depends(require_roles("admin", "advogado"))],
    summary="Baixa o termo de autorização salvo",
)
def baixar_termo_autorizacao(cliente_id: int, db: Session = Depends(get_db)):
    cliente = repository.buscar_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado!")
    if not cliente.termo_autorizacao_arquivo:
        raise HTTPException(status_code=404, detail="Nenhum arquivo cadastrado.")

    caminho = os.path.join(UPLOAD_DIR, cliente.termo_autorizacao_arquivo)
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no servidor.")

    return FileResponse(caminho, filename=cliente.termo_autorizacao_arquivo)
