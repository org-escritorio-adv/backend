from src.leads import repository
from src.leads.schema import LeadSite, LeadSiteCreate, LeadSiteUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/leads",
    tags=["Site (Leads)"],
    model=LeadSite,
    model_create=LeadSiteCreate,
    model_update=LeadSiteUpdate,
    listar=repository.listar_leads,
    buscar_por_id=repository.buscar_lead,
    criar=repository.criar_lead,
    atualizar=repository.atualizar_lead,
    remover=repository.remover_lead,
    resource_name="Lead",
    roles_listar=["admin", "advogado"],
    roles_buscar=["admin", "advogado"],
    roles_criar=["admin", "advogado"],
    roles_atualizar=["admin", "advogado"],
    roles_remover=["admin"],
)