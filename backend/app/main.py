import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.database import init_db
from app.api import auth, campos, parcelas, sensores, alertas, predicciones, reglas, mapa
from app.components.iot_ingestion import IoTIngestionService
from app.components.analytics_engine import AnalyticsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

iot_task: asyncio.Task | None = None
analytics_engine: AnalyticsEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global iot_task, analytics_engine

    await init_db()
    logger.info("Database initialized")

    iot_service = IoTIngestionService()
    iot_task = asyncio.create_task(iot_service.start())
    logger.info("IoT Ingestion Service started")

    analytics_engine = AnalyticsEngine()
    analytics_engine.start_scheduler()
    logger.info("Analytics Engine scheduler started")

    yield

    if iot_task:
        iot_task.cancel()
    if analytics_engine:
        analytics_engine.stop_scheduler()
    logger.info("Services stopped")


app = FastAPI(
    title="AgTechUNS API",
    description="Plataforma de monitoreo y predicción agrícola",
    version="1.0.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Access-Control-Request-Private-Network"],
)


@app.middleware("http")
async def private_network_access(request: Request, call_next):
    if request.method == "OPTIONS" and request.headers.get("access-control-request-private-network"):
        origin = request.headers.get("origin", "")
        if origin in ALLOWED_ORIGINS:
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Private-Network": "true",
                    "Access-Control-Max-Age": "600",
                },
            )
    response = await call_next(request)
    if request.headers.get("access-control-request-private-network"):
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(campos.router, prefix="/campos", tags=["Campos"])
app.include_router(parcelas.router, prefix="/parcelas", tags=["Parcelas"])
app.include_router(sensores.router, prefix="/sensores", tags=["Sensores"])
app.include_router(alertas.router, prefix="/alertas", tags=["Alertas"])
app.include_router(predicciones.router, prefix="/predicciones", tags=["Predicciones"])
app.include_router(reglas.router, prefix="/reglas", tags=["Reglas"])
app.include_router(mapa.router, prefix="/mapa", tags=["Mapa"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "AgTechUNS Backend"}
