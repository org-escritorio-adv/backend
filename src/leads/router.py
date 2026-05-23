from src.leads import repository
from src.leads.schema import LeadSite, LeadSiteCreate, LeadSiteUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/leads",
    tags=["Site (Leads)"],
    model=LeadSite,
    model_create=LeadSiteCreate,
    model_update=LeadSiteUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Lead",
)
