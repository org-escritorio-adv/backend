from sqlalchemy.orm import Session
from src.prazos.model import Prazo
from src.prazos.schema import PrazoCreate, PrazoUpdate

def listar(db: Session):
    return db.query(Prazo).all()

def buscar_por_id(db: Session, item_id: int):
    return db.query(Prazo).filter(Prazo.id == item_id).first()

def criar(db: Session, data: PrazoCreate):
    novo_prazo = Prazo(**data.model_dump())
    db.add(novo_prazo)
    db.commit()
    db.refresh(novo_prazo)
    return novo_prazo

def atualizar(db: Session, item_id: int, data: PrazoUpdate):
    prazo = buscar_por_id(db, item_id)
    if not prazo:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prazo, key, value)
        
    db.commit()
    db.refresh(prazo)
    return prazo

def remover(db: Session, item_id: int):
    prazo = buscar_por_id(db, item_id)
    if not prazo:
        return False
    db.delete(prazo)
    db.commit()
    return True
