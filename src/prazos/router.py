from datetime import datetime, timedelta
import holidays
from fastapi import APIRouter, Depends, HTTPException
from src.prazos import repository
from src.keycloak_auth import require_roles
from src.prazos.schema import Prazo, PrazoCreate, PrazoUpdate
from src.shared.crud_factory import create_crud_router

router = create_crud_router(
    prefix="/prazos",
    tags=["prazos"],
    model=Prazo,
    model_create=PrazoCreate,
    model_update=PrazoUpdate,
    listar=repository.listar,
    buscar_por_id=repository.buscar_por_id,
    criar=repository.criar,
    atualizar=repository.atualizar,
    remover=repository.remover,
    resource_name="Prazo",
    roles_listar=["admin", "advogado", "estagiario"],
    roles_buscar=["admin", "advogado", "estagiario"],
    roles_criar=["admin", "advogado"],
    roles_atualizar=["admin", "advogado"],
    roles_remover=["admin"],
)


custom_router = APIRouter(prefix="/prazos", tags=["prazos"])

@custom_router.get(
    "/calcular-data",
    dependencies=[Depends(require_roles("admin", "advogado", "estagiario"))]
)
def calcular_data_prazo(data_inicial: str, dias_uteis: int):
    try:
        data_atual = datetime.fromisoformat(data_inicial)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use ISO 8601 (ex: 2023-10-25T12:00:00)")

    feriados_br = holidays.BR()
    dias_adicionados = 0
    while dias_adicionados < dias_uteis:
        data_atual += timedelta(days=1)
        if data_atual.weekday() < 5 and data_atual.date() not in feriados_br:
            dias_adicionados += 1

    return {"data_inicial": data_inicial, "dias_uteis": dias_uteis, "data_final": data_atual.isoformat()}

