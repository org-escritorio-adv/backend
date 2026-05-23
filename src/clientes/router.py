from src.clientes import repository, service
from src.clientes.schema import Client, ClientCreate, ClientUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/clientes",
    tags=["Clientes"],
    model=Client,
    model_create=ClientCreate,
    model_update=ClientUpdate,
    resource_name="Cliente",
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=service.criar_cliente,
    atualizar=service.atualizar_cliente,
    remover=service.remover_cliente,
)
