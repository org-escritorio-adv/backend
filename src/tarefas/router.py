from src.shared.crud_factory import create_crud_router
from src.tarefas import repository
from src.tarefas.schema import Tarefa, TarefaCreate, TarefaUpdate

router = create_crud_router(
    prefix="/tarefas",
    tags=["tarefas"],
    model=Tarefa,
    model_create=TarefaCreate,
    model_update=TarefaUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Tarefa",
)
