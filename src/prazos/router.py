from src.prazos import repository
from src.prazos.schema import Prazo, PrazoCreate, PrazoUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/prazos",
    tags=["prazos"],
    model=Prazo,
    model_create=PrazoCreate,
    model_update=PrazoUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Prazo",
    roles_listar=["admin", "advogado", "estagiario"],
    roles_buscar=["admin", "advogado", "estagiario"],
    roles_criar=["admin", "advogado"],
    roles_atualizar=["admin", "advogado"],
    roles_remover=["admin"],
)
