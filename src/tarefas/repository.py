from sqlalchemy.orm import Session

from src.tarefas.model import Tarefa
from src.tarefas.schema import TarefaCreate, TarefaUpdate


def listar(db: Session) -> list[Tarefa]:
    return db.query(Tarefa).order_by(Tarefa.id).all()


def buscar_por_id(db: Session, tarefa_id: int) -> Tarefa | None:
    return db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()


def criar(db: Session, dados: TarefaCreate) -> Tarefa:
    tarefa = Tarefa(**dados.model_dump())
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


def atualizar(db: Session, tarefa_id: int, dados: TarefaUpdate) -> Tarefa | None:
    tarefa = buscar_por_id(db, tarefa_id)
    if not tarefa:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)
    db.commit()
    db.refresh(tarefa)
    return tarefa


def remover(db: Session, tarefa_id: int) -> bool:
    tarefa = buscar_por_id(db, tarefa_id)
    if not tarefa:
        return False
    db.delete(tarefa)
    db.commit()
    return True
