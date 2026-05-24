from sqlalchemy.orm import Session
from src.processos.model import Processo
from src.processos.schema import ProcessoCreate, ProcessoUpdate

def listar(db: Session):
    return db.query(Processo).all()

def buscar_por_id(db: Session, item_id: int):
    return db.query(Processo).filter(Processo.id == item_id).first()

def criar(db: Session, data: ProcessoCreate):
    novo_processo = Processo(**data.model_dump())
    db.add(novo_processo)
    db.commit()
    db.refresh(novo_processo)
    return novo_processo

def atualizar(db: Session, item_id: int, data: ProcessoUpdate):
    processo = buscar_por_id(db, item_id)
    if not processo:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(processo, key, value)
        
    db.commit()
    db.refresh(processo)
    return processo

def remover(db: Session, item_id: int):
    processo = buscar_por_id(db, item_id)
    if not processo:
        return False
    db.delete(processo)
    db.commit()
    return True

def toggle_favorite(db: Session, item_id: int):
    processo = buscar_por_id(db, item_id)
    if not processo:
        return None
    processo.favorito = not processo.favorito
    db.commit()
    db.refresh(processo)
    return processo
