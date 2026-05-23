from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.processos import repository
from src.processos.schema import Process, ProcessCreate, ProcessUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/processos",
    tags=["processos"],
    model=Process,
    model_create=ProcessCreate,
    model_update=ProcessUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Processo",
)


@router.patch("/{process_id}/favoritar", response_model=Process)
def favoritar_processo(process_id: int, db: Session = Depends(get_db)):
    item = repository.toggle_favorito(db, process_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado!")
    return item
