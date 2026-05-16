from app.utils.crud_factory import create_crud_router
from app.mocks.db_mocks import db_clients

from app.schemas.cliente_schema import Client, ClientCreate, ClientUpdate

'''Rora Crud para Clientes'''
clients_router = create_crud_router(
    prefix="/clientes",
    tags=["Clientes"],
    model=Client,
    model_create=ClientCreate,
    model_update=ClientUpdate,
    db_mock=db_clients,
    resource_name="Cliente"
)

