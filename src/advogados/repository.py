from sqlalchemy.orm import Session
from src.advogados.model import Advogado
from src.advogados.schema import AdvogadoCreate, AdvogadoUpdate
from typing import List, Optional

def listar_advogados(db: Session) -> List[Advogado]:
    return db.query(Advogado).all()

def buscar_advogado(db: Session, advogado_id: int) -> Optional[Advogado]:
    return db.query(Advogado).filter(Advogado.id == advogado_id).first()

def criar_advogado(db: Session, advogado: AdvogadoCreate) -> Advogado:
    db_advogado = Advogado(**advogado.model_dump())
    db.add(db_advogado)
    db.commit()
    db.refresh(db_advogado)
    return db_advogado

def atualizar_advogado(db: Session, advogado_id: int, advogado: AdvogadoUpdate) -> Optional[Advogado]:
    db_advogado = buscar_advogado(db, advogado_id)
    if db_advogado:
        update_data = advogado.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_advogado, key, value)
        db.commit()
        db.refresh(db_advogado)
    return db_advogado

def remover_advogado(db: Session, advogado_id: int) -> bool:
    db_advogado = buscar_advogado(db, advogado_id)
    if db_advogado:
        db.delete(db_advogado)
        db.commit()
        return True
    return False
