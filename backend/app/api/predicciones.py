from fastapi import APIRouter, BackgroundTasks
from app.api.deps import DB, CurrentUser
from app.repositories import relational as repo
from app.schemas.prediccion import PrediccionResponse
from app.components.analytics_engine import AnalyticsEngine

router = APIRouter()


@router.get("/", response_model=list[PrediccionResponse])
async def listar_predicciones(db: DB, _: CurrentUser, limit: int = 20):
    return await repo.get_predicciones(db, limit=limit)


@router.get("/parcela/{nombre_parcela}", response_model=list[PrediccionResponse])
async def predicciones_por_parcela(nombre_parcela: str, db: DB, _: CurrentUser, limit: int = 10):
    return await repo.get_predicciones(db, nombre_parcela=nombre_parcela, limit=limit)


@router.post("/ejecutar", status_code=202)
async def ejecutar_batch_manual(background_tasks: BackgroundTasks, _: CurrentUser):
    engine = AnalyticsEngine()
    background_tasks.add_task(engine.run_batch)
    return {"message": "Ejecución batch iniciada en background"}
