from datetime import date, datetime

from sqlalchemy.orm import Session, joinedload

from src.movimentacoes.schema import Movement
from src.processos.model import Processo
from src.processos.schema import Process, ProcessCreate, ProcessUpdate


def _as_date(value: datetime | date | None) -> date:
    if value is None:
        return date.today()
    if isinstance(value, datetime):
        return value.date()
    return value


def _to_process(processo: Processo) -> Process:
    movements = [
        Movement(date=_as_date(m.data), description=m.descricao)
        for m in processo.movimentacoes
    ]
    return Process(
        id=processo.id,
        created_at=_as_date(processo.created_at),
        updated_at=_as_date(processo.updated_at or processo.created_at),
        number=processo.numero_cnj,
        court=processo.tribunal or "",
        parts=processo.partes or "",
        start_date=_as_date(processo.data_abertura),
        status=processo.status or "",
        favorite=bool(processo.favorito),
        movements=movements,
        client_id=processo.cliente_id or 0,
        tribunal_id=0,
        advogado_id=processo.advogado_id or 0,
    )


def _query(db: Session):
    return db.query(Processo).options(joinedload(Processo.movimentacoes))


def listar(db: Session) -> list[Process]:
    return [_to_process(p) for p in _query(db).order_by(Processo.id).all()]


def buscar_por_id(db: Session, processo_id: int) -> Process | None:
    processo = _query(db).filter(Processo.id == processo_id).first()
    return _to_process(processo) if processo else None


def _get_orm(db: Session, processo_id: int) -> Processo | None:
    return _query(db).filter(Processo.id == processo_id).first()


def criar(db: Session, dados: ProcessCreate) -> Process:
    processo = Processo(
        numero_cnj=dados.number,
        tribunal=dados.court,
        partes=dados.parts,
        data_abertura=dados.start_date,
        status=dados.status,
    )
    db.add(processo)
    db.commit()
    db.refresh(processo)
    return _to_process(processo)


def atualizar(db: Session, processo_id: int, dados: ProcessUpdate) -> Process | None:
    processo = _get_orm(db, processo_id)
    if not processo:
        return None

    campos = dados.model_dump(exclude_unset=True, exclude={"movements"})
    mapeamento = {
        "number": "numero_cnj",
        "court": "tribunal",
        "parts": "partes",
        "start_date": "data_abertura",
        "status": "status",
        "favorite": "favorito",
    }
    for campo_api, valor in campos.items():
        setattr(processo, mapeamento.get(campo_api, campo_api), valor)

    db.commit()
    db.refresh(processo)
    return _to_process(processo)


def remover(db: Session, processo_id: int) -> bool:
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        return False
    db.delete(processo)
    db.commit()
    return True


def toggle_favorito(db: Session, processo_id: int) -> Process | None:
    processo = _get_orm(db, processo_id)
    if not processo:
        return None
    processo.favorito = not processo.favorito
    db.commit()
    db.refresh(processo)
    return _to_process(processo)
