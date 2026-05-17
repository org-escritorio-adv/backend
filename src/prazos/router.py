from src.prazos.repository import get_store
from src.prazos.schema import Prazo, PrazoCreate, PrazoUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/prazos",
    tags=["prazos"],
    model=Prazo,
    model_create=PrazoCreate,
    model_update=PrazoUpdate,
    db_mock=get_store(),
    resource_name="Prazo",
)
