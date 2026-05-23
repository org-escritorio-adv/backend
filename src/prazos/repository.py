from sqlalchemy.orm import Session

from src.prazos.model import Prazo
from src.prazos.schema import PrazoCreate, PrazoUpdate


def listar(db: Session) -> list[Prazo]:
    return db.query(Prazo).order_by(Prazo.id).all()


def buscar_por_id(db: Session, prazo_id: int) -> Prazo | None:
    return db.query(Prazo).filter(Prazo.id == prazo_id).first()


def criar(db: Session, dados: PrazoCreate) -> Prazo:
    prazo = Prazo(**dados.model_dump())
    db.add(prazo)
    db.commit()
    db.refresh(prazo)
    return prazo


def atualizar(db: Session, prazo_id: int, dados: PrazoUpdate) -> Prazo | None:
    prazo = buscar_por_id(db, prazo_id)
    if not prazo:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(prazo, campo, valor)
    db.commit()
    db.refresh(prazo)
    return prazo


def remover(db: Session, prazo_id: int) -> bool:
    prazo = buscar_por_id(db, prazo_id)
    if not prazo:
        return False
    db.delete(prazo)
    db.commit()
    return True
