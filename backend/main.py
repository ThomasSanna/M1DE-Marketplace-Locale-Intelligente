import time

from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response
from api.v1.routers import products, auth, orders, data

app = FastAPI(
    title="Marketplace Locale Intelligente API",
    description="API pour la marketplace locale avec intégration frontend, SRE et data.",
    version="1.0.0"
)

REQUEST_LATENCY_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Duree des requetes HTTP en secondes.",
    ["method", "path", "status_code"],
)
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Nombre total de requetes HTTP recues.",
    ["method", "path", "status_code"],
)
REQUESTS_SUCCESS_TOTAL = Counter(
    "http_requests_success_total",
    "Nombre total de requetes considerees en succes pour le service (status < 500).",
    ["method", "path"],
)
REQUESTS_ERROR_TOTAL = Counter(
    "http_requests_error_total",
    "Nombre total de requetes en erreur (status >= 500).",
    ["method", "path"],
)


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    if route and hasattr(route, "path"):
        return str(route.path)
    return request.url.path


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    start = time.perf_counter()
    status_code = "500"
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    finally:
        duration = time.perf_counter() - start
        path = _route_path(request)
        method = request.method
        REQUEST_LATENCY_SECONDS.labels(method=method, path=path, status_code=status_code).observe(duration)
        REQUESTS_TOTAL.labels(method=method, path=path, status_code=status_code).inc()
        if int(status_code) < 500:
            REQUESTS_SUCCESS_TOTAL.labels(method=method, path=path).inc()
        else:
            REQUESTS_ERROR_TOTAL.labels(method=method, path=path).inc()

app.include_router(products.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")


@app.get("/metrics", include_in_schema=False)
def prometheus_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de la Marketplace Locale Intelligente !"}
