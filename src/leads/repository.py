from sqlalchemy.orm import Session

from src.leads.model import LeadSite
from src.leads.schema import LeadSiteCreate, LeadSiteUpdate


def listar(db: Session) -> list[LeadSite]:
    return db.query(LeadSite).order_by(LeadSite.id).all()


def buscar_por_id(db: Session, lead_id: int) -> LeadSite | None:
    return db.query(LeadSite).filter(LeadSite.id == lead_id).first()


def criar(db: Session, dados: LeadSiteCreate) -> LeadSite:
    lead = LeadSite(**dados.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def atualizar(db: Session, lead_id: int, dados: LeadSiteUpdate) -> LeadSite | None:
    lead = buscar_por_id(db, lead_id)
    if not lead:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(lead, campo, valor)
    db.commit()
    db.refresh(lead)
    return lead


def remover(db: Session, lead_id: int) -> bool:
    lead = buscar_por_id(db, lead_id)
    if not lead:
        return False
    db.delete(lead)
    db.commit()
    return True
