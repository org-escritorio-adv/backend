from src.shared.crud_factory import create_crud_router
from src.movimentacoes import repository
from src.movimentacoes.schema import Movimentacao, MovimentacaoCreate, MovimentacaoUpdate

router = create_crud_router(
    prefix="/movimentacoes",
    tags=["movimentacoes"],
    model=Movimentacao,
    model_create=MovimentacaoCreate,
    model_update=MovimentacaoUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Movimentação",
    roles_listar=["admin", "advogado", "estagiario"],
    roles_buscar=["admin", "advogado", "estagiario"],
    roles_criar=["admin", "advogado"],
    roles_atualizar=["admin", "advogado"],
    roles_remover=["admin"],
)
