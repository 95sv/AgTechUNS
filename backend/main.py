from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from src.interfaces.http.auth_router import router as auth_router
from src.interfaces.http.analytics_router import router as analytics_router
from src.interfaces.http.diagnostic_router import router as diagnostic_router
from src.interfaces.http.dashboard_router import router as dashboard_router
from src.interfaces.http.campos_router import router as campos_router
from src.interfaces.http.parcelas_router import router as parcelas_router
from src.interfaces.http.cultivos_router import router as cultivos_router
from src.interfaces.http.reglas_router import router as reglas_router
from src.interfaces.http.usuarios_router import router as usuarios_router
from src.interfaces.http.external_router import router as external_router


app = FastAPI(
    title="API de AgTechUNS",
    version="1.1.0",
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

# Rutas públicas del contrato YAML Entrega 4
app.include_router(auth_router)
app.include_router(campos_router)       # /campos/** + /campos/{campo}/parcelas/** + recomendaciones
app.include_router(parcelas_router)     # /parcelas (rutas planas, usadas por el panel HTML legacy)
app.include_router(cultivos_router)     # /cultivos
app.include_router(reglas_router)       # /reglas
app.include_router(usuarios_router)     # /usuarios
app.include_router(external_router)     # /external/weather + /external/satelital

# Rutas internas del sistema (dashboard y diagnóstico)
app.include_router(dashboard_router)    # /dashboard/parcelas  (usado por el frontend Next.js)
app.include_router(analytics_router)   # /analytics/evaluar  (endpoint interno del dashboard)
app.include_router(diagnostic_router)  # /diagnostico/health

# Panel HTML estático (versión legacy del frontend)
app.mount("/panel", StaticFiles(directory="static", html=True), name="panel")
