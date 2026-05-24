from sqlalchemy.orm import Session
from src.leads.model import LeadSite
from src.leads.schema import LeadSiteCreate, LeadSiteUpdate

def listar_leads(db: Session):
    return db.query(LeadSite).all()

def buscar_lead(db: Session, item_id: int):
    return db.query(LeadSite).filter(LeadSite.id == item_id).first()

def criar_lead(db: Session, lead_data: LeadSiteCreate):
    novo_lead = LeadSite(**lead_data.model_dump())
    db.add(novo_lead)
    db.commit()
    db.refresh(novo_lead)
    return novo_lead

def atualizar_lead(db: Session, item_id: int, lead_data: LeadSiteUpdate):
    lead = buscar_lead(db, item_id)
    if not lead:
        return None
    
    update_data = lead_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)
        
    db.commit() 
    db.refresh(lead)
    return lead

def remover_lead(db: Session, item_id: int):
    lead = buscar_lead(db, item_id)
    if not lead:
        return False
    db.delete(lead)
    db.commit()
    return True