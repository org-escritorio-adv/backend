from datetime import datetime
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
    dados_dict = dados.model_dump()
    if dados_dict.get("autorizacao_busca") and not dados_dict.get("data_autorizacao_busca"):
        dados_dict["data_autorizacao_busca"] = datetime.utcnow()
    cliente = Cliente(**dados_dict)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def atualizar(db: Session, cliente: Cliente, dados: ClientUpdate) -> Cliente:
    update_data = dados.model_dump(exclude_unset=True)
    if update_data.get("autorizacao_busca") and not update_data.get("data_autorizacao_busca"):
        update_data["data_autorizacao_busca"] = datetime.utcnow()
    
    for campo, valor in update_data.items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente


def remover(db: Session, cliente: Cliente) -> None:
    db.delete(cliente)
    db.commit()
