from pydantic import BaseModel

class JusbrasilConsultaRequest(BaseModel):
    numero_processo: str

class JusbrasilConsultaResponse(BaseModel):
    numero_processo: str
    status: str
    dados: dict = {}
