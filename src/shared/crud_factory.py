from datetime import date
from typing import Any, Dict, List, Type

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


def create_crud_router(
    prefix: str,
    tags: List[str],
    model: Type[BaseModel],
    model_create: Type[BaseModel],
    model_update: Type[BaseModel],
    db_mock: List[Dict[str, Any]],
    resource_name: str = "Recurso",
    created_field: str = "created_at",
    updated_field: str = "updated_at",
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("/", response_model=List[model])
    def list_items():
        return db_mock

    @router.get("/{item_id}", response_model=model)
    def get_item(item_id: int):
        for item in db_mock:
            if item["id"] == item_id:
                return item
        raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")

    @router.post("/", response_model=model)
    def create_item(item: model_create):
        new_id = max((i["id"] for i in db_mock), default=0) + 1
        today = date.today()
        new_item = {
            "id": new_id,
            created_field: today,
            updated_field: today,
            **item.model_dump(),
        }
        db_mock.append(new_item)
        return new_item

    @router.patch("/{item_id}", response_model=model)
    def update_item(item_id: int, body: model_update):
        for item in db_mock:
            if item["id"] != item_id:
                continue
            updates = body.model_dump(exclude_unset=True)
            if not updates:
                return item
            item.update(updates)
            item[updated_field] = date.today()
            return item
        raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")

    @router.delete("/{item_id}", status_code=204)
    def delete_item(item_id: int):
        for i, item in enumerate(db_mock):
            if item["id"] == item_id:
                db_mock.pop(i)
                return
        raise HTTPException(status_code=404, detail=f"{resource_name} não encontrado!")

    return router
