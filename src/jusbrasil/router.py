from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.jusbrasil import repository
from src.jusbrasil.schema import (
    DataJudConsultaRequest,
    DataJudConsultaResponse,
    DataJudImportarRequest,
    DataJudImportarResponse,
    DataJudProcesso,
)
from src.movimentacoes.model import Movimentacao

router = APIRouter(prefix="/datajud", tags=["datajud"])


def _hits_para_processos(hits: list) -> list[DataJudProcesso]:
    result = []
    for hit in hits:
        try:
            result.append(DataJudProcesso(**hit.get("_source", {})))
        except Exception:
            pass
    return result


@router.post("/consultar", response_model=DataJudConsultaResponse)
def consultar_processo(body: DataJudConsultaRequest):
    """Consulta DataJud e retorna payload bruto — não persiste no banco."""
    try:
        raw = repository.consultar_por_numero(body.numero_processo, body.tribunal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro DataJud: {e}")

    hits = raw.get("hits", {})
    return DataJudConsultaResponse(
        numero_processo=body.numero_processo,
        tribunal=body.tribunal,
        total=hits.get("total", {}).get("value", 0),
        processos=_hits_para_processos(hits.get("hits", [])),
    )


@router.post("/importar", response_model=DataJudImportarResponse)
def importar_processo(body: DataJudImportarRequest, db: Session = Depends(get_db)):
    """Consulta DataJud e persiste o processo + movimentações no banco."""
    try:
        raw = repository.consultar_por_numero(body.numero_processo, body.tribunal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro DataJud: {e}")

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
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco: {e}")

    total_movs = db.query(Movimentacao).filter(Movimentacao.processo_id == processo.id).count()

    return DataJudImportarResponse(
        processo_id=processo.id,
        numero_cnj=processo.numero_cnj,
        tribunal=processo.tribunal,
        data_abertura=processo.data_abertura.isoformat() if processo.data_abertura else None,
        movimentacoes_importadas=total_movs,
    )


@router.get("/buscar/{tribunal}", response_model=DataJudConsultaResponse)
def buscar_processos(
    tribunal: str,
    numero_processo: str | None = Query(default=None, description="Número CNJ (20 dígitos)"),
    cpf: str | None = Query(default=None, description="CPF de uma das partes"),
    oab: str | None = Query(default=None, description="Número OAB do advogado"),
    size: int = Query(default=10, ge=1, le=100),
):
    """Busca processos por número, CPF ou OAB. Informe ao menos um filtro."""
    try:
        raw = repository.buscar_por_filtro(tribunal, numero_processo, cpf, oab, size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro DataJud: {e}")

    hits = raw.get("hits", {})
    return DataJudConsultaResponse(
        numero_processo=numero_processo or cpf or oab or "*",
        tribunal=tribunal,
        total=hits.get("total", {}).get("value", 0),
        processos=_hits_para_processos(hits.get("hits", [])),
    )


@router.get("/listar/{tribunal}", response_model=DataJudConsultaResponse)
def listar_processos(
    tribunal: str,
    size: int = Query(default=10, ge=1, le=100),
):
    """Lista processos recentes do tribunal — não persiste no banco."""
    try:
        raw = repository.listar_processos(tribunal, size=size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro DataJud: {e}")

    hits = raw.get("hits", {})
    return DataJudConsultaResponse(
        numero_processo="*",
        tribunal=tribunal,
        total=hits.get("total", {}).get("value", 0),
        processos=_hits_para_processos(hits.get("hits", [])),
    )
