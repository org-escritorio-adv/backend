import hashlib
from sqlalchemy.orm import Session
from src.usuarios.model import Usuario
from src.usuarios.schema import UsuarioCreate, UsuarioUpdate

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def listar(db: Session):
    return db.query(Usuario).all()

def buscar_por_id(db: Session, item_id: int):
    return db.query(Usuario).filter(Usuario.id == item_id).first()

def criar(db: Session, user_data: UsuarioCreate):
    dumped = user_data.model_dump()
    senha = dumped.pop("senha")
    senha_hash = hash_senha(senha)
    
    novo_usuario = Usuario(**dumped, senha_hash=senha_hash)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

def atualizar(db: Session, item_id: int, user_data: UsuarioUpdate):
    usuario = buscar_por_id(db, item_id)
    if not usuario:
        return None
    
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)
        
    db.commit()
    db.refresh(usuario)
    return usuario

def remover(db: Session, item_id: int):
    usuario = buscar_por_id(db, item_id)
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True
