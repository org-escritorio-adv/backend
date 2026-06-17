from src.advogados import repository
from src.advogados.schema import Advogado, AdvogadoCreate, AdvogadoUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/advogados",
    tags=["Advogados"],
    model=Advogado,
    model_create=AdvogadoCreate,
    model_update=AdvogadoUpdate,
    listar=repository.listar_advogados,
    buscar_por_id=repository.buscar_advogado,
    criar=repository.criar_advogado,
    atualizar=repository.atualizar_advogado,
    remover=repository.remover_advogado,
    resource_name="Advogado",
    roles_listar=["admin", "advogado", "estagiario"],
    roles_buscar=["admin", "advogado", "estagiario"],
    roles_criar=["admin"],
    roles_atualizar=["admin"],
    roles_remover=["admin"],
)
