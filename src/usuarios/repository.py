from sqlalchemy.orm import Session

from src.usuarios.model import Usuario
from src.usuarios.schema import UsuarioCreate, UsuarioUpdate


def listar(db: Session) -> list[Usuario]:
    return db.query(Usuario).order_by(Usuario.id).all()


def buscar_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def criar(db: Session, dados: UsuarioCreate) -> Usuario:
    payload = dados.model_dump(exclude={"senha"})
    usuario = Usuario(**payload, senha_hash=dados.senha)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def atualizar(db: Session, usuario_id: int, dados: UsuarioUpdate) -> Usuario | None:
    usuario = buscar_por_id(db, usuario_id)
    if not usuario:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def remover(db: Session, usuario_id: int) -> bool:
    usuario = buscar_por_id(db, usuario_id)
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True
