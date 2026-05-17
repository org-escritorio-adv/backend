from fastapi import APIRouter, HTTPException

from src.processos.repository import get_store, toggle_favorite
from src.processos.schema import Process, ProcessCreate, ProcessUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/processos",
    tags=["processos"],
    model=Process,
    model_create=ProcessCreate,
    model_update=ProcessUpdate,
    db_mock=get_store(),
    resource_name="Processo",
)


@router.patch("/{process_id}/favoritar", response_model=Process)
def favoritar_processo(process_id: int):
    item = toggle_favorite(process_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Processo não encontrado!")
    return item
