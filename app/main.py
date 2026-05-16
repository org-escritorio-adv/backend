from fastapi import FastAPI

from app.routers import process_router, health_check, client_router, lead_site_router

app = FastAPI(title="Escritorio Adv")

'''Rota para cada Modelo'''
app.include_router(process_router.router)
app.include_router(health_check.health)
app.include_router(client_router)
app.include_router(lead_site_router)

@app.get("/")
def read_root():
    return {"message": "Rota Base da API"}
