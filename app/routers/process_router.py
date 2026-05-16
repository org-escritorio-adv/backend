from datetime import date
from fastapi import APIRouter, HTTPException
from typing import List
from app.mocks.process_mock import db_processos
from app.schemas.process_schema import Process, ProcessCreate, ProcessUpdate
from app.utils.crud_factory import create_crud_router

'''Construção da Rota Básica'''
router = create_crud_router(
    prefix="/processos",
    tags=["processos"],
    model=Process,
    model_create=ProcessCreate,
    model_update=ProcessUpdate,
    db_mock=db_processos,
    resource_name="Processo"
)

@router.post(f"{process_id}/favoritar")
def favoritar_processo(process_id: int):
    pass
