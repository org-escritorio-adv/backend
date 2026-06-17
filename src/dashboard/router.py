from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.keycloak_auth import require_roles
from src.processos.model import Processo
from src.tarefas.model import Tarefa
from src.prazos.model import Prazo
from src.movimentacoes.model import Movimentacao

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class ResumoDashboard(BaseModel):
    totalProcessos: int
    processosAtivos: int
    tarefasAbertas: int
    prazosProximos: int


class AtividadeResumo(BaseModel):
    id: int
    descricao: str
    data: str
    processo_id: int


class DashboardResponse(BaseModel):
    resumo: ResumoDashboard
    atividades: list[AtividadeResumo]


@router.get(
    "/resumo",
    response_model=DashboardResponse,
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def get_resumo(db: Session = Depends(get_db)):
    hoje = datetime.utcnow()
    em7dias = hoje + timedelta(days=7)

    total_processos = db.query(Processo).count()
    processos_ativos = db.query(Processo).filter(Processo.status == "ativo").count()
    tarefas_abertas = db.query(Tarefa).filter(Tarefa.status == "aberta").count()
    prazos_proximos = (
        db.query(Prazo)
        .filter(
            Prazo.status == "pendente",
            Prazo.data_limite >= hoje,
            Prazo.data_limite <= em7dias,
        )
        .count()
    )

    atividades_raw = (
        db.query(Movimentacao)
        .order_by(Movimentacao.data.desc())
        .limit(10)
        .all()
    )

    atividades = [
        AtividadeResumo(
            id=m.id,
            descricao=m.descricao,
            data=m.data.isoformat() if m.data else "",
            processo_id=m.processo_id,
        )
        for m in atividades_raw
    ]

    return DashboardResponse(
        resumo=ResumoDashboard(
            totalProcessos=total_processos,
            processosAtivos=processos_ativos,
            tarefasAbertas=tarefas_abertas,
            prazosProximos=prazos_proximos,
        ),
        atividades=atividades,
    )
