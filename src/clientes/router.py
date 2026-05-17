from src.clientes.repository import get_store
from src.clientes.schema import Client, ClientCreate, ClientUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/clientes",
    tags=["Clientes"],
    model=Client,
    model_create=ClientCreate,
    model_update=ClientUpdate,
    db_mock=get_store(),
    resource_name="Cliente",
)
