from fastapi import FastAPI

from src.clientes.router import router as clientes_router
from src.jusbrasil.router import router as jusbrasil_router
from src.leads.router import router as leads_router
from src.movimentacoes.router import router as movimentacoes_router
from src.prazos.router import router as prazos_router
from src.processos.router import router as processos_router
from src.shared.health import router as health_router
from src.tarefas.router import router as tarefas_router
from src.usuarios.router import router as usuarios_router

app = FastAPI(title="Escritorio Adv")

app.include_router(processos_router)
app.include_router(clientes_router)
app.include_router(leads_router)
app.include_router(usuarios_router)
app.include_router(prazos_router)
app.include_router(tarefas_router)
app.include_router(movimentacoes_router)
app.include_router(jusbrasil_router)
app.include_router(health_router)


@app.get("/")
def read_root():
    return {"message": "Rota Base da API"}
