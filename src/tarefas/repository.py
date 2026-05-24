from sqlalchemy.orm import Session
from src.tarefas.model import Tarefa
from src.tarefas.schema import TarefaCreate, TarefaUpdate

def listar(db: Session):
    return db.query(Tarefa).all()

def buscar_por_id(db: Session, item_id: int):
    return db.query(Tarefa).filter(Tarefa.id == item_id).first()

def criar(db: Session, data: TarefaCreate):
    nova_tarefa = Tarefa(**data.model_dump())
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return nova_tarefa

def atualizar(db: Session, item_id: int, data: TarefaUpdate):
    tarefa = buscar_por_id(db, item_id)
    if not tarefa:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tarefa, key, value)
        
    db.commit()
    db.refresh(tarefa)
    return tarefa

def remover(db: Session, item_id: int):
    tarefa = buscar_por_id(db, item_id)
    if not tarefa:
        return False
    db.delete(tarefa)
    db.commit()
    return True
