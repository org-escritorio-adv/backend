from src.shared.crud_factory import create_crud_router
from src.tarefas.repository import get_store
from src.tarefas.schema import Tarefa, TarefaCreate, TarefaUpdate

router = create_crud_router(
    prefix="/tarefas",
    tags=["tarefas"],
    model=Tarefa,
    model_create=TarefaCreate,
    model_update=TarefaUpdate,
    db_mock=get_store(),
    resource_name="Tarefa",
)
