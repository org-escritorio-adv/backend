from fastapi import FastAPI

from app.routers import process_router, health_check

app = FastAPI(title="Escritorio Adv")

'''Rota para Processos'''
app.include_router(process_router.router)

app.include_router(health_check.health)

@app.get("/")
def read_root():
    return {"message": "Rota Base da API"}
