from collections.abc import Callable
from typing import Any, List, Type

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db

def create_crud_router(
    prefix: str,
    tags: List[str],
    model: Type[BaseModel],
    model_create: Type[BaseModel],
    model_update: Type[BaseModel],
    listar: Callable[[Session], list[Any]],
    buscar_por_id: Callable[[Session, int], Any | None],
    criar: Callable[[Session, BaseModel], Any],
    atualizar: Callable[[Session, int, BaseModel], Any | None],
    remover: Callable[[Session, int], bool],
    resource_name: str = "Recurso",
) -> APIRouter:
    
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("/", response_model=List[model])
    def list_items(db: Session = Depends(get_db)):
        return listar(db)

    @router.get("/{item_id}", response_model=model)
    def get_item(item_id: int, db: Session = Depends(get_db)):
        item = buscar_por_id(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")
        return item

    @router.post("/", response_model=model, status_code=201)
    def create_item(body: model_create, db: Session = Depends(get_db)):
        return criar(db, body)

    @router.patch("/{item_id}", response_model=model)
    def update_item(item_id: int, body: model_update, db: Session = Depends(get_db)):
        item = atualizar(db, item_id, body)
        if not item:
            raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")
        return item

    @router.delete("/{item_id}", status_code=204)
    def delete_item(item_id: int, db: Session = Depends(get_db)):
        sucesso = remover(db, item_id)
        if not sucesso:
            raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")

    return router