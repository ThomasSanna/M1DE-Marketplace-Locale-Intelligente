from fastapi import FastAPI
from api.v1.routers import products, auth, orders, data

app = FastAPI(
    title="Marketplace Locale Intelligente API",
    description="API pour la marketplace locale avec intégration frontend, SRE et data.",
    version="1.0.0"
)

app.include_router(products.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de la Marketplace Locale Intelligente !"}
