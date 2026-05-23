from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.clientes import repository
from src.clientes.schema import ClientCreate, ClientUpdate


def _garantir_cpf_disponivel(
    db: Session, cpf_cnpj: str, cliente_id: int | None = None
) -> None:
    existente = repository.buscar_por_cpf(db, cpf_cnpj)
    if existente and (cliente_id is None or existente.id != cliente_id):
        raise HTTPException(status_code=409, detail="CPF/CNPJ já cadastrado")


def criar_cliente(db: Session, dados: ClientCreate):
    _garantir_cpf_disponivel(db, dados.cpf_cnpj)
    try:
        return repository.criar(db, dados)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="CPF/CNPJ já cadastrado")


def atualizar_cliente(db: Session, cliente_id: int, dados: ClientUpdate):
    cliente = repository.buscar_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado!")

    if dados.cpf_cnpj is not None:
        _garantir_cpf_disponivel(db, dados.cpf_cnpj, cliente_id=cliente_id)

    try:
        return repository.atualizar(db, cliente, dados)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="CPF/CNPJ já cadastrado")


def remover_cliente(db: Session, cliente_id: int) -> None:
    cliente = repository.buscar_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado!")
    repository.remover(db, cliente)
