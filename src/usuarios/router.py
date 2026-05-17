from src.shared.crud_factory import create_crud_router
from src.usuarios.repository import get_store
from src.usuarios.schema import Usuario, UsuarioCreate, UsuarioUpdate

router = create_crud_router(
    prefix="/usuarios",
    tags=["usuarios"],
    model=Usuario,
    model_create=UsuarioCreate,
    model_update=UsuarioUpdate,
    db_mock=get_store(),
    resource_name="Usuário",
)
