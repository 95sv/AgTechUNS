"""
Composition Root del backend AgTechUNS — arquitectura hexagonal.

Acá se "ensambla" la aplicación FastAPI: se incluyen los routers HTTP y se
configuran middlewares globales (CORS, rate limiting). Este backend expone
únicamente la API — la visualización vive en un servicio aparte (ver
../frontend), consumida vía HTTP desde el navegador.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from src.interfaces.http.auth_router import router as auth_router
from src.interfaces.http.analytics_router import router as analytics_router
from src.interfaces.http.diagnostic_router import router as diagnostic_router
from src.interfaces.http.dashboard_router import router as dashboard_router


app = FastAPI(
    title="AgTechUNS Backend",
    version="1.0.0",
    description="Plataforma de Agricultura Inteligente — Comisión 13 — UNS 2026",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Routers
app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(diagnostic_router)
app.include_router(dashboard_router)
