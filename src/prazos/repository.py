from sqlalchemy.orm import Session
from src.prazos.model import Prazo
from src.prazos.schema import PrazoCreate, PrazoUpdate
from src.tarefas import repository as tarefas_repo
from src.tarefas import schema as tarefas_schema

def listar(db: Session):
    return db.query(Prazo).all()

def buscar_por_id(db: Session, item_id: int):
    return db.query(Prazo).filter(Prazo.id == item_id).first()

def criar(db: Session, data: PrazoCreate):
    novo_prazo = Prazo(**data.model_dump())
    db.add(novo_prazo)
    db.commit()
    db.refresh(novo_prazo)
    
    # Automatiza a criação de uma Tarefa vinculada a este Prazo
    nova_tarefa_data = tarefas_schema.TarefaCreate(
        titulo=f"Prazo: {data.titulo}",
        descricao=f"Tarefa gerada automaticamente a partir do prazo com data limite {data.data_limite.strftime('%d/%m/%Y %H:%M')}.",
        processo_id=data.processo_id,
        status="aberta"
    )
    tarefas_repo.criar(db, nova_tarefa_data)
    
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
