from app.utils.crud_factory import create_crud_router
from app.mocks.lead_mock import db_leads

from app.schemas.lead_site_schema import LeadSite, LeadSiteCreate, LeadSiteUpdate 

'''Rora Crud para Clientes'''
leads_router = create_crud_router(
    prefix="/leads",
    tags=["Site (Leads)"],
    model=LeadSite,
    model_create=LeadSiteCreate,
    model_update=LeadSiteUpdate,
    db_mock=db_leads,
    resource_name="Lead"
)

