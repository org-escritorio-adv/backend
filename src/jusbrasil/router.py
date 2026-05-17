from fastapi import APIRouter

from src.jusbrasil.schema import JusbrasilConsultaRequest, JusbrasilConsultaResponse

router = APIRouter(prefix="/jusbrasil", tags=["jusbrasil"])


@router.post("/consultar", response_model=JusbrasilConsultaResponse)
def consultar_processo(body: JusbrasilConsultaRequest):
    return JusbrasilConsultaResponse(
        numero_processo=body.numero_processo,
        status="pendente",
        dados={},
    )
