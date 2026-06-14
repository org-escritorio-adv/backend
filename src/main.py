from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.models  # — registra todos os models no Base.metadata
from src.config import FRONTEND_URL
from src.database import Base, engine
from src.clientes.router import router as clientes_router
from src.apiJud.router import router as datajud_router
from src.leads.router import router as leads_router
from src.movimentacoes.router import router as movimentacoes_router
from src.prazos.router import router as prazos_router
from src.processos.router import router as processos_router
from src.shared.health import router as health_router
from src.tarefas.router import router as tarefas_router
from src.usuarios.router import router as usuarios_router
from src.auth.router import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Escritorio Adv")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(processos_router)
app.include_router(clientes_router)
app.include_router(leads_router)
app.include_router(usuarios_router)
app.include_router(prazos_router)
app.include_router(tarefas_router)
app.include_router(movimentacoes_router)
app.include_router(datajud_router)
app.include_router(health_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "Rota Base da API"}
