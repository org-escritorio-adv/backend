from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.keycloak_auth import require_roles
from src.apiJud import repository
from src.apiJud.schema import (
    DataJudConsultaRequest,
    DataJudConsultaResponse,
    DataJudImportarRequest,
    DataJudImportarResponse,
    DataJudProcesso,
    DataJudSincronizarResponse,
)
from src.movimentacoes.model import Movimentacao
from src.processos.model import Processo

router = APIRouter(prefix="/datajud", tags=["datajud"])

MENSAGEM_DATAJUD_INDISPONIVEL = "O DataJud está indisponível no momento. Tente novamente mais tarde."


def _hits_para_processos(hits: list) -> list[DataJudProcesso]:
    result = []
    for hit in hits:
        try:
            result.append(DataJudProcesso(**hit.get("_source", {})))
        except Exception:
            pass
    return result


@router.post("/consultar", response_model=DataJudConsultaResponse, dependencies=[Depends(require_roles("admin", "advogado"))])
def consultar_processo(body: DataJudConsultaRequest):
    """Consulta DataJud e retorna payload bruto — não persiste no banco."""
    try:
        raw = repository.consultar_por_numero(body.numero_processo, body.tribunal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao consultar DataJud: {e}")
        raise HTTPException(status_code=502, detail=MENSAGEM_DATAJUD_INDISPONIVEL)

    hits = raw.get("hits", {})
    return DataJudConsultaResponse(
        numero_processo=body.numero_processo,
        tribunal=body.tribunal,
        total=hits.get("total", {}).get("value", 0),
        processos=_hits_para_processos(hits.get("hits", [])),
    )


@router.post("/importar", response_model=DataJudImportarResponse, dependencies=[Depends(require_roles("admin", "advogado"))])
def importar_processo(body: DataJudImportarRequest, db: Session = Depends(get_db)):
    """Consulta DataJud e persiste o processo + movimentações no banco."""
    try:
        raw = repository.consultar_por_numero(body.numero_processo, body.tribunal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao consultar DataJud: {e}")
        raise HTTPException(status_code=502, detail=MENSAGEM_DATAJUD_INDISPONIVEL)

    hits = raw.get("hits", {}).get("hits", [])
    if not hits:
        raise HTTPException(
            status_code=404,
            detail="Processo não encontrado no DataJud. Pode ainda não ter sido indexado.",
        )

    source = hits[0]["_source"]
    try:
        processo = repository.importar_processo(
            db,
            source,
            cliente_id=body.cliente_id,
            advogado_id=body.advogado_id,
        )
    except Exception as e:
        print(f"Erro ao salvar processo importado: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar o processo no banco de dados.")

    total_movs = db.query(Movimentacao).filter(Movimentacao.processo_id == processo.id).count()

    return DataJudImportarResponse(
        processo_id=processo.id,
        numero_cnj=processo.numero_cnj,
        tribunal=processo.tribunal,
        data_abertura=processo.data_abertura.isoformat() if processo.data_abertura else None,
        movimentacoes_importadas=total_movs,
    )


@router.get("/buscar/{tribunal}", response_model=DataJudConsultaResponse, dependencies=[Depends(require_roles("admin", "advogado"))])
def buscar_processos(
    tribunal: str,
    numero_processo: str | None = Query(default=None, description="Número CNJ (20 dígitos)"),
    cpf: str | None = Query(default=None, description="CPF de uma das partes (atenção: campo raramente preenchido no DataJud — resultado pode ser vazio)"),
    oab: str | None = Query(default=None, description="Número OAB do advogado (atenção: campo raramente preenchido no DataJud — resultado pode ser vazio)"),
    size: int = Query(default=10, ge=1, le=100),
):
    """Busca processos por número, CPF ou OAB. Informe ao menos um filtro."""
    try:
        raw = repository.buscar_por_filtro(tribunal, numero_processo, cpf, oab, size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao buscar processos no DataJud: {e}")
        raise HTTPException(status_code=502, detail=MENSAGEM_DATAJUD_INDISPONIVEL)

    hits = raw.get("hits", {})
    return DataJudConsultaResponse(
        numero_processo=numero_processo or cpf or oab or "*",
        tribunal=tribunal,
        total=hits.get("total", {}).get("value", 0),
        processos=_hits_para_processos(hits.get("hits", [])),
    )


@router.get("/recentes/{tribunal}", response_model=DataJudConsultaResponse, dependencies=[Depends(require_roles("admin", "advogado"))])
def buscar_recentes(
    tribunal: str,
    size: int = Query(default=10, ge=1, le=100),
):
    """Retorna processos recentes direto do DataJud — não persiste no banco."""
    try:
        raw = repository.buscar_recentes(tribunal, size=size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao buscar processos recentes no DataJud: {e}")
        raise HTTPException(status_code=502, detail=MENSAGEM_DATAJUD_INDISPONIVEL)

    hits = raw.get("hits", {})
    return DataJudConsultaResponse(
        numero_processo="*",
        tribunal=tribunal,
        total=hits.get("total", {}).get("value", 0),
        processos=_hits_para_processos(hits.get("hits", [])),
    )


@router.post(
    "/sincronizar-todos",
    response_model=DataJudSincronizarResponse,
    dependencies=[Depends(require_roles("admin", "advogado"))],
)
def sincronizar_todos_processos(db: Session = Depends(get_db)):
    """
    Atualiza todos os processos cadastrados consultando o DataJud.
    Se o DataJud estiver indisponível, aborta tudo e retorna 502 (US 2.1.1) —
    o front-end mantém os dados antigos visíveis com a data da última
    sincronização bem-sucedida.
    """
    processos = db.query(Processo).all()

    sucesso = 0
    falhas = 0

    for processo in processos:
        try:
            raw = repository.consultar_por_numero(processo.numero_cnj, processo.tribunal)
        except ValueError:
            # Tribunal inválido só nesse processo — não é o DataJud que caiu,
            # então não aborta a sincronização inteira.
            falhas += 1
            continue
        except Exception as e:
            # Falha de conectividade/disponibilidade do próprio DataJud.
            print(f"Erro ao sincronizar com o DataJud: {e}")
            raise HTTPException(status_code=502, detail=MENSAGEM_DATAJUD_INDISPONIVEL)

        hits = raw.get("hits", {}).get("hits", [])
        if not hits:
            falhas += 1
            continue

        source = hits[0]["_source"]
        try:
            repository.importar_processo(
                db,
                source,
                cliente_id=processo.cliente_id,
                advogado_id=processo.advogado_id,
            )
            sucesso += 1
        except Exception as e:
            print(f"Erro ao salvar processo {processo.numero_cnj} durante sincronização: {e}")
            falhas += 1

    return DataJudSincronizarResponse(
        total_processos=len(processos),
        sincronizados_com_sucesso=sucesso,
        falhas=falhas,
        ultima_sincronizacao=datetime.now(timezone.utc).isoformat(),
    )