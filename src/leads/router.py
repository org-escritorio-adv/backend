from src.leads.repository import get_store
from src.leads.schema import LeadSite, LeadSiteCreate, LeadSiteUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/leads",
    tags=["Site (Leads)"],
    model=LeadSite,
    model_create=LeadSiteCreate,
    model_update=LeadSiteUpdate,
    db_mock=get_store(),
    resource_name="Lead",
    created_field="criado_em",
    updated_field="atualizado_em",
)
