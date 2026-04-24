from datetime import date
from fastapi import APIRouter, HTTPException
from typing import List
from app.mocks.process_mock import db_processos
from app.schemas.process_schema import Process, ProcessCreate, ProcessUpdate

'''Rota para processos'''
router = APIRouter(prefix="/processos", tags=["Processos"])

'''Retorna todos os processos'''
@router.get("/", response_model=List[Process])
def list_processes():
    return db_processos


@router.get("/{process_id}", response_model=Process)
def get_process(process_id: int):
    for proc in db_processos:
        if proc["id"] == process_id:
            return proc
    raise HTTPException(status_code=404, detail="Processo não encontrado!")


@router.post("/", response_model=Process)
def create_process(process: ProcessCreate):
    new_id = len(db_processos) + 1
    today = date.today()
    new_process = {
        "id": new_id,
        "created_at": today,
        "updated_at": today,
        **process.model_dump(),
        "favorite": False,
        "movements": [],
    }
    db_processos.append(new_process)
    return new_process

'''Update: Recebe alguns campos para atualização'''
@router.patch("/{process_id}", response_model=Process)
def update_process(process_id: int, body: ProcessUpdate):
    for proc in db_processos:
        if proc["id"] != process_id:
            continue
        updates = body.model_dump(exclude_unset=True)
        if not updates:
            return proc
        proc.update(updates)
        proc["updated_at"] = date.today()
        return proc
    raise HTTPException(status_code=404, detail="Processo não encontrado!")


@router.delete("/{process_id}", status_code=204)
def delete_process(process_id: int):
    for i, proc in enumerate(db_processos): 
        if proc["id"] == process_id:
            db_processos.pop(i)
            return
    raise HTTPException(status_code=404, detail="Processo não encontrado!")
