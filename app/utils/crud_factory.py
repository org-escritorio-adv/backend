from datetime import date
from fastapi import APIRouter, HTTPException
from typing import List, Type, Dict, Any
from pydantic import BaseModel

def create_crud_router(
    prefix: str,
    tags: List[str],
    model: Type[BaseModel],
    model_create: Type[BaseModel],
    model_update: Type[BaseModel],
    db_mock: List[Dict[str, Any]], #Temporario
    resource_name: str = "Recurso" #Mensagem de Erro
) -> APIRouter:

    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("/", response_model=List[model])
    def list_items():
        return db_mock

    @router.get(f"/{id}", response_model=model)
    def get_item(item_id: int):
        for item in db_mock:
            if item["id"] == item_id:
                return item
        raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")
    
    @router.post("/", response_model=model)
    def create_item(item: model_create):
        new_id = len(db_mock) + 1 if db_mock else 1
        today = date.today()

        new_item = {
            "id": new_id,
            "created_at": today,
            "updated_at": today,
            **item.model_dump() #unpacking operator - move o restante para o dicionario
        }
        db_mock.append(new_item)
        return new_item

    @router.patch(f"/{item_id}", response_model=model)
    def update_item(item_id: int, body: model_update):
        for item in db_mock:
            if item["id"] != item_id:
                continue

            updates = body.model_dump(exclude_unset=True)
            if not updates:
                return item

            item.update(updates)
            item["updated_at"] = date.today()
            return item

        raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")

    @router.delete(f"/{item_id}", status_code=204)
    def delete_item(item_id: int):
        for i, item in enumerate(db_mock):
            if item["id"] == item_id:
                db_mock.pop(i)
                return
        raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")

    # Retorna router com crud completo (5 rotas)
    return router
