from sqlalchemy.orm import Session
from src.movimentacoes.model import Movimentacao
from src.movimentacoes.schema import MovimentacaoCreate, MovimentacaoUpdate

def listar(db: Session):
    return db.query(Movimentacao).all()

def buscar_por_id(db: Session, item_id: int):
    return db.query(Movimentacao).filter(Movimentacao.id == item_id).first()

def criar(db: Session, data: MovimentacaoCreate):
    nova_mov = Movimentacao(**data.model_dump())
    db.add(nova_mov)
    db.commit()
    db.refresh(nova_mov)
    return nova_mov

def atualizar(db: Session, item_id: int, data: MovimentacaoUpdate):
    mov = buscar_por_id(db, item_id)
    if not mov:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(mov, key, value)
        
    db.commit()
    db.refresh(mov)
    return mov

def remover(db: Session, item_id: int):
    mov = buscar_por_id(db, item_id)
    if not mov:
        return False
    db.delete(mov)
    db.commit()
    return True
