from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.keycloak_auth import require_roles
from src.notificacoes.model import Notificacao
from src.notificacoes import schema

router = APIRouter(prefix="/notificacoes", tags=["notificacoes"])


@router.get(
    "/",
    response_model=list[schema.Notificacao],
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def listar_notificacoes(
    apenas_nao_lidas: bool = False,
    limite: int = 50,
    db: Session = Depends(get_db),
):
    """Lista as notificações mais recentes (globais + do usuário)."""
    query = db.query(Notificacao)
    if apenas_nao_lidas:
        query = query.filter(Notificacao.lida == False)  # noqa: E712
    return (
        query.order_by(Notificacao.created_at.desc())
        .limit(limite)
        .all()
    )


@router.get(
    "/nao-lidas/contagem",
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def contar_nao_lidas(db: Session = Depends(get_db)):
    """Retorna quantas notificações não lidas existem (para o badge do sininho)."""
    total = db.query(Notificacao).filter(Notificacao.lida == False).count()  # noqa: E712
    return {"nao_lidas": total}


@router.patch(
    "/{notificacao_id}/marcar-lida",
    response_model=schema.Notificacao,
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def marcar_como_lida(notificacao_id: int, db: Session = Depends(get_db)):
    """Marca uma notificação específica como lida."""
    notificacao = db.query(Notificacao).filter(Notificacao.id == notificacao_id).first()
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada.")
    notificacao.lida = True
    db.commit()
    db.refresh(notificacao)
    return notificacao


@router.patch(
    "/marcar-todas-lidas",
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))],
)
def marcar_todas_como_lidas(db: Session = Depends(get_db)):
    """Marca todas as notificações não lidas como lidas."""
    atualizadas = (
        db.query(Notificacao)
        .filter(Notificacao.lida == False)  # noqa: E712
        .update({Notificacao.lida: True})
    )
    db.commit()
    return {"marcadas_como_lidas": atualizadas}