from sqlalchemy.orm import Session

from src.clientes.model import Cliente
from src.clientes.schema import ClientCreate, ClientUpdate


def listar(db: Session) -> list[Cliente]:
    return db.query(Cliente).order_by(Cliente.id).all()


def buscar_por_id(db: Session, cliente_id: int) -> Cliente | None:
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


def buscar_por_cpf(db: Session, cpf_cnpj: str) -> Cliente | None:
    return db.query(Cliente).filter(Cliente.cpf_cnpj == cpf_cnpj).first()


def criar(db: Session, dados: ClientCreate) -> Cliente:
    cliente = Cliente(**dados.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def atualizar(db: Session, cliente: Cliente, dados: ClientUpdate) -> Cliente:
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente


def remover(db: Session, cliente: Cliente) -> None:
    db.delete(cliente)
    db.commit()
