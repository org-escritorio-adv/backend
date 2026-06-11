from src.shared.crud_factory import create_crud_router
from src.usuarios import repository
from src.usuarios.schema import Usuario, UsuarioCreate, UsuarioUpdate

router = create_crud_router(
    prefix="/usuarios",
    tags=["usuarios"],
    model=Usuario,
    model_create=UsuarioCreate,
    model_update=UsuarioUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=None,
    atualizar=None,
    remover=None,
    resource_name="Usuário",
    roles_listar=["Admin"],
    roles_buscar=["Admin"],
)