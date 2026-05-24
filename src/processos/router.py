from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.processos import repository
from src.processos.schema import Processo, ProcessoCreate, ProcessoUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/processos",
    tags=["processos"],
    model=Processo,
    model_create=ProcessoCreate,
    model_update=ProcessoUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Processo",
)


@router.patch("/{processo_id}/favoritar", response_model=Processo)
def favoritar_processo(processo_id: int, db: Session = Depends(get_db)):
    item = repository.toggle_favorite(db, processo_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado!")
    return item
